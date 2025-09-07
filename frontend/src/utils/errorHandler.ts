import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'

// ======== 错误类型定义 ========
export enum ErrorType {
  NETWORK = 'NETWORK',
  API = 'API',
  VALIDATION = 'VALIDATION',
  PERMISSION = 'PERMISSION',
  BUSINESS = 'BUSINESS',
  UNKNOWN = 'UNKNOWN'
}

export enum ErrorLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface ErrorInfo {
  id?: string
  type: ErrorType
  level: ErrorLevel
  message: string
  detail?: string
  code?: string | number
  timestamp?: number
  context?: Record<string, any>
  stack?: string
  source?: string
  userId?: string
  sessionId?: string
  url?: string
  userAgent?: string
}

export interface ErrorHandlerConfig {
  enableConsoleLog?: boolean
  enableNotification?: boolean
  enableReporting?: boolean
  reportUrl?: string
  maxErrorQueue?: number
  showRetryButton?: boolean
  autoRetry?: boolean
  maxRetryAttempts?: number
  retryDelay?: number
  silentErrors?: ErrorType[]
}

// ======== 错误处理器类 ========
export class ErrorHandler {
  private config: ErrorHandlerConfig
  private errorQueue: ErrorInfo[] = []
  private retryMap = new Map<string, number>()
  private listeners: Set<(error: ErrorInfo) => void> = new Set()

  constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = {
      enableConsoleLog: true,
      enableNotification: true,
      enableReporting: false,
      maxErrorQueue: 100,
      showRetryButton: true,
      autoRetry: false,
      maxRetryAttempts: 3,
      retryDelay: 1000,
      silentErrors: [],
      ...config
    }
  }

  /**
   * 处理错误
   */
  handle(error: Error | ErrorInfo | string, context?: Record<string, any>): void {
    const errorInfo = this.normalizeError(error, context)
    
    // 添加到错误队列
    this.addToQueue(errorInfo)
    
    // 控制台日志
    if (this.config.enableConsoleLog) {
      this.logToConsole(errorInfo)
    }
    
    // 显示通知
    if (this.config.enableNotification && !this.isSilentError(errorInfo.type)) {
      this.showNotification(errorInfo)
    }
    
    // 上报错误
    if (this.config.enableReporting) {
      this.reportError(errorInfo)
    }
    
    // 通知监听器
    this.notifyListeners(errorInfo)
  }

  /**
   * 规范化错误信息
   */
  private normalizeError(error: Error | ErrorInfo | string, context?: Record<string, any>): ErrorInfo {
    if (typeof error === 'string') {
      return {
        id: this.generateErrorId(),
        type: ErrorType.UNKNOWN,
        level: ErrorLevel.MEDIUM,
        message: error,
        timestamp: Date.now(),
        context: context || {},
        url: window.location.href,
        userAgent: navigator.userAgent
      }
    }
    
    if (error instanceof Error) {
      return {
        id: this.generateErrorId(),
        type: this.classifyError(error),
        level: this.assessErrorLevel(error),
        message: error.message,
        detail: error.name,
        stack: error.stack || '',
        timestamp: Date.now(),
        context: context || {},
        url: window.location.href,
        userAgent: navigator.userAgent
      }
    }
    
    // 如果已经是 ErrorInfo 对象
    return {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      ...error
    }
  }

  /**
   * 分类错误类型
   */
  private classifyError(error: Error): ErrorType {
    const message = error.message.toLowerCase()
    const name = error.name.toLowerCase()
    
    if (name.includes('network') || message.includes('network') || message.includes('fetch')) {
      return ErrorType.NETWORK
    }
    
    if (message.includes('permission') || message.includes('unauthorized') || message.includes('forbidden')) {
      return ErrorType.PERMISSION
    }
    
    if (message.includes('validation') || message.includes('invalid')) {
      return ErrorType.VALIDATION
    }
    
    if (message.includes('api') || message.includes('server')) {
      return ErrorType.API
    }
    
    return ErrorType.UNKNOWN
  }

  /**
   * 评估错误级别
   */
  private assessErrorLevel(error: Error): ErrorLevel {
    const message = error.message.toLowerCase()
    
    if (message.includes('critical') || message.includes('fatal') || message.includes('crash')) {
      return ErrorLevel.CRITICAL
    }
    
    if (message.includes('error') || message.includes('failed')) {
      return ErrorLevel.HIGH
    }
    
    if (message.includes('warning') || message.includes('deprecated')) {
      return ErrorLevel.MEDIUM
    }
    
    return ErrorLevel.LOW
  }

  /**
   * 生成错误ID
   */
  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 添加到错误队列
   */
  private addToQueue(errorInfo: ErrorInfo): void {
    this.errorQueue.push(errorInfo)
    
    // 限制队列大小
    if (this.errorQueue.length > this.config.maxErrorQueue!) {
      this.errorQueue.shift()
    }
  }

  /**
   * 控制台日志
   */
  private logToConsole(errorInfo: ErrorInfo): void {
    const logMethod = this.getLogMethod(errorInfo.level)
    
    console.group(`🚨 ${errorInfo.type} Error (${errorInfo.level})`)
    console[logMethod]('Message:', errorInfo.message)
    
    if (errorInfo.detail) {
      console[logMethod]('Detail:', errorInfo.detail)
    }
    
    if (errorInfo.code) {
      console[logMethod]('Code:', errorInfo.code)
    }
    
    if (errorInfo.context) {
      console[logMethod]('Context:', errorInfo.context)
    }
    
    if (errorInfo.stack) {
      console[logMethod]('Stack:', errorInfo.stack)
    }
    
    console.groupEnd()
  }

  /**
   * 获取日志方法
   */
  private getLogMethod(level: ErrorLevel): 'log' | 'warn' | 'error' {
    switch (level) {
      case ErrorLevel.CRITICAL:
      case ErrorLevel.HIGH:
        return 'error'
      case ErrorLevel.MEDIUM:
        return 'warn'
      default:
        return 'log'
    }
  }

  /**
   * 显示通知
   */
  private showNotification(errorInfo: ErrorInfo): void {
    const { type, level, message } = errorInfo
    
    // 根据错误级别选择通知方式
    switch (level) {
      case ErrorLevel.CRITICAL:
        this.showCriticalError(errorInfo)
        break
        
      case ErrorLevel.HIGH:
        ElNotification({
          title: this.getErrorTitle(type),
          message: message,
          type: 'error',
          duration: 0, // 不自动关闭
          showClose: true
        })
        break
        
      case ErrorLevel.MEDIUM:
        ElMessage({
          type: 'warning',
          message: message,
          duration: 5000,
          showClose: true
        })
        break
        
      case ErrorLevel.LOW:
        ElMessage({
          type: 'info',
          message: message,
          duration: 3000
        })
        break
    }
  }

  /**
   * 显示严重错误对话框
   */
  private showCriticalError(errorInfo: ErrorInfo): void {
    ElMessageBox.alert(
      `${errorInfo.message}${errorInfo.detail ? `\n\n详细信息：${errorInfo.detail}` : ''}`,
      '系统错误',
      {
        type: 'error',
        dangerouslyUseHTMLString: false,
        showCancelButton: this.config.showRetryButton,
        confirmButtonText: '确定',
        cancelButtonText: '重试'
      }
    ).catch(() => {
      // 重试按钮逻辑
      if (this.config.showRetryButton) {
        this.handleRetry(errorInfo)
      }
    })
  }

  /**
   * 获取错误标题
   */
  private getErrorTitle(type: ErrorType): string {
    const titles = {
      [ErrorType.NETWORK]: '网络错误',
      [ErrorType.API]: 'API错误',
      [ErrorType.VALIDATION]: '验证错误',
      [ErrorType.PERMISSION]: '权限错误',
      [ErrorType.BUSINESS]: '业务错误',
      [ErrorType.UNKNOWN]: '未知错误'
    }
    
    return titles[type] || '系统错误'
  }

  /**
   * 处理重试
   */
  private handleRetry(errorInfo: ErrorInfo): void {
    const retryKey = errorInfo.id || 'unknown'
    const currentAttempts = this.retryMap.get(retryKey) || 0
    
    if (currentAttempts >= this.config.maxRetryAttempts!) {
      ElMessage.error('重试次数已达上限')
      return
    }
    
    this.retryMap.set(retryKey, currentAttempts + 1)
    
    setTimeout(() => {
      // 触发重试事件
      this.notifyListeners({
        ...errorInfo,
        type: ErrorType.UNKNOWN,
        message: 'RETRY_REQUESTED'
      })
    }, this.config.retryDelay)
  }

  /**
   * 上报错误
   */
  private async reportError(errorInfo: ErrorInfo): Promise<void> {
    if (!this.config.reportUrl) return
    
    try {
      await fetch(this.config.reportUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...errorInfo,
          timestamp: Date.now(),
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      })
    } catch (error) {
      console.warn('错误上报失败:', error)
    }
  }

  /**
   * 是否为静默错误
   */
  private isSilentError(type: ErrorType): boolean {
    return this.config.silentErrors!.includes(type)
  }

  /**
   * 添加错误监听器
   */
  addListener(listener: (error: ErrorInfo) => void): () => void {
    this.listeners.add(listener)
    
    // 返回移除监听器的函数
    return () => {
      this.listeners.delete(listener)
    }
  }

  /**
   * 通知监听器
   */
  private notifyListeners(errorInfo: ErrorInfo): void {
    this.listeners.forEach(listener => {
      try {
        listener(errorInfo)
      } catch (error) {
        console.warn('错误监听器执行失败:', error)
      }
    })
  }

  /**
   * 获取错误队列
   */
  getErrorQueue(): ErrorInfo[] {
    return [...this.errorQueue]
  }

  /**
   * 清空错误队列
   */
  clearErrorQueue(): void {
    this.errorQueue.length = 0
  }

  /**
   * 获取错误统计
   */
  getErrorStats(): Record<string, any> {
    const stats = {
      total: this.errorQueue.length,
      byType: {} as Record<ErrorType, number>,
      byLevel: {} as Record<ErrorLevel, number>,
      recent: this.errorQueue.slice(-10)
    }
    
    this.errorQueue.forEach(error => {
      stats.byType[error.type] = (stats.byType[error.type] || 0) + 1
      stats.byLevel[error.level] = (stats.byLevel[error.level] || 0) + 1
    })
    
    return stats
  }
}

