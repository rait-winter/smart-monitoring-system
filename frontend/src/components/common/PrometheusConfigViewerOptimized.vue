<template>
  <div class="prometheus-config-viewer">
    <!-- 当前配置显示 -->
    <el-card class="current-config-card" v-loading="loading">
      <template #header>
        <div class="config-header">
          <el-icon><Setting /></el-icon>
          <span>当前Prometheus配置</span>
          <div class="header-actions">
            <el-button 
              size="small" 
              @click="refreshConfig"
              :loading="refreshing"
              :disabled="isRefreshDisabled"
            >
              刷新 {{ refreshCooldownText }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="currentConfig" class="config-display">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="配置名称">
            {{ currentConfig.name || '默认配置' }}
          </el-descriptions-item>
          <el-descriptions-item label="服务器地址">
            <el-link :href="currentConfig.url" target="_blank" type="primary">
              {{ currentConfig.url }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="超时时间">
            {{ currentConfig.timeout }}ms
          </el-descriptions-item>
          <el-descriptions-item label="采集间隔">
            {{ currentConfig.scrape_interval }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentConfig.is_enabled ? 'success' : 'danger'">
              {{ currentConfig.is_enabled ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="连接状态">
            <el-tag 
              :type="connectionStatus === 'connected' ? 'success' : 
                     connectionStatus === 'testing' ? 'warning' : 'danger'"
            >
              {{ getConnectionStatusText() }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 快速操作 -->
        <div class="quick-actions">
          <el-button 
            type="primary" 
            @click="testConnection"
            :loading="testingConnection"
          >
            测试连接
          </el-button>
          <el-button 
            type="success" 
            @click="showQueryDialog = true"
            :disabled="connectionStatus !== 'connected'"
          >
            快速查询
          </el-button>
          <el-button 
            type="info" 
            @click="openPrometheusWeb"
            :disabled="!currentConfig.url"
          >
            打开Prometheus Web界面
          </el-button>
        </div>
      </div>

      <el-empty v-else description="未找到配置信息" />
    </el-card>

    <!-- 配置历史记录（简化版） -->
    <el-card class="config-history-card">
      <template #header>
        <div class="history-header">
          <el-icon><Clock /></el-icon>
          <span>配置历史</span>
          <div class="header-info">
            <el-tag size="small">共 {{ historyList.length }} 个配置</el-tag>
            <el-button 
              size="small" 
              type="text" 
              @click="showAllHistory = true"
              v-if="historyList.length > 3"
            >
              查看全部
            </el-button>
          </div>
        </div>
      </template>

      <div class="history-list">
        <el-table 
          :data="historyList.slice(0, 3)" 
          stripe
          size="small"
          v-loading="historyLoading"
        >
          <el-table-column prop="name" label="名称" min-width="120" />
          <el-table-column prop="url" label="地址" min-width="200" show-overflow-tooltip />
          <el-table-column prop="timeout" label="超时(ms)" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="!row.is_current"
                type="primary" 
                size="small"
                @click="switchConfig(row)"
                :loading="switching"
              >
                切换
              </el-button>
              <el-tag v-else type="success" size="small">使用中</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!historyList.length" description="暂无历史记录" />
      </div>
    </el-card>

    <!-- PromQL查询对话框 -->
    <el-dialog 
      v-model="showQueryDialog" 
      title="PromQL查询" 
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="query-section">
        <!-- 预设查询 -->
        <div class="preset-queries">
          <el-tag 
            v-for="preset in presetQueries" 
            :key="preset.label"
            @click="selectPresetQuery(preset)"
            class="preset-tag"
            :type="queryForm.query === preset.query ? 'primary' : ''"
          >
            {{ preset.label }}
          </el-tag>
        </div>

        <!-- 查询表单 -->
        <el-form :model="queryForm" label-width="80px">
          <el-form-item label="查询语句">
            <el-input 
              v-model="queryForm.query" 
              placeholder="请输入PromQL查询语句"
              type="textarea"
              :rows="3"
              @keydown.ctrl.enter="executeQuery"
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="executeQuery"
              :loading="queryLoading"
              :disabled="!queryForm.query.trim()"
            >
              执行查询
            </el-button>
            <el-button @click="clearQueryResult">清空结果</el-button>
          </el-form-item>
        </el-form>

        <!-- 查询结果 -->
        <div v-if="queryResult || queryError" class="query-result">
          <el-alert 
            v-if="queryError" 
            :title="queryError" 
            type="error" 
            show-icon 
          />
          
          <div v-else-if="queryResult">
            <el-divider content-position="left">查询结果</el-divider>
            <el-table 
              :data="formattedQueryResult" 
              stripe 
              size="small"
              max-height="400"
            >
              <el-table-column 
                v-for="col in resultColumns" 
                :key="col.prop"
                :prop="col.prop" 
                :label="col.label" 
                :width="col.width"
                show-overflow-tooltip
              />
            </el-table>
            
            <div class="result-info">
              <el-tag size="small">
                共 {{ queryResult?.data?.data?.result?.length || 0 }} 条结果
              </el-tag>
              <el-tag size="small" type="info">
                查询时间: {{ queryDuration }}ms
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showQueryDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 全部历史对话框 -->
    <el-dialog 
      v-model="showAllHistory" 
      title="全部配置历史" 
      width="80%"
    >
      <el-table 
        :data="historyList" 
        stripe
        v-loading="historyLoading"
      >
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="url" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled ? 'success' : 'danger'" size="small">
              {{ row.is_enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timeout" label="超时(ms)" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              v-if="!row.is_current"
              type="primary" 
              size="small"
              @click="switchConfig(row)"
              :loading="switching"
            >
              切换
            </el-button>
            <el-tag v-else type="success" size="small">使用中</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="showAllHistory = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Clock } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'
import { debounce } from 'lodash-es'

// ======== 响应式数据 ========
const loading = ref(false)
const refreshing = ref(false)
const historyLoading = ref(false)
const testingConnection = ref(false)
const queryLoading = ref(false)
const switching = ref(false)

const connectionStatus = ref<'connected' | 'disconnected' | 'testing' | 'unknown'>('unknown')
const currentConfig = ref<any>(null)
const historyList = ref<any[]>([])

const showQueryDialog = ref(false)
const showAllHistory = ref(false)
const queryResult = ref<any>(null)
const queryError = ref('')
const queryDuration = ref(0)

const queryForm = ref({
  query: 'up'
})

// ======== 刷新冷却机制 ========
const lastRefreshTime = ref(0)
const refreshCooldown = 5000 // 5秒
const cooldownTimer = ref<NodeJS.Timeout | null>(null)
const cooldownRemaining = ref(0)

// ======== 预设查询 ========
const presetQueries = [
  { label: '服务状态', query: 'up' },
  { label: 'CPU使用率', query: 'rate(cpu_usage_total[5m])' },
  { label: '内存使用率', query: 'memory_usage_percent' },
  { label: '磁盘使用率', query: 'disk_usage_percent' },
  { label: '网络流量', query: 'rate(network_bytes_total[5m])' }
]

// ======== 计算属性 ========
const isRefreshDisabled = computed(() => {
  return refreshing.value || cooldownRemaining.value > 0
})

const refreshCooldownText = computed(() => {
  return cooldownRemaining.value > 0 ? `(${cooldownRemaining.value}s)` : ''
})

const resultColumns = computed(() => {
  if (!queryResult.value?.data?.data?.result?.length) return []
  
  const result = queryResult.value.data.data.result[0]
  const columns = [
    { prop: 'metric', label: '指标', width: 200 }
  ]
  
  if (result.metric) {
    Object.keys(result.metric).forEach(key => {
      if (key !== '__name__') {
        columns.push({ prop: `labels.${key}`, label: key, width: 120 })
      }
    })
  }
  
  columns.push({ prop: 'value', label: '值', width: 100 })
  columns.push({ prop: 'timestamp', label: '时间', width: 160 })
  
  return columns
})

const formattedQueryResult = computed(() => {
  if (!queryResult.value?.data?.data?.result) return []
  
  return queryResult.value.data.data.result.slice(0, 20).map((item: any, index: number) => {
    const row: any = {
      metric: item.metric?.__name__ || `metric_${index}`,
      labels: item.metric || {},
      value: '',
      timestamp: ''
    }
    
    if (item.value) {
      row.value = parseFloat(item.value[1]).toFixed(2)
      row.timestamp = new Date(item.value[0] * 1000).toLocaleString()
    }
    
    return row
  })
})

// ======== 方法 ========
const getConnectionStatusText = () => {
  const statusMap = {
    connected: '已连接',
    disconnected: '未连接',
    testing: '测试中',
    unknown: '未知'
  }
  return statusMap[connectionStatus.value] || '未知'
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return '-'
  try {
    return new Date(timeStr).toLocaleString()
  } catch {
    return timeStr
  }
}

// ======== 数据加载 ========
const loadCurrentConfig = async (useCache = true) => {
  try {
    const response = await apiService.getPrometheusConfig(useCache)
    if (response?.data?.config) {
      currentConfig.value = response.data.config
      console.log('当前配置加载成功:', response.data.config)
    } else if (response?.data) {
      // 兼容直接返回配置的情况
      currentConfig.value = response.data
      console.log('当前配置加载成功(兼容格式):', response.data)
    }
  } catch (error: any) {
    console.error('加载当前配置失败:', error)
    if (!useCache) {
      ElMessage.error('加载配置失败: ' + (error.message || '未知错误'))
    }
  }
}

const loadConfigHistory = async (useCache = true) => {
  try {
    historyLoading.value = true
    const response = await apiService.getPrometheusConfigHistory(useCache)
    if (response?.data?.configs) {
      historyList.value = response.data.configs
      console.log('配置历史加载成功:', response.data.configs.length, '条记录')
    } else {
      historyList.value = []
    }
  } catch (error: any) {
    console.error('加载配置历史失败:', error)
    if (!useCache) {
      ElMessage.error('加载历史失败: ' + (error.message || '未知错误'))
    }
    historyList.value = []
  } finally {
    historyLoading.value = false
  }
}

// ======== 刷新配置 ========
const refreshConfig = debounce(async () => {
  const now = Date.now()
  if (now - lastRefreshTime.value < refreshCooldown) {
    return
  }
  
  try {
    refreshing.value = true
    lastRefreshTime.value = now
    
    // 启动冷却计时器
    startCooldownTimer()
    
    // 强制不使用缓存
    await Promise.all([
      loadCurrentConfig(false),
      loadConfigHistory(false)
    ])
    
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}, 1000)

const startCooldownTimer = () => {
  cooldownRemaining.value = Math.ceil(refreshCooldown / 1000)
  
  cooldownTimer.value = setInterval(() => {
    cooldownRemaining.value--
    if (cooldownRemaining.value <= 0) {
      if (cooldownTimer.value) {
        clearInterval(cooldownTimer.value)
        cooldownTimer.value = null
      }
    }
  }, 1000)
}

// ======== 连接测试 ========
const testConnection = async () => {
  if (!currentConfig.value) {
    ElMessage.warning('请先配置Prometheus服务器')
    return
  }
  
  try {
    testingConnection.value = true
    connectionStatus.value = 'testing'
    
    const response = await apiService.testPrometheusConnection(currentConfig.value)
    
    if (response?.success) {
      connectionStatus.value = 'connected'
      ElMessage.success('连接测试成功')
    } else {
      connectionStatus.value = 'disconnected'
      ElMessage.error('连接测试失败: ' + (response?.message || '未知错误'))
    }
  } catch (error: any) {
    connectionStatus.value = 'disconnected'
    console.error('连接测试失败:', error)
    ElMessage.error('连接测试失败: ' + (error.message || '网络错误'))
  } finally {
    testingConnection.value = false
  }
}

// ======== PromQL查询 ========
const selectPresetQuery = (preset: any) => {
  queryForm.value.query = preset.query
}

const executeQuery = debounce(async () => {
  if (!queryForm.value.query.trim()) {
    ElMessage.warning('请输入PromQL查询语句')
    return
  }

  try {
    queryLoading.value = true
    queryError.value = ''
    const startTime = Date.now()
    
    const queryParams = {
      query: queryForm.value.query
    }
    
    console.log('执行PromQL查询:', queryParams)
    const response = await apiService.executePromQLQuery(queryParams)
    
    queryDuration.value = Date.now() - startTime
    
    if (response?.success) {
      queryResult.value = response
      console.log('查询成功:', response)
      ElMessage.success('查询成功')
    } else {
      queryError.value = response?.message || '查询失败'
      ElMessage.error(queryError.value)
    }
  } catch (error: any) {
    console.error('PromQL查询失败:', error)
    
    let errorMessage = '查询失败'
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 400:
          errorMessage = 'PromQL语法错误，请检查查询语句'
          break
        case 503:
          errorMessage = 'Prometheus服务不可用，请检查配置'
          break
        case 504:
          errorMessage = '查询超时，请简化查询条件'
          break
        default:
          errorMessage = error.response.data?.message || `服务器错误 (${status})`
      }
    } else if (error.code === 'NETWORK_ERROR') {
      errorMessage = '网络连接失败，请检查网络连接'
    } else {
      errorMessage = error.message || '未知错误'
    }
    
    queryError.value = errorMessage
    ElMessage.error(errorMessage)
  } finally {
    queryLoading.value = false
  }
}, 500)

const clearQueryResult = () => {
  queryResult.value = null
  queryError.value = ''
}

// ======== 配置操作 ========
const switchConfig = async (config: any) => {
  try {
    switching.value = true
    
    // 使用新的设置当前配置API
    await apiService.setCurrentPrometheusConfig(config.id)
    
    // 刷新当前配置
    await loadCurrentConfig(false)
    await loadConfigHistory(false)
    
    ElMessage.success(`已切换到配置: ${config.name}`)
    
    // 关闭对话框
    showAllHistory.value = false
  } catch (error: any) {
    console.error('切换配置失败:', error)
    ElMessage.error('切换失败: ' + (error.message || '未知错误'))
  } finally {
    switching.value = false
  }
}

const openPrometheusWeb = () => {
  if (currentConfig.value?.url) {
    window.open(currentConfig.value.url, '_blank')
  }
}

// ======== 生命周期 ========
onMounted(async () => {
  try {
    loading.value = true
    
    // 并行加载数据
    const [configResult, historyResult] = await Promise.allSettled([
      loadCurrentConfig(true),
      loadConfigHistory(true)
    ])
    
    // 检查加载结果
    if (configResult.status === 'rejected') {
      console.warn('加载当前配置失败:', configResult.reason)
    }
    if (historyResult.status === 'rejected') {
      console.warn('加载配置历史失败:', historyResult.reason)
    }
  } catch (error) {
    console.error('初始化失败:', error)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (cooldownTimer.value) {
    clearInterval(cooldownTimer.value)
  }
})

// ======== 暴露方法给父组件 ========
defineExpose({
  refreshConfig,
  loadCurrentConfig,
  loadConfigHistory
})
</script>

<style scoped>
.prometheus-config-viewer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-header,
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.config-header span,
.history-header span {
  margin-left: 8px;
  font-weight: 500;
}

.header-actions,
.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-display {
  margin-top: 16px;
}

.quick-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.history-list {
  min-height: 200px;
}

.query-section {
  max-height: 70vh;
  overflow-y: auto;
}

.preset-queries {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.preset-tag:hover {
  transform: scale(1.05);
}

.query-result {
  margin-top: 20px;
}

.result-info {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-header,
  .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .header-actions,
  .header-info {
    width: 100%;
    justify-content: flex-end;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-actions .el-button {
    width: 100%;
  }
}

/* 加载状态优化 */
.el-card.is-loading {
  position: relative;
}

.el-card.is-loading::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 1;
}
</style>
