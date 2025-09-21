/**
 * 系统诊断工具 - 检测和解决前端系统问题
 */

import { requestManager } from './requestManager'
import { performanceMonitor } from './performanceMonitor'
import { globalErrorHandler } from './errorHandler'
import apiService from '@/services/api'

interface DiagnosticResult {
  category: string
  name: string
  status: 'healthy' | 'warning' | 'error'
  message: string
  details?: any
  suggestions?: string[]
  timestamp: number
}

interface SystemHealth {
  overall: 'healthy' | 'warning' | 'critical'
  score: number
  results: DiagnosticResult[]
  summary: {
    healthy: number
    warning: number
    error: number
  }
}

class SystemDiagnostics {
  private diagnostics: DiagnosticResult[] = []
  
  /**
   * 运行完整的系统诊断
   */
  async runFullDiagnostic(): Promise<SystemHealth> {
    console.log('🔍 开始系统诊断...')
    
    this.diagnostics = []
    
    // 并行运行所有诊断
    const diagnosticPromises = [
      this.checkNetworkConnectivity(),
      this.checkAPIEndpoints(),
      this.checkPerformanceMetrics(),
      this.checkErrorRates(),
      this.checkBrowserCompatibility(),
      this.checkMemoryUsage(),
      this.checkLocalStorage(),
      this.checkConsoleErrors()
    ]
    
    await Promise.allSettled(diagnosticPromises)
    
    // 计算健康分数和状态
    const health = this.calculateHealthScore()
    
    console.log('✅ 系统诊断完成:', health)
    return health
  }
  
  /**
   * 检查网络连接
   */
  private async checkNetworkConnectivity(): Promise<void> {
    try {
      const online = navigator.onLine
      const startTime = performance.now()
      
      // 测试到后端的连接
      const response = await fetch('/api/v1/system/health', {
        method: 'GET',
        cache: 'no-cache'
      })
      
      const responseTime = performance.now() - startTime
      
      if (!online) {
        this.addResult({
          category: '网络连接',
          name: '网络状态',
          status: 'error',
          message: '设备处于离线状态',
          suggestions: ['检查网络连接', '确认WiFi或网线连接正常']
        })
      } else if (!response.ok) {
        this.addResult({
          category: '网络连接',
          name: '后端连接',
          status: 'error',
          message: `后端服务不可达 (HTTP ${response.status})`,
          details: { responseTime, status: response.status },
          suggestions: ['检查后端服务是否运行', '确认API地址配置正确', '检查防火墙设置']
        })
      } else if (responseTime > 3000) {
        this.addResult({
          category: '网络连接',
          name: '连接速度',
          status: 'warning',
          message: `网络延迟较高 (${responseTime.toFixed(0)}ms)`,
          details: { responseTime },
          suggestions: ['检查网络质量', '尝试刷新页面', '联系网络管理员']
        })
      } else {
        this.addResult({
          category: '网络连接',
          name: '网络状态',
          status: 'healthy',
          message: `连接正常 (${responseTime.toFixed(0)}ms)`,
          details: { responseTime }
        })
      }
    } catch (error) {
      this.addResult({
        category: '网络连接',
        name: '连接测试',
        status: 'error',
        message: '无法连接到后端服务',
        details: { error: error.message },
        suggestions: ['检查后端服务状态', '确认代理配置正确', '检查CORS设置']
      })
    }
  }
  
  /**
   * 检查API端点
   */
  private async checkAPIEndpoints(): Promise<void> {
    const criticalEndpoints = [
      { name: 'Prometheus配置', endpoint: '/prometheus/config' },
      { name: '系统信息', endpoint: '/system/info' },
      { name: '健康检查', endpoint: '/system/health' }
    ]
    
    for (const { name, endpoint } of criticalEndpoints) {
      try {
        const startTime = performance.now()
        const response = await apiService.get(endpoint)
        const responseTime = performance.now() - startTime
        
        if (response && response.success !== false) {
          this.addResult({
            category: 'API端点',
            name,
            status: 'healthy',
            message: `API响应正常 (${responseTime.toFixed(0)}ms)`,
            details: { endpoint, responseTime, hasData: !!response.data }
          })
        } else {
          this.addResult({
            category: 'API端点',
            name,
            status: 'warning',
            message: 'API返回异常响应',
            details: { endpoint, response },
            suggestions: ['检查API实现', '确认数据格式正确']
          })
        }
      } catch (error) {
        this.addResult({
          category: 'API端点',
          name,
          status: 'error',
          message: `API调用失败: ${error.message}`,
          details: { endpoint, error: error.message },
          suggestions: ['检查端点是否存在', '确认权限设置', '查看后端日志']
        })
      }
    }
  }
  
