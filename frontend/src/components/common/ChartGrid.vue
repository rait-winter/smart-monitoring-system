<template>
  <div 
    class="chart-grid" 
    :class="[gridClass, { 'grid-responsive': responsive }]"
  >
    <!-- 图表项 -->
    <div 
      v-for="(chart, index) in charts"
      :key="chart.id || index"
      class="chart-item"
      :class="{
        'chart-highlighted': chart.highlighted,
        [`span-${chart.span}`]: chart.span
      }"
      :style="{ height: chart.height || defaultHeight }"
    >
      <!-- 图表头部 -->
      <div v-if="showHeader" class="chart-header">
        <div class="chart-title-section">
          <el-icon v-if="chart.icon" class="chart-icon">
            <component :is="chart.icon" />
          </el-icon>
          <h4 class="chart-title">{{ chart.title }}</h4>
          <el-tag 
            v-if="chart.status" 
            :type="getStatusType(chart.status)"
            size="small"
          >
            {{ chart.status }}
          </el-tag>
        </div>
        
        <div class="chart-actions">
          <el-button
            size="small"
            text
            circle
            @click="refreshChart(chart, index)"
            title="刷新"
          >
            <el-icon><Refresh /></el-icon>
          </el-button>
          
          <el-dropdown 
            @command="(cmd: string) => exportChart(chart, index, cmd)"
            placement="bottom-end"
          >
            <el-button size="small" text circle title="导出">
              <el-icon><Download /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="png">PNG 图片</el-dropdown-item>
                <el-dropdown-item command="jpg">JPG 图片</el-dropdown-item>
                <el-dropdown-item command="svg">SVG 矢量图</el-dropdown-item>
                <el-dropdown-item command="pdf">PDF 文档</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <el-button
            size="small"
            text
            circle
            @click="toggleFullscreen(chart, index)"
            title="全屏"
          >
            <el-icon><FullScreen /></el-icon>
          </el-button>
          
          <el-button
            size="small"
            text
            circle
            @click="openConfig(chart, index)"
            title="配置"
          >
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>
      
      <!-- 图表内容 -->
      <div class="chart-content">
        <MonitorChart
          :ref="(el: any) => setChartRef(el, index)"
          :chart-data="chart.data"
          :chart-type="chart.type"
          :theme="chart.theme || theme"
          :loading="chart.loading"
          :large="chart.large"
          :config="chart.config"
          :responsive="chart.responsive"
          @chart-event="(type: string, params: any) => handleChartEvent(type, chart, index, params)"
          @chart-error="(error: Error) => handleChartError(chart, index, error)"
        />
      </div>
      
      <!-- 图表统计 -->
      <div v-if="showStats && chart.stats" class="chart-stats">
        <div 
          v-for="(stat, key) in chart.stats"
          :key="key"
          class="stat-item"
          :class="`stat-${stat.type || 'info'}`"
        >
          <span class="stat-label">{{ stat.label }}:</span>
          <span class="stat-value">{{ formatStatValue(stat.value, stat.unit) }}</span>
          <el-icon v-if="stat.trend" :class="`trend-${stat.trend}`">
            <ArrowUp v-if="stat.trend === 'up'" />
            <ArrowDown v-if="stat.trend === 'down'" />
            <Minus v-if="stat.trend === 'stable'" />
          </el-icon>
        </div>
      </div>
    </div>
    
    <!-- 添加图表按钮 -->
    <div v-if="allowAdd" class="add-chart-btn" @click="addChart">
      <div class="add-chart-content">
        <el-icon class="add-icon">
          <Plus />
        </el-icon>
        <span>添加图表</span>
      </div>
    </div>
  </div>

  <!-- 全屏弹窗 -->
  <el-dialog
    v-model="fullscreenVisible"
    :title="fullscreenChart?.title || '图表详情'"
    width="90%"
    top="5%"
    custom-class="chart-fullscreen-dialog"
    destroy-on-close
  >
    <div style="height: 70vh;">
      <MonitorChart
        v-if="fullscreenChart"
        :chart-data="fullscreenChart.data"
        :chart-type="fullscreenChart.type"
        :theme="fullscreenChart.theme || theme"
        :large="true"
        :config="fullscreenChart.config"
        :responsive="true"
      />
    </div>
  </el-dialog>

  <!-- 配置弹窗 -->
  <el-dialog
    v-model="configVisible"
    title="图表配置"
    width="500px"
    custom-class="chart-config-dialog"
  >
    <el-form
      class="chart-config-form"
      :model="configForm"
      label-width="100px"
    >
      <el-form-item label="图表标题">
        <el-input v-model="configForm.title" placeholder="请输入图表标题" />
      </el-form-item>
      
      <el-form-item label="图表类型">
        <el-select v-model="configForm.type" placeholder="请选择图表类型">
          <el-option label="线图" value="line" />
          <el-option label="柱状图" value="bar" />
          <el-option label="饼图" value="pie" />
          <el-option label="仪表盘" value="gauge" />
          <el-option label="散点图" value="scatter" />
          <el-option label="热力图" value="heatmap" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="图表高度">
        <el-input v-model="configForm.height" placeholder="如: 300px" />
      </el-form-item>
      
      <el-form-item label="大数据模式">
        <el-switch v-model="configForm.large" />
      </el-form-item>
      
      <el-form-item label="刷新间隔">
        <el-input-number
          v-model="configForm.refreshInterval"
          :min="0"
          :max="3600"
          controls-position="right"
        />
        <span style="margin-left: 8px; color: var(--el-text-color-secondary);">秒</span>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="configVisible = false">取消</el-button>
      <el-button type="primary" @click="saveConfig">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  Download, 
  FullScreen, 
  Setting, 
  Plus,
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue'
import MonitorChart from './MonitorChart.vue'
import { formatValue } from '@/utils/echarts'

