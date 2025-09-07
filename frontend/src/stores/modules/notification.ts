import { defineStore } from 'pinia'
import type { NotificationItem } from '@/types/global'

interface NotificationState {
  // 通知列表
  notifications: NotificationItem[]
  
  // 未读数量
  unreadCount: number
  
  // 通知配置
  config: {
    position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
    maxVisible: number
    autoClose: boolean
    closeDelay: number
    showProgress: boolean
    enableSound: boolean
    soundFile: string
  }
  
  // 通知历史
  history: NotificationItem[]
  
  // 过滤器
  filters: {
    type: string[]
    read: boolean | null
    dateRange: [Date, Date] | null
  }
}

export const useNotificationStore = defineStore('notification', {
  state: (): NotificationState => ({
    notifications: [],
    unreadCount: 0,
    
    config: {
      position: 'top-right',
      maxVisible: 5,
      autoClose: true,
      closeDelay: 5000,
      showProgress: true,
      enableSound: false,
      soundFile: '/sounds/notification.mp3'
    },
    
    history: [],
    
    filters: {
      type: [],
      read: null,
      dateRange: null
    }
  }),

  getters: {
    // 可见的通知
    visibleNotifications: (state) => {
      return state.notifications
        .filter(notification => !notification.hidden)
        .slice(0, state.config.maxVisible)
    },
    
    // 按类型分组的通知
    notificationsByType: (state) => {
      const groups: Record<string, NotificationItem[]> = {}
      
      state.notifications.forEach(notification => {
        const type = notification.type || 'info'
        if (!groups[type]) {
          groups[type] = []
        }
        groups[type].push(notification)
      })
      
      return groups
    },
    
    // 过滤后的历史通知
    filteredHistory: (state) => {
      let filtered = state.history
      
      // 类型过滤
      if (state.filters.type.length > 0) {
        filtered = filtered.filter(notification => 
          state.filters.type.includes(notification.type)
        )
      }
      
      // 读取状态过滤
      if (state.filters.read !== null) {
        filtered = filtered.filter(notification => 
          notification.read === state.filters.read
        )
      }
      
      // 时间范围过滤
      if (state.filters.dateRange) {
        const [start, end] = state.filters.dateRange
        filtered = filtered.filter(notification => {
          const date = new Date(notification.timestamp)
          return date >= start && date <= end
        })
      }
      
      return filtered.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
    },
    
    // 通知统计
    notificationStats: (state) => {
      const total = state.history.length
      const unread = state.history.filter(n => !n.read).length
      const byType = state.history.reduce((acc, notification) => {
        const type = notification.type
        acc[type] = (acc[type] || 0) + 1
        return acc
      }, {} as Record<string, number>)
      
      return {
        total,
        unread,
        read: total - unread,
        byType
      }
    }
  },

  actions: {
    /**
     * 添加通知
     */
    addNotification(notification: Omit<NotificationItem, 'id' | 'timestamp'>) {
      const newNotification: NotificationItem = {
        id: this.generateId(),
        timestamp: new Date().toISOString(),
        read: false,
        hidden: false,
        sticky: false,
        closable: true,
        ...notification
      }
      
      // 添加到通知列表
      this.notifications.unshift(newNotification)
      
      // 添加到历史记录
      this.history.unshift({ ...newNotification })
      
      // 更新未读数量
      this.updateUnreadCount()
      
      // 播放声音
      if (this.config.enableSound) {
        this.playNotificationSound()
      }
      
      // 自动关闭
      if (this.config.autoClose && !newNotification.sticky) {
        setTimeout(() => {
          this.removeNotification(newNotification.id)
        }, this.config.closeDelay)
      }
      
      return newNotification.id
    },

    /**
     * 移除通知
     */
    removeNotification(id: string) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    /**
     * 隐藏通知
     */
    hideNotification(id: string) {
      const notification = this.notifications.find(n => n.id === id)
      if (notification) {
        notification.hidden = true
      }
    },

    /**
     * 标记为已读
     */
    markAsRead(id: string) {
      // 更新通知列表
      const notification = this.notifications.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
      
      // 更新历史记录
      const historyItem = this.history.find(n => n.id === id)
      if (historyItem) {
        historyItem.read = true
      }
      
      this.updateUnreadCount()
    },

    /**
     * 标记所有为已读
     */
    markAllAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true
      })
      
      this.history.forEach(notification => {
        notification.read = true
      })
      
      this.unreadCount = 0
    },

    /**
     * 清除所有通知
     */
    clearAll() {
      this.notifications = []
    },

    /**
     * 清除已读通知
     */
    clearRead() {
      this.notifications = this.notifications.filter(n => !n.read)
    },

    /**
     * 更新通知配置
     */
    updateConfig(config: Partial<NotificationState['config']>) {
      this.config = { ...this.config, ...config }
    },

    /**
     * 设置过滤器
     */
    setFilters(filters: Partial<NotificationState['filters']>) {
      this.filters = { ...this.filters, ...filters }
    },

    /**
     * 清除过滤器
     */
    clearFilters() {
      this.filters = {
        type: [],
        read: null,
        dateRange: null
      }
    },

    /**
     * 更新未读数量
     */
    updateUnreadCount() {
      this.unreadCount = this.history.filter(n => !n.read).length
    },

    /**
     * 播放通知声音
     */
    playNotificationSound() {
      try {
        const audio = new Audio(this.config.soundFile)
        audio.volume = 0.5
        audio.play().catch(error => {
          console.warn('无法播放通知声音:', error)
        })
      } catch (error) {
        console.warn('通知声音播放失败:', error)
      }
    },

    /**
     * 生成唯一ID
     */
    generateId(): string {
      return Date.now().toString(36) + Math.random().toString(36).substr(2)
    },

    // 便捷方法
    /**
     * 成功通知
     */
    success(message: string, title?: string, options?: any) {
      return this.addNotification({
        type: 'success',
        title: title || '成功',
        message,
        ...options
      })
    },

    /**
     * 错误通知
     */
    error(message: string, title?: string, options?: any) {
      return this.addNotification({
        type: 'error',
        title: title || '错误',
        message,
        sticky: true,
        ...options
      })
    },

    /**
     * 警告通知
     */
    warning(message: string, title?: string, options?: any) {
      return this.addNotification({
        type: 'warning',
        title: title || '警告',
        message,
        ...options
      })
    },

    /**
     * 信息通知
     */
    info(message: string, title?: string, options?: any) {
      return this.addNotification({
        type: 'info',
        title: title || '信息',
        message,
        ...options
      })
    }
  },

  // 持久化配置
  persist: {
    key: 'notification-store',
    storage: localStorage,
    paths: ['config', 'history']
  }
})