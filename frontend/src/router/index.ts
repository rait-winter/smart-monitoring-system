import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'

// 懒加载组件函数
const lazyLoad = (view: string) => {
  return () => import(`@/views/${view}.vue`)
}

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: lazyLoad('Dashboard'),
    meta: {
      title: '监控仪表盘',
      icon: 'dashboard',
      keepAlive: true
    }
  },
  {
    path: '/anomaly-detection',
    name: 'AnomalyDetection', 
    component: lazyLoad('AnomalyDetection'),
    meta: {
      title: 'AI异常检测',
      icon: 'brain',
      keepAlive: true
    }
  },
  {
    path: '/rules',
    name: 'Rules',
    component: lazyLoad('Rules'),
    meta: {
      title: '规则管理',
      icon: 'rule',
      keepAlive: true
    }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: lazyLoad('Notifications'),
    meta: {
      title: '通知中心',
      icon: 'notification',
      keepAlive: true
    }
  },
  {
    path: '/metrics',
    name: 'Metrics',
    component: lazyLoad('Metrics'),
    meta: {
      title: '指标查询',
      icon: 'chart',
      keepAlive: true
    }
  },
  {
    path: '/system',
    name: 'System',
    component: lazyLoad('System'),
    meta: {
      title: '系统管理',
      icon: 'setting',
      keepAlive: false // 系统管理页面每次重新加载
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 显示加载进度
  NProgress.start()
  
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 智能监控预警系统`
  }
  
  // 添加加载提示
  console.log(`%c→ 导航至: ${to.meta?.title || to.path}`, 'color: #409eff; font-size: 12px;')
  
  next()
})

router.afterEach((to, from) => {
  // 隐藏加载进度
  NProgress.done()
  
  // 记录页面访问
  console.log(`%c✓ 页面加载完成: ${to.meta?.title || to.path}`, 'color: #67c23a; font-size: 12px;')
})

// 路由错误处理
router.onError((error) => {
  NProgress.done()
  console.error('路由加载错误:', error)
})

export default router