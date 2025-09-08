/* 智能监控预警系统 - 全局类型定义 */

// ======== 基础类型 ========

/**
 * 通用响应类型
 */
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
  timestamp: number
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page: number
  size: number
  sort?: string
  order?: 'asc' | 'desc'
}

/**
 * 分页响应
 */
export interface PaginationResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  hasNext: boolean
  hasPrev: boolean
}

/**
 * 通用实体基类
 */
export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
  createdBy?: string
  updatedBy?: string
}

/**
 * 键值对类型
 */
export interface KeyValue<K = string, V = any> {
  key: K
  value: V
  label?: string
}

/**
 * 选项类型
 */
export interface Option<T = any> {
  label: string
  value: T
  disabled?: boolean
  children?: Option<T>[]
}

/**
 * 树形结构
 */
export interface TreeNode<T = any> {
  id: string
  label: string
  children?: TreeNode<T>[]
  data?: T
  disabled?: boolean
  expanded?: boolean
  selected?: boolean
}

// ======== 监控系统类型 ========

/**
 * 指标类型
 */
export interface Metric extends BaseEntity {
  name: string
  displayName: string
  description?: string
  unit: string
  type: 'counter' | 'gauge' | 'histogram' | 'summary'
  labels: Record<string, string>
  value: number
  timestamp: number
  source: string
  tags?: string[]
}

/**
 * 指标查询参数
 */
export interface MetricQuery {
  metrics: string[]
  start: string
  end: string
  step?: string
  filters?: Record<string, string>
  aggregation?: 'sum' | 'avg' | 'min' | 'max' | 'count'
  groupBy?: string[]
}

/**
 * 指标数据点
 */
export interface MetricDataPoint {
  timestamp: number
  value: number
  labels?: Record<string, string>
}

/**
 * 指标时间序列
 */
export interface MetricTimeSeries {
  metric: string
  labels: Record<string, string>
  values: MetricDataPoint[]
}

/**
 * 规则状态
 */
export type RuleStatus = 'active' | 'inactive' | 'pending' | 'error'

/**
 * 规则严重程度
 */
export type RuleSeverity = 'critical' | 'warning' | 'info'

/**
 * 监控规则
 */
export interface MonitorRule extends BaseEntity {
  name: string
  description?: string
  expression: string
  threshold: number
  operator: '>' | '<' | '>=' | '<=' | '==' | '!='
  duration: number
  severity: RuleSeverity
  status: RuleStatus
  labels: Record<string, string>
  annotations: Record<string, string>
  enabledChannels: string[]
  lastEvaluated?: string
  lastTriggered?: string
  triggerCount: number
}

/**
 * 告警状态
 */
export type AlertStatus = 'firing' | 'resolved' | 'pending' | 'silenced'

/**
 * 告警记录
 */
export interface Alert extends BaseEntity {
  ruleId: string
  ruleName: string
  status: AlertStatus
  severity: RuleSeverity
  message: string
  description?: string
  labels: Record<string, string>
  annotations: Record<string, string>
  startsAt: string
  endsAt?: string
  duration?: number
  value: number
  threshold: number
  silencedBy?: string
  silencedUntil?: string
  acknowledgedBy?: string
  acknowledgedAt?: string
}

/**
 * 通知渠道类型
 */
export type NotificationChannelType = 'email' | 'slack' | 'webhook' | 'sms' | 'dingtalk'

/**
 * 通知渠道状态
 */
export type NotificationChannelStatus = 'active' | 'inactive' | 'error' | 'testing'

/**
 * 通知渠道
 */
export interface NotificationChannel extends BaseEntity {
  name: string
  type: NotificationChannelType
  description?: string
  status: NotificationChannelStatus
  config: Record<string, any>
  isDefault: boolean
  tags?: string[]
  lastUsed?: string
  successCount: number
  errorCount: number
  testResult?: {
    success: boolean
    message: string
    testedAt: string
  }
}

/**
 * 通知记录状态
 */
export type NotificationStatus = 'pending' | 'sent' | 'failed' | 'retrying'

/**
 * 通知记录
 */
export interface NotificationRecord extends BaseEntity {
  alertId: string
  channelId: string
  channelName: string
  channelType: NotificationChannelType
  status: NotificationStatus
  subject: string
  content: string
  recipients: string[]
  sentAt?: string
  failedAt?: string
  retryCount: number
  maxRetries: number
  error?: string
  metadata?: Record<string, any>
}

// ======== AI 分析类型 ========

/**
 * 异常检测算法类型
 */
export type AnomalyDetectionAlgorithm = 'isolation_forest' | 'lstm' | 'prophet' | 'statistical'

