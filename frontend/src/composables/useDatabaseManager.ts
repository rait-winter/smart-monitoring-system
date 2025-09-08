import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'

// 数据库配置接口
export interface DatabaseConfig {
  host: string
  port: number
  database: string
  username: string
  password: string
  ssl: boolean
  connectionTimeout: number
  queryTimeout: number
}

// 数据表结构
export interface TableSchema {
  name: string
  columns: Column[]
  indexes: Index[]
  primaryKey: string[]
}

export interface Column {
  name: string
  type: string
  nullable: boolean
  defaultValue?: any
  comment?: string
}

export interface Index {
  name: string
  columns: string[]
  unique: boolean
}

// 数据库连接状态
export interface DatabaseStatus {
  connected: boolean
  version: string
  uptime: number
  totalConnections: number
  activeConnections: number
  dbSize: string
}

// 数据导出选项
export interface ExportOptions {
  format: 'json' | 'csv' | 'excel' | 'sql'
  includeSchema: boolean
  dateRange?: {
    start: string
    end: string
  }
  filters?: Record<string, any>
  compression?: boolean
}

export function useDatabaseManager() {
  // 响应式数据
  const isConnected = ref(false)
  const connectionLoading = ref(false)
  const operationLoading = ref(false)
  
  // 数据库配置
  const dbConfig = reactive<DatabaseConfig>({
    host: 'localhost',
    port: 5432,
    database: 'monitoring',
    username: 'postgres',
    password: '',
    ssl: false,
    connectionTimeout: 30000,
    queryTimeout: 60000
  })
  
  // 数据库状态
  const dbStatus = ref<DatabaseStatus>({
    connected: false,
    version: '',
    uptime: 0,
    totalConnections: 0,
    activeConnections: 0,
    dbSize: '0 MB'
  })
  
  // 表结构
  const tableSchemas = ref<TableSchema[]>([
    {
      name: 'inspections',
      columns: [
        { name: 'id', type: 'BIGSERIAL', nullable: false, comment: '主键ID' },
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, comment: '巡检时间' },
        { name: 'type', type: 'VARCHAR(50)', nullable: false, comment: '巡检类型' },
        { name: 'servers', type: 'JSONB', nullable: false, comment: '巡检服务器列表' },
        { name: 'status', type: 'VARCHAR(20)', nullable: false, comment: '巡检状态' },
        { name: 'duration', type: 'INTEGER', nullable: true, comment: '巡检耗时(秒)' },
        { name: 'results', type: 'JSONB', nullable: true, comment: '巡检结果' },
        { name: 'ai_analysis', type: 'BOOLEAN', nullable: false, defaultValue: false, comment: '是否包含AI分析' },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false, defaultValue: 'NOW()', comment: '创建时间' },
        { name: 'updated_at', type: 'TIMESTAMP', nullable: false, defaultValue: 'NOW()', comment: '更新时间' }
      ],
      indexes: [
        { name: 'idx_inspections_timestamp', columns: ['timestamp'], unique: false },
        { name: 'idx_inspections_type', columns: ['type'], unique: false },
        { name: 'idx_inspections_status', columns: ['status'], unique: false }
      ],
      primaryKey: ['id']
    },
    {
      name: 'metrics',
      columns: [
        { name: 'id', type: 'BIGSERIAL', nullable: false, comment: '主键ID' },
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, comment: '指标时间' },
        { name: 'server_id', type: 'VARCHAR(100)', nullable: false, comment: '服务器ID' },
        { name: 'metric_name', type: 'VARCHAR(100)', nullable: false, comment: '指标名称' },
        { name: 'metric_value', type: 'DOUBLE PRECISION', nullable: false, comment: '指标值' },
        { name: 'unit', type: 'VARCHAR(20)', nullable: true, comment: '单位' },
        { name: 'tags', type: 'JSONB', nullable: true, comment: '标签' },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false, defaultValue: 'NOW()', comment: '创建时间' }
      ],
      indexes: [
        { name: 'idx_metrics_timestamp', columns: ['timestamp'], unique: false },
        { name: 'idx_metrics_server_id', columns: ['server_id'], unique: false },
        { name: 'idx_metrics_name', columns: ['metric_name'], unique: false },
        { name: 'idx_metrics_compound', columns: ['server_id', 'metric_name', 'timestamp'], unique: false }
      ],
      primaryKey: ['id']
    },
    {
      name: 'analysis_results',
      columns: [
        { name: 'id', type: 'BIGSERIAL', nullable: false, comment: '主键ID' },
        { name: 'inspection_id', type: 'BIGINT', nullable: true, comment: '关联巡检ID' },
        { name: 'analysis_type', type: 'VARCHAR(50)', nullable: false, comment: '分析类型' },
        { name: 'summary', type: 'TEXT', nullable: false, comment: '分析摘要' },
        { name: 'insights', type: 'JSONB', nullable: false, comment: '洞察结果' },
        { name: 'recommendations', type: 'JSONB', nullable: false, comment: '优化建议' },
        { name: 'severity', type: 'VARCHAR(20)', nullable: false, comment: '严重程度' },
        { name: 'confidence', type: 'DOUBLE PRECISION', nullable: false, comment: '置信度' },
        { name: 'model_version', type: 'VARCHAR(50)', nullable: true, comment: 'AI模型版本' },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false, defaultValue: 'NOW()', comment: '创建时间' }
      ],
      indexes: [
        { name: 'idx_analysis_inspection_id', columns: ['inspection_id'], unique: false },
        { name: 'idx_analysis_type', columns: ['analysis_type'], unique: false },
        { name: 'idx_analysis_severity', columns: ['severity'], unique: false },
        { name: 'idx_analysis_created_at', columns: ['created_at'], unique: false }
      ],
      primaryKey: ['id']
    }
  ])
  
  // 数据库操作方法
  
  /**
   * 测试数据库连接
   */
  const testConnection = async (): Promise<boolean> => {
    connectionLoading.value = true
    try {
      const result = await apiService.checkDatabaseHealth()
      
      if (result.success) {
        isConnected.value = true
        dbStatus.value = {
          connected: true,
          version: result.data.version || 'PostgreSQL 15.x',
          uptime: result.data.uptime || 0,
          totalConnections: result.data.totalConnections || 0,
          activeConnections: result.data.activeConnections || 0,
          dbSize: result.data.dbSize || '0 MB'
        }
        ElMessage.success('数据库连接成功！')
        return true
      } else {
        isConnected.value = false
        ElMessage.error('数据库连接失败：' + (result.message || '未知错误'))
        return false
      }
    } catch (error) {
      console.error('数据库连接测试失败:', error)
      isConnected.value = false
      ElMessage.error('数据库连接测试失败')
      return false
    } finally {
      connectionLoading.value = false
    }
  }
  
  /**
   * 保存巡检数据
   */
  const saveInspectionData = async (inspectionData: any): Promise<boolean> => {
    try {
      operationLoading.value = true
      
      const data = {
        timestamp: inspectionData.timestamp || new Date().toISOString(),
        type: inspectionData.type,
        servers: JSON.stringify(inspectionData.servers),
        status: inspectionData.status,
        duration: inspectionData.duration,
        results: JSON.stringify(inspectionData.results || {}),
        ai_analysis: inspectionData.aiAnalysis || false
      }
      
      const result = await apiService.saveInspectionData(data)
      
      if (result.success) {
        ElMessage.success('巡检数据保存成功！')
        return true
      } else {
        ElMessage.error('保存失败：' + (result.message || '未知错误'))
        return false
      }
    } catch (error) {
      console.error('保存巡检数据失败:', error)
      ElMessage.error('保存巡检数据失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }
  
  /**
   * 保存指标数据
   */
  const saveMetricsData = async (metricsData: any[]): Promise<boolean> => {
    try {
      operationLoading.value = true
      
      const batchData = metricsData.map(metric => ({
        timestamp: metric.timestamp || new Date().toISOString(),
        server_id: metric.serverId,
        metric_name: metric.name,
        metric_value: metric.value,
        unit: metric.unit || null,
        tags: JSON.stringify(metric.tags || {})
      }))
      
      const result = await apiService.saveMetricsData({ metrics: batchData })
      
      if (result.success) {
        ElMessage.success(`成功保存 ${batchData.length} 条指标数据！`)
        return true
      } else {
        ElMessage.error('保存失败：' + (result.message || '未知错误'))
        return false
      }
    } catch (error) {
      console.error('保存指标数据失败:', error)
      ElMessage.error('保存指标数据失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }
  
  /**
   * 保存AI分析结果
   */
  const saveAnalysisResult = async (analysisData: any): Promise<boolean> => {
    try {
      operationLoading.value = true
      
      const data = {
        inspection_id: analysisData.inspectionId || null,
        analysis_type: analysisData.type || 'general',
        summary: analysisData.summary,
        insights: JSON.stringify(analysisData.insights || []),
        recommendations: JSON.stringify(analysisData.recommendations || []),
        severity: analysisData.severity || 'medium',
        confidence: analysisData.confidence || 0.5,
        model_version: analysisData.modelVersion || 'unknown'
      }
      
      const result = await apiService.saveAnalysisResult(data)
      
      if (result.success) {
        ElMessage.success('AI分析结果保存成功！')
        return true
      } else {
        ElMessage.error('保存失败：' + (result.message || '未知错误'))
        return false
      }
    } catch (error) {
      console.error('保存AI分析结果失败:', error)
      ElMessage.error('保存AI分析结果失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }
  
  /**
   * 导出数据
   */
  const exportData = async (type: string, options: ExportOptions): Promise<boolean> => {
    try {
      operationLoading.value = true
      
      const params = {
        format: options.format,
        includeSchema: options.includeSchema,
        ...options.filters,
        ...options.dateRange
      }
      
      const blob = await apiService.exportDatabaseData(type, params)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().slice(0, 10)
      const extension = options.format === 'excel' ? 'xlsx' : options.format
      link.download = `${type}_export_${timestamp}.${extension}`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('数据导出成功！')
      return true
    } catch (error) {
      console.error('导出数据失败:', error)
      ElMessage.error('导出数据失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }
  
  /**
   * 备份数据库
   */
  const backupDatabase = async (): Promise<boolean> => {
    try {
      operationLoading.value = true
      
      const result = await apiService.backupDatabase()
      
      if (result.success) {
        ElMessage.success('数据库备份成功！')
        return true
      } else {
        ElMessage.error('备份失败：' + (result.message || '未知错误'))
        return false
      }
    } catch (error) {
      console.error('数据库备份失败:', error)
      ElMessage.error('数据库备份失败')
      return false
    } finally {
      operationLoading.value = false
    }
  }
  
  /**
   * 查询巡检数据
   */
  const queryInspectionData = async (params: any = {}) => {
    try {
      const result = await apiService.getInspectionData(params)
      return result.data || []
    } catch (error) {
      console.error('查询巡检数据失败:', error)
      ElMessage.error('查询巡检数据失败')
      return []
    }
  }
  
  /**
   * 查询指标数据
   */
  const queryMetricsData = async (params: any = {}) => {
    try {
      const result = await apiService.getMetricsData(params)
      return result.data || []
    } catch (error) {
      console.error('查询指标数据失败:', error)
      ElMessage.error('查询指标数据失败')
      return []
    }
  }
  
  /**
   * 查询AI分析结果
   */
  const queryAnalysisResults = async (params: any = {}) => {
    try {
      const result = await apiService.getAnalysisResults(params)
      return result.data || []
    } catch (error) {
      console.error('查询AI分析结果失败:', error)
      ElMessage.error('查询AI分析结果失败')
      return []
    }
  }
  
  /**
   * 获取数据库统计信息
   */
  const getDatabaseStats = () => {
    return {
      tables: tableSchemas.value.length,
      totalColumns: tableSchemas.value.reduce((sum, table) => sum + table.columns.length, 0),
      totalIndexes: tableSchemas.value.reduce((sum, table) => sum + table.indexes.length, 0),
      status: dbStatus.value
    }
  }
  
  return {
    // 状态
    isConnected,
    connectionLoading,
    operationLoading,
    dbConfig,
    dbStatus,
    tableSchemas,
    
    // 方法
    testConnection,
    saveInspectionData,
    saveMetricsData,
    saveAnalysisResult,
    exportData,
    backupDatabase,
    queryInspectionData,
    queryMetricsData,
    queryAnalysisResults,
    getDatabaseStats
  }
}