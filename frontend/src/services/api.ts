import axios, { type AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'
import { globalErrorHandler, ErrorType } from '@/utils/errorHandler'
import type { ApiResponse } from '@/types/global'
import type { RequestConfig } from '@/types/api'

// ======== API 配置 ========
const API_BASE_URL = '/api/v1'  // 强制使用相对路径，通过Vite代理转发
const API_TIMEOUT = 30000

/**
 * 创建 HTTP 客户端
 */
function createHttpClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      
      console.log(`%c→ API请求: ${config.method?.toUpperCase()} ${config.url}`, 'color: #e6a23c; font-size: 11px;')
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
      console.log(`%c✓ API响应: ${response.config.url}`, 'color: #67c23a; font-size: 11px;')
      console.log('响应数据:', response.data)
      
      // 检查响应数据是否存在
      if (!response.data) {
        console.warn('响应数据为空')
        return { success: false, message: '响应数据为空' }
      }
      
      // 检查业务错误
      if (response.data && !response.data.success && response.data.code !== 200) {
        const error = new Error(response.data.message || '请求失败')
        throw error
      }
      
      console.log('响应拦截器返回:', response.data)
      return response.data
    },
    (error) => {
      console.error('API响应错误:', error)
      
      if (error.response?.status === 401) {
        localStorage.clear()
        window.location.href = '/login'
      }
      
      const message = error.response?.data?.message || error.message || '网络请求失败'
      ElMessage.error(message)
      globalErrorHandler.handle(error, { type: ErrorType.API })
      
      return Promise.reject(error)
    }
  )

  return client
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
    const { method = 'GET', params, data, ...restConfig } = config
    
    const response = await this.httpClient.request<T>({
      url,
      method,
      params,
      data,
      ...restConfig
    })
    
    console.log('request方法接收到的响应:', response)
    
    // 响应拦截器已经处理了数据，直接返回
    return response as T
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
  async getPrometheusConfig() {
    console.log('🔥 [FIXED] 发送Prometheus配置请求: /prometheus/config')
    console.log('🔥 [FIXED] 完整baseURL:', API_BASE_URL)
    return this.get('/prometheus/config?_t=' + Date.now())
  }
  
  async updatePrometheusConfig(config: any) {
    return this.post('/prometheus/config', config)
  }
  
  async testPrometheusConnection(config: any) {
    return this.post('/prometheus/test', config)
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