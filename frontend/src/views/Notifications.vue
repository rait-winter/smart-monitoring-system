<template>
  <div class="notifications">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><Bell /></el-icon>
          通知管理
        </h1>
        <p class="page-description">
          管理系统通知渠道和消息配置，支持多种通知方式和模板定制
        </p>
      </div>
      
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Setting" 
          @click="showChannelSettings = true"
        >
          渠道设置
        </el-button>
        <el-button 
          type="success" 
          :icon="Plus" 
          @click="showCreateTemplate = true"
        >
          创建模板
        </el-button>
      </div>
    </div>

    <!-- 通知统计 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="今日发送"
            :value="notificationStats.todaySent"
            suffix="条"
            :value-style="{ color: '#409eff' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Message /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="成功率"
            :value="notificationStats.successRate"
            suffix="%"
            :value-style="{ color: '#67c23a' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="待发送"
            :value="notificationStats.pending"
            suffix="条"
            :value-style="{ color: '#e6a23c' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="失败数量"
            :value="notificationStats.failed"
            suffix="条"
            :value-style="{ color: '#f56c6c' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能选项卡 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 通知历史 -->
      <el-tab-pane label="通知历史" name="history">
        <el-card>
          <!-- 筛选条件 -->
          <el-form :model="historyFilter" :inline="true" class="filter-form">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="historyFilter.dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                style="width: 350px"
              />
            </el-form-item>
            
            <el-form-item label="通知类型">
              <el-select v-model="historyFilter.type" style="width: 120px">
                <el-option label="全部" value="" />
                <el-option label="邮件" value="email" />
                <el-option label="Slack" value="slack" />
                <el-option label="Webhook" value="webhook" />
                <el-option label="短信" value="sms" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="发送状态">
              <el-select v-model="historyFilter.status" style="width: 120px">
                <el-option label="全部" value="" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
                <el-option label="待发送" value="pending" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="filterHistory">
                筛选
              </el-button>
              <el-button @click="resetHistoryFilter">
                重置
              </el-button>
            </el-form-item>
          </el-form>
          
          <!-- 通知列表 -->
          <el-table 
            :data="filteredNotifications" 
            style="width: 100%"
            :loading="tableLoading"
            stripe
          >
            <el-table-column prop="timestamp" label="发送时间" width="180" sortable />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getNotificationTypeColor(row.type)" size="small">
                  {{ getNotificationTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recipient" label="接收者" width="200" />
            <el-table-column prop="subject" label="主题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusColor(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="retryCount" label="重试次数" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="viewNotificationDetail(row)">
                  详情
                </el-button>
                <el-button 
                  v-if="row.status === 'failed'"
                  size="small" 
                  type="warning" 
                  link
                  @click="retryNotification(row)"
                >
                  重试
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[20, 50, 100]"
              :total="totalNotifications"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 渠道配置 -->
      <el-tab-pane label="渠道配置" name="channels">
        <el-row :gutter="20">
          <el-col 
            v-for="channel in notificationChannels" 
            :key="channel.type"
            :span="12"
          >
            <el-card class="channel-card">
              <template #header>
                <div class="channel-header">
                  <div class="channel-info">
                    <el-icon class="channel-icon">{{ getChannelIcon(channel.type) }}</el-icon>
                    <h3>{{ channel.name }}</h3>
                  </div>
                  <el-switch
                    v-model="channel.enabled"
                    @change="toggleChannel(channel)"
                  />
                </div>
              </template>
              
              <div class="channel-content">
                <p class="channel-description">{{ channel.description }}</p>
                
                <div class="channel-stats">
                  <div class="stat-item">
                    <span class="label">今日发送:</span>
                    <span class="value">{{ channel.todaySent }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">成功率:</span>
                    <span class="value">{{ channel.successRate }}%</span>
                  </div>
                  <div class="stat-item">
                    <span class="label">最后使用:</span>
                    <span class="value">{{ channel.lastUsed || '从未' }}</span>
                  </div>
                </div>
                
                <div class="channel-actions">
                  <el-button size="small" @click="configureChannel(channel)">
                    配置
                  </el-button>
                  <el-button size="small" type="primary" @click="testChannel(channel)">
                    测试
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
      
      <!-- 模板管理 -->
      <el-tab-pane label="模板管理" name="templates">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>模板列表</h3>
              <el-button size="small" type="primary" @click="showCreateTemplate = true">
                新建模板
              </el-button>
            </div>
          </template>
          
          <el-table :data="notificationTemplates" style="width: 100%">
            <el-table-column prop="name" label="模板名称" width="200" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getNotificationTypeColor(row.type)" size="small">
                  {{ getNotificationTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="subject" label="主题模板" min-width="250" show-overflow-tooltip />
            <el-table-column prop="usage" label="使用次数" width="100" sortable />
            <el-table-column prop="lastUsed" label="最后使用" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="editTemplate(row)">
                  编辑
                </el-button>
                <el-button size="small" type="success" link @click="duplicateTemplate(row)">
                  复制
                </el-button>
                <el-button size="small" type="info" link @click="previewTemplate(row)">
                  预览
                </el-button>
                <el-button size="small" type="danger" link @click="deleteTemplate(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 渠道设置弹窗 -->
    <el-dialog
      v-model="showChannelSettings"
      title="渠道设置"
      width="600px"
    >
      <div class="channel-settings">
        <p>在这里可以配置各种通知渠道的参数...</p>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showChannelSettings = false">取消</el-button>
          <el-button type="primary" @click="saveChannelSettings">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建模板弹窗 -->
    <el-dialog
      v-model="showCreateTemplate"
      title="创建通知模板"
      width="800px"
    >
      <div class="template-form">
        <p>在这里可以创建和编辑通知模板...</p>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateTemplate = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell,
  Setting,
  Plus,
  Message,
  CircleCheck,
  Clock,
  CircleClose
} from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('history')
const tableLoading = ref(false)
const showChannelSettings = ref(false)
const showCreateTemplate = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)

// 通知统计数据
const notificationStats = ref({
  todaySent: 1247,
  successRate: 96.8,
  pending: 23,
  failed: 8
})

// 历史筛选
const historyFilter = ref({
  dateRange: [],
  type: '',
  status: ''
})

// 通知历史数据
const notifications = ref([
  {
    id: 1,
    timestamp: '2025-09-06 22:45:32',
    type: 'email',
    recipient: 'admin@company.com',
    subject: 'CPU使用率超过85%告警',
    status: 'success',
    retryCount: 0
  },
  {
    id: 2,
    timestamp: '2025-09-06 22:30:15',
    type: 'slack',
    recipient: '#monitoring',
    subject: '内存使用率异常告警',
    status: 'success',
    retryCount: 0
  },
  {
    id: 3,
    timestamp: '2025-09-06 22:15:45',
    type: 'webhook',
    recipient: 'https://api.company.com/webhook',
    subject: '网络延迟异常通知',
    status: 'failed',
    retryCount: 2
  },
  {
    id: 4,
    timestamp: '2025-09-06 21:58:22',
    type: 'sms',
    recipient: '+86 138****8888',
    subject: '磁盘空间不足紧急通知',
    status: 'success',
    retryCount: 0
  },
  {
    id: 5,
    timestamp: '2025-09-06 21:30:10',
    type: 'email',
    recipient: 'ops@company.com',
    subject: '服务器响应时间超时',
    status: 'pending',
    retryCount: 1
  }
])

// 通知渠道数据
const notificationChannels = ref([
  {
    type: 'email',
    name: '邮件通知',
    description: '通过SMTP发送邮件通知，支持HTML模板',
    enabled: true,
    todaySent: 856,
    successRate: 98.2,
    lastUsed: '2025-09-06 22:45:32'
  },
  {
    type: 'slack',
    name: 'Slack通知',
    description: '发送消息到Slack频道或私信',
    enabled: true,
    todaySent: 234,
    successRate: 99.1,
    lastUsed: '2025-09-06 22:30:15'
  },
  {
    type: 'webhook',
    name: 'Webhook通知',
    description: '发送HTTP POST请求到指定URL',
    enabled: true,
    todaySent: 125,
    successRate: 94.5,
    lastUsed: '2025-09-06 22:15:45'
  },
  {
    type: 'sms',
    name: '短信通知',
    description: '通过SMS网关发送短信通知',
    enabled: false,
    todaySent: 32,
    successRate: 97.8,
    lastUsed: '2025-09-06 21:58:22'
  }
])

// 通知模板数据
const notificationTemplates = ref([
  {
    id: 1,
    name: 'CPU告警模板',
    type: 'email',
    subject: 'CPU使用率超过{{threshold}}%告警',
    usage: 156,
    lastUsed: '2025-09-06 22:45:32'
  },
  {
    id: 2,
    name: '内存告警模板',
    type: 'slack',
    subject: '内存使用率赶到{{usage}}%，请注意检查',
    usage: 89,
    lastUsed: '2025-09-06 22:30:15'
  },
  {
    id: 3,
    name: '系统异常模板',
    type: 'webhook',
    subject: '系统检测到{{anomaly_type}}异常',
    usage: 67,
    lastUsed: '2025-09-06 21:15:20'
  }
])

// 计算属性
const totalNotifications = computed(() => notifications.value.length)

const filteredNotifications = computed(() => {
  let filtered = notifications.value
  
  if (historyFilter.value.type) {
    filtered = filtered.filter(n => n.type === historyFilter.value.type)
  }
  
  if (historyFilter.value.status) {
    filtered = filtered.filter(n => n.status === historyFilter.value.status)
  }
  
  return filtered
})

// 方法函数

/**
 * 筛选历史记录
 */
const filterHistory = () => {
  ElMessage.success('筛选完成')
}

/**
 * 重置历史筛选
 */
const resetHistoryFilter = () => {
  historyFilter.value = {
    dateRange: [],
    type: '',
    status: ''
  }
}

/**
 * 查看通知详情
 */
const viewNotificationDetail = (notification: any) => {
  ElMessage.info(`查看通知详情: ${notification.subject}`)
}

/**
 * 重试通知
 */
const retryNotification = async (notification: any) => {
  try {
    await ElMessageBox.confirm('确定要重试发送这条通知吗？', '确认操作')
    notification.status = 'pending'
    notification.retryCount += 1
    ElMessage.success('已加入重试队列')
  } catch {
    // 用户取消
  }
}

/**
 * 切换渠道状态
 */
const toggleChannel = (channel: any) => {
  const status = channel.enabled ? '启用' : '禁用'
  ElMessage.success(`${channel.name}已${status}`)
}

/**
 * 配置渠道
 */
const configureChannel = (channel: any) => {
  ElMessage.info(`配置${channel.name}功能开发中...`)
}

/**
 * 测试渠道
 */
const testChannel = async (channel: any) => {
  ElMessage.loading('正在测试通知渠道...')
  
  // 模拟测试过程
  setTimeout(() => {
    ElMessage.success(`${channel.name}测试成功`)
  }, 2000)
}

/**
 * 编辑模板
 */
const editTemplate = (template: any) => {
  ElMessage.info(`编辑模板: ${template.name}`)
}

/**
 * 复制模板
 */
const duplicateTemplate = (template: any) => {
  const newTemplate = {
    ...template,
    id: Date.now(),
    name: template.name + ' - 副本',
    usage: 0,
    lastUsed: null
  }
  notificationTemplates.value.push(newTemplate)
  ElMessage.success('模板复制成功')
}

/**
 * 预览模板
 */
const previewTemplate = (template: any) => {
  ElMessage.info(`预览模板: ${template.name}`)
}

/**
 * 删除模板
 */
const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm(
      `确定删除模板「${template.name}」吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const index = notificationTemplates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      notificationTemplates.value.splice(index, 1)
      ElMessage.success('模板删除成功')
    }
  } catch {
    // 用户取消
  }
}

/**
 * 保存渠道设置
 */
const saveChannelSettings = () => {
  showChannelSettings.value = false
  ElMessage.success('渠道设置已保存')
}

/**
 * 保存模板
 */
const saveTemplate = () => {
  showCreateTemplate.value = false
  ElMessage.success('模板已保存')
}

/**
 * 分页处理
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 工具函数

const getNotificationTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    email: 'primary',
    slack: 'success',
    webhook: 'warning',
    sms: 'info'
  }
  return colorMap[type] || 'info'
}

const getNotificationTypeText = (type: string): string => {
  const textMap: Record<string, string> = {
    email: '邮件',
    slack: 'Slack',
    webhook: 'Webhook',
    sms: '短信'
  }
  return textMap[type] || '未知'
}

const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    pending: 'warning'
  }
  return colorMap[status] || 'info'
}

const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    success: '成功',
    failed: '失败',
    pending: '待发送'
  }
  return textMap[status] || '未知'
}

const getChannelIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    email: '📧',
    slack: '💬',
    webhook: '🔗',
    sms: '📱'
  }
  return iconMap[type] || '🔔'
}

// 生命周期钩子
onMounted(() => {
  document.title = '通知管理 - 智能监控预警系统'
})
</script>

<style scoped lang="scss">
.notifications {
  padding: 20px;
  
  .page-header {
    @include flex-between;
    margin-bottom: 24px;
    
    .header-content {
      .page-title {
        @include flex-center;
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 600;
        color: $primary-color;
        gap: 12px;
        
        .el-icon {
          font-size: 32px;
        }
      }
      
      .page-description {
        margin: 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
        line-height: 1.5;
        max-width: 600px;
      }
    }
    
    .header-actions {
      @include flex-center;
      gap: 12px;
    }
  }
  
  .stats-section {
    margin-bottom: 24px;
    
    .stat-card {
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .stat-icon {
        font-size: 20px;
        margin-right: 8px;
      }
    }
  }
  
  .main-tabs {
    .filter-form {
      margin-bottom: 20px;
      
      .el-form-item {
        margin-bottom: 16px;
      }
    }
    
    .table-pagination {
      @include flex-center;
      margin-top: 20px;
    }
    
    .channel-card {
      height: 100%;
      margin-bottom: 20px;
      transition: all 0.2s;
      
      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .channel-header {
        @include flex-between;
        
        .channel-info {
          @include flex-center;
          gap: 12px;
          
          .channel-icon {
            font-size: 24px;
          }
          
          h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
          }
        }
      }
      
      .channel-content {
        .channel-description {
          margin: 16px 0;
          color: var(--el-text-color-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .channel-stats {
          margin-bottom: 20px;
          
          .stat-item {
            @include flex-between;
            margin-bottom: 8px;
            font-size: 12px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .label {
              color: var(--el-text-color-secondary);
            }
            
            .value {
              font-weight: 500;
              color: var(--el-text-color-primary);
            }
          }
        }
        
        .channel-actions {
          @include flex-center;
          gap: 8px;
          
          .el-button {
            flex: 1;
          }
        }
      }
    }
    
    .section-header {
      @include flex-between;
      margin-bottom: 16px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
    }
  }
  
  .channel-settings {
    padding: 20px 0;
    text-align: center;
    color: var(--el-text-color-secondary);
  }
  
  .template-form {
    padding: 20px 0;
    text-align: center;
    color: var(--el-text-color-secondary);
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .notifications {
    .channel-card .el-col {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .notifications {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .stats-section .el-col {
      margin-bottom: 16px;
    }
    
    .main-tabs {
      .filter-form {
        .el-form-item {
          width: 100%;
          margin-bottom: 12px;
        }
      }
    }
  }
}

// 暗色模式适配
.dark {
  .stat-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
  
  .channel-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
}
</style>