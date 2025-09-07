<template>
  <div 
    class="mobile-chart"
    :class="[
      `mobile-chart--${type}`,
      { 'mobile-chart--loading': loading },
      { 'mobile-chart--fullscreen': isFullscreen }
    ]"
  >
    <!-- 图表头部 -->
    <div v-if="showHeader" class="mobile-chart__header">
      <div class="mobile-chart__title">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="mobile-chart__subtitle">{{ subtitle }}</p>
      </div>
      
      <div class="mobile-chart__actions">
        <!-- 刷新按钮 -->
        <el-button
          v-if="showRefresh"
          class="mobile-chart__action-btn"
          :icon="Refresh"
          :loading="refreshing"
          text
          @click="handleRefresh"
        />
        
        <!-- 全屏按钮 -->
        <el-button
          v-if="showFullscreen"
          class="mobile-chart__action-btn"
          :icon="isFullscreen ? Close : FullScreen"
          text
          @click="toggleFullscreen"
        />
        
        <!-- 更多选项 -->
        <el-dropdown v-if="showMenu" @command="handleMenuCommand">
          <el-button class="mobile-chart__action-btn" :icon="More" text />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="export">导出数据</el-dropdown-item>
              <el-dropdown-item command="share">分享</el-dropdown-item>
              <el-dropdown-item command="config">设置</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 图表内容 -->
    <div class="mobile-chart__content">
      <!-- 加载状态 -->
      <div v-if="loading" class="mobile-chart__loading">
        <el-skeleton :rows="5" animated />
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="mobile-chart__error">
        <el-empty :image-size="80" description="图表加载失败">
          <el-button type="primary" @click="handleRefresh">重试</el-button>
        </el-empty>
      </div>
      
      <!-- 图表容器 -->
      <div
        v-else
        ref="chartContainer"
        class="mobile-chart__chart"
        :style="{ height: chartHeight }"
      />
    </div>
    
    <!-- 移动端数据展示 -->
    <div v-if="showMobileData && isMobile" class="mobile-chart__data">
      <div class="mobile-data-grid">
        <div
          v-for="(item, index) in mobileDataItems"
          :key="index"
          class="mobile-data-item"
        >
          <div class="mobile-data-item__label">{{ item.label }}</div>
          <div class="mobile-data-item__value" :style="{ color: item.color }">
            {{ item.value }}
          </div>
          <div v-if="item.change" class="mobile-data-item__change">
            <el-icon 
              :class="[
                'mobile-data-item__change-icon',
                item.change > 0 ? 'is-up' : item.change < 0 ? 'is-down' : ''
              ]"
            >
              <component :is="item.change > 0 ? ArrowUp : ArrowDown" />
            </el-icon>
            <span 
              :class="[
                'mobile-data-item__change-text',
                item.change > 0 ? 'is-up' : item.change < 0 ? 'is-down' : ''
              ]"
            >
              {{ Math.abs(item.change) }}%
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图表说明 -->
    <div v-if="showDescription && description" class="mobile-chart__description">
      <el-collapse v-model="descriptionVisible">
        <el-collapse-item name="description" title="图表说明">
          <p>{{ description }}</p>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch, readonly } from 'vue'
import type { ECharts, EChartsOption } from 'echarts'
import { createResponsiveChart, formatValue } from '@/utils/echarts'
import { getResponsiveConfig, isMobileDevice } from '@/utils/responsive'
import { 
  Refresh, 
  FullScreen, 
  Close, 
  More, 
  ArrowUp, 
  ArrowDown 
} from '@element-plus/icons-vue'

// Props
interface Props {
  type: 'line' | 'bar' | 'pie' | 'gauge' | 'scatter'
  title?: string
  subtitle?: string
  description?: string
  data: any[]
  option?: EChartsOption
  loading?: boolean
  error?: string
  height?: string | number
  showHeader?: boolean
  showRefresh?: boolean
  showFullscreen?: boolean
  showMenu?: boolean
  showMobileData?: boolean
  showDescription?: boolean
  autoResize?: boolean
  theme?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '300px',
  showHeader: true,
  showRefresh: true,
  showFullscreen: true,
  showMenu: true,
  showMobileData: true,
  showDescription: true,
  autoResize: true,
  theme: 'monitoring-light'
})

