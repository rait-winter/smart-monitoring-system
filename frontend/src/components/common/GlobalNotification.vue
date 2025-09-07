<template>
  <div class="global-notification-container">
    <!-- 通知列表 -->
    <transition-group name="notification" tag="div" class="notification-list">
      <div
        v-for="notification in visibleNotifications"
        :key="notification.id"
        class="notification-item"
        :class="[
          `notification-${notification.type}`,
          { 'notification-sticky': notification.sticky },
          { 'notification-closable': notification.closable }
        ]"
        @click="handleNotificationClick(notification)"
      >
        <!-- 图标 -->
        <div class="notification-icon">
          <el-icon>
            <component :is="getNotificationIcon(notification.type)" />
          </el-icon>
        </div>
        
        <!-- 内容 -->
        <div class="notification-content">
          <div v-if="notification.title" class="notification-title">
            {{ notification.title }}
          </div>
          <div class="notification-message">
            {{ notification.message }}
          </div>
          <div v-if="notification.detail" class="notification-detail">
            {{ notification.detail }}
          </div>
          
          <!-- 操作按钮 -->
          <div v-if="notification.actions && notification.actions.length" class="notification-actions">
            <el-button
              v-for="action in notification.actions"
              :key="action.key"
              :type="action.type || 'default'"
              :size="action.size || 'small'"
              @click.stop="handleActionClick(notification, action)"
            >
              {{ action.label }}
            </el-button>
          </div>
        </div>
        
        <!-- 关闭按钮 -->
        <div
          v-if="notification.closable"
          class="notification-close"
          @click.stop="removeNotification(notification.id)"
        >
          <el-icon><Close /></el-icon>
        </div>
        
        <!-- 进度条 -->
        <div
          v-if="notification.showProgress"
          class="notification-progress"
          :style="{ width: getProgressWidth(notification) }"
        />
      </div>
    </transition-group>
    
    <!-- 清空所有按钮 -->
    <transition name="fade">
      <div
        v-if="notifications.length > 1"
        class="clear-all-btn"
        @click="clearAllNotifications"
      >
        <el-icon><Delete /></el-icon>
        <span>清空所有</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled,
  QuestionFilled,
  Close,
  Delete
} from '@element-plus/icons-vue'
import { globalErrorHandler } from '@/utils/errorHandler'

// ======== 类型定义 ========
export interface NotificationAction {
  key: string
  label: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'large' | 'default' | 'small'
  handler?: (notification: NotificationItem) => void
}

export interface NotificationItem {
  id: string
  type: 'success' | 'warning' | 'error' | 'info' | 'question'
  title?: string
  message: string
  detail?: string
  duration?: number // 0 表示不自动关闭
  sticky?: boolean // 是否粘性显示
  closable?: boolean
  showProgress?: boolean
  actions?: NotificationAction[]
  onClick?: (notification: NotificationItem) => void
  onClose?: (notification: NotificationItem) => void
  createdAt: number
  expiresAt?: number
  progress?: number // 0-100
}

// ======== 响应式数据 ========
const notifications = ref<NotificationItem[]>([])
const timers = new Map<string, NodeJS.Timeout>()
const progressTimers = new Map<string, NodeJS.Timeout>()

// ======== 计算属性 ========
const visibleNotifications = computed(() => {
  return notifications.value.filter(n => !n.expiresAt || Date.now() < n.expiresAt)
})

// ======== 方法函数 ========

/**
 * 添加通知
 */
const addNotification = (notification: Omit<NotificationItem, 'id' | 'createdAt'>): string => {
  const id = generateId()
  const now = Date.now()
  
  const item: NotificationItem = {
    id,
    createdAt: now,
    duration: 5000, // 默认5秒
    closable: true,
    showProgress: false,
    ...notification
  }
  
  // 设置过期时间
  if (item.duration && item.duration > 0 && !item.sticky) {
    item.expiresAt = now + item.duration
  }
  
  notifications.value.unshift(item)
  
  // 启动计时器
  if (item.duration && item.duration > 0 && !item.sticky) {
    startTimer(item)
  }
  
  // 启动进度条
  if (item.showProgress && item.duration && item.duration > 0) {
    startProgressTimer(item)
  }
  
  return id
}

/**
 * 移除通知
 */
const removeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index === -1) return
  
  const notification = notifications.value[index]
  
  // 清理计时器
  clearTimer(id)
  clearProgressTimer(id)
  
  // 触发关闭回调
  if (notification.onClose) {
    notification.onClose(notification)
  }
  
  notifications.value.splice(index, 1)
}

/**
 * 清空所有通知
 */
const clearAllNotifications = () => {
  notifications.value.forEach(n => {
    clearTimer(n.id)
    clearProgressTimer(n.id)
    
    if (n.onClose) {
      n.onClose(n)
    }
  })
  
  notifications.value.length = 0
  ElMessage.success('已清空所有通知')
}

