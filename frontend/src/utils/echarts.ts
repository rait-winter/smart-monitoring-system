import * as echarts from 'echarts'
import type { EChartsOption, ECharts } from 'echarts'

// ======== 主题配置 ========

// 默认（亮色）主题
const lightTheme = {
  color: [
    '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
    '#c71585', '#00ced1', '#ffd700', '#ff6347', '#8a2be2'
  ],
  backgroundColor: 'transparent',
  textStyle: {
    color: '#303133',
    fontFamily: 'Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif'
  },
  title: {
    textStyle: {
      color: '#303133',
      fontWeight: '500'
    }
  },
  legend: {
    textStyle: {
      color: '#606266'
    }
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: '#dcdfe6'
      }
    },
    axisLabel: {
      color: '#606266'
    },
    splitLine: {
      lineStyle: {
        color: '#ebeef5'
      }
    }
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: '#dcdfe6'
      }
    },
    axisLabel: {
      color: '#606266'
    },
    splitLine: {
      lineStyle: {
        color: '#ebeef5'
      }
    }
  },
  grid: {
    borderColor: '#ebeef5'
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#dcdfe6',
    textStyle: {
      color: '#303133'
    }
  }
}

// 暗色主题
const darkTheme = {
  color: [
    '#79bbff', '#95d475', '#ebb563', '#f78989', '#a6a9ad',
    '#e785c5', '#5ccdd1', '#ffef60', '#ff8a65', '#b39ddb'
  ],
  backgroundColor: 'transparent',
  textStyle: {
    color: '#e5eaf3',
    fontFamily: 'Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif'
  },
  title: {
    textStyle: {
      color: '#e5eaf3',
      fontWeight: '500'
    }
  },
  legend: {
    textStyle: {
      color: '#cfd3dc'
    }
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: '#414243'
      }
    },
    axisLabel: {
      color: '#a3a6ad'
    },
    splitLine: {
      lineStyle: {
        color: '#2b2c2d'
      }
    }
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: '#414243'
      }
    },
    axisLabel: {
      color: '#a3a6ad'
    },
    splitLine: {
      lineStyle: {
        color: '#2b2c2d'
      }
    }
  },
  grid: {
    borderColor: '#2b2c2d'
  },
  tooltip: {
    backgroundColor: 'rgba(20, 20, 20, 0.95)',
    borderColor: '#414243',
    textStyle: {
      color: '#e5eaf3'
    }
  }
}

// ======== 图表类型接口 ========
export interface ChartConfig {
  theme?: 'light' | 'dark' | 'monitoring-light' | 'monitoring-dark'
  responsive?: boolean
  animation?: boolean
  large?: boolean
  dataZoom?: boolean
  toolbox?: boolean
}

export interface ChartData {
  xAxis?: any[]
  series: any[]
  [key: string]: any
}

export interface MetricChartOptions {
  title?: string
  subtitle?: string
  type: 'line' | 'bar' | 'pie' | 'gauge' | 'scatter' | 'heatmap' | 'graph'
  data: ChartData
  config?: ChartConfig
}

// ======== 工具函数 ========

/**
 * 格式化数值
 */
export function formatValue(value: number, unit?: string, precision = 2): string {
  if (value === null || value === undefined) return '-'
  
  let formattedValue = value
  let suffix = unit || ''
  
  // 自动单位转换
  if (value >= 1000000000) {
    formattedValue = value / 1000000000
    suffix = 'G' + (unit || '')
  } else if (value >= 1000000) {
    formattedValue = value / 1000000
    suffix = 'M' + (unit || '')
  } else if (value >= 1000) {
    formattedValue = value / 1000
    suffix = 'K' + (unit || '')
  }
  
  return formattedValue.toFixed(precision) + suffix
}

/**
 * 格式化时间轴
 */
