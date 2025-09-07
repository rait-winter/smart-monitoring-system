import type { App } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// 导入store模块
import { useUserStore } from './modules/user'
import { useAppStore } from './modules/app'
import { useMetricsStore } from './modules/metrics'
import { useNotificationStore } from './modules/notification'

// 创建pinia实例
export const pinia = createPinia()

// 使用持久化插件
pinia.use(piniaPluginPersistedstate)

/**
 * 注册状态管理
 */
export function setupStore(app: App) {
  app.use(pinia)
}

/**
 * 导出所有store
 */
export {
  useUserStore,
  useAppStore,
  useMetricsStore,
  useNotificationStore
}

/**
 * 全局重置所有store
 */
export function resetAllStores() {
  const userStore = useUserStore()
  const appStore = useAppStore()
  const metricsStore = useMetricsStore()
  const notificationStore = useNotificationStore()

  userStore.$reset()
  appStore.$reset()
  metricsStore.$reset()
  notificationStore.$reset()
}