/**
 * 启动计时器
 */
const startTimer = (notification: NotificationItem) => {
  if (!notification.duration || notification.sticky) return
  
  const timer = setTimeout(() => {
    removeNotification(notification.id)
  }, notification.duration)
  
  timers.set(notification.id, timer)
}

/**
 * 启动进度条计时器
 */
const startProgressTimer = (notification: NotificationItem) => {
  if (!notification.duration || notification.sticky) return
  
  const startTime = Date.now()
  const duration = notification.duration
  
  const updateProgress = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(100, (elapsed / duration) * 100)
    
    notification.progress = 100 - progress // 倒计时效果
    
    if (progress < 100) {
      const timer = setTimeout(updateProgress, 50) // 20fps
      progressTimers.set(notification.id, timer)
    }
  }
  
  updateProgress()
}

/**
 * 清理计时器
 */
const clearTimer = (id: string) => {
  const timer = timers.get(id)
  if (timer) {
    clearTimeout(timer)
    timers.delete(id)
  }
}

/**
 * 清理进度条计时器
 */
const clearProgressTimer = (id: string) => {
  const timer = progressTimers.get(id)
  if (timer) {
    clearTimeout(timer)
    progressTimers.delete(id)
  }
}

/**
 * 生成唯一ID
 */
const generateId = (): string => {
  return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 获取通知图标
 */
const getNotificationIcon = (type: NotificationItem['type']) => {
  const icons = {
    success: SuccessFilled,
    warning: WarningFilled,
    error: CircleCloseFilled,
    info: InfoFilled,
    question: QuestionFilled
  }
  
  return icons[type] || InfoFilled
}

/**
 * 获取进度条宽度
 */
const getProgressWidth = (notification: NotificationItem): string => {
  return `${notification.progress || 0}%`
}

/**
 * 处理通知点击
 */
const handleNotificationClick = (notification: NotificationItem) => {
  if (notification.onClick) {
    notification.onClick(notification)
  }
}

/**
 * 处理操作按钮点击
 */
const handleActionClick = (notification: NotificationItem, action: NotificationAction) => {
  if (action.handler) {
    action.handler(notification)
  } else {
    console.log('Action clicked:', action.key, notification)
  }
}

// ======== 预定义通知方法 ========

/**
 * 成功通知
 */
const success = (message: string, options?: Partial<NotificationItem>): string => {
  return addNotification({
    type: 'success',
    message,
    ...options
  })
}

/**
 * 警告通知
 */
const warning = (message: string, options?: Partial<NotificationItem>): string => {
  return addNotification({
    type: 'warning',
    message,
    ...options
  })
}

/**
 * 错误通知
 */
const error = (message: string, options?: Partial<NotificationItem>): string => {
  return addNotification({
    type: 'error',
    message,
    duration: 0, // 错误通知默认不自动关闭
    ...options
  })
}

/**
 * 信息通知
 */
const info = (message: string, options?: Partial<NotificationItem>): string => {
  return addNotification({
    type: 'info',
    message,
    ...options
  })
}

/**
 * 询问通知
 */
const question = (message: string, options?: Partial<NotificationItem>): string => {
  return addNotification({
    type: 'question',
    message,
    duration: 0, // 询问通知默认不自动关闭
    actions: [
      {
        key: 'confirm',
        label: '确定',
        type: 'primary'
      },
      {
        key: 'cancel',
        label: '取消'
      }
    ],
    ...options
  })
}

// ======== 生命周期 ========
onMounted(() => {
  // 监听全局错误
  const unsubscribe = globalErrorHandler.addListener((errorInfo) => {
    if (errorInfo.message === 'RETRY_REQUESTED') return
    
    error(errorInfo.message, {
      title: '系统错误',
      detail: errorInfo.detail,
      actions: errorInfo.type === 'NETWORK' ? [
        {
          key: 'retry',
          label: '重试',
          type: 'primary',
          handler: () => {
            // 这里可以触发重试逻辑
            console.log('重试请求')
          }
        }
      ] : undefined
    })
  })
  
  // 组件卸载时清理
  onUnmounted(() => {
    unsubscribe()
    // 清理所有计时器
    timers.forEach(timer => clearTimeout(timer))
    progressTimers.forEach(timer => clearTimeout(timer))
  })
  
  console.log('全局通知组件已初始化')
})

// ======== 暴露方法 ========
defineExpose({
  addNotification,
  removeNotification,
  clearAllNotifications,
  success,
  warning,
  error,
  info,
  question,
  notifications: computed(() => notifications.value)
})
</script>

<style scoped lang="scss">
.global-notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: $z-index-notification;
  width: 400px;
  max-width: 90vw;
  pointer-events: none;
  
  .notification-list {
    .notification-item {
      @include monitor-card;
      @include flex-start;
      margin-bottom: $margin-md;
      padding: $padding-lg;
      background: var(--el-bg-color);
      border-left: 4px solid var(--el-color-info);
      cursor: pointer;
      pointer-events: auto;
      position: relative;
      overflow: hidden;
      max-width: 100%;
      word-wrap: break-word;
      
      // 不同类型的边框颜色
      &.notification-success {
        border-left-color: var(--el-color-success);
        
        .notification-icon {
          color: var(--el-color-success);
        }
      }
      
      &.notification-warning {
        border-left-color: var(--el-color-warning);
        
        .notification-icon {
          color: var(--el-color-warning);
        }
      }
      
      &.notification-error {
        border-left-color: var(--el-color-danger);
        
        .notification-icon {
          color: var(--el-color-danger);
        }
      }
      
      &.notification-info {
        border-left-color: var(--el-color-info);
        
        .notification-icon {
          color: var(--el-color-info);
        }
      }
      
      &.notification-question {
        border-left-color: var(--el-color-primary);
        
        .notification-icon {
          color: var(--el-color-primary);
        }
      }
      
      // 粘性通知样式
      &.notification-sticky {
        @include elevation(3);
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, 
            var(--el-color-primary) 0%, 
            var(--el-color-primary-light-3) 100%
          );
        }
      }
      
      .notification-icon {
        @include flex-center;
        width: 24px;
        height: 24px;
        margin-right: $margin-md;
        flex-shrink: 0;
        
        .el-icon {
          font-size: 20px;
        }
      }
      
      .notification-content {
        flex: 1;
        min-width: 0;
        
        .notification-title {
          font-weight: 600;
          font-size: $font-size-md;
          color: var(--el-text-color-primary);
          margin-bottom: $margin-xs;
          @include text-ellipsis;
        }
        
        .notification-message {
          font-size: $font-size-base;
          color: var(--el-text-color-regular);
          line-height: 1.4;
          margin-bottom: $margin-xs;
        }
        
        .notification-detail {
          font-size: $font-size-sm;
          color: var(--el-text-color-secondary);
          line-height: 1.3;
          margin-bottom: $margin-sm;
          @include text-clamp(2);
        }
        
        .notification-actions {
          @include flex-start;
          gap: $margin-sm;
          margin-top: $margin-md;
          
          .el-button {
            min-width: 60px;
          }
        }
      }
      
      .notification-close {
        @include flex-center;
        width: 20px;
        height: 20px;
        margin-left: $margin-sm;
        cursor: pointer;
        color: var(--el-text-color-placeholder);
        transition: color $transition-fast ease;
        flex-shrink: 0;
        
        &:hover {
          color: var(--el-text-color-regular);
        }
        
        .el-icon {
          font-size: 16px;
        }
      }
      
      // 进度条
      .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 2px;
        background: var(--el-color-primary);
        transition: width 0.1s linear;
      }
      
      // 悬停效果
      &:hover {
        @include elevation(2);
        transform: translateX(-2px);
      }
    }
  }
  
  // 清空按钮
  .clear-all-btn {
    @include flex-center;
    gap: $margin-xs;
    padding: $padding-sm $padding-md;
    background: var(--el-fill-color-dark);
    border-radius: $border-radius-lg;
    cursor: pointer;
    color: var(--el-text-color-secondary);
    font-size: $font-size-sm;
    transition: all $transition-fast ease;
    pointer-events: auto;
    
    &:hover {
      background: var(--el-fill-color-darker);
      color: var(--el-text-color-regular);
    }
    
    .el-icon {
      font-size: 14px;
    }
  }
}

// 动画效果
.notification-enter-active {
  transition: all 0.3s ease;
}

.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// 暗色模式适配
.dark {
  .global-notification-container {
    .notification-item {
      background: var(--el-bg-color-overlay);
      border-left-color: var(--el-border-color);
    }
    
    .clear-all-btn {
      background: var(--el-fill-color-darker);
      
      &:hover {
        background: var(--el-fill-color);
      }
    }
  }
}

// 响应式设计
@include respond-to(xs) {
  .global-notification-container {
    top: 10px;
    right: 10px;
    left: 10px;
    width: auto;
    
    .notification-list {
      .notification-item {
        padding: $padding-md;
        
        .notification-content {
          .notification-title {
            font-size: $font-size-base;
          }
          
          .notification-message {
            font-size: $font-size-sm;
          }
          
          .notification-detail {
            font-size: 12px;
          }
          
          .notification-actions {
            flex-wrap: wrap;
            
            .el-button {
              min-width: 50px;
              font-size: 12px;
            }
          }
        }
      }
    }
  }
}
</style>