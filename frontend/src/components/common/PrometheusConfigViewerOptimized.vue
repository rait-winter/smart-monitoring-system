<template>
  <div class="prometheus-config-viewer">
    <!-- 当前配置部分 -->
    <el-card class="config-card">
      <template #header>
        <div class="config-header">
          <h3>
            <el-icon><Monitor /></el-icon>
            当前Prometheus配置
          </h3>
          <div class="header-actions">
            <el-button 
              size="small" 
              @click="refreshConfig" 
              :loading="configLoading"
              circle
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="configLoading" class="loading-state">
        <el-skeleton :rows="4" animated />
      </div>

      <div v-else-if="currentConfig" class="config-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="配置名称">
            <el-tag type="primary">{{ currentConfig.name || '默认Prometheus配置' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="currentConfig.enabled ? 'success' : 'info'">
              {{ currentConfig.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="服务器地址">
            <span>{{ currentConfig.url || 'http://localhost:9090' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            <span>{{ currentConfig.username || '无' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="超时时间">
            <span>{{ currentConfig.timeout || 30 }}秒</span>
          </el-descriptions-item>
          <el-descriptions-item label="抓取间隔">
            <span>{{ currentConfig.scrapeInterval || '15s' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="评估间隔">
            <span>{{ currentConfig.evaluationInterval || '15s' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            <span>{{ formatTime(currentConfig.updatedAt) }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-empty v-else description="暂无配置信息" />
    </el-card>

    <!-- 连接测试部分 -->
    <el-card class="test-card">
      <template #header>
        <div class="test-header">
          <h3>
            <el-icon><Lightning /></el-icon>
            连接测试
          </h3>
        </div>
      </template>

      <div class="test-content">
        <el-button 
          type="primary" 
          @click="testConnection" 
          :loading="testLoading"
          :disabled="!currentConfig?.enabled"
        >
          <el-icon><Link /></el-icon>
          测试Prometheus连接
        </el-button>

        <div v-if="testResult" class="test-result" :class="{ 'success': testResult.success, 'error': !testResult.success }">
          <el-alert 
            :title="testResult.success ? '连接成功' : '连接失败'"
            :type="testResult.success ? 'success' : 'error'"
            :description="testResult.message"
            show-icon
            :closable="false"
          />
          <div v-if="testResult.data" class="connection-details">
            <el-descriptions :column="1" size="small" border style="margin-top: 12px;">
              <el-descriptions-item v-if="testResult.data.version" label="Prometheus版本">
                {{ testResult.data.version }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.uptime" label="运行时间">
                {{ testResult.data.uptime }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.targets !== undefined" label="监控目标数">
                {{ testResult.data.targets }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.metrics !== undefined" label="指标数量">
                {{ testResult.data.metrics }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 指标查询测试部分 -->
    <el-card class="query-card">
      <template #header>
        <div class="query-header">
          <h3>
            <el-icon><Search /></el-icon>
            指标查询测试
          </h3>
        </div>
      </template>

      <div class="query-content">
        <div class="query-input">
          <el-input
            v-model="queryText"
            type="textarea"
            :rows="3"
            placeholder="输入PromQL查询语句...&#10;例如: up"
            :disabled="!currentConfig?.enabled"
          />
          <div class="query-actions">
            <el-button-group>
              <el-button 
                @click="executeQuery" 
                :loading="queryLoading" 
                type="primary"
                :disabled="!queryText.trim() || !currentConfig?.enabled"
              >
                <el-icon><CaretRight /></el-icon>
                执行查询
              </el-button>
              <el-button 
                @click="clearQuery"
                :disabled="!queryText.trim()"
              >
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </el-button-group>
            
            <!-- 快速查询按钮 -->
            <el-dropdown trigger="click" style="margin-left: 12px;">
              <el-button type="info">
                快速查询<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="setQuickQuery('up')">
                    服务状态查询
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('cpu_usage')">
                    CPU使用率
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('memory_usage')">
                    内存使用率
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('disk_usage')">
                    磁盘使用率
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('rate(http_requests_total[5m])')">
                    HTTP请求率
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div v-if="queryResult" class="query-result">
          <el-alert 
            v-if="queryResult.error"
            :title="'查询失败'"
            type="error"
            :description="queryResult.error"
            show-icon
            :closable="false"
          />
          <div v-else-if="queryResult.data && queryResult.data.length > 0" class="result-table">
            <el-table 
              :data="queryResult.data" 
              border 
              stripe 
              size="small"
              style="width: 100%"
              max-height="300"
            >
              <el-table-column 
                v-for="(value, key) in queryResult.data[0]" 
                :key="key"
                :prop="key" 
                :label="key"
                show-overflow-tooltip
              />
            </el-table>
            <div class="result-info">
              共 {{ queryResult.data.length }} 条结果
            </div>
          </div>
          <el-alert 
            v-else
            title="查询成功"
            type="success"
            description="查询执行成功，但没有返回数据"
            show-icon
            :closable="false"
          />
        </div>
      </div>
    </el-card>

    <!-- 配置历史部分 -->
    <el-card class="history-card">
      <template #header>
        <div class="history-header">
          <h3>
            <el-icon><Clock /></el-icon>
            配置历史
          </h3>
          <div class="header-actions">
            <el-button 
              size="small" 
              @click="loadConfigHistory" 
              :loading="historyLoading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="clearHistory"
              :disabled="!configHistory.length"
            >
              <el-icon><Delete /></el-icon>
              清空历史
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="historyLoading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="configHistory.length > 0" class="history-content">
        <div 
          v-for="config in configHistory" 
          :key="config.id" 
          class="history-item"
          :class="{ 'current': config.isDefault }"
        >
          <div class="history-info">
            <div class="config-name">
              <el-tag 
                :type="config.isDefault ? 'primary' : 'info'"
                size="small"
              >
                {{ config.name }}
              </el-tag>
              <span v-if="config.isDefault" class="current-badge">当前</span>
            </div>
            <div class="config-details">
              <span class="url-info">{{ config.url || 'http://localhost:9090' }}</span>
              <span class="time-info">{{ formatTime(config.updatedAt) }}</span>
            </div>
          </div>
          <div class="history-actions">
            <el-button 
              v-if="!config.isDefault"
              size="small" 
              type="primary" 
              @click="switchConfig(config.id)"
              :loading="switchLoading"
            >
              切换
            </el-button>
            <el-button 
              size="small" 
              @click="viewConfigDetails(config)"
            >
              查看
            </el-button>
          </div>
        </div>
      </div>

      <el-empty v-else description="暂无配置历史" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Monitor, 
  Refresh, 
  Lightning, 
  Link, 
  Search, 
  CaretRight, 
  Delete, 
  ArrowDown, 
  Clock 
} from '@element-plus/icons-vue'
import apiService from '@/services/api'

// 响应式数据
const configLoading = ref(false)
const testLoading = ref(false)
const queryLoading = ref(false)
const historyLoading = ref(false)
const switchLoading = ref(false)

const currentConfig = ref<any>(null)
const testResult = ref<any>(null)
const queryResult = ref<any>(null)
const configHistory = ref<any[]>([])
const queryText = ref('')

// 格式化时间
const formatTime = (time: string | Date) => {
  if (!time) return '未知'
  const date = typeof time === 'string' ? new Date(time) : time
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString('zh-CN')
}

// 加载当前配置
const loadCurrentConfig = async () => {
  configLoading.value = true
  try {
    const response = await apiService.getPrometheusConfig(false)
    
    if (response?.success && response?.data) {
      const configData = response.data.config || response.data
      currentConfig.value = {
        name: configData.name || '默认Prometheus配置',
        enabled: configData.enabled ?? true,
        url: configData.url || 'http://localhost:9090',
        username: configData.username || '',
        timeout: configData.timeout || 30,
        scrapeInterval: configData.scrapeInterval || '15s',
        evaluationInterval: configData.evaluationInterval || '15s',
        updatedAt: configData.updatedAt || new Date().toISOString()
      }
      console.log('✅ 加载Prometheus配置成功:', currentConfig.value)
    } else {
      console.warn('⚠️ 未找到Prometheus配置')
      currentConfig.value = null
    }
  } catch (error) {
    console.error('❌ 加载Prometheus配置失败:', error)
    ElMessage.error('加载配置失败')
    currentConfig.value = null
  } finally {
    configLoading.value = false
  }
}

// 测试连接
const testConnection = async () => {
  if (!currentConfig.value) return
  
  testLoading.value = true
  testResult.value = null
  
  try {
    // 从API获取包含凭据的完整配置
    const configResponse = await apiService.getPrometheusConfig(false)
    
    if (!configResponse?.success || !configResponse?.data) {
      throw new Error('无法获取Prometheus配置')
    }
    
    const fullConfig = configResponse.data.config || configResponse.data
    console.log('测试Prometheus连接，使用完整配置:', fullConfig)
    
    const response = await apiService.testPrometheusConnection(fullConfig)
    testResult.value = response
    
    if (response?.success) {
      ElMessage.success('连接成功！')
    } else {
      ElMessage.error('连接失败，请检查配置')
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: '连接测试失败: ' + (error instanceof Error ? error.message : '未知错误')
    }
    ElMessage.error('连接测试失败')
  } finally {
    testLoading.value = false
  }
}

// 执行查询
const executeQuery = async () => {
  if (!queryText.value.trim() || !currentConfig.value) return
  
  queryLoading.value = true
  queryResult.value = null
  
  try {
    // 从API获取完整配置
    const configResponse = await apiService.getPrometheusConfig(false)
    
    if (!configResponse?.success || !configResponse?.data) {
      throw new Error('无法获取Prometheus配置')
    }
    
    const fullConfig = configResponse.data.config || configResponse.data
    
    const response = await apiService.queryPrometheus({
      query: queryText.value.trim(),
      config: fullConfig
    })
    
    if (response?.success) {
      queryResult.value = response.data
      ElMessage.success('查询执行成功')
    } else {
      queryResult.value = {
        error: response?.message || '查询执行失败'
      }
      ElMessage.error('查询执行失败')
    }
  } catch (error) {
    queryResult.value = {
      error: '查询执行失败: ' + (error instanceof Error ? error.message : '未知错误')
    }
    ElMessage.error('查询执行失败')
  } finally {
    queryLoading.value = false
  }
}

// 清空查询
const clearQuery = () => {
  queryText.value = ''
  queryResult.value = null
}

// 设置快速查询
const setQuickQuery = (query: string) => {
  queryText.value = query
}

// 加载配置历史
const loadConfigHistory = async () => {
  historyLoading.value = true
  try {
    const response = await apiService.getPrometheusConfigHistory(false)
    
    if (response?.success && response?.data) {
      const configs = response.data.configs || response.data || []
      if (Array.isArray(configs)) {
        configHistory.value = configs.map((config: any) => ({
          id: config.id,
          name: config.name || '未命名配置',
          url: config.url || 'http://localhost:9090',
          isDefault: config.isDefault || false,
          updatedAt: config.updatedAt || config.updated_at
        }))
        console.log('✅ 加载Prometheus配置历史成功:', configHistory.value.length, '个配置')
      } else {
        configHistory.value = []
        console.log('⚠️ 配置数据格式不正确')
      }
    } else {
      configHistory.value = []
      console.log('⚠️ 未找到Prometheus配置历史')
    }
  } catch (error) {
    console.error('❌ 加载Prometheus配置历史失败:', error)
    ElMessage.error('加载配置历史失败')
    configHistory.value = []
  } finally {
    historyLoading.value = false
  }
}

// 切换配置
const switchConfig = async (configId: number) => {
  switchLoading.value = true
  try {
    const response = await apiService.setCurrentPrometheusConfig(configId)
    
    if (response?.success) {
      ElMessage.success('配置切换成功')
      // 刷新当前配置和历史
      await Promise.all([loadCurrentConfig(), loadConfigHistory()])
    } else {
      ElMessage.error(response?.message || '配置切换失败')
    }
  } catch (error) {
    console.error('切换Prometheus配置失败:', error)
    ElMessage.error('配置切换失败')
  } finally {
    switchLoading.value = false
  }
}

// 查看配置详情
const viewConfigDetails = async (config: any) => {
  const details = `
配置名称: ${config.name}
服务器地址: ${config.url}
更新时间: ${formatTime(config.updatedAt)}
  `.trim()
  
  await ElMessageBox.alert(details, '配置详情', {
    confirmButtonText: '确定',
    type: 'info',
  })
}

// 清空历史
const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有配置历史记录吗？当前配置不会被删除。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await apiService.clearPrometheusConfigHistory()
    if (response?.success) {
      ElMessage.success('配置历史已清空')
      await loadConfigHistory()
    } else {
      ElMessage.error('清空历史失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空历史失败')
    }
  }
}

// 刷新配置
const refreshConfig = async () => {
  await Promise.all([loadCurrentConfig(), loadConfigHistory()])
}

// 暴露方法供父组件调用
defineExpose({
  refreshConfig,
  loadCurrentConfig,
  loadConfigHistory
})

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([loadCurrentConfig(), loadConfigHistory()])
})
</script>

<style scoped>
.prometheus-config-viewer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-card,
.test-card,
.query-card,
.history-card {
  width: 100%;
}

.config-header,
.test-header,
.query-header,
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.loading-state {
  padding: 20px;
}

.config-content {
  margin-top: 8px;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-result {
  margin-top: 16px;
}

.connection-details {
  margin-top: 12px;
}

.query-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.query-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.query-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-result {
  margin-top: 16px;
}

.result-table {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.result-info {
  padding: 8px 12px;
  background-color: var(--el-fill-color-light);
  border-top: 1px solid var(--el-border-color);
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.history-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.history-item:hover {
  background-color: var(--el-fill-color-light);
}

.history-item.current {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.config-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-badge {
  font-size: 12px;
  color: var(--el-color-primary);
  font-weight: 500;
}

.config-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.history-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .query-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .history-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .history-actions {
    justify-content: center;
  }
}
</style>