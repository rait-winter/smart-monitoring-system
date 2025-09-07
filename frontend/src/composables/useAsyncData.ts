import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

export interface AsyncDataOptions {
  immediate?: boolean
  defaultValue?: any
  onSuccess?: (data: any) => void
  onError?: (error: any) => void
}

export function useAsyncData<T = any>(
  asyncFn: () => Promise<T>,
  options: AsyncDataOptions = {}
) {
  const {
    immediate = true,
    defaultValue = null,
    onSuccess,
    onError
  } = options

  const data = ref<T>(defaultValue)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const execute = async () => {
    try {
      loading.value = true
      error.value = null
      
      const result = await asyncFn()
      data.value = result
      
      onSuccess?.(result)
      return result
    } catch (err) {
      error.value = err as Error
      onError?.(err)
      
      console.error('异步数据加载失败:', err)
      ElMessage.error('数据加载失败，请稍后重试')
      
      throw err
    } finally {
      loading.value = false
    }
  }

  const refresh = () => execute()

  const isReady = computed(() => !loading.value && !error.value)

  if (immediate) {
    execute()
  }

  return {
    data,
    loading,
    error,
    execute,
    refresh,
    isReady
  }
}

// 分页数据加载hook
export function usePaginatedData<T = any>(
  fetchFn: (page: number, size: number, filters?: any) => Promise<{ data: T[], total: number }>,
  options: { 
    pageSize?: number
    immediate?: boolean 
  } = {}
) {
  const { pageSize = 20, immediate = true } = options
  
  const data = ref<T[]>([])
  const loading = ref(false)
  const currentPage = ref(1)
  const total = ref(0)
  const filters = ref({})

  const fetch = async () => {
    try {
      loading.value = true
      const result = await fetchFn(currentPage.value, pageSize, filters.value)
      
      data.value = result.data
      total.value = result.total
    } catch (error) {
      console.error('分页数据加载失败:', error)
      ElMessage.error('数据加载失败')
    } finally {
      loading.value = false
    }
  }

  const handlePageChange = (page: number) => {
    currentPage.value = page
    fetch()
  }

  const updateFilters = (newFilters: any) => {
    filters.value = { ...filters.value, ...newFilters }
    currentPage.value = 1
    fetch()
  }

  const refresh = () => fetch()

  if (immediate) {
    fetch()
  }

  return {
    data,
    loading,
    currentPage,
    total,
    filters,
    handlePageChange,
    updateFilters,
    refresh
  }
}