<template>
  <div class="rules">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><Setting /></el-icon>
          规则配置
        </h1>
        <p class="page-description">
          配置和管理监控告警规则，支持复杂条件组合和多种通知方式
        </p>
      </div>
      
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="showCreateRule = true"
        >
          创建规则
        </el-button>
        <el-button 
          type="success" 
          :icon="Upload" 
          @click="importRules"
        >
          导入规则
        </el-button>
        <el-button 
          :icon="Download" 
          @click="exportRules"
        >
          导出规则
        </el-button>
      </div>
    </div>

    <!-- 规则统计 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="总规则数"
            :value="ruleStats.total"
            suffix="个"
            :value-style="{ color: '#409eff' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="启用规则"
            :value="ruleStats.enabled"
            suffix="个"
            :value-style="{ color: '#67c23a' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="今日触发"
            :value="ruleStats.todayTriggered"
            suffix="次"
            :value-style="{ color: '#e6a23c' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic
            title="异常规则"
            :value="ruleStats.errors"
            suffix="个"
            :value-style="{ color: '#f56c6c' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><CircleClose /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 规则筛选 -->
    <el-card class="filter-section">
      <el-form :model="filterForm" :inline="true" class="filter-form">
        <el-form-item label="规则状态">
          <el-select v-model="filterForm.status" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="启用" value="enabled" />
            <el-option label="禁用" value="disabled" />
            <el-option label="异常" value="error" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="规则类型">
          <el-select v-model="filterForm.type" style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="阈值告警" value="threshold" />
            <el-option label="异常检测" value="anomaly" />
            <el-option label="趋势分析" value="trend" />
            <el-option label="聚合规则" value="aggregation" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="紧急" value="critical" />
            <el-option label="重要" value="high" />
            <el-option label="一般" value="medium" />
            <el-option label="较低" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="搜索规则名称或描述..."
            style="width: 200px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="filterRules">
            筛选
          </el-button>
          <el-button @click="resetFilter">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 规则列表 -->
    <el-card class="rules-list-section">
      <template #header>
        <div class="section-header">
          <h3>
            <el-icon><List /></el-icon>
            规则列表
          </h3>
          <div class="header-controls">
            <el-button-group size="small">
              <el-button 
                :type="viewMode === 'list' ? 'primary' : ''"
                @click="viewMode = 'list'"
              >
                列表视图
              </el-button>
              <el-button 
                :type="viewMode === 'card' ? 'primary' : ''"
                @click="viewMode = 'card'"
              >
                卡片视图
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'">
        <el-table 
          :data="filteredRules" 
          style="width: 100%"
          :loading="tableLoading"
          stripe
        >
          <el-table-column prop="name" label="规则名称" width="200" />
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getRuleTypeColor(row.type)" size="small">
                {{ getRuleTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :type="getPriorityColor(row.priority)" size="small">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-switch
                v-model="row.enabled"
                @change="toggleRule(row)"
                active-text="启用"
                inactive-text="禁用"
              />
            </template>
          </el-table-column>
          <el-table-column prop="triggerCount" label="触发次数" width="120" sortable />
          <el-table-column prop="lastTriggered" label="最后触发" width="180" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" link @click="editRule(row)">
                编辑
              </el-button>
              <el-button size="small" type="success" link @click="duplicateRule(row)">
                复制
              </el-button>
              <el-button size="small" type="info" link @click="testRule(row)">
                测试
              </el-button>
              <el-button size="small" type="danger" link @click="deleteRule(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 卡片视图 -->
      <div v-else class="rules-cards">
        <el-row :gutter="20">
          <el-col 
            v-for="rule in filteredRules" 
            :key="rule.id"
            :span="8"
          >
            <div class="rule-card">
              <div class="rule-header">
                <div class="rule-info">
                  <h4>{{ rule.name }}</h4>
                  <p class="rule-description">{{ rule.description }}</p>
                </div>
                <el-switch
                  v-model="rule.enabled"
                  @change="toggleRule(rule)"
                  size="small"
                />
              </div>
              
              <div class="rule-meta">
                <el-tag :type="getRuleTypeColor(rule.type)" size="small">
                  {{ getRuleTypeText(rule.type) }}
                </el-tag>
                <el-tag :type="getPriorityColor(rule.priority)" size="small">
                  {{ getPriorityText(rule.priority) }}
                </el-tag>
              </div>
              
              <div class="rule-stats">
                <div class="stat-item">
                  <span class="stat-label">触发次数:</span>
                  <span class="stat-value">{{ rule.triggerCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">最后触发:</span>
                  <span class="stat-value">{{ rule.lastTriggered || '从未' }}</span>
                </div>
              </div>
              
              <div class="rule-actions">
                <el-button size="small" type="primary" @click="editRule(rule)">
                  编辑
                </el-button>
                <el-button size="small" @click="duplicateRule(rule)">
                  复制
                </el-button>
                <el-button size="small" type="info" @click="testRule(rule)">
                  测试
                </el-button>
                <el-dropdown @command="(command) => handleRuleAction(command, rule)">
                  <el-button size="small" type="text">
                    更多<el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="history">查看历史</el-dropdown-item>
                      <el-dropdown-item command="export">导出规则</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除规则</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 分页 -->
      <div class="table-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[12, 24, 48, 96]"
          :total="totalRules"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑规则弹窗 -->
    <el-dialog
      v-model="showCreateRule"
      :title="editingRule ? '编辑规则' : '创建规则'"
      width="800px"
      @close="resetRuleForm"
    >
      <el-form :model="ruleForm" :rules="ruleFormRules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="name">
              <el-input v-model="ruleForm.name" placeholder="请输入规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规则类型" prop="type">
              <el-select v-model="ruleForm.type" style="width: 100%">
                <el-option label="阈值告警" value="threshold" />
                <el-option label="异常检测" value="anomaly" />
                <el-option label="趋势分析" value="trend" />
                <el-option label="聚合规则" value="aggregation" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="ruleForm.priority" style="width: 100%">
                <el-option label="紧急" value="critical" />
                <el-option label="重要" value="high" />
                <el-option label="一般" value="medium" />
                <el-option label="较低" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="ruleForm.enabled" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="规则描述" prop="description">
          <el-input 
            v-model="ruleForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入规则描述"
          />
        </el-form-item>
        
        <el-form-item label="监控指标" prop="metric">
          <el-select v-model="ruleForm.metric" style="width: 100%">
            <el-option label="CPU使用率" value="cpu_usage" />
            <el-option label="内存使用率" value="memory_usage" />
            <el-option label="磁盘使用率" value="disk_usage" />
            <el-option label="网络流量" value="network_traffic" />
            <el-option label="响应时间" value="response_time" />
            <el-option label="错误率" value="error_rate" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="ruleForm.type === 'threshold'" label="阈值条件">
          <el-row :gutter="10">
            <el-col :span="8">
              <el-select v-model="ruleForm.operator" placeholder="操作符">
                <el-option label="大于" value=">" />
                <el-option label="大于等于" value=">=" />
                <el-option label="小于" value="<" />
                <el-option label="小于等于" value="<=" />
                <el-option label="等于" value="==" />
                <el-option label="不等于" value="!=" />
              </el-select>
            </el-col>
            <el-col :span="8">
              <el-input-number 
                v-model="ruleForm.threshold" 
                placeholder="阈值"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="8">
              <el-input v-model="ruleForm.unit" placeholder="单位" />
            </el-col>
          </el-row>
        </el-form-item>
        
        <el-form-item label="通知方式">
          <el-checkbox-group v-model="ruleForm.notifications">
            <el-checkbox label="email">邮件通知</el-checkbox>
            <el-checkbox label="slack">Slack通知</el-checkbox>
            <el-checkbox label="webhook">Webhook</el-checkbox>
            <el-checkbox label="sms">短信通知</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateRule = false">取消</el-button>
          <el-button type="primary" @click="saveRule" :loading="saveLoading">
            {{ editingRule ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Plus,
  Upload,
  Download,
  Document,
  CircleCheck,
  Warning,
  CircleClose,
  Search,
  List,
  ArrowDown
} from '@element-plus/icons-vue'

// 响应式数据
const tableLoading = ref(false)
const saveLoading = ref(false)
const showCreateRule = ref(false)
const editingRule = ref<any>(null)
const viewMode = ref('list') // 'list' | 'card'
const currentPage = ref(1)
const pageSize = ref(12)

// 规则统计
const ruleStats = ref({
  total: 24,
  enabled: 18,
  todayTriggered: 156,
  errors: 2
})

// 筛选表单
const filterForm = ref({
  status: '',
  type: '',
  priority: '',
  search: ''
})

// 规则表单
const ruleForm = ref({
  name: '',
  type: 'threshold',
  priority: 'medium',
  enabled: true,
  description: '',
  metric: '',
  operator: '>',
  threshold: 0,
  unit: '',
  notifications: ['email']
})

// 表单验证规则
const ruleFormRules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入规则描述', trigger: 'blur' }
  ],
  metric: [
    { required: true, message: '请选择监控指标', trigger: 'change' }
  ]
}

// 规则数据
const rules = ref([
  {
    id: 1,
    name: 'CPU高使用率告警',
    type: 'threshold',
    priority: 'high',
    enabled: true,
    description: '当CPU使用率超过85%时触发告警',
    metric: 'cpu_usage',
    triggerCount: 45,
    lastTriggered: '2025-09-06 22:30:15',
    operator: '>',
    threshold: 85,
    unit: '%'
  },
  {
    id: 2,
    name: '内存使用率监控',
    type: 'threshold',
    priority: 'medium',
    enabled: true,
    description: '监控内存使用率，超过90%时告警',
    metric: 'memory_usage',
    triggerCount: 23,
    lastTriggered: '2025-09-06 21:45:32',
    operator: '>',
    threshold: 90,
    unit: '%'
  },
  {
    id: 3,
    name: '响应时间异常检测',
    type: 'anomaly',
    priority: 'high',
    enabled: true,
    description: '使用机器学习算法检测响应时间异常',
    metric: 'response_time',
    triggerCount: 12,
    lastTriggered: '2025-09-06 20:15:21'
  },
  {
    id: 4,
    name: '磁盘空间使用监控',
    type: 'threshold',
    priority: 'critical',
    enabled: true,
    description: '磁盘空间使用率超过95%时紧急告警',
    metric: 'disk_usage',
    triggerCount: 8,
    lastTriggered: '2025-09-06 19:30:45',
    operator: '>',
    threshold: 95,
    unit: '%'
  },
  {
    id: 5,
    name: '网络流量趋势分析',
    type: 'trend',
    priority: 'medium',
    enabled: false,
    description: '分析网络流量趋势，检测异常流量增长',
    metric: 'network_traffic',
    triggerCount: 0,
    lastTriggered: null
  },
  {
    id: 6,
    name: '错误率聚合监控',
    type: 'aggregation',
    priority: 'low',
    enabled: true,
    description: '5分钟内错误率超过1%时告警',
    metric: 'error_rate',
    triggerCount: 34,
    lastTriggered: '2025-09-06 18:22:10'
  }
])

// 计算属性
const totalRules = computed(() => rules.value.length)

const filteredRules = computed(() => {
  let filtered = rules.value
  
  if (filterForm.value.status) {
    if (filterForm.value.status === 'enabled') {
      filtered = filtered.filter(rule => rule.enabled)
    } else if (filterForm.value.status === 'disabled') {
      filtered = filtered.filter(rule => !rule.enabled)
    }
  }
  
  if (filterForm.value.type) {
    filtered = filtered.filter(rule => rule.type === filterForm.value.type)
  }
  
  if (filterForm.value.priority) {
    filtered = filtered.filter(rule => rule.priority === filterForm.value.priority)
  }
  
  if (filterForm.value.search) {
    const search = filterForm.value.search.toLowerCase()
    filtered = filtered.filter(rule => 
      rule.name.toLowerCase().includes(search) ||
      rule.description.toLowerCase().includes(search)
    )
  }
  
  return filtered
})

// 方法函数

/**
 * 导入规则
 */
const importRules = () => {
  ElMessage.info('导入功能开发中...')
}

/**
 * 导出规则
 */
const exportRules = () => {
  ElMessage.info('导出功能开发中...')
}

/**
 * 筛选规则
 */
const filterRules = () => {
  ElMessage.success('筛选完成')
}

/**
 * 重置筛选
 */
const resetFilter = () => {
  filterForm.value = {
    status: '',
    type: '',
    priority: '',
    search: ''
  }
}

/**
 * 切换规则状态
 */
const toggleRule = (rule: any) => {
  const status = rule.enabled ? '启用' : '禁用'
  ElMessage.success(`规则「${rule.name}」已${status}`)
}

/**
 * 编辑规则
 */
const editRule = (rule: any) => {
  editingRule.value = rule
  ruleForm.value = {
    name: rule.name,
    type: rule.type,
    priority: rule.priority,
    enabled: rule.enabled,
    description: rule.description,
    metric: rule.metric,
    operator: rule.operator || '>',
    threshold: rule.threshold || 0,
    unit: rule.unit || '',
    notifications: ['email']
  }
  showCreateRule.value = true
}

/**
 * 复制规则
 */
const duplicateRule = (rule: any) => {
  const newRule = {
    ...rule,
    id: Date.now(),
    name: rule.name + ' - 副本',
    triggerCount: 0,
    lastTriggered: null
  }
  rules.value.push(newRule)
  ElMessage.success('规则复制成功')
}

/**
 * 测试规则
 */
const testRule = (rule: any) => {
  ElMessage.info(`正在测试规则「${rule.name}」...`)
  setTimeout(() => {
    ElMessage.success('规则测试通过')
  }, 2000)
}

/**
 * 删除规则
 */
const deleteRule = async (rule: any) => {
  try {
    await ElMessageBox.confirm(
      `确定删除规则「${rule.name}」吗？此操作不可恢复。`,
      '确认删除',
      {
        type: 'warning'
      }
    )
    
    const index = rules.value.findIndex(r => r.id === rule.id)
    if (index > -1) {
      rules.value.splice(index, 1)
      ElMessage.success('规则删除成功')
    }
  } catch {
    // 用户取消
  }
}

/**
 * 处理规则操作
 */
const handleRuleAction = (command: string, rule: any) => {
  switch (command) {
    case 'history':
      ElMessage.info(`查看规则「${rule.name}」的历史记录`)
      break
    case 'export':
      ElMessage.info(`导出规则「${rule.name}」`)
      break
    case 'delete':
      deleteRule(rule)
      break
  }
}

/**
 * 保存规则
 */
const saveRule = async () => {
  saveLoading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingRule.value) {
      // 更新规则
      Object.assign(editingRule.value, ruleForm.value)
      ElMessage.success('规则更新成功')
    } else {
      // 创建新规则
      const newRule = {
        ...ruleForm.value,
        id: Date.now(),
        triggerCount: 0,
        lastTriggered: null
      }
      rules.value.push(newRule)
      ElMessage.success('规则创建成功')
    }
    
    showCreateRule.value = false
    resetRuleForm()
  } catch (error) {
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    saveLoading.value = false
  }
}

/**
 * 重置规则表单
 */
const resetRuleForm = () => {
  editingRule.value = null
  ruleForm.value = {
    name: '',
    type: 'threshold',
    priority: 'medium',
    enabled: true,
    description: '',
    metric: '',
    operator: '>',
    threshold: 0,
    unit: '',
    notifications: ['email']
  }
}

/**
 * 分页处理
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 工具函数

const getRuleTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    threshold: 'primary',
    anomaly: 'warning',
    trend: 'info',
    aggregation: 'success'
  }
  return colorMap[type] || 'info'
}

const getRuleTypeText = (type: string): string => {
  const textMap: Record<string, string> = {
    threshold: '阈值告警',
    anomaly: '异常检测',
    trend: '趋势分析',
    aggregation: '聚合规则'
  }
  return textMap[type] || '未知'
}

const getPriorityColor = (priority: string): string => {
  const colorMap: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return colorMap[priority] || 'info'
}

const getPriorityText = (priority: string): string => {
  const textMap: Record<string, string> = {
    critical: '紧急',
    high: '重要',
    medium: '一般',
    low: '较低'
  }
  return textMap[priority] || '未知'
}

// 生命周期钩子
onMounted(() => {
  document.title = '规则配置 - 智能监控预警系统'
})
</script>

<style scoped lang="scss">
.rules {
  padding: 20px;
  
  .page-header {
    @include flex-between;
    margin-bottom: 24px;
    
    .header-content {
      .page-title {
        @include flex-center;
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 600;
        color: $primary-color;
        gap: 12px;
        
        .el-icon {
          font-size: 32px;
        }
      }
      
      .page-description {
        margin: 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
        line-height: 1.5;
        max-width: 600px;
      }
    }
    
    .header-actions {
      @include flex-center;
      gap: 12px;
    }
  }
  
  .stats-section {
    margin-bottom: 24px;
    
    .stat-card {
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .stat-icon {
        font-size: 20px;
        margin-right: 8px;
      }
    }
  }
  
  .filter-section {
    margin-bottom: 24px;
    
    .filter-form {
      .el-form-item {
        margin-bottom: 16px;
      }
    }
  }
  
  .rules-list-section {
    .section-header {
      @include flex-between;
      
      h3 {
        @include flex-center;
        margin: 0;
        gap: 8px;
      }
      
      .header-controls {
        @include flex-center;
      }
    }
    
    .el-table {
      margin-top: 16px;
      
      .el-button--small {
        padding: 4px 8px;
      }
    }
    
    .rules-cards {
      margin-top: 16px;
      
      .rule-card {
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 20px;
        transition: all 0.2s;
        height: 100%;
        margin-bottom: 20px;
        
        &:hover {
          border-color: var(--el-border-color);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .rule-header {
          @include flex-between;
          margin-bottom: 16px;
          
          .rule-info {
            flex: 1;
            
            h4 {
              margin: 0 0 8px 0;
              font-size: 16px;
              font-weight: 600;
              color: var(--el-text-color-primary);
            }
            
            .rule-description {
              margin: 0;
              font-size: 12px;
              color: var(--el-text-color-secondary);
              line-height: 1.4;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              overflow: hidden;
            }
          }
        }
        
        .rule-meta {
          @include flex-center;
          gap: 8px;
          margin-bottom: 16px;
        }
        
        .rule-stats {
          margin-bottom: 16px;
          
          .stat-item {
            @include flex-between;
            margin-bottom: 8px;
            font-size: 12px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .stat-label {
              color: var(--el-text-color-secondary);
            }
            
            .stat-value {
              font-weight: 500;
              color: var(--el-text-color-primary);
            }
          }
        }
        
        .rule-actions {
          @include flex-center;
          gap: 8px;
          
          .el-button {
            flex: 1;
          }
        }
      }
    }
    
    .table-pagination {
      @include flex-center;
      margin-top: 20px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .rules {
    .rules-cards .el-col {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .rules {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .stats-section .el-col {
      margin-bottom: 16px;
    }
    
    .filter-section {
      .filter-form {
        .el-form-item {
          width: 100%;
          margin-bottom: 12px;
        }
      }
    }
    
    .rules-cards {
      .el-col {
        span: 24 !important;
      }
    }
  }
}

// 暗色模式适配
.dark {
  .stat-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
  
  .rule-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
}
</style>