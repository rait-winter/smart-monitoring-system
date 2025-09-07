<template>
  <div 
    class="monitor-chart"
    :class="{
      'chart-loading': loading,
      [`chart-${type}`]: type
    }"
  >
    <!-- 图表容器 -->
    <div 
      ref="chartRef"
      class="chart-container"
      :style="{ height: height || '300px' }"
    />
    
    <!-- 加载状态覆盖层 -->
    <div v-if="loading" class="chart-loading-overlay">
      <el-icon class="chart-loading-icon is-loading">
        <Loading />
      </el-icon>
      <div class="chart-loading-text">{{ loadingText }}</div>
    </div>
    
    <!-- 错误状态覆盖层 -->
    <div v-if="hasError" class="chart-error-overlay">
      <el-icon class="chart-error-icon">
        <Warning />
      </el-icon>
      <div class="chart-error-text">{{ errorMessage }}</div>
      <el-button @click="retry" type="primary" size="small">
        重试
      </el-button>
    </div>
    
    <!-- 空数据状态覆盖层 -->
    <div v-if="!loading && !hasError && isEmpty" class="chart-empty-overlay">
      <el-icon class="chart-empty-icon">
        <Document />
      </el-icon>
      <div class="chart-empty-text">{{ emptyText }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useDark, useResizeObserver } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import { Loading, Warning, Document } from '@element-plus/icons-vue'
import { 
  generateChartOption, 
  createResponsiveChart, 
  type MetricChartOptions 
} from '@/utils/echarts'
import type { ECharts } from 'echarts'

// ======== 类型定义 ========
export interface ChartData {
  series: any[]
  xAxis?: any
  yAxis?: any
  legend?: any
  [key: string]: any
}

export interface MonitorChartProps {
  // 基础配置
  type: 'line' | 'bar' | 'pie' | 'gauge' | 'scatter' | 'heatmap'
  data?: ChartData
  title?: string
  subtitle?: string
  height?: string
  
  // 状态控制
  loading?: boolean
  loadingText?: string
  emptyText?: string
  
  // 主题和样式
  theme?: 'light' | 'dark' | 'auto'
  
  // 功能配置
  responsive?: boolean
  large?: boolean
  autoResize?: boolean
  
  // 刷新配置
  refreshInterval?: number
  
  // 自定义配置
  config?: Record<string, any>
}

const props = withDefaults(defineProps<MonitorChartProps>(), {
  type: 'line',
  loading: false,
  loadingText: '加载中...',
  emptyText: '暂无数据',
  theme: 'auto',
  responsive: true,
  large: false,
  autoResize: true,
  refreshInterval: 0,
  config: () => ({})
})

// ======== 组件事件 ========
const emit = defineEmits<{
  chartClick: [params: any]
  chartBrush: [params: any]
  legendClick: [params: any]
  dataZoom: [params: any]
  refresh: []
  error: [error: Error]
}>()

// ======== 响应式数据 ========
const chartRef = ref<HTMLElement>()
const chartInstance = ref<ECharts>()
const hasError = ref(false)
const errorMessage = ref('')
const isDark = useDark()

// 计算属性
const currentTheme = computed(() => {
  if (props.theme === 'auto') {
    return isDark.value ? 'monitoring-dark' : 'monitoring-light'
  }
  return props.theme === 'dark' ? 'monitoring-dark' : 'monitoring-light'
})

const isEmpty = computed(() => {
  if (!props.data || props.loading) return false
  
  if (Array.isArray(props.data.series)) {
    return props.data.series.length === 0 || 
           props.data.series.every((s: any) => !s.data || s.data.length === 0)
  }
  
  return false
})

const chartOptions = computed((): MetricChartOptions => ({
  title: props.title,
  subtitle: props.subtitle,
  type: props.type,
  data: props.data,
  config: {
    responsive: props.responsive,
    large: props.large,
    animation: !props.large,
    dataZoom: props.large || (props.data?.series?.[0]?.data?.length || 0) > 100,
    toolbox: true,
    ...props.config
  }
}))