  /**
   * 检查性能指标
   */
  private async checkPerformanceMetrics(): Promise<void> {
    const stats = performanceMonitor.getStats()
    const health = performanceMonitor.getHealthStatus()
    
    if (health.status === 'critical') {
      this.addResult({
        category: '性能指标',
        name: '整体性能',
        status: 'error',
        message: '性能状况严重',
        details: { stats, issues: health.issues },
        suggestions: [
          '清理浏览器缓存',
          '关闭其他标签页',
          '检查网络连接',
          '联系技术支持'
        ]
      })
    } else if (health.status === 'warning') {
      this.addResult({
        category: '性能指标',
        name: '整体性能',
        status: 'warning',
        message: '性能需要优化',
        details: { stats, issues: health.issues },
        suggestions: [
          '刷新页面重试',
          '检查网络稳定性',
          '清理浏览器数据'
        ]
      })
    } else {
      this.addResult({
        category: '性能指标',
        name: '整体性能',
        status: 'healthy',
        message: '性能状况良好',
        details: { stats }
      })
    }
    
    // 检查慢请求
    const slowRequests = performanceMonitor.getSlowRequests(2000, 5)
    if (slowRequests.length > 0) {
      this.addResult({
        category: '性能指标',
        name: '慢请求',
        status: 'warning',
        message: `发现 ${slowRequests.length} 个慢请求`,
        details: { slowRequests },
        suggestions: ['优化API查询', '检查数据库性能', '考虑添加缓存']
      })
    }
  }
  
  /**
   * 检查错误率
   */
  private async checkErrorRates(): Promise<void> {
    const errorStats = requestManager.getErrorStats()
    const serviceHealth = requestManager.getServiceHealth()
    
    const totalErrors = errorStats.total
    const errorRate = totalErrors > 0 ? (totalErrors / (totalErrors + 100)) * 100 : 0
    
    if (errorRate > 20) {
      this.addResult({
        category: '错误率',
        name: '请求错误',
        status: 'error',
        message: `错误率过高 (${errorRate.toFixed(1)}%)`,
        details: { errorStats, serviceHealth },
        suggestions: [
          '检查后端服务状态',
          '确认API配置正确',
          '查看错误日志详情',
          '联系技术支持'
        ]
      })
    } else if (errorRate > 5) {
      this.addResult({
        category: '错误率',
        name: '请求错误',
        status: 'warning',
        message: `错误率偏高 (${errorRate.toFixed(1)}%)`,
        details: { errorStats },
        suggestions: ['监控错误趋势', '检查网络稳定性']
      })
    } else {
      this.addResult({
        category: '错误率',
        name: '请求错误',
        status: 'healthy',
        message: `错误率正常 (${errorRate.toFixed(1)}%)`,
        details: { errorStats }
      })
    }
    
    // 检查不健康的服务
    const unhealthyServices = Object.entries(serviceHealth)
      .filter(([_, health]) => health.status === 'unhealthy')
    
    if (unhealthyServices.length > 0) {
      this.addResult({
        category: '错误率',
        name: '服务健康',
        status: 'error',
        message: `${unhealthyServices.length} 个服务不健康`,
        details: { unhealthyServices },
        suggestions: [
          '检查对应的后端服务',
          '确认服务配置正确',
          '查看服务日志'
        ]
      })
    }
  }
  
