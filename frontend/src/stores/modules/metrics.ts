import { defineStore } from 'pinia'
import type { Metric, MetricHistory, MetricQuery } from '@/types/global'
import { ApiService } from '@/services/api'

interface MetricsState {
  // 指标数据
  metrics: Metric[]
  
  // 历史数据缓存
  historyCache: Record<string, MetricHistory[]>
  
  // 查询配置
  queryConfig: {
    interval: string
    range: string
    step: string
  }
  
  // 实时数据
  realTimeData: Record<string, any>
  
  // 图表配置
  chartConfigs: Record<string, any>
  
  // 过滤器
  filters: {
    category: string[]
    status: string[]
    search: string
  }
  
  // 加载状态
  loading: boolean
  
  // 错误信息
  error: string | null
  
  // 自动刷新
  autoRefresh: {
    enabled: boolean
    interval: number
    timer: number | null
  }
}

export const useMetricsStore = defineStore('metrics', {
  state: (): MetricsState => ({
    metrics: [],
    historyCache: {},
    
    queryConfig: {
      interval: '5m',
      range: '1h',
      step: '15s'
    },
    
    realTimeData: {},
    chartConfigs: {},
    
    filters: {
      category: [],
      status: [],
      search: ''
    },
    
    loading: false,
    error: null,
    
    autoRefresh: {
      enabled: true,
      interval: 30000, // 30秒
      timer: null
    }
  }),

  getters: {
    // 过滤后的指标
    filteredMetrics: (state) => {
      let filtered = state.metrics
      
      // 分类过滤
      if (state.filters.category.length > 0) {
        filtered = filtered.filter(metric => 
          state.filters.category.includes(metric.category)
        )
      }
      
      // 状态过滤
      if (state.filters.status.length > 0) {
        filtered = filtered.filter(metric => 
          state.filters.status.includes(metric.status)
        )
      }
      
      // 搜索过滤
      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(metric => 
          metric.name.toLowerCase().includes(search) ||
          metric.description?.toLowerCase().includes(search)
        )
      }
      
      return filtered
    },
    
    // 按分类分组的指标
    metricsByCategory: (state) => {
      const groups: Record<string, Metric[]> = {}
      
      state.metrics.forEach(metric => {
        const category = metric.category || '未分类'
        if (!groups[category]) {
          groups[category] = []
        }
        groups[category].push(metric)
      })
      
      return groups
    },
    
    // 异常指标
    anomalyMetrics: (state) => {
      return state.metrics.filter(metric => metric.status === 'error' || metric.status === 'warning')
    },
    
    // 指标统计
    metricsStats: (state) => {
      const total = state.metrics.length
      const normal = state.metrics.filter(m => m.status === 'success').length
      const warning = state.metrics.filter(m => m.status === 'warning').length
      const error = state.metrics.filter(m => m.status === 'error').length
      
      return {
        total,
        normal,
        warning,
        error,
        normalRate: total > 0 ? (normal / total * 100).toFixed(1) : '0'
      }
    },
    
    // 获取指标历史数据
    getMetricHistory: (state) => (metricName: string) => {
      return state.historyCache[metricName] || []
    }
  },

  actions: {
    /**
     * 获取指标列表
     */
    async fetchMetrics(params?: MetricQuery) {
      this.loading = true
      this.error = null
      
      try {
        const apiService = ApiService.getInstance()
        const response = await apiService.getMetrics(params)
        
        this.metrics = response.data || []
        
        // 更新实时数据
        this.updateRealTimeData()
        
      } catch (error: any) {
        this.error = error.message || '获取指标数据失败'
        console.error('获取指标失败:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取指标历史数据
     */
    async fetchMetricHistory(metricName: string, params?: any) {
      try {
        const apiService = ApiService.getInstance()
        const response = await apiService.getMetricHistory(metricName, {
          ...this.queryConfig,
          ...params
        })
        
        // 缓存历史数据
        this.historyCache[metricName] = response.data || []
        
        return response.data
      } catch (error: any) {
        console.error('获取指标历史数据失败:', error)
        throw error
      }
    },

    /**
     * 更新实时数据
     */
    updateRealTimeData() {
      const realTimeData: Record<string, any> = {}
      
      this.metrics.forEach(metric => {
        realTimeData[metric.name] = {
          value: metric.value,
          timestamp: metric.timestamp,
          status: metric.status,
          change: metric.change || 0
        }
      })
      
      this.realTimeData = realTimeData
    },

    /**
     * 设置查询配置
     */
    setQueryConfig(config: Partial<MetricsState['queryConfig']>) {
      this.queryConfig = { ...this.queryConfig, ...config }
    },

    /**
     * 设置过滤器
     */
    setFilters(filters: Partial<MetricsState['filters']>) {
      this.filters = { ...this.filters, ...filters }
    },

    /**
     * 清除过滤器
     */
    clearFilters() {
      this.filters = {
        category: [],
        status: [],
        search: ''
      }
    },

    /**
     * 保存图表配置
     */
    saveChartConfig(metricName: string, config: any) {
      this.chartConfigs[metricName] = config
    },

    /**
     * 获取图表配置
     */
    getChartConfig(metricName: string) {
      return this.chartConfigs[metricName] || {}
    },

    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
      if (this.autoRefresh.timer) {
        this.stopAutoRefresh()
      }
      
      this.autoRefresh.enabled = true
      this.autoRefresh.timer = window.setInterval(() => {
        this.fetchMetrics()
      }, this.autoRefresh.interval)
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
      if (this.autoRefresh.timer) {
        clearInterval(this.autoRefresh.timer)
        this.autoRefresh.timer = null
      }
      this.autoRefresh.enabled = false
    },

    /**
     * 设置自动刷新间隔
     */
    setAutoRefreshInterval(interval: number) {
      this.autoRefresh.interval = interval
      
      if (this.autoRefresh.enabled) {
        this.startAutoRefresh()
      }
    },

    /**
     * 清除缓存
     */
    clearCache() {
      this.historyCache = {}
      this.realTimeData = {}
    },

    /**
     * 重置状态
     */
    reset() {
      this.metrics = []
      this.historyCache = {}
      this.realTimeData = {}
      this.error = null
      this.clearFilters()
      this.stopAutoRefresh()
    }
  },

  // 持久化配置
  persist: {
    key: 'metrics-store',
    storage: localStorage,
    paths: ['queryConfig', 'chartConfigs', 'autoRefresh.interval']
  }
})