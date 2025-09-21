<template>
  <div class="prometheus-config-viewer">
    <!-- 当前配置显示 -->
    <el-card class="current-config-card">
      <template #header>
        <div class="config-header">
          <el-icon><Setting /></el-icon>
          <span>当前Prometheus配置</span>
          <div class="header-actions">
            <el-button 
              size="small" 
              @click="refreshConfig"
              :loading="loading"
            >
              刷新
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
          </div>
        </div>
      </template>

      <div class="history-list">
        <el-table 
          :data="historyList.slice(0, 5)" 
          stripe
          size="small"
          v-loading="loading"
        >
          <el-table-column prop="name" label="名称" min-width="120" />
          <el-table-column prop="url" label="地址" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag 
                v-if="row.is_current" 
                type="success" 
                size="small"
              >
                当前
              </el-tag>
              <el-tag 
                v-else 
                type="info" 
                size="small"
              >
                历史
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button 
                v-if="!row.is_current"
                type="primary" 
                size="small"
                @click="switchConfig(row)"
              >
                切换
              </el-button>
              <el-tag v-else type="success" size="small">使用中</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="historyList.length > 5" class="more-configs">
          <el-button type="text" @click="showAllHistory = true">
            查看全部 {{ historyList.length }} 个配置...
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 快速查询对话框 -->
    <el-dialog
      v-model="showQueryDialog"
      title="快速查询验证"
      width="60%"
      destroy-on-close
    >
      <div class="query-section">
        <el-form :model="queryForm" label-width="100px">
          <el-form-item label="查询类型">
            <el-select v-model="queryForm.type" style="width: 200px">
              <el-option label="服务状态" value="up" />
              <el-option label="指标数量" value="metrics" />
              <el-option label="目标状态" value="targets" />
              <el-option label="自定义查询" value="custom" />
            </el-select>
          </el-form-item>
          
          <el-form-item 
            v-if="queryForm.type === 'custom'" 
            label="PromQL语句"
          >
            <el-input
              v-model="queryForm.query"
              placeholder="输入PromQL查询语句，如：up"
            />
          </el-form-item>
        </el-form>

        <el-button 
          type="primary" 
          @click="executeQuery"
          :loading="queryLoading"
        >
          执行查询
        </el-button>

        <!-- 查询结果 -->
        <div v-if="queryResult" class="query-result">
          <h4>查询结果</h4>
          <el-table 
            :data="formattedQueryResult" 
            border 
            size="small"
            max-height="300"
          >
            <el-table-column 
              v-for="column in resultColumns" 
              :key="column.prop"
              :prop="column.prop" 
              :label="column.label"
              :width="column.width"
              show-overflow-tooltip
            />
          </el-table>
        </div>

        <!-- 查询错误 -->
        <el-alert
          v-if="queryError"
          title="查询失败"
          type="error"
          :description="queryError"
          show-icon
          closable
          @close="queryError = ''"
        />
      </div>

      <template #footer>
        <el-button @click="showQueryDialog = false">关闭</el-button>
        <el-button type="primary" @click="clearQuery">清空结果</el-button>
      </template>
    </el-dialog>

    <!-- 全部历史记录对话框 -->
    <el-dialog
      v-model="showAllHistory"
      title="全部配置历史"
      width="80%"
      destroy-on-close
    >
      <el-table :data="historyList" stripe border>
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="url" label="地址" min-width="250" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag 
              v-if="row.is_current" 
              type="success" 
              size="small"
            >
              当前
            </el-tag>
            <el-tag 
              v-else 
              type="info" 
              size="small"
            >
              历史
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Clock } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

// 响应式数据
const loading = ref(false)
const testingConnection = ref(false)
const queryLoading = ref(false)
const connectionStatus = ref('unknown')
const currentConfig = ref(null)
const historyList = ref([])
const showQueryDialog = ref(false)
const showAllHistory = ref(false)
const queryResult = ref(null)
const queryError = ref('')

const queryForm = reactive({
  type: 'up',
  query: ''
})