  /**
   * 检查浏览器兼容性
   */
  private async checkBrowserCompatibility(): Promise<void> {
    const issues: string[] = []
    const warnings: string[] = []
    
    // 检查关键API支持
    if (!window.fetch) {
      issues.push('不支持 Fetch API')
    }
    
    if (!window.Promise) {
      issues.push('不支持 Promise')
    }
    
    if (!window.localStorage) {
      issues.push('不支持 LocalStorage')
    }
    
    if (!window.sessionStorage) {
      warnings.push('不支持 SessionStorage')
    }
    
    if (!('PerformanceObserver' in window)) {
      warnings.push('不支持 Performance Observer')
    }
    
    // 检查浏览器版本
    const userAgent = navigator.userAgent
    const isOldBrowser = /MSIE|Trident/.test(userAgent) || 
                        /Chrome\/[1-5][0-9]\./.test(userAgent) ||
                        /Firefox\/[1-5][0-9]\./.test(userAgent)
    
    if (isOldBrowser) {
      warnings.push('浏览器版本较旧，建议升级')
    }
    
    if (issues.length > 0) {
      this.addResult({
        category: '浏览器兼容性',
        name: 'API支持',
        status: 'error',
        message: '浏览器不支持关键功能',
        details: { issues, warnings, userAgent },
        suggestions: [
          '升级到现代浏览器',
          '推荐使用 Chrome、Firefox、Safari 或 Edge 最新版本'
        ]
      })
    } else if (warnings.length > 0) {
      this.addResult({
        category: '浏览器兼容性',
        name: '功能支持',
        status: 'warning',
        message: '部分功能可能受限',
        details: { warnings, userAgent },
        suggestions: ['考虑升级浏览器以获得更好体验']
      })
    } else {
      this.addResult({
        category: '浏览器兼容性',
        name: '兼容性检查',
        status: 'healthy',
        message: '浏览器兼容性良好',
        details: { userAgent }
      })
    }
  }
  
