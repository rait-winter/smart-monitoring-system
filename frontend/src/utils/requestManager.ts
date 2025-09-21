/**
 * 请求状态管理器 - 解决接口访问偶尔出错问题
 */

import { ElMessage, ElNotification } from 'element-plus'

interface RequestState {
  url: string
  method: string
  status: 'pending' | 'success' | 'error' | 'timeout'
  startTime: number
  endTime?: number
  retryCount: number
  lastError?: any
}

interface RequestConfig {
  maxRetries?: number
  retryDelay?: number
  timeout?: number
  enableCircuitBreaker?: boolean
  circuitBreakerThreshold?: number
  circuitBreakerTimeout?: number
}

class RequestManager {
  private activeRequests = new Map<string, RequestState>()
  private requestHistory: RequestState[] = []
  private circuitBreakers = new Map<string, {
    failures: number
    lastFailureTime: number
    isOpen: boolean
  }>()
  
  private config: Required<RequestConfig> = {
    maxRetries: 3,
    retryDelay: 1000,
    timeout: 15000,
    enableCircuitBreaker: true,
    circuitBreakerThreshold: 5,
    circuitBreakerTimeout: 30000
  }

  constructor(config?: Partial<RequestConfig>) {
    if (config) {
      this.config = { ...this.config, ...config }
    }
    this.startHealthCheck()
  }

