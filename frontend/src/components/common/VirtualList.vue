<template>
  <div class="virtual-list" ref="containerRef" @scroll="handleScroll">
    <div class="virtual-list-wrapper" :style="{ height: totalHeight + 'px' }">
      <div 
        class="virtual-list-items" 
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="(item, index) in visibleItems"
          :key="getItemKey(item, startIndex + index)"
          class="virtual-list-item"
          :style="getItemStyle(startIndex + index)"
          @click="handleItemClick(item, startIndex + index, $event)"
        >
          <slot 
            :item="item" 
            :index="startIndex + index"
            :active="activeIndex === startIndex + index"
          >
            <div class="default-item">
              {{ item }}
            </div>
          </slot>
        </div>
      </div>

      <!-- 加载更多指示器 -->
      <div
        v-if="showLoadMore"
        class="load-more-indicator"
        :style="{ transform: `translateY(${loadMoreY}px)` }"
      >
        <el-icon v-if="loadingMore" class="is-loading">
          <Loading />
        </el-icon>
        <span>{{ loadingMore ? loadingText : loadMoreText }}</span>
      </div>
    </div>
    
    <!-- 自定义滚动条 -->
    <div 
      v-if="showScrollbar && totalHeight > visibleHeight"
      class="virtual-scrollbar"
      @mousedown="handleScrollbarMouseDown"
    >
      <div 
        class="scrollbar-thumb"
        :style="scrollbarStyle"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useThrottleFn, useEventListener } from '@vueuse/core'
import { Loading } from '@element-plus/icons-vue'

// 类型定义
export interface VirtualListProps {
  items: any[]
  itemHeight?: number | ((index: number) => number)
  containerHeight?: string
  buffer?: number
  threshold?: number
  keyField?: string
  horizontal?: boolean
  showScrollbar?: boolean
  loadMoreText?: string
  loadingText?: string
  loadingMore?: boolean
  hasMore?: boolean
  keepAlive?: boolean
  preload?: number
}

const props = withDefaults(defineProps<VirtualListProps>(), {
  itemHeight: 50,
  containerHeight: '400px',
  buffer: 5,
  threshold: 100,
  keyField: 'id',
  horizontal: false,
  showScrollbar: true,
  loadMoreText: '加载更多',
  loadingText: '加载中...',
  loadingMore: false,
  hasMore: true,
  keepAlive: false,
  preload: 200
})

// 组件事件
const emit = defineEmits<{
  loadMore: []
  scroll: [{ scrollTop: number; scrollLeft: number }]
  itemClick: [{ item: any; index: number; event: Event }]
  itemVisible: [{ item: any; index: number }]
  itemHidden: [{ item: any; index: number }]
}>()

// 响应式数据
const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)
const scrollLeft = ref(0)
const containerSize = ref({ width: 0, height: 0 })
const activeIndex = ref(-1)
const visibleRange = ref({ start: 0, end: 0 })

// 滚动条拖拽状态
const isDragging = ref(false)
const dragStartY = ref(0)
const dragStartScrollTop = ref(0)

// 获取项高度
const getItemHeight = (index: number): number => {
  if (typeof props.itemHeight === 'function') {
    return props.itemHeight(index)
  }
  return props.itemHeight
}

// 计算总高度
const totalHeight = computed(() => {
  if (typeof props.itemHeight === 'function') {
    return props.items.reduce((sum, _, index) => sum + getItemHeight(index), 0)
  }
  return props.items.length * props.itemHeight
})

// 容器可见高度
const visibleHeight = computed(() => {
  return parseInt(props.containerHeight) || containerSize.value.height
})

// 可见项数量
const visibleCount = computed(() => {
  if (typeof props.itemHeight === 'function') {
    let count = 0
    let height = 0
    let index = startIndex.value
    
    while (height < visibleHeight.value && index < props.items.length) {
      height += getItemHeight(index)
      count++
      index++
    }
    
    return Math.min(count + props.buffer * 2, props.items.length - startIndex.value)
  }
  
  return Math.min(
    Math.ceil(visibleHeight.value / props.itemHeight) + props.buffer * 2,
    props.items.length
  )
})

