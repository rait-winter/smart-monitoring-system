<template>
  <div 
    class="mobile-table"
    :class="[
      { 'mobile-table--mobile': isMobile },
      { 'mobile-table--loading': loading }
    ]"
  >
    <!-- 表格头部工具栏 -->
    <div v-if="showToolbar" class="mobile-table__toolbar">
      <!-- 搜索框 -->
      <div v-if="showSearch" class="mobile-table__search">
        <el-input
          v-model="searchText"
          :placeholder="searchPlaceholder"
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      
      <!-- 过滤器 -->
      <div v-if="showFilter && filters.length > 0" class="mobile-table__filters">
        <el-dropdown v-for="filter in filters" :key="filter.key" @command="(value) => handleFilter(filter.key, value)">
          <el-button text>
            {{ filter.label }}
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="option in filter.options" 
                :key="option.value" 
                :command="option.value"
              >
                {{ option.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      
      <!-- 操作按钮 -->
      <div v-if="showActions" class="mobile-table__actions">
        <slot name="toolbar-actions" />
      </div>
    </div>
    
    <!-- 桌面端表格 -->
    <div v-if="!isMobile" class="desktop-table">
      <el-table
        ref="tableRef"
        :data="paginatedData"
        :loading="loading"
        :height="tableHeight"
        :stripe="stripe"
        :border="border"
        :show-header="showHeader"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        @row-click="handleRowClick"
      >
        <!-- 选择列 -->
        <el-table-column
          v-if="showSelection"
          type="selection"
          width="55"
          align="center"
        />
        
        <!-- 索引列 -->
        <el-table-column
          v-if="showIndex"
          type="index"
          :label="indexLabel"
          width="60"
          align="center"
        />
        
        <!-- 数据列 -->
        <el-table-column
          v-for="column in columns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :min-width="column.minWidth"
          :fixed="column.fixed"
          :sortable="column.sortable"
          :align="column.align || 'left'"
          :show-overflow-tooltip="column.showOverflowTooltip !== false"
        >
          <template #default="{ row, column: col, $index }">
            <slot 
              :name="column.prop" 
              :row="row" 
              :column="col" 
              :index="$index"
              :value="row[column.prop]"
            >
              <span v-if="column.formatter">
                {{ column.formatter(row, col, row[column.prop], $index) }}
              </span>
              <span v-else>{{ row[column.prop] }}</span>
            </slot>
          </template>
        </el-table-column>
        
        <!-- 操作列 -->
        <el-table-column
          v-if="showOperations"
          :label="operationsLabel"
          :width="operationsWidth"
          :fixed="operationsFixed"
          align="center"
        >
          <template #default="{ row, $index }">
            <slot name="operations" :row="row" :index="$index" />
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 移动端卡片列表 -->
    <div v-else class="mobile-cards">
      <!-- 加载状态 -->
      <div v-if="loading" class="mobile-cards__loading">
        <el-skeleton 
          v-for="i in 3" 
          :key="i" 
          class="mobile-card-skeleton"
          :rows="3" 
          animated 
        />
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="paginatedData.length === 0" class="mobile-cards__empty">
        <el-empty :description="emptyText" />
      </div>
      
      <!-- 数据卡片 -->
      <div v-else class="mobile-cards__list">
        <div
          v-for="(row, index) in paginatedData"
          :key="getRowKey(row, index)"
          class="mobile-card"
          :class="{ 'mobile-card--selected': isRowSelected(row) }"
          @click="handleRowClick(row, null, null)"
        >
          <!-- 卡片头部 -->
          <div class="mobile-card__header">
            <!-- 选择框 -->
            <el-checkbox
              v-if="showSelection"
              :model-value="isRowSelected(row)"
              @change="(checked) => handleRowSelection(row, checked)"
              @click.stop
            />
            
            <!-- 主要信息 -->
            <div class="mobile-card__primary">
              <slot name="mobile-primary" :row="row" :index="index">
                <div class="mobile-card__title">
                  {{ row[primaryField] || `项目 ${index + 1}` }}
                </div>
                <div v-if="secondaryField" class="mobile-card__subtitle">
                  {{ row[secondaryField] }}
                </div>
              </slot>
            </div>
            
            <!-- 状态或标签 -->
            <div class="mobile-card__status">
              <slot name="mobile-status" :row="row" :index="index">
                <el-tag v-if="statusField" :type="getStatusType(row[statusField])">
                  {{ row[statusField] }}
                </el-tag>
              </slot>
            </div>
          </div>
          
          <!-- 卡片内容 -->
          <div class="mobile-card__content">
            <div class="mobile-card__fields">
              <div
                v-for="column in mobileDisplayColumns"
                :key="column.prop"
                class="mobile-card__field"
              >
                <span class="mobile-card__field-label">{{ column.label }}:</span>
                <span class="mobile-card__field-value">
                  <slot 
                    :name="column.prop" 
                    :row="row" 
                    :column="column" 
                    :index="index"
                    :value="row[column.prop]"
                  >
                    <span v-if="column.formatter">
                      {{ column.formatter(row, column, row[column.prop], index) }}
                    </span>
                    <span v-else>{{ row[column.prop] }}</span>
                  </slot>
                </span>
              </div>
            </div>
          </div>
          
          <!-- 卡片操作 -->
          <div v-if="showOperations" class="mobile-card__actions">
            <slot name="mobile-operations" :row="row" :index="index">
              <slot name="operations" :row="row" :index="index" />
            </slot>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页器 -->
    <div v-if="showPagination && totalCount > pageSize" class="mobile-table__pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="pageSizes"
        :layout="paginationLayout"
        :small="isMobile"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { getResponsiveConfig } from '@/utils/responsive'
import { Search, ArrowDown } from '@element-plus/icons-vue'

// 接口定义
interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: boolean | string
  sortable?: boolean | string
  align?: 'left' | 'center' | 'right'
  showOverflowTooltip?: boolean
  formatter?: (row: any, column: any, cellValue: any, index: number) => string
  mobileDisplay?: boolean // 移动端是否显示
}

interface FilterOption {
  label: string
  value: any
}

interface TableFilter {
  key: string
  label: string
  options: FilterOption[]
}

// Props
interface Props {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  height?: string | number
  stripe?: boolean
  border?: boolean
  showHeader?: boolean
  showSelection?: boolean
  showIndex?: boolean
  showOperations?: boolean
  showToolbar?: boolean
  showSearch?: boolean
  showFilter?: boolean
  showActions?: boolean
  showPagination?: boolean
  indexLabel?: string
  operationsLabel?: string
  operationsWidth?: string | number
  operationsFixed?: boolean | string
  searchPlaceholder?: string
  emptyText?: string
  primaryField?: string
  secondaryField?: string
  statusField?: string
  rowKey?: string | ((row: any) => string)
  pageSize?: number
  pageSizes?: number[]
  filters?: TableFilter[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  height: 'auto',
  stripe: true,
  border: false,
  showHeader: true,
  showSelection: false,
  showIndex: false,
  showOperations: false,
  showToolbar: true,
  showSearch: true,
  showFilter: true,
  showActions: true,
  showPagination: true,
  indexLabel: '#',
  operationsLabel: '操作',
  operationsWidth: 150,
  operationsFixed: 'right',
  searchPlaceholder: '搜索...',
  emptyText: '暂无数据',
  primaryField: 'name',
  secondaryField: 'description',
  statusField: 'status',
  rowKey: 'id',
  pageSize: 10,
  pageSizes: () => [10, 20, 50, 100]
})

// Emits
interface Emits {
  (e: 'selection-change', selection: any[]): void
  (e: 'sort-change', { column, prop, order }: any): void
  (e: 'row-click', row: any, column: any, event: Event): void
  (e: 'page-change', page: number): void
  (e: 'page-size-change', size: number): void
  (e: 'search', text: string): void
  (e: 'filter', filters: Record<string, any>): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const tableRef = ref()
const searchText = ref('')
const currentPage = ref(1)
const currentPageSize = ref(props.pageSize)
const selectedRows = ref<any[]>([])
const activeFilters = ref<Record<string, any>>({})

// 计算属性
const isMobile = computed(() => getResponsiveConfig().isMobile)

const pageSize = computed({
  get: () => currentPageSize.value,
  set: (value) => {
    currentPageSize.value = value
    emit('page-size-change', value)
  }
})

const tableHeight = computed(() => {
  if (isMobile.value) return 'auto'
  return props.height
})

const paginationLayout = computed(() => {
  return isMobile.value 
    ? 'prev, pager, next'
    : 'total, sizes, prev, pager, next, jumper'
})

// 过滤和搜索后的数据
const filteredData = computed(() => {
  let result = [...props.data]
  
  // 搜索过滤
  if (searchText.value.trim()) {
    const searchTerm = searchText.value.toLowerCase()
    result = result.filter(row => {
      return props.columns.some(column => {
        const value = row[column.prop]
        return value && value.toString().toLowerCase().includes(searchTerm)
      })
    })
  }
  
  // 过滤器过滤
  Object.entries(activeFilters.value).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      result = result.filter(row => row[key] === value)
    }
  })
  
  return result
})