// ======== 类型定义 ========
export interface ChartItem {
  id?: string
  title?: string
  subtitle?: string
  type: 'line' | 'bar' | 'pie' | 'gauge' | 'scatter' | 'heatmap'
  data: any
  height?: string
  width?: string
  config?: any
  loading?: boolean
  theme?: 'light' | 'dark' | 'auto'
  responsive?: boolean
  large?: boolean
  refreshInterval?: number
  span?: number // 网格跨度
  icon?: any // 图标组件
  status?: string // 状态文本
  highlighted?: boolean // 是否高亮
  stats?: Record<string, {
    label: string
    value: number
    unit?: string
    type?: 'success' | 'warning' | 'danger' | 'info'
    trend?: 'up' | 'down' | 'stable'
  }>
}

export interface Props {
  charts: ChartItem[]
  layout?: '1x1' | '2x1' | '2x2' | '3x2' | '4x2' | 'auto'
  theme?: 'light' | 'dark' | 'auto'
  responsive?: boolean
  showHeader?: boolean
  showStats?: boolean
  allowAdd?: boolean
  defaultHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'auto',
  theme: 'auto',
  responsive: true,
  showHeader: true,
  showStats: true,
  allowAdd: false,
  defaultHeight: '300px'
})

// ======== 组件事件 ========
const emit = defineEmits<{
  chartEvent: [type: string, chart: ChartItem, index: number, params: any]
  chartError: [chart: ChartItem, index: number, error: Error]
  chartRefresh: [chart: ChartItem, index: number]
  chartConfig: [chart: ChartItem, index: number, config: any]
  addChart: []
}>()

// ======== 响应式数据 ========
const chartRefs = ref<any[]>([])
const fullscreenVisible = ref(false)
const fullscreenChart = ref<ChartItem | null>(null)
const configVisible = ref(false)
const configChart = ref<ChartItem | null>(null)
const configChartIndex = ref(-1)
const configForm = ref({
  title: '',
  type: 'line' as ChartItem['type'],
  height: '300px',
  large: false,
  refreshInterval: 0
})