export function formatTimeAxis(timestamp: number | string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 获取响应式配置
 */
export function getResponsiveConfig(): any {
  return {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    // 移动端适配
    media: [
      {
        query: {
          maxWidth: 768
        },
        option: {
          grid: {
            left: '2%',
            right: '2%',
            bottom: '5%'
          },
          legend: {
            bottom: 0,
            orient: 'horizontal'
          },
          xAxis: {
            axisLabel: {
              interval: 'auto',
              rotate: 45
            }
          }
        }
      }
    ]
  }
}

/**
 * 获取大数据配置
 */
export function getLargeDataConfig(): any {
  return {
    animation: false,
    progressive: 1000,
    progressiveThreshold: 3000,
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 30
      }
    ]
  }
}

/**
 * 创建基础配置
 */
export function createBaseOption(options: MetricChartOptions): EChartsOption {
  const { title, subtitle, type, data, config = {} } = options
  
  const baseOption: EChartsOption = {
    title: {
      text: title || '',
      subtext: subtitle || '',
      left: 'left',
      textStyle: {
        fontSize: 16,
        fontWeight: 500 as any
      },
      subtextStyle: {
        fontSize: 12,
        color: '#909399'
      }
    },
    tooltip: {
      trigger: type === 'pie' ? 'item' : 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#dcdfe6',
      borderWidth: 1,
      textStyle: {
        color: '#303133'
      },
      formatter: function(params: any) {
        if (Array.isArray(params)) {
          let result = params[0].axisValueLabel + '<br/>'
          params.forEach((param: any) => {
            result += `${param.marker} ${param.seriesName}: ${formatValue(param.value)}<br/>`
          })
          return result
        } else {
          return `${params.marker} ${params.seriesName}: ${formatValue(params.value)}`
        }
      }
    },
    legend: {
      top: 'bottom',
      icon: 'circle'
    },
    animationDuration: config.animation !== false ? 1000 : 0,
    animationEasing: 'cubicOut'
  }
  
  // 添加响应式配置
  if (config.responsive !== false) {
    Object.assign(baseOption, getResponsiveConfig())
  }
  
  // 添加大数据配置
  if (config.large) {
    Object.assign(baseOption, getLargeDataConfig())
  }
  
  // 添加工具箱
  if (config.toolbox) {
    baseOption.toolbox = {
      feature: {
        saveAsImage: { title: '保存为图片' },
        dataZoom: { title: { zoom: '区域缩放', back: '还原缩放' } },
        dataView: { title: '数据视图', readOnly: false },
        magicType: {
          title: {
            line: '切换为折线图',
            bar: '切换为柱状图'
          },
          type: ['line', 'bar']
        },
        restore: { title: '还原' }
      },
      right: 20,
      top: 20
    }
  }
  
  return baseOption
}

// ======== 图表生成器 ========

/**
 * 创建折线图配置
 */
export function createLineChart(options: MetricChartOptions): EChartsOption {
  const baseOption = createBaseOption(options)
  const { data } = options
  
  return {
    ...baseOption,
    xAxis: {
      type: 'category',
      data: data.xAxis || [],
      axisLabel: {
        formatter: (value: any) => {
          // 如果是时间戳，格式化为时间
          if (typeof value === 'number' && value > 1000000000) {
            return formatTimeAxis(value)
          }
          return value
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => formatValue(value)
      }
    },
    series: data.series.map((series: any) => ({
      ...series,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2
      },
      areaStyle: series.area ? {
        opacity: 0.3
      } : undefined
    }))
  }
}

/**
 * 创建柱状图配置
 */
export function createBarChart(options: MetricChartOptions): EChartsOption {
  const baseOption = createBaseOption(options)
  const { data } = options
  
  return {
    ...baseOption,
    xAxis: {
      type: 'category',
      data: data.xAxis || []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => formatValue(value)
      }
    },
    series: data.series.map((series: any) => ({
      ...series,
      type: 'bar',
      barWidth: '60%',
      itemStyle: {
        borderRadius: [4, 4, 0, 0]
      }
    }))
  }
}

/**
 * 创建饼图配置
 */
export function createPieChart(options: MetricChartOptions): EChartsOption {
  const baseOption = createBaseOption(options)
  const { data } = options
  
  return {
    ...baseOption,
    series: data.series.map((series: any) => ({
      ...series,
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      }
    }))
  }
}

