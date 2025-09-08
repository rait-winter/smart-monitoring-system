import { type App } from 'vue'

// 导入组件
import MainLayout from './layout/MainLayout.vue'
import ResponsiveLayout from './layout/ResponsiveLayout.vue'
import AppLoading from './common/AppLoading.vue'
import GlobalNotification from './common/GlobalNotification.vue'
import MonitorChart from './common/MonitorChart.vue'
import MobileChart from './common/MobileChart.vue'
import ChartGrid from './common/ChartGrid.vue'
import VirtualList from './common/VirtualList.vue'
import LazyImage from './common/LazyImage.vue'
import InfiniteScroll from './common/InfiniteScroll.vue'
import MobileTable from './common/MobileTable.vue'

// 组件列表
const components = {
  MainLayout,
  ResponsiveLayout,
  AppLoading,
  GlobalNotification,
  MonitorChart,
  MobileChart,
  ChartGrid,
  VirtualList,
  LazyImage,
  InfiniteScroll,
  MobileTable
}

/**
 * 注册全局组件
 */
export function registerGlobalComponents(app: App) {
  // 注册所有组件为全局组件
  Object.entries(components).forEach(([name, component]) => {
    app.component(name, component)
  })
  
  console.log('%c✓ 全局组件注册完成', 'color: #67c23a; font-size: 12px;', Object.keys(components))
}

// 导出单个组件
export {
  MainLayout,
  ResponsiveLayout,
  AppLoading,
  GlobalNotification,
  MonitorChart,
  MobileChart,
  ChartGrid,
  VirtualList,
  LazyImage,
  InfiniteScroll,
  MobileTable
}

// 默认导出
export default {
  install: registerGlobalComponents
}