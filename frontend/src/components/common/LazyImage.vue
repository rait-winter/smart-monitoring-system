<template>
  <div 
    class="lazy-image"
    ref="containerRef"
    :style="containerStyle"
    :class="[
      `lazy-image--${status}`,
      { 'lazy-image--has-overlay': overlay }
    ]"
  >
    <!-- 占位符 -->
    <div v-if="showPlaceholder" class="lazy-image__placeholder">
      <slot name="placeholder">
        <div class="default-placeholder">
          <el-icon class="placeholder-icon">
            <Picture />
          </el-icon>
          <span v-if="placeholderText" class="placeholder-text">
            {{ placeholderText }}
          </span>
        </div>
      </slot>
    </div>

    <!-- 渐进式加载画布 -->
    <div v-if="progressive && progressiveImageData" class="lazy-image__progressive">
      <img :src="progressiveImageData" class="progressive-canvas" alt="" />
    </div>

    <!-- 实际图片 -->
    <img
      v-if="shouldShowImage"
      ref="imageRef"
      :src="currentSrc"
      :alt="alt"
      :class="imageClass"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
      @click="handlePreview"
    />

    <!-- 加载状态 -->
    <div v-if="showLoading" class="lazy-image__loading">
      <slot name="loading">
        <div class="default-loading">
          <el-icon class="loading-icon is-loading">
            <Loading />
          </el-icon>
          <span class="loading-text">{{ loadingText }}</span>
        </div>
      </slot>
    </div>

    <!-- 错误状态 -->
    <div v-if="showError" class="lazy-image__error">
      <slot name="error">
        <div class="default-error">
          <el-icon class="error-icon">
            <Warning />
          </el-icon>
          <span class="error-text">{{ errorText }}</span>
          <el-button 
            v-if="retryable && retryCount < maxRetries"
            size="small" 
            type="primary" 
            @click="retry"
          >
            重试
          </el-button>
        </div>
      </slot>
    </div>

    <!-- 遮罩层 -->
    <div v-if="overlay" class="lazy-image__overlay" :style="overlayStyle">
      <slot name="overlay" />
    </div>

    <!-- 渐进式加载用的隐藏画布 -->
    <canvas
      v-if="progressive"
      ref="canvasRef"
      :width="progressiveWidth"
      :height="progressiveHeight"
      style="display: none;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import { Picture, Loading, Warning } from '@element-plus/icons-vue'

// 类型定义
export interface LazyImageProps {
  src: string
  alt?: string
  placeholder?: string
  fallback?: string
  width?: string | number
  height?: string | number
  fit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
  lazy?: boolean
  threshold?: number
  retryable?: boolean
  maxRetries?: number
  retryDelay?: number
  progressive?: boolean
  blur?: boolean
  preview?: boolean
  placeholderText?: string
  loadingText?: string
  errorText?: string
  overlay?: boolean
  overlayColor?: string
  overlayOpacity?: number
  transition?: string
  radius?: string
  border?: string
  shadow?: boolean
}

const props = withDefaults(defineProps<LazyImageProps>(), {
  alt: '',
  width: '100%',
  height: 'auto',
  fit: 'cover',
  lazy: true,
  threshold: 0.1,
  retryable: true,
  maxRetries: 3,
  retryDelay: 1000,
  progressive: false,
  blur: false,
  preview: false,
  placeholderText: '',
  loadingText: '加载中...',
  errorText: '加载失败',
  overlay: false,
  overlayColor: 'rgba(0, 0, 0, 0.5)',
  overlayOpacity: 0.5,
  transition: 'fade',
  radius: '0',
  border: 'none',
  shadow: false
})

// 组件事件
const emit = defineEmits<{
  load: [event: Event]
  error: [event: Event]
  retry: [attempt: number]
  intersect: [isIntersecting: boolean]
  preview: [src: string]
}>()

// 响应式数据
const containerRef = ref<HTMLElement>()
const imageRef = ref<HTMLImageElement>()
const canvasRef = ref<HTMLCanvasElement>()

