import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      title: '监控仪表盘',
      icon: 'dashboard',
    }
  },
  {
    path: '/anomaly-detection',
    name: 'AnomalyDetection', 
    component: () => import('@/views/AnomalyDetection.vue'),
    meta: {
      title: 'AI异常检测',
      icon: 'brain',
    }
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('@/views/Rules.vue'),
    meta: {
      title: '规则管理',
      icon: 'rule',
    }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/Notifications.vue'),
    meta: {
      title: '通知中心',
      icon: 'notification',
    }
  },
  {
    path: '/metrics',
    name: 'Metrics',
    component: () => import('@/views/Metrics.vue'),
    meta: {
      title: '指标查询',
      icon: 'chart',
    }
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('@/views/System.vue'),
    meta: {
      title: '系统管理',
      icon: 'setting',
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
  NProgress.start()
  
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 智能监控预警系统`
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router