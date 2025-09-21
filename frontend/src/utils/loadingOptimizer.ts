/**
 * 页面加载优化器 - 解决页面加载卡顿问题
 */

import { ref, nextTick } from 'vue'
import { ElLoading } from 'element-plus'

interface LoadingTask {
  id: string
  name: string
  priority: number
  execute: () => Promise<any>
  dependencies?: string[]
  timeout?: number
  retryCount?: number
}

interface LoadingState {
  isLoading: boolean
  progress: number
  currentTask: string
  completedTasks: string[]
  failedTasks: string[]
}

class LoadingOptimizer {
  private tasks: Map<string, LoadingTask> = new Map()
  private state = ref<LoadingState>({
    isLoading: false,
    progress: 0,
    currentTask: '',
    completedTasks: [],
    failedTasks: []
  })
  private loadingInstance: any = null
  private abortController: AbortController | null = null

  /**
   * 添加加载任务
   */
  addTask(task: LoadingTask): void {
    this.tasks.set(task.id, {
      priority: 1,
      timeout: 10000,
      retryCount: 0,
      ...task
    })
  }

  /**
   * 批量添加任务
   */
  addTasks(tasks: LoadingTask[]): void {
    tasks.forEach(task => this.addTask(task))
  }

  /**
   * 执行所有任务
   */
  async executeAll(showLoading = true): Promise<{
    success: string[]
    failed: string[]
    results: Record<string, any>
  }> {
    if (this.state.value.isLoading) {
      console.warn('加载器已在运行中')
      return { success: [], failed: [], results: {} }
    }

    this.state.value.isLoading = true
    this.state.value.progress = 0
    this.state.value.completedTasks = []
    this.state.value.failedTasks = []
    
    this.abortController = new AbortController()

    if (showLoading) {
      this.showGlobalLoading()
    }

    const results: Record<string, any> = {}
    const executionPlan = this.createExecutionPlan()

    try {
      let completedCount = 0
      const totalTasks = executionPlan.length

      for (const batch of executionPlan) {
        // 并行执行同批次任务
        const batchPromises = batch.map(async (taskId) => {
          const task = this.tasks.get(taskId)!
          return this.executeTask(task)
        })

        const batchResults = await Promise.allSettled(batchPromises)
        
        batchResults.forEach((result, index) => {
          const taskId = batch[index]
          const task = this.tasks.get(taskId)!
          
          if (result.status === 'fulfilled') {
            this.state.value.completedTasks.push(taskId)
            results[taskId] = result.value
            console.log(`✅ 任务完成: ${task.name}`)
          } else {
            this.state.value.failedTasks.push(taskId)
            console.error(`❌ 任务失败: ${task.name}`, result.reason)
          }
          
          completedCount++
          this.state.value.progress = (completedCount / totalTasks) * 100
          this.state.value.currentTask = task.name
        })

        // 给UI一个更新的机会
        await nextTick()
      }

    } catch (error) {
      console.error('任务执行过程中发生错误:', error)
    } finally {
      this.state.value.isLoading = false
      this.state.value.progress = 100
      this.state.value.currentTask = ''
      
      if (showLoading && this.loadingInstance) {
        this.loadingInstance.close()
        this.loadingInstance = null
      }
    }

    return {
      success: this.state.value.completedTasks,
      failed: this.state.value.failedTasks,
      results
    }
  }

