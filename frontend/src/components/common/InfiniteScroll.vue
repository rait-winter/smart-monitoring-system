<template>
  <div 
    ref="containerRef"
    class="infinite-scroll"
    :class="{ 'scroll-disabled': disabled }"
    @scroll="handleScroll"
  >
    <!-- 主要内容区域 -->
    <div class="content-container">
      <!-- 自定义内容插槽 -->
      <slot :items="displayItems" :loading="isLoading" :error="error" />
      
      <!-- 默认内容渲染 -->
      <div v-if="!$slots.default" class="default-content">
        <div 
          v-for="(item, index) in displayItems" 
          :key="index"
          class="default-item"
        >
          {{ item }}
        </div>
      </div>
    </div>

    <!-- 加载更多指示器 -->
    <div 
      v-if="showLoadMore"
      ref="loadMoreRef" 
      class="load-more-indicator"
      :class="{ 'is-loading': isLoading }"
    >
      <slot name="loading" :loading="isLoading">
        <div class="default-loading">
          <el-icon v-if="isLoading" class="is-loading">
            <Loading />
          </el-icon>
          <span>{{ isLoading ? loadingText : loadMoreText }}</span>
        </div>
      </slot>
    </div>

    <!-- 加载完成指示器 -->
    <div v-if="showFinished" class="finished-indicator">
      <slot name="finished">
        <div class="default-finished">
          <el-icon class="finished-icon">
            <Check />
          </el-icon>
          <span>{{ finishedText }}</span>
        </div>
      </slot>
    </div>

    <!-- 错误指示器 -->
    <div v-if="showError" class="error-indicator">
      <slot name="error" :error="error" :retry="retry">
        <div class="default-error">
          <el-icon class="error-icon">
            <Warning />
          </el-icon>
          <div class="error-text">{{ errorText }}</div>
          <el-button @click="retry" size="small" type="primary">
            重试
          </el-button>
        </div>
      </slot>
    </div>

    <!-- 空数据指示器 -->
    <div v-if="showEmpty" class="empty-indicator">
      <slot name="empty">
        <el-empty :description="emptyText" />
      </slot>
    </div>

    <!-- 回到顶部按钮 -->
    <transition name="fade">
      <div 
        v-if="showBackTopButton"
        class="back-to-top"
        @click="scrollToTop"
      >
        <el-icon>
          <ArrowUp />
        </el-icon>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useThrottleFn, useIntersectionObserver } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import { Loading, Check, Warning, ArrowUp } from '@element-plus/icons-vue'

// ======== 类型定义 ========
export interface InfiniteScrollProps {
  // 数据源
  items?: any[]
  // 加载函数
  loadMore?: () => Promise<any[]> | any[]
  // 是否禁用
  disabled?: boolean
  // 触发距离
  distance?: number
  // 是否立即加载
  immediate?: boolean
  // 延迟加载时间
  delay?: number
  // 是否使用交叉观察器
  useObserver?: boolean
  //  分页大小
  pageSize?: number
  // 当前页码
  currentPage?: number
  // 总页数
  totalPages?: number
  // 是否有更多数据
  hasMore?: boolean
  // 加载状态
  loading?: boolean
  // 是否加载完成
  finished?: boolean
  // 错误对象
  error?: Error | null
  // 文本配置
  loadingText?: string
  loadMoreText?: string
  finishedText?: string
  errorText?: string
  emptyText?: string
  // 显示配置
  showBackTop?: boolean
  backTopDistance?: number
  // 缓存配置
  cache?: boolean
  cacheKey?: string
  maxCacheSize?: number
}