// ======== 图表方法 ========

/**
 * 初始化图表
 */
const initChart = async () => {
  if (!chartRef.value || props.loading || isEmpty.value) return
  
  try {
    hasError.value = false
    errorMessage.value = ''
    
    // 如果已有实例，先销毁
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }
    
    await nextTick()
    
    // 生成配置
    const option = generateChartOption(chartOptions.value)
    
    // 创建图表实例
    chartInstance.value = createResponsiveChart(
      chartRef.value,
      option,
      currentTheme.value
    )
    
    // 绑定事件
    bindChartEvents()
    
    console.log('📊 图表初始化成功:', props.type)
  } catch (error) {
    console.error('❌ 图表初始化失败:', error)
    hasError.value = true
    errorMessage.value = error instanceof Error ? error.message : '图表初始化失败'
    emit('error', error as Error)
  }
}

/**
 * 更新图表
 */
const updateChart = async () => {
  if (!chartInstance.value || props.loading || isEmpty.value) return
  
  try {
    const option = generateChartOption(chartOptions.value)
    chartInstance.value.setOption(option, true)
    console.log('📈 图表更新成功')
  } catch (error) {
    console.error('❌ 图表更新失败:', error)
    hasError.value = true
    errorMessage.value = error instanceof Error ? error.message : '图表更新失败'
    emit('error', error as Error)
  }
}

/**
 * 绑定图表事件
 */
const bindChartEvents = () => {
  if (!chartInstance.value) return
  
  chartInstance.value.on('click', (params) => {
    emit('chartClick', params)
  })
  
  chartInstance.value.on('brush', (params) => {
    emit('chartBrush', params)
  })
  
  chartInstance.value.on('legendselectchanged', (params) => {
    emit('legendClick', params)
  })
  
  chartInstance.value.on('datazoom', (params) => {
    emit('dataZoom', params)
  })
}

/**
 * 重试加载
 */
const retry = () => {
  hasError.value = false
  errorMessage.value = ''
  initChart()
}

/**
 * 调整图表大小
 */
const resizeChart = () => {
  if (chartInstance.value && !props.loading) {
    chartInstance.value.resize()
  }
}

/**
 * 导出图表
 */
const exportChart = (type: 'png' | 'jpeg' | 'svg' = 'png') => {
  if (!chartInstance.value) {
    ElMessage.warning('图表尚未初始化')
    return
  }
  
  try {
    const url = chartInstance.value.getDataURL({
      type: type,
      pixelRatio: 2,
      backgroundColor: '#fff'
    })
    
    const link = document.createElement('a')
    link.download = `chart_${Date.now()}.${type}`
    link.href = url
    link.click()
    
    ElMessage.success('图表导出成功')
  } catch (error) {
    console.error('导出图表失败:', error)
    ElMessage.error('图表导出失败')
  }
}

/**
 * 显示加载状态
 */
const showLoading = (text = '加载中...') => {
  if (chartInstance.value) {
    chartInstance.value.showLoading({
      text: text,
      color: '#409eff',
      textColor: '#000',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      zlevel: 0,
      // 加载动画
      spinnerRadius: 10,
      lineWidth: 5
    })
  }
}

/**
 * 隐藏加载状态
 */
const hideLoading = () => {
  if (chartInstance.value) {
    chartInstance.value.hideLoading()
  }
}

// ======== 自动刷新 ========
let refreshTimer: NodeJS.Timeout | null = null

