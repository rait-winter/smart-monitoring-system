import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// Element Plus样式
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

// WindiCSS - 暂时禁用
// import 'virtual:windi.css'

// 进度条
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 自定义样式
import '@/styles/index.scss'

// 应用组件
import App from './App.vue'
import router from './router'

// 状态管理
import { setupStore } from '@/stores'

// 全局组件和指令
import { registerGlobalComponents } from '@/components'

// ECharts配置
import { setupECharts } from '@/utils/echarts'

// 错误处理
import { setupErrorHandler } from '@/utils/errorHandler'

// NProgress配置
NProgress.configure({ 
  showSpinner: false,
  minimum: 0.1,
  speed: 500,
})

async function bootstrap() {
  // 创建应用实例
  const app = createApp(App)
  
  // 设置状态管理
  setupStore(app)
  
  // 注册路由
  app.use(router)
  
  // 注册全局组件
  registerGlobalComponents(app)
  
  // 配置ECharts
  setupECharts(app)
  
  // 设置错误处理
  setupErrorHandler(app)
  
  // 挂载应用
  app.mount('#app')
  
  console.log(
    `%c🚀 智能监控预警系统 v${import.meta.env.VITE_APP_VERSION || '2.0.0'}`,
    'color: #42b883; font-size: 16px; font-weight: bold;'
  )
  
  console.log(
    '%c🔧 技术栈: Vue 3 + TypeScript + Vite + Element Plus + ECharts',
    'color: #35495e; font-size: 12px;'
  )
}

bootstrap().catch(console.error)