// ======== 计算属性 ========
const gridClass = computed(() => {
  if (props.layout === 'auto') {
    const count = props.charts.length
    if (count <= 1) return 'grid-1x1'
    if (count <= 2) return 'grid-2x1'
    if (count <= 4) return 'grid-2x2'
    if (count <= 6) return 'grid-3x2'
    return 'grid-4x2'
  }
  return `grid-${props.layout}`
})

// ======== 方法函数 ========

/**
 * 设置图表引用
 */
const setChartRef = (el: any, index: number) => {
  if (el) {
    chartRefs.value[index] = el
  }
}

/**
 * 获取状态类型
 */
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '正常': 'success',
    '运行中': 'success',
    '警告': 'warning',
    '异常': 'danger',
    '错误': 'danger',
    '离线': 'info',
    '停止': 'info'
  }
  return statusMap[status] || 'info'
}

/**
 * 格式化统计值
 */
const formatStatValue = (value: number, unit?: string) => {
  return formatValue(value, unit)
}

/**
 * 处理图表事件
 */
const handleChartEvent = (type: string, chart: ChartItem, index: number, params: any) => {
  emit('chartEvent', type, chart, index, params)
}

/**
 * 处理图表错误
 */
const handleChartError = (chart: ChartItem, index: number, error: Error) => {
  emit('chartError', chart, index, error)
}

/**
 * 刷新图表
 */
const refreshChart = (chart: ChartItem, index: number) => {
  emit('chartRefresh', chart, index)
}

/**
 * 切换全屏
 */
const toggleFullscreen = (chart: ChartItem, index: number) => {
  fullscreenChart.value = chart
  fullscreenVisible.value = true
}

/**
 * 导出图表
 */
const exportChart = (chart: ChartItem, index: number, format: string) => {
  const chartRef = chartRefs.value[index]
  if (chartRef && chartRef.exportChart) {
    chartRef.exportChart(format)
  } else {
    ElMessage.warning('图表导出功能不可用')
  }
}

/**
 * 打开配置
 */
const openConfig = (chart: ChartItem, index: number) => {
  configChart.value = chart
  configChartIndex.value = index
  configForm.value = {
    title: chart.title || '',
    type: chart.type,
    height: chart.height || '300px',
    large: chart.large || false,
    refreshInterval: chart.refreshInterval ? chart.refreshInterval / 1000 : 0
  }
  configVisible.value = true
}

/**
 * 保存配置
 */
const saveConfig = () => {
  if (configChart.value) {
    const newConfig = {
      ...configChart.value,
      title: configForm.value.title,
      type: configForm.value.type,
      height: configForm.value.height,
      large: configForm.value.large,
      refreshInterval: configForm.value.refreshInterval * 1000
    }
    
    emit('chartConfig', configChart.value, configChartIndex.value, newConfig)
    configVisible.value = false
    ElMessage.success('图表配置已保存')
  }
}

/**
 * 添加图表
 */
const addChart = () => {
  emit('addChart')
}

/**
 * 调整所有图表大小
 */
const resizeAllCharts = () => {
  nextTick(() => {
    chartRefs.value.forEach(chartRef => {
      if (chartRef && chartRef.resizeChart) {
        chartRef.resizeChart()
      }
    })
  })
}

// ======== 暴露方法 ========
defineExpose({
  resizeAllCharts,
  chartRefs
})
</script>

<style scoped lang="scss">
@use '@/styles/mixins.scss' as *;

