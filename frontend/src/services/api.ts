import axios, { type AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'
import { globalErrorHandler, ErrorType } from '@/utils/errorHandler'
import { requestManager } from '@/utils/requestManager'
import { performanceMonitor } from '@/utils/performanceMonitor'
import type { ApiResponse } from '@/types/global'
import type { RequestConfig } from '@/types/api'

// ======== API 配置 ========
const API_BASE_URL = '/api/v1'  // 强制使用相对路径，通过Vite代理转发
const API_TIMEOUT = 15000  // 减少超时时间，提高响应性
const MAX_RETRIES = 3
const RETRY_DELAY = 1000
const CACHE_DURATION = 60000  // 缓存1分钟

// ======== 请求缓存 ========
interface CacheItem {
  data: any
  timestamp: number
  url: string
}

const requestCache = new Map<string, CacheItem>()

// 清理过期缓存
setInterval(() => {
  const now = Date.now()
  for (const [key, item] of requestCache.entries()) {
    if (now - item.timestamp > CACHE_DURATION) {
      requestCache.delete(key)
    }
  }
}, CACHE_DURATION)

/**
 * 创建 HTTP 客户端
 */
function createHttpClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json; charset=utf-8'
    },
    // 启用请求压缩
    transformRequest: [function (data) {
      if (typeof data === 'object') {
        return JSON.stringify(data)
      }
      return data
    }],
    // 自动重试配置
    validateStatus: function (status) {
      return status >= 200 && status < 300
    }
  })

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      // 添加认证token
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      
      // 生成请求ID并开始追踪
      const requestId = requestManager.startRequest(config.url || '', config.method?.toUpperCase() || 'GET')
      config.headers['X-Request-ID'] = requestId
      config.metadata = { requestId } // 保存到config中供后续使用
      
      // 添加时间戳防止缓存
      if (config.method?.toLowerCase() === 'get') {
        config.params = { ...config.params, _t: Date.now() }
      }
      
      // 开始性能监控
      config.startTime = performance.now()
      
      console.log(`%c→ API请求: ${config.method?.toUpperCase()} ${config.url} [${requestId}]`, 'color: #e6a23c; font-size: 11px;')
      return config
    },
    (error) => {
      globalErrorHandler.handle(error, { source: 'request_interceptor' })
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  client.interceptors.response.use(
    (response) => {
      const config = response.config as any
      const requestId = config.metadata?.requestId
      const duration = config.startTime ? performance.now() - config.startTime : 0
      
      // 完成请求追踪
      if (requestId) {
        requestManager.finishRequest(requestId, 'success')
      }
      
      // 添加性能监控
      if (config.url) {
        performanceMonitor.addMetric({
          name: config.url,
          duration,
          timestamp: Date.now(),
          type: 'api',
          status: 'success',
          details: {
            method: config.method,
            status: response.status
          }
        })
      }
      
      console.log(`%c✓ API响应: ${response.config.url} (${duration.toFixed(0)}ms) [${requestId}]`, 'color: #67c23a; font-size: 11px;')
      
      // 检查响应数据
      if (!response.data) {
        console.warn('响应数据为空')
        return { success: false, message: '响应数据为空', data: null }
      }
      
      // 标准化响应格式
      const standardResponse = {
        success: response.data.success !== false,
        message: response.data.message || 'OK',
        data: response.data.data || response.data,
        timestamp: response.data.timestamp || new Date().toISOString()
      }
      
      // 缓存GET请求结果
      if (response.config.method?.toLowerCase() === 'get') {
        const cacheKey = `${response.config.url}_${JSON.stringify(response.config.params)}`
        requestCache.set(cacheKey, {
          data: standardResponse,
          timestamp: Date.now(),
          url: response.config.url || ''
        })
      }
      
      return standardResponse
    },
    async (error) => {
      const config = error.config as any
      const requestId = config?.metadata?.requestId
      const duration = config?.startTime ? performance.now() - config.startTime : 0
      
      // 完成请求追踪
      if (requestId) {
        requestManager.finishRequest(requestId, 'error', error)
      }
      
      // 添加性能监控
      if (config?.url) {
        performanceMonitor.addMetric({
          name: config.url,
          duration,
          timestamp: Date.now(),
          type: 'api',
          status: 'error',
          details: {
            method: config.method,
            status: error.response?.status,
            error: error.message
          }
        })
      }
      
      // 记录请求失败
      console.error(`❌ API请求失败: ${config?.url} [${requestId}]`, {
        status: error.response?.status,
        message: error.message,
        data: error.response?.data,
        duration: `${duration.toFixed(0)}ms`
      })
      
      // 处理认证错误
      if (error.response?.status === 401) {
        localStorage.clear()
        ElMessage.error('登录已过期，请重新登录')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1000)
        return Promise.reject(error)
      }
      
      // 自动重试逻辑
      if (shouldRetry(error) && requestId && requestManager.retryRequest(requestId)) {
        const retryCount = requestManager.getRequestState(requestId)?.retryCount || 0
        console.log(`🔄 重试请求 (${retryCount}/${MAX_RETRIES}): ${config?.url} [${requestId}]`)
        
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * retryCount))
        return client(config)
      }
      
      // 标准化错误响应
      const errorResponse = {
        success: false,
        message: getErrorMessage(error),
        data: null,
        timestamp: new Date().toISOString(),
        error: {
          status: error.response?.status,
          code: error.code,
          type: error.name,
          requestId
        }
      }
      
      // 显示用户友好的错误信息
      ElMessage.error(errorResponse.message)
      globalErrorHandler.handle(error, { type: ErrorType.API, requestId })
      
      return Promise.reject(errorResponse)
    }
  )

  return client
}