/**
 * 异常状态
 */
export type AnomalyStatus = 'detected' | 'confirmed' | 'ignored' | 'resolved'

/**
 * 异常严重程度
 */
export type AnomalySeverity = 'low' | 'medium' | 'high' | 'critical'

/**
 * 异常记录
 */
export interface Anomaly extends BaseEntity {
  metricName: string
  algorithm: AnomalyDetectionAlgorithm
  status: AnomalyStatus
  severity: AnomalySeverity
  score: number
  threshold: number
  value: number
  expectedValue: number
  deviation: number
  confidence: number
  timestamp: string
  duration?: number
  labels: Record<string, string>
  context: Record<string, any>
  description?: string
  resolution?: string
  resolvedBy?: string
  resolvedAt?: string
}

/**
 * AI 分析结果
 */
export interface AnalysisResult {
  id: string
  type: 'anomaly' | 'prediction' | 'recommendation'
  algorithm: string
  confidence: number
  summary: string
  insights: string[]
  recommendations: string[]
  data: Record<string, any>
  metadata: Record<string, any>
  createdAt: string
  expiresAt?: string
}

/**
 * 预测结果
 */
export interface PredictionResult {
  metric: string
  timestamp: string
  predictedValue: number
  confidence: number
  upperBound: number
  lowerBound: number
  algorithm: string
  features: Record<string, number>
}

// ======== 系统管理类型 ========

/**
 * 用户角色
 */
export type UserRole = 'admin' | 'operator' | 'viewer' | 'guest'

/**
 * 用户状态
 */
export type UserStatus = 'active' | 'inactive' | 'locked' | 'pending'

/**
 * 用户信息
 */
export interface User extends BaseEntity {
  username: string
  email: string
  displayName: string
  avatar?: string
  role: UserRole
  status: UserStatus
  permissions: string[]
  lastLoginAt?: string
  loginCount: number
  preferences: Record<string, any>
  department?: string
  phone?: string
}

/**
 * 权限定义
 */
export interface Permission {
  code: string
  name: string
  description?: string
  category: string
  isSystem: boolean
}

/**
 * 系统配置类别
 */
export type ConfigCategory = 'system' | 'notification' | 'ai' | 'monitoring' | 'security'

/**
 * 系统配置
 */
export interface SystemConfig extends BaseEntity {
  key: string
  value: any
  category: ConfigCategory
  name: string
  description?: string
  type: 'string' | 'number' | 'boolean' | 'json' | 'array'
  isEncrypted: boolean
  isRequired: boolean
  defaultValue?: any
  validation?: {
    pattern?: string
    min?: number
    max?: number
    options?: string[]
  }
}

/**
 * 系统状态
 */
export interface SystemStatus {
  status: 'healthy' | 'warning' | 'critical' | 'unknown'
  uptime: number
  version: string
  environment: string
  services: ServiceStatus[]
  resources: ResourceUsage
  lastCheck: string
}

/**
 * 服务状态
 */
export interface ServiceStatus {
  name: string
  status: 'running' | 'stopped' | 'error' | 'starting' | 'stopping'
  uptime: number
  version?: string
  endpoint?: string
  lastCheck: string
  error?: string
  metrics?: Record<string, number>
}

/**
 * 资源使用情况
 */
export interface ResourceUsage {
  cpu: {
    usage: number
    cores: number
    load: number[]
  }
  memory: {
    used: number
    total: number
    usage: number
  }
  disk: {
    used: number
    total: number
    usage: number
    iops?: number
  }
  network: {
    bytesIn: number
    bytesOut: number
    packetsIn: number
    packetsOut: number
  }
}

// ======== 图表和可视化类型 ========

/**
 * 图表类型
 */
export type ChartType = 'line' | 'bar' | 'pie' | 'gauge' | 'scatter' | 'heatmap' | 'graph'

/**
 * 图表主题
 */
export type ChartTheme = 'light' | 'dark' | 'monitoring-light' | 'monitoring-dark'

/**
 * 图表配置
 */
export interface ChartConfig {
  theme?: ChartTheme
  responsive?: boolean
  animation?: boolean
  large?: boolean
  dataZoom?: boolean
  toolbox?: boolean
  legend?: boolean
  grid?: {
    left?: string | number
    right?: string | number
    top?: string | number
    bottom?: string | number
  }
  colors?: string[]
}

/**
 * 图表数据系列
 */
export interface ChartSeries {
  name: string
  type: ChartType
  data: any[]
  color?: string
  lineStyle?: Record<string, any>
  areaStyle?: Record<string, any>
  itemStyle?: Record<string, any>
  stack?: string
  smooth?: boolean
  symbol?: string
  symbolSize?: number
  [key: string]: any
}

