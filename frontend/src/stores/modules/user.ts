import { defineStore } from 'pinia'
import type { User, LoginCredentials } from '@/types/global'
import { apiService } from '@/services/api'

interface UserState {
  user: User | null
  token: string | null
  isLoggedIn: boolean
  permissions: string[]
  preferences: {
    theme: 'light' | 'dark' | 'auto'
    language: 'zh-CN' | 'en-US'
    dateFormat: string
    timezone: string
  }
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    token: localStorage.getItem('access_token'),
    isLoggedIn: false,
    permissions: [],
    preferences: {
      theme: 'light',
      language: 'zh-CN',
      dateFormat: 'YYYY-MM-DD HH:mm:ss',
      timezone: 'Asia/Shanghai'
    }
  }),

  getters: {
    // 用户信息
    userInfo: (state) => state.user,
    
    // 用户名
    username: (state) => state.user?.username || '',
    
    // 用户角色
    roles: (state) => state.user?.roles || [],
    
    // 是否为管理员
    isAdmin: (state) => state.user?.roles?.includes('admin') || false,
    
    // 检查权限
    hasPermission: (state) => (permission: string) => {
      return state.permissions.includes(permission) || state.permissions.includes('*')
    },
    
    // 检查多个权限
    hasAnyPermission: (state) => (permissions: string[]) => {
      return permissions.some(permission => state.permissions.includes(permission))
    },
    
    // 检查所有权限
    hasAllPermissions: (state) => (permissions: string[]) => {
      return permissions.every(permission => state.permissions.includes(permission))
    }
  },

  actions: {
    /**
     * 登录
     */
    async login(credentials: LoginCredentials) {
      try {
        const response = await apiService.login(credentials)
        
        const { user, token, permissions } = response.data
        
        // 保存用户信息
        this.user = user
        this.token = token
        this.isLoggedIn = true
        this.permissions = permissions || []
        
        // 存储token
        localStorage.setItem('access_token', token)
        
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.message || '登录失败' 
        }
      }
    },

    /**
     * 登出
     */
    async logout() {
      try {
        await apiService.logout()
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        // 清除用户信息
        this.user = null
        this.token = null
        this.isLoggedIn = false
        this.permissions = []
        
        // 清除本地存储
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    },

    /**
     * 获取用户信息
     */
    async fetchUserInfo() {
      if (!this.token) {
        return false
      }

      try {
        const response = await apiService.get('/user/profile')
        
        this.user = response.data.user
        this.permissions = response.data.permissions || []
        this.isLoggedIn = true
        
        return true
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        return false
      }
    },

    /**
     * 更新用户偏好设置
     */
    updatePreferences(preferences: Partial<UserState['preferences']>) {
      this.preferences = { ...this.preferences, ...preferences }
    },

    /**
     * 切换主题
     */
    toggleTheme() {
      const themes = ['light', 'dark', 'auto'] as const
      const currentIndex = themes.indexOf(this.preferences.theme)
      const nextIndex = (currentIndex + 1) % themes.length
      this.preferences.theme = themes[nextIndex]
    },

    /**
     * 设置语言
     */
    setLanguage(language: 'zh-CN' | 'en-US') {
      this.preferences.language = language
    }
  },

  // 持久化配置
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['user', 'preferences', 'token', 'isLoggedIn']
  }
})