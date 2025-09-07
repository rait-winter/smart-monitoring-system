<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-left">
        <h1 class="app-title">
          <el-icon class="title-icon">
            <Monitor />
          </el-icon>
          智能监控预警系统
        </h1>
      </div>
      
      <div class="header-right">
        <!-- 主题切换 -->
        <el-button 
          :icon="isDark ? Sunny : Moon" 
          circle 
          @click="toggleDark"
          class="theme-toggle"
        />
        
        <!-- 通知中心 -->
        <el-badge :value="notificationCount" class="notification-badge">
          <el-button 
            :icon="Bell" 
            circle 
            @click="showNotifications"
          />
        </el-badge>
        
        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <el-button circle>
            <el-icon><User /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="content-container">
      <!-- 侧边栏导航 -->
      <el-aside 
        :width="isCollapsed ? '64px' : '200px'" 
        class="sidebar"
      >
        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon>
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        
        <!-- 导航菜单 -->
        <el-menu
          :default-active="$route.path"
          :collapse="isCollapsed"
          :unique-opened="true"
          router
          class="nav-menu"
        >
          <el-menu-item 
            v-for="route in menuRoutes" 
            :key="route.path"
            :index="route.path"
          >
            <el-icon>
              <component :is="getRouteIcon(route.meta?.icon)" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <!-- 面包屑导航 -->
        <el-breadcrumb class="breadcrumb" separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item 
            v-if="$route.meta?.title && $route.path !== '/'"
          >
            {{ $route.meta.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>
        
        <!-- 页面内容 -->
        <div class="page-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Moon,
  Sunny,
  Bell,
  User,
  Fold,
  Expand,
  House,
  TrendCharts,
  Setting,
  ChatDotRound,
  DataAnalysis,
  Tools
} from '@element-plus/icons-vue'

// 响应式数据
const router = useRouter()
const route = useRoute()
const isDark = useDark()
const toggleDark = useToggle(isDark)

// 侧边栏折叠状态
const isCollapsed = ref(false)
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

// 通知数量
const notificationCount = ref(3)

// 菜单路由配置
const menuRoutes = computed(() => {
  return router.getRoutes().filter(route => 
    route.meta?.title && !route.meta?.hidden
  )
})

// 获取路由图标组件
const getRouteIcon = (iconName?: string) => {
  const iconMap: Record<string, any> = {
    dashboard: House,
    brain: TrendCharts,
    rule: Setting,
    notification: ChatDotRound,
    chart: DataAnalysis,
    setting: Tools
  }
  return iconMap[iconName || 'House'] || House
}

// 显示通知
const showNotifications = () => {
  router.push('/notifications')
}

// 用户菜单处理
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人设置功能开发中...')
      break
    case 'logout':
      ElMessage.success('已退出登录')
      // 这里可以添加登录逻辑
      break
  }
}

// 注入全局应用名称
const appName = inject('appName', '智能监控预警系统')
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  @include flex-between;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  padding: 0 20px;
  
  .header-left {
    .app-title {
      @include flex-center;
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: $primary-color;
      gap: 8px;
      
      .title-icon {
        font-size: 24px;
      }
    }
  }
  
  .header-right {
    @include flex-center;
    gap: 12px;
    
    .theme-toggle {
      color: var(--el-text-color-primary);
    }
    
    .notification-badge {
      .el-button {
        color: var(--el-text-color-primary);
      }
    }
  }
}

.content-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  transition: width 0.3s ease;
  position: relative;
  
  .collapse-btn {
    @include flex-center;
    height: 48px;
    cursor: pointer;
    border-bottom: 1px solid var(--el-border-color-lighter);
    transition: background-color 0.2s;
    
    &:hover {
      background: var(--el-fill-color-light);
    }
    
    .el-icon {
      font-size: 16px;
      color: var(--el-text-color-regular);
    }
  }
  
  .nav-menu {
    border: none;
    height: calc(100% - 48px);
    
    .el-menu-item {
      margin: 4px 8px;
      border-radius: 6px;
      
      &:hover {
        background: var(--el-color-primary-light-9);
      }
      
      &.is-active {
        background: var(--el-color-primary-light-8);
        color: $primary-color;
        
        .el-icon {
          color: $primary-color;
        }
      }
    }
  }
}

.main-content {
  background: var(--el-bg-color-page);
  padding: 0;
  
  .breadcrumb {
    padding: 16px 20px;
    background: var(--el-bg-color);
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  
  .page-content {
    height: calc(100% - 52px);
    overflow-y: auto;
    padding: 0;
  }
}

// 暗色模式适配
:deep(.dark) {
  .header {
    background: var(--el-bg-color);
    border-bottom-color: var(--el-border-color);
  }
  
  .sidebar {
    background: var(--el-bg-color);
    border-right-color: var(--el-border-color);
  }
}
</style>