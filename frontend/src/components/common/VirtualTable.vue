<template>
  <div class="virtual-table" ref="containerRef" @scroll="handleScroll">
    <div class="virtual-table-header" v-if="showHeader">
      <div class="header-row">
        <div 
          v-for="column in columns" 
          :key="column.key"
          class="header-cell"
          :style="{ width: column.width || 'auto' }"
        >
          {{ column.title }}
        </div>
      </div>
    </div>
    
    <div class="virtual-table-body" :style="{ height: containerHeight + 'px' }">
      <div class="virtual-table-content" :style="{ height: totalHeight + 'px', transform: `translateY(${offsetY}px)` }">
        <div 
          v-for="(item, index) in visibleItems" 
          :key="getItemKey(item, startIndex + index)"
          class="table-row"
          :class="{ 'row-even': (startIndex + index) % 2 === 0 }"
        >
          <div 
            v-for="column in columns" 
            :key="column.key"
            class="table-cell"
            :style="{ width: column.width || 'auto' }"
          >
            <slot 
              :name="column.key" 
              :item="item" 
              :index="startIndex + index"
              :value="getItemValue(item, column.key)"
            >
              {{ getItemValue(item, column.key) }}
            </slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

export interface TableColumn {
  key: string
  title: string
  width?: string
  sortable?: boolean
}

export interface VirtualTableProps {
  data: any[]
  columns: TableColumn[]
  itemHeight?: number
  containerHeight?: number
  showHeader?: boolean
  bufferSize?: number
  keyField?: string
}

const props = withDefaults(defineProps<VirtualTableProps>(), {
  itemHeight: 40,
  containerHeight: 400,
  showHeader: true,
  bufferSize: 5,
  keyField: 'id'
})

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)

// 计算可见区域
const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))
const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.bufferSize))
const endIndex = computed(() => Math.min(props.data.length, startIndex.value + visibleCount.value + props.bufferSize * 2))

// 可见项目
const visibleItems = computed(() => props.data.slice(startIndex.value, endIndex.value))

// 总高度
const totalHeight = computed(() => props.data.length * props.itemHeight)

// 偏移量
const offsetY = computed(() => startIndex.value * props.itemHeight)

// 获取项目键值
const getItemKey = (item: any, index: number) => {
  return item[props.keyField] || index
}

// 获取项目值
const getItemValue = (item: any, key: string) => {
  return item[key]
}

// 处理滚动
const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
}

// 滚动到指定位置
const scrollTo = (index: number) => {
  if (containerRef.value) {
    const scrollTop = index * props.itemHeight
    containerRef.value.scrollTop = scrollTop
  }
}

// 滚动到顶部
const scrollToTop = () => {
  scrollTo(0)
}

// 滚动到底部
const scrollToBottom = () => {
  scrollTo(props.data.length - 1)
}

// 暴露方法
defineExpose({
  scrollTo,
  scrollToTop,
  scrollToBottom
})
</script>

<style scoped lang="scss">
.virtual-table {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
  
  .virtual-table-header {
    background: var(--el-bg-color-page);
    border-bottom: 1px solid var(--el-border-color);
    
    .header-row {
      display: flex;
      height: 40px;
      
      .header-cell {
        display: flex;
        align-items: center;
        padding: 0 12px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        border-right: 1px solid var(--el-border-color-lighter);
        
        &:last-child {
          border-right: none;
        }
      }
    }
  }
  
  .virtual-table-body {
    overflow: auto;
    
    .virtual-table-content {
      position: relative;
      
      .table-row {
        display: flex;
        height: 40px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        &:last-child {
          border-bottom: none;
        }
        
        &.row-even {
          background: var(--el-bg-color);
        }
        
        &:hover {
          background: var(--el-fill-color-light);
        }
        
        .table-cell {
          display: flex;
          align-items: center;
          padding: 0 12px;
          color: var(--el-text-color-regular);
          border-right: 1px solid var(--el-border-color-lighter);
          
          &:last-child {
            border-right: none;
          }
        }
      }
    }
  }
}

// 暗色模式适配
.dark {
  .virtual-table {
    .table-row {
      &.row-even {
        background: var(--monitor-bg-secondary);
      }
      
      &:hover {
        background: var(--monitor-bg-hover);
      }
    }
  }
}
</style>
