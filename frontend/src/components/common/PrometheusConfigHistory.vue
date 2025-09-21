<template>
  <div class="config-history">
    <el-card>
      <template #header>
        <div class="history-header">
          <el-icon><Clock /></el-icon>
          <span>配置历史记录</span>
          <div class="header-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="refreshHistory"
              :loading="loading"
            >
              刷新
            </el-button>
            <el-button 
              type="danger" 
              size="small"
              @click="clearHistory"
              :disabled="!historyList.length"
            >
              清空历史
            </el-button>
          </div>
        </div>
      </template>

      <!-- 统计信息 -->
      <div class="stats-section">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-statistic title="总配置数" :value="historyList.length" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="当前配置" :value="currentConfigId || 'N/A'" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="最后更新" :value="lastUpdateTime" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="配置版本" :value="latestVersion" />
          </el-col>
        </el-row>
      </div>

      <!-- 搜索和过滤 -->
      <div class="filter-section">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="搜索配置名称或URL"
              :prefix-icon="Search"
              clearable
            />
          </el-col>
          <el-col :span="6">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
              <el-option label="全部" value="" />
              <el-option label="启用" value="enabled" />
              <el-option label="禁用" value="disabled" />
              <el-option label="当前使用" value="current" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="default"
            />
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="applyFilters">筛选</el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 配置列表 -->
      <div class="history-list">
        <el-table 
          :data="filteredHistory" 
          stripe 
          border
          v-loading="loading"
          @row-click="viewConfigDetail"
        >
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="config-detail">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="配置名称">{{ row.name }}</el-descriptions-item>
                  <el-descriptions-item label="服务器地址">{{ row.url }}</el-descriptions-item>
                  <el-descriptions-item label="超时时间">{{ row.timeout }}ms</el-descriptions-item>
                  <el-descriptions-item label="采集间隔">{{ row.scrape_interval }}</el-descriptions-item>
                  <el-descriptions-item label="评估间隔">{{ row.evaluation_interval }}</el-descriptions-item>
                  <el-descriptions-item label="最大重试">{{ row.max_retries }}</el-descriptions-item>
                  <el-descriptions-item label="创建时间">{{ formatTime(row.created_at) }}</el-descriptions-item>
                  <el-descriptions-item label="更新时间">{{ formatTime(row.updated_at) }}</el-descriptions-item>
                </el-descriptions>
                
                <div class="config-actions" style="margin-top: 16px;">
                  <el-button 
                    type="primary" 
                    size="small"
                    @click.stop="restoreConfig(row)"
                    :disabled="row.is_current"
                  >
                    {{ row.is_current ? '当前使用' : '恢复配置' }}
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small"
                    @click.stop="duplicateConfig(row)"
                  >
                    复制配置
                  </el-button>
                  <el-button 
                    type="info" 
                    size="small"
                    @click.stop="exportConfig(row)"
                  >
                    导出配置
                  </el-button>
                  <el-button 
                    type="warning" 
                    size="small"
                    @click.stop="testConfig(row)"
                  >
                    测试连接
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small"
                    @click.stop="deleteConfig(row)"
                    :disabled="row.is_current"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="name" label="配置名称" min-width="120" />
          <el-table-column prop="url" label="服务器地址" min-width="200" show-overflow-tooltip />
          <el-table-column prop="timeout" label="超时(ms)" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_current" type="success">当前</el-tag>
              <el-tag v-else-if="row.is_enabled" type="primary">启用</el-tag>
              <el-tag v-else type="info">禁用</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="连接状态" width="100">
            <template #default="{ row }">
              <el-tag 
                :type="getConnectionStatusType(row.connection_status)"
                size="small"
              >
                {{ getConnectionStatusText(row.connection_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button 
                  type="primary" 
                  size="small"
                  @click.stop="restoreConfig(row)"
                  :disabled="row.is_current"
                >
                  {{ row.is_current ? '使用中' : '恢复' }}
                </el-button>
                <el-dropdown @command="(command) => handleAction(command, row)">
                  <el-button type="primary" size="small">
                    更多<el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="duplicate">复制配置</el-dropdown-item>
                      <el-dropdown-item command="export">导出配置</el-dropdown-item>
                      <el-dropdown-item command="test">测试连接</el-dropdown-item>
                      <el-dropdown-item 
                        command="delete" 
                        :disabled="row.is_current"
                      >
                        删除配置
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          v-if="total > pageSize"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
        />
      </div>
    </el-card>

    <!-- 配置详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="配置详情"
      width="60%"
      destroy-on-close
    >
      <div v-if="selectedConfig" class="config-detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedConfig.id }}</el-descriptions-item>
          <el-descriptions-item label="配置名称">{{ selectedConfig.name }}</el-descriptions-item>
          <el-descriptions-item label="服务器地址">{{ selectedConfig.url }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedConfig.username || '无' }}</el-descriptions-item>
          <el-descriptions-item label="超时时间">{{ selectedConfig.timeout }}ms</el-descriptions-item>
          <el-descriptions-item label="采集间隔">{{ selectedConfig.scrape_interval }}</el-descriptions-item>
          <el-descriptions-item label="评估间隔">{{ selectedConfig.evaluation_interval }}</el-descriptions-item>
          <el-descriptions-item label="最大重试">{{ selectedConfig.max_retries }}</el-descriptions-item>
          <el-descriptions-item label="是否启用">
            <el-tag :type="selectedConfig.is_enabled ? 'success' : 'danger'">
              {{ selectedConfig.is_enabled ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否默认">
            <el-tag :type="selectedConfig.is_default ? 'primary' : 'info'">
              {{ selectedConfig.is_default ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(selectedConfig.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatTime(selectedConfig.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- JSON 配置 -->
        <div style="margin-top: 20px;">
          <h4>完整配置 (JSON)</h4>
          <el-input
            :model-value="JSON.stringify(selectedConfig, null, 2)"
            type="textarea"
            :rows="10"
            readonly
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="restoreConfig(selectedConfig)"
          :disabled="selectedConfig?.is_current"
        >
          恢复此配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Search, ArrowDown } from '@element-plus/icons-vue'
import { apiService } from '@/services/api'

// 响应式数据
const loading = ref(false)
const historyList = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const showDetailDialog = ref(false)
const selectedConfig = ref(null)

// 计算属性
const total = computed(() => filteredHistory.value.length)

const currentConfigId = computed(() => {
  const current = historyList.value.find(item => item.is_current)
  return current?.id || null
})

const lastUpdateTime = computed(() => {
  if (!historyList.value.length) return 'N/A'
  const latest = historyList.value.reduce((latest, item) => {
    return new Date(item.updated_at) > new Date(latest.updated_at) ? item : latest
  })
  return formatTime(latest.updated_at)
})

const latestVersion = computed(() => {
  return historyList.value.length ? `v${historyList.value.length}` : 'N/A'
})

const filteredHistory = computed(() => {
  let filtered = [...historyList.value]

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(query) ||
      item.url.toLowerCase().includes(query)
    )
  }

  // 状态过滤
  if (statusFilter.value) {
    filtered = filtered.filter(item => {
      switch (statusFilter.value) {
        case 'enabled':
          return item.is_enabled
        case 'disabled':
          return !item.is_enabled
        case 'current':
          return item.is_current
        default:
          return true
      }
    })
  }

  // 日期范围过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    filtered = filtered.filter(item => {
      const itemDate = new Date(item.created_at)
      return itemDate >= startDate && itemDate <= endDate
    })
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// 方法
const refreshHistory = async () => {
  loading.value = true
  try {
    const response = await apiService.getPrometheusConfigHistory()
    historyList.value = response.data || []
    ElMessage.success('历史记录刷新成功')
  } catch (error) {
    ElMessage.error('获取历史记录失败')
    console.error('获取历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史记录吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await apiService.clearPrometheusConfigHistory()
    await refreshHistory()
    ElMessage.success('历史记录已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空历史记录失败')
    }
  }
}

const applyFilters = () => {
  currentPage.value = 1
}

const viewConfigDetail = (row) => {
  selectedConfig.value = row
  showDetailDialog.value = true
}

const restoreConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复配置 "${config.name}" 吗？`,
      '确认恢复',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await apiService.restorePrometheusConfig(config.id)
    await refreshHistory()
    ElMessage.success('配置恢复成功')
    
    // 触发父组件刷新
    emit('configRestored', config)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('配置恢复失败')
    }
  }
}

const duplicateConfig = async (config) => {
  try {
    const newConfig = {
      ...config,
      name: `${config.name}_copy_${Date.now()}`,
      is_current: false,
      is_default: false
    }
    
    await apiService.createPrometheusConfig(newConfig)
    await refreshHistory()
    ElMessage.success('配置复制成功')
  } catch (error) {
    ElMessage.error('配置复制失败')
  }
}

const exportConfig = (config) => {
  const configData = {
    ...config,
    exported_at: new Date().toISOString(),
    exported_by: 'system'
  }
  
  const dataStr = JSON.stringify(configData, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `prometheus_config_${config.name}_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('配置导出成功')
}

const testConfig = async (config) => {
  try {
    loading.value = true
    const response = await apiService.testPrometheusConnection({
      url: config.url,
      username: config.username,
      password: config.password,
      timeout: config.timeout
    })
    
    if (response.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
  } finally {
    loading.value = false
  }
}

const deleteConfig = async (config) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.name}" 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await apiService.deletePrometheusConfig(config.id)
    await refreshHistory()
    ElMessage.success('配置删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('配置删除失败')
    }
  }
}

const handleAction = (command, row) => {
  switch (command) {
    case 'duplicate':
      duplicateConfig(row)
      break
    case 'export':
      exportConfig(row)
      break
    case 'test':
      testConfig(row)
      break
    case 'delete':
      deleteConfig(row)
      break
  }
}

const getConnectionStatusType = (status) => {
  switch (status) {
    case 'connected':
      return 'success'
    case 'disconnected':
      return 'danger'
    case 'testing':
      return 'warning'
    default:
      return 'info'
  }
}

const getConnectionStatusText = (status) => {
  switch (status) {
    case 'connected':
      return '已连接'
    case 'disconnected':
      return '已断开'
    case 'testing':
      return '测试中'
    default:
      return '未知'
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return 'N/A'
  return new Date(timeStr).toLocaleString()
}

// 事件
const emit = defineEmits(['configRestored'])

// 生命周期
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.config-history {
  margin-bottom: 20px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-header span {
  margin-left: 8px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.stats-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.history-list {
  margin-top: 16px;
}

.config-detail {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.config-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.config-detail-dialog h4 {
  color: #409eff;
  margin-bottom: 8px;
}
</style>
