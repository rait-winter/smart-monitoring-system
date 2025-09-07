import type { App } from 'vue'
import * as echarts from 'echarts'

/**
 * 配置ECharts
 */
export function setupECharts(app: App) {
  // 全局ECharts配置
  echarts.registerTheme('smart-monitoring', {
    color: [
      '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
      '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
    ],
    backgroundColor: 'transparent'
  })
  
  app.config.globalProperties.$echarts = echarts
  console.log('ECharts配置完成')
}