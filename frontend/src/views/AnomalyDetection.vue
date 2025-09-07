<template>
  <div class="anomaly-detection">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          AI异常检测
        </h1>
        <p class="page-description">
          基于机器学习算法的智能异常检测系统，实时监控系统指标并自动识别异常模式
        </p>
      </div>
      
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          @click="refreshDetection"
          :loading="refreshLoading"
        >
          刷新检测
        </el-button>
        <el-button 
          type="success" 
          :icon="Setting" 
          @click="showSettings = true"
        >
          检测设置
        </el-button>
      </div>
    </div>

    <!-- 检测概览 -->
    <el-row :gutter="20" class="overview-section">
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic
            title="检测模型"
            :value="detectionStats.totalModels"
            suffix="个"
            :value-style="{ color: '#409eff', fontSize: '24px' }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic
            title="活跃异常"
            :value="detectionStats.activeAnomalies"
            suffix="个"
            :value-style="{ color: '#f56c6c', fontSize: '24px' }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic
            title="检测准确率"
            :value="detectionStats.accuracy"
            suffix="%"
            :value-style="{ color: '#67c23a', fontSize: '24px' }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic
            title="今日检测"
            :value="detectionStats.todayDetections"
            suffix="次"
            :value-style="{ color: '#e6a23c', fontSize: '24px' }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 检测模型状态 -->
    <el-card class="models-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Cpu /></el-icon>
            检测模型状态
          </h3>
          <el-button size="small" @click="addModel">
            添加模型
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col 
          v-for="model in detectionModels" 
          :key="model.id"
          :span="8"
        >
          <div class="model-card">
            <div class="model-header">
              <div class="model-info">
                <h4>{{ model.name }}</h4>
                <p class="model-type">{{ model.type }}</p>
              </div>
              <el-tag 
                :type="getModelStatusType(model.status)"
                size="small"
              >
                {{ getModelStatusText(model.status) }}
              </el-tag>
            </div>
            
            <div class="model-metrics">
              <div class="metric-item">
                <span class="metric-label">准确率:</span>
                <span class="metric-value">{{ model.accuracy }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">检测数:</span>
                <span class="metric-value">{{ model.detectionCount }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">最后训练:</span>
                <span class="metric-value">{{ model.lastTrained }}</span>
              </div>
            </div>
            
            <div class="model-actions">
              <el-button 
                size="small" 
                type="primary" 
                @click="trainModel(model)"
                :loading="model.training"
              >
                重新训练
              </el-button>
              <el-button 
                size="small" 
                @click="configureModel(model)"
              >
                配置
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 实时异常检测 -->
    <el-card class="realtime-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Monitor /></el-icon>
            实时异常检测
          </h3>
          <div class="header-controls">
            <el-switch
              v-model="realtimeEnabled"
              @change="toggleRealtime"
              active-text="实时检测"
              inactive-text="已暂停"
            />
          </div>
        </div>
      </template>
      
      <div class="realtime-content">
        <div class="detection-chart">
          <div class="chart-placeholder">
            <el-icon class="chart-icon"><TrendCharts /></el-icon>
            <p>实时异常检测图表</p>
            <p class="chart-description">显示最近24小时的异常检测结果和趋势</p>
          </div>
        </div>
        
        <div class="detection-log">
          <h4>检测日志</h4>
          <div class="log-container">
            <div 
              v-for="log in detectionLogs" 
              :key="log.id"
              class="log-item"
              :class="getLogLevelClass(log.level)"
            >
              <div class="log-time">{{ log.timestamp }}</div>
              <div class="log-content">
                <span class="log-level">{{ log.level }}</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 异常列表 -->
    <el-card class="anomalies-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Warning /></el-icon>
            异常列表
          </h3>
          <div class="header-controls">
            <el-select 
              v-model="anomalyFilter" 
              placeholder="筛选异常类型"
              style="width: 150px; margin-right: 10px"
            >
              <el-option label="全部" value="all" />
              <el-option label="高危" value="high" />
              <el-option label="中危" value="medium" />
              <el-option label="低危" value="low" />
            </el-select>
            <el-button size="small" @click="exportAnomalies">
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="filteredAnomalies" 
        style="width: 100%"
        :loading="tableLoading"
      >
        <el-table-column prop="timestamp" label="检测时间" width="180" />
        <el-table-column prop="metric" label="指标名称" width="150" />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              {{ getSeverityText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="anomalyScore" label="异常分数" width="120">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.anomalyScore) }">
              {{ row.anomalyScore.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="异常描述" min-width="200" />
        <el-table-column prop="status" label="处理状态" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="row.status === 'resolved' ? 'success' : 'warning'" 
              size="small"
            >
              {{ row.status === 'resolved' ? '已处理' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="viewAnomalyDetail(row)"
            >
              详情
            </el-button>
            <el-button 
              v-if="row.status !== 'resolved'"
              size="small" 
              type="success" 
              link
              @click="resolveAnomaly(row)"
            >
              标记已处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalAnomalies"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 设置弹窗 -->
    <el-dialog
      v-model="showSettings"
      title="检测设置"
      width="600px"
    >
      <el-form :model="settingsForm" label-width="120px">
        <el-form-item label="检测间隔">
          <el-select v-model="settingsForm.interval">
            <el-option label="30秒" value="30" />
            <el-option label="1分钟" value="60" />
            <el-option label="5分钟" value="300" />
            <el-option label="10分钟" value="600" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="敏感度">
          <el-slider 
            v-model="settingsForm.sensitivity"
            :min="1"
            :max="10"
            show-stops
            show-tooltip
          />
        </el-form-item>
        
        <el-form-item label="启用通知">
          <el-switch v-model="settingsForm.notifications" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettings = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  Refresh,
  Setting,
  DataAnalysis,
  Warning,
  CircleCheck,
  Clock,
  Cpu,
  Monitor
} from '@element-plus/icons-vue'

// 响应式数据
const refreshLoading = ref(false)
const showSettings = ref(false)
const realtimeEnabled = ref(true)
const tableLoading = ref(false)
const anomalyFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)

// 检测统计数据
const detectionStats = ref({
  totalModels: 4,
  activeAnomalies: 15,
  accuracy: 96.5,
  todayDetections: 1247
})

// 检测模型数据
const detectionModels = ref([
  {
    id: 1,
    name: 'CPU异常检测',
    type: 'Isolation Forest',
    status: 'active',
    accuracy: 97.2,
    detectionCount: 1523,
    lastTrained: '2025-09-05',
    training: false
  },
  {
    id: 2,
    name: '内存使用检测',
    type: 'LSTM AutoEncoder',
    status: 'active',
    accuracy: 95.8,
    detectionCount: 892,
    lastTrained: '2025-09-04',
    training: false
  },
  {
    id: 3,
    name: '网络流量检测',
    type: 'One-Class SVM',
    status: 'training',
    accuracy: 94.1,
    detectionCount: 674,
    lastTrained: '2025-09-03',
    training: true
  },
  {
    id: 4,
    name: '磁盘IO检测',
    type: 'Random Forest',
    status: 'inactive',
    accuracy: 92.5,
    detectionCount: 445,
    lastTrained: '2025-09-01',
    training: false
  }
])

// 检测日志
const detectionLogs = ref([
  {
    id: 1,
    timestamp: '2025-09-06 22:45:32',
    level: 'WARNING',
    message: 'CPU使用率异常检测: 值 95.2% 超出正常范围'
  },
  {
    id: 2,
    timestamp: '2025-09-06 22:43:15',
    level: 'INFO',
    message: '内存检测模型已更新，准确率: 95.8%'
  },
  {
    id: 3,
    timestamp: '2025-09-06 22:40:21',
    level: 'ERROR',
    message: '网络流量检测失败: 数据源连接中断'
  },
  {
    id: 4,
    timestamp: '2025-09-06 22:38:45',
    level: 'SUCCESS',
    message: '磁盘IO异常已自动修复，系统恢复正常'
  }
])

// 异常数据
const anomalies = ref([
  {
    id: 1,
    timestamp: '2025-09-06 22:45:32',
    metric: 'CPU使用率',
    severity: 'high',
    anomalyScore: 0.95,
    description: 'CPU使用率突然从65%跳升到95%，远超正常范围',
    status: 'pending'
  },
  {
    id: 2,
    timestamp: '2025-09-06 22:30:15',
    metric: '内存使用率',
    severity: 'medium',
    anomalyScore: 0.78,
    description: '内存使用率持续高于85%，可能存在内存泄漏',
    status: 'pending'
  },
  {
    id: 3,
    timestamp: '2025-09-06 22:15:45',
    metric: '网络延迟',
    severity: 'low',
    anomalyScore: 0.65,
    description: '网络延迟间歇性增高，平均延迟达到120ms',
    status: 'resolved'
  },
  {
    id: 4,
    timestamp: '2025-09-06 21:58:22',
    metric: '磁盘IO',
    severity: 'high',
    anomalyScore: 0.89,
    description: '磁盘读写速度异常缓慢，可能磁盘故障',
    status: 'resolved'
  }
])

// 设置表单
const settingsForm = ref({
  interval: '60',
  sensitivity: 7,
  notifications: true
})

// 计算属性
const totalAnomalies = computed(() => anomalies.value.length)

const filteredAnomalies = computed(() => {
  if (anomalyFilter.value === 'all') {
    return anomalies.value
  }
  return anomalies.value.filter(anomaly => anomaly.severity === anomalyFilter.value)
})

// 方法函数

/**
 * 刷新检测数据
 */
const refreshDetection = async () => {
  refreshLoading.value = true
  try {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 更新统计数据
    detectionStats.value.activeAnomalies = Math.floor(Math.random() * 20) + 10
    detectionStats.value.todayDetections += Math.floor(Math.random() * 50) + 10
    
    ElMessage.success('检测数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    refreshLoading.value = false
  }
}

/**
 * 添加检测模型
 */
const addModel = () => {
  ElMessage.info('添加模型功能开发中...')
}

/**
 * 训练模型
 */
const trainModel = async (model: any) => {
  model.training = true
  try {
    await new Promise(resolve => setTimeout(resolve, 3000))
    model.accuracy = Math.min(99, model.accuracy + Math.random() * 2)
    ElMessage.success(`${model.name} 训练完成`)
  } catch (error) {
    ElMessage.error('模型训练失败')
  } finally {
    model.training = false
  }
}

/**
 * 配置模型
 */
const configureModel = (model: any) => {
  ElMessage.info(`配置 ${model.name} 功能开发中...`)
}

/**
 * 切换实时检测
 */
const toggleRealtime = (enabled: boolean) => {
  if (enabled) {
    ElMessage.success('实时检测已启用')
  } else {
    ElMessage.info('实时检测已暂停')
  }
}

/**
 * 导出异常数据
 */
const exportAnomalies = () => {
  ElMessage.info('导出功能开发中...')
}

/**
 * 查看异常详情
 */
const viewAnomalyDetail = (anomaly: any) => {
  ElMessage.info(`查看异常详情: ${anomaly.description}`)
}

/**
 * 标记异常已处理
 */
const resolveAnomaly = async (anomaly: any) => {
  try {
    await ElMessageBox.confirm('确定标记该异常为已处理吗？', '确认操作')
    anomaly.status = 'resolved'
    ElMessage.success('异常已标记为已处理')
  } catch {
    // 用户取消
  }
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

/**
 * 保存设置
 */
const saveSettings = () => {
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 工具函数

const getModelStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    training: 'warning',
    inactive: 'info'
  }
  return statusMap[status] || 'info'
}

const getModelStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '正常运行',
    training: '训练中',
    inactive: '已停用'
  }
  return statusMap[status] || '未知'
}

const getLogLevelClass = (level: string) => {
  return `log-${level.toLowerCase()}`
}

const getSeverityType = (severity: string) => {
  const severityMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return severityMap[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const severityMap: Record<string, string> = {
    high: '高危',
    medium: '中危',
    low: '低危'
  }
  return severityMap[severity] || '未知'
}

const getScoreColor = (score: number) => {
  if (score >= 0.8) return '#f56c6c'
  if (score >= 0.6) return '#e6a23c'
  return '#67c23a'
}

// 生命周期钩子
onMounted(() => {
  document.title = 'AI异常检测 - 智能监控预警系统'
})

onUnmounted(() => {
  // 清理定时器等资源
})
</script>

<style scoped lang="scss">
.anomaly-detection {
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
  
  .overview-section {
    margin-bottom: 24px;
    
    .metric-card {
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .metric-icon {
        font-size: 20px;
        margin-right: 8px;
      }
    }
  }
  
  .models-section {
    margin-bottom: 24px;
    
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
      }
    }
    
    .model-card {
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 8px;
      padding: 16px;
      transition: border-color 0.2s, box-shadow 0.2s;
      
      &:hover {
        border-color: var(--el-border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .model-header {
        @include flex-between;
        margin-bottom: 12px;
        
        .model-info {
          h4 {
            margin: 0 0 4px 0;
            font-size: 16px;
            font-weight: 600;
          }
          
          .model-type {
            margin: 0;
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
      
      .model-metrics {
        margin-bottom: 16px;
        
        .metric-item {
          @include flex-between;
          margin-bottom: 8px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .metric-label {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
          
          .metric-value {
            font-size: 12px;
            font-weight: 500;
          }
        }
      }
      
      .model-actions {
        @include flex-center;
        gap: 8px;
        
        .el-button {
          flex: 1;
        }
      }
    }
  }
  
  .realtime-section {
    margin-bottom: 24px;
    
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
      }
      
      .header-controls {
        @include flex-center;
        gap: 16px;
      }
    }
    
    .realtime-content {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      
      .detection-chart {
        .chart-placeholder {
          @include flex-center;
          flex-direction: column;
          height: 300px;
          background: var(--el-fill-color-light);
          border-radius: 8px;
          color: var(--el-text-color-secondary);
          
          .chart-icon {
            font-size: 48px;
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
      
      .detection-log {
        h4 {
          margin: 0 0 16px 0;
          font-size: 14px;
          font-weight: 600;
        }
        
        .log-container {
          max-height: 300px;
          overflow-y: auto;
          border: 1px solid var(--el-border-color-lighter);
          border-radius: 6px;
          
          .log-item {
            padding: 8px 12px;
            border-bottom: 1px solid var(--el-border-color-extra-light);
            font-size: 12px;
            
            &:last-child {
              border-bottom: none;
            }
            
            .log-time {
              color: var(--el-text-color-placeholder);
              margin-bottom: 4px;
            }
            
            .log-content {
              .log-level {
                display: inline-block;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 500;
                margin-right: 8px;
              }
              
              .log-message {
                color: var(--el-text-color-primary);
              }
            }
            
            &.log-info .log-level {
              background: var(--el-color-info-light-8);
              color: var(--el-color-info);
            }
            
            &.log-warning .log-level {
              background: var(--el-color-warning-light-8);
              color: var(--el-color-warning);
            }
            
            &.log-error .log-level {
              background: var(--el-color-danger-light-8);
              color: var(--el-color-danger);
            }
            
            &.log-success .log-level {
              background: var(--el-color-success-light-8);
              color: var(--el-color-success);
            }
          }
        }
      }
    }
  }
  
  .anomalies-section {
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
      }
      
      .header-controls {
        @include flex-center;
      }
    }
    
    .table-pagination {
      @include flex-center;
      margin-top: 20px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .anomaly-detection {
    .realtime-content {
      grid-template-columns: 1fr !important;
      
      .detection-log {
        margin-top: 20px;
      }
    }
  }
}

@media (max-width: 768px) {
  .anomaly-detection {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .overview-section .el-col {
      margin-bottom: 16px;
    }
    
    .models-section .el-col {
      margin-bottom: 20px;
    }
  }
}

// 暗色模式适配
.dark {
  .model-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
  
  .chart-placeholder {
    background: var(--monitor-bg-secondary) !important;
  }
  
  .log-container {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
}
</style>