const props = withDefaults(defineProps<InfiniteScrollProps>(), {
  items: () => [],
  disabled: false,
  distance: 100,
  immediate: true,
  delay: 300,
  useObserver: true,
  pageSize: 20,
  currentPage: 1,
  totalPages: 0,
  hasMore: true,
  loading: false,
  finished: false,
  error: null,
  loadingText: '加载中...',
  loadMoreText: '加载更多',
  finishedText: '没有更多了',
  errorText: '加载失败',
  emptyText: '暂无数据',
  showBackTop: true,
  backTopDistance: 300,
  cache: false,
  cacheKey: '',
  maxCacheSize: 1000
})

// ======== 组件事件 ========
const emit = defineEmits<{
  'update:loading': [loading: boolean]
  'update:finished': [finished: boolean]
  'update:error': [error: Error | null]
  'update:currentPage': [page: number]
  load: [page: number]
  loaded: [items: any[], page: number]
  error: [error: Error, page: number]
  finished: []
  scroll: [{ scrollTop: number; scrollLeft: number }]
  'back-top': []
}>()

// ======== 响应式数据 ========
const containerRef = ref<HTMLElement>()
const loadMoreRef = ref<HTMLElement>()

const displayItems = ref<any[]>([])
const internalLoading = ref(false)
const internalFinished = ref(false)
const internalError = ref<Error | null>(null)
const internalPage = ref(1)
const scrollTop = ref(0)
const isRetrying = ref(false)

// 缓存相关
const cache = ref<Map<string, any[]>>(new Map())
const cacheTimestamps = ref<Map<string, number>>(new Map())

// ======== 计算属性 ========
const isLoading = computed({
  get: () => props.loading ?? internalLoading.value,
  set: (value) => {
    internalLoading.value = value
    emit('update:loading', value)
  }
})

const isFinished = computed({
  get: () => props.finished ?? internalFinished.value,
  set: (value) => {
    internalFinished.value = value
    emit('update:finished', value)
  }
})

const error = computed({
  get: () => props.error ?? internalError.value,
  set: (value) => {
    internalError.value = value
    emit('update:error', value)
  }
})

const currentPage = computed({
  get: () => props.currentPage ?? internalPage.value,
  set: (value) => {
    internalPage.value = value
    emit('update:currentPage', value)
  }
})

const showLoadMore = computed(() => {
  return !isFinished.value && !error.value && displayItems.value.length > 0
})

const showFinished = computed(() => {
  return isFinished.value && displayItems.value.length > 0
})

const showError = computed(() => {
  return !!error.value && !isLoading.value
})

const showEmpty = computed(() => {
  return displayItems.value.length === 0 && isFinished.value && !isLoading.value
})

const showBackTopButton = computed(() => {
  return props.showBackTop && scrollTop.value > props.backTopDistance
})

// ======== 方法函数 ========

/**
 * 加载数据
 */
const loadData = async (page: number = currentPage.value) => {
  if (isLoading.value || isFinished.value || props.disabled) {
    return
  }
  
  try {
    isLoading.value = true
    error.value = null
    
    emit('load', page)
    
    // 检查缓存
    if (props.cache && props.cacheKey) {
      const cacheKey = `${props.cacheKey}_${page}`
      const cachedData = cache.value.get(cacheKey)
      
      if (cachedData) {
        console.log('从缓存加载数据:', page)
        handleLoadSuccess(cachedData, page)
        return
      }
    }
    
    // 调用加载函数
    if (props.loadMore) {
      const result = await props.loadMore()
      const newItems = Array.isArray(result) ? result : []
      
      handleLoadSuccess(newItems, page)
    } else {
      // 如果没有提供加载函数，使用外部传入的items
      handleLoadSuccess(props.items || [], page)
    }
  } catch (err) {
    console.error('加载数据失败:', err)
    const errorObj = err instanceof Error ? err : new Error(String(err))
    error.value = errorObj
    emit('error', errorObj, page)
  } finally {
    isLoading.value = false
  }
}

/**
 * 处理加载成功
 */