const status = ref<'placeholder' | 'loading' | 'loaded' | 'error'>('placeholder')
const retryCount = ref(0)
const currentSrc = ref('')
const isVisible = ref(false)

// 渐进式加载相关
const progressiveWidth = ref(50)
const progressiveHeight = ref(50)
const progressiveImageData = ref<string | null>(null)

// 计算属性
const isLoading = computed(() => status.value === 'loading')
const isLoaded = computed(() => status.value === 'loaded')
const hasError = computed(() => status.value === 'error')

const showPlaceholder = computed(() => {
  return status.value === 'placeholder' || (props.progressive && isLoading.value)
})

const showLoading = computed(() => {
  return isLoading.value && !props.progressive
})

const showError = computed(() => {
  return hasError.value
})

const shouldShowImage = computed(() => {
  return isLoaded.value || (isLoading.value && currentSrc.value)
})

const containerStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  borderRadius: props.radius,
  border: props.border,
  boxShadow: props.shadow ? '0 2px 8px rgba(0, 0, 0, 0.15)' : 'none'
}))

const imageClass = computed(() => [
  'lazy-image__img',
  `fit-${props.fit}`,
  {
    'blur-load': props.blur && isLoading.value,
    'preview-enabled': props.preview
  }
])

const imageStyle = computed(() => ({
  objectFit: props.fit,
  width: '100%',
  height: '100%',
  borderRadius: props.radius,
  transition: `opacity 0.3s ease, filter 0.3s ease`
}))

const overlayStyle = computed(() => ({
  backgroundColor: props.overlayColor,
  opacity: props.overlayOpacity
}))

// 方法函数
const startLoad = async () => {
  if (status.value === 'loading' || status.value === 'loaded') return
  
  status.value = 'loading'
  
  try {
    // 渐进式加载
    if (props.progressive) {
      await loadProgressiveImage()
    }
    
    // 加载实际图片
    currentSrc.value = props.src
  } catch (error) {
    console.error('图片加载失败:', error)
    handleImageError()
  }
}

const loadProgressiveImage = async () => {
  try {
    const canvas = canvasRef.value
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    return new Promise<void>((resolve, reject) => {
      img.onload = () => {
        ctx.filter = 'blur(2px)'
        ctx.drawImage(img, 0, 0, progressiveWidth.value, progressiveHeight.value)
        
        progressiveImageData.value = canvas.toDataURL()
        resolve()
      }
      
      img.onerror = reject
      
      img.src = props.placeholder || generateThumbnailUrl(props.src)
    })
  } catch (error) {
    console.warn('渐进式加载失败:', error)
  }
}

const generateThumbnailUrl = (url: string): string => {
  return url.replace(/\.(jpg|jpeg|png|webp)$/i, '_thumb.$1')
}

const handleLoad = (event: Event) => {
  status.value = 'loaded'
  retryCount.value = 0
  emit('load', event)
}

const handleError = (event: Event) => {
  handleImageError()
  emit('error', event)
}

const handleImageError = () => {
  if (retryCount.value < props.maxRetries && props.retryable) {
    setTimeout(() => {
      retry()
    }, props.retryDelay)
  } else {
    if (props.fallback && currentSrc.value !== props.fallback) {
      currentSrc.value = props.fallback
      retryCount.value = 0
    } else {
      status.value = 'error'
    }
  }
}

const retry = () => {
  if (retryCount.value >= props.maxRetries) {
    ElMessage.warning('重试次数已达上限')
    return
  }
  
  retryCount.value++
  status.value = 'loading'
  currentSrc.value = props.src
  
  emit('retry', retryCount.value)
}

const handlePreview = () => {
  if (props.preview && isLoaded.value) {
    emit('preview', props.src)
  }
}

const reset = () => {
  status.value = 'placeholder'
  retryCount.value = 0
  currentSrc.value = ''
  progressiveImageData.value = null
}

// 生命周期
onMounted(() => {
  if (props.progressive && containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    progressiveWidth.value = Math.max(50, Math.floor(rect.width / 10))
    progressiveHeight.value = Math.max(50, Math.floor(rect.height / 10))
  }
  
  if (!props.lazy) {
    startLoad()
  }
})