/**
 * 图表数据
 */
export interface ChartData {
  xAxis?: any[]
  yAxis?: any[]
  series: ChartSeries[]
  legend?: string[]
  categories?: string[]
}

/**
 * 仪表盘布局
 */
export type DashboardLayout = '1x1' | '2x1' | '2x2' | '3x2' | '4x2' | 'auto'

/**
 * 仪表盘小部件
 */
export interface DashboardWidget {
  id: string
  title: string
  type: 'chart' | 'metric' | 'table' | 'text' | 'image'
  chartType?: ChartType
  span: number
  height: string
  config: Record<string, any>
  data?: any
  refreshInterval?: number
  visible: boolean
  order: number
}

/**
 * 仪表盘配置
 */
export interface Dashboard extends BaseEntity {
  name: string
  description?: string
  layout: DashboardLayout
  widgets: DashboardWidget[]
  isPublic: boolean
  tags?: string[]
  autoRefresh: boolean
  refreshInterval: number
  theme?: ChartTheme
}

// ======== 事件和日志类型 ========

/**
 * 事件类型
 */
export type EventType = 'alert' | 'anomaly' | 'system' | 'user' | 'config' | 'notification'

/**
 * 事件严重程度
 */
export type EventSeverity = 'debug' | 'info' | 'warning' | 'error' | 'critical'

/**
 * 系统事件
 */
export interface SystemEvent extends BaseEntity {
  type: EventType
  severity: EventSeverity
  source: string
  title: string
  message: string
  details?: Record<string, any>
  userId?: string
  sessionId?: string
  ipAddress?: string
  userAgent?: string
  tags?: string[]
  acknowledged?: boolean
  acknowledgedBy?: string
  acknowledgedAt?: string
}

/**
 * 操作日志
 */
export interface OperationLog extends BaseEntity {
  userId: string
  username: string
  action: string
  resource: string
  resourceId?: string
  method: string
  path: string
  params?: Record<string, any>
  result: 'success' | 'failure' | 'error'
  statusCode: number
  duration: number
  ipAddress: string
  userAgent: string
  error?: string
}

// ======== 工具类型 ========

/**
 * 深度可选类型
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

/**
 * 深度必需类型
 */
export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P]
}

/**
 * 提取对象值类型
 */
export type ValueOf<T> = T[keyof T]

/**
 * 创建联合类型
 */
export type UnionOf<T extends readonly unknown[]> = T[number]

/**
 * 排除 null 和 undefined
 */
export type NonNullable<T> = T extends null | undefined ? never : T

/**
 * 条件类型
 */
export type If<C extends boolean, T, F> = C extends true ? T : F

/**
 * 异步函数类型
 */
export type AsyncFunction<T extends any[] = any[], R = any> = (...args: T) => Promise<R>

/**
 * 回调函数类型
 */
export type CallbackFunction<T extends any[] = any[], R = void> = (...args: T) => R

/**
 * 事件处理器类型
 */
export type EventHandler<T = Event> = (event: T) => void

/**
 * 时间范围
 */
export interface TimeRange {
  start: string | Date
  end: string | Date
  label?: string
}

/**
 * 快速时间范围选项
 */
export type QuickTimeRange = 
  | 'last_5m'
  | 'last_15m'
  | 'last_30m'
  | 'last_1h'
  | 'last_3h'
  | 'last_6h'
  | 'last_12h'
  | 'last_1d'
  | 'last_3d'
  | 'last_7d'
  | 'last_30d'
  | 'custom'

/**
 * 登录凭据
 */
export interface LoginCredentials {
  username: string
  password: string
  rememberMe?: boolean
  captcha?: string
}

/**
 * 通知项
 */
export interface NotificationItem {
  id: string
  title: string
  message: string
  type: 'success' | 'warning' | 'error' | 'info'
  timestamp: string
  read: boolean
  hidden: boolean
  priority: 'low' | 'medium' | 'high'
  category?: string
  actions?: Array<{
    label: string
    action: string
    type?: 'primary' | 'success' | 'warning' | 'danger'
  }>
  data?: Record<string, any>
}

/**
 * 状态类型联合
 */
export type Status = 
  | 'pending'
  | 'running'
  | 'success'
  | 'failure'
  | 'error'
  | 'cancelled'
  | 'timeout'

// ======== 模块声明 ========

declare global {
  interface Window {
    $errorHandler?: any
    $notification?: any
    __APP_VERSION__?: string
    __BUILD_TIME__?: string
    __GIT_HASH__?: string
  }
}

export {}