/**
 * 创建仪表盘配置
 */
export function createGaugeChart(options: MetricChartOptions): EChartsOption {
  const baseOption = createBaseOption(options)
  const { data } = options
  
  return {
    ...baseOption,
    series: data.series.map((series: any) => ({
      ...series,
      type: 'gauge',
      radius: '80%',
      center: ['50%', '60%'],
      startAngle: 180,
      endAngle: 0,
      min: series.min || 0,
      max: series.max || 100,
      splitNumber: 10,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [0.3, '#67c23a'],
            [0.7, '#e6a23c'],
            [1, '#f56c6c']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 20,
        offsetCenter: [0, '-60%'],
        itemStyle: {
          color: 'auto'
        }
      },
      axisTick: {
        length: 12,
        lineStyle: {
          color: 'auto',
          width: 2
        }
      },
      splitLine: {
        length: 20,
        lineStyle: {
          color: 'auto',
          width: 5
        }
      },
      axisLabel: {
        color: '#464646',
        fontSize: 12,
        distance: -60,
        formatter: function (value: number) {
          return value + (series.unit || '')
        }
      },
      title: {
        offsetCenter: [0, '-20%'],
        fontSize: 16
      },
      detail: {
        fontSize: 24,
        offsetCenter: [0, '0%'],
        valueAnimation: true,
        formatter: function (value: number) {
          return Math.round(value) + (series.unit || '')
        },
        color: 'auto'
      }
    }))
  }
}

/**
 * 图表配置生成器
 */
export function generateChartOption(options: MetricChartOptions): EChartsOption {
  switch (options.type) {
    case 'line':
      return createLineChart(options)
    case 'bar':
      return createBarChart(options)
    case 'pie':
      return createPieChart(options)
    case 'gauge':
      return createGaugeChart(options)
    default:
      return createLineChart(options)
  }
}

/**
 * 配置ECharts
 */
export function setupECharts(app: any) {
  // 注册主题
  echarts.registerTheme('monitoring-light', lightTheme)
  echarts.registerTheme('monitoring-dark', darkTheme)
  
  // 全局配置
  app.config.globalProperties.$echarts = echarts
  app.config.globalProperties.$generateChartOption = generateChartOption
  app.config.globalProperties.$formatValue = formatValue
  
  console.log('%c✓ ECharts配置完成', 'color: #67c23a; font-size: 12px;', '支持主题: monitoring-light, monitoring-dark')
}

/**
 * 创建响应式图表实例
 */
export function createResponsiveChart(
  container: HTMLElement,
  option: EChartsOption,
  theme = 'monitoring-light'
): ECharts {
  const chart = echarts.init(container, theme)
  
  // 设置配置
  chart.setOption(option)
  
  // 响应式处理 - 添加防抖
  let resizeTimer: NodeJS.Timeout | null = null
  const resizeHandler = () => {
    if (resizeTimer) {
      clearTimeout(resizeTimer)
    }
    
    resizeTimer = setTimeout(() => {
      try {
        chart.resize()
      } catch (error) {
        console.warn('ECharts resize失败:', error)
      }
    }, 100) // 100ms防抖
  }
  
  window.addEventListener('resize', resizeHandler)
  
  // 监听主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const themeHandler = (e: MediaQueryListEvent) => {
    const newTheme = e.matches ? 'monitoring-dark' : 'monitoring-light'
    chart.dispose()
    const newChart = echarts.init(container, newTheme)
    newChart.setOption(option)
  }
  
  mediaQuery.addEventListener('change', themeHandler)
  
  // 返回实例和清理函数
  const cleanup = () => {
    if (resizeTimer) {
      clearTimeout(resizeTimer)
    }
    window.removeEventListener('resize', resizeHandler)
    mediaQuery.removeEventListener('change', themeHandler)
    chart.dispose()
  }
  
  ;(chart as any).cleanup = cleanup
  
  return chart
}

export default {
  setupECharts,
  generateChartOption,
  createResponsiveChart,
  formatValue,
  formatTimeAxis
}