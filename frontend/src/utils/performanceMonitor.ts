/**
 * 前端性能监控工具
 */

interface PerformanceMetric {
  name: string
  duration: number
  timestamp: number
  type: 'api' | 'component' | 'page' | 'custom'
  status?: 'success' | 'error' | 'timeout'
  details?: Record<string, any>
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = []
  private maxMetrics = 1000
  private observers: Map<string, PerformanceObserver> = new Map()

  constructor() {
    this.initializeObservers()
  }

  /**
   * 初始化性能观察器
   */
  private initializeObservers() {
    // 观察页面加载性能
    if ('PerformanceObserver' in window) {
      try {
        const navigationObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          entries.forEach((entry) => {
            this.addMetric({
              name: entry.name,
              duration: entry.duration,
              timestamp: Date.now(),
              type: 'page',
              details: {
                entryType: entry.entryType,
                startTime: entry.startTime
              }
            })
          })
        })
        navigationObserver.observe({ entryTypes: ['navigation'] })
        this.observers.set('navigation', navigationObserver)

        // 观察资源加载性能
        const resourceObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          entries.forEach((entry) => {
            if (entry.name.includes('/api/')) {
              this.addMetric({
                name: entry.name,
                duration: entry.duration,
                timestamp: Date.now(),
                type: 'api',
                status: entry.responseStatus >= 200 && entry.responseStatus < 300 ? 'success' : 'error',
                details: {
                  transferSize: (entry as any).transferSize,
                  responseStatus: (entry as any).responseStatus
                }
              })
            }
          })
        })
        resourceObserver.observe({ entryTypes: ['resource'] })
        this.observers.set('resource', resourceObserver)
      } catch (error) {
        console.warn('Performance Observer not supported:', error)
      }
    }
  }

  /**
   * 添加性能指标
   */
  addMetric(metric: PerformanceMetric) {
    this.metrics.push(metric)
    
    // 限制指标数量
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift()
    }

    // 实时报告慢请求
    if (metric.type === 'api' && metric.duration > 3000) {
      console.warn(`🐌 慢请求警告: ${metric.name} 耗时 ${metric.duration.toFixed(2)}ms`)
    }
  }

  /**
   * 测量函数执行时间
   */
  async measureAsync<T>(
    name: string, 
    fn: () => Promise<T>,
    type: PerformanceMetric['type'] = 'custom'
  ): Promise<T> {
    const startTime = performance.now()
    let status: PerformanceMetric['status'] = 'success'
    
    try {
      const result = await fn()
      return result
    } catch (error) {
      status = 'error'
      throw error
    } finally {
      const duration = performance.now() - startTime
      this.addMetric({
        name,
        duration,
        timestamp: Date.now(),
        type,
        status
      })
    }
  }

  /**
   * 测量同步函数执行时间
   */
  measure<T>(
    name: string, 
    fn: () => T,
    type: PerformanceMetric['type'] = 'custom'
  ): T {
    const startTime = performance.now()
    let status: PerformanceMetric['status'] = 'success'
    
    try {
      const result = fn()
      return result
    } catch (error) {
      status = 'error'
      throw error
    } finally {
      const duration = performance.now() - startTime
      this.addMetric({
        name,
        duration,
        timestamp: Date.now(),
        type,
        status
      })
    }
  }

  /**
   * 开始计时
   */
  startTimer(name: string): () => void {
    const startTime = performance.now()
    
    return (status: PerformanceMetric['status'] = 'success', details?: Record<string, any>) => {
      const duration = performance.now() - startTime
      this.addMetric({
        name,
        duration,
        timestamp: Date.now(),
        type: 'custom',
        status,
        details
      })
    }
  }

  /**
   * 获取性能统计
   */
  getStats() {
    const now = Date.now()
    const last5Minutes = now - 5 * 60 * 1000
    const recentMetrics = this.metrics.filter(m => m.timestamp > last5Minutes)

    const stats = {
      total: this.metrics.length,
      recent: recentMetrics.length,
      byType: {} as Record<string, number>,
      byStatus: {} as Record<string, number>,
      avgDuration: 0,
      slowRequests: 0,
      errorRate: 0
    }

    let totalDuration = 0
    let errorCount = 0

    recentMetrics.forEach(metric => {
      // 按类型统计
      stats.byType[metric.type] = (stats.byType[metric.type] || 0) + 1
      
      // 按状态统计
      if (metric.status) {
        stats.byStatus[metric.status] = (stats.byStatus[metric.status] || 0) + 1
        if (metric.status === 'error') {
          errorCount++
        }
      }

      // 计算平均时长
      totalDuration += metric.duration
      
      // 慢请求统计（超过2秒）
      if (metric.duration > 2000) {
        stats.slowRequests++
      }
    })

    stats.avgDuration = recentMetrics.length > 0 ? totalDuration / recentMetrics.length : 0
    stats.errorRate = recentMetrics.length > 0 ? (errorCount / recentMetrics.length) * 100 : 0

    return stats
  }

  /**
   * 获取慢请求列表
   */
  getSlowRequests(threshold = 2000, limit = 10) {
    return this.metrics
      .filter(m => m.duration > threshold)
      .sort((a, b) => b.duration - a.duration)
      .slice(0, limit)
  }

  /**
   * 获取错误请求列表
   */
  getErrorRequests(limit = 10) {
    return this.metrics
      .filter(m => m.status === 'error')
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit)
  }

  /**
   * 获取API性能分析
   */
  getApiAnalysis() {
    const apiMetrics = this.metrics.filter(m => m.type === 'api')
    const analysis: Record<string, {
      count: number
      avgDuration: number
      maxDuration: number
      minDuration: number
      errorCount: number
      successRate: number
    }> = {}

    apiMetrics.forEach(metric => {
      const url = this.normalizeApiUrl(metric.name)
      
      if (!analysis[url]) {
        analysis[url] = {
          count: 0,
          avgDuration: 0,
          maxDuration: 0,
          minDuration: Infinity,
          errorCount: 0,
          successRate: 0
        }
      }

      const stats = analysis[url]
      stats.count++
      stats.maxDuration = Math.max(stats.maxDuration, metric.duration)
      stats.minDuration = Math.min(stats.minDuration, metric.duration)
      
      if (metric.status === 'error') {
        stats.errorCount++
      }
      
      // 计算平均时长（滑动平均）
      stats.avgDuration = (stats.avgDuration * (stats.count - 1) + metric.duration) / stats.count
      stats.successRate = ((stats.count - stats.errorCount) / stats.count) * 100
    })

    return analysis
  }

  /**
   * 标准化API URL（去除参数和ID）
   */
  private normalizeApiUrl(url: string): string {
    return url
      .replace(/\/\d+/g, '/:id') // 替换数字ID
      .replace(/\?.*$/, '') // 移除查询参数
      .replace(/\/api\/v\d+/, '') // 移除API版本前缀
  }

  /**
   * 导出性能数据
   */
  exportData() {
    return {
      metrics: this.metrics,
      stats: this.getStats(),
      slowRequests: this.getSlowRequests(),
      errorRequests: this.getErrorRequests(),
      apiAnalysis: this.getApiAnalysis(),
      timestamp: new Date().toISOString()
    }
  }

  /**
   * 清空指标数据
   */
  clear() {
    this.metrics = []
  }

  /**
   * 销毁监控器
   */
  destroy() {
    this.observers.forEach(observer => {
      observer.disconnect()
    })
    this.observers.clear()
    this.metrics = []
  }

  /**
   * 检查性能健康状态
   */
  getHealthStatus() {
    const stats = this.getStats()
    
    let status: 'healthy' | 'warning' | 'critical' = 'healthy'
    const issues: string[] = []

    // 检查错误率
    if (stats.errorRate > 10) {
      status = 'critical'
      issues.push(`错误率过高: ${stats.errorRate.toFixed(1)}%`)
    } else if (stats.errorRate > 5) {
      status = 'warning'
      issues.push(`错误率偏高: ${stats.errorRate.toFixed(1)}%`)
    }

    // 检查平均响应时间
    if (stats.avgDuration > 3000) {
      status = 'critical'
      issues.push(`平均响应时间过长: ${stats.avgDuration.toFixed(0)}ms`)
    } else if (stats.avgDuration > 1500) {
      if (status !== 'critical') status = 'warning'
      issues.push(`平均响应时间偏长: ${stats.avgDuration.toFixed(0)}ms`)
    }

    // 检查慢请求比例
    const slowRequestRate = stats.recent > 0 ? (stats.slowRequests / stats.recent) * 100 : 0
    if (slowRequestRate > 20) {
      status = 'critical'
      issues.push(`慢请求比例过高: ${slowRequestRate.toFixed(1)}%`)
    } else if (slowRequestRate > 10) {
      if (status !== 'critical') status = 'warning'
      issues.push(`慢请求比例偏高: ${slowRequestRate.toFixed(1)}%`)
    }

    return {
      status,
      issues,
      stats
    }
  }
}

// 创建全局实例
export const performanceMonitor = new PerformanceMonitor()

// Vue插件安装函数
export function setupPerformanceMonitor(app: any) {
  app.config.globalProperties.$perf = performanceMonitor
  app.provide('performanceMonitor', performanceMonitor)
  
  // 定期输出性能报告（仅在开发环境）
  if (import.meta.env.DEV) {
    setInterval(() => {
      const health = performanceMonitor.getHealthStatus()
      if (health.status !== 'healthy') {
        console.warn('🚨 性能警告:', health)
      } else {
        console.log('✅ 性能状态良好:', health.stats)
      }
    }, 60000) // 每分钟检查一次
  }
  
  console.log('✅ 性能监控器配置完成')
}

export default performanceMonitor