// Emits
interface Emits {
  (e: 'refresh'): void
  (e: 'export'): void
  (e: 'share'): void
  (e: 'config'): void
  (e: 'fullscreen', isFullscreen: boolean): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const chartContainer = ref<HTMLElement>()
const chart = ref<ECharts>()
const isFullscreen = ref(false)
const refreshing = ref(false)
const descriptionVisible = ref<string[]>([])

// 计算属性
const isMobile = computed(() => getResponsiveConfig().isMobile)

const chartHeight = computed(() => {
  if (isFullscreen.value) {
    return 'calc(100vh - 120px)'
  }
  
  if (isMobile.value) {
    return typeof props.height === 'number' 
      ? `${Math.min(props.height, 250)}px`
      : '250px'
  }
  
  return typeof props.height === 'number' 
    ? `${props.height}px` 
    : props.height
})

// 移动端数据项
const mobileDataItems = computed(() => {
  if (!props.data || !Array.isArray(props.data)) return []
  
  return props.data.slice(0, 4).map(item => ({
    label: item.name || item.label || '数据',
    value: formatValue(item.value || item.y || 0),
    color: item.color || '#409eff',
    change: item.change || 0
  }))
})

// 方法
const initChart = async () => {
  await nextTick()
  
  if (!chartContainer.value || props.loading || props.error) return
  
  try {
    // 创建图表实例
    chart.value = createResponsiveChart(
      chartContainer.value,
      getMobileOptimizedOption(),
      props.theme
    )
    
    // 移动端触摸优化
    if (isMobile.value) {
      optimizeForMobile()
    }
    
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

const getMobileOptimizedOption = (): EChartsOption => {
  const baseOption = props.option || getDefaultOption()
  
  if (!isMobile.value) return baseOption
  
  // 移动端优化配置
  return {
    ...baseOption,
    animation: false, // 移动端禁用动画提升性能
    grid: {
      ...baseOption.grid,
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%',
      containLabel: true
    },
    legend: {
      ...baseOption.legend,
      type: 'scroll',
      orient: 'horizontal',
      bottom: 0,
      itemWidth: 12,
      itemHeight: 8,
      textStyle: {
        fontSize: 10
      }
    },
    tooltip: {
      ...baseOption.tooltip,
      trigger: 'axis',
      confine: true, // 限制在容器内
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: 'transparent',
      textStyle: {
        fontSize: 12,
        color: '#fff'
      }
    },
    xAxis: Array.isArray(baseOption.xAxis) ? baseOption.xAxis.map(axis => ({
      ...axis,
      axisLabel: {
        ...axis.axisLabel,
        fontSize: 10,
        interval: 'auto',
        rotate: 0
      }
    })) : {
      ...baseOption.xAxis,
      axisLabel: {
        ...baseOption.xAxis?.axisLabel,
        fontSize: 10,
        interval: 'auto',
        rotate: 0
      }
    },
    yAxis: Array.isArray(baseOption.yAxis) ? baseOption.yAxis.map(axis => ({
      ...axis,
      axisLabel: {
        ...axis.axisLabel,
        fontSize: 10
      }
    })) : {
      ...baseOption.yAxis,
      axisLabel: {
        ...baseOption.yAxis?.axisLabel,
        fontSize: 10
      }
    }
  }
}

const getDefaultOption = (): EChartsOption => {
  // 根据图表类型返回默认配置
  switch (props.type) {
    case 'line':
      return {
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: props.data }]
      }
    case 'bar':
      return {
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: props.data }]
      }
    case 'pie':
      return {
        series: [{ type: 'pie', data: props.data, radius: '70%' }]
      }
    default:
      return {}
  }
}

const optimizeForMobile = () => {
  if (!chart.value) return
  
  // 禁用部分交互功能以提升性能
  chart.value.getZr().off('click')
  chart.value.getZr().off('dblclick')
  
  // 优化触摸体验
  const chartDom = chart.value.getDom()
  if (chartDom) {
    chartDom.style.touchAction = 'pan-y'
  }
}