// 交叉观察器
if (props.lazy) {
  const { stop } = useIntersectionObserver(
    containerRef,
    ([{ isIntersecting }]) => {
      isVisible.value = isIntersecting
      emit('intersect', isIntersecting)
      
      if (isIntersecting && status.value === 'placeholder') {
        startLoad()
        stop()
      }
    },
    {
      threshold: props.threshold,
      rootMargin: '50px'
    }
  )
}

// 监听器
watch(
  () => props.src,
  (newSrc, oldSrc) => {
    if (newSrc !== oldSrc) {
      reset()
      if (!props.lazy || isVisible.value) {
        nextTick(() => {
          startLoad()
        })
      }
    }
  }
)

// 暴露方法
defineExpose({
  retry,
  reset,
  startLoad,
  status: computed(() => status.value),
  isLoaded,
  hasError
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
@use '@/styles/mixins' as *;

.lazy-image {
  position: relative;
  display: inline-block;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
  
  &__placeholder {
    @include absolute-full;
    @include flex-center;
    background: var(--el-fill-color-light);
    
    .default-placeholder {
      @include flex-column-center;
      gap: $margin-sm;
      color: var(--el-text-color-placeholder);
      
      .placeholder-icon {
        font-size: 32px;
        opacity: 0.6;
      }
      
      .placeholder-text {
        font-size: $font-size-sm;
      }
    }
  }
  
  &__loading {
    @include absolute-full;
    @include flex-center;
    background: rgba(255, 255, 255, 0.9);
    z-index: 2;
    
    .default-loading {
      @include flex-column-center;
      gap: $margin-sm;
      color: var(--el-color-primary);
      
      .loading-icon {
        font-size: 24px;
      }
      
      .loading-text {
        font-size: $font-size-sm;
      }
    }
  }
  
  &__error {
    @include absolute-full;
    @include flex-center;
    background: var(--el-fill-color-light);
    
    .default-error {
      @include flex-column-center;
      gap: $margin-sm;
      color: var(--el-color-danger);
      
      .error-icon {
        font-size: 32px;
      }
      
      .error-text {
        font-size: $font-size-sm;
        color: var(--el-text-color-secondary);
      }
    }
  }
  
  &__img {
    display: block;
    max-width: 100%;
    
    &.blur-load {
      filter: blur(2px);
    }
    
    &.preview-enabled {
      cursor: pointer;
      transition: transform 0.3s ease;
      
      &:hover {
        transform: scale(1.05);
      }
    }
    
    &.fit-fill {
      object-fit: fill;
    }
    
    &.fit-contain {
      object-fit: contain;
    }
    
    &.fit-cover {
      object-fit: cover;
    }
    
    &.fit-none {
      object-fit: none;
    }
    
    &.fit-scale-down {
      object-fit: scale-down;
    }
  }
  
  &__overlay {
    @include absolute-full;
    @include flex-center;
    z-index: 3;
    pointer-events: none;
  }
  
  &__progressive {
    @include absolute-full;
    z-index: 1;
    
    .progressive-canvas {
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: blur(1px);
    }
  }
  
  &--loading {
    .lazy-image__img {
      opacity: 0.7;
    }
  }
  
  &--error {
    .lazy-image__img {
      display: none;
    }
  }
  
  &--loaded {
    .lazy-image__img {
      opacity: 1;
    }
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.dark {
  .lazy-image {
    background: var(--el-fill-color-dark);
    
    &__placeholder {
      background: var(--el-fill-color-darker);
    }
    
    &__loading {
      background: rgba(20, 20, 20, 0.9);
    }
    
    &__error {
      background: var(--el-fill-color-darker);
    }
  }
}

@include respond-to(xs) {
  .lazy-image {
    &__placeholder,
    &__loading,
    &__error {
      .default-placeholder,
      .default-loading,
      .default-error {
        .placeholder-icon,
        .loading-icon,
        .error-icon {
          font-size: 24px;
        }
        
        .placeholder-text,
        .loading-text,
        .error-text {
          font-size: 12px;
        }
      }
    }
  }
}
</style>