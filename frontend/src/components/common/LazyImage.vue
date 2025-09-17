<template>
  <div 
    class="lazy-image-container" 
    :style="{ width: width, height: height }"
    ref="containerRef"
  >
    <img
      v-if="loaded"
      :src="src"
      :alt="alt"
      :class="['lazy-image', { 'loaded': loaded }]"
      @load="handleLoad"
      @error="handleError"
    />
    <div 
      v-else 
      class="lazy-image-placeholder"
      :class="{ 'loading': isLoading }"
    >
      <el-icon v-if="isLoading" class="loading-icon">
        <Loading />
      </el-icon>
      <span v-else>{{ placeholderText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, readonly } from 'vue'
import { Loading } from '@element-plus/icons-vue'

export interface LazyImageProps {
  src: string
  alt?: string
  width?: string
  height?: string
  placeholder?: string
  threshold?: number
  rootMargin?: string
  fallbackSrc?: string
}

const props = withDefaults(defineProps<LazyImageProps>(), {
  alt: '',
  width: '100%',
  height: '200px',
  placeholder: '加载中...',
  threshold: 0.1,
  rootMargin: '50px',
  fallbackSrc: ''
})

const containerRef = ref<HTMLElement>()
const loaded = ref(false)
const isLoading = ref(false)
const error = ref(false)
const observer = ref<IntersectionObserver | null>(null)

const placeholderText = computed(() => {
  if (error.value) return '加载失败'
  if (isLoading.value) return '加载中...'
  return props.placeholder
})

// 处理图片加载
const handleLoad = () => {
  loaded.value = true
  isLoading.value = false
  error.value = false
}

// 处理图片错误
const handleError = () => {
  if (props.fallbackSrc && !error.value) {
    error.value = true
    // 尝试加载备用图片
    const img = new Image()
    img.onload = () => {
      // 更新src为备用图片
      const imgElement = containerRef.value?.querySelector('img')
      if (imgElement) {
        imgElement.src = props.fallbackSrc!
      }
      loaded.value = true
      isLoading.value = false
      error.value = false
    }
    img.onerror = () => {
      error.value = true
      isLoading.value = false
    }
    img.src = props.fallbackSrc
  } else {
    error.value = true
    isLoading.value = false
  }
}

// 开始加载图片
const startLoading = () => {
  if (loaded.value || isLoading.value) return
  
  isLoading.value = true
  error.value = false
  
  // 创建图片元素进行预加载
  const img = new Image()
  img.onload = () => {
    loaded.value = true
    isLoading.value = false
  }
  img.onerror = handleError
  img.src = props.src
}

// 设置交叉观察器
const setupObserver = () => {
  if (!containerRef.value) return
  
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          startLoading()
          // 加载后停止观察
          observer.value?.unobserve(entry.target)
        }
      })
    },
    {
      threshold: props.threshold,
      rootMargin: props.rootMargin
    }
  )
  
  observer.value.observe(containerRef.value)
}

// 清理观察器
const cleanupObserver = () => {
  if (observer.value) {
    observer.value.disconnect()
    observer.value = null
  }
}

// 监听src变化
watch(() => props.src, () => {
  loaded.value = false
  error.value = false
  isLoading.value = false
  
  if (observer.value && containerRef.value) {
    observer.value.observe(containerRef.value)
  }
})

onMounted(() => {
  setupObserver()
})

onUnmounted(() => {
  cleanupObserver()
})

// 暴露方法
defineExpose({
  startLoading,
  loaded: readonly(loaded),
  error: readonly(error)
})
</script>

<style scoped lang="scss">
.lazy-image-container {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
  
  .lazy-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: opacity 0.3s ease;
    opacity: 0;
    
    &.loaded {
      opacity: 1;
    }
  }
  
  .lazy-image-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--el-fill-color-light);
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    
    &.loading {
      background: var(--el-fill-color);
      
      .loading-icon {
        animation: spin 1s linear infinite;
        font-size: 20px;
        color: var(--el-color-primary);
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 暗色模式适配
.dark {
  .lazy-image-placeholder {
    background: var(--monitor-bg-secondary);
    color: var(--monitor-text-secondary);
  }
}
</style>