const totalCount = computed(() => filteredData.value.length)

// 分页数据
const paginatedData = computed(() => {
  if (!props.showPagination) return filteredData.value
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// 移动端显示的列
const mobileDisplayColumns = computed(() => {
  return props.columns.filter(column => 
    column.mobileDisplay !== false && 
    column.prop !== props.primaryField &&
    column.prop !== props.secondaryField &&
    column.prop !== props.statusField
  ).slice(0, 3) // 最多显示3个字段
})

// 方法
const getRowKey = (row: any, index: number): string => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || index.toString()
}

const isRowSelected = (row: any): boolean => {
  const key = getRowKey(row, 0)
  return selectedRows.value.some(selectedRow => 
    getRowKey(selectedRow, 0) === key
  )
}

const getStatusType = (status: string): string => {
  const statusMap: Record<string, string> = {
    'success': 'success',
    'warning': 'warning',
    'error': 'danger',
    'danger': 'danger',
    'info': 'info',
    '正常': 'success',
    '警告': 'warning',
    '错误': 'danger',
    '异常': 'danger'
  }
  return statusMap[status] || ''
}

const handleSearch = (value: string) => {
  currentPage.value = 1
  emit('search', value)
}

const handleFilter = (key: string, value: any) => {
  activeFilters.value[key] = value
  currentPage.value = 1
  emit('filter', { ...activeFilters.value })
}

const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

const handleRowSelection = (row: any, checked: boolean) => {
  if (checked) {
    if (!isRowSelected(row)) {
      selectedRows.value.push(row)
    }
  } else {
    const key = getRowKey(row, 0)
    selectedRows.value = selectedRows.value.filter(selectedRow => 
      getRowKey(selectedRow, 0) !== key
    )
  }
  emit('selection-change', selectedRows.value)
}

const handleSortChange = (sortInfo: any) => {
  emit('sort-change', sortInfo)
}

const handleRowClick = (row: any, column: any, event: Event) => {
  emit('row-click', row, column, event)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  emit('page-change', page)
}

const handlePageSizeChange = (size: number) => {
  currentPage.value = 1
  pageSize.value = size
}

// 监听器
watch(() => props.data, () => {
  currentPage.value = 1
})

watch(() => props.pageSize, (newSize) => {
  currentPageSize.value = newSize
})

// 暴露方法
defineExpose({
  clearSelection: () => {
    selectedRows.value = []
    tableRef.value?.clearSelection()
  },
  toggleRowSelection: (row: any, selected?: boolean) => {
    if (isMobile.value) {
      handleRowSelection(row, selected ?? !isRowSelected(row))
    } else {
      tableRef.value?.toggleRowSelection(row, selected)
    }
  },
  setCurrentRow: (row: any) => {
    tableRef.value?.setCurrentRow(row)
  }
})
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;
@use '@/styles/mixins' as *;
@use '@/styles/responsive' as responsive;

.mobile-table {
  background: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  overflow: hidden;
  
  &--loading {
    .mobile-cards__list {
      opacity: 0.6;
      pointer-events: none;
    }
  }
}

// 工具栏
.mobile-table__toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  @include responsive.media-down(sm) {
    padding: 12px;
  }
}

