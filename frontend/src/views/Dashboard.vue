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

// 路由对象
const router = useRouter()

// 响应式数据
const statusLoading = ref(false)

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