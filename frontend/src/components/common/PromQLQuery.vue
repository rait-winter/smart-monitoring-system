<template>
  <div class="promql-query">
    <el-card>
      <template #header>
        <div class="query-header">
          <el-icon><Search /></el-icon>
          <span>PromQL 查询</span>
          <div class="header-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="showExamples = !showExamples"
            >
              示例查询
            </el-button>
            <el-button 
              type="info" 
              size="small"
              @click="showHelp = !showHelp"
            >
              语法帮助
            </el-button>
          </div>
        </div>
      </template>

      <!-- 查询输入区域 -->
      <div class="query-input-section">
        <el-form :model="queryForm" @submit.prevent="executeQuery">
          <el-form-item label="PromQL 查询语句">
            <el-input
              v-model="queryForm.query"
              type="textarea"
              :rows="3"
              placeholder="输入 PromQL 查询语句，例如：up 或 rate(http_requests_total[5m])"
              class="query-input"
            />
          </el-form-item>
          
          <el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="查询时间">
                  <el-date-picker
                    v-model="queryForm.time"
                    type="datetime"
                    placeholder="选择查询时间点"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="查询类型">
                  <el-select v-model="queryForm.queryType" style="width: 100%">
                    <el-option label="即时查询 (query)" value="query" />
                    <el-option label="范围查询 (query_range)" value="query_range" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form-item>

          <!-- 范围查询参数 -->
          <el-form-item v-if="queryForm.queryType === 'query_range'">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="开始时间">
                  <el-date-picker
                    v-model="queryForm.start"
                    type="datetime"
                    placeholder="开始时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="结束时间">
                  <el-date-picker
                    v-model="queryForm.end"
                    type="datetime"
                    placeholder="结束时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DDTHH:mm:ss"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="步长">
                  <el-select v-model="queryForm.step" style="width: 100%">
                    <el-option label="15秒" value="15s" />
                    <el-option label="30秒" value="30s" />
                    <el-option label="1分钟" value="1m" />
                    <el-option label="5分钟" value="5m" />
                    <el-option label="15分钟" value="15m" />
                    <el-option label="1小时" value="1h" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              @click="executeQuery"
              :loading="queryLoading"
              :icon="Search"
            >
              执行查询
            </el-button>
            <el-button @click="clearQuery">清空</el-button>
            <el-button 
              type="success" 
              @click="exportResults"
              :disabled="!queryResults"
            >
              导出结果
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 示例查询 -->
      <el-collapse v-if="showExamples" class="examples-section">
        <el-collapse-item title="常用查询示例" name="examples">
          <div class="examples-grid">
            <el-card 
              v-for="example in queryExamples" 
              :key="example.title"
              class="example-card"
              @click="useExample(example.query)"
            >
              <h4>{{ example.title }}</h4>
              <code>{{ example.query }}</code>
              <p>{{ example.description }}</p>
            </el-card>
          </div>
        </el-collapse-item>
      </el-collapse>

      <!-- 语法帮助 -->
      <el-collapse v-if="showHelp" class="help-section">
        <el-collapse-item title="PromQL 语法帮助" name="help">
          <div class="help-content">
            <h4>基本语法</h4>
            <ul>
              <li><code>metric_name</code> - 基本指标查询</li>
              <li><code>metric_name{label="value"}</code> - 带标签过滤</li>
              <li><code>rate(metric_name[5m])</code> - 计算速率</li>
              <li><code>sum(metric_name) by (label)</code> - 聚合查询</li>
            </ul>
            
            <h4>时间范围</h4>
            <ul>
              <li><code>s</code> - 秒</li>
              <li><code>m</code> - 分钟</li>
              <li><code>h</code> - 小时</li>
              <li><code>d</code> - 天</li>
              <li><code>w</code> - 周</li>
            </ul>

            <h4>常用函数</h4>
            <ul>
              <li><code>rate()</code> - 计算平均每秒增长率</li>
              <li><code>sum()</code> - 求和</li>
              <li><code>avg()</code> - 平均值</li>
              <li><code>max()</code> - 最大值</li>
              <li><code>min()</code> - 最小值</li>
            </ul>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 查询结果 -->
    <el-card v-if="queryResults" class="results-section">
      <template #header>
        <div class="results-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>查询结果</span>
          <div class="result-actions">
            <el-radio-group v-model="resultViewMode" size="small">
              <el-radio-button label="table">表格</el-radio-button>
              <el-radio-button label="chart">图表</el-radio-button>
              <el-radio-button label="json">JSON</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 查询信息 -->
      <div class="query-info">
        <el-descriptions :column="4" size="small" border>
          <el-descriptions-item label="查询语句">{{ queryForm.query }}</el-descriptions-item>
          <el-descriptions-item label="查询时间">{{ formatTime(queryResults.executionTime) }}</el-descriptions-item>
          <el-descriptions-item label="结果数量">{{ queryResults.data?.result?.length || 0 }}</el-descriptions-item>
          <el-descriptions-item label="查询耗时">{{ queryResults.duration }}ms</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 表格视图 -->
      <div v-if="resultViewMode === 'table'" class="table-view">
        <el-table 
          :data="formattedTableData" 
          stripe 
          border
          max-height="400"
          style="width: 100%"
        >
          <el-table-column 
            v-for="column in tableColumns" 
            :key="column.prop"
            :prop="column.prop" 
            :label="column.label"
            :width="column.width"
            show-overflow-tooltip
          />
        </el-table>
      </div>

      <!-- 图表视图 -->
      <div v-if="resultViewMode === 'chart'" class="chart-view">
        <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
      </div>

      <!-- JSON视图 -->
      <div v-if="resultViewMode === 'json'" class="json-view">
        <el-input
          :model-value="JSON.stringify(queryResults, null, 2)"
          type="textarea"
          :rows="20"
          readonly
        />
      </div>
    </el-card>

    <!-- 错误信息 -->
    <el-alert
      v-if="queryError"
      title="查询错误"
      type="error"
      :description="queryError"
      show-icon
      closable
      @close="queryError = ''"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { apiService } from '@/services/api'

