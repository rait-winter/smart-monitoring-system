<template>
  <div 
    class="responsive-layout"
    :class="[
      `responsive-layout--${deviceType}`,
      `responsive-layout--${orientation}`,
      { 'responsive-layout--mobile': isMobile }
    ]"
  >
    <!-- 移动端顶部导航 -->
    <div v-if="isMobile" class="mobile-header">
      <div class="mobile-header__content">
        <el-button
          class="mobile-header__menu-btn"
          :icon="Expand"
          text
          @click="toggleSidebar"
        />
        
        <div class="mobile-header__title">
          {{ currentPageTitle }}
        </div>
        
        <div class="mobile-header__actions">
          <el-button
            class="mobile-header__action-btn"
            :icon="Bell"
            text
            @click="showNotifications"
          >
            <el-badge v-if="unreadCount > 0" :value="unreadCount" />
          </el-button>
          
          <el-dropdown @command="handleUserAction">
            <el-button class="mobile-header__user-btn" text>
              <el-avatar :size="28" :src="userAvatar" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="responsive-layout__body">
      <!-- 侧边栏 -->
      <div 
        v-if="showSidebar"
        class="responsive-layout__sidebar"
        :class="{ 'responsive-layout__sidebar--mobile': isMobile }"
      >
        <div 
          v-if="isMobile" 
          class="mobile-sidebar-overlay"
          @click="closeSidebar"
        />
        
        <div class="sidebar-content">
          <slot name="sidebar" :is-mobile="isMobile" :device-type="deviceType" />
        </div>
      </div>
      
      <!-- 主内容 -->
      <div 
        class="responsive-layout__main"
        :class="{ 'responsive-layout__main--with-sidebar': showSidebar }"
      >
        <!-- 桌面端面包屑 -->
        <div v-if="!isMobile && showBreadcrumb" class="desktop-breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="item.path"
            >
              <el-icon v-if="item.icon">
                <component :is="item.icon" />
              </el-icon>
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <!-- 主要内容 -->
        <div class="responsive-layout__content">
          <slot :is-mobile="isMobile" :device-type="deviceType" :responsive-config="responsiveConfig" />
        </div>
      </div>
    </div>
    
    <!-- 移动端底部导航 -->
    <div v-if="isMobile && showBottomNav" class="mobile-bottom-nav">
      <div 
        v-for="item in bottomNavItems"
        :key="item.path"
        class="mobile-bottom-nav__item"
        :class="{ 'mobile-bottom-nav__item--active': item.path === currentPath }"
        @click="navigateTo(item.path)"
      >
        <el-icon class="mobile-bottom-nav__icon">
          <component :is="item.icon" />
        </el-icon>
        <span class="mobile-bottom-nav__label">{{ item.label }}</span>
        <el-badge v-if="item.badge" :value="item.badge" />
      </div>
    </div>
    
    <!-- 移动端通知抽屉 -->
    <el-drawer
      v-model="notificationDrawerVisible"
      title="通知消息"
      direction="rtl"
      size="100%"
      :modal="true"
      :show-close="true"
    >
      <div class="notification-drawer">
        <slot name="notifications" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, readonly } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/modules/app'
import { useNotificationStore } from '@/stores/modules/notification'
import { 
  getResponsiveConfig, 
  watchDeviceType, 
  watchOrientation,
  type DeviceType,
  type ScreenOrientation,
  type ResponsiveConfig
} from '@/utils/responsive'
import { Expand, Bell } from '@element-plus/icons-vue'

// Props
interface Props {
  showSidebar?: boolean
  showBreadcrumb?: boolean
  showBottomNav?: boolean
  bottomNavItems?: Array<{
    path: string
    label: string
    icon: string
    badge?: number
  }>
}

const props = withDefaults(defineProps<Props>(), {
  showSidebar: true,
  showBreadcrumb: true,
  showBottomNav: true,
  bottomNavItems: () => [
    { path: '/', label: '首页', icon: 'House' },
    { path: '/metrics', label: '指标', icon: 'DataAnalysis' },
    { path: '/rules', label: '规则', icon: 'Setting' },
    { path: '/notifications', label: '通知', icon: 'Bell' }
  ]
})

// Emits
interface Emits {
  (e: 'sidebar-toggle', visible: boolean): void
  (e: 'device-change', deviceType: DeviceType): void
  (e: 'orientation-change', orientation: ScreenOrientation): void
}

const emit = defineEmits<Emits>()

// Store
const appStore = useAppStore()
const notificationStore = useNotificationStore()

// Router
const route = useRoute()
const router = useRouter()

// 响应式状态
const responsiveConfig = ref<ResponsiveConfig>(getResponsiveConfig())
const notificationDrawerVisible = ref(false)

// 计算属性
const deviceType = computed(() => responsiveConfig.value.deviceType)
const orientation = computed(() => responsiveConfig.value.orientation)
const isMobile = computed(() => responsiveConfig.value.isMobile)

const currentPath = computed(() => route.path)
const currentPageTitle = computed(() => {
  return route.meta?.title as string || '智能监控系统'
})

const breadcrumbs = computed(() => appStore.breadcrumbs)
const unreadCount = computed(() => notificationStore.unreadCount)
const userAvatar = computed(() => 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')

// 侧边栏控制
const sidebarVisible = ref(props.showSidebar && !isMobile.value)
const showSidebar = computed(() => sidebarVisible.value)

// 方法
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
  emit('sidebar-toggle', sidebarVisible.value)
}

const closeSidebar = () => {
  if (isMobile.value) {
    sidebarVisible.value = false
    emit('sidebar-toggle', false)
  }
}