  /**
   * 执行单个任务
   */
  private async executeTask(task: LoadingTask): Promise<any> {
    const timeout = task.timeout || 10000
    const maxRetries = 3

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error(`任务超时: ${task.name}`)), timeout)
        })

        const taskPromise = task.execute()
        
        // 添加取消支持
        if (this.abortController?.signal.aborted) {
          throw new Error('任务已被取消')
        }

        const result = await Promise.race([taskPromise, timeoutPromise])
        return result

      } catch (error) {
        if (attempt < maxRetries) {
          console.warn(`⚠️ 任务重试 ${attempt + 1}/${maxRetries}: ${task.name}`)
          await this.delay(1000 * (attempt + 1)) // 指数退避
          continue
        }
        throw error
      }
    }
  }

  /**
   * 创建执行计划（按依赖关系和优先级排序）
   */
  private createExecutionPlan(): string[][] {
    const tasks = Array.from(this.tasks.values())
    const plan: string[][] = []
    const completed = new Set<string>()
    
    // 按优先级排序
    const sortedTasks = tasks.sort((a, b) => b.priority - a.priority)
    
    while (completed.size < tasks.length) {
      const currentBatch: string[] = []
      
      for (const task of sortedTasks) {
        if (completed.has(task.id)) continue
        
        // 检查依赖是否都已完成
        const dependenciesMet = !task.dependencies || 
          task.dependencies.every(dep => completed.has(dep))
        
        if (dependenciesMet) {
          currentBatch.push(task.id)
          completed.add(task.id)
        }
      }
      
      if (currentBatch.length === 0) {
        // 防止无限循环，添加剩余任务
        const remaining = sortedTasks.filter(t => !completed.has(t.id))
        if (remaining.length > 0) {
          currentBatch.push(remaining[0].id)
          completed.add(remaining[0].id)
        }
      }
      
      if (currentBatch.length > 0) {
        plan.push(currentBatch)
      }
    }
    
    return plan
  }

  /**
   * 显示全局加载状态
   */
  private showGlobalLoading(): void {
    this.loadingInstance = ElLoading.service({
      lock: true,
      text: '正在加载系统数据...',
      background: 'rgba(0, 0, 0, 0.7)',
      customClass: 'loading-optimizer-overlay'
    })
  }

  /**
   * 取消所有任务
   */
  cancel(): void {
    if (this.abortController) {
      this.abortController.abort()
    }
    
    this.state.value.isLoading = false
    
    if (this.loadingInstance) {
      this.loadingInstance.close()
      this.loadingInstance = null
    }
  }

  /**
   * 获取加载状态
   */
  getState() {
    return this.state
  }

  /**
   * 清空所有任务
   */
  clear(): void {
    this.tasks.clear()
    this.state.value = {
      isLoading: false,
      progress: 0,
      currentTask: '',
      completedTasks: [],
      failedTasks: []
    }
  }

  /**
   * 延迟工具函数
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * 预加载关键资源
   */
  async preloadCriticalResources(resources: Array<{
    type: 'script' | 'style' | 'image' | 'font'
    url: string
    priority?: number
  }>): Promise<void> {
    const preloadTasks = resources.map((resource, index) => ({
      id: `preload_${index}`,
      name: `预加载 ${resource.type}: ${resource.url}`,
      priority: resource.priority || 10,
      execute: () => this.preloadResource(resource)
    }))

    this.addTasks(preloadTasks)
  }

  /**
   * 预加载单个资源
   */
  private preloadResource(resource: {
    type: 'script' | 'style' | 'image' | 'font'
    url: string
  }): Promise<void> {
    return new Promise((resolve, reject) => {
      let element: HTMLElement

      switch (resource.type) {
        case 'script':
          element = document.createElement('script')
          ;(element as HTMLScriptElement).src = resource.url
          break
        case 'style':
          element = document.createElement('link')
          ;(element as HTMLLinkElement).rel = 'stylesheet'
          ;(element as HTMLLinkElement).href = resource.url
          break
        case 'image':
          element = document.createElement('img')
          ;(element as HTMLImageElement).src = resource.url
          break
        case 'font':
          element = document.createElement('link')
          ;(element as HTMLLinkElement).rel = 'preload'
          ;(element as HTMLLinkElement).as = 'font'
          ;(element as HTMLLinkElement).href = resource.url
          ;(element as HTMLLinkElement).crossOrigin = 'anonymous'
          break
        default:
          reject(new Error(`不支持的资源类型: ${resource.type}`))
          return
      }

      element.onload = () => resolve()
      element.onerror = () => reject(new Error(`加载失败: ${resource.url}`))

      document.head.appendChild(element)
    })
  }

  /**
   * 智能批量加载数据
   */
  async loadDataInBatches<T>(
    items: T[],
    batchSize: number,
    processor: (batch: T[]) => Promise<any>,
    onProgress?: (progress: number) => void
  ): Promise<any[]> {
    const results: any[] = []
    const batches: T[][] = []
    
    // 分批
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize))
    }

    // 逐批处理
    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i]
      try {
        const batchResult = await processor(batch)
        results.push(batchResult)
        
        if (onProgress) {
          const progress = ((i + 1) / batches.length) * 100
          onProgress(progress)
        }
        
        // 给浏览器喘息的机会
        if (i < batches.length - 1) {
          await nextTick()
        }
      } catch (error) {
        console.error(`批次 ${i + 1} 处理失败:`, error)
        throw error
      }
    }

    return results
  }

  /**
   * 创建页面加载优化策略
   */
  createPageLoadStrategy(pageName: string) {
    return {
      // 关键数据优先加载
      critical: (tasks: LoadingTask[]) => {
        tasks.forEach(task => {
          task.priority = 10
          this.addTask(task)
        })
      },

      // 次要数据延迟加载
      deferred: (tasks: LoadingTask[]) => {
        tasks.forEach(task => {
          task.priority = 5
          this.addTask(task)
        })
      },

      // 可选数据后台加载
      optional: (tasks: LoadingTask[]) => {
        tasks.forEach(task => {
          task.priority = 1
          this.addTask(task)
        })
      },

      // 执行加载策略
      execute: () => this.executeAll(),

      // 获取页面特定的加载状态
      getPageState: () => ({
        ...this.state.value,
        pageName
      })
    }
  }
}

// 创建全局实例
export const loadingOptimizer = new LoadingOptimizer()

// Vue组合式API钩子
export function useLoadingOptimizer() {
  return {
    loadingOptimizer,
    loadingState: loadingOptimizer.getState(),
    addTask: (task: LoadingTask) => loadingOptimizer.addTask(task),
    executeAll: (showLoading?: boolean) => loadingOptimizer.executeAll(showLoading),
    cancel: () => loadingOptimizer.cancel(),
    clear: () => loadingOptimizer.clear()
  }
}

// Vue插件安装函数
export function setupLoadingOptimizer(app: any) {
  app.config.globalProperties.$loadingOptimizer = loadingOptimizer
  app.provide('loadingOptimizer', loadingOptimizer)
  
  console.log('✅ 加载优化器配置完成')
}

export default loadingOptimizer
