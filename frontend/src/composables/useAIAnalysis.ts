import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiService } from '@/services/api'

export interface AnalysisResult {
  id: string
  timestamp: string
  summary: string
  insights: string[]
  recommendations: string[]
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  rawData: any
}

export interface AnalysisRequest {
  type: 'metrics' | 'anomalies' | 'logs' | 'full'
  timeRange: {
    start: string
    end: string
  }
  targets?: string[]
  includeMetrics?: string[]
  parameters?: Record<string, any>
}

export function useAIAnalysis() {
  const isAnalyzing = ref(false)
  const analysisHistory = ref<AnalysisResult[]>([])
  const currentAnalysis = ref<AnalysisResult | null>(null)

  // 执行AI分析
  const analyzeData = async (request: AnalysisRequest): Promise<AnalysisResult> => {
    try {
      isAnalyzing.value = true
      
      console.log('🤖 开始AI分析:', request)
      
      // 调用后端AI分析接口
      const result = await apiService.analyzeWithAI(request)
      
      const analysis: AnalysisResult = {
        id: result.id || Date.now().toString(),
        timestamp: result.timestamp || new Date().toISOString(),
        summary: result.summary || '分析完成',
        insights: result.insights || [],
        recommendations: result.recommendations || [],
        severity: result.severity || 'medium',
        confidence: result.confidence || 0.8,
        rawData: result.rawData || request
      }
      
      // 保存到历史记录
      analysisHistory.value.unshift(analysis)
      currentAnalysis.value = analysis
      
      console.log('✅ AI分析完成:', analysis)
      ElMessage.success('AI分析完成！')
      
      return analysis
    } catch (error) {
      console.error('❌ AI分析失败:', error)
      ElMessage.error('AI分析失败，请检查Ollama服务是否正常运行')
      throw error
    } finally {
      isAnalyzing.value = false
    }
  }

  // 快速分析当前指标
  const quickAnalyzeMetrics = async (metrics: any[]) => {
    const request: AnalysisRequest = {
      type: 'metrics',
      timeRange: {
        start: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      parameters: {
        metrics: metrics,
        analysisType: 'quick'
      }
    }
    
    return analyzeData(request)
  }

  // 分析异常数据
  const analyzeAnomalies = async (anomalies: any[]) => {
    const request: AnalysisRequest = {
      type: 'anomalies',
      timeRange: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      parameters: {
        anomalies: anomalies,
        analysisType: 'detailed'
      }
    }
    
    return analyzeData(request)
  }

  // 全面系统分析
  const fullSystemAnalysis = async (targets: string[] = []) => {
    const request: AnalysisRequest = {
      type: 'full',
      timeRange: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      targets: targets,
      parameters: {
        analysisType: 'comprehensive',
        includeRecommendations: true,
        includeTrends: true
      }
    }
    
    return analyzeData(request)
  }

  // 生成分析报告
  const generateReport = (analysis: AnalysisResult) => {
    const report = {
      title: `系统巡检报告 - ${new Date(analysis.timestamp).toLocaleString()}`,
      summary: analysis.summary,
      severity: analysis.severity,
      confidence: `${(analysis.confidence * 100).toFixed(1)}%`,
      insights: analysis.insights,
      recommendations: analysis.recommendations,
      timestamp: analysis.timestamp
    }
    
    return report
  }

  // 导出分析结果
  const exportAnalysis = async (analysis: AnalysisResult, format: 'json' | 'pdf' | 'excel' = 'json') => {
    try {
      const report = generateReport(analysis)
      
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(report, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `analysis_${analysis.id}.json`
        a.click()
        URL.revokeObjectURL(url)
      } else {
        // 调用后端导出服务
        const blob = await apiService.exportData('analysis', {
          id: analysis.id,
          format: format
        })
        
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `analysis_${analysis.id}.${format}`
        a.click()
        URL.revokeObjectURL(url)
      }
      
      ElMessage.success('分析结果导出成功！')
    } catch (error) {
      console.error('导出分析结果失败:', error)
      ElMessage.error('导出失败，请稍后重试')
    }
  }

  // 清理历史记录
  const clearHistory = () => {
    analysisHistory.value = []
    currentAnalysis.value = null
  }

  return {
    // 状态
    isAnalyzing,
    analysisHistory,
    currentAnalysis,
    
    // 方法
    analyzeData,
    quickAnalyzeMetrics,
    analyzeAnomalies,
    fullSystemAnalysis,
    generateReport,
    exportAnalysis,
    clearHistory
  }
}