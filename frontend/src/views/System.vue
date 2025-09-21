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
                      :class="getServiceStatusClass(service.status)"
                    >
                      <CircleCheck v-if="service.status === 'running'" />
                      <CircleClose v-else-if="service.status === 'stopped'" />
                      <Warning v-else />
                    </el-icon>
                    <h4>{{ service.name }}</h4>
                  </div>
                  <el-tag :type="getServiceStatusType(service.status)" size="small">
                    {{ getServiceStatusText(service.status) }}
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
                </div>
                
                <div class="service-actions">
                  <el-button 
                    v-if="service.status === 'stopped'"
                    size="small" 
                    type="success" 
                    @click="startService(service)"
                  >
                    启动
                  </el-button>
                  <el-button 
                    v-else
                    size="small" 
                    type="warning" 
                    @click="stopService(service)"
                  >
                    停止
                  </el-button>
                  <el-button size="small" @click="restartService(service)">
                    重启
                  </el-button>
                  <el-button size="small" type="info" @click="viewServiceLogs(service)">
                    日志
                  </el-button>
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
          
          <el-form :model="ollamaConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>基础配置</h4>
                <el-form-item label="启用AI分析">
                  <el-switch v-model="ollamaConfig.enabled" />
                </el-form-item>
                <el-form-item label="配置名称" :error="ollamaConfigNameValidation.valid ? '' : ollamaConfigNameValidation.message">
                  <el-input 
                    v-model="ollamaConfig.name" 
                    placeholder="例如：production-ollama"
                    :disabled="!ollamaConfig.enabled"
                    maxlength="50"
                    show-word-limit
                    :class="{ 'is-error': !ollamaConfigNameValidation.valid }"
                  />
                  <div class="form-item-tip">
                    <el-icon><InfoFilled /></el-icon>
                    只能包含字母、数字、下划线和短横线，不能以数字或符号开头或结尾
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
                  @click="testDatabaseConnection" 
                  :loading="testDbLoading"
                >
                  测试连接
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="saveDatabaseConfig" 
                  :loading="saveDbLoading"
                >
                  保存配置
                </el-button>
              </div>
            </div>
          </template>
          
          <el-form :model="databaseConfig" label-width="150px" class="config-form">
            <el-row :gutter="40">
              <el-col :span="12">
                <h4>连接配置</h4>
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
      </el-tab-pane>
      
      <el-tab-pane label="系统配置" name="config">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>系统参数配置</h3>
              <el-button size="small" type="primary" @click="savePrometheusConfig" :loading="saveLoading">
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
                <el-form-item label="数据保留天数">
                  <el-input-number 
                    v-model="systemConfig.dataRetentionDays" 
                    :min="1" 
                    :max="365"
                    style="width: 100%"
                  />
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
                </el-form-item>
                <el-form-item label="默认告警阈值">
                  <el-input-number 
                    v-model="systemConfig.defaultThreshold" 
                    :min="50" 
                    :max="95"
                    style="width: 100%"
                  />
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
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>用户列表</h3>
              <el-button size="small" type="primary" @click="showCreateUser = true">
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
      </el-tab-pane>
      
      <!-- 系统日志 -->
      <el-tab-pane label="系统日志" name="logs">
        <el-card>
          <template #header>
            <div class="section-header">
              <h3>系统操作日志</h3>
              <el-button size="small" @click="refreshLogs">
                刷新日志
              </el-button>
            </div>
          </template>
          
          <div class="logs-container">
            <div 
              v-for="log in systemLogs" 
              :key="log.id"
              class="log-item"
              :class="getLogLevelClass(log.level)"
            >
              <div class="log-header">
                <span class="log-time">{{ log.timestamp }}</span>
                <span class="log-level">{{ log.level }}</span>
                <span class="log-user">{{ log.user }}</span>
              </div>
              <div class="log-content">{{ log.message }}</div>
            </div>
          </div>
          
          <div class="logs-pagination">
            <el-pagination
              v-model:current-page="logsCurrentPage"
              :page-size="20"
              :total="totalLogs"
              layout="prev, pager, next"
              @current-change="handleLogsPageChange"
            />
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

    <!-- 添加用户弹窗 -->
    <el-dialog
      v-model="showCreateUser"
      title="添加用户"
      width="500px"
    >
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="观察员" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateUser = false">取消</el-button>
          <el-button type="primary" @click="createUser">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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
  InfoFilled
} from '@element-plus/icons-vue'
import { useLoadingOptimizer } from '@/utils/loadingOptimizer'
import { requestManager } from '@/utils/requestManager'
import { performanceMonitor } from '@/utils/performanceMonitor'
import { useConfigManager } from '@/composables/useConfigManager'
import { useDatabaseManager } from '@/composables/useDatabaseManager'
import type { PrometheusTarget } from '@/composables/useConfigManager'
import PrometheusConfigViewerOptimized from '@/components/common/PrometheusConfigViewerOptimized.vue'
import OllamaConfigViewerOptimized from '@/components/common/OllamaConfigViewerOptimized.vue'

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
  testOllamaConnection
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
const modelsLoading = ref(false)
const backupLoading = ref(false)
const showCreateUser = ref(false)
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