const handleLoadSuccess = (newItems: any[], page: number) => {
  // 缓存数据
  if (props.cache && props.cacheKey) {
    const cacheKey = `${props.cacheKey}_${page}`
    cache.value.set(cacheKey, newItems)
    cacheTimestamps.value.set(cacheKey, Date.now())
    
    // 清理过期缓存
    cleanupCache()
  }
  
  if (page === 1) {
    // 首次加载或刷新
    displayItems.value = newItems
  } else {
    // 追加数据
    displayItems.value = [...displayItems.value, ...newItems]
  }
  
  // 检查是否还有更多数据
  if (newItems.length < props.pageSize || 
      (props.totalPages > 0 && page >= props.totalPages) ||
      !props.hasMore) {
    isFinished.value = true
    emit('finished')
  } else {
    currentPage.value = page + 1
  }
  
  emit('loaded', newItems, page)
}

/**
 * 清理过期缓存
 */
const cleanupCache = () => {
  if (cache.value.size > props.maxCacheSize) {
    // 删除最旧的缓存
    const entries = Array.from(cacheTimestamps.value.entries())
    entries.sort((a, b) => a[1] - b[1])
    
    const toDelete = entries.slice(0, Math.floor(props.maxCacheSize * 0.2))
    toDelete.forEach(([key]) => {
      cache.value.delete(key)
      cacheTimestamps.value.delete(key)
    })
  }
}

/**
 * 处理滚动事件
 */
const handleScroll = useThrottleFn((event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
  
  emit('scroll', {
    scrollTop: target.scrollTop,
    scrollLeft: target.scrollLeft
  })
  
  // 检查是否需要加载更多（非观察器模式）
  if (!props.useObserver) {
    checkLoadMore(target)
  }
}, 100)

/**
 * 检查是否需要加载更多
 */
const checkLoadMore = (element: HTMLElement) => {
  if (isLoading.value || isFinished.value || error.value || props.disabled) {
    return
  }
  
  const { scrollTop, scrollHeight, clientHeight } = element
  const distanceToBottom = scrollHeight - scrollTop - clientHeight
  
  if (distanceToBottom <= props.distance) {
    loadMore()
  }
}

/**
 * 加载更多
 */
const loadMore = () => {
  if (props.delay > 0) {
    setTimeout(() => {
      loadData(currentPage.value)
    }, props.delay)
  } else {
    loadData(currentPage.value)
  }
}

/**
 * 重试加载
 */
const retry = () => {
  if (isRetrying.value) return
  
  isRetrying.value = true
  error.value = null
  
  setTimeout(() => {
    loadData(currentPage.value)
    isRetrying.value = false
  }, 500)
}

/**
 * 刷新数据
 */
const refresh = () => {
  displayItems.value = []
  currentPage.value = 1
  isFinished.value = false
  error.value = null
  
  // 清除缓存
  if (props.cache && props.cacheKey) {
    cache.value.clear()
    cacheTimestamps.value.clear()
  }
  
  loadData(1)
}

/**
 * 滚动到顶部
 */
const scrollToTop = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
    emit('back-top')
  }
}

/**
 * 滚动到底部
 */
const scrollToBottom = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({
      top: containerRef.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

/**
 * 滚动到指定项
 */
const scrollToItem = (index: number) => {
  if (containerRef.value && index >= 0 && index < displayItems.value.length) {
    const itemElements = containerRef.value.children
    const targetElement = itemElements[index] as HTMLElement
    
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      })
    }
  }
}

// ======== 交叉观察器 ========
if (props.useObserver) {
  const { stop } = useIntersectionObserver(
    loadMoreRef,
    ([{ isIntersecting }]) => {
      if (isIntersecting && !isLoading.value && !isFinished.value && !error.value) {
        loadMore()
      }
    },
    {
      threshold: 0.1,
      rootMargin: '100px'
    }
  )
  
  onUnmounted(() => {
    stop()
  })
}