  /**
   * 生成请求ID
   */
  private generateRequestId(url: string, method: string): string {
    return `${method.toLowerCase()}_${url}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 获取服务标识符（用于熔断器）
   */
  private getServiceKey(url: string): string {
    try {
      const urlObj = new URL(url, window.location.origin)
      const pathParts = urlObj.pathname.split('/').filter(Boolean)
      // 使用前两级路径作为服务标识
      return pathParts.slice(0, 2).join('/')
    } catch {
      return url.split('?')[0]
    }
  }

  /**
   * 检查熔断器状态
   */
  private isCircuitBreakerOpen(serviceKey: string): boolean {
    if (!this.config.enableCircuitBreaker) return false
    
    const breaker = this.circuitBreakers.get(serviceKey)
    if (!breaker) return false
    
    if (breaker.isOpen) {
      const now = Date.now()
      // 检查是否应该尝试恢复
      if (now - breaker.lastFailureTime > this.config.circuitBreakerTimeout) {
        breaker.isOpen = false
        breaker.failures = 0
        console.log(`🔄 熔断器恢复: ${serviceKey}`)
        return false
      }
      return true
    }
    
    return false
  }

  /**
   * 记录请求失败
   */
  private recordFailure(serviceKey: string) {
    if (!this.config.enableCircuitBreaker) return
    
    let breaker = this.circuitBreakers.get(serviceKey)
    if (!breaker) {
      breaker = { failures: 0, lastFailureTime: 0, isOpen: false }
      this.circuitBreakers.set(serviceKey, breaker)
    }
    
    breaker.failures++
    breaker.lastFailureTime = Date.now()
    
    if (breaker.failures >= this.config.circuitBreakerThreshold && !breaker.isOpen) {
      breaker.isOpen = true
      console.warn(`⚡ 熔断器开启: ${serviceKey} (失败次数: ${breaker.failures})`)
      ElNotification({
        title: '服务熔断',
        message: `服务 ${serviceKey} 暂时不可用，请稍后重试`,
        type: 'warning',
        duration: 5000
      })
    }
  }

  /**
   * 记录请求成功
   */
  private recordSuccess(serviceKey: string) {
    const breaker = this.circuitBreakers.get(serviceKey)
    if (breaker && breaker.failures > 0) {
      breaker.failures = Math.max(0, breaker.failures - 1)
      if (breaker.failures === 0 && breaker.isOpen) {
        breaker.isOpen = false
        console.log(`✅ 熔断器关闭: ${serviceKey}`)
      }
    }
  }

  /**
   * 开始请求
   */
  startRequest(url: string, method: string = 'GET'): string {
    const requestId = this.generateRequestId(url, method)
    const serviceKey = this.getServiceKey(url)
    
    // 检查熔断器
    if (this.isCircuitBreakerOpen(serviceKey)) {
      throw new Error(`服务 ${serviceKey} 暂时不可用（熔断器开启）`)
    }
    
    const requestState: RequestState = {
      url,
      method,
      status: 'pending',
      startTime: Date.now(),
      retryCount: 0
    }
    
    this.activeRequests.set(requestId, requestState)
    
    // 设置超时检查
    setTimeout(() => {
      const state = this.activeRequests.get(requestId)
      if (state && state.status === 'pending') {
        this.finishRequest(requestId, 'timeout', new Error('Request timeout'))
      }
    }, this.config.timeout)
    
    return requestId
  }

  /**
   * 完成请求
   */
  finishRequest(requestId: string, status: 'success' | 'error' | 'timeout', error?: any): void {
    const state = this.activeRequests.get(requestId)
    if (!state) return
    
    state.status = status
    state.endTime = Date.now()
    state.lastError = error
    
    const serviceKey = this.getServiceKey(state.url)
    
    if (status === 'success') {
      this.recordSuccess(serviceKey)
    } else {
      this.recordFailure(serviceKey)
    }
    
    // 移到历史记录
    this.requestHistory.push({ ...state })
    this.activeRequests.delete(requestId)
    
    // 限制历史记录大小
    if (this.requestHistory.length > 1000) {
      this.requestHistory.splice(0, 100)
    }
    
    // 记录慢请求
    const duration = (state.endTime || Date.now()) - state.startTime
    if (duration > 3000) {
      console.warn(`🐌 慢请求: ${state.method} ${state.url} 耗时 ${duration}ms`)
    }
  }

  /**
   * 重试请求
   */
  retryRequest(requestId: string): boolean {
    const state = this.activeRequests.get(requestId)
    if (!state) return false
    
    if (state.retryCount >= this.config.maxRetries) {
      return false
    }
    
    state.retryCount++
    state.status = 'pending'
    state.startTime = Date.now()
    
    console.log(`🔄 重试请求 (${state.retryCount}/${this.config.maxRetries}): ${state.method} ${state.url}`)
    
    return true
  }

  /**
   * 获取请求状态
   */
  getRequestState(requestId: string): RequestState | undefined {
    return this.activeRequests.get(requestId)
  }

  /**
   * 获取活跃请求数量
   */
  getActiveRequestCount(): number {
    return this.activeRequests.size
  }

  /**
   * 获取服务健康状态
   */
  getServiceHealth(): Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy'
    successRate: number
    avgResponseTime: number
    recentErrors: number
  }> {
    const now = Date.now()
    const last5Minutes = now - 5 * 60 * 1000
    const recentRequests = this.requestHistory.filter(r => r.startTime > last5Minutes)
    
    const serviceStats: Record<string, {
      total: number
      success: number
      errors: number
      totalTime: number
    }> = {}
    
    // 统计各服务的请求情况
    recentRequests.forEach(request => {
      const serviceKey = this.getServiceKey(request.url)
      if (!serviceStats[serviceKey]) {
        serviceStats[serviceKey] = { total: 0, success: 0, errors: 0, totalTime: 0 }
      }
      
      const stats = serviceStats[serviceKey]
      stats.total++
      
      if (request.status === 'success') {
        stats.success++
      } else {
        stats.errors++
      }
      
      if (request.endTime) {
        stats.totalTime += request.endTime - request.startTime
      }
    })
    
    // 计算健康指标
    const healthStatus: Record<string, any> = {}
    
    Object.entries(serviceStats).forEach(([serviceKey, stats]) => {
      const successRate = stats.total > 0 ? (stats.success / stats.total) * 100 : 100
      const avgResponseTime = stats.success > 0 ? stats.totalTime / stats.success : 0
      const recentErrors = stats.errors
      
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy'
      
      if (successRate < 90 || avgResponseTime > 3000 || recentErrors > 10) {
        status = 'unhealthy'
      } else if (successRate < 95 || avgResponseTime > 1500 || recentErrors > 5) {
        status = 'degraded'
      }
      
      healthStatus[serviceKey] = {
        status,
        successRate,
        avgResponseTime,
        recentErrors
      }
    })
    
    return healthStatus
  }

  /**
   * 获取错误统计
   */
  getErrorStats(): {
    total: number
    byType: Record<string, number>
    recent: Array<{
      url: string
      method: string
      error: string
      time: string
    }>
  } {
    const now = Date.now()
    const last10Minutes = now - 10 * 60 * 1000
    const recentErrors = this.requestHistory
      .filter(r => r.status === 'error' && r.startTime > last10Minutes)
    
    const byType: Record<string, number> = {}
    
    recentErrors.forEach(request => {
      const errorType = this.classifyError(request.lastError)
      byType[errorType] = (byType[errorType] || 0) + 1
    })
    
    return {
      total: recentErrors.length,
      byType,
      recent: recentErrors.slice(-10).map(r => ({
        url: r.url,
        method: r.method,
        error: r.lastError?.message || '未知错误',
        time: new Date(r.startTime).toLocaleString()
      }))
    }
  }

  /**
   * 分类错误类型
   */
  private classifyError(error: any): string {
    if (!error) return '未知错误'
    
    const message = error.message?.toLowerCase() || ''
    
    if (message.includes('network') || message.includes('fetch')) {
      return '网络错误'
    }
    if (message.includes('timeout')) {
      return '超时错误'
    }
    if (message.includes('abort')) {
      return '请求取消'
    }
    if (error.response?.status) {
      const status = error.response.status
      if (status >= 400 && status < 500) {
        return '客户端错误'
      }
      if (status >= 500) {
        return '服务器错误'
      }
    }
    
    return '其他错误'
  }

  /**
   * 启动健康检查
   */
  private startHealthCheck() {
    setInterval(() => {
      const health = this.getServiceHealth()
      const unhealthyServices = Object.entries(health)
        .filter(([_, status]) => status.status === 'unhealthy')
      
      if (unhealthyServices.length > 0) {
        console.warn('🚨 服务健康检查警告:', unhealthyServices)
      }
      
      // 清理过期的历史记录
      const oneHourAgo = Date.now() - 60 * 60 * 1000
      this.requestHistory = this.requestHistory.filter(r => r.startTime > oneHourAgo)
      
    }, 60000) // 每分钟检查一次
  }

  /**
   * 导出诊断信息
   */
  exportDiagnostics() {
    return {
      activeRequests: Array.from(this.activeRequests.entries()),
      requestHistory: this.requestHistory.slice(-100),
      circuitBreakers: Array.from(this.circuitBreakers.entries()),
      serviceHealth: this.getServiceHealth(),
      errorStats: this.getErrorStats(),
      timestamp: new Date().toISOString()
    }
  }

  /**
   * 清空所有数据
   */
  clear() {
    this.activeRequests.clear()
    this.requestHistory = []
    this.circuitBreakers.clear()
  }
}

// 创建全局实例
export const requestManager = new RequestManager()

// Vue插件安装函数
export function setupRequestManager(app: any, config?: Partial<RequestConfig>) {
  const manager = new RequestManager(config)
  
  app.config.globalProperties.$requestManager = manager
  app.provide('requestManager', manager)
  
  console.log('✅ 请求管理器配置完成')
  
  return manager
}

export default requestManager