// ======== 辅助函数 ========
function shouldRetry(error: any): boolean {
  // 网络错误或服务器错误时重试
  return !error.response || 
         error.response.status >= 500 || 
         error.code === 'NETWORK_ERROR' || 
         error.code === 'ECONNABORTED'
}

function getErrorMessage(error: any): string {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  switch (error.response?.status) {
    case 400:
      return '请求参数错误'
    case 401:
      return '未授权访问'
    case 403:
      return '权限不足'
    case 404:
      return '请求的资源不存在'
    case 422:
      return '请求数据验证失败'
    case 429:
      return '请求过于频繁，请稍后再试'
    case 500:
      return '服务器内部错误'
    case 502:
      return '网关错误'
    case 503:
      return '服务暂时不可用'
    case 504:
      return '请求超时'
    default:
      if (error.code === 'NETWORK_ERROR') {
        return '网络连接错误，请检查网络状态'
      }
      if (error.code === 'ECONNABORTED') {
        return '请求超时，请稍后重试'
      }
      return error.message || '未知错误'
  }
}

// ======== API 服务类 ========
export class ApiService {
  private static instance: ApiService
  private httpClient: AxiosInstance

  constructor() {
    this.httpClient = createHttpClient()
  }

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService()
    }
    return ApiService.instance
  }

  /**
   * 通用请求方法
   */
  async request<T = any>(url: string, config: RequestConfig = {}): Promise<T> {
    const { method = 'GET', params, data, useCache = true, ...restConfig } = config
    
    // 检查缓存（仅GET请求）
    if (method === 'GET' && useCache) {
      const cacheKey = `${url}_${JSON.stringify(params)}`
      const cached = requestCache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log(`%c📦 使用缓存: ${url}`, 'color: #909399; font-size: 11px;')
        return cached.data as T
      }
    }
    
    // 添加请求开始时间用于性能监控
    const requestStartTime = Date.now()
    
    try {
      const response = await this.httpClient.request<T>({
        url,
        method,
        params,
        data,
        ...restConfig,
        requestStartTime // 传递给拦截器
      } as any)
      
      return response as T
    } catch (error: any) {
      // 增强错误信息
      const duration = Date.now() - requestStartTime
      console.error(`❌ 请求失败 ${url} (${duration}ms):`, error)
      throw error
    }
  }

  /**
   * 带缓存的GET请求
   */
  async getCached<T = any>(url: string, params?: any, cacheDuration = CACHE_DURATION): Promise<T> {
    const cacheKey = `${url}_${JSON.stringify(params)}`
    const cached = requestCache.get(cacheKey)
    
    if (cached && Date.now() - cached.timestamp < cacheDuration) {
      return cached.data as T
    }
    
    const result = await this.get<T>(url, params)
    
    // 手动缓存结果
    requestCache.set(cacheKey, {
      data: result,
      timestamp: Date.now(),
      url
    })
    
    return result
  }

  /**
   * 清除指定URL的缓存
   */
  clearCache(url?: string): void {
    if (url) {
      for (const [key, item] of requestCache.entries()) {
        if (item.url.includes(url)) {
          requestCache.delete(key)
        }
      }
    } else {
      requestCache.clear()
    }
  }

  // HTTP 方法快捷方式
  get<T = any>(url: string, params?: any): Promise<T> {
    return this.request<T>(url, { method: 'GET', params })
  }

  post<T = any>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, { method: 'POST', data })
  }

  put<T = any>(url: string, data?: any): Promise<T> {
    return this.request<T>(url, { method: 'PUT', data })
  }

  delete<T = any>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' })
  }

  // ======== 业务API方法 ========

  // 认证相关
  async login(credentials: any) {
    return this.post('/auth/login', credentials)
  }

  async logout() {
    return this.post('/auth/logout')
  }

  // Prometheus 配置相关
  async getPrometheusConfig(useCache = true) {
    console.log('🔥 发送Prometheus配置请求: /prometheus/config')
    if (useCache) {
      return this.getCached('/prometheus/config', {}, 30000) // 30秒缓存
    }
    return this.get('/prometheus/config')
  }
  
  async updatePrometheusConfig(config: any) {
    // 清除相关缓存
    this.clearCache('/prometheus/config')
    return this.post('/prometheus/config', config)
  }
  
  async testPrometheusConnection(config: any) {
    return this.post('/prometheus/test', config)
  }

  // Prometheus 配置历史相关
  async getPrometheusConfigHistory(useCache = true) {
    if (useCache) {
      return this.getCached('/prometheus/config/history', {}, 60000) // 1分钟缓存
    }
    return this.get('/prometheus/config/history')
  }

  async restorePrometheusConfig(configId: string) {
    // 清除相关缓存
    this.clearCache('/prometheus/config')
    return this.post(`/prometheus/config/restore/${configId}`)
  }

  async createPrometheusConfig(config: any) {
    // 清除相关缓存
    this.clearCache('/prometheus/config')
    return this.post('/prometheus/config/create', config)
  }

  async deletePrometheusConfig(configId: string) {
    // 清除相关缓存
    this.clearCache('/prometheus/config')
    return this.delete(`/prometheus/config/${configId}`)
  }

  async clearPrometheusConfigHistory() {
    // 清除相关缓存
    this.clearCache('/prometheus/config')
    return this.delete('/prometheus/config/history')
  }

  // PromQL 查询相关
  async executePromQLQuery(queryParams: any) {
    return this.post('/prometheus/query', queryParams)
  }

  async getPrometheusMetrics() {
    return this.get('/prometheus/metrics')
  }

  async getPrometheusTargets() {
    return this.get('/prometheus/targets')
  }

  async validatePrometheusConfigName(name: string) {
    return this.post('/prometheus/config/validate-name', { name })
  }

  async setCurrentPrometheusConfig(configId: number) {
    return this.post(`/prometheus/config/set-current/${configId}`)
  }
  
  // Ollama 配置相关
  async getOllamaConfig(useCache = true) {
    if (useCache) {
      return this.getCached('/ollama/config', {}, 30000) // 30秒缓存
    }
    return this.get('/ollama/config')
  }

  async updateOllamaConfig(config: any) {
    // 清除相关缓存
    this.clearCache('/ollama/config')
    return this.post('/ollama/config', config)
  }
  
  async testOllamaConnection(config: any) {
    return this.post('/ollama/test', config)
  }

  // Ollama 配置历史相关
  async getOllamaConfigHistory(useCache = true) {
    if (useCache) {
      return this.getCached('/ollama/config/history', {}, 60000) // 1分钟缓存
    }
    return this.get('/ollama/config/history')
  }

  async setCurrentOllamaConfig(configId: number) {
    return this.post(`/ollama/config/set-current/${configId}`)
  }

  async clearOllamaConfigHistory() {
    return this.delete('/ollama/config/history')
  }

  // Ollama 聊天相关
  async chatWithOllama(params: { message: string; config: any }) {
    return this.post('/ollama/chat', params)
  }

  // Ollama 模型相关
  async getOllamaModels(apiUrl: string = 'http://localhost:11434') {
    return this.get(`/ollama/models?api_url=${encodeURIComponent(apiUrl)}`)
  }
  
  // 数据库健康检查
  async checkDatabaseHealth() {
    return this.get('/database/health')
  }
  
  // 指标数据
  async getMetrics(params?: any) {
    return this.get('/metrics', params)
  }
  
  async getMetricHistory(metric: string, params?: any) {
    return this.get(`/metrics/${metric}/history`, params)
  }
  
  // 异常检测
  async getAnomalies(params?: any) {
    return this.get('/anomalies', params)
  }
  
  async analyzeWithAI(data: any) {
    return this.post('/ai/analyze', data)
  }
  
  // 规则管理
  async getRules(params?: any) {
    return this.get('/rules', params)
  }
  
  async createRule(rule: any) {
    return this.post('/rules', rule)
  }
  
  async updateRule(id: string, rule: any) {
    return this.put(`/rules/${id}`, rule)
  }
  
  async deleteRule(id: string) {
    return this.delete(`/rules/${id}`)
  }
  
  // 通知管理
  async getNotifications(params?: any) {
    return this.get('/notifications', params)
  }
  
  async getNotificationChannels() {
    return this.get('/notifications/channels')
  }
  
  // 系统管理
  async getSystemInfo() {
    return this.get('/system/info')
  }
  
  async getSystemServices() {
    return this.get('/system/services')
  }

  // 新增：获取系统健康状态
  async getSystemHealth() {
    return this.get('/system/health')
  }

  // 新增：获取系统统计信息
  async getSystemStatistics() {
    return this.get('/system/statistics')
  }

  // 新增：获取仪表盘数据
  async getDashboardData() {
    return this.get('/system/dashboard')
  }

  async getCurrentUser() {
    return this.get('/users/me')
  }
  
  // 数据导出
  async exportData(type: string, params: any): Promise<Blob> {
    const response = await this.httpClient.request({
      url: `/export/${type}`,
      method: 'GET',
      params,
      responseType: 'blob'
    })
    return response.data
  }
  
  // 数据库相关
  async saveInspectionData(data: any) {
    return this.post('/database/inspections', data)
  }

  async getInspectionData(params?: any) {
    return this.get('/database/inspections', params)
  }

  async saveMetricsData(data: any) {
    return this.post('/database/metrics', data)
  }

  async getMetricsData(params?: any) {
    return this.get('/database/metrics', params)
  }

  async saveAnalysisResult(data: any) {
    return this.post('/database/analysis', data)
  }

  async getAnalysisResults(params?: any) {
    return this.get('/database/analysis', params)
  }

  async exportDatabaseData(type: string, params: any): Promise<Blob> {
    const response = await this.httpClient.request({
      url: `/database/export/${type}`,
      method: 'GET',
      params,
      responseType: 'blob'
    })
    return response.data
  }

  async backupDatabase() {
    return this.post('/database/backup')
  }
}

// 导出单例实例
export const apiService = ApiService.getInstance()
export default apiService