// 开始索引
const startIndex = computed(() => {
  if (typeof props.itemHeight === 'function') {
    let index = 0
    let height = 0
    
    while (height < scrollTop.value && index < props.items.length) {
      height += getItemHeight(index)
      if (height > scrollTop.value) {
        break
      }
      index++
    }
    
    return Math.max(0, index - props.buffer)
  }
  
  const index = Math.floor(scrollTop.value / props.itemHeight)
  return Math.max(0, index - props.buffer)
})

// 结束索引
const endIndex = computed(() => {
  return Math.min(startIndex.value + visibleCount.value, props.items.length)
})

// 可见项目
const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value)
})

// 偏移量
const offsetY = computed(() => {
  if (typeof props.itemHeight === 'function') {
    let offset = 0
    for (let i = 0; i < startIndex.value; i++) {
      offset += getItemHeight(i)
    }
    return offset
  }
  
  return startIndex.value * props.itemHeight
})

// 是否显示加载更多
const showLoadMore = computed(() => {
  return props.hasMore && props.items.length > 0
})

// 加载更多位置
const loadMoreY = computed(() => {
  return totalHeight.value - 50
})

// 滚动条样式
const scrollbarStyle = computed(() => {
  const thumbHeight = Math.max(
    20,
    (visibleHeight.value / totalHeight.value) * visibleHeight.value
  )
  
  const thumbTop = (scrollTop.value / totalHeight.value) * visibleHeight.value
  
  return {
    height: thumbHeight + 'px',
    transform: `translateY(${thumbTop}px)`
  }
})

// 获取项的唯一key
const getItemKey = (item: any, index: number): string | number => {
  if (typeof item === 'object' && item[props.keyField]) {
    return item[props.keyField]
  }
  return index
}

// 获取项样式
const getItemStyle = (index: number) => {
  return {
    height: getItemHeight(index) + 'px',
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0
  }
}

// 处理滚动事件
const handleScroll = useThrottleFn((event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
  scrollLeft.value = target.scrollLeft
  
  // 触发滚动事件
  emit('scroll', {
    scrollTop: scrollTop.value,
    scrollLeft: scrollLeft.value
  })
  
  // 检查是否需要加载更多
  checkLoadMore()
  
  // 更新可见范围
  updateVisibleRange()
}, 16)

// 检查是否需要加载更多
const checkLoadMore = () => {
  if (!props.hasMore || props.loadingMore) return
  
  const scrollBottom = scrollTop.value + visibleHeight.value
  const shouldLoadMore = totalHeight.value - scrollBottom <= props.threshold
  
  if (shouldLoadMore) {
    emit('loadMore')
  }
}

// 更新可见范围
const updateVisibleRange = () => {
  const newStart = startIndex.value
  const newEnd = endIndex.value
  
  // 检查新进入视野的项
  for (let i = newStart; i < newEnd; i++) {
    if (i < visibleRange.value.start || i >= visibleRange.value.end) {
      emit('itemVisible', {
        item: props.items[i],
        index: i
      })
    }
  }
  
  // 检查离开视野的项
  for (let i = visibleRange.value.start; i < visibleRange.value.end; i++) {
    if (i < newStart || i >= newEnd) {
      emit('itemHidden', {
        item: props.items[i],
        index: i
      })
    }
  }
  
  visibleRange.value = { start: newStart, end: newEnd }
}

// 滚动到指定位置
const scrollTo = (options: {
  index?: number
  offset?: number
  behavior?: 'smooth' | 'auto'
}) => {
  if (!containerRef.value) return
  
  let targetScrollTop = 0
  
  if (options.index !== undefined) {
    if (typeof props.itemHeight === 'function') {
      for (let i = 0; i < options.index; i++) {
        targetScrollTop += getItemHeight(i)
      }
    } else {
      targetScrollTop = options.index * props.itemHeight
    }
  } else if (options.offset !== undefined) {
    targetScrollTop = options.offset
  }
  
  containerRef.value.scrollTo({
    top: targetScrollTop,
    behavior: options.behavior || 'smooth'
  })
}

// 滚动到顶部
const scrollToTop = () => {
  scrollTo({ offset: 0, behavior: 'smooth' })
}

// 滚动到底部
const scrollToBottom = () => {
  scrollTo({ offset: totalHeight.value, behavior: 'smooth' })
}