const startAutoRefresh = () => {
  if (props.refreshInterval > 0) {
    refreshTimer = setInterval(() => {
      emit('refresh')
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// ======== 生命周期 ========
onMounted(() => {
  initChart()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  if (chartInstance.value) {
    ;(chartInstance.value as any).cleanup?.()
    chartInstance.value.dispose()
  }
})

// ======== 监听器 ========

// 监听数据变化
watch(
  () => props.data,
  (newData, oldData) => {
    if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
      if (chartInstance.value) {
        updateChart()
      } else {
        initChart()
      }
    }
  },
  { deep: true }
)

// 监听主题变化
watch(
  currentTheme,
  () => {
    initChart()
  }
)

// 监听加载状态
watch(
  () => props.loading,
  (loading) => {
    if (loading) {
      showLoading(props.loadingText)
    } else {
      hideLoading()
      if (!chartInstance.value) {
        initChart()
      }
    }
  }
)

// 自动调整大小
if (props.autoResize) {
  useResizeObserver(chartRef, () => {
    resizeChart()
  })
}

// ======== 暴露方法 ========
defineExpose({
  chartInstance,
  initChart,
  updateChart,
  resizeChart,
  exportChart,
  showLoading,
  hideLoading,
  retry
})
</script>

<style scoped lang="scss">
@use '@/styles/mixins.scss' as *;

.monitor-chart {
  position: relative;
  width: 100%;
  min-height: 200px;
  background: var(--el-bg-color);
  border-radius: $border-radius-lg;
  transition: all $transition-base ease;
  
  .chart-container {
    width: 100%;
    height: 100%;
  }
  
  &.chart-loading {
    pointer-events: none;
  }
  
  // 加载状态覆盖层
  .chart-loading-overlay {
    @include absolute-full;
    @include flex-column-center;
    background: rgba(255, 255, 255, 0.9);
    z-index: $z-index-loading;
    
    .chart-loading-icon {
      font-size: 32px;
      color: var(--el-color-primary);
      margin-bottom: $margin-sm;
    }
    
    .chart-loading-text {
      color: var(--el-text-color-secondary);
      font-size: $font-size-sm;
    }
  }
  
  // 错误状态覆盖层
  .chart-error-overlay {
    @include absolute-full;
    @include flex-column-center;
    background: var(--el-bg-color);
    z-index: $z-index-loading;
    gap: $margin-md;
    
    .chart-error-icon {
      font-size: 48px;
      color: var(--el-color-danger);
    }
    
    .chart-error-text {
      color: var(--el-text-color-secondary);
      font-size: $font-size-base;
      text-align: center;
      max-width: 80%;
    }
  }
  
  // 空数据状态覆盖层
  .chart-empty-overlay {
    @include absolute-full;
    @include flex-column-center;
    background: var(--el-bg-color);
    z-index: $z-index-loading;
    gap: $margin-md;
    
    .chart-empty-icon {
      font-size: 48px;
      color: var(--el-text-color-placeholder);
      opacity: 0.6;
    }
    
    .chart-empty-text {
      color: var(--el-text-color-secondary);
      font-size: $font-size-base;
    }
  }
}

// 不同图表类型的特殊样式
.chart-line {
  // 折线图特殊样式
}

.chart-bar {
  // 柱状图特殊样式
}

.chart-pie {
  // 饼图特殊样式
  min-height: 300px;
}

.chart-gauge {
  // 仪表盘特殊样式
  min-height: 250px;
}

// 暗色模式适配
.dark {
  .monitor-chart {
    .chart-loading-overlay {
      background: rgba(20, 20, 20, 0.9);
    }
  }
}

// 响应式设计
@include respond-to(xs) {
  .monitor-chart {
    min-height: 180px;
    
    .chart-error-overlay,
    .chart-empty-overlay {
      .chart-error-icon,
      .chart-empty-icon {
        font-size: 36px;
      }
      
      .chart-error-text,
      .chart-empty-text {
        font-size: $font-size-sm;
      }
    }
  }
}

// 打印样式
@media print {
  .monitor-chart {
    .chart-loading-overlay,
    .chart-error-overlay {
      display: none;
    }
  }
}
</style>