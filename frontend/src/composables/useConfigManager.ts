import { ref, computed } from 'vue'
import { apiService } from '@/services/api'

// Prometheus配置接口
export interface PrometheusConfig {
  enabled: boolean
  name?: string  // 配置名称，字母+符号，不使用中文
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
  name?: string
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
    name: '',  // 默认为空，用户需要填写
    url: 'http://localhost:9090',
    timeout: 30000,
    scrapeInterval: '15s',
    evaluationInterval: '15s',
    targets: []
  })

  // Ollama配置
  const ollamaConfig = ref<OllamaConfig>({
    name: '',
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

  // 配置名称验证函数
  const validateConfigName = (name: string): { valid: boolean; message?: string } => {
    if (!name || name.trim() === '') {
      return { valid: false, message: '配置名称不能为空' }
    }
    
    // 只允许字母、数字、下划线、短横线
    const namePattern = /^[a-zA-Z0-9_-]+$/
    if (!namePattern.test(name)) {
      return { valid: false, message: '配置名称只能包含字母、数字、下划线(_)和短横线(-)' }
    }
    
    // 长度限制
    if (name.length < 2) {
      return { valid: false, message: '配置名称至少需要2个字符' }
    }
    
    if (name.length > 50) {
      return { valid: false, message: '配置名称不能超过50个字符' }
    }
    
    // 不能以数字开头
    if (/^[0-9]/.test(name)) {
      return { valid: false, message: '配置名称不能以数字开头' }
    }
    
    // 不能以特殊符号开头或结尾
    if (/^[-_]|[-_]$/.test(name)) {
      return { valid: false, message: '配置名称不能以下划线或短横线开头/结尾' }
    }
    
    return { valid: true }
  }

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
      console.log('🔍 准备保存的配置数据:', prometheusConfig.value)
      console.log('🔍 配置名称:', prometheusConfig.value.name)
      
      const saveResult = await apiService.updatePrometheusConfig(prometheusConfig.value)
      console.log('🔍 保存结果:', saveResult)
      
      // 如果保存成功并且返回了配置ID，设置为当前配置
      if (saveResult?.success && saveResult?.data?.id) {
        console.log('🔍 设置为当前配置:', saveResult.data.id)
        await apiService.setCurrentPrometheusConfig(saveResult.data.id)
      }
      
      return saveResult?.success || false
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

  // 加载Ollama配置
  const loadOllamaConfig = async () => {
    try {
      const response = await apiService.getOllamaConfig()
      if (response && (response.data || response)) {
        const config = response.data || response
        ollamaConfig.value = {
          name: config.name || '',
          enabled: config.enabled || false,
          apiUrl: config.apiUrl || 'http://localhost:11434',
          model: config.model || 'llama3.2',
          timeout: config.timeout || 60000,
          maxTokens: config.maxTokens || 2048,
          temperature: config.temperature || 0.7
        }
      }
    } catch (error) {
      console.error('加载Ollama配置失败:', error)
    }
  }

  // 保存Ollama配置
  const saveOllamaConfig = async () => {
    try {
      console.log('🔍 准备保存的Ollama配置数据:', ollamaConfig.value)
      console.log('🔍 配置名称:', ollamaConfig.value.name)
      
      const saveResult = await apiService.updateOllamaConfig(ollamaConfig.value)
      console.log('🔍 保存结果:', saveResult)
      
      // 如果保存成功并且返回了配置ID，设置为当前配置
      if (saveResult?.success && saveResult?.data?.id) {
        console.log('🔍 设置为当前配置:', saveResult.data.id)
        await apiService.setCurrentOllamaConfig(saveResult.data.id)
      }
      
      return saveResult?.success || false
    } catch (error) {
      console.error('保存Ollama配置失败:', error)
      return false
    }
  }

  // 测试Ollama连接
  const testOllamaConnection = async () => {
    try {
      const result = await apiService.testOllamaConnection(ollamaConfig.value)
      return result
    } catch (error) {
      console.error('测试Ollama连接失败:', error)
      return {
        success: false,
        message: '连接测试失败',
        details: error instanceof Error ? error.message : '未知错误'
      }
    }
  }

  return {
    // 配置状态
    prometheusConfig,
    ollamaConfig,
    databaseConfig,
    
    // 计算属性
    isPrometheusConfigured,
    isOllamaConfigured,
    isDatabaseConfigured,
    
    // Prometheus方法
    loadPrometheusConfig,
    savePrometheusConfig,
    testPrometheusConnection,
    addPrometheusTarget,
    removePrometheusTarget,
    validateConfigName,
    
    // Ollama方法
    loadOllamaConfig,
    saveOllamaConfig,
    testOllamaConnection
  }
}