const handleRefresh = async () => {
  refreshing.value = true
  try {
    emit('refresh')
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟加载
  } finally {
    refreshing.value = false
  }
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  emit('fullscreen', isFullscreen.value)
  
  // 延迟调整图表大小
  nextTick(() => {
    if (chart.value) {
      chart.value.resize()
    }
  })
}

const handleMenuCommand = (command: string) => {
  switch (command) {
    case 'export':
      emit('export')
      break
    case 'share':
      emit('share')
      break
    case 'config':
      emit('config')
      break
  }
}

const resizeChart = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

// 监听器
watch(() => props.option, () => {
  if (chart.value) {
    chart.value.setOption(getMobileOptimizedOption(), true)
  }
}, { deep: true })

watch(() => props.data, () => {
  if (chart.value) {
    chart.value.setOption(getMobileOptimizedOption(), true)
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  initChart()
  
  if (props.autoResize) {
    window.addEventListener('resize', resizeChart)
    window.addEventListener('orientationchange', resizeChart)
  }
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.dispose()
  }
  
  if (props.autoResize) {
    window.removeEventListener('resize', resizeChart)
    window.removeEventListener('orientationchange', resizeChart)
  }
})

// 暴露方法
defineExpose({
  chart: readonly(chart),
  refresh: handleRefresh,
  resize: resizeChart,
  toggleFullscreen
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
@use '@/styles/mixins' as *;
@use '@/styles/responsive' as responsive;

.mobile-chart {
  background: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  
  &--loading {
    .mobile-chart__content {
      min-height: 200px;
    }
  }
  
  &--fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 2000;
    border-radius: 0;
    border: none;
  }
}

// 图表头部
.mobile-chart__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  @include responsive.media-down(sm) {
    padding: 12px;
  }
}

.mobile-chart__title {
  flex: 1;
  
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    line-height: 1.4;
    
    @include responsive.media-down(sm) {
      font-size: 15px;
    }
  }
}

.mobile-chart__subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: var(--el-text-color-regular);
  line-height: 1.4;
}

.mobile-chart__actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mobile-chart__action-btn {
  @include mobile-touch-optimization;
  
  .el-icon {
    font-size: 16px;
  }
}

// 图表内容
.mobile-chart__content {
  position: relative;
  padding: 16px;
  
  @include responsive.media-down(sm) {
    padding: 8px;
  }
}

.mobile-chart__loading {
  padding: 20px;
}

.mobile-chart__error {
  padding: 20px;
  text-align: center;
}

.mobile-chart__chart {
  width: 100%;
  transition: height 0.3s ease;
}

// 移动端数据展示
.mobile-chart__data {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  
  @include responsive.media-down(sm) {
    padding: 12px;
  }
}

.mobile-data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  
  @include responsive.media-down(sm) {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

.mobile-data-item {
  padding: 12px;
  background: var(--el-fill-color-extra-light);
  border-radius: var(--el-border-radius-small);
  text-align: center;
  
  &__label {
    font-size: 12px;
    color: var(--el-text-color-regular);
    margin-bottom: 4px;
  }
  
  &__value {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 4px;
    
    @include responsive.media-down(sm) {
      font-size: 16px;
    }
  }
  
  &__change {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    font-size: 11px;
  }
  
  &__change-icon {
    font-size: 12px;
    
    &.is-up {
      color: var(--el-color-success);
    }
    
    &.is-down {
      color: var(--el-color-danger);
    }
  }
  
  &__change-text {
    &.is-up {
      color: var(--el-color-success);
    }
    
    &.is-down {
      color: var(--el-color-danger);
    }
  }
}

// 图表说明
.mobile-chart__description {
  border-top: 1px solid var(--el-border-color-lighter);
  
  .el-collapse {
    border: none;
    
    :deep(.el-collapse-item__header) {
      padding: 12px 16px;
      font-size: 13px;
      background: var(--el-fill-color-extra-light);
    }
    
    :deep(.el-collapse-item__content) {
      padding: 12px 16px;
      font-size: 12px;
      color: var(--el-text-color-regular);
      line-height: 1.5;
    }
  }
}

// 响应式适配
@include media-down(sm) {
  .mobile-chart__header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    
    .mobile-chart__actions {
      align-self: flex-end;
    }
  }
}
</style>