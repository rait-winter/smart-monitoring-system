import { ref, computed } from 'vue'
import { apiService } from '@/services/api'

// Prometheus配置接口
export interface PrometheusConfig {
  enabled: boolean
  url: string
  username?: string
  password?: string
  timeout: number
  scrapeInterval: string
  evaluationInterval: string
  targets: PrometheusTarget[]
}

export interface PrometheusTarget {
  id: string
  name: string
  address: string
  port: number
  path: string
  enabled: boolean
  labels: Record<string, string>
}

// Ollama配置接口
export interface OllamaConfig {
  enabled: boolean
  apiUrl: string
  model: string
  timeout: number
  maxTokens: number
  temperature: number
}

// 数据库配置接口
export interface DatabaseConfig {
  postgresql: {
    enabled: boolean
    host: string
    port: number
    database: string
    username: string
    password: string
    ssl: boolean
  }
  backup: {
    enabled: boolean
    schedule: string
    retention: number
    path: string
  }
}

// 配置管理器
export function useConfigManager() {
  // Prometheus配置
  const prometheusConfig = ref<PrometheusConfig>({
    enabled: false,
    url: 'http://localhost:9090',
    timeout: 30000,
    scrapeInterval: '15s',
    evaluationInterval: '15s',
    targets: []
  })

  // Ollama配置
  const ollamaConfig = ref<OllamaConfig>({
    enabled: false,
    apiUrl: 'http://localhost:11434',
    model: 'llama3.2',
    timeout: 60000,
    maxTokens: 2048,
    temperature: 0.7
  })

  // 数据库配置
  const databaseConfig = ref<DatabaseConfig>({
    postgresql: {
      enabled: true,
      host: 'localhost',
      port: 5432,
      database: 'monitoring',
      username: 'postgres',
      password: '',
      ssl: false
    },
    backup: {
      enabled: true,
      schedule: '0 2 * * *', // 每天凌晨2点
      retention: 30, // 保留30天
      path: '/data/backups'
    }
  })

  // 加载配置
  const loadPrometheusConfig = async () => {
    try {
      const response = await apiService.getPrometheusConfig()
      console.log('API响应:', response)
      
      // 检查响应格式并提取配置数据
      if (response && response.data && response.data.config) {
        prometheusConfig.value = { ...prometheusConfig.value, ...response.data.config }
        console.log('配置加载成功:', prometheusConfig.value)
      } else if (response && response.config) {
        // 兼容直接返回config的情况
        prometheusConfig.value = { ...prometheusConfig.value, ...response.config }
        console.log('配置加载成功(兼容格式):', prometheusConfig.value)
      } else {
        console.warn('API响应格式不正确:', response)
      }
    } catch (error) {
      console.error('加载Prometheus配置失败:', error)
    }
  }

  // 保存Prometheus配置
  const savePrometheusConfig = async () => {
    try {
      await apiService.updatePrometheusConfig(prometheusConfig.value)
      return true
    } catch (error) {
      console.error('保存Prometheus配置失败:', error)
      return false
    }
  }

  // 测试Prometheus连接
  const testPrometheusConnection = async () => {
    try {
      const result = await apiService.testPrometheusConnection(prometheusConfig.value)
      console.log('Prometheus连接测试结果:', result)
      return result?.success || false
    } catch (error) {
      console.error('测试Prometheus连接失败:', error)
      return false
    }
  }

  // 添加监控目标
  const addPrometheusTarget = (target: Omit<PrometheusTarget, 'id'>) => {
    const newTarget: PrometheusTarget = {
      ...target,
      id: Date.now().toString()
    }
    prometheusConfig.value.targets.push(newTarget)
  }

  // 删除监控目标
  const removePrometheusTarget = (id: string) => {
    const index = prometheusConfig.value.targets.findIndex(t => t.id === id)
    if (index > -1) {
      prometheusConfig.value.targets.splice(index, 1)
    }
  }

  // 计算属性
  const isPrometheusConfigured = computed(() => {
    return prometheusConfig.value.enabled && 
           prometheusConfig.value.url && 
           prometheusConfig.value.targets.length > 0
  })

  const isOllamaConfigured = computed(() => {
    return ollamaConfig.value.enabled && 
           ollamaConfig.value.apiUrl && 
           ollamaConfig.value.model
  })

  const isDatabaseConfigured = computed(() => {
    return databaseConfig.value.postgresql.enabled &&
           databaseConfig.value.postgresql.host &&
           databaseConfig.value.postgresql.database
  })

  return {
    // 配置状态
    prometheusConfig,
    ollamaConfig,
    databaseConfig,
    
    // 计算属性
    isPrometheusConfigured,
    isOllamaConfigured,
    isDatabaseConfigured,
    
    // 方法
    loadPrometheusConfig,
    savePrometheusConfig,
    testPrometheusConnection,
    addPrometheusTarget,
    removePrometheusTarget
  }
}