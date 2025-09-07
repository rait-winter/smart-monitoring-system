/* API 服务类型定义 */

import type {
  ApiResponse,
  PaginationParams,
  PaginationResponse,
  Metric,
  MetricQuery,
  MetricTimeSeries,
  MonitorRule,
  Alert,
  NotificationChannel,
  NotificationRecord,
  Anomaly,
  AnalysisResult,
  User,
  SystemConfig,
  SystemStatus,
  Dashboard,
  SystemEvent,
  OperationLog
} from './global'

// ======== API 基础类型 ========

/**
 * HTTP 请求方法
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

/**
 * 请求配置
 */
export interface RequestConfig {
  method?: HttpMethod
  headers?: Record<string, string>
  params?: Record<string, any>
  data?: any
  timeout?: number
  retries?: number
  retryDelay?: number
  cache?: boolean
  cacheKey?: string
  skipErrorHandler?: boolean
  skipAuth?: boolean
}

/**
 * 响应配置
 */
export interface ResponseConfig<T = any> {
  data: ApiResponse<T>
  status: number
  statusText: string
  headers: Record<string, string>
  config: RequestConfig
  request?: any
}

/**
 * API 错误
 */
export interface ApiError {
  code: number
  message: string
  detail?: string
  field?: string
  type?: string
  requestId?: string
}

// ======== 认证相关 ========

/**
 * 登录请求
 */
export interface LoginRequest {
  username: string
  password: string
  remember?: boolean
  captcha?: string
  captchaId?: string
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: string
  refreshToken: string
  user: User
  permissions: string[]
  expiresIn: number
}

/**
 * 刷新令牌请求
 */
export interface RefreshTokenRequest {
  refreshToken: string
}

/**
 * 修改密码请求
 */
