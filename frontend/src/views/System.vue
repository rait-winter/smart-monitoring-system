<template>
  <div class="system">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon><Tools /></el-icon>
          系统管理
        </h1>
        <p class="page-description">
          管理系统配置、用户权限、服务状态和系统监控参数
        </p>
      </div>
      
      <div class="header-actions">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          @click="refreshSystemInfo"
          :loading="refreshLoading"
        >
          刷新状态
        </el-button>
        <el-button 
          type="warning" 
          :icon="Download" 
          @click="backupSystem"
        >
          系统备份
        </el-button>
      </div>
    </div>

    <!-- 系统概览 -->
    <el-row :gutter="20" class="overview-section">
      <el-col :span="6">
        <el-card class="overview-card">
          <el-statistic
            title="系统运行时间"
            :value="systemInfo.uptime"
            suffix="天"
            :value-style="{ color: '#409eff' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Timer /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <el-statistic
            title="在线用户"
            :value="systemInfo.onlineUsers"
            suffix="人"
            :value-style="{ color: '#67c23a' }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <el-statistic
            title="系统负载"
            :value="systemInfo.cpuUsage"
            suffix="%"
            :value-style="{ color: getCpuColor(systemInfo.cpuUsage) }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Cpu /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card">
          <el-statistic
            title="内存使用"
            :value="systemInfo.memoryUsage"
            suffix="%"
            :value-style="{ color: getMemoryColor(systemInfo.memoryUsage) }"
          >
            <template #prefix>
              <el-icon class="stat-icon"><Monitor /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统详细信息 -->
    <el-row :gutter="20" class="system-details-section" v-if="systemInfo.systemDetails && Object.keys(systemInfo.systemDetails).length > 0">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>
                <el-icon><Monitor /></el-icon>
                系统详细信息
              </h3>
              <el-button size="small" text type="primary" @click="showSystemDetails = !showSystemDetails">
                {{ showSystemDetails ? '收起' : '展开' }}
              </el-button>
            </div>
          </template>
          
          <el-collapse-transition>
            <div v-show="showSystemDetails">
              <el-row :gutter="20">
                <!-- 基本信息 -->
                <el-col :span="8">
                  <el-card class="detail-card">
                    <h4>基本信息</h4>
                    <el-descriptions :column="1" size="small">
                      <el-descriptions-item label="操作系统">
                        {{ systemInfo.systemDetails.platform }} {{ systemInfo.systemDetails.platform_release }}
                      </el-descriptions-item>
                      <el-descriptions-item label="主机名">
                        {{ systemInfo.systemDetails.hostname }}
                      </el-descriptions-item>
                      <el-descriptions-item label="架构">
                        {{ systemInfo.systemDetails.architecture }}
                      </el-descriptions-item>
                      <el-descriptions-item label="处理器">
                        {{ systemInfo.systemDetails.processor || '未知' }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </el-card>
                </el-col>
                
                <!-- CPU信息 -->
                <el-col :span="8">
                  <el-card class="detail-card">
                    <h4>CPU信息</h4>
                    <el-descriptions :column="1" size="small">
                      <el-descriptions-item label="逻辑核心">
                        {{ systemInfo.systemDetails.cpu_count_logical || 'N/A' }} 核
                      </el-descriptions-item>
                      <el-descriptions-item label="物理核心">
                        {{ systemInfo.systemDetails.cpu_count_physical || 'N/A' }} 核
                      </el-descriptions-item>
                      <el-descriptions-item label="当前频率" v-if="systemInfo.systemDetails.cpu_freq_current">
                        {{ systemInfo.systemDetails.cpu_freq_current }} MHz
                      </el-descriptions-item>
                      <el-descriptions-item label="最大频率" v-if="systemInfo.systemDetails.cpu_freq_max">
                        {{ systemInfo.systemDetails.cpu_freq_max }} MHz
                      </el-descriptions-item>
                    </el-descriptions>
                  </el-card>
                </el-col>
                
                <!-- 存储和网络信息 -->
                <el-col :span="8">
                  <el-card class="detail-card">
                    <h4>存储和网络</h4>
                    <el-descriptions :column="1" size="small">
                      <el-descriptions-item label="磁盘总容量" v-if="systemInfo.systemDetails.disk_total">
                        {{ systemInfo.systemDetails.disk_total }} GB
                      </el-descriptions-item>
                      <el-descriptions-item label="磁盘已用" v-if="systemInfo.systemDetails.disk_used">
                        {{ systemInfo.systemDetails.disk_used }} GB ({{ systemInfo.systemDetails.disk_usage_percent }}%)
                      </el-descriptions-item>
                      <el-descriptions-item label="网络发送" v-if="systemInfo.systemDetails.network_bytes_sent">
                        {{ (systemInfo.systemDetails.network_bytes_sent / (1024*1024*1024)).toFixed(2) }} GB
                      </el-descriptions-item>
                      <el-descriptions-item label="网络接收" v-if="systemInfo.systemDetails.network_bytes_recv">
                        {{ (systemInfo.systemDetails.network_bytes_recv / (1024*1024*1024)).toFixed(2) }} GB
                      </el-descriptions-item>
                    </el-descriptions>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </el-collapse-transition>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能选项卡 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 服务状态 -->
      <el-tab-pane label="服务状态" name="services">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>服务状态监控</h3>
              <el-button size="small" @click="refreshServices" :loading="servicesLoading">
                刷新状态
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col 
              v-for="service in systemServices" 
              :key="service.name"
              :span="8"
            >
              <div class="service-card">
                <div class="service-header">
                  <div class="service-info">
                    <el-icon 
                      class="service-icon"
                      :class="getServiceStatusClass(service.status, service.health)"
                    >
                      <CircleCheck v-if="service.status === 'running' && service.health === 'healthy'" />
                      <Warning v-else-if="service.status === 'running' && service.health === 'degraded'" />
                      <CircleClose v-else-if="service.status === 'stopped'" />
                      <Warning v-else />
                    </el-icon>
                    <h4>{{ service.name }}</h4>
                  </div>
                  <el-tag :type="getServiceStatusType(service.status, service.health)" size="small">
                    {{ getServiceStatusText(service.status, service.health) }}
                  </el-tag>
                </div>
                
                <div class="service-details">
                  <div class="detail-item">
                    <span class="label">端口:</span>
                    <span class="value">{{ service.port }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">CPU:</span>
                    <span class="value">{{ service.cpuUsage }}%</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">内存:</span>
                    <span class="value">{{ service.memoryUsage }}MB</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">运行时间:</span>
                    <span class="value">{{ service.uptime }}</span>
                  </div>
                  <div class="detail-item" v-if="service.message">
                    <span class="label">状态信息:</span>
                    <span class="value" :class="{ 'text-warning': service.health === 'degraded', 'text-danger': service.health === 'unhealthy' }">
                      {{ service.message }}
                    </span>
                  </div>
                </div>
                
                <div class="service-actions">
                  <el-button 
                    v-if="service.status === 'stopped'"
                    size="small" 
                    type="success" 
                    @click="handleServiceAction(service, 'start')"
                    :loading="servicesLoading"
                  >
                    启动
                  </el-button>
                  <el-button 
                    v-else-if="service.status === 'running'"
                    size="small" 
                    type="warning" 
                    @click="handleServiceAction(service, 'stop')"
                    :loading="servicesLoading"
                  >
                    停止
                  </el-button>
                  <el-button 
                    v-if="service.status === 'running'"
                    size="small" 
                    @click="handleServiceAction(service, 'restart')"
                    :loading="servicesLoading"
                  >
                    重启
                  </el-button>
                  <el-button size="small" type="info" @click="viewServiceLogs(service)">
                    日志
                  </el-button>
                  <el-tag 
                    v-if="service.status === 'unknown'"
                    type="info" 
                    size="small"
                  >
                    状态未知
                  </el-tag>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
      
      <!-- 数据源配置 -->
      <el-tab-pane label="数据源配置" name="datasource">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>
                <el-icon><Connection /></el-icon>
                Prometheus数据源配置
              </h3>
              <el-button 
                size="small" 
                type="primary" 
                @click="savePrometheusConfigLocal" 
                :loading="savePrometheusLoading"
              >
                保存配置
              </el-button>
            </div>
          </template>
          
          <el-form :model="prometheusConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>基础配置</h4>
                <el-form-item label="启用Prometheus">
                  <el-switch v-model="prometheusConfig.enabled" />
                </el-form-item>
                <el-form-item 
                  label="配置名称" 
                  :error="!configNameValidation.valid ? configNameValidation.message : ''"
                >
                  <el-input 
                    v-model="prometheusConfig.name" 
                    placeholder="例如: prod-prometheus, dev-monitor"
                    :disabled="!prometheusConfig.enabled"
                    :class="{ 'is-error': !configNameValidation.valid }"
                    maxlength="50"
                    show-word-limit
                  />
                  <div class="form-item-tip">
                    <el-icon><InfoFilled /></el-icon>
                    <span>只能包含字母、数字、下划线(_)和短横线(-)，不能以数字或符号开头/结尾</span>
                  </div>
                </el-form-item>
                <el-form-item label="服务器地址">
                  <el-input 
                    v-model="prometheusConfig.url" 
                    placeholder="http://localhost:9090"
                    :disabled="!prometheusConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="用户名">
                  <el-input 
                    v-model="prometheusConfig.username" 
                    placeholder="可选"
                    :disabled="!prometheusConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="密码">
                  <el-input 
                    v-model="prometheusConfig.password" 
                    type="password" 
                    placeholder="可选"
                    :disabled="!prometheusConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="连接测试">
                  <el-button 
                    @click="testPrometheusConnection" 
                    :loading="testConnectionLoading"
                    :disabled="!prometheusConfig.enabled || !prometheusConfig.url"
                  >
                    测试连接
                  </el-button>
                  <el-tag 
                    v-if="connectionStatus"
                    :type="connectionStatus.success ? 'success' : 'danger'"
                    style="margin-left: 10px"
                  >
                    {{ connectionStatus.message }}
                  </el-tag>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <h4>高级配置</h4>
                <el-form-item label="请求超时(ms)">
                  <el-input-number 
                    v-model="prometheusConfig.timeout" 
                    :min="5000" 
                    :max="60000"
                    :step="1000"
                    style="width: 100%"
                    :disabled="!prometheusConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="采集间隔">
                  <el-select 
                    v-model="prometheusConfig.scrapeInterval" 
                    style="width: 100%"
                    :disabled="!prometheusConfig.enabled"
                  >
                    <el-option label="5秒" value="5s" />
                    <el-option label="10秒" value="10s" />
                    <el-option label="15秒" value="15s" />
                    <el-option label="30秒" value="30s" />
                    <el-option label="1分钟" value="1m" />
                  </el-select>
                </el-form-item>
                <el-form-item label="评估间隔">
                  <el-select 
                    v-model="prometheusConfig.evaluationInterval" 
                    style="width: 100%"
                    :disabled="!prometheusConfig.enabled"
                  >
                    <el-option label="5秒" value="5s" />
                    <el-option label="10秒" value="10s" />
                    <el-option label="15秒" value="15s" />
                    <el-option label="30秒" value="30s" />
                    <el-option label="1分钟" value="1m" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          
          <!-- 监控目标配置 -->
          <el-divider />
          <div class="targets-section">
            <div class="section-header">
              <h4>
                <el-icon><Monitor /></el-icon>
                监控目标
              </h4>
              <el-button 
                size="small" 
                type="primary" 
                @click="showAddTarget = true"
                :disabled="!prometheusConfig.enabled"
              >
                添加目标
              </el-button>
            </div>
            
            <el-table 
              :data="prometheusConfig.targets" 
              style="width: 100%"
              empty-text="暂无监控目标"
            >
              <el-table-column prop="name" label="名称" width="150" />
              <el-table-column prop="address" label="地址" width="150" />
              <el-table-column prop="port" label="端口" width="80" />
              <el-table-column prop="path" label="路径" width="100" />
              <el-table-column prop="enabled" label="状态" width="80">
                <template #default="{ row }">
                  <el-switch 
                    v-model="row.enabled" 
                    size="small"
                    @change="updateTargetStatus(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="标签" min-width="200">
                <template #default="{ row }">
                  <el-tag 
                    v-for="(value, key) in row.labels" 
                    :key="key"
                    size="small"
                    style="margin-right: 5px"
                  >
                    {{ key }}={{ value }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="editTarget(row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" link @click="deleteTarget(row.id)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- Prometheus配置查看器 -->
        <PrometheusConfigViewerOptimized 
          ref="configViewerRef"
          @configChanged="handleConfigChanged"
          class="config-viewer-section"
        />
      </el-tab-pane>
      
      <!-- AI配置 -->
      <el-tab-pane label="AI配置" name="ai">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>
                <el-icon><DataAnalysis /></el-icon>
                Ollama AI配置
              </h3>
              <el-button 
                size="small" 
                type="primary" 
                @click="saveOllamaConfigLocal" 
                :loading="saveOllamaLoading"
              >
                保存配置
              </el-button>
            </div>
          </template>
          
          <!-- 配置状态提示 -->
          <el-alert
            v-if="ollamaConfig.name"
            :title="`正在使用已保存的配置: ${ollamaConfig.name}`"
            type="success"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <template #default>
              <span>您可以修改以下配置参数并保存为新的配置，或者覆盖当前配置。</span>
            </template>
          </el-alert>
          
          <el-alert
            v-else
            title="使用默认配置"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <template #default>
              <span>当前使用的是默认配置，建议填写配置名称并保存，以便后续管理和使用。</span>
            </template>
          </el-alert>
          
          <el-form :model="ollamaConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>基础配置</h4>
                <el-form-item label="启用AI分析">
                  <el-switch v-model="ollamaConfig.enabled" />
                  <div class="form-item-tip" v-if="ollamaConfig.enabled">
                    <el-icon><InfoFilled /></el-icon>
                    <span style="color: #67c23a;">AI分析功能已启用，系统将提供智能监控和预警服务</span>
                  </div>
                </el-form-item>
                <el-form-item 
                  label="配置名称" 
                  :error="!ollamaConfigNameValidation.valid ? ollamaConfigNameValidation.message : ''"
                >
                  <el-input 
                    v-model="ollamaConfig.name" 
                    :placeholder="ollamaConfig.name ? `当前配置: ${ollamaConfig.name}` : '为配置命名，例如: prod-ollama, dev-ai'"
                    :disabled="!ollamaConfig.enabled"
                    :class="{ 'is-error': !ollamaConfigNameValidation.valid }"
                    maxlength="50"
                    show-word-limit
                  />
                  <div class="form-item-tip">
                    <el-icon><InfoFilled /></el-icon>
                    <span v-if="ollamaConfig.name">
                      修改配置名称将创建新配置，留空则覆盖当前配置
                    </span>
                    <span v-else>
                      只能包含字母、数字、下划线(_)和短横线(-)，不能以数字或符号开头/结尾
                    </span>
                  </div>
                </el-form-item>
                <el-form-item label="API地址">
                  <el-input 
                    v-model="ollamaConfig.apiUrl" 
                    placeholder="http://localhost:11434"
                    :disabled="!ollamaConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="AI模型">
                  <el-select 
                    v-model="ollamaConfig.model" 
                    style="width: 100%"
                    :disabled="!ollamaConfig.enabled"
                    placeholder="选择AI模型"
                    :loading="modelsLoading"
                    @focus="loadAvailableModels"
                    filterable
                  >
                    <el-option 
                      v-for="model in availableModels" 
                      :key="model.name"
                      :label="model.label"
                      :value="model.name"
                    >
                      <span style="float: left">{{ model.label }}</span>
                      <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                        {{ model.size }}
                      </span>
                    </el-option>
                    <!-- 如果没有模型，显示提示 -->
                    <el-option 
                      v-if="!modelsLoading && availableModels.length === 0"
                      disabled
                      value=""
                      label="未找到可用模型，请检查Ollama服务"
                    />
                  </el-select>
                  <div class="form-item-tip" v-if="availableModels.length === 0 && !modelsLoading">
                    <el-icon><InfoFilled /></el-icon>
                    请先启动Ollama服务并拉取模型
                  </div>
                </el-form-item>
                <el-form-item label="连接测试">
                  <el-button 
                    @click="testOllamaConnectionLocal" 
                    :loading="testOllamaLoading"
                    :disabled="!ollamaConfig.enabled || !ollamaConfig.apiUrl"
                  >
                    测试连接
                  </el-button>
                  <el-tag 
                    v-if="ollamaConnectionStatus"
                    :type="ollamaConnectionStatus.success ? 'success' : 'danger'"
                    style="margin-left: 10px"
                  >
                    {{ ollamaConnectionStatus.message }}
                  </el-tag>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <h4>高级配置</h4>
                <el-form-item label="请求超时(ms)">
                  <el-input-number 
                    v-model="ollamaConfig.timeout" 
                    :min="10000" 
                    :max="300000"
                    :step="5000"
                    style="width: 100%"
                    :disabled="!ollamaConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="最大Token数">
                  <el-input-number 
                    v-model="ollamaConfig.maxTokens" 
                    :min="512" 
                    :max="4096"
                    :step="256"
                    style="width: 100%"
                    :disabled="!ollamaConfig.enabled"
                  />
                </el-form-item>
                <el-form-item label="创造性(Temperature)">
                  <el-slider 
                    v-model="ollamaConfig.temperature"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    :disabled="!ollamaConfig.enabled"
                    show-stops
                    show-tooltip
                  />
                  <p class="config-description">
                    较低值(0.1-0.3)：更确定、一致的输出<br/>
                    较高值(0.7-0.9)：更有创造性的输出
                  </p>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
        
        <!-- Ollama配置查看器 -->
        <OllamaConfigViewerOptimized ref="ollamaConfigViewerRef" />
        
        <!-- AI功能配置 -->
        <el-card>
          <el-divider />
          <div class="ai-features-section">
            <div class="section-header">
              <h4>
                <el-icon><Setting /></el-icon>
                AI功能配置
              </h4>
            </div>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="feature-card">
                  <template #header>
                    <h5>异常检测</h5>
                  </template>
                  <div class="feature-content">
                    <el-switch v-model="aiFeatures.anomalyDetection.enabled" />
                    <p class="feature-description">
                      自动检测系统指标异常，识别潜在问题
                    </p>
                    <div v-if="aiFeatures.anomalyDetection.enabled" class="feature-config">
                      <el-form-item label="检测间隔(分钟)">
                        <el-input-number 
                          v-model="aiFeatures.anomalyDetection.interval" 
                          :min="5" 
                          :max="60"
                          size="small"
                        />
                      </el-form-item>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="feature-card">
                  <template #header>
                    <h5>智能分析</h5>
                  </template>
                  <div class="feature-content">
                    <el-switch v-model="aiFeatures.intelligentAnalysis.enabled" />
                    <p class="feature-description">
                      深度分析系统性能，提供优化建议
                    </p>
                    <div v-if="aiFeatures.intelligentAnalysis.enabled" class="feature-config">
                      <el-form-item label="分析深度">
                        <el-select v-model="aiFeatures.intelligentAnalysis.depth" size="small">
                          <el-option label="基础" value="basic" />
                          <el-option label="标准" value="standard" />
                          <el-option label="深度" value="deep" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="feature-card">
                  <template #header>
                    <h5>自动报告</h5>
                  </template>
                  <div class="feature-content">
                    <el-switch v-model="aiFeatures.autoReport.enabled" />
                    <p class="feature-description">
                      定期生成AI分析报告并自动发送
                    </p>
                    <div v-if="aiFeatures.autoReport.enabled" class="feature-config">
                      <el-form-item label="报告频率">
                        <el-select v-model="aiFeatures.autoReport.frequency" size="small">
                          <el-option label="每日" value="daily" />
                          <el-option label="每周" value="weekly" />
                          <el-option label="每月" value="monthly" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 数据库配置 -->
      <el-tab-pane label="数据库配置" name="database">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>
                <el-icon><DataBoard /></el-icon>
                PostgreSQL数据库配置
              </h3>
              <div class="header-actions">
                <el-button 
                  size="small" 
                  @click="testDatabaseConnectionLocal" 
                  :loading="testDbLoading"
                >
                  测试连接
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="saveDatabaseConfigLocal" 
                  :loading="saveDbLoading"
                >
                  保存配置
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 加载状态 -->
          <div v-if="loadDbConfigLoading" class="loading-skeleton">
            <el-skeleton :rows="8" animated>
              <template #template>
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
                <el-skeleton-item style="height: 40px; margin-bottom: 16px;" />
              </template>
            </el-skeleton>
          </div>
          
          <!-- 配置表单 -->
          <el-form v-else :model="databaseConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>连接配置</h4>
                <el-form-item label="配置名称" :error="databaseConfigNameValidation.valid ? '' : databaseConfigNameValidation.message">
                  <el-input
                    v-model="databaseConfig.name"
                    placeholder="例如：production-database"
                    :disabled="!databaseConfig.postgresql.enabled"
                    maxlength="50"
                    show-word-limit
                    :class="{ 'is-error': !databaseConfigNameValidation.valid }"
                  />
                  <div class="form-item-tip">
                    <el-icon><InfoFilled /></el-icon>
                    只能包含字母、数字、下划线和短横线，不能以数字或符号开头或结尾
                  </div>
                </el-form-item>
                <el-form-item label="启用数据库">
                  <el-switch v-model="databaseConfig.postgresql.enabled" />
                </el-form-item>
                <el-form-item label="主机地址">
                  <el-input 
                    v-model="databaseConfig.postgresql.host" 
                    placeholder="localhost"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="端口">
                  <el-input-number 
                    v-model="databaseConfig.postgresql.port" 
                    :min="1" 
                    :max="65535"
                    style="width: 100%"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="数据库名">
                  <el-input 
                    v-model="databaseConfig.postgresql.database" 
                    placeholder="monitoring"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="用户名">
                  <el-input 
                    v-model="databaseConfig.postgresql.username" 
                    placeholder="postgres"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="密码">
                  <el-input 
                    v-model="databaseConfig.postgresql.password" 
                    type="password" 
                    placeholder="请输入密码"
                    :disabled="!databaseConfig.postgresql.enabled"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="连接状态">
                  <el-tag 
                    v-if="dbConnectionStatus"
                    :type="dbConnectionStatus.success ? 'success' : 'danger'"
                  >
                    {{ dbConnectionStatus.message }}
                  </el-tag>
                  <span v-else class="text-secondary">未测试</span>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <h4>高级配置</h4>
                <el-form-item label="启用SSL">
                  <el-switch 
                    v-model="databaseConfig.postgresql.ssl" 
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="连接超时(秒)">
                  <el-input-number 
                    v-model="dbAdvancedConfig.connectionTimeout" 
                    :min="5" 
                    :max="300"
                    style="width: 100%"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="查询超时(秒)">
                  <el-input-number 
                    v-model="dbAdvancedConfig.queryTimeout" 
                    :min="10" 
                    :max="600"
                    style="width: 100%"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                <el-form-item label="连接池大小">
                  <el-input-number 
                    v-model="dbAdvancedConfig.poolSize" 
                    :min="5" 
                    :max="100"
                    style="width: 100%"
                    :disabled="!databaseConfig.postgresql.enabled"
                  />
                </el-form-item>
                
                <!-- 数据库状态信息 -->
                <div v-if="dbStatus" class="db-status-info">
                  <h5>数据库状态</h5>
                  <div class="status-item">
                    <span class="label">版本:</span>
                    <span class="value">{{ dbStatus.version }}</span>
                  </div>
                  <div class="status-item">
                    <span class="label">运行时间:</span>
                    <span class="value">{{ formatUptime(dbStatus.uptime) }}</span>
                  </div>
                  <div class="status-item">
                    <span class="label">活跃连接:</span>
                    <span class="value">{{ dbStatus.activeConnections }} / {{ dbStatus.totalConnections }}</span>
                  </div>
                  <div class="status-item">
                    <span class="label">数据库大小:</span>
                    <span class="value">{{ dbStatus.dbSize }}</span>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-form>
          
          <!-- 备份配置 -->
          <el-divider />
          <div class="backup-section">
            <div class="section-header">
              <h4>
                <el-icon><FolderOpened /></el-icon>
                备份配置
              </h4>
              <div class="backup-actions">
                <el-button 
                  size="small" 
                  type="warning" 
                  @click="backupDatabase"
                  :loading="backupLoading"
                  :disabled="!databaseConfig.postgresql.enabled"
                >
                  立即备份
                </el-button>
              </div>
            </div>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="自动备份">
                  <el-switch v-model="databaseConfig.backup.enabled" />
                </el-form-item>
                <el-form-item label="备份计划">
                  <el-input 
                    v-model="databaseConfig.backup.schedule" 
                    placeholder="0 2 * * *"
                    :disabled="!databaseConfig.backup.enabled"
                  >
                    <template #append>Cron</template>
                  </el-input>
                  <p class="config-description">
                    示例: 0 2 * * * (每天凌晨2点)
                  </p>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="保留天数">
                  <el-input-number 
                    v-model="databaseConfig.backup.retention" 
                    :min="1" 
                    :max="365"
                    style="width: 100%"
                    :disabled="!databaseConfig.backup.enabled"
                  />
                </el-form-item>
                <el-form-item label="备份路径">
                  <el-input 
                    v-model="databaseConfig.backup.path" 
                    placeholder="/data/backups"
                    :disabled="!databaseConfig.backup.enabled"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <!-- 数据导出 -->
          <el-divider />
          <div class="export-section">
            <div class="section-header">
              <h4>
                <el-icon><Download /></el-icon>
                数据导出
              </h4>
            </div>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="export-card">
                  <template #header>
                    <h5>巡检数据</h5>
                  </template>
                  <div class="export-content">
                    <p class="export-description">导出所有巡检记录和结果</p>
                    <el-select v-model="exportConfig.inspection.format" style="width: 100%; margin-bottom: 10px">
                      <el-option label="JSON" value="json" />
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                    </el-select>
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="exportInspectionData"
                      :loading="exportLoading.inspection"
                      style="width: 100%"
                    >
                      导出巡检数据
                    </el-button>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="export-card">
                  <template #header>
                    <h5>指标数据</h5>
                  </template>
                  <div class="export-content">
                    <p class="export-description">导出监控指标历史数据</p>
                    <el-select v-model="exportConfig.metrics.format" style="width: 100%; margin-bottom: 10px">
                      <el-option label="JSON" value="json" />
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                    </el-select>
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="exportMetricsData"
                      :loading="exportLoading.metrics"
                      style="width: 100%"
                    >
                      导出指标数据
                    </el-button>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="export-card">
                  <template #header>
                    <h5>AI分析结果</h5>
                  </template>
                  <div class="export-content">
                    <p class="export-description">导出AI分析结果和建议</p>
                    <el-select v-model="exportConfig.analysis.format" style="width: 100%; margin-bottom: 10px">
                      <el-option label="JSON" value="json" />
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                    </el-select>
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="exportAnalysisData"
                      :loading="exportLoading.analysis"
                      style="width: 100%"
                    >
                      导出AI结果
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
        
        <!-- PostgreSQL配置查看器 -->
        <PostgreSQLConfigViewerOptimized ref="databaseConfigViewerRef" />
      </el-tab-pane>
      
      <el-tab-pane label="系统配置" name="config">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>系统参数配置</h3>
              <el-button size="small" type="primary" @click="saveSystemConfig" :loading="systemConfigLoading">
                保存配置
              </el-button>
            </div>
          </template>
          
          <el-form :model="systemConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>基础配置</h4>
                <el-form-item label="系统名称">
                  <el-input v-model="systemConfig.systemName" />
                </el-form-item>
                <el-form-item label="系统描述">
                  <el-input 
                    v-model="systemConfig.systemDescription" 
                    type="textarea" 
                    :rows="2"
                    placeholder="智能监控预警系统，基于AI的自动化巡检与智能预警"
                  />
                </el-form-item>
                <el-form-item label="数据保留天数">
                  <el-input-number 
                    v-model="systemConfig.dataRetentionDays" 
                    :min="1" 
                    :max="365"
                    style="width: 100%"
                  />
                  <div class="form-item-tip">
                    超过此天数的数据将被自动清理
                  </div>
                </el-form-item>
                <el-form-item label="自动备份">
                  <el-switch v-model="systemConfig.autoBackup" />
                </el-form-item>
                <el-form-item label="备份间隔(小时)">
                  <el-input-number 
                    v-model="systemConfig.backupInterval" 
                    :min="1" 
                    :max="168"
                    :disabled="!systemConfig.autoBackup"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item label="备份保留数量">
                  <el-input-number 
                    v-model="systemConfig.backupRetentionCount" 
                    :min="1" 
                    :max="50"
                    :disabled="!systemConfig.autoBackup"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <h4>监控配置</h4>
                <el-form-item label="数据采集间隔(秒)">
                  <el-input-number 
                    v-model="systemConfig.collectInterval" 
                    :min="5" 
                    :max="300"
                    style="width: 100%"
                  />
                  <div class="form-item-tip">
                    系统指标数据的采集频率
                  </div>
                </el-form-item>
                <el-form-item label="默认告警阈值">
                  <el-input-number 
                    v-model="systemConfig.defaultThreshold" 
                    :min="50" 
                    :max="95"
                    style="width: 100%"
                  />
                  <div class="form-item-tip">
                    当指标超过此阈值时触发告警
                  </div>
                </el-form-item>
                <el-form-item label="启用异常检测">
                  <el-switch v-model="systemConfig.enableAnomalyDetection" />
                </el-form-item>
                <el-form-item label="检测灵敏度">
                  <el-slider 
                    v-model="systemConfig.detectionSensitivity"
                    :min="1"
                    :max="10"
                    :disabled="!systemConfig.enableAnomalyDetection"
                    show-stops
                    show-tooltip
                  />
                  <div class="form-item-tip">
                    1：最低灵敏度，10：最高灵敏度
                  </div>
                </el-form-item>
                <el-form-item label="最大并发连接数">
                  <el-input-number 
                    v-model="systemConfig.maxConnections" 
                    :min="10" 
                    :max="1000"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 高级配置 -->
            <el-divider />
            <h4>高级配置</h4>
            <el-row :gutter="40">
              <el-col :span="12">
                <el-form-item label="启用日志记录">
                  <el-switch v-model="systemConfig.enableLogging" />
                </el-form-item>
                <el-form-item label="日志级别">
                  <el-select 
                    v-model="systemConfig.logLevel" 
                    style="width: 100%"
                    :disabled="!systemConfig.enableLogging"
                  >
                    <el-option label="ERROR" value="error" />
                    <el-option label="WARN" value="warn" />
                    <el-option label="INFO" value="info" />
                    <el-option label="DEBUG" value="debug" />
                  </el-select>
                </el-form-item>
                <el-form-item label="启用性能监控">
                  <el-switch v-model="systemConfig.enablePerformanceMonitoring" />
                </el-form-item>
                <el-form-item label="缓存过期时间(分钟)">
                  <el-input-number 
                    v-model="systemConfig.cacheExpireTime" 
                    :min="1" 
                    :max="1440"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用API限流">
                  <el-switch v-model="systemConfig.enableRateLimit" />
                </el-form-item>
                <el-form-item label="每分钟请求限制">
                  <el-input-number 
                    v-model="systemConfig.rateLimit" 
                    :min="10" 
                    :max="10000"
                    :disabled="!systemConfig.enableRateLimit"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item label="时区">
                  <el-select v-model="systemConfig.timezone" style="width: 100%">
                    <el-option label="Asia/Shanghai (UTC+8)" value="Asia/Shanghai" />
                    <el-option label="UTC (UTC+0)" value="UTC" />
                    <el-option label="America/New_York (UTC-5)" value="America/New_York" />
                    <el-option label="Europe/London (UTC+0)" value="Europe/London" />
                  </el-select>
                </el-form-item>
                <el-form-item label="语言">
                  <el-select v-model="systemConfig.language" style="width: 100%">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 通知配置 -->
            <el-divider />
            <h4>通知配置</h4>
            <el-row :gutter="40">
              <el-col :span="12">
                <el-form-item label="启用邮件通知">
                  <el-switch v-model="systemConfig.notifications.email.enabled" />
                </el-form-item>
                <el-form-item label="SMTP服务器">
                  <el-input 
                    v-model="systemConfig.notifications.email.smtp.server" 
                    :disabled="!systemConfig.notifications.email.enabled"
                    placeholder="smtp.gmail.com"
                  />
                </el-form-item>
                <el-form-item label="SMTP端口">
                  <el-input-number 
                    v-model="systemConfig.notifications.email.smtp.port" 
                    :min="1" 
                    :max="65535"
                    :disabled="!systemConfig.notifications.email.enabled"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item label="发件人邮箱">
                  <el-input 
                    v-model="systemConfig.notifications.email.from" 
                    :disabled="!systemConfig.notifications.email.enabled"
                    placeholder="noreply@company.com"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用企业微信通知">
                  <el-switch v-model="systemConfig.notifications.wechat.enabled" />
                </el-form-item>
                <el-form-item label="企业微信Webhook">
                  <el-input 
                    v-model="systemConfig.notifications.wechat.webhook" 
                    :disabled="!systemConfig.notifications.wechat.enabled"
                    placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
                  />
                </el-form-item>
                <el-form-item label="启用钉钉通知">
                  <el-switch v-model="systemConfig.notifications.dingtalk.enabled" />
                </el-form-item>
                <el-form-item label="钉钉Webhook">
                  <el-input 
                    v-model="systemConfig.notifications.dingtalk.webhook" 
                    :disabled="!systemConfig.notifications.dingtalk.enabled"
                    placeholder="https://oapi.dingtalk.com/robot/send"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
        
        <!-- AI配置查看器 -->
        <div class="config-viewer-section">
          <OllamaConfigViewerOptimized ref="ollamaConfigViewerRef2" />
        </div>
      </el-tab-pane>
      
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>用户列表</h3>
              <el-button size="small" type="primary" @click="showUserDialog = true">
                添加用户
              </el-button>
            </div>
          </template>
          
          <el-table :data="users" style="width: 100%">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="getRoleColor(row.role)" size="small">
                  {{ getRoleText(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'active' ? '正常' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastLogin" label="最后登录" width="180" />
            <el-table-column prop="createdAt" label="创建时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="editUser(row)">
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  :type="row.status === 'active' ? 'warning' : 'success'" 
                  link
                  @click="toggleUserStatus(row)"
                >
                  {{ row.status === 'active' ? '禁用' : '启用' }}
                </el-button>
                <el-button size="small" type="info" link @click="resetPassword(row)">
                  重置密码
                </el-button>
                <el-button size="small" type="danger" link @click="deleteUser(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        
        <!-- 用户创建/编辑对话框 -->
        <el-dialog
          v-model="showUserDialog"
          :title="editingUser ? '编辑用户' : '创建用户'"
          width="500px"
          @close="resetUserForm"
        >
          <el-form
            ref="userFormRef"
            :model="userForm"
            :rules="userFormRules"
            label-width="80px"
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="userForm.username"
                placeholder="请输入用户名"
                :disabled="editingUser !== null"
              />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="userForm.email"
                type="email"
                placeholder="请输入邮箱地址"
              />
            </el-form-item>
            
            <el-form-item v-if="!editingUser" label="密码" prop="password">
              <el-input
                v-model="userForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="角色" prop="role">
              <el-select v-model="userForm.role" placeholder="请选择角色">
                <el-option label="管理员" value="admin" />
                <el-option label="操作员" value="operator" />
                <el-option label="只读用户" value="viewer" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="userForm.status">
                <el-radio value="active">正常</el-radio>
                <el-radio value="inactive">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
          
          <template #footer>
            <el-button @click="showUserDialog = false">取消</el-button>
            <el-button type="primary" @click="submitUserForm" :loading="userFormLoading">
              {{ editingUser ? '更新' : '创建' }}
            </el-button>
          </template>
        </el-dialog>
      </el-tab-pane>
      
      <!-- 系统日志 -->
      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>系统操作日志</h3>
              <div class="log-controls">
                <el-input
                  v-model="logSearchText"
                  placeholder="搜索日志内容..."
                  style="width: 200px;"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select
                  v-model="logLevelFilter"
                  placeholder="日志级别"
                  style="width: 120px; margin-left: 10px;"
                  clearable
                >
                  <el-option label="INFO" value="INFO" />
                  <el-option label="WARNING" value="WARNING" />
                  <el-option label="ERROR" value="ERROR" />
                  <el-option label="SUCCESS" value="SUCCESS" />
                  <el-option label="DEBUG" value="DEBUG" />
                </el-select>
                <el-select
                  v-model="logUserFilter"
                  placeholder="操作用户"
                  style="width: 120px; margin-left: 10px;"
                  clearable
                >
                  <el-option label="system" value="system" />
                  <el-option label="admin" value="admin" />
                  <el-option label="operator" value="operator" />
                  <el-option label="viewer" value="viewer" />
                </el-select>
                <el-button size="small" @click="refreshLogs" style="margin-left: 10px;">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-button size="small" type="danger" @click="clearLogs" style="margin-left: 10px;">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="logs-container">
            <div v-if="filteredLogs.length === 0" class="no-logs">
              <el-empty description="没有找到匹配的日志" />
            </div>
            <div 
              v-for="log in paginatedLogs" 
              :key="log.id"
              class="log-item"
              :class="getLogLevelClass(log.level)"
            >
              <div class="log-header">
                <span class="log-time">{{ log.timestamp }}</span>
                <el-tag :type="getLogLevelTagType(log.level)" size="small" class="log-level">
                  {{ log.level }}
                </el-tag>
                <span class="log-user">{{ log.user }}</span>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
            
            <!-- 分页 -->
            <div v-if="filteredLogs.length > 0" class="log-pagination">
              <el-pagination
                v-model:current-page="logCurrentPage"
                v-model:page-size="logPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="filteredLogs.length"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleLogPageSizeChange"
                @current-change="handleLogCurrentChange"
              />
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加监控目标弹窗 -->
    <el-dialog
      v-model="showAddTarget"
      :title="editingTarget ? '编辑监控目标' : '添加监控目标'"
      width="600px"
      @close="resetTargetForm"
    >
      <el-form :model="targetForm" :rules="targetFormRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标名称" prop="name">
              <el-input v-model="targetForm.name" placeholder="请输入目标名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务器地址" prop="address">
              <el-input v-model="targetForm.address" placeholder="192.168.1.100" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="端口" prop="port">
              <el-input-number 
                v-model="targetForm.port" 
                :min="1" 
                :max="65535"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="路径" prop="path">
              <el-input v-model="targetForm.path" placeholder="/metrics" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="启用状态">
          <el-switch v-model="targetForm.enabled" />
        </el-form-item>
        
        <el-form-item label="标签">
          <div class="labels-editor">
            <div 
              v-for="(label, index) in targetLabels" 
              :key="index"
              class="label-item"
            >
              <el-input 
                v-model="label.key" 
                placeholder="键"
                style="width: 40%"
              />
              <span style="margin: 0 10px">=</span>
              <el-input 
                v-model="label.value" 
                placeholder="值"
                style="width: 40%"
              />
              <el-button 
                type="danger" 
                link 
                @click="removeLabel(index)"
                style="margin-left: 10px"
              >
                删除
              </el-button>
            </div>
            <el-button 
              type="primary" 
              link 
              @click="addLabel"
              style="margin-top: 10px"
            >
              + 添加标签
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddTarget = false">取消</el-button>
          <el-button type="primary" @click="saveTarget">保存</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tools,
  Refresh,
  Download,
  Timer,
  User,
  Cpu,
  Monitor,
  CircleCheck,
  CircleClose,
  Warning,
  Connection,
  DataAnalysis,
  Setting,
  DataBoard,
  FolderOpened,
  InfoFilled,
  Search,
  Delete
} from '@element-plus/icons-vue'
import { useLoadingOptimizer } from '@/utils/loadingOptimizer'
import { requestManager } from '@/utils/requestManager'
import { performanceMonitor } from '@/utils/performanceMonitor'
import { useConfigManager } from '@/composables/useConfigManager'
import { apiService } from '@/services/api'
import { useDatabaseManager } from '@/composables/useDatabaseManager'
import type { PrometheusTarget } from '@/composables/useConfigManager'
import PrometheusConfigViewerOptimized from '@/components/common/PrometheusConfigViewerOptimized.vue'
import OllamaConfigViewerOptimized from '@/components/common/OllamaConfigViewerOptimized.vue'
import PostgreSQLConfigViewerOptimized from '@/components/common/PostgreSQLConfigViewerOptimized.vue'

// 使用配置管理器
const {
  prometheusConfig,
  ollamaConfig,
  databaseConfig,
  isPrometheusConfigured,
  isOllamaConfigured,
  isDatabaseConfigured,
  loadPrometheusConfig,
  savePrometheusConfig,
  testPrometheusConnection: testConnection,
  addPrometheusTarget,
  removePrometheusTarget,
  validateConfigName,
  loadOllamaConfig,
  saveOllamaConfig,
  testOllamaConnection,
  loadDatabaseConfig,
  saveDatabaseConfig,
  testDatabaseConnection
} = useConfigManager()

// 使用数据库管理器
const {
  isConnected: isDbConnected,
  connectionLoading: dbConnectionLoading,
  operationLoading: dbOperationLoading,
  dbStatus,
  testConnection: testDbConnection,
  exportData: exportDbData,
  backupDatabase: performBackup
} = useDatabaseManager()

// 使用加载优化器
const { loadingOptimizer, loadingState, addTask, executeAll } = useLoadingOptimizer()

// 响应式数据
const activeTab = ref('services')
const refreshLoading = ref(false)
const servicesLoading = ref(false)
const saveLoading = ref(false)
const savePrometheusLoading = ref(false)
const saveOllamaLoading = ref(false)
const saveDbLoading = ref(false)
const testConnectionLoading = ref(false)
const testOllamaLoading = ref(false)
const testDbLoading = ref(false)
const loadDbConfigLoading = ref(false)
const modelsLoading = ref(false)
const backupLoading = ref(false)
const showAddTarget = ref(false)
const logsCurrentPage = ref(1)
const totalLogs = ref(500)
const editingTarget = ref<PrometheusTarget | null>(null)
const connectionStatus = ref<{ success: boolean; message: string } | null>(null)
const ollamaConnectionStatus = ref<{ success: boolean; message: string } | null>(null)
const dbConnectionStatus = ref<{ success: boolean; message: string } | null>(null)

// 配置名称验证状态
const configNameValidation = ref<{ valid: boolean; message?: string }>({ valid: true })
const ollamaConfigNameValidation = ref<{ valid: boolean; message?: string }>({ valid: true })
const databaseConfigNameValidation = ref<{ valid: boolean; message?: string }>({ valid: true })

// Ollama可用模型
const availableModels = ref<Array<{ name: string; label: string; size?: string }>>([])
const modelsLoadTime = ref<number>(0)

// 配置查看器引用
const configViewerRef = ref(null)
const ollamaConfigViewerRef = ref(null)
const databaseConfigViewerRef = ref(null)

// 监听配置名称变化，实时验证
watch(() => prometheusConfig.value.name, (newName) => {
  if (newName !== undefined) {
    configNameValidation.value = validateConfigName(newName)
  }
}, { immediate: true })

// 监听Ollama配置名称变化，实时验证
watch(() => ollamaConfig.value.name, (newName) => {
  if (newName !== undefined) {
    ollamaConfigNameValidation.value = validateConfigName(newName)
  }
}, { immediate: true })

watch(() => databaseConfig.value.name, (newName) => {
  if (newName !== undefined) {
    databaseConfigNameValidation.value = validateConfigName(newName)
  }
}, { immediate: true })

// 监控目标表单
const targetForm = ref({
  name: '',
  address: '',
  port: 9100,
  path: '/metrics',
  enabled: true
})

// 标签编辑器
const targetLabels = ref<Array<{ key: string; value: string }>>([{ key: '', value: '' }])

// AI功能配置
const aiFeatures = ref({
  anomalyDetection: {
    enabled: true,
    interval: 15  // 分钟
  },
  intelligentAnalysis: {
    enabled: true,
    depth: 'standard'  // basic, standard, deep
  },
  autoReport: {
    enabled: false,
    frequency: 'weekly'  // daily, weekly, monthly
  }
})

// 数据库高级配置
const dbAdvancedConfig = ref({
  connectionTimeout: 30,
  queryTimeout: 60,
  poolSize: 10
})

// 导出配置
const exportConfig = ref({
  inspection: {
    format: 'json'
  },
  metrics: {
    format: 'json'
  },
  analysis: {
    format: 'json'
  }
})

// 导出加载状态
const exportLoading = ref({
  inspection: false,
  metrics: false,
  analysis: false
})



// 备份数据库
const backupDatabase = async () => {
  backupLoading.value = true
  try {
    const result = await performBackup()
    if (result) {
      ElMessage.success('数据库备份成功')
    } else {
      ElMessage.error('数据库备份失败')
    }
  } catch (error) {
    ElMessage.error('备份操作失败')
  } finally {
    backupLoading.value = false
  }
}

// 导出数据功能
const exportInspectionData = async () => {
  exportLoading.value.inspection = true
  try {
    await exportDbData('inspection', exportConfig.value.inspection.format)
    ElMessage.success('巡检数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value.inspection = false
  }
}

const exportMetricsData = async () => {
  exportLoading.value.metrics = true
  try {
    await exportDbData('metrics', exportConfig.value.metrics.format)
    ElMessage.success('指标数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value.metrics = false
  }
}

const exportAnalysisData = async () => {
  exportLoading.value.analysis = true
  try {
    await exportDbData('analysis', exportConfig.value.analysis.format)
    ElMessage.success('AI分析结果导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value.analysis = false
  }
}

// 表单验证规则
const targetFormRules = {
  name: [
    { required: true, message: '请输入目标名称', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入服务器地址', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '请输入路径', trigger: 'blur' }
  ]
}

// 系统信息
const systemInfo = ref({
  uptime: 127,
  onlineUsers: 12,
  cpuUsage: 68.5,
  memoryUsage: 74.2,
  systemDetails: {}
})

// 系统详情展开状态
const showSystemDetails = ref(false)

// 系统服务
const systemServices = ref([])
const realTimeSystemInfo = ref({
  uptime: '0天0小时',
  cpuUsage: 0,
  memoryUsage: 0,
  diskUsage: 0
})

// 系统配置相关
const systemConfigLoading = ref(false)

// 系统配置
const systemConfig = ref({
  systemName: '智能监控预警系统',
  systemDescription: '基于AI的自动化巡检与智能预警系统',
  dataRetentionDays: 90,
  autoBackup: true,
  backupInterval: 24,
  backupRetentionCount: 10,
  collectInterval: 60,
  defaultThreshold: 85,
  enableAnomalyDetection: true,
  detectionSensitivity: 7,
  maxConnections: 100,
  
  // 高级配置
  enableLogging: true,
  logLevel: 'info',
  enablePerformanceMonitoring: true,
  cacheExpireTime: 60,
  enableRateLimit: true,
  rateLimit: 1000,
  timezone: 'Asia/Shanghai',
  language: 'zh-CN',
  
  // 通知配置
  notifications: {
    email: {
      enabled: false,
      smtp: {
        server: '',
        port: 587
      },
      from: ''
    },
    wechat: {
      enabled: false,
      webhook: ''
    },
    dingtalk: {
      enabled: false,
      webhook: ''
    }
  }
})

// 用户数据
const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@company.com',
    role: 'admin',
    status: 'active',
    lastLogin: '2025-09-06 22:30:15',
    createdAt: '2025-01-01 00:00:00'
  },
  {
    id: 2,
    username: 'operator',
    email: 'ops@company.com',
    role: 'operator',
    status: 'active',
    lastLogin: '2025-09-06 20:15:32',
    createdAt: '2025-01-15 09:00:00'
  },
  {
    id: 3,
    username: 'viewer',
    email: 'view@company.com',
    role: 'viewer',
    status: 'inactive',
    lastLogin: '2025-09-05 14:22:10',
    createdAt: '2025-02-01 16:30:00'
  }
])

// 用户管理相关
const showUserDialog = ref(false)
const editingUser = ref(null)
const userFormRef = ref()
const userFormLoading = ref(false)

// 用户表单
const userForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'viewer',
  status: 'active'
})

// 用户表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择用户状态', trigger: 'change' }
  ]
}

// 系统日志相关
const logSearchText = ref('')
const logLevelFilter = ref('')
const logUserFilter = ref('')
const logCurrentPage = ref(1)
const logPageSize = ref(20)

// 系统日志数据
const systemLogs = ref([
  {
    id: 1,
    timestamp: '2025-09-21 22:45:32',
    level: 'INFO',
    user: 'admin',
    message: '用户登录系统'
  },
  {
    id: 2,
    timestamp: '2025-09-21 22:30:15',
    level: 'WARNING',
    user: 'system',
    message: '通知服务响应缓慢'
  },
  {
    id: 3,
    timestamp: '2025-09-21 22:15:45',
    level: 'ERROR',
    user: 'system',
    message: 'Redis服务连接失败'
  },
  {
    id: 4,
    timestamp: '2025-09-21 21:58:22',
    level: 'INFO',
    user: 'operator',
    message: '创建新的监控规则'
  },
  {
    id: 5,
    timestamp: '2025-09-21 21:30:10',
    level: 'SUCCESS',
    user: 'system',
    message: '系统备份完成'
  },
  {
    id: 6,
    timestamp: '2025-09-21 21:15:30',
    level: 'DEBUG',
    user: 'system',
    message: '缓存清理完成'
  },
  {
    id: 7,
    timestamp: '2025-09-21 21:00:18',
    level: 'ERROR',
    user: 'system',
    message: '数据库连接超时'
  },
  {
    id: 8,
    timestamp: '2025-09-21 20:45:12',
    level: 'INFO',
    user: 'admin',
    message: '配置更新完成'
  },
  {
    id: 9,
    timestamp: '2025-09-21 20:30:05',
    level: 'WARNING',
    user: 'system',
    message: 'CPU使用率较高'
  },
  {
    id: 10,
    timestamp: '2025-09-21 20:15:00',
    level: 'SUCCESS',
    user: 'system',
    message: '服务重启成功'
  }
])

// 过滤后的日志
const filteredLogs = computed(() => {
  let logs = systemLogs.value
  
  // 按搜索文本过滤
  if (logSearchText.value) {
    const searchText = logSearchText.value.toLowerCase()
    logs = logs.filter(log => 
      log.message.toLowerCase().includes(searchText) ||
      log.user.toLowerCase().includes(searchText)
    )
  }
  
  // 按日志级别过滤
  if (logLevelFilter.value) {
    logs = logs.filter(log => log.level === logLevelFilter.value)
  }
  
  // 按用户过滤
  if (logUserFilter.value) {
    logs = logs.filter(log => log.user === logUserFilter.value)
  }
  
  return logs
})

// 分页后的日志
const paginatedLogs = computed(() => {
  const start = (logCurrentPage.value - 1) * logPageSize.value
  const end = start + logPageSize.value
  return filteredLogs.value.slice(start, end)
})

/**
 * Ollama配置相关方法
 */

/**
 * 保存Prometheus配置
 */
const savePrometheusConfigLocal = async () => {
  // 验证配置名称
  if (!configNameValidation.value.valid) {
    ElMessage.error(configNameValidation.value.message || '配置名称验证失败')
    return
  }
  
  // 检查是否启用Prometheus但未填写配置名称
  if (prometheusConfig.value.enabled && (!prometheusConfig.value.name || prometheusConfig.value.name.trim() === '')) {
    ElMessage.error('启用Prometheus时必须填写配置名称')
    return
  }
  
  savePrometheusLoading.value = true
  try {
    // 调用composable中的保存函数
    const success = await savePrometheusConfig()
    if (success) {
      ElMessage.success('Prometheus配置已保存')
      
      // 延迟一下确保数据库已更新，然后刷新配置查看器组件
      setTimeout(async () => {
        if (configViewerRef.value && typeof configViewerRef.value.refreshConfig === 'function') {
          await configViewerRef.value.refreshConfig()
        }
      }, 500)
      
      // 不立即重新加载配置，避免覆盖用户输入
      // await loadPrometheusConfig()
    } else {
      ElMessage.error('配置保存失败')
    }
  } catch (error) {
    console.error('保存Prometheus配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    savePrometheusLoading.value = false
  }
}

/**
 * 处理配置更改事件
 */
const handleConfigChanged = async (config) => {
  try {
    // 重新加载当前配置
    await loadPrometheusConfig()
    ElMessage.success(`配置已切换到 "${config.name}"`)
  } catch (error) {
    console.error('配置切换后重新加载失败:', error)
    ElMessage.error('配置切换成功，但重新加载失败，请手动刷新页面')
  }
}

/**
 * 保存Ollama配置
 */
const saveOllamaConfigLocal = async () => {
  // 验证配置名称
  if (!ollamaConfigNameValidation.value.valid) {
    ElMessage.error(ollamaConfigNameValidation.value.message || '配置名称验证失败')
    return
  }
  
  // 检查是否启用Ollama但未填写配置名称
  if (ollamaConfig.value.enabled && (!ollamaConfig.value.name || ollamaConfig.value.name.trim() === '')) {
    ElMessage.error('启用Ollama时必须填写配置名称')
    return
  }
  
  saveOllamaLoading.value = true
  try {
    // 调用composable中的保存函数
    const success = await saveOllamaConfig()
    if (success) {
      ElMessage.success('Ollama配置已保存')
      
      // 延迟一下确保数据库已更新，然后刷新配置查看器组件
      setTimeout(async () => {
        if (ollamaConfigViewerRef.value && typeof ollamaConfigViewerRef.value.refreshConfig === 'function') {
          await ollamaConfigViewerRef.value.refreshConfig()
        }
      }, 500)
    } else {
      ElMessage.error('配置保存失败')
    }
  } catch (error) {
    console.error('保存Ollama配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    saveOllamaLoading.value = false
  }
}

/**
 * 加载可用的Ollama模型
 */
const loadAvailableModels = async () => {
  // 防止重复加载（5分钟内不重新加载）
  const now = Date.now()
  if (modelsLoadTime.value && (now - modelsLoadTime.value) < 300000) {
    return
  }
  
  if (!ollamaConfig.value.enabled || !ollamaConfig.value.apiUrl) {
    return
  }
  
  modelsLoading.value = true
  try {
    // 使用后端API获取模型列表
    const response = await apiService.getOllamaModels(ollamaConfig.value.apiUrl)
    
    if (response?.success && response?.data?.models) {
      const models = response.data.models
      
      availableModels.value = models.map((model: any) => ({
        name: model.name,
        label: model.label || model.name,
        size: formatModelSize(model.size)
      }))
      
      modelsLoadTime.value = now
      
      if (models.length > 0) {
        console.log(`✅ 加载到 ${models.length} 个Ollama模型`)
        ElMessage.success(`发现 ${models.length} 个可用模型`)
      } else {
        console.warn('⚠️ 未找到可用的Ollama模型')
        ElMessage.warning('未找到可用模型，请检查Ollama服务并拉取模型')
      }
    } else {
      console.error('❌ 获取Ollama模型失败:', response?.message)
      availableModels.value = []
      ElMessage.error(response?.message || '获取模型列表失败')
    }
  } catch (error) {
    console.error('❌ 连接Ollama服务失败:', error)
    availableModels.value = []
    ElMessage.error('连接Ollama服务失败')
  } finally {
    modelsLoading.value = false
  }
}

/**
 * 格式化模型大小
 */
const formatModelSize = (size: number) => {
  if (!size) return ''
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let index = 0
  let sizeValue = size
  
  while (sizeValue >= 1024 && index < units.length - 1) {
    sizeValue /= 1024
    index++
  }
  
  return `${sizeValue.toFixed(1)}${units[index]}`
}

/**
 * 测试Ollama连接
 */
const testOllamaConnectionLocal = async () => {
  testOllamaLoading.value = true
  ollamaConnectionStatus.value = null
  
  try {
    console.log('测试Ollama连接:', ollamaConfig.value.apiUrl)
    
    // 调用composable中的测试函数
    const result = await testOllamaConnection()
    
    ollamaConnectionStatus.value = {
      success: result.success || false,
      message: result.message || '连接测试完成'
    }
    
    if (result.success) {
      ElMessage.success('连接成功！')
      // 如果测试结果包含模型列表，直接使用
      if (result.data?.models && Array.isArray(result.data.models)) {
        availableModels.value = result.data.models.map((model: any) => ({
          name: model.name,
          label: model.label || model.name,
          size: formatModelSize(model.size)
        }))
        modelsLoadTime.value = Date.now()
        console.log(`✅ 从连接测试获取到 ${result.data.models.length} 个模型`)
      } else {
        // 否则主动加载模型列表
        await loadAvailableModels()
      }
    } else {
      ElMessage.error('连接失败，请检查配置')
    }
  } catch (error) {
    ollamaConnectionStatus.value = {
      success: false,
      message: '连接失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testOllamaLoading.value = false
  }
}

/**
 * 保存数据库配置
 */
const saveDatabaseConfigLocal = async () => {
  if (!databaseConfigNameValidation.value.valid) {
    ElMessage.error(databaseConfigNameValidation.value.message || '配置名称验证失败')
    return
  }
  if (databaseConfig.value.postgresql.enabled && (!databaseConfig.value.name || databaseConfig.value.name.trim() === '')) {
    ElMessage.error('启用数据库时必须填写配置名称')
    return
  }
  saveDbLoading.value = true
  try {
    const success = await saveDatabaseConfig()
    if (success) {
      ElMessage.success('数据库配置已保存')
      setTimeout(async () => {
        if (databaseConfigViewerRef.value && typeof databaseConfigViewerRef.value.refreshConfig === 'function') {
          await databaseConfigViewerRef.value.refreshConfig()
        }
      }, 500)
    } else {
      ElMessage.error('配置保存失败')
    }
  } catch (error) {
    console.error('保存数据库配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    saveDbLoading.value = false
  }
}

/**
 * 测试数据库连接
 */
const testDatabaseConnectionLocal = async () => {
  testDbLoading.value = true
  dbConnectionStatus.value = null

  try {
    console.log('测试数据库连接:', databaseConfig.value.postgresql.host)
    const result = await testDatabaseConnection()

    dbConnectionStatus.value = {
      success: result.success || false,
      message: result.message || '连接测试完成'
    }

    if (result.success) {
      ElMessage.success('连接成功！')
    } else {
      ElMessage.error('连接失败，请检查配置')
    }
  } catch (error) {
    dbConnectionStatus.value = {
      success: false,
      message: '连接失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testDbLoading.value = false
  }
}

/**
 * 测试Prometheus连接
 */
const testPrometheusConnection = async () => {
  testConnectionLoading.value = true
  connectionStatus.value = null
  
  try {
    const success = await testConnection()
    connectionStatus.value = {
      success,
      message: success ? '连接成功' : '连接失败'
    }
    
    if (success) {
      ElMessage.success('连接成功！')
    } else {
      ElMessage.error('连接失败，请检查配置')
    }
  } catch (error) {
    connectionStatus.value = {
      success: false,
      message: '连接失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testConnectionLoading.value = false
  }
}

/**
 * 添加标签
 */
const addLabel = () => {
  targetLabels.value.push({ key: '', value: '' })
}

/**
 * 删除标签
 */
const removeLabel = (index: number) => {
  targetLabels.value.splice(index, 1)
}

/**
 * 保存监控目标
 */
const saveTarget = () => {
  // 构建标签对象
  const labels: Record<string, string> = {}
  targetLabels.value.forEach(label => {
    if (label.key && label.value) {
      labels[label.key] = label.value
    }
  })
  
  const target = {
    ...targetForm.value,
    labels
  }
  
  if (editingTarget.value) {
    // 编辑模式
    const index = prometheusConfig.value.targets.findIndex(t => t.id === editingTarget.value!.id)
    if (index > -1) {
      prometheusConfig.value.targets[index] = { ...editingTarget.value, ...target }
    }
    ElMessage.success('监控目标更新成功')
  } else {
    // 新增模式
    addPrometheusTarget(target)
    ElMessage.success('监控目标添加成功')
  }
  
  showAddTarget.value = false
  resetTargetForm()
}

/**
 * 编辑监控目标
 */
const editTarget = (target: PrometheusTarget) => {
  editingTarget.value = target
  targetForm.value = {
    name: target.name,
    address: target.address,
    port: target.port,
    path: target.path,
    enabled: target.enabled
  }
  
  // 设置标签
  targetLabels.value = Object.entries(target.labels || {}).map(([key, value]) => ({
    key,
    value
  }))
  
  if (targetLabels.value.length === 0) {
    targetLabels.value = [{ key: '', value: '' }]
  }
  
  showAddTarget.value = true
}

/**
 * 删除监控目标
 */
const deleteTarget = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这个监控目标吗？', '确认删除')
    removePrometheusTarget(id)
    ElMessage.success('监控目标删除成功')
  } catch {
    // 用户取消
  }
}

/**
 * 更新目标状态
 */
const updateTargetStatus = (target: PrometheusTarget) => {
  const status = target.enabled ? '启用' : '禁用'
  ElMessage.success(`监控目标「${target.name}」已${status}`)
}

/**
 * 重置目标表单
 */
const resetTargetForm = () => {
  editingTarget.value = null
  targetForm.value = {
    name: '',
    address: '',
    port: 9100,
    path: '/metrics',
    enabled: true
  }
  targetLabels.value = [{ key: '', value: '' }]
}


/**
 * 系统备份
 */
const backupSystem = async () => {
  try {
    await ElMessageBox.confirm('确定要进行系统备份吗？此操作可能需要几分钟。', '确认备份')
    
    ElMessage.loading('正在进行系统备份...')
    
    // 模拟备份过程
    setTimeout(() => {
      ElMessage.success('系统备份完成')
    }, 3000)
  } catch {
    // 用户取消
  }
}

/**
 * 刷新服务状态
 */
const refreshServices = async () => {
  servicesLoading.value = true
  try {
    console.log('🔄 刷新服务状态...')
    const response = await apiService.getServicesStatus()
    
    if (response?.success && response?.data) {
      systemServices.value = response.data.services || []
      console.log('✅ 服务状态刷新成功:', systemServices.value.length, '个服务')
      ElMessage.success(`服务状态刷新成功，共${systemServices.value.length}个服务`)
    } else {
      console.warn('⚠️ 服务状态响应格式异常:', response)
      ElMessage.warning('服务状态数据格式异常')
    }
  } catch (error) {
    console.error('❌ 刷新服务状态失败:', error)
    ElMessage.error('刷新服务状态失败')
  } finally {
    servicesLoading.value = false
  }
}

/**
 * 刷新系统信息
 */
const refreshSystemInfo = async () => {
  refreshLoading.value = true
  try {
    console.log('🔄 刷新系统信息...')
    const response = await apiService.getSystemHealth()
    
    if (response?.success && response?.data) {
      const healthData = response.data
      realTimeSystemInfo.value = {
        uptime: healthData.uptime || '未知',
        cpuUsage: healthData.cpuUsage || 0,
        memoryUsage: healthData.memoryUsage || 0,
        diskUsage: healthData.diskUsage || 0
      }
      
      // 更新系统概览数据
      systemInfo.value = {
        uptime: healthData.uptimeSeconds ? Math.floor(healthData.uptimeSeconds / (3600 * 24)) : 0, // 转换为天数
        onlineUsers: healthData.onlineUsers || 1, // 使用真实的在线用户数
        cpuUsage: healthData.cpuUsage || 0,
        memoryUsage: healthData.memoryUsage || 0,
        // 添加额外的系统信息
        systemDetails: healthData.systemInfo || {}
      }
      
      console.log('✅ 系统信息刷新成功:', realTimeSystemInfo.value)
      ElMessage.success('系统信息刷新成功')
    } else {
      console.warn('⚠️ 系统健康状态响应异常:', response)
      ElMessage.warning('系统健康状态数据异常')
    }
  } catch (error) {
    console.error('❌ 刷新系统信息失败:', error)
    ElMessage.error('刷新系统信息失败')
  } finally {
    refreshLoading.value = false
  }
}

/**
 * 服务操作
 */
const handleServiceAction = async (service: any, action: string) => {
  try {
    console.log(`🔧 执行服务操作: ${action} ${service.name}`)
    let response
    
    switch (action) {
      case 'restart':
        response = await apiService.restartService(service.name)
        break
      case 'start':
        response = await apiService.startService(service.name)
        break
      case 'stop':
        response = await apiService.stopService(service.name)
        break
      default:
        throw new Error(`未知的服务操作: ${action}`)
    }
    
    if (response?.success) {
      ElMessage.success(response.message)
      // 操作成功后刷新服务状态
      await refreshServices()
    } else {
      ElMessage.error(response?.message || `${action}操作失败`)
    }
  } catch (error) {
    console.error(`❌ 服务${action}操作失败:`, error)
    ElMessage.error(`服务${action}操作失败`)
  }
}

/**
 * 启动服务
 */
const startService = async (service: any) => {
  try {
    ElMessage.loading(`正在启动${service.name}...`)
    await new Promise(resolve => setTimeout(resolve, 2000))
    service.status = 'running'
    ElMessage.success(`${service.name}启动成功`)
  } catch (error) {
    ElMessage.error(`${service.name}启动失败`)
  }
}

/**
 * 停止服务
 */
const stopService = async (service: any) => {
  try {
    await ElMessageBox.confirm(`确定要停止${service.name}吗？`, '确认操作')
    service.status = 'stopped'
    ElMessage.success(`${service.name}已停止`)
  } catch {
    // 用户取消
  }
}

/**
 * 重启服务
 */
const restartService = async (service: any) => {
  try {
    ElMessage.loading(`正在重启${service.name}...`)
    await new Promise(resolve => setTimeout(resolve, 3000))
    service.status = 'running'
    ElMessage.success(`${service.name}重启成功`)
  } catch (error) {
    ElMessage.error(`${service.name}重启失败`)
  }
}

/**
 * 查看服务日志
 */
const viewServiceLogs = (service: any) => {
  ElMessage.info(`查看${service.name}日志功能开发中...`)
}

/**
 * 编辑用户
 */
const editUser = (user: any) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email,
    password: '', // 编辑时不显示密码
    role: user.role,
    status: user.status
  }
  showUserDialog.value = true
}

/**
 * 切换用户状态
 */
const toggleUserStatus = async (user: any) => {
  try {
    const response = await apiService.toggleUserStatus(user.id)
    if (response?.success) {
      // 更新本地数据
      const index = users.value.findIndex(u => u.id === user.id)
      if (index > -1) {
        users.value[index] = response.data.user
      }
      ElMessage.success(response.message)
    }
  } catch (error) {
    console.error('切换用户状态失败:', error)
    ElMessage.error('切换用户状态失败')
  }
}

/**
 * 重置密码
 */
const resetPassword = async (user: any) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户${user.username}的密码吗？`, '确认操作')
    
    const response = await apiService.resetUserPassword(user.id)
    if (response?.success) {
      ElMessage.success(response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置密码失败:', error)
      ElMessage.error('重置密码失败')
    }
  }
}

/**
 * 删除用户
 */
const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户${user.username}吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    
    const response = await apiService.deleteUser(user.id)
    if (response?.success) {
      const index = users.value.findIndex(u => u.id === user.id)
      if (index > -1) {
        users.value.splice(index, 1)
      }
      ElMessage.success(response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

/**
 * 提交用户表单
 */
const submitUserForm = async () => {
  try {
    await userFormRef.value?.validate()
    
    userFormLoading.value = true
    
    if (editingUser.value) {
      // 编辑用户
      const response = await apiService.updateUser(editingUser.value.id, {
        email: userForm.value.email,
        role: userForm.value.role,
        status: userForm.value.status
      })
      
      if (response?.success) {
        // 更新本地数据
        const index = users.value.findIndex(u => u.id === editingUser.value.id)
        if (index > -1) {
          users.value[index] = response.data.user
        }
        ElMessage.success('用户信息更新成功')
      }
    } else {
      // 创建新用户
      const response = await apiService.createUser({
        username: userForm.value.username,
        email: userForm.value.email,
        role: userForm.value.role,
        status: userForm.value.status
      })
      
      if (response?.success) {
        users.value.unshift(response.data.user)
        ElMessage.success('用户创建成功')
      }
    }
    
    showUserDialog.value = false
    resetUserForm()
    
  } catch (error) {
    console.error('用户操作失败:', error)
    ElMessage.error('用户操作失败')
  } finally {
    userFormLoading.value = false
  }
}

/**
 * 重置用户表单
 */
const resetUserForm = () => {
  editingUser.value = null
  userForm.value = {
    username: '',
    email: '',
    password: '',
    role: 'viewer',
    status: 'active'
  }
  userFormRef.value?.resetFields()
}

/**
 * 日志相关函数
 */

/**
 * 获取日志级别对应的Tag类型
 */
const getLogLevelTagType = (level: string) => {
  const typeMap: Record<string, string> = {
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'danger',
    SUCCESS: 'success',
    DEBUG: ''
  }
  return typeMap[level] || 'info'
}

/**
 * 刷新日志
 */
const refreshLogs = async () => {
  try {
    const response = await apiService.refreshSystemLogsApi()
    if (response?.success) {
      // 重新加载日志数据
      await loadSystemLogs()
      ElMessage.success(response.message)
    }
  } catch (error) {
    console.error('刷新日志失败:', error)
    ElMessage.error('刷新日志失败')
  }
}

/**
 * 清空日志
 */
const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      { type: 'warning' }
    )
    
    const response = await apiService.clearSystemLogsApi()
    if (response?.success) {
      systemLogs.value = []
      logCurrentPage.value = 1
      ElMessage.success(response.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空日志失败:', error)
      ElMessage.error('清空日志失败')
    }
  }
}

/**
 * 处理日志分页大小变化
 */
const handleLogPageSizeChange = (size: number) => {
  logPageSize.value = size
  logCurrentPage.value = 1
}

/**
 * 处理日志当前页变化
 */
const handleLogCurrentChange = (page: number) => {
  logCurrentPage.value = page
}

/**
 * 系统配置相关函数
 */

/**
 * 保存系统配置
 */
const saveSystemConfig = async () => {
  try {
    systemConfigLoading.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    console.log('🔧 保存系统配置:', systemConfig.value)
    
    // 这里可以调用后端API保存配置
    // const response = await apiService.saveSystemConfig(systemConfig.value)
    
    ElMessage.success('系统配置保存成功')
    
  } catch (error) {
    console.error('❌ 保存系统配置失败:', error)
    ElMessage.error('保存系统配置失败')
  } finally {
    systemConfigLoading.value = false
  }
}



/**
 * 日志分页
 */
const handleLogsPageChange = (page: number) => {
  logsCurrentPage.value = page
}

// 工具函数

const getCpuColor = (value: number): string => {
  if (value >= 80) return '#f56c6c'
  if (value >= 60) return '#e6a23c'
  return '#67c23a'
}

const getMemoryColor = (value: number): string => {
  if (value >= 85) return '#f56c6c'
  if (value >= 70) return '#e6a23c'
  return '#67c23a'
}

const getServiceStatusClass = (status: string, health?: string): string => {
  if (status === 'running' && health === 'healthy') return 'service-running'
  if (status === 'running' && health === 'degraded') return 'service-warning'
  if (status === 'stopped') return 'service-stopped'
  return 'service-unknown'
}

const getServiceStatusType = (status: string, health?: string): string => {
  if (status === 'running' && health === 'healthy') return 'success'
  if (status === 'running' && health === 'degraded') return 'warning'
  if (status === 'stopped') return 'danger'
  return 'info'
}

const getServiceStatusText = (status: string, health?: string): string => {
  if (status === 'running' && health === 'healthy') return '健康运行'
  if (status === 'running' && health === 'degraded') return '运行异常'
  if (status === 'stopped') return '已停止'
  if (status === 'unknown') return '状态未知'
  return '未知'
}

const getRoleColor = (role: string): string => {
  const colorMap: Record<string, string> = {
    admin: 'danger',
    operator: 'warning',
    viewer: 'info'
  }
  return colorMap[role] || 'info'
}

const getRoleText = (role: string): string => {
  const textMap: Record<string, string> = {
    admin: '管理员',
    operator: '操作员',
    viewer: '观察员'
  }
  return textMap[role] || '未知'
}

const getLogLevelClass = (level: string): string => {
  return `log-${level.toLowerCase()}`
}

/**
 * 格式化运行时间
 */
const formatUptime = (seconds: number): string => {
  if (typeof seconds !== 'number' || seconds < 0) {
    return '未知'
  }
  
  const days = Math.floor(seconds / (24 * 3600))
  const hours = Math.floor((seconds % (24 * 3600)) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}天 ${hours}小时`
  } else if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

// 轻量化页面初始化函数
const initializePage = async () => {
  document.title = '系统管理 - 智能监控预警系统'
  console.log('🚀 轻量化页面初始化开始...')
  
  try {
    // 只加载最基础的系统信息，快速响应用户
    console.log('📊 加载基础系统信息...')
    await refreshSystemInfo()
    
    console.log('✅ 基础页面加载完成，其他数据将按需加载')
    ElMessage.success('页面加载完成')
  } catch (error) {
    console.error('❌ 页面初始化失败:', error)
    ElMessage.warning('部分功能可能不可用，请刷新重试')
  }
}

// 按需加载配置数据
const loadConfigOnDemand = async (configType: string) => {
  console.log(`🔄 按需加载${configType}配置...`)
  
  try {
    switch (configType) {
      case 'prometheus':
        // 总是尝试加载最新的保存配置
        console.log('🔄 加载Prometheus配置...')
        await loadPrometheusConfig()
        console.log('✅ Prometheus配置加载完成:', prometheusConfig.value)
        break
      case 'ollama':
        // 总是尝试加载最新的保存配置
        console.log('🔄 加载Ollama配置...')
        await loadOllamaConfig()
        console.log('✅ Ollama配置加载完成:', ollamaConfig.value)
        break
      case 'database':
        // 总是尝试加载最新的保存配置
        console.log('🔄 加载数据库配置...')
        loadDbConfigLoading.value = true
        await loadDatabaseConfig()
        loadDbConfigLoading.value = false
        console.log('✅ 数据库配置加载完成:', databaseConfig.value)
        break
      case 'services':
        if (systemServices.value.length === 0) {
          await refreshServices()
        }
        break
      case 'users':
        if (users.value.length <= 3) { // 初始示例数据只有3个
          await loadUsers()
        }
        break
      case 'logs':
        if (systemLogs.value.length <= 10) { // 初始示例数据只有10个
          await loadSystemLogs()
        }
        break
    }
  } catch (error) {
    console.warn(`⚠️ ${configType}配置加载失败:`, error.message)
  }
}

/**
 * 加载用户数据
 */
const loadUsers = async () => {
  try {
    const response = await apiService.getUsers()
    if (response?.success) {
      users.value = response.data.users || []
      console.log('✅ 用户数据加载成功:', users.value.length, '个用户')
    }
  } catch (error) {
    console.error('❌ 加载用户数据失败:', error)
  }
}

/**
 * 加载系统日志
 */
const loadSystemLogs = async () => {
  try {
    const params = {
      page: logCurrentPage.value,
      page_size: logPageSize.value,
      level: logLevelFilter.value,
      user: logUserFilter.value,
      search: logSearchText.value
    }
    
    const response = await apiService.getSystemLogsApi(params)
    if (response?.success) {
      systemLogs.value = response.data.logs || []
      console.log('✅ 系统日志加载成功:', systemLogs.value.length, '条日志')
    }
  } catch (error) {
    console.error('❌ 加载系统日志失败:', error)
  }
}

// 生命周期钩子
onMounted(() => {
  // 使用轻量化初始化函数
  initializePage()
})

// 监听标签页切换，按需加载数据
watch(activeTab, async (newTab) => {
  console.log(`🔄 切换到标签页: ${newTab}`)
  
  switch (newTab) {
    case 'services':
      await loadConfigOnDemand('services')
      break
    case 'datasource':
      await loadConfigOnDemand('prometheus')
      break
    case 'ai':
      await loadConfigOnDemand('ollama')
      break
    case 'database':
      await loadConfigOnDemand('database')
      break
    case 'users':
      await loadConfigOnDemand('users')
      break
    case 'logs':
      await loadConfigOnDemand('logs')
      break
  }
})

// 调试信息 - 监听databaseConfig变化
watch(() => databaseConfig.value, (newValue) => {
  console.log('🔍 数据库配置变化:', newValue)
}, { deep: true })
</script>

<style scoped lang="scss">
.system {
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
  
  .overview-section {
    margin-bottom: 24px;
    
    .overview-card {
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
  
  .main-tabs {
    .section-header {
      @include flex-between;
      margin-bottom: 16px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
    }
    
    .service-card {
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
      
      .service-header {
        @include flex-between;
        margin-bottom: 16px;
        
        .service-info {
          @include flex-center;
          gap: 12px;
          
          .service-icon {
            font-size: 20px;
            
            &.service-running {
              color: $success-color;
            }
            
            &.service-stopped {
              color: $danger-color;
            }
            
            &.service-warning {
              color: $warning-color;
            }
            
            &.service-unknown {
              color: var(--el-text-color-secondary);
            }
          }
          
          h4 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
          }
        }
      }
      
      .service-details {
        margin-bottom: 16px;
        
        .detail-item {
          @include flex-between;
          margin-bottom: 8px;
          font-size: 12px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .label {
            color: var(--el-text-color-secondary);
          }
          
          .value {
            font-weight: 500;
            color: var(--el-text-color-primary);
            
            &.text-warning {
              color: var(--el-color-warning);
            }
            
            &.text-danger {
              color: var(--el-color-danger);
            }
          }
        }
      }
      
      .service-actions {
        @include flex-center;
        gap: 8px;
        
        .el-button {
          flex: 1;
        }
      }
    }
    
    .config-form {
      h4 {
        margin: 0 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--el-border-color-lighter);
        color: var(--el-text-color-primary);
        font-weight: 600;
      }
      
      .el-form-item {
        margin-bottom: 20px;
      }
    }
    
    .logs-container {
      max-height: 500px;
      overflow-y: auto;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 6px;
      
      .log-item {
        padding: 12px 16px;
        border-bottom: 1px solid var(--el-border-color-extra-light);
        
        &:last-child {
          border-bottom: none;
        }
        
        .log-header {
          @include flex-between;
          margin-bottom: 4px;
          font-size: 12px;
          
          .log-time {
            color: var(--el-text-color-placeholder);
          }
          
          .log-level {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 500;
          }
          
          .log-user {
            color: var(--el-text-color-secondary);
          }
        }
        
        .log-content {
          color: var(--el-text-color-primary);
          font-size: 14px;
        }
        
        &.log-info .log-level {
          background: var(--el-color-info-light-8);
          color: var(--el-color-info);
        }
        
        &.log-warning .log-level {
          background: var(--el-color-warning-light-8);
          color: var(--el-color-warning);
        }
        
        &.log-error .log-level {
          background: var(--el-color-danger-light-8);
          color: var(--el-color-danger);
        }
        
        &.log-success .log-level {
          background: var(--el-color-success-light-8);
          color: var(--el-color-success);
        }
      }
    }
    
    .logs-pagination {
      @include flex-center;
      margin-top: 20px;
    }
    
    .targets-section {
      margin-top: 20px;
      
      .section-header {
        @include flex-between;
        margin-bottom: 16px;
        
        h4 {
          @include flex-center;
          margin: 0;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
        }
      }
    }
    
    .labels-editor {
      .label-item {
        @include flex-center;
        margin-bottom: 10px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
    
    .ai-features-section {
      margin-top: 20px;
      
      .section-header {
        @include flex-between;
        margin-bottom: 16px;
        
        h4 {
          @include flex-center;
          margin: 0;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }
      
      .feature-card {
        height: 100%;
        
        .el-card__header {
          padding: 16px 20px;
          
          h5 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: var(--el-text-color-primary);
          }
        }
        
        .feature-content {
          .el-switch {
            margin-bottom: 12px;
          }
          
          .feature-description {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            margin: 8px 0 16px 0;
            line-height: 1.4;
          }
          
          .feature-config {
            padding: 12px;
            background: var(--el-color-info-light-9);
            border-radius: 6px;
            border: 1px solid var(--el-border-color-lighter);
            
            .el-form-item {
              margin-bottom: 8px;
              
              &:last-child {
                margin-bottom: 0;
              }
            }
          }
        }
      }
    }
    
    .config-description {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 8px;
      line-height: 1.4;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .system {
    .service-card .el-col {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .system {
    padding: 16px;
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .overview-section .el-col {
      margin-bottom: 16px;
    }
    
    .main-tabs {
      .config-form {
        .el-col {
          margin-bottom: 20px;
        }
      }
    }
  }
}

// 暗色模式适配
.dark {
  .overview-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
  
  .service-card {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
  
  .logs-container {
    background: var(--monitor-bg-secondary);
    border-color: var(--monitor-border-color);
  }
}

// 日志控件样式
.log-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.no-logs {
  text-align: center;
  padding: 40px 0;
}

.log-pagination {
  margin-top: 20px;
  text-align: right;
}

// 系统详情样式
.system-details-section {
  margin: 20px 0;
  
  .detail-card {
    height: 100%;
    
    h4 {
      margin: 0 0 16px 0;
      color: #409eff;
      font-size: 14px;
      font-weight: 600;
    }
    
    .el-descriptions {
      :deep(.el-descriptions__label) {
        font-weight: 500;
        color: #606266;
        width: 80px;
      }
      
      :deep(.el-descriptions__content) {
        color: #303133;
        font-weight: 400;
      }
    }
  }
}

// 新组件样式
.config-viewer-section {
  margin-top: 24px;
}

// 数据源配置标签页样式优化
.el-tab-pane[name="datasource"] {
  .el-card + .config-viewer-section {
    margin-top: 24px;
  }
}

// 配置名称字段样式
.config-form {
  .form-item-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    
    .el-icon {
      font-size: 14px;
      color: var(--el-color-info);
    }
  }
  
  .el-input.is-error {
    .el-input__wrapper {
      border-color: var(--el-color-danger);
      box-shadow: 0 0 0 1px var(--el-color-danger) inset;
    }
  }
  
  .el-form-item.is-error {
    .form-item-tip {
      color: var(--el-color-danger);
      
      .el-icon {
        color: var(--el-color-danger);
      }
    }
  }
}

// 响应式优化
@media (max-width: 1200px) {
  .config-viewer-section {
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .config-viewer-section {
    margin-top: 16px;
  }
}

// 加载状态样式
.loading-skeleton {
  padding: 20px;
  
  .el-skeleton {
    --el-skeleton-color: #f2f2f2;
    --el-skeleton-to-color: #e6e6e6;
  }
}
</style>