const showNotifications = () => {
  notificationDrawerVisible.value = true
}

const navigateTo = (path: string) => {
  router.push(path)
}

const handleUserAction = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      // 处理登出逻辑
      break
  }
}

// 更新响应式配置
const updateResponsiveConfig = () => {
  responsiveConfig.value = getResponsiveConfig()
}

// 设备类型变化处理
const handleDeviceChange = (newDeviceType: DeviceType) => {
  emit('device-change', newDeviceType)
  
  // 移动端自动隐藏侧边栏
  if (newDeviceType === 'mobile') {
    sidebarVisible.value = false
  } else {
    sidebarVisible.value = props.showSidebar
  }
}

// 屏幕方向变化处理
const handleOrientationChange = (newOrientation: ScreenOrientation) => {
  emit('orientation-change', newOrientation)
}

// 生命周期
let deviceTypeCleanup: (() => void) | null = null
let orientationCleanup: (() => void) | null = null

onMounted(() => {
  // 初始化响应式配置
  updateResponsiveConfig()
  
  // 监听设备类型变化
  deviceTypeCleanup = watchDeviceType(handleDeviceChange)
  
  // 监听屏幕方向变化
  orientationCleanup = watchOrientation(handleOrientationChange)
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateResponsiveConfig)
  
  // 初始化侧边栏状态
  sidebarVisible.value = props.showSidebar && !isMobile.value
})

onUnmounted(() => {
  // 清理监听器
  if (deviceTypeCleanup) deviceTypeCleanup()
  if (orientationCleanup) orientationCleanup()
  window.removeEventListener('resize', updateResponsiveConfig)
})

// 暴露方法
defineExpose({
  toggleSidebar,
  closeSidebar,
  responsiveConfig: readonly(responsiveConfig)
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
@use '@/styles/mixins' as *;
@use '@/styles/responsive' as responsive;

.responsive-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  
  // 移动端适配
  &--mobile {
    @include safe-area-padding(all);
  }
  
  // 横屏适配
  &--landscape {
    .mobile-header {
      height: 50px;
    }
  }
}

// 移动端顶部导航
.mobile-header {
  height: 60px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  padding: 0 16px;
  position: relative;
  z-index: 1000;
  
  &__content {
    display: flex;
    align-items: center;
    width: 100%;
  }
  
  &__menu-btn {
    margin-right: 12px;
    
    .el-icon {
      font-size: 20px;
    }
  }
  
  &__title {
    flex: 1;
    font-size: 16px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    text-align: center;
    margin: 0 12px;
  }
  
  &__actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  &__action-btn {
    position: relative;
    
    .el-badge {
      position: absolute;
      top: -4px;
      right: -4px;
    }
  }
  
  &__user-btn {
    padding: 4px;
  }
}

// 主体布局
.responsive-layout__body {
  display: flex;
  flex: 1;
  min-height: 0;
}

// 侧边栏
.responsive-layout__sidebar {
  width: 240px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  transition: transform 0.3s ease;
  
  // 移动端侧边栏
  &--mobile {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    width: 280px;
    z-index: 999;
    transform: translateX(-100%);
    animation: slideInLeft 0.3s ease forwards;
    
    @include safe-area-padding(left);
  }
}

.mobile-sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  
  @include mobile-list-optimization;
}

// 主内容区
.responsive-layout__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  
  // 有侧边栏时的样式
  &--with-sidebar {
    @include responsive.media-down(md) {
      margin-left: 0;
    }
  }
}

// 桌面端面包屑
.desktop-breadcrumb {
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  .el-breadcrumb {
    font-size: 14px;
  }
}

// 主要内容
.responsive-layout__content {
  flex: 1;
  overflow: auto;
  padding: 16px;
  
  @include mobile-list-optimization;
  
  // 移动端内边距调整
  @include media-down(sm) {
    padding: 12px;
  }
}

// 移动端底部导航
.mobile-bottom-nav {
  height: 60px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0 8px;
  position: relative;
  z-index: 1000;
  
  @include safe-area-padding(bottom);
  
  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 6px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    
    @include mobile-touch-optimization;
    
    &:active {
      transform: scale(0.95);
      background: var(--el-fill-color-light);
    }
    
    &--active {
      color: var(--el-color-primary);
      
      .mobile-bottom-nav__icon {
        color: var(--el-color-primary);
      }
      
      .mobile-bottom-nav__label {
        color: var(--el-color-primary);
        font-weight: 500;
      }
    }
  }
  
  &__icon {
    font-size: 20px;
    margin-bottom: 2px;
    color: var(--el-text-color-regular);
    transition: color 0.2s ease;
  }
  
  &__label {
    font-size: 12px;
    color: var(--el-text-color-regular);
    transition: color 0.2s ease;
  }
  
  .el-badge {
    position: absolute;
    top: 2px;
    right: 8px;
  }
}

// 通知抽屉
.notification-drawer {
  height: 100%;
  padding: 16px;
}

// 动画
@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

// 响应式适配
@include media-down(md) {
  .responsive-layout__sidebar:not(.responsive-layout__sidebar--mobile) {
    width: 200px;
  }
}

@include media-down(sm) {
  .mobile-header {
    height: 56px;
    padding: 0 12px;
    
    &__title {
      font-size: 15px;
      margin: 0 8px;
    }
  }
  
  .mobile-bottom-nav {
    height: 56px;
    padding: 0 4px;
    
    &__item {
      padding: 4px 8px;
    }
    
    &__icon {
      font-size: 18px;
    }
    
    &__label {
      font-size: 11px;
    }
  }
  
  .responsive-layout__content {
    padding: 8px;
  }
}
</style>