  /**
   * 检查内存使用情况
   */
  private async checkMemoryUsage(): Promise<void> {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024)
      const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024)
      const limitMB = Math.round(memory.jsHeapSizeLimit / 1024 / 1024)
      
      const usagePercent = (usedMB / limitMB) * 100
      
      if (usagePercent > 80) {
        this.addResult({
          category: '内存使用',
          name: '内存占用',
          status: 'error',
          message: `内存使用率过高 (${usagePercent.toFixed(1)}%)`,
          details: { usedMB, totalMB, limitMB, usagePercent },
          suggestions: [
            '刷新页面释放内存',
            '关闭其他标签页',
            '清理浏览器缓存'
          ]
        })
      } else if (usagePercent > 60) {
        this.addResult({
          category: '内存使用',
          name: '内存占用',
          status: 'warning',
          message: `内存使用率偏高 (${usagePercent.toFixed(1)}%)`,
          details: { usedMB, totalMB, limitMB, usagePercent },
          suggestions: ['监控内存使用情况', '考虑刷新页面']
        })
      } else {
        this.addResult({
          category: '内存使用',
          name: '内存占用',
          status: 'healthy',
          message: `内存使用正常 (${usedMB}MB/${limitMB}MB)`,
          details: { usedMB, totalMB, limitMB, usagePercent }
        })
      }
    } else {
      this.addResult({
        category: '内存使用',
        name: '内存监控',
        status: 'warning',
        message: '无法获取内存使用信息',
        suggestions: ['浏览器不支持内存API']
      })
    }
  }
  
  /**
   * 检查本地存储
   */
  private async checkLocalStorage(): Promise<void> {
    try {
      const testKey = '__diagnostic_test__'
      localStorage.setItem(testKey, 'test')
      localStorage.removeItem(testKey)
      
      // 检查存储使用情况
      let totalSize = 0
      for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
          totalSize += localStorage[key].length + key.length
        }
      }
      
      const sizeMB = totalSize / 1024 / 1024
      
      if (sizeMB > 8) {
        this.addResult({
          category: '本地存储',
          name: '存储空间',
          status: 'warning',
          message: `本地存储使用较多 (${sizeMB.toFixed(2)}MB)`,
          details: { sizeMB, totalSize },
          suggestions: ['清理过期的本地数据', '考虑清空浏览器存储']
        })
      } else {
        this.addResult({
          category: '本地存储',
          name: '存储功能',
          status: 'healthy',
          message: `本地存储正常 (${sizeMB.toFixed(2)}MB)`,
          details: { sizeMB, totalSize }
        })
      }
    } catch (error) {
      this.addResult({
        category: '本地存储',
        name: '存储测试',
        status: 'error',
        message: '本地存储不可用',
        details: { error: error.message },
        suggestions: [
          '检查浏览器隐私设置',
          '确保未禁用本地存储',
          '尝试无痕模式'
        ]
      })
    }
  }
  
  /**
   * 检查控制台错误
   */
  private async checkConsoleErrors(): Promise<void> {
    const errorQueue = globalErrorHandler.getErrorQueue()
    const recentErrors = errorQueue.filter(e => Date.now() - e.timestamp < 5 * 60 * 1000)
    
    if (recentErrors.length > 10) {
      this.addResult({
        category: '控制台错误',
        name: '错误数量',
        status: 'error',
        message: `发现大量错误 (${recentErrors.length}个)`,
        details: { recentErrors: recentErrors.slice(0, 5) },
        suggestions: [
          '查看详细错误信息',
          '刷新页面重试',
          '联系技术支持'
        ]
      })
    } else if (recentErrors.length > 3) {
      this.addResult({
        category: '控制台错误',
        name: '错误数量',
        status: 'warning',
        message: `发现一些错误 (${recentErrors.length}个)`,
        details: { recentErrors },
        suggestions: ['监控错误情况', '必要时刷新页面']
      })
    } else {
      this.addResult({
        category: '控制台错误',
        name: '错误监控',
        status: 'healthy',
        message: `错误数量正常 (${recentErrors.length}个)`,
        details: { recentErrors }
      })
    }
  }
  
  /**
   * 添加诊断结果
   */
  private addResult(result: Omit<DiagnosticResult, 'timestamp'>): void {
    this.diagnostics.push({
      ...result,
      timestamp: Date.now()
    })
  }
  
  /**
   * 计算健康分数
   */
  private calculateHealthScore(): SystemHealth {
    const total = this.diagnostics.length
    const healthy = this.diagnostics.filter(d => d.status === 'healthy').length
    const warning = this.diagnostics.filter(d => d.status === 'warning').length
    const error = this.diagnostics.filter(d => d.status === 'error').length
    
    const score = total > 0 ? Math.round(((healthy + warning * 0.5) / total) * 100) : 100
    
    let overall: 'healthy' | 'warning' | 'critical' = 'healthy'
    if (error > 0 || score < 60) {
      overall = 'critical'
    } else if (warning > 0 || score < 80) {
      overall = 'warning'
    }
    
    return {
      overall,
      score,
      results: this.diagnostics,
      summary: {
        healthy,
        warning,
        error
      }
    }
  }
  
  /**
   * 生成诊断报告
   */
  generateReport(health: SystemHealth): string {
    const report = [
      '=== 系统诊断报告 ===',
      `生成时间: ${new Date().toLocaleString()}`,
      `整体状态: ${health.overall.toUpperCase()}`,
      `健康分数: ${health.score}/100`,
      '',
      '=== 检查项目 ===',
      `✅ 正常: ${health.summary.healthy}`,
      `⚠️  警告: ${health.summary.warning}`,
      `❌ 错误: ${health.summary.error}`,
      '',
      '=== 详细结果 ===',
      ...health.results.map(result => {
        const icon = result.status === 'healthy' ? '✅' : 
                    result.status === 'warning' ? '⚠️' : '❌'
        const lines = [
          `${icon} [${result.category}] ${result.name}: ${result.message}`
        ]
        if (result.suggestions && result.suggestions.length > 0) {
          lines.push(`   建议: ${result.suggestions.join(', ')}`)
        }
        return lines.join('\n')
      })
    ]
    
    return report.join('\n')
  }
  
  /**
   * 导出诊断数据
   */
  exportDiagnosticData(health: SystemHealth) {
    const data = {
      ...health,
      browser: {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine
      },
      performance: performanceMonitor.exportData(),
      requests: requestManager.exportDiagnostics(),
      errors: globalErrorHandler.getErrorStats(),
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `system-diagnostic-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }
  
  /**
   * 清空诊断历史
   */
  clear(): void {
    this.diagnostics = []
  }
}

// 创建全局实例
export const systemDiagnostics = new SystemDiagnostics()

// Vue组合式API钩子
export function useSystemDiagnostics() {
  return {
    runDiagnostic: () => systemDiagnostics.runFullDiagnostic(),
    generateReport: (health: SystemHealth) => systemDiagnostics.generateReport(health),
    exportData: (health: SystemHealth) => systemDiagnostics.exportDiagnosticData(health),
    clear: () => systemDiagnostics.clear()
  }
}

export default systemDiagnostics