.mobile-table__search {
  margin-bottom: 12px;
  
  .el-input {
    max-width: 300px;
  }
  
  @include responsive.media-down(sm) {
    .el-input {
      max-width: 100%;
    }
  }
}

.mobile-table__filters {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.mobile-table__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

// 桌面端表格
.desktop-table {
  .el-table {
    --el-table-header-bg-color: var(--el-fill-color-light);
  }
}

// 移动端卡片
.mobile-cards {
  &__loading {
    padding: 16px;
  }
  
  &__empty {
    padding: 40px 16px;
    text-align: center;
  }
  
  &__list {
    padding: 8px;
  }
}

.mobile-card-skeleton {
  margin-bottom: 12px;
  border-radius: var(--el-border-radius-base);
}

// 移动端卡片样式
.mobile-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--el-border-radius-base);
  margin-bottom: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  
  @include mobile-touch-optimization;
  
  &:hover {
    border-color: var(--el-border-color);
    box-shadow: var(--el-box-shadow-light);
  }
  
  &:active {
    transform: scale(0.98);
  }
  
  &--selected {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
  
  &__header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px 8px 16px;
  }
  
  &__primary {
    flex: 1;
    min-width: 0;
  }
  
  &__title {
    font-size: 15px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    line-height: 1.4;
    word-break: break-word;
  }
  
  &__subtitle {
    font-size: 12px;
    color: var(--el-text-color-regular);
    margin-top: 2px;
    line-height: 1.4;
  }
  
  &__status {
    flex-shrink: 0;
  }
  
  &__content {
    padding: 0 16px 8px 16px;
  }
  
  &__fields {
    display: grid;
    gap: 6px;
  }
  
  &__field {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    
    &-label {
      color: var(--el-text-color-regular);
      flex-shrink: 0;
      font-weight: 500;
    }
    
    &-value {
      color: var(--el-text-color-primary);
      text-align: right;
      word-break: break-word;
    }
  }
  
  &__actions {
    padding: 8px 16px 12px 16px;
    border-top: 1px solid var(--el-border-color-extra-light);
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
}

// 分页器
.mobile-table__pagination {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: center;
  
  .el-pagination {
    &.is-small {
      .el-pager li {
        min-width: 32px;
        height: 32px;
        line-height: 32px;
      }
    }
  }
}

// 响应式适配
@include media-down(sm) {
  .mobile-card {
    &__header {
      padding: 10px 12px 6px 12px;
      gap: 8px;
    }
    
    &__title {
      font-size: 14px;
    }
    
    &__subtitle {
      font-size: 11px;
    }
    
    &__content {
      padding: 0 12px 6px 12px;
    }
    
    &__field {
      font-size: 12px;
      gap: 6px;
    }
    
    &__actions {
      padding: 6px 12px 10px 12px;
    }
  }
}
</style>