// Ollama可用模型
const availableModels = ref<Array<{ name: string; label: string; size?: string }>>([])
const modelsLoadTime = ref<number>(0)

// 配置查看器引用
const configViewerRef = ref(null)
const ollamaConfigViewerRef = ref(null)

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

// 数据库状态信息
const testDatabaseConnection = async () => {
  testDbLoading.value = true
  dbConnectionStatus.value = null
  
  try {
    const success = await testDbConnection()
    dbConnectionStatus.value = {
      success,
      message: success ? '连接成功' : '连接失败'
    }
    
    if (success) {
      ElMessage.success('数据库连接测试成功！')
    } else {
      ElMessage.error('数据库连接失败，请检查配置')
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

// 保存数据库配置
const saveDatabaseConfig = async () => {
  saveDbLoading.value = true
  try {
    // 这里调用API保存数据库配置
    console.log('保存数据库配置:', databaseConfig.value)
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('数据库配置已保存')
  } catch (error) {
    console.error('保存数据库配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    saveDbLoading.value = false
  }
}

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
  memoryUsage: 74.2
})

// 系统服务
const systemServices = ref([
  {
    name: 'API网关',
    status: 'running',
    port: 8000,
    cpuUsage: 15.2,
    memoryUsage: 256,
    uptime: '5天 12小时'
  },
  {
    name: 'AI检测服务',
    status: 'running',
    port: 8001,
    cpuUsage: 32.8,
    memoryUsage: 512,
    uptime: '3天 8小时'
  },
  {
    name: '规则引擎',
    status: 'running',
    port: 8002,
    cpuUsage: 8.5,
    memoryUsage: 128,
    uptime: '7天 2小时'
  },
  {
    name: '通知服务',
    status: 'warning',
    port: 8003,
    cpuUsage: 12.1,
    memoryUsage: 64,
    uptime: '1天 15小时'
  },
  {
    name: '数据库服务',
    status: 'running',
    port: 5432,
    cpuUsage: 22.3,
    memoryUsage: 1024,
    uptime: '15天 6小时'
  },
  {
    name: 'Redis服务',
    status: 'stopped',
    port: 6379,
    cpuUsage: 0,
    memoryUsage: 0,
    uptime: '-'
  }
])

// 系统配置
const systemConfig = ref({
  systemName: '智能监控预警系统',
  dataRetentionDays: 90,
  autoBackup: true,
  backupInterval: 24,
  collectInterval: 60,
  defaultThreshold: 85,
  enableAnomalyDetection: true,
  detectionSensitivity: 7
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

// 用户表单
const userForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'viewer'
})

// 系统日志
const systemLogs = ref([
  {
    id: 1,
    timestamp: '2025-09-06 22:45:32',
    level: 'INFO',
    user: 'admin',
    message: '用户登录系统'
  },
  {
    id: 2,
    timestamp: '2025-09-06 22:30:15',
    level: 'WARNING',
    user: 'system',
    message: '通知服务响应缓慢'
  },
  {
    id: 3,
    timestamp: '2025-09-06 22:15:45',
    level: 'ERROR',
    user: 'system',
    message: 'Redis服务连接失败'
  },
  {
    id: 4,
    timestamp: '2025-09-06 21:58:22',
    level: 'INFO',
    user: 'operator',
    message: '创建新的监控规则'
  },
  {
    id: 5,
    timestamp: '2025-09-06 21:30:10',
    level: 'SUCCESS',
    user: 'system',
    message: '系统备份完成'
  }
])

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
 * 刷新系统信息
 */
const refreshSystemInfo = async () => {
  refreshLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 更新系统数据
    systemInfo.value.cpuUsage = Math.random() * 30 + 50
    systemInfo.value.memoryUsage = Math.random() * 20 + 60
    systemInfo.value.onlineUsers = Math.floor(Math.random() * 10) + 8
    
    ElMessage.success('系统信息已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshLoading.value = false
  }
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
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('服务状态已刷新')
  } finally {
    servicesLoading.value = false
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
  ElMessage.info(`编辑用户: ${user.username}`)
}

/**
 * 切换用户状态
 */
const toggleUserStatus = (user: any) => {
  user.status = user.status === 'active' ? 'inactive' : 'active'
  const statusText = user.status === 'active' ? '启用' : '禁用'
  ElMessage.success(`用户${user.username}已${statusText}`)
}

/**
 * 重置密码
 */
const resetPassword = async (user: any) => {
  try {
    await ElMessageBox.confirm(`确定要重置用户${user.username}的密码吗？`, '确认操作')
    ElMessage.success('密码重置成功，新密码已发送至用户邮箱')
  } catch {
    // 用户取消
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
    
    const index = users.value.findIndex(u => u.id === user.id)
    if (index > -1) {
      users.value.splice(index, 1)
      ElMessage.success('用户删除成功')
    }
  } catch {
    // 用户取消
  }
}

/**
 * 创建用户
 */
const createUser = () => {
  const newUser = {
    id: Date.now(),
    ...userForm.value,
    status: 'active',
    lastLogin: '-',
    createdAt: new Date().toLocaleString()
  }
  
  users.value.push(newUser)
  showCreateUser.value = false
  
  // 重置表单
  userForm.value = {
    username: '',
    email: '',
    password: '',
    role: 'viewer'
  }
  
  ElMessage.success('用户创建成功')
}

/**
 * 刷新日志
 */
const refreshLogs = () => {
  ElMessage.success('日志已刷新')
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

const getServiceStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    running: 'service-running',
    stopped: 'service-stopped',
    warning: 'service-warning'
  }
  return classMap[status] || ''
}

const getServiceStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    running: 'success',
    stopped: 'danger',
    warning: 'warning'
  }
  return typeMap[status] || 'info'
}

const getServiceStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    running: '运行中',
    stopped: '已停止',
    warning: '异常'
  }
  return textMap[status] || '未知'
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

// 优化的页面初始化函数
const initializePage = async () => {
  document.title = '系统管理 - 智能监控预警系统'
  
  // 创建页面加载策略
  const pageStrategy = loadingOptimizer.createPageLoadStrategy('system-page')
  
  // 关键数据：立即加载
  pageStrategy.critical([
    {
      id: 'prometheus-config',
      name: '加载Prometheus配置',
      execute: () => performanceMonitor.measureAsync('load-prometheus-config', () => loadPrometheusConfig())
    }
  ])
  
  // 次要数据：延迟加载
  pageStrategy.deferred([
    {
      id: 'system-health',
      name: '检查系统健康状态',
      execute: () => performanceMonitor.measureAsync('check-system-health', async () => {
        try {
          const health = requestManager.getServiceHealth()
          console.log('系统健康状态:', health)
          return health
        } catch (error) {
          console.warn('健康检查失败:', error)
          return null
        }
      })
    }
  ])
  
  // 可选数据：后台加载
  pageStrategy.optional([
    {
      id: 'performance-stats',
      name: '收集性能统计',
      execute: () => performanceMonitor.measureAsync('collect-perf-stats', async () => {
        const stats = performanceMonitor.getStats()
        console.log('性能统计:', stats)
        return stats
      })
    }
  ])
  
  // 执行加载策略
  try {
    const results = await pageStrategy.execute()
    console.log('页面加载完成:', results)
    
    // 如果有失败的任务，显示警告
    if (results.failed.length > 0) {
      ElMessage.warning(`部分数据加载失败: ${results.failed.join(', ')}`)
    }
  } catch (error) {
    console.error('页面初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新重试')
  }
}

// 生命周期钩子
onMounted(() => {
  // 使用优化的初始化函数
  initializePage()
})
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
</style>