// 处理滚动条鼠标按下
const handleScrollbarMouseDown = (event: MouseEvent) => {
  isDragging.value = true
  dragStartY.value = event.clientY
  dragStartScrollTop.value = scrollTop.value
  
  document.addEventListener('mousemove', handleScrollbarMouseMove)
  document.addEventListener('mouseup', handleScrollbarMouseUp)
  
  event.preventDefault()
}

// 处理滚动条鼠标移动
const handleScrollbarMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || !containerRef.value) return
  
  const deltaY = event.clientY - dragStartY.value
  const scrollRatio = deltaY / visibleHeight.value
  const targetScrollTop = dragStartScrollTop.value + scrollRatio * totalHeight.value
  
  containerRef.value.scrollTop = Math.max(0, Math.min(targetScrollTop, totalHeight.value - visibleHeight.value))
}

// 处理滚动条鼠标释放
const handleScrollbarMouseUp = () => {
  isDragging.value = false
  
  document.removeEventListener('mousemove', handleScrollbarMouseMove)
  document.removeEventListener('mouseup', handleScrollbarMouseUp)
}

// 更新容器尺寸
const updateContainerSize = () => {
  if (containerRef.value) {
    containerSize.value = {
      width: containerRef.value.clientWidth,
      height: containerRef.value.clientHeight
    }
  }
}

// 处理项点击
const handleItemClick = (item: any, index: number, event: Event) => {
  activeIndex.value = index
  emit('itemClick', { item, index, event })
}

// 生命周期
onMounted(() => {
  updateContainerSize()
  useEventListener(window, 'resize', updateContainerSize)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleScrollbarMouseMove)
  document.removeEventListener('mouseup', handleScrollbarMouseUp)
})

// 监听数据变化
watch(
  () => props.items,
  () => {
    nextTick(() => {
      scrollTop.value = 0
      visibleRange.value = { start: 0, end: 0 }
      updateVisibleRange()
    })
  },
  { immediate: true }
)

// 暴露方法
defineExpose({
  scrollTo,
  scrollToTop,
  scrollToBottom,
  containerRef,
  visibleItems,
  startIndex,
  endIndex
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
@use '@/styles/mixins' as *;

.virtual-list {
  position: relative;
  overflow: auto;
  background: var(--el-bg-color);
  
  &::-webkit-scrollbar {
    width: 0;
    height: 0;
  }
  
  .virtual-list-wrapper {
    position: relative;
  }
  
  .virtual-list-items {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
  }
  
  .virtual-list-item {
    position: absolute;
    width: 100%;
    
    .default-item {
      @include flex-start;
      height: 100%;
      padding: $padding-md;
      border-bottom: 1px solid var(--el-border-color-lighter);
      background: var(--el-bg-color);
      transition: background $transition-fast ease;
      
      &:hover {
        background: var(--el-fill-color-light);
      }
    }
  }
  
  .load-more-indicator {
    @include flex-center;
    position: absolute;
    width: 100%;
    height: 50px;
    gap: $margin-sm;
    color: var(--el-text-color-secondary);
    font-size: $font-size-sm;
    
    .el-icon {
      font-size: 16px;
    }
  }
  
  .virtual-scrollbar {
    position: absolute;
    right: 2px;
    top: 2px;
    bottom: 2px;
    width: 6px;
    background: var(--el-fill-color-lighter);
    border-radius: 3px;
    z-index: 10;
    
    .scrollbar-thumb {
      position: absolute;
      width: 100%;
      background: var(--el-fill-color-dark);
      border-radius: 3px;
      cursor: pointer;
      transition: background $transition-fast ease;
      
      &:hover {
        background: var(--el-color-primary);
      }
    }
  }
}

// 暗色模式适配
.dark {
  .virtual-list {
    .virtual-list-item {
      .default-item {
        border-bottom-color: var(--el-border-color-darker);
        
        &:hover {
          background: var(--el-fill-color-dark);
        }
      }
    }
  }
}

// 响应式设计
@include respond-to(xs) {
  .virtual-list {
    .virtual-scrollbar {
      width: 4px;
    }
    
    .virtual-list-item {
      .default-item {
        padding: $padding-sm;
      }
    }
  }
}
</style>