.chart-grid {
  display: grid;
  gap: $margin-lg;
  width: 100%;
  
  // 不同布局的网格配置
  &.grid-1x1 {
    grid-template-columns: 1fr;
  }
  
  &.grid-2x1 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.grid-2x2 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
  
  &.grid-3x2 {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
  
  &.grid-4x2 {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
  
  // 响应式布局
  &.grid-responsive {
    @include respond-to(xs) {
      grid-template-columns: 1fr !important;
      grid-template-rows: auto !important;
    }
    
    @include respond-to(sm) {
      grid-template-columns: repeat(1, 1fr) !important;
      grid-template-rows: auto !important;
    }
    
    @include respond-to(md) {
      grid-template-columns: repeat(2, 1fr) !important;
    }
  }
}

.chart-item {
  @include monitor-card;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  transition: all $transition-base ease;
  overflow: hidden;
  
  &.chart-highlighted {
    @include elevation(3);
    border: 2px solid var(--el-color-primary);
  }
  
  // 跨度支持
  &.span-2 {
    grid-column: span 2;
  }
  
  &.span-3 {
    grid-column: span 3;
  }
  
  &.span-4 {
    grid-column: span 4;
  }
  
  // 图表头部
  .chart-header {
    @include flex-between;
    padding: $padding-md $padding-lg;
    border-bottom: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-lighter);
    
    .chart-title-section {
      @include flex-start;
      gap: $margin-sm;
      
      .chart-icon {
        color: var(--el-color-primary);
        font-size: 18px;
      }
      
      .chart-title {
        margin: 0;
        font-size: $font-size-md;
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
    }
    
    .chart-actions {
      @include flex-start;
      gap: $margin-xs;
      
      .el-button {
        &.is-circle {
          width: 28px;
          height: 28px;
          padding: 0;
        }
      }
    }
  }
  
  // 图表内容
  .chart-content {
    flex: 1;
    padding: $padding-sm;
    overflow: hidden;
  }
  
  // 图表统计
  .chart-stats {
    display: flex;
    flex-wrap: wrap;
    gap: $margin-md;
    padding: $padding-md $padding-lg;
    border-top: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-extra-light);
    
    .stat-item {
      @include flex-start;
      gap: $margin-xs;
      font-size: $font-size-sm;
      
      .stat-label {
        color: var(--el-text-color-secondary);
      }
      
      .stat-value {
        font-weight: 500;
        color: var(--el-text-color-primary);
      }
      
      .trend-up {
        color: $success-color;
      }
      
      .trend-down {
        color: $danger-color;
      }
      
      .trend-stable {
        color: var(--el-text-color-secondary);
      }
      
      &.stat-success .stat-value {
        color: $success-color;
      }
      
      &.stat-warning .stat-value {
        color: $warning-color;
      }
      
      &.stat-danger .stat-value {
        color: $danger-color;
      }
      
      &.stat-info .stat-value {
        color: $info-color;
      }
    }
  }
}

// 添加图表按钮
.add-chart-btn {
  @include flex-center;
  min-height: 200px;
  border: 2px dashed var(--el-border-color);
  background: var(--el-fill-color-lighter);
  cursor: pointer;
  transition: all $transition-fast ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    background: var(--el-fill-color-light);
  }
  
  .add-chart-content {
    @include flex-column-center;
    gap: $margin-sm;
    color: var(--el-text-color-secondary);
    
    .add-icon {
      font-size: 32px;
    }
    
    span {
      font-size: $font-size-base;
    }
  }
}

// 弹窗样式
:deep(.chart-fullscreen-dialog) {
  .el-dialog__body {
    padding: $padding-lg;
  }
}

:deep(.chart-config-dialog) {
  .chart-config-form {
    .el-form-item {
      margin-bottom: $margin-lg;
    }
  }
}

// 暗色模式适配
.dark {
  .chart-item {
    .chart-header {
      background: var(--el-fill-color-dark);
    }
    
    .chart-stats {
      background: var(--el-fill-color-darker);
    }
  }
  
  .add-chart-btn {
    background: var(--el-fill-color-dark);
    
    &:hover {
      background: var(--el-fill-color);
    }
  }
}
</style>