// 响应式数据
const queryForm = reactive({
  query: '',
  queryType: 'query',
  time: '',
  start: '',
  end: '',
  step: '15s'
})

const queryLoading = ref(false)
const queryResults = ref(null)
const queryError = ref('')
const showExamples = ref(false)
const showHelp = ref(false)
const resultViewMode = ref('table')
const chartContainer = ref(null)
const chartInstance = ref(null)

// 查询示例
const queryExamples = [
  {
    title: '服务可用性',
    query: 'up',
    description: '查看所有服务的运行状态'
  },
  {
    title: 'CPU 使用率',
    query: '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
    description: '计算各实例的CPU使用率'
  },
  {
    title: '内存使用率',
    query: '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100',
    description: '计算内存使用率百分比'
  },
  {
    title: 'HTTP 请求速率',
    query: 'rate(http_requests_total[5m])',
    description: '计算HTTP请求的每秒速率'
  },
  {
    title: '磁盘使用率',
    query: '100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes)',
    description: '计算磁盘使用率'
  },
  {
    title: '网络流量',
    query: 'rate(node_network_receive_bytes_total[5m])',
    description: '网络接收流量速率'
  }
]

// 计算属性
const tableColumns = computed(() => {
  if (!queryResults.value?.data?.result?.length) return []
  
  const result = queryResults.value.data.result[0]
  const columns = [
    { prop: 'metric', label: '指标', width: 200 }
  ]
  
  if (result.metric) {
    Object.keys(result.metric).forEach(key => {
      columns.push({ prop: `labels.${key}`, label: key, width: 150 })
    })
  }
  
  if (result.value) {
    columns.push({ prop: 'value', label: '值', width: 150 })
    columns.push({ prop: 'timestamp', label: '时间戳', width: 180 })
  } else if (result.values) {
    columns.push({ prop: 'values', label: '时间序列数据', width: 300 })
  }
  
  return columns
})

const formattedTableData = computed(() => {
  if (!queryResults.value?.data?.result) return []
  
  return queryResults.value.data.result.map((item, index) => {
    const row = {
      metric: item.metric?.__name__ || `series_${index}`,
      labels: item.metric || {},
      timestamp: '',
      value: '',
      values: ''
    }
    
    if (item.value) {
      row.timestamp = formatTime(item.value[0] * 1000)
      row.value = parseFloat(item.value[1]).toFixed(4)
    } else if (item.values) {
      row.values = `${item.values.length} data points`
    }
    
    return row
  })
})

