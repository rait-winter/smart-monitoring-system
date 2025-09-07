<template>
  <div id="app" :class="{ 'dark': isDark }">
    <!-- 全局加载进度条 -->
    <Suspense>
      <template #default>
        <MainLayout />
      </template>
      <template #fallback>
        <AppLoading />
      </template>
    </Suspense>
    
    <!-- 全局通知容器 -->
    <Teleport to="body">
      <GlobalNotification />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { provide } from 'vue'
import { useDark } from '@vueuse/core'
import AppLoading from '@/components/common/AppLoading.vue'
import GlobalNotification from '@/components/common/GlobalNotification.vue'
import MainLayout from '@/components/layout/MainLayout.vue'

// 应用名称
const appName = import.meta.env.VITE_APP_TITLE || '智能监控预警系统'

// 暗色模式
const isDark = useDark({
  selector: 'body',
  attribute: 'data-theme',
  valueDark: 'dark',
  valueLight: 'light',
})

// 提供全局状态
provide('appName', appName)
provide('isDark', isDark)

// 页面标题
document.title = appName

// 设置页面描述
const metaDescription = document.querySelector('meta[name="description"]')
if (metaDescription) {
  metaDescription.setAttribute('content', '基于AI的自动化巡检与智能预警系统')
}
</script>

<style lang="scss">
// 全局样式重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100%;
  background-color: var(--el-bg-color-page);
  color: var(--el-text-color-primary);
  transition: all 0.3s;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--el-bg-color-page);
}

::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
  
  &:hover {
    background: var(--el-border-color-hover);
  }
}

// NProgress样式覆盖
#nprogress {
  .bar {
    background: var(--el-color-primary) !important;
  }
  
  .peg {
    box-shadow: 0 0 10px var(--el-color-primary), 0 0 5px var(--el-color-primary) !important;
  }
  
  .spinner-icon {
    border-top-color: var(--el-color-primary) !important;
    border-left-color: var(--el-color-primary) !important;
  }
}

// Element Plus 自定义变量
:root {
  --el-color-primary: #409eff;
  --el-color-success: #67c23a;
  --el-color-warning: #e6a23c;
  --el-color-danger: #f56c6c;
  --el-color-info: #909399;
  
  // 自定义监控主题色
  --monitor-color-normal: #67c23a;
  --monitor-color-warning: #e6a23c;
  --monitor-color-critical: #f56c6c;
  --monitor-color-unknown: #909399;
}

// 暗色模式下的自定义变量
.dark {
  --monitor-bg-primary: #1a1a1a;
  --monitor-bg-secondary: #2d2d2d;
  --monitor-border-color: #404040;
}
</style>