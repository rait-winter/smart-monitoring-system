<template>
  <div class="postgresql-config-viewer">
    <!-- 当前配置部分 -->
    <el-card class="config-card">
      <template #header>
        <div class="config-header">
          <h3>
            <el-icon><DataBoard /></el-icon>
            当前PostgreSQL配置
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
            <el-tag type="primary">{{ currentConfig.name || '默认数据库配置' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="currentConfig.enabled ? 'success' : 'info'">
              {{ currentConfig.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="主机地址">
            <span>{{ currentConfig.host || 'localhost' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="端口">
            <span>{{ currentConfig.port || 5432 }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="数据库名">
            <span>{{ currentConfig.database || 'monitoring' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="用户名">
            <span>{{ currentConfig.username || 'postgres' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="SSL连接">
            <el-tag :type="currentConfig.ssl ? 'success' : 'info'">
              {{ currentConfig.ssl ? '启用' : '禁用' }}
            </el-tag>
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
          测试数据库连接
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
              <el-descriptions-item v-if="testResult.data.version" label="PostgreSQL版本">
                {{ testResult.data.version }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.uptime" label="运行时间">
                {{ testResult.data.uptime }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.totalConnections !== undefined" label="总连接数">
                {{ testResult.data.totalConnections }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.activeConnections !== undefined" label="活跃连接数">
                {{ testResult.data.activeConnections }}
              </el-descriptions-item>
              <el-descriptions-item v-if="testResult.data.dbSize" label="数据库大小">
                {{ testResult.data.dbSize }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>
    </el-card>

    <!-- SQL查询测试部分 -->
    <el-card class="query-card">
      <template #header>
        <div class="query-header">
          <h3>
            <el-icon><DocumentCopy /></el-icon>
            SQL查询测试
          </h3>
        </div>
      </template>

      <div class="query-content">
        <div class="query-input">
          <el-input
            v-model="queryText"
            type="textarea"
            :rows="4"
            placeholder="输入SQL查询语句...&#10;例如: SELECT version();"
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
                  <el-dropdown-item @click="setQuickQuery('SELECT version();')">
                    PostgreSQL版本
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('SELECT pg_size_pretty(pg_database_size(current_database()));')">
                    数据库大小
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('SELECT count(*) as active_connections FROM pg_stat_activity;')">
                    活跃连接数
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats LIMIT 10;')">
                    表统计信息
                  </el-dropdown-item>
                  <el-dropdown-item @click="setQuickQuery('SHOW ALL;')">
                    所有配置参数
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
              共 {{ queryResult.data.length }} 行结果
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
              <span class="host-info">{{ config.host }}:{{ config.port }}/{{ config.database }}</span>
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
  DataBoard, 
  Refresh, 
  Lightning, 
  Link, 
  DocumentCopy, 
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
    const response = await apiService.getDatabaseConfig(false) // 不使用缓存
    
    if (response?.success && response?.data) {
      // 正确访问数据结构
      const configData = response.data.config || response.data
      currentConfig.value = {
        name: configData.name || '默认数据库配置',
        enabled: configData.postgresql?.enabled ?? true,
        host: configData.postgresql?.host || 'localhost',
        port: configData.postgresql?.port || 5432,
        database: configData.postgresql?.database || 'monitoring',
        username: configData.postgresql?.username || 'postgres',
        ssl: configData.postgresql?.ssl ?? false,
        updatedAt: configData.updatedAt || new Date().toISOString()
      }
      console.log('✅ 加载数据库配置成功:', currentConfig.value)
    } else {
      console.warn('⚠️ 未找到数据库配置')
      currentConfig.value = null
    }
  } catch (error) {
    console.error('❌ 加载数据库配置失败:', error)
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
    // 从API获取包含密码的完整配置
    const configResponse = await apiService.getDatabaseConfig(false)
    
    if (!configResponse?.success || !configResponse?.data) {
      throw new Error('无法获取数据库配置')
    }
    
    const fullConfig = configResponse.data.config || configResponse.data
    console.log('测试数据库连接，使用完整配置:', fullConfig)
    
    const response = await apiService.testDatabaseConnection(fullConfig)
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

// 执行SQL查询
const executeQuery = async () => {
  if (!queryText.value.trim() || !currentConfig.value) return
  
  queryLoading.value = true
  queryResult.value = null
  
  try {
    // 从API获取包含密码的完整配置
    const configResponse = await apiService.getDatabaseConfig(false)
    
    if (!configResponse?.success || !configResponse?.data) {
      throw new Error('无法获取数据库配置')
    }
    
    const fullConfig = configResponse.data.config || configResponse.data
    
    const response = await apiService.executeDatabaseQuery({
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
    const response = await apiService.getDatabaseConfigHistory(false) // 不使用缓存
    
    if (response?.success && response?.data) {
      const configs = response.data.configs || response.data || []
      if (Array.isArray(configs)) {
        configHistory.value = configs.map((config: any) => ({
          id: config.id,
          name: config.name || '未命名配置',
          host: config.host || 'localhost',
          port: config.port || 5432,
          database: config.database || 'monitoring',
          isDefault: config.isDefault || false,
          updatedAt: config.updatedAt || config.updated_at
        }))
        console.log('✅ 加载数据库配置历史成功:', configHistory.value.length, '个配置')
      } else {
        configHistory.value = []
        console.log('⚠️ 配置数据格式不正确')
      }
    } else {
      configHistory.value = []
      console.log('⚠️ 未找到数据库配置历史')
    }
  } catch (error) {
    console.error('❌ 加载数据库配置历史失败:', error)
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
    const response = await apiService.setCurrentDatabaseConfig(configId)
    
    if (response?.success) {
      ElMessage.success('配置切换成功')
      // 刷新当前配置和历史
      await Promise.all([loadCurrentConfig(), loadConfigHistory()])
    } else {
      ElMessage.error(response?.message || '配置切换失败')
    }
  } catch (error) {
    console.error('切换数据库配置失败:', error)
    ElMessage.error('配置切换失败')
  } finally {
    switchLoading.value = false
  }
}

// 查看配置详情
const viewConfigDetails = async (config: any) => {
  const details = `
配置名称: ${config.name}
主机地址: ${config.host}:${config.port}
数据库: ${config.database}
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
    
    const response = await apiService.clearDatabaseConfigHistory()
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
.postgresql-config-viewer {
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

.test-result.success {
  /* 成功状态样式 */
}

.test-result.error {
  /* 错误状态样式 */
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