// 方法
const executeQuery = async () => {
  if (!queryForm.query.trim()) {
    ElMessage.warning('请输入查询语句')
    return
  }
  
  queryLoading.value = true
  queryError.value = ''
  
  try {
    const startTime = Date.now()
    const response = await apiService.executePromQLQuery({
      query: queryForm.query,
      queryType: queryForm.queryType,
      time: queryForm.time,
      start: queryForm.start,
      end: queryForm.end,
      step: queryForm.step
    })
    
    const endTime = Date.now()
    
    queryResults.value = {
      ...response,
      executionTime: new Date().toISOString(),
      duration: endTime - startTime
    }
    
    // 如果是图表视图，渲染图表
    if (resultViewMode.value === 'chart') {
      nextTick(() => {
        renderChart()
      })
    }
    
    ElMessage.success('查询执行成功')
  } catch (error) {
    queryError.value = error.message || '查询执行失败'
    ElMessage.error('查询执行失败')
  } finally {
    queryLoading.value = false
  }
}

const clearQuery = () => {
  queryForm.query = ''
  queryForm.time = ''
  queryForm.start = ''
  queryForm.end = ''
  queryResults.value = null
  queryError.value = ''
}

const useExample = (query: string) => {
  queryForm.query = query
  showExamples.value = false
}

const exportResults = () => {
  if (!queryResults.value) return
  
  const dataStr = JSON.stringify(queryResults.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `promql_results_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleString()
}

const renderChart = () => {
  if (!chartContainer.value || !queryResults.value?.data?.result) return
  
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  
  chartInstance.value = echarts.init(chartContainer.value)
  
  const series = queryResults.value.data.result.map((item, index) => {
    const name = item.metric?.__name__ || `Series ${index + 1}`
    
    if (item.values) {
      return {
        name,
        type: 'line',
        data: item.values.map(([timestamp, value]) => [
          timestamp * 1000,
          parseFloat(value)
        ])
      }
    } else if (item.value) {
      return {
        name,
        type: 'bar',
        data: [parseFloat(item.value[1])]
      }
    }
    
    return null
  }).filter(Boolean)
  
  const option = {
    title: {
      text: 'PromQL 查询结果',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      top: 30,
      type: 'scroll'
    },
    xAxis: {
      type: queryForm.queryType === 'query_range' ? 'time' : 'category',
      data: queryForm.queryType === 'query_range' ? undefined : series.map(s => s.name)
    },
    yAxis: {
      type: 'value'
    },
    series
  }
  
  chartInstance.value.setOption(option)
}

// 监听结果视图模式变化
watch(() => resultViewMode.value, (newMode) => {
  if (newMode === 'chart' && queryResults.value) {
    nextTick(() => {
      renderChart()
    })
  }
})

onMounted(() => {
  // 设置默认时间
  const now = new Date()
  queryForm.time = now.toISOString().slice(0, 19)
  queryForm.end = now.toISOString().slice(0, 19)
  queryForm.start = new Date(now.getTime() - 3600000).toISOString().slice(0, 19) // 1小时前
})
</script>

<style scoped>
.promql-query {
  margin-bottom: 20px;
}

.query-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.query-header span {
  margin-left: 8px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.query-input-section {
  margin-bottom: 20px;
}

.query-input {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.examples-section,
.help-section {
  margin: 20px 0;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.example-card {
  cursor: pointer;
  transition: all 0.3s;
}

.example-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.example-card h4 {
  margin: 0 0 8px 0;
  color: #409eff;
}

.example-card code {
  display: block;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  margin: 8px 0;
  font-size: 12px;
  word-break: break-all;
}

.example-card p {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 12px;
}

.help-content h4 {
  color: #409eff;
  margin: 16px 0 8px 0;
}

.help-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.help-content code {
  background: #f5f7fa;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 12px;
}

.results-section {
  margin-top: 20px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.results-header span {
  margin-left: 8px;
  font-weight: 600;
}

.query-info {
  margin-bottom: 20px;
}

.table-view,
.chart-view,
.json-view {
  margin-top: 16px;
}

.json-view .el-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
