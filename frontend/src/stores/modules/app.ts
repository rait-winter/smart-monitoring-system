import { defineStore } from 'pinia'
import type { RouteLocationNormalized } from 'vue-router'

interface AppState {
  // 应用配置
  appConfig: {
    title: string
    version: string
    description: string
  }
  
  // 布局配置
  layout: {
    collapsed: boolean
    sidebarWidth: number
    headerHeight: number
    footerHeight: number
  }
  
  // 主题配置
  theme: {
    mode: 'light' | 'dark' | 'auto'
    primaryColor: string
    borderRadius: number
    compactMode: boolean
  }
  
  // 面包屑导航
  breadcrumbs: Array<{
    title: string
    path: string
    icon?: string
  }>
  
  // 标签页
  tabs: Array<{
    path: string
    title: string
    icon?: string
    closable: boolean
  }>
  
  // 当前活动标签
  activeTab: string
  
  // 全屏状态
  isFullscreen: boolean
  
  // 加载状态
  globalLoading: boolean
  
  // 网络状态
  networkStatus: 'online' | 'offline'
  
  // 设备信息
  device: {
    isMobile: boolean
    isTablet: boolean
    isDesktop: boolean
  }
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    appConfig: {
      title: '智能监控预警系统',
      version: '2.0.0',
      description: '基于AI的智能监控预警系统'
    },
    
    layout: {
      collapsed: false,
      sidebarWidth: 240,
      headerHeight: 60,
      footerHeight: 40
    },
    
    theme: {
      mode: 'light',
      primaryColor: '#409eff',
      borderRadius: 6,
      compactMode: false
    },
    
    breadcrumbs: [],
    tabs: [
      {
        path: '/',
        title: '首页',
        icon: 'House',
        closable: false
      }
    ],
    activeTab: '/',
    
    isFullscreen: false,
    globalLoading: false,
    networkStatus: 'online',
    
    device: {
      isMobile: false,
      isTablet: false,
      isDesktop: true
    }
  }),

  getters: {
    // 应用标题
    appTitle: (state) => state.appConfig.title,
    
    // 侧边栏状态
    sidebarCollapsed: (state) => state.layout.collapsed,
    
    // 当前主题模式
    currentTheme: (state) => state.theme.mode,
    
    // 是否暗色模式
    isDarkMode: (state) => {
      if (state.theme.mode === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      return state.theme.mode === 'dark'
    },
    
    // 当前标签页
    currentTab: (state) => {
      return state.tabs.find(tab => tab.path === state.activeTab)
    },
    
    // 可关闭的标签页
    closableTabs: (state) => state.tabs.filter(tab => tab.closable),
    
    // 设备类型
    deviceType: (state) => {
      if (state.device.isMobile) return 'mobile'
      if (state.device.isTablet) return 'tablet'
      return 'desktop'
    }
  },

  actions: {
    /**
     * 切换侧边栏
     */
    toggleSidebar() {
      this.layout.collapsed = !this.layout.collapsed
    },

    /**
     * 设置侧边栏状态
     */
    setSidebarCollapsed(collapsed: boolean) {
      this.layout.collapsed = collapsed
    },

    /**
     * 设置主题模式
     */
    setThemeMode(mode: 'light' | 'dark' | 'auto') {
      this.theme.mode = mode
      this.applyTheme()
    },

    /**
     * 切换主题
     */
    toggleTheme() {
      const modes = ['light', 'dark', 'auto'] as const
      const currentIndex = modes.indexOf(this.theme.mode)
      const nextIndex = (currentIndex + 1) % modes.length
      this.setThemeMode(modes[nextIndex])
    },

    /**
     * 应用主题
     */
    applyTheme() {
      const isDark = this.isDarkMode
      const html = document.documentElement
      
      if (isDark) {
        html.classList.add('dark')
        html.setAttribute('data-theme', 'dark')
      } else {
        html.classList.remove('dark')
        html.setAttribute('data-theme', 'light')
      }
    },

    /**
     * 设置主色调
     */
    setPrimaryColor(color: string) {
      this.theme.primaryColor = color
      document.documentElement.style.setProperty('--el-color-primary', color)
    },

    /**
     * 更新面包屑
     */
    updateBreadcrumbs(route: RouteLocationNormalized) {
      const breadcrumbs = []
      const matched = route.matched.filter(item => item.meta?.title)
      
      for (const item of matched) {
        breadcrumbs.push({
          title: item.meta.title as string,
          path: item.path,
          icon: item.meta.icon as string
        })
      }
      
      this.breadcrumbs = breadcrumbs
    },

    /**
     * 添加标签页
     */
    addTab(tab: { path: string; title: string; icon?: string }) {
      const existingTab = this.tabs.find(t => t.path === tab.path)
      
      if (!existingTab) {
        this.tabs.push({
          ...tab,
          closable: tab.path !== '/'
        })
      }
      
      this.activeTab = tab.path
    },

    /**
     * 移除标签页
     */
    removeTab(path: string) {
      const index = this.tabs.findIndex(tab => tab.path === path)
      
      if (index > -1 && this.tabs[index].closable) {
        this.tabs.splice(index, 1)
        
        // 如果移除的是当前标签，切换到其他标签
        if (this.activeTab === path) {
          const newTab = this.tabs[Math.max(0, index - 1)]
          this.activeTab = newTab.path
        }
      }
    },

    /**
     * 设置活动标签
     */
    setActiveTab(path: string) {
      this.activeTab = path
    },

    /**
     * 关闭其他标签
     */
    closeOtherTabs(path: string) {
      this.tabs = this.tabs.filter(tab => !tab.closable || tab.path === path)
      this.activeTab = path
    },

    /**
     * 关闭所有标签
     */
    closeAllTabs() {
      this.tabs = this.tabs.filter(tab => !tab.closable)
      this.activeTab = '/'
    },

    /**
     * 设置全屏状态
     */
    setFullscreen(isFullscreen: boolean) {
      this.isFullscreen = isFullscreen
    },

    /**
     * 切换全屏
     */
    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
        this.isFullscreen = true
      } else {
        document.exitFullscreen()
        this.isFullscreen = false
      }
    },

    /**
     * 设置全局加载状态
     */
    setGlobalLoading(loading: boolean) {
      this.globalLoading = loading
    },

    /**
     * 设置网络状态
     */
    setNetworkStatus(status: 'online' | 'offline') {
      this.networkStatus = status
    },

    /**
     * 更新设备信息
     */
    updateDeviceInfo() {
      const width = window.innerWidth
      
      this.device = {
        isMobile: width < 768,
        isTablet: width >= 768 && width < 1024,
        isDesktop: width >= 1024
      }
      
      // 在移动设备上自动收起侧边栏
      if (this.device.isMobile) {
        this.layout.collapsed = true
      }
    }
  },

  // 持久化配置
  persist: {
    key: 'app-store',
    storage: localStorage,
    paths: ['layout', 'theme', 'tabs', 'activeTab']
  }
})