// ======== 全局错误处理器实例 ========
export const globalErrorHandler = new ErrorHandler()

// ======== Vue插件安装函数 ========
export function setupErrorHandler(app: any, config?: Partial<ErrorHandlerConfig>) {
  // 更新配置
  if (config) {
    Object.assign(globalErrorHandler['config'], config)
  }
  
  // Vue错误处理
  app.config.errorHandler = (error: any, instance: any, info: string) => {
    globalErrorHandler.handle(error, {
      component: instance?.$options.name || 'Unknown',
      errorInfo: info,
      source: 'vue'
    })
  }
  
  // 全局未捕获错误
  window.addEventListener('error', (event) => {
    globalErrorHandler.handle(event.error || event.message, {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      source: 'window'
    })
  })
  
  // Promise未捕获拒绝
  window.addEventListener('unhandledrejection', (event) => {
    globalErrorHandler.handle(event.reason, {
      source: 'promise'
    })
  })
  
  // 注入到全局属性
  app.config.globalProperties.$errorHandler = globalErrorHandler
  app.provide('errorHandler', globalErrorHandler)
  
  console.log('✅ 错误处理器配置完成')
}

// ======== 工具函数 ========

/**
 * 安全执行函数，自动捕获错误
 */
export async function safeExecute<T>(
  fn: () => T | Promise<T>,
  fallback?: T,
  context?: Record<string, any>
): Promise<T | undefined> {
  try {
    return await fn()
  } catch (error) {
    globalErrorHandler.handle(error as Error, context)
    return fallback
  }
}

export default {
  setupErrorHandler,
  globalErrorHandler,
  ErrorType,
  ErrorLevel,
  safeExecute
}