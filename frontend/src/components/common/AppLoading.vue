<template>
  <div class="app-loading">
    <div class="loading-container">
      <div class="loading-spinner">
        <el-icon :size="40" class="is-loading">
          <Loading />
        </el-icon>
      </div>
      <div class="loading-text">
        {{ loadingText }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const loadingText = ref('正在加载...')

const loadingTexts = [
  '正在加载...',
  '初始化系统...',
  '连接服务器...',
  '加载组件...',
  '准备就绪...'
]

let textIndex = 0

onMounted(() => {
  const interval = setInterval(() => {
    textIndex = (textIndex + 1) % loadingTexts.length
    loadingText.value = loadingTexts[textIndex]
  }, 800)

  // 清理定时器
  setTimeout(() => {
    clearInterval(interval)
  }, 5000)
})
</script>

<style scoped lang="scss">
.app-loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-container {
  text-align: center;
  color: white;
}

.loading-spinner {
  margin-bottom: 20px;
  
  .el-icon {
    color: white;
    animation: rotate 2s linear infinite;
  }
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}
</style>