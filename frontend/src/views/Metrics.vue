<template>
  <div class="metrics">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          监控指标
        </h1>
        <p class="page-description">
          实时监控系统关键指标，支持多维度查询和自定义时间范围分析
        </p>
      </div>
      
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          @click="refreshMetrics"
          :loading="refreshLoading"
        >
          刷新数据
        </el-button>
        <el-button 
          type="success" 
          :icon="Download" 
          @click="exportMetrics"
        >
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 查询条件 -->
    <el-card class="query-section">
      <el-form :model="queryForm" :inline="true" class="query-form">
        <el-form-item label="时间范围">
          <el-select v-model="queryForm.timeRange" style="width: 180px">
            <el-option label="最近1小时" value="1h" />
            <el-option label="最近6小时" value="6h" />
            <el-option label="最近24小时" value="24h" />
            <el-option label="最近7天" value="7d" />
            <el-option label="最近30天" value="30d" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="queryForm.timeRange === 'custom'" label="开始时间">
          <el-date-picker
            v-model="queryForm.startTime"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item v-if="queryForm.timeRange === 'custom'" label="结束时间">
          <el-date-picker
            v-model="queryForm.endTime"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="指标类型">
          <el-select v-model="queryForm.metricType" multiple style="width: 200px">
            <el-option label="CPU使用率" value="cpu" />
            <el-option label="内存使用率" value="memory" />
            <el-option label="磁盘使用率" value="disk" />
            <el-option label="网络IO" value="network" />
            <el-option label="响应时间" value="response_time" />
            <el-option label="错误率" value="error_rate" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="主机">
          <el-select v-model="queryForm.host" style="width: 150px">
            <el-option label="全部主机" value="all" />
            <el-option label="Web服务器" value="web-01" />
            <el-option label="数据库服务器" value="db-01" />
            <el-option label="应用服务器" value="app-01" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="queryMetrics" :loading="queryLoading">
            查询
          </el-button>
          <el-button @click="resetQuery">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 关键指标概览 -->
    <el-row :gutter="20" class="overview-section">
      <el-col :span="6">
        <el-card class="metric-overview-card">
          <el-statistic
            title="平均CPU使用率"
            :value="overviewStats.avgCpu"
            suffix="%"
            :value-style="{ color: getCpuColor(overviewStats.avgCpu) }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Cpu /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-trend">
            <span :class="overviewStats.cpuTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ overviewStats.cpuTrend > 0 ? '↗' : '↘' }} 
              {{ Math.abs(overviewStats.cpuTrend) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-overview-card">
          <el-statistic
            title="平均内存使用率"
            :value="overviewStats.avgMemory"
            suffix="%"
            :value-style="{ color: getMemoryColor(overviewStats.avgMemory) }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Monitor /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-trend">
            <span :class="overviewStats.memoryTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ overviewStats.memoryTrend > 0 ? '↗' : '↘' }} 
              {{ Math.abs(overviewStats.memoryTrend) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-overview-card">
          <el-statistic
            title="平均响应时间"
            :value="overviewStats.avgResponseTime"
            suffix="ms"
            :value-style="{ color: getResponseTimeColor(overviewStats.avgResponseTime) }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Timer /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-trend">
            <span :class="overviewStats.responseTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ overviewStats.responseTrend > 0 ? '↗' : '↘' }} 
              {{ Math.abs(overviewStats.responseTrend) }}ms
            </span>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-overview-card">
          <el-statistic
            title="错误率"
            :value="overviewStats.errorRate"
            suffix="%"
            :value-style="{ color: getErrorRateColor(overviewStats.errorRate) }"
          >
            <template #prefix>
              <el-icon class="metric-icon"><Warning /></el-icon>
            </template>
          </el-statistic>
          <div class="metric-trend">
            <span :class="overviewStats.errorTrend > 0 ? 'trend-up' : 'trend-down'">
              {{ overviewStats.errorTrend > 0 ? '↗' : '↘' }} 
              {{ Math.abs(overviewStats.errorTrend) }}%
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 指标图表 -->
    <el-row :gutter="20" class="charts-section">
      <!-- CPU和内存使用率趋势 -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <h3>
                <el-icon><TrendCharts /></el-icon>
                系统资源使用率趋势
              </h3>
              <el-button-group size="small">
                <el-button 
                  v-for="period in chartPeriods" 
                  :key="period.value"
                  :type="chartPeriod === period.value ? 'primary' : ''"
                  @click="chartPeriod = period.value"
                >
                  {{ period.label }}
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <div class="chart-container" style="height: 300px">
            <div ref="cpuMemoryChart" style="width: 100%; height: 100%"></div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 网络IO和磁盘IO -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>
              <el-icon><Connection /></el-icon>
              网络和磁盘IO
            </h3>
          </template>
          
          <div class="chart-container" style="height: 300px">
            <div ref="networkChart" style="width: 100%; height: 100%"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 响应时间和错误率 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>
              <el-icon><Timer /></el-icon>
              应用响应时间
            </h3>
          </template>
          
          <div class="chart-container" style="height: 300px">
            <div ref="responseTimeChart" style="width: 100%; height: 100%"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>
              <el-icon><Warning /></el-icon>
              错误率统计
            </h3>
          </template>
          
          <div class="chart-container" style="height: 300px">
            <div ref="errorRateChart" style="width: 100%; height: 100%"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 巡检服务器选择 -->
    <el-card class="inspection-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Monitor /></el-icon>
            巡检服务器选择
          </h3>
          <div class="header-actions">
            <el-button 
              type="primary" 
              @click="startInspection" 
              :loading="inspectionLoading"
              :disabled="selectedServers.length === 0"
            >
              开始巡检
            </el-button>
            <el-button 
              type="success" 
              @click="exportInspectionData"
              :disabled="inspectionHistory.length === 0"
            >
              导出巡检数据
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="inspection-content">
        <div class="server-selection">
          <h4>选择巡检服务器</h4>
          <el-checkbox-group v-model="selectedServers">
            <el-row :gutter="20">
              <el-col 
                v-for="server in availableServers" 
                :key="server.id"
                :span="8"
              >
                <el-card 
                  class="server-card" 
                  :class="{ 'selected': selectedServers.includes(server.id) }"
                  @click="toggleServer(server.id)"
                >
                  <div class="server-info">
                    <div class="server-header">
                      <el-checkbox :value="selectedServers.includes(server.id)" />
                      <span class="server-name">{{ server.name }}</span>
                      <el-tag 
                        :type="getServerStatusType(server.status)" 
                        size="small"
                      >
                        {{ server.status === 'online' ? '在线' : '离线' }}
                      </el-tag>
                    </div>
                    <div class="server-details">
                      <p><strong>IP:</strong> {{ server.ip }}</p>
                      <p><strong>端口:</strong> {{ server.port }}</p>
                      <p><strong>类型:</strong> {{ server.type }}</p>
                      <p><strong>上次巡检:</strong> {{ server.lastInspection || '未巡检' }}</p>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-checkbox-group>
        </div>
        
        <el-divider />
        
        <div class="inspection-config">
          <h4>巡检配置</h4>
          <el-form :model="inspectionConfig" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="巡检类型">
                  <el-select v-model="inspectionConfig.type" style="width: 100%">
                    <el-option label="基础巡检" value="basic" />
                    <el-option label="全面巡检" value="full" />
                    <el-option label="性能巡检" value="performance" />
                    <el-option label="安全巡检" value="security" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="巡检时间范围">
                  <el-select v-model="inspectionConfig.timeRange" style="width: 100%">
                    <el-option label="最近1小时" value="1h" />
                    <el-option label="最近6小时" value="6h" />
                    <el-option label="最近24小时" value="24h" />
                    <el-option label="最近7天" value="7d" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="包含AI分析">
                  <el-switch v-model="inspectionConfig.includeAI" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="保存到数据库">
                  <el-switch v-model="inspectionConfig.saveToDatabase" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>
    </el-card>
    
    <!-- 巡检历史 -->
    <el-card class="inspection-history-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Document /></el-icon>
            巡检历史
          </h3>
          <el-button 
            size="small" 
            @click="refreshInspectionHistory"
            :loading="historyLoading"
          >
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="inspectionHistory" 
        style="width: 100%"
        :loading="historyLoading"
      >
        <el-table-column prop="timestamp" label="巡检时间" width="180" />
        <el-table-column prop="type" label="巡检类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getInspectionTypeColor(row.type)" size="small">
              {{ getInspectionTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="servers" label="巡检服务器" min-width="200">
          <template #default="{ row }">
            <el-tag 
              v-for="server in row.servers" 
              :key="server"
              size="small"
              style="margin-right: 5px"
            >
              {{ getServerName(server) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getInspectionStatusColor(row.status)" size="small">
              {{ getInspectionStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="aiAnalysis" label="AI分析" width="100">
          <template #default="{ row }">
            <el-tag :type="row.aiAnalysis ? 'success' : 'info'" size="small">
              {{ row.aiAnalysis ? '已分析' : '未分析' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="viewInspectionDetail(row)"
            >
              查看报告
            </el-button>
            <el-button 
              size="small" 
              type="success" 
              link
              @click="exportInspectionReport(row)"
            >
              导出
            </el-button>
            <el-button 
              v-if="row.status === 'completed' && !row.aiAnalysis"
              size="small" 
              type="warning" 
              link
              @click="triggerAIAnalysis(row)"
            >
              AI分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-pagination">
        <el-pagination
          v-model:current-page="historyCurrentPage"
          v-model:page-size="historyPageSize"
          :page-sizes="[10, 20, 50]"
          :total="totalHistory"
          layout="total, sizes, prev, pager, next"
          @size-change="handleHistorySizeChange"
          @current-change="handleHistoryCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 详细指标数据 -->
    <el-card class="metrics-table-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><Document /></el-icon>
            详细指标数据
          </h3>
          <div class="header-controls">
            <el-input
              v-model="tableSearch"
              placeholder="搜索指标..."
              style="width: 200px; margin-right: 10px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button size="small" @click="exportTableData">
              导出表格
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="filteredMetricsData" 
        style="width: 100%"
        :loading="tableLoading"
        stripe
      >
        <el-table-column prop="timestamp" label="时间" width="180" sortable />
        <el-table-column prop="host" label="主机" width="120" />
        <el-table-column prop="cpu" label="CPU使用率" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: getCpuColor(row.cpu) }">
              {{ row.cpu }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="memory" label="内存使用率" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: getMemoryColor(row.memory) }">
              {{ row.memory }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="disk" label="磁盘使用率" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: getDiskColor(row.disk) }">
              {{ row.disk }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="networkIn" label="网络入站" width="120">
          <template #default="{ row }">
            {{ formatBytes(row.networkIn) }}/s
          </template>
        </el-table-column>
        <el-table-column prop="networkOut" label="网络出站" width="120">
          <template #default="{ row }">
            {{ formatBytes(row.networkOut) }}/s
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="响应时间" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: getResponseTimeColor(row.responseTime) }">
              {{ row.responseTime }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="errorRate" label="错误率" width="100" sortable>
          <template #default="{ row }">
            <span :style="{ color: getErrorRateColor(row.errorRate) }">
              {{ row.errorRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="viewMetricDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="table-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="totalMetrics"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis,
  Refresh,
  Download,
  Cpu,
  Monitor,
  Timer,
  Warning,
  TrendCharts,
  Connection,
  Document,
  Search
} from '@element-plus/icons-vue'

// 图表引用
const cpuMemoryChart = ref<HTMLElement>()
const networkChart = ref<HTMLElement>()
const responseTimeChart = ref<HTMLElement>()
const errorRateChart = ref<HTMLElement>()

// ECharts实例
let cpuMemoryChartInstance: echarts.ECharts | null = null
let networkChartInstance: echarts.ECharts | null = null
let responseTimeChartInstance: echarts.ECharts | null = null
let errorRateChartInstance: echarts.ECharts | null = null

// 响应式数据
const refreshLoading = ref(false)
const queryLoading = ref(false)
const tableLoading = ref(false)
const inspectionLoading = ref(false)
const historyLoading = ref(false)
const tableSearch = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const chartPeriod = ref('24h')
const historyCurrentPage = ref(1)
const historyPageSize = ref(10)
const totalHistory = ref(25)

// 查询表单
const queryForm = ref({
  timeRange: '24h',
  startTime: '',
  endTime: '',
  metricType: ['cpu', 'memory'],
  host: 'all'
})

// 概览统计数据
const overviewStats = ref({
  avgCpu: 68.5,
  cpuTrend: 2.3,
  avgMemory: 74.2,
  memoryTrend: -1.5,
  avgResponseTime: 125,
  responseTrend: 8,
  errorRate: 0.12,
  errorTrend: -0.03
})

// 图表时间周期选项
const chartPeriods = ref([
  { label: '1小时', value: '1h' },
  { label: '6小时', value: '6h' },
  { label: '24小时', value: '24h' },
  { label: '7天', value: '7d' }
])

// 巡检相关数据
const selectedServers = ref<string[]>([])
const availableServers = ref([
  {
    id: 'web-01',
    name: 'Web服务器-01',
    ip: '192.168.1.10',
    port: 9100,
    type: 'Web服务器',
    status: 'online',
    lastInspection: '2025-09-06 20:30:15'
  },
  {
    id: 'db-01',
    name: '数据库服务器-01',
    ip: '192.168.1.20',
    port: 9100,
    type: '数据库服务器',
    status: 'online',
    lastInspection: '2025-09-06 18:45:22'
  },
  {
    id: 'app-01',
    name: '应用服务器-01',
    ip: '192.168.1.30',
    port: 9100,
    type: '应用服务器',
    status: 'online',
    lastInspection: '2025-09-06 22:15:10'
  },
  {
    id: 'cache-01',
    name: '缓存服务器-01',
    ip: '192.168.1.40',
    port: 9100,
    type: '缓存服务器',
    status: 'offline',
    lastInspection: '2025-09-05 16:20:30'
  },
  {
    id: 'lb-01',
    name: '负载均衡器-01',
    ip: '192.168.1.50',
    port: 9100,
    type: '负载均衡器',
    status: 'online',
    lastInspection: '2025-09-06 21:30:45'
  },
  {
    id: 'monitor-01',
    name: '监控服务器-01',
    ip: '192.168.1.60',
    port: 9100,
    type: '监控服务器',
    status: 'online',
    lastInspection: '2025-09-06 19:10:15'
  }
])

// 巡检配置
const inspectionConfig = ref({
  type: 'full',
  timeRange: '24h',
  includeAI: true,
  saveToDatabase: true
})

// 巡检历史数据
const inspectionHistory = ref([
  {
    id: 1,
    timestamp: '2025-09-06 20:30:15',
    type: 'full',
    servers: ['web-01', 'db-01', 'app-01'],
    status: 'completed',
    duration: '5分钟',
    aiAnalysis: true
  },
  {
    id: 2,
    timestamp: '2025-09-06 18:45:22',
    type: 'basic',
    servers: ['db-01'],
    status: 'completed',
    duration: '2分钟',
    aiAnalysis: false
  },
  {
    id: 3,
    timestamp: '2025-09-06 16:20:30',
    type: 'performance',
    servers: ['web-01', 'app-01'],
    status: 'failed',
    duration: '3分钟',
    aiAnalysis: false
  },
  {
    id: 4,
    timestamp: '2025-09-06 14:10:15',
    type: 'security',
    servers: ['web-01', 'db-01', 'app-01', 'lb-01'],
    status: 'completed',
    duration: '8分钟',
    aiAnalysis: true
  },
  {
    id: 5,
    timestamp: '2025-09-06 12:05:40',
    type: 'full',
    servers: ['monitor-01'],
    status: 'running',
    duration: '-',
    aiAnalysis: false
  }
])

// 指标数据
const metricsData = ref([
  {
    id: 1,
    timestamp: '2025-09-06 22:45:00',
    host: 'web-01',
    cpu: 72.5,
    memory: 68.3,
    disk: 45.2,
    networkIn: 1024 * 1024 * 2.5, // 2.5MB/s
    networkOut: 1024 * 1024 * 1.8, // 1.8MB/s
    responseTime: 145,
    errorRate: 0.15
  },
  {
    id: 2,
    timestamp: '2025-09-06 22:40:00',
    host: 'db-01',
    cpu: 65.8,
    memory: 82.1,
    disk: 67.9,
    networkIn: 1024 * 1024 * 1.2,
    networkOut: 1024 * 1024 * 0.8,
    responseTime: 98,
    errorRate: 0.05
  },
  {
    id: 3,
    timestamp: '2025-09-06 22:35:00',
    host: 'app-01',
    cpu: 58.2,
    memory: 71.5,
    disk: 34.1,
    networkIn: 1024 * 1024 * 3.2,
    networkOut: 1024 * 1024 * 2.1,
    responseTime: 167,
    errorRate: 0.22
  },
  {
    id: 4,
    timestamp: '2025-09-06 22:30:00',
    host: 'web-01',
    cpu: 84.3,
    memory: 76.8,
    disk: 48.7,
    networkIn: 1024 * 1024 * 4.1,
    networkOut: 1024 * 1024 * 3.2,
    responseTime: 203,
    errorRate: 0.38
  },
  {
    id: 5,
    timestamp: '2025-09-06 22:25:00',
    host: 'db-01',
    cpu: 59.7,
    memory: 79.4,
    disk: 72.3,
    networkIn: 1024 * 1024 * 0.9,
    networkOut: 1024 * 1024 * 0.6,
    responseTime: 89,
    errorRate: 0.03
  },
  {
    id: 6,
    timestamp: '2025-09-06 22:20:00',
    host: 'app-01',
    cpu: 63.1,
    memory: 68.9,
    disk: 38.5,
    networkIn: 1024 * 1024 * 2.8,
    networkOut: 1024 * 1024 * 1.9,
    responseTime: 134,
    errorRate: 0.18
  }
])

// 计算属性
const totalMetrics = computed(() => metricsData.value.length)

const filteredMetricsData = computed(() => {
  if (!tableSearch.value) {
    return metricsData.value
  }
  return metricsData.value.filter(item => 
    item.host.toLowerCase().includes(tableSearch.value.toLowerCase()) ||
    item.timestamp.includes(tableSearch.value)
  )
})

// 方法函数

/**
 * 刷新指标数据
 */
const refreshMetrics = async () => {
  refreshLoading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 更新概览数据
    overviewStats.value.avgCpu = Math.random() * 30 + 50
    overviewStats.value.avgMemory = Math.random() * 20 + 60
    overviewStats.value.avgResponseTime = Math.random() * 100 + 80
    overviewStats.value.errorRate = Math.random() * 0.5
    
    ElMessage.success('指标数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    refreshLoading.value = false
  }
}

/**
 * 导出指标数据
 */
const exportMetrics = () => {
  ElMessage.info('导出功能开发中...')
}

/**
 * 查询指标
 */
const queryMetrics = async () => {
  queryLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('查询完成')
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    queryLoading.value = false
  }
}

/**
 * 重置查询条件
 */
const resetQuery = () => {
  queryForm.value = {
    timeRange: '24h',
    startTime: '',
    endTime: '',
    metricType: ['cpu', 'memory'],
    host: 'all'
  }
}

/**
 * 导出表格数据
 */
const exportTableData = () => {
  ElMessage.info('导出表格功能开发中...')
}

/**
 * 查看指标详情
 */
const viewMetricDetail = (row: any) => {
  ElMessage.info(`查看${row.host}的详细指标信息`)
  // TODO: 打开详情对话框或跳转到详情页面
}

/**
 * 处理分页大小变化
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  ElMessage.success(`已切换到每页${size}条`)
}

/**
 * 处理当前页变化
 */
const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

/**
 * 初始化图表
 */
const initCharts = async () => {
  await nextTick()
  
  // CPU和内存图表
  if (cpuMemoryChart.value) {
    cpuMemoryChartInstance = echarts.init(cpuMemoryChart.value)
    cpuMemoryChartInstance.setOption(getCPUMemoryOption())
  }
  
  // 网络 IO图表
  if (networkChart.value) {
    networkChartInstance = echarts.init(networkChart.value)
    networkChartInstance.setOption(getNetworkOption())
  }
  
  // 响应时间图表
  if (responseTimeChart.value) {
    responseTimeChartInstance = echarts.init(responseTimeChart.value)
    responseTimeChartInstance.setOption(getResponseTimeOption())
  }
  
  // 错误率图表
  if (errorRateChart.value) {
    errorRateChartInstance = echarts.init(errorRateChart.value)
    errorRateChartInstance.setOption(getErrorRateOption())
  }
}

/**
 * 获取CPU和内存图表配置
 */
const getCPUMemoryOption = () => {
  const hours = []
  const cpuData = []
  const memoryData = []
  
  // 生成模拟数据
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000)
    hours.push(hour.getHours() + ':00')
    cpuData.push(Math.random() * 40 + 30) // 30-70%
    memoryData.push(Math.random() * 30 + 50) // 50-80%
  }
  
  return {
    title: {
      text: 'CPU和内存使用率',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let html = params[0].axisValueLabel + '<br/>'
        params.forEach((param: any) => {
          html += param.marker + param.seriesName + ': ' + param.value.toFixed(1) + '%<br/>'
        })
        return html
      }
    },
    legend: {
      data: ['CPU使用率', '内存使用率'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        smooth: true,
        data: cpuData,
        lineStyle: { color: '#409eff' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
      },
      {
        name: '内存使用率',
        type: 'line',
        smooth: true,
        data: memoryData,
        lineStyle: { color: '#67c23a' },
        areaStyle: { color: 'rgba(103, 194, 58, 0.2)' }
      }
    ]
  }
}

/**
 * 获取网络 IO图表配置
 */
const getNetworkOption = () => {
  const hours = []
  const inData = []
  const outData = []
  
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000)
    hours.push(hour.getHours() + ':00')
    inData.push(Math.random() * 500 + 100)
    outData.push(Math.random() * 300 + 50)
  }
  
  return {
    title: {
      text: '网络 IO 流量',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let html = params[0].axisValueLabel + '<br/>'
        params.forEach((param: any) => {
          html += param.marker + param.seriesName + ': ' + param.value.toFixed(1) + ' MB/s<br/>'
        })
        return html
      }
    },
    legend: {
      data: ['网络入站', '网络出站'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value} MB/s'
      }
    },
    series: [
      {
        name: '网络入站',
        type: 'bar',
        data: inData,
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '网络出站',
        type: 'bar',
        data: outData,
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }
}

/**
 * 获取响应时间图表配置
 */
const getResponseTimeOption = () => {
  const data = [
    { name: 'API接口', value: 120 },
    { name: '数据库查询', value: 89 },
    { name: '缓存访问', value: 15 },
    { name: '文件操作', value: 200 },
    { name: '网络请求', value: 156 }
  ]
  
  return {
    title: {
      text: '响应时间分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}ms ({d}%)'
    },
    series: [
      {
        name: '响应时间',
        type: 'pie',
        radius: ['40%', '70%'],
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
}

/**
 * 获取错误率图表配置
 */
const getErrorRateOption = () => {
  const hours = []
  const errorData = []
  
  for (let i = 23; i >= 0; i--) {
    const hour = new Date(Date.now() - i * 60 * 60 * 1000)
    hours.push(hour.getHours() + ':00')
    errorData.push(Math.random() * 0.5)
  }
  
  return {
    title: {
      text: '系统错误率趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        return params[0].axisValueLabel + '<br/>' +
               params[0].marker + '错误率: ' + params[0].value.toFixed(3) + '%'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '错误率',
        type: 'line',
        smooth: true,
        data: errorData,
        lineStyle: { color: '#f56c6c', width: 3 },
        areaStyle: { color: 'rgba(245, 108, 108, 0.2)' },
        markLine: {
          data: [
            { yAxis: 0.3, name: '警告线', lineStyle: { color: '#e6a23c', type: 'dashed' } }
          ]
        }
      }
    ]
  }
}

/**
 * 巡检相关方法
 */

/**
 * 切换服务器选择状态
 */
const toggleServer = (serverId: string) => {
  const index = selectedServers.value.indexOf(serverId)
  if (index > -1) {
    selectedServers.value.splice(index, 1)
  } else {
    selectedServers.value.push(serverId)
  }
}

/**
 * 开始巡检
 */
const startInspection = async () => {
  if (selectedServers.value.length === 0) {
    ElMessage.warning('请选择要巡检的服务器')
    return
  }

  inspectionLoading.value = true
  try {
    const newInspection = {
      id: Date.now(),
      timestamp: new Date().toLocaleString('zh-CN'),
      type: inspectionConfig.value.type,
      servers: [...selectedServers.value],
      status: 'running',
      duration: '-',
      aiAnalysis: false
    }
    
    // 添加到历史记录
    inspectionHistory.value.unshift(newInspection)
    
    ElMessage.info(`正在对 ${selectedServers.value.length} 个服务器进行巡棄...`)
    
    // 模拟巡检过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 更新状态
    const inspection = inspectionHistory.value.find(item => item.id === newInspection.id)
    if (inspection) {
      inspection.status = 'completed'
      inspection.duration = `${Math.floor(Math.random() * 5) + 2}分钟`
      
      // 如果包含AI分析
      if (inspectionConfig.value.includeAI) {
        ElMessage.info('正在进行AI分析...')
        await new Promise(resolve => setTimeout(resolve, 2000))
        inspection.aiAnalysis = true
      }
    }
    
    // 更新服务器最后巡检时间
    selectedServers.value.forEach(serverId => {
      const server = availableServers.value.find(s => s.id === serverId)
      if (server) {
        server.lastInspection = new Date().toLocaleString('zh-CN')
      }
    })
    
    ElMessage.success('巡检完成！')
    
    // 清空选择
    selectedServers.value = []
  } catch (error) {
    ElMessage.error('巡检失败，请稍后重试')
  } finally {
    inspectionLoading.value = false
  }
}

/**
 * 导出巡检数据
 */
const exportInspectionData = () => {
  if (inspectionHistory.value.length === 0) {
    ElMessage.warning('暂无巡检数据可导出')
    return
  }
  
  try {
    const data = {
      exportTime: new Date().toLocaleString('zh-CN'),
      totalInspections: inspectionHistory.value.length,
      inspections: inspectionHistory.value.map(item => ({
        ...item,
        servers: item.servers.map(serverId => {
          const server = availableServers.value.find(s => s.id === serverId)
          return server ? server.name : serverId
        })
      }))
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `inspection_data_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('巡检数据导出成功！')
  } catch (error) {
    ElMessage.error('导出失败，请稍后重试')
  }
}

/**
 * 查看巡检详情
 */
const viewInspectionDetail = (inspection: any) => {
  ElMessage.info(`查看巡检报告: ${inspection.timestamp}`)
  // 这里可以打开详情对话框或跳转到详情页面
}

/**
 * 导出巡检报告
 */
const exportInspectionReport = (inspection: any) => {
  try {
    const report = {
      inspectionId: inspection.id,
      timestamp: inspection.timestamp,
      type: getInspectionTypeText(inspection.type),
      servers: inspection.servers.map((serverId: string) => {
        const server = availableServers.value.find(s => s.id === serverId)
        return server ? {
          id: server.id,
          name: server.name,
          ip: server.ip,
          type: server.type
        } : { id: serverId, name: serverId }
      }),
      status: getInspectionStatusText(inspection.status),
      duration: inspection.duration,
      aiAnalysis: inspection.aiAnalysis,
      exportTime: new Date().toLocaleString('zh-CN')
    }
    
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `inspection_report_${inspection.id}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功！')
  } catch (error) {
    ElMessage.error('导出失败，请稍后重试')
  }
}

/**
 * 触发AI分析
 */
const triggerAIAnalysis = async (inspection: any) => {
  try {
    ElMessage.info('正在启动AI分析...')
    
    // 模拟AI分析过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    inspection.aiAnalysis = true
    ElMessage.success('AI分析完成！')
  } catch (error) {
    ElMessage.error('AI分析失败，请稍后重试')
  }
}

/**
 * 刷新巡检历史
 */
const refreshInspectionHistory = async () => {
  historyLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('巡检历史已刷新')
  } catch (error) {
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    historyLoading.value = false
  }
}

/**
 * 历史记录分页处理
 */
const handleHistorySizeChange = (size: number) => {
  historyPageSize.value = size
}

const handleHistoryCurrentChange = (page: number) => {
  historyCurrentPage.value = page
}

/**
 * 巡检相关工具函数
 */

/**
 * 获取服务器状态类型
 */
const getServerStatusType = (status: string) => {
  return status === 'online' ? 'success' : 'danger'
}

/**
 * 获取服务器名称
 */
const getServerName = (serverId: string) => {
  const server = availableServers.value.find(s => s.id === serverId)
  return server ? server.name : serverId
}

/**
 * 获取巡检类型颜色
 */
const getInspectionTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    basic: 'info',
    full: 'primary',
    performance: 'warning',
    security: 'danger'
  }
  return colorMap[type] || 'info'
}

/**
 * 获取巡检类型文本
 */
const getInspectionTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    basic: '基础巡检',
    full: '全面巡检',
    performance: '性能巡检',
    security: '安全巡检'
  }
  return textMap[type] || type
}

/**
 * 获取巡检状态颜色
 */
const getInspectionStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colorMap[status] || 'info'
}

/**
 * 获取巡检状态文本
 */
const getInspectionStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    running: '运行中',
    completed: '已完成',
    failed: '已失败'
  }
  return textMap[status] || status
}

// 工具函数

/**
 * 获取图表周期文本
 */
const getChartPeriodText = () => {
  const periodMap: Record<string, string> = {
    '1h': '1小时',
    '6h': '6小时', 
    '24h': '24小时',
    '7d': '7天'
  }
  return periodMap[chartPeriod.value] || '24小时'
}

/**
 * 格式化字节数
 */
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * 获取CPU颜色
 */
const getCpuColor = (value: number): string => {
  if (value >= 80) return '#f56c6c'
  if (value >= 60) return '#e6a23c'
  return '#67c23a'
}

/**
 * 获取内存颜色
 */
const getMemoryColor = (value: number): string => {
  if (value >= 85) return '#f56c6c'
  if (value >= 70) return '#e6a23c'
  return '#67c23a'
}

/**
 * 获取磁盘颜色
 */
const getDiskColor = (value: number): string => {
  if (value >= 90) return '#f56c6c'
  if (value >= 75) return '#e6a23c'
  return '#67c23a'
}

/**
 * 获取响应时间颜色
 */
const getResponseTimeColor = (value: number): string => {
  if (value >= 200) return '#f56c6c'
  if (value >= 150) return '#e6a23c'
  return '#67c23a'
}

/**
 * 获取错误率颜色
 */
const getErrorRateColor = (value: number): string => {
  if (value >= 0.3) return '#f56c6c'
  if (value >= 0.1) return '#e6a23c'
  return '#67c23a'
}

/**
 * 销毁图表实例
 */
const destroyCharts = () => {
  if (cpuMemoryChartInstance) {
    cpuMemoryChartInstance.dispose()
    cpuMemoryChartInstance = null
  }
  if (networkChartInstance) {
    networkChartInstance.dispose()
    networkChartInstance = null
  }
  if (responseTimeChartInstance) {
    responseTimeChartInstance.dispose()
    responseTimeChartInstance = null
  }
  if (errorRateChartInstance) {
    errorRateChartInstance.dispose()
    errorRateChartInstance = null
  }
}

/**
 * 窗口大小调整处理
 */
const handleResize = () => {
  if (cpuMemoryChartInstance) cpuMemoryChartInstance.resize()
  if (networkChartInstance) networkChartInstance.resize()
  if (responseTimeChartInstance) responseTimeChartInstance.resize()
  if (errorRateChartInstance) errorRateChartInstance.resize()
}

// 生命周期钩子
onMounted(async () => {
  document.title = '监控指标 - 智能监控预警系统'
  
  // 初始化图表
  await initCharts()
  
  // 添加窗口大小调整监听器
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 销毁图表实例
  destroyCharts()
  
  // 移除事件监听器
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.metrics {
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
  
  .query-section {
    margin-bottom: 24px;
    
    .query-form {
      .el-form-item {
        margin-bottom: 16px;
      }
    }
  }
  
  .overview-section {
    margin-bottom: 24px;
    
    .metric-overview-card {
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
      position: relative;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .metric-icon {
        font-size: 20px;
        margin-right: 8px;
      }
      
      .metric-trend {
        position: absolute;
        top: 16px;
        right: 16px;
        font-size: 12px;
        font-weight: 500;
        
        .trend-up {
          color: #f56c6c;
        }
        
        .trend-down {
          color: #67c23a;
        }
      }
    }
  }
  
  .charts-section {
    margin-bottom: 24px;
    
    .chart-card {
      height: 400px;
      
      .chart-header {
        @include flex-between;
        
        h3 {
          @include flex-center;
          margin: 0;
          gap: 8px;
        }
      }
      
      .chart-container {
        height: 320px;
        
        .chart-placeholder {
          @include flex-center;
          flex-direction: column;
          height: 100%;
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
    }
  }
  
  .metrics-table-section {
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
    
    .el-table {
      margin-top: 16px;
      
      .el-button--small {
        padding: 4px 8px;
      }
    }
    
    .table-pagination {
      @include flex-center;
      margin-top: 20px;
    }
  }
  
  .inspection-section {
    margin-bottom: 24px;
    
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
      }
      
      .header-actions {
        @include flex-center;
        gap: 12px;
      }
    }
    
    .inspection-content {
      .server-selection {
        h4 {
          margin: 0 0 16px 0;
          color: var(--el-text-color-primary);
          font-weight: 600;
        }
        
        .server-card {
          cursor: pointer;
          transition: all 0.2s;
          border: 2px solid transparent;
          
          &:hover {
            border-color: var(--el-color-primary-light-5);
            transform: translateY(-2px);
          }
          
          &.selected {
            border-color: var(--el-color-primary);
            background: var(--el-color-primary-light-9);
          }
          
          .server-info {
            .server-header {
              @include flex-between;
              margin-bottom: 12px;
              
              .server-name {
                font-weight: 600;
                color: var(--el-text-color-primary);
              }
            }
            
            .server-details {
              p {
                margin: 4px 0;
                font-size: 12px;
                color: var(--el-text-color-secondary);
                
                strong {
                  color: var(--el-text-color-primary);
                }
              }
            }
          }
        }
      }
      
      .inspection-config {
        h4 {
          margin: 0 0 16px 0;
          color: var(--el-text-color-primary);
          font-weight: 600;
        }
      }
    }
  }
  
  .inspection-history-section {
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
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
  .metrics {
    .charts-section .el-col {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .metrics {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .overview-section .el-col {
      margin-bottom: 16px;
    }
    
    .query-section {
      .query-form {
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
  .chart-placeholder {
    background: var(--monitor-bg-secondary) !important;
  }
  
  .metric-overview-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
}
</style>