export interface ChangePasswordRequest {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

// ======== 指标相关 ========

/**
 * 指标列表查询参数
 */
export interface MetricListParams extends PaginationParams {
  search?: string
  type?: string
  source?: string
  tags?: string[]
  labels?: Record<string, string>
}

/**
 * 指标查询请求
 */
export interface MetricQueryRequest extends MetricQuery {
  format?: 'json' | 'csv' | 'prometheus'
  timeout?: number
}

/**
 * 指标查询响应
 */
export interface MetricQueryResponse {
  resultType: 'matrix' | 'vector' | 'scalar' | 'string'
  result: MetricTimeSeries[]
  stats?: {
    totalSeries: number
    totalSamples: number
    executionTime: number
  }
}

/**
 * 指标统计
 */
export interface MetricStats {
  totalMetrics: number
  activeMetrics: number
  metricsByType: Record<string, number>
  metricsBySource: Record<string, number>
  sampleRate: number
  retention: string
}

// ======== 规则相关 ========

/**
 * 规则列表查询参数
 */
export interface RuleListParams extends PaginationParams {
  search?: string
  status?: string
  severity?: string
  labels?: Record<string, string>
}

/**
 * 创建规则请求
 */
export interface CreateRuleRequest {
  name: string
  description?: string
  expression: string
  threshold: number
  operator: string
  duration: number
  severity: string
  labels?: Record<string, string>
  annotations?: Record<string, string>
  enabledChannels?: string[]
}

/**
 * 更新规则请求
 */
export interface UpdateRuleRequest extends Partial<CreateRuleRequest> {
  id: string
}

/**
 * 规则验证请求
 */
export interface ValidateRuleRequest {
  expression: string
  duration?: number
}

/**
 * 规则验证响应
 */
export interface ValidateRuleResponse {
  valid: boolean
  error?: string
  suggestion?: string
  estimatedCost?: number
}

/**
 * 规则执行请求
 */
export interface ExecuteRuleRequest {
  ruleId: string
  startTime?: string
  endTime?: string
}

/**
 * 规则执行响应
 */
export interface ExecuteRuleResponse {
  triggered: boolean
  value: number
  threshold: number
  evaluationTime: string
  samples: number
  duration: number
}

// ======== 告警相关 ========

/**
 * 告警列表查询参数
 */
export interface AlertListParams extends PaginationParams {
  search?: string
  status?: string
  severity?: string
  ruleId?: string
  startTime?: string
  endTime?: string
  labels?: Record<string, string>
}

/**
 * 告警统计
 */
export interface AlertStats {
  total: number
  firing: number
  resolved: number
  pending: number
  silenced: number
  byStatus: Record<string, number>
  bySeverity: Record<string, number>
  byRule: Record<string, number>
  trends: {
    period: string
    data: Array<{
      timestamp: string
      firing: number
      resolved: number
    }>
  }
}

/**
 * 确认告警请求
 */
export interface AcknowledgeAlertRequest {
  alertIds: string[]
  comment?: string
}

/**
 * 静默告警请求
 */
export interface SilenceAlertRequest {
  alertIds: string[]
  duration: number
  reason?: string
}

// ======== 通知相关 ========

/**
 * 通知渠道列表查询参数
 */
export interface ChannelListParams extends PaginationParams {
  search?: string
  type?: string
  status?: string
  tags?: string[]
}

/**
 * 创建通知渠道请求
 */
export interface CreateChannelRequest {
  name: string
  type: string
  description?: string
  config: Record<string, any>
  isDefault?: boolean
  tags?: string[]
}

/**
 * 更新通知渠道请求
 */
export interface UpdateChannelRequest extends Partial<CreateChannelRequest> {
  id: string
}

/**
 * 测试通知渠道请求
 */
export interface TestChannelRequest {
  channelId: string
  message?: string
}

/**
 * 测试通知渠道响应
 */
export interface TestChannelResponse {
  success: boolean
  message: string
  duration: number
  details?: Record<string, any>
}

/**
 * 通知记录列表查询参数
 */
export interface NotificationListParams extends PaginationParams {
  search?: string
  status?: string
  channelId?: string
  channelType?: string
  alertId?: string
  startTime?: string
  endTime?: string
}

/**
 * 通知统计
 */
export interface NotificationStats {
  total: number
  sent: number
  failed: number
  pending: number
  byStatus: Record<string, number>
  byChannel: Record<string, number>
  successRate: number
  avgDeliveryTime: number
}

// ======== AI 分析相关 ========

/**
 * 异常检测请求
 */
export interface AnomalyDetectionRequest {
  metrics: string[]
  algorithm?: string
  startTime: string
  endTime: string
  threshold?: number
  parameters?: Record<string, any>
}

/**
 * 异常检测响应
 */
export interface AnomalyDetectionResponse {
  anomalies: Anomaly[]
  totalCount: number
  detectionTime: number
  algorithm: string
  parameters: Record<string, any>
  confidence: number
}

/**
 * AI 分析请求
 */
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

/**
 * AI 分析响应
 */
export interface AnalysisResponse extends AnalysisResult {
  executionTime: number
  resourceUsage?: {
    cpu: number
    memory: number
    duration: number
  }
}

/**
 * 预测请求
 */
export interface PredictionRequest {
  metric: string
  horizon: number
  interval?: string
  algorithm?: string
  parameters?: Record<string, any>
}

/**
 * 预测响应
 */
export interface PredictionResponse {
  predictions: Array<{
    timestamp: string
    value: number
    confidence: number
    upperBound: number
    lowerBound: number
  }>
  accuracy?: number
  algorithm: string
  parameters: Record<string, any>
}

// ======== 系统管理相关 ========

/**
 * 用户列表查询参数
 */
export interface UserListParams extends PaginationParams {
  search?: string
  role?: string
  status?: string
  department?: string
}

/**
 * 创建用户请求
 */
export interface CreateUserRequest {
  username: string
  email: string
  displayName: string
  password: string
  role: string
  department?: string
  phone?: string
}

/**
 * 更新用户请求
 */
export interface UpdateUserRequest extends Partial<Omit<CreateUserRequest, 'password'>> {
  id: string
}

/**
 * 用户配置更新请求
 */
export interface UpdateUserPreferencesRequest {
  theme?: string
  language?: string
  timezone?: string
  notifications?: Record<string, boolean>
  dashboard?: Record<string, any>
}

/**
 * 系统配置列表查询参数
 */
export interface ConfigListParams extends PaginationParams {
  category?: string
  search?: string
}

/**
 * 更新系统配置请求
 */
export interface UpdateConfigRequest {
  key: string
  value: any
  category?: string
}

/**
 * 批量更新系统配置请求
 */
export interface BatchUpdateConfigRequest {
  configs: Array<{
    key: string
    value: any
  }>
}

/**
 * 系统状态查询参数
 */
export interface SystemStatusParams {
  includeServices?: boolean
  includeResources?: boolean
  includeMetrics?: boolean
}

/**
 * 服务操作请求
 */
export interface ServiceOperationRequest {
  serviceName: string
  operation: 'start' | 'stop' | 'restart' | 'reload'
}

// ======== 仪表盘相关 ========

/**
 * 仪表盘列表查询参数
 */
export interface DashboardListParams extends PaginationParams {
  search?: string
  tags?: string[]
  isPublic?: boolean
  createdBy?: string
}

/**
 * 创建仪表盘请求
 */
export interface CreateDashboardRequest {
  name: string
  description?: string
  layout?: string
  widgets?: any[]
  isPublic?: boolean
  tags?: string[]
  theme?: string
}

/**
 * 更新仪表盘请求
 */
export interface UpdateDashboardRequest extends Partial<CreateDashboardRequest> {
  id: string
}

/**
 * 复制仪表盘请求
 */
export interface CloneDashboardRequest {
  dashboardId: string
  name: string
  description?: string
}

/**
 * 导出仪表盘请求
 */
export interface ExportDashboardRequest {
  dashboardId: string
  format: 'json' | 'pdf' | 'png'
  options?: Record<string, any>
}

// ======== 事件和日志相关 ========

/**
 * 事件列表查询参数
 */
export interface EventListParams extends PaginationParams {
  search?: string
  type?: string
  severity?: string
  source?: string
  userId?: string
  startTime?: string
  endTime?: string
  acknowledged?: boolean
}

/**
 * 操作日志列表查询参数
 */
export interface LogListParams extends PaginationParams {
  search?: string
  userId?: string
  action?: string
  resource?: string
  result?: string
  startTime?: string
  endTime?: string
}

/**
 * 日志统计
 */
export interface LogStats {
  total: number
  success: number
  failure: number
  error: number
  byUser: Record<string, number>
  byAction: Record<string, number>
  byResource: Record<string, number>
  trends: Array<{
    timestamp: string
    count: number
    success: number
    failure: number
  }>
}

// ======== 导出相关 ========

/**
 * 导出请求
 */
export interface ExportRequest {
  type: 'metrics' | 'alerts' | 'notifications' | 'logs' | 'dashboard'
  format: 'csv' | 'excel' | 'json' | 'pdf'
  filters?: Record<string, any>
  timeRange?: {
    start: string
    end: string
  }
  options?: Record<string, any>
}

/**
 * 导出响应
 */
export interface ExportResponse {
  taskId: string
  downloadUrl?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  error?: string
  expiresAt?: string
}

/**
 * 导入请求
 */
export interface ImportRequest {
  type: 'rules' | 'channels' | 'dashboards' | 'configs'
  format: 'csv' | 'excel' | 'json'
  file: File
  options?: {
    skipErrors?: boolean
    overwrite?: boolean
    dryRun?: boolean
  }
}

/**
 * 导入响应
 */
export interface ImportResponse {
  taskId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  summary?: {
    total: number
    success: number
    failed: number
    skipped: number
  }
  errors?: Array<{
    line: number
    message: string
    data?: any
  }>
}

// ======== 实时数据相关 ========

/**
 * WebSocket 消息类型
 */
export type WebSocketMessageType = 
  | 'metrics'
  | 'alerts'
  | 'notifications'
  | 'system_status'
  | 'user_activity'
  | 'heartbeat'

/**
 * WebSocket 消息
 */
export interface WebSocketMessage<T = any> {
  type: WebSocketMessageType
  data: T
  timestamp: string
  id?: string
}

/**
 * WebSocket 连接配置
 */
export interface WebSocketConfig {
  url: string
  protocols?: string[]
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
  timeout?: number
}

/**
 * 实时指标数据
 */
export interface RealtimeMetricData {
  metric: string
  value: number
  timestamp: string
  labels: Record<string, string>
  change?: number
  trend?: 'up' | 'down' | 'stable'
}

/**
 * 实时告警数据
 */
export interface RealtimeAlertData {
  alert: Alert
  action: 'firing' | 'resolved' | 'updated'
  timestamp: string
}

/**
 * 实时系统状态数据
 */
export interface RealtimeSystemData {
  status: SystemStatus
  changes: Array<{
    service: string
    oldStatus: string
    newStatus: string
    timestamp: string
  }>
}

export {}