// ======== 生命周期 ========
onMounted(() => {
  if (props.immediate && displayItems.value.length === 0) {
    nextTick(() => {
      loadData(1)
    })
  }
})

// ======== 监听器 ========
watch(
  () => props.items,
  (newItems) => {
    if (newItems && newItems.length > 0) {
      displayItems.value = [...newItems]
    }
  },
  { immediate: true }
)

watch(
  () => props.hasMore,
  (hasMore) => {
    if (!hasMore) {
      isFinished.value = true
    }
  }
)

// ======== 暴露方法 ========
defineExpose({
  loadData,
  loadMore,
  retry,
  refresh,
  scrollToTop,
  scrollToBottom,
  scrollToItem,
  displayItems: computed(() => displayItems.value),
  isLoading,
  isFinished,
  error
})
</script>

<style scoped lang="scss">
@use '@/styles/mixins.scss' as *;

.infinite-scroll {
  position: relative;
  height: 100%;
  overflow: auto;
  @include scrollbar-style;
  
  &.scroll-disabled {
    overflow: hidden;
  }
  
  // 加载更多指示器
  .load-more-indicator {
    @include flex-center;
    min-height: 60px;
    padding: $padding-lg;
    color: var(--el-text-color-secondary);
    font-size: $font-size-sm;
    transition: all $transition-base ease;
    
    &.is-loading {
      color: var(--el-color-primary);
    }
    
    .default-loading {
      @include flex-center;
      gap: $margin-sm;
      
      .el-icon {
        font-size: 16px;
      }
    }
  }
  
  // 加载完成指示器
  .finished-indicator {
    @include flex-center;
    min-height: 50px;
    padding: $padding-md;
    color: var(--el-text-color-placeholder);
    font-size: $font-size-sm;
    border-top: 1px solid var(--el-border-color-lighter);
    
    .default-finished {
      @include flex-center;
      gap: $margin-sm;
      
      .finished-icon {
        color: var(--el-color-success);
      }
    }
  }
  
  // 错误指示器
  .error-indicator {
    @include flex-center;
    min-height: 80px;
    padding: $padding-lg;
    color: var(--el-color-danger);
    
    .default-error {
      @include flex-column-center;
      gap: $margin-md;
      text-align: center;
      
      .error-icon {
        font-size: 32px;
      }
      
      .error-text {
        color: var(--el-text-color-secondary);
        font-size: $font-size-sm;
      }
    }
  }
  
  // 空数据指示器
  .empty-indicator {
    @include flex-center;
    min-height: 200px;
    padding: $padding-xl;
  }
  
  // 回到顶部按钮
  .back-to-top {
    position: fixed;
    right: 20px;
    bottom: 20px;
    @include size(40px);
    @include flex-center;
    background: var(--el-color-primary);
    color: white;
    border-radius: $border-radius-circle;
    cursor: pointer;
    @include elevation(2);
    z-index: $z-index-fixed;
    transition: all $transition-base ease;
    
    &:hover {
      @include elevation(3);
      transform: translateY(-2px);
    }
    
    &:active {
      transform: translateY(0);
    }
    
    .el-icon {
      font-size: 18px;
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

// 暗色模式适配
.dark {
  .infinite-scroll {
    .load-more-indicator {
      border-top-color: var(--el-border-color-darker);
    }
    
    .finished-indicator {
      border-top-color: var(--el-border-color-darker);
    }
  }
}

// 响应式设计
@include respond-to(xs) {
  .infinite-scroll {
    .back-to-top {
      right: 15px;
      bottom: 15px;
      @include size(36px);
      
      .el-icon {
        font-size: 16px;
      }
    }
    
    .load-more-indicator,
    .finished-indicator,
    .error-indicator {
      min-height: 50px;
      padding: $padding-md;
      
      .default-loading,
      .default-finished,
      .default-error {
        font-size: 12px;
        
        .el-icon {
          font-size: 14px;
        }
      }
    }
  }
}
</style>