<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon class="title-icon">
              <TrendCharts />
            </el-icon>
            智能监控预警系统
          </h2>
          <div class="header-actions">
            <el-tag type="success" size="large">v2.0.0</el-tag>
            <el-tag :type="systemStatus.type" size="large">{{ systemStatus.text }}</el-tag>
          </div>
        </div>
      </template>
      
      <!-- 关键指标统计 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic 
            title="监控指标" 
            :value="metrics.totalMetrics" 
            suffix="个"
            :value-style="{ color: '#409eff' }"
          >
            <template #prefix>
              <el-icon class="statistic-icon">
                <Monitor />
              </el-icon>
            </template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic 
            title="活跃规则" 
            :value="metrics.activeRules" 
            suffix="条"
            :value-style="{ color: '#67c23a' }"
          >
            <template #prefix>
              <el-icon class="statistic-icon">
                <Setting />
              </el-icon>
            </template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic 
            title="24H告警" 
            :value="metrics.alertsToday" 
            suffix="次"
            :value-style="{ color: '#e6a23c' }"
          >
            <template #prefix>
              <el-icon class="statistic-icon">
                <Warning />
              </el-icon>
            </template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic 
            title="异常检测" 
            :value="metrics.anomalies" 
            suffix="个"
            :value-style="{ color: '#f56c6c' }"
          >
            <template #prefix>
              <el-icon class="statistic-icon">
                <DataAnalysis />
              </el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 主要功能区域 -->
    <el-row :gutter="20" class="main-content-row">
      <!-- 系统状态 -->
      <el-col :span="12">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon><CircleCheck /></el-icon>
                系统状态
              </h3>
              <el-button 
                size="small" 
                @click="refreshSystemStatus"
                :loading="statusLoading"
              >
                刷新状态
              </el-button>
            </div>
          </template>
          
          <div class="status-list">
            <div 
              v-for="status in systemServices" 
              :key="status.name"
              class="status-item"
            >
              <div class="status-info">
                <el-icon 
                  :class="status.status === 'running' ? 'status-success' : 'status-error'"
                >
                  <CircleCheck v-if="status.status === 'running'" />
                  <CircleClose v-else />
                </el-icon>
                <span class="service-name">{{ status.name }}</span>
              </div>
              <el-tag 
                :type="status.status === 'running' ? 'success' : 'danger'"
                size="small"
              >
                {{ status.status === 'running' ? '运行中' : '已停止' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 快速操作 -->
      <el-col :span="12">
        <el-card class="actions-card">
          <template #header>
            <h3>
              <el-icon><Lightning /></el-icon>
              快速操作
            </h3>
          </template>
          
          <div class="quick-actions">
            <el-button 
              v-for="action in quickActions" 
              :key="action.path"
              :type="action.type"
              :icon="action.icon"
              size="large"
              @click="navigateTo(action.path)"
              class="action-button"
            >
              {{ action.title }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- AI分析区域 -->
    <el-card class="ai-analysis-card">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><DataAnalysis /></el-icon>
            AI智能分析
          </h3>
          <div class="header-actions">
            <el-button 
              type="primary" 
              @click="startAIAnalysis"
              :loading="isAnalyzing"
              :disabled="!isAIConfigured"
            >
              {{ isAnalyzing ? '分析中...' : '开始分析' }}
            </el-button>
            <el-button 
              size="small" 
              @click="viewAnalysisHistory"
            >
              历史记录
            </el-button>
          </div>
        </div>
      </template>
      
      <div v-if="!isAIConfigured" class="ai-not-configured">
        <el-empty description="AI分析服务未配置">
          <el-button type="primary" @click="navigateTo('/system?tab=ai')">
            去配置
          </el-button>
        </el-empty>
      </div>
      
      <div v-else-if="currentAnalysis" class="analysis-result">
        <div class="analysis-header">
          <div class="analysis-info">
            <h4>{{ currentAnalysis.summary }}</h4>
            <div class="analysis-meta">
              <el-tag :type="getSeverityType(currentAnalysis.severity)" size="small">
                {{ getSeverityText(currentAnalysis.severity) }}
              </el-tag>
              <span class="confidence">置信度: {{ (currentAnalysis.confidence * 100).toFixed(1) }}%</span>
              <span class="timestamp">{{ formatTime(currentAnalysis.timestamp) }}</span>
            </div>
          </div>
          <el-button 
            size="small" 
            type="primary" 
            @click="showAnalysisDetail = true"
          >
            查看详情
          </el-button>
        </div>
        
        <div class="insights-preview">
          <h5>关键洞察：</h5>
          <ul>
            <li v-for="insight in currentAnalysis.insights.slice(0, 3)" :key="insight">
              {{ insight }}
            </li>
          </ul>
          <span v-if="currentAnalysis.insights.length > 3" class="more-insights">
            还有 {{ currentAnalysis.insights.length - 3 }} 条洞察...
          </span>
        </div>
      </div>
      
      <div v-else class="no-analysis">
        <el-empty description="暂无分析结果">
          <el-button type="primary" @click="startAIAnalysis" :loading="isAnalyzing">
            开始首次分析
          </el-button>
        </el-empty>
      </div>
    </el-card>
    
    <!-- 实时数据展示 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 告警趋势图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>
              <el-icon><TrendCharts /></el-icon>
              告警趋势 (近7天)
            </h3>
          </template>
          
          <div class="chart-placeholder">
            <el-icon class="chart-icon"><TrendCharts /></el-icon>
            <p>图表功能开发中...</p>
            <p class="chart-description">将显示近7天的告警数量变化趋势</p>
          </div>
        </el-card>
      </el-col>
      
      <!-- 异常分布图 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>
              <el-icon><PieChart /></el-icon>
              异常类型分布
            </h3>
          </template>
          
          <div class="chart-placeholder">
            <el-icon class="chart-icon"><PieChart /></el-icon>
            <p>图表功能开发中...</p>
            <p class="chart-description">将显示不同类型异常的分布情况</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近告警列表 -->
    <el-card class="recent-alerts-card">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Bell /></el-icon>
            最近告警
          </h3>
          <el-button 
            size="small" 
            @click="navigateTo('/notifications')"
          >
            查看全部
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="recentAlerts" 
        style="width: 100%"
        :show-header="true"
      >
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getAlertTypeColor(row.type)" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="告警内容" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已处理' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="handleAlert(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- AI分析详情弹窗 -->
    <el-dialog
      v-model="showAnalysisDetail"
      title="AI分析详情"
      width="800px"
    >
      <div v-if="currentAnalysis" class="analysis-detail">
        <div class="analysis-summary">
          <h3>{{ currentAnalysis.summary }}</h3>
          <div class="meta-info">
            <el-tag :type="getSeverityType(currentAnalysis.severity)" size="large">
              {{ getSeverityText(currentAnalysis.severity) }}
            </el-tag>
            <span class="confidence">置信度: {{ (currentAnalysis.confidence * 100).toFixed(1) }}%</span>
            <span class="timestamp">{{ formatTime(currentAnalysis.timestamp) }}</span>
          </div>
        </div>
        
        <el-divider />
        
        <div class="insights-section">
          <h4>🔍 关键洞察</h4>
          <ul class="insights-list">
            <li v-for="insight in currentAnalysis.insights" :key="insight">
              {{ insight }}
            </li>
          </ul>
        </div>
        
        <el-divider />
        
        <div class="recommendations-section">
          <h4>💡 优化建议</h4>
          <ol class="recommendations-list">
            <li v-for="recommendation in currentAnalysis.recommendations" :key="recommendation">
              {{ recommendation }}
            </li>
          </ol>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAnalysisDetail = false">关闭</el-button>
          <el-button type="primary" @click="exportAnalysisReport">导出报告</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Setting,
  Warning,
  TrendCharts,
  DataAnalysis,
  CircleCheck,
  CircleClose,
  Lightning,
  Bell,
  PieChart
} from '@element-plus/icons-vue'
import { useAIAnalysis } from '@/composables/useAIAnalysis'
import { useConfigManager } from '@/composables/useConfigManager'
import type { AnalysisResult } from '@/composables/useAIAnalysis'

// 路由对象
const router = useRouter()

// AI分析hooks
const {
  isAnalyzing,
  analysisHistory,
  currentAnalysis,
  quickAnalyzeMetrics,
  fullSystemAnalysis,
  exportAnalysis
} = useAIAnalysis()

// 配置管理hooks
const {
  isOllamaConfigured,
  isPrometheusConfigured
} = useConfigManager()

// 响应式数据
const statusLoading = ref(false)
const refreshLoading = ref(false)
const showAnalysisDetail = ref(false)

// AI配置状态
const isAIConfigured = computed(() => {
  return isOllamaConfigured.value && isPrometheusConfigured.value
})

// 系统指标数据
const metrics = ref({
  totalMetrics: 150,
  activeRules: 25,
  alertsToday: 12,
  anomalies: 8
})

// 系统状态
const systemStatus = computed(() => {
  const runningServices = systemServices.value.filter(s => s.status === 'running').length
  const totalServices = systemServices.value.length
  
  if (runningServices === totalServices) {
    return { type: 'success', text: '系统正常' }
  } else if (runningServices > totalServices * 0.7) {
    return { type: 'warning', text: '部分异常' }
  } else {
    return { type: 'danger', text: '系统异常' }
  }
})

// 系统服务状态
const systemServices = ref([
  { name: 'API服务', status: 'running' },
  { name: 'AI检测服务', status: 'running' },
  { name: '规则引擎', status: 'running' },
  { name: '通知服务', status: 'running' },
  { name: '数据库服务', status: 'running' }
])

// 快速操作配置
const quickActions = ref([
  {
    title: 'AI异常检测',
    path: '/anomaly-detection',
    type: 'primary',
    icon: TrendCharts
  },
  {
    title: '规则管理',
    path: '/rules',
    type: 'success',
    icon: Setting
  },
  {
    title: '通知中心',
    path: '/notifications',
    type: 'warning',
    icon: Bell
  },
  {
    title: '指标查询',
    path: '/metrics',
    type: 'info',
    icon: DataAnalysis
  }
])

// 最近告警数据
const recentAlerts = ref([
  {
    id: 1,
    time: '2025-09-06 22:30:15',
    type: 'CPU告警',
    message: 'CPU使用率超过阈值 85%',
    status: '待处理'
  },
  {
    id: 2,
    time: '2025-09-06 22:15:32',
    type: '内存告警',
    message: '内存使用率超过阈值 90%',
    status: '已处理'
  },
  {
    id: 3,
    time: '2025-09-06 21:45:21',
    type: '网络告警',
    message: '网络延迟异常，平均延迟 150ms',
    status: '已处理'
  },
  {
    id: 4,
    time: '2025-09-06 21:30:10',
    type: '磁盘告警',
    message: '磁盘空间使用率超过 95%',
    status: '待处理'
  }
])

// 方法函数

/**
 * 导航到指定页面
 */
const navigateTo = (path: string) => {
  router.push(path)
}

/**
 * 刷新系统状态
 */
const refreshSystemStatus = async () => {
  statusLoading.value = true
  try {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新服务状态（这里可以接入真实的 API）
    systemServices.value = systemServices.value.map(service => ({
      ...service,
      status: Math.random() > 0.1 ? 'running' : 'stopped' // 90% 概率运行正常
    }))
    
    ElMessage.success('系统状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    statusLoading.value = false
  }
}

/**
 * 获取告警类型颜色
 */
const getAlertTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    'CPU告警': 'danger',
    '内存告警': 'warning',
    '网络告警': 'info',
    '磁盘告警': 'success'
  }
  return colorMap[type] || 'info'
}

/**
 * 处理告警
 */
const handleAlert = (alert: any) => {
  ElMessage.info(`正在处理告警: ${alert.message}`)
  // 这里可以添加具体的告警处理逻辑
}

/**
 * 刷新系统信息
 */
const refreshSystemInfo = async () => {
  refreshLoading.value = true
  try {
    await Promise.all([
      refreshSystemStatus(),
      loadMetrics()
    ])
    ElMessage.success('系统信息已更新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    refreshLoading.value = false
  }
}

/**
 * 系统备份
 */
const backupSystem = async () => {
  try {
    ElMessage.info('正在进行系统备份...')
    // 这里调用备份API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('系统备份完成')
  } catch (error) {
    ElMessage.error('备份失败，请稍后重试')
  }
}

/**
 * 加载指标数据
 */
const loadMetrics = async () => {
  try {
    // 模拟从API加载指标数据
    await new Promise(resolve => setTimeout(resolve, 500))
    metrics.value = {
      totalMetrics: Math.floor(Math.random() * 50) + 100,
      activeRules: Math.floor(Math.random() * 10) + 20,
      alertsToday: Math.floor(Math.random() * 20) + 5,
      anomalies: Math.floor(Math.random() * 15) + 3
    }
  } catch (error) {
    console.error('加载指标数据失败:', error)
  }
}

/**
 * 开始AI分析
 */
const startAIAnalysis = async () => {
  if (!isAIConfigured.value) {
    ElMessage.warning('请先配置Ollama和Prometheus服务')
    return
  }

  try {
    // 获取当前系统指标进行分析
    const metricsData = [
      { name: 'cpu_usage', value: 75, threshold: 80 },
      { name: 'memory_usage', value: 68, threshold: 85 },
      { name: 'disk_usage', value: 45, threshold: 90 },
      { name: 'network_latency', value: 120, threshold: 100 }
    ]

    await fullSystemAnalysis(['cpu', 'memory', 'disk', 'network'])
    ElMessage.success('AI分析完成！')
  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error('AI分析失败，请检查服务配置')
  }
}

/**
 * 查看分析历史
 */
const viewAnalysisHistory = () => {
  if (analysisHistory.value.length === 0) {
    ElMessage.info('暂无分析历史记录')
    return
  }
  
  // 导航到分析历史页面或显示历史弹窗
  ElMessage.info('分析历史功能开发中...')
}

/**
 * 获取严重程度类型
 */
const getSeverityType = (severity: string) => {
  const typeMap: Record<string, string> = {
    low: 'info',
    medium: 'warning', 
    high: 'warning',
    critical: 'danger'
  }
  return typeMap[severity] || 'info'
}

/**
 * 获取严重程度文本
 */
const getSeverityText = (severity: string) => {
  const textMap: Record<string, string> = {
    low: '低风险',
    medium: '中等风险',
    high: '高风险', 
    critical: '严重风险'
  }
  return textMap[severity] || '未知'
}

/**
 * 格式化时间
 */
const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

/**
 * 导出分析报告
 */
const exportAnalysisReport = async () => {
  if (!currentAnalysis.value) {
    ElMessage.warning('没有可导出的分析结果')
    return
  }

  try {
    await exportAnalysis(currentAnalysis.value, 'json')
    showAnalysisDetail.value = false
  } catch (error) {
    ElMessage.error('导出失败，请稍后重试')
  }
}

// 生命周期钩子
onMounted(() => {
  // 设置页面标题
  document.title = '监控仪表盘 - 智能监控预警系统'
  
  // 可以在这里初始化数据，调用 API 获取实时数据
  console.log('仪表盘页面已加载')
})
</script>

<style scoped lang="scss">
.dashboard {
  // 使用主布局的内边距
  
  .welcome-card {
    margin-bottom: 20px;
    
    .card-header {
      @include flex-between;
      
      h2 {
        @include flex-center;
        margin: 0;
        color: $primary-color;
        font-size: 24px;
        gap: 8px;
        
        .title-icon {
          font-size: 28px;
          color: $primary-color;
        }
      }
      
      .header-actions {
        @include flex-center;
        gap: 10px;
      }
    }
    
    .statistic-icon {
      font-size: 24px;
      margin-right: 8px;
    }
  }
  
  .main-content-row {
    margin-bottom: 20px;
    
    .status-card,
    .actions-card {
      height: 320px;
      
      .card-header {
        @include flex-between;
        
        h3 {
          @include flex-center;
          margin: 0;
          gap: 8px;
          color: var(--el-text-color-primary);
        }
      }
    }
    
    .status-list {
      .status-item {
        @include flex-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        &:last-child {
          border-bottom: none;
        }
        
        .status-info {
          @include flex-center;
          gap: 10px;
          
          .status-success {
            color: $success-color;
          }
          
          .status-error {
            color: $danger-color;
          }
          
          .service-name {
            font-weight: 500;
          }
        }
      }
    }
    
    .quick-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 15px;
      
      .action-button {
        height: 60px;
        font-size: 16px;
        font-weight: 500;
        
        .el-icon {
          margin-right: 8px;
          font-size: 18px;
        }
      }
    }
  }
  
  .charts-row {
    margin-bottom: 20px;
    
    .chart-card {
      height: 400px;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
        color: var(--el-text-color-primary);
      }
      
      .chart-placeholder {
        @include flex-center;
        flex-direction: column;
        height: 320px;
        background: var(--el-fill-color-light);
        border-radius: 8px;
        color: var(--el-text-color-secondary);
        
        .chart-icon {
          font-size: 64px;
          margin-bottom: 16px;
          opacity: 0.6;
        }
        
        p {
          margin: 4px 0;
          
          &.chart-description {
            font-size: 12px;
            color: var(--el-text-color-placeholder);
          }
        }
      }
    }
  }
  
  .recent-alerts-card {
    .card-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
        color: var(--el-text-color-primary);
      }
    }
    
    .el-table {
      .el-button--small {
        padding: 4px 8px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard {
    .main-content-row {
      .el-col {
        margin-bottom: 20px;
      }
    }
    
    .charts-row {
      .el-col {
        margin-bottom: 20px;
      }
    }
    
    .quick-actions {
      grid-template-columns: 1fr !important;
      
      .action-button {
        height: 50px !important;
      }
    }
  }
}

// 暗色模式适配
.dark {
  .chart-placeholder {
    background: var(--monitor-bg-secondary) !important;
    border: 1px solid var(--monitor-border-color) !important;
  }
}
</style>