// 计算属性
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
  
  return queryResult.value.data.data.result.slice(0, 10).map((item, index) => {
    const row = {
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

// 方法
const refreshConfig = async () => {
  loading.value = true
  try {
    // 获取当前配置
    const configResponse = await apiService.getPrometheusConfig()
    if (configResponse?.data?.config) {
      currentConfig.value = configResponse.data.config
    }
    
    // 获取历史配置
    const historyResponse = await apiService.getPrometheusConfigHistory()
    if (historyResponse?.data?.configs) {
      historyList.value = historyResponse.data.configs
    }
    
    ElMessage.success('配置信息刷新成功')
  } catch (error) {
    console.error('刷新配置失败:', error)
    ElMessage.error('刷新配置失败')
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  if (!currentConfig.value) return
  
  testingConnection.value = true
  connectionStatus.value = 'testing'
  
  try {
    const response = await apiService.testPrometheusConnection(currentConfig.value)
    
    if (response.success) {
      connectionStatus.value = 'connected'
      ElMessage.success('Prometheus连接测试成功')
    } else {
      connectionStatus.value = 'disconnected'
      ElMessage.error('Prometheus连接测试失败')
    }
  } catch (error) {
    connectionStatus.value = 'disconnected'
    ElMessage.error('连接测试失败')
  } finally {
    testingConnection.value = false
  }
}

const executeQuery = async () => {
  queryLoading.value = true
  queryError.value = ''
  queryResult.value = null
  
  try {
    let query = ''
    
    switch (queryForm.type) {
      case 'up':
        query = 'up'
        break
      case 'metrics':
        query = 'prometheus_tsdb_symbol_table_size_bytes'
        break
      case 'targets':
        query = 'up{job!=""}'
        break
      case 'custom':
        query = queryForm.query
        break
    }
    
    if (!query) {
      ElMessage.warning('请输入查询语句')
      return
    }
    
    console.log('🔍 执行查询:', query)
    
    const response = await apiService.executePromQLQuery({
      query: query,
      queryType: 'query'
    })
    
    console.log('📊 查询响应:', response)
    
    if (response && response.success) {
      queryResult.value = response
      ElMessage.success('查询执行成功')
    } else {
      throw new Error(response?.message || '查询返回失败')
    }
    
  } catch (error) {
    console.error('❌ 查询失败:', error)
    
    let errorMessage = '查询执行失败'
    
    if (error.response) {
      // HTTP错误
      const status = error.response.status
      if (status === 503) {
        errorMessage = '无法连接到Prometheus服务器，请检查配置'
      } else if (status === 504) {
        errorMessage = '查询超时，请简化查询条件'
      } else if (status >= 400 && status < 500) {
        errorMessage = '查询语句有误，请检查PromQL语法'
      } else {
        errorMessage = `服务器错误 (${status})`
      }
    } else if (error.code === 'NETWORK_ERROR') {
      errorMessage = '网络连接失败，请检查网络连接'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    queryError.value = errorMessage
    ElMessage.error(errorMessage)
  } finally {
    queryLoading.value = false
  }
}

const switchConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要切换到配置 "${config.name}" 吗？`,
      '确认切换',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await apiService.restorePrometheusConfig(config.id)
    await refreshConfig()
    ElMessage.success(`已切换到配置: ${config.name}`)
    
    // 触发父组件更新
    emit('configChanged', config)
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('配置切换失败')
    }
  }
}

const clearQuery = () => {
  queryResult.value = null
  queryError.value = ''
  queryForm.query = ''
}

const openPrometheusWeb = () => {
  if (currentConfig.value?.url) {
    window.open(currentConfig.value.url, '_blank')
  }
}

const getConnectionStatusText = () => {
  switch (connectionStatus.value) {
    case 'connected':
      return '已连接'
    case 'disconnected':
      return '连接失败'
    case 'testing':
      return '测试中...'
    default:
      return '未测试'
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return 'N/A'
  return new Date(timeStr).toLocaleString()
}

// 事件
const emit = defineEmits(['configChanged'])

// 生命周期
onMounted(() => {
  refreshConfig()
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
}

.config-header span,
.history-header span {
  margin-left: 8px;
  font-weight: 600;
}

.config-display {
  margin-top: 16px;
}

.quick-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.history-list {
  margin-top: 16px;
}

.more-configs {
  margin-top: 12px;
  text-align: center;
}

.query-section {
  margin-bottom: 20px;
}

.query-result {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.query-result h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #409eff;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-actions {
    flex-direction: column;
  }
  
  .quick-actions .el-button {
    width: 100%;
  }
}
</style>
