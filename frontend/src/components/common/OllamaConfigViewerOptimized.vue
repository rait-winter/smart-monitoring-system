<template>
  <el-card>
    <template #header>
      <div class="section-header">
        <h3>
          <el-icon><Platform /></el-icon>
          当前Ollama配置
        </h3>
        <div class="header-actions">
          <el-button 
            size="small" 
            @click="refreshConfig"
            :loading="refreshLoading"
            :icon="Refresh"
          >
            刷新
          </el-button>
        </div>
      </div>
    </template>

    <!-- 当前配置显示 -->
    <div v-if="currentConfig" class="current-config">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="配置名称">
          <el-tag type="primary">{{ currentConfig.name || '默认配置' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentConfig.enabled ? 'success' : 'danger'">
            {{ currentConfig.enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="API地址">
          <span>{{ currentConfig.apiUrl || 'http://localhost:11434' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="AI模型">
          <el-tag>{{ currentConfig.model || 'llama3.2' }}</el-tag>
          <el-button 
            v-if="currentConfig.enabled" 
            size="small" 
            text 
            type="primary" 
            @click="checkAvailableModels"
            style="margin-left: 8px;"
          >
            查看可用模型
          </el-button>
        </el-descriptions-item>
        <el-descriptions-item label="超时时间">
          <span>{{ currentConfig.timeout || 60000 }}ms</span>
        </el-descriptions-item>
        <el-descriptions-item label="最大Token数">
          <span>{{ currentConfig.maxTokens || 2048 }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="创造性">
          <el-rate 
            :model-value="(currentConfig.temperature || 0.7) * 5" 
            disabled 
            show-score 
            text-color="#ff9900"
          />
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          <span>{{ formatTime(currentConfig.updatedAt) }}</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 快速测试 -->
      <div class="quick-test-section">
        <el-divider content-position="left">
          <el-icon><Lightning /></el-icon>
          快速测试
        </el-divider>
        
        <div class="test-controls">
          <el-button 
            type="success" 
            @click="testConnection"
            :loading="testLoading"
            :disabled="!currentConfig.enabled"
          >
            <el-icon><Link /></el-icon>
            连接测试
          </el-button>
          
          <el-button 
            type="primary" 
            @click="showModelTest"
            :loading="modelTestLoading"
            :disabled="!currentConfig.enabled"
          >
            <el-icon><ChatDotSquare /></el-icon>
            模型测试
          </el-button>
        </div>

        <!-- 测试结果 -->
        <div v-if="testResult" class="test-result">
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.message"
            :description="testResult.details"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 模型测试对话 -->
        <div v-if="showChat" class="model-chat">
          <el-divider content-position="left">AI模型对话测试</el-divider>
          
          <div class="chat-input">
            <el-input
              v-model="testPrompt"
              type="textarea"
              :rows="3"
              placeholder="输入测试提示词，例如：你好，请介绍一下你自己"
              maxlength="500"
              show-word-limit
            />
            <div class="chat-actions">
              <el-button 
                type="primary" 
                @click="sendTestMessage"
                :loading="chatLoading"
                :disabled="!testPrompt.trim()"
              >
                发送测试
              </el-button>
              <el-button @click="clearChat">清空对话</el-button>
            </div>
          </div>

          <!-- 对话记录 -->
          <div v-if="chatHistory.length > 0" class="chat-history">
            <div v-for="(msg, index) in chatHistory" :key="index" class="chat-message">
              <div :class="['message-bubble', msg.role]">
                <div class="message-header">
                  <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                  <el-icon v-else><Avatar /></el-icon>
                  <span class="role-name">{{ msg.role === 'user' ? '用户' : 'AI助手' }}</span>
                  <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                </div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无配置状态 -->
    <el-empty v-else description="暂无Ollama配置" />
  </el-card>

  <!-- 配置历史记录 -->
  <el-card style="margin-top: 20px;">
    <template #header>
      <div class="section-header">
        <h3>
          <el-icon><Clock /></el-icon>
          配置历史
        </h3>
        <div class="header-actions">
          <el-button 
            size="small" 
            @click="loadConfigHistory"
            :loading="historyLoading"
            :icon="Refresh"
          >
            刷新历史
          </el-button>
          <el-button 
            size="small" 
            type="danger"
            @click="clearHistory"
            :disabled="!configHistory.length"
          >
            清空历史
          </el-button>
        </div>
      </div>
    </template>

    <!-- 配置历史列表 -->
    <div v-if="configHistory.length > 0">
      <el-table :data="configHistory" style="width: 100%">
        <el-table-column prop="name" label="名称" width="200">
          <template #default="{ row }">
            <el-tag v-if="row.isDefault" type="success">{{ row.name }}</el-tag>
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="apiUrl" label="API地址" />
        <el-table-column prop="model" label="模型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.model }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timeout" label="超时(ms)" width="100" />
        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary"
              @click="switchConfig(row.id)"
              :loading="switchLoading"
              :disabled="row.isDefault"
            >
              {{ row.isDefault ? '当前配置' : '切换' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-empty v-else description="暂无配置历史" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Lightning,
  Link,
  ChatDotSquare,
  User,
  Avatar,
  Clock,
  Platform
} from '@element-plus/icons-vue'
// 移除date-fns依赖，使用内置日期格式化
import apiService from '@/services/api'

// 响应式数据
const currentConfig = ref<any>(null)
const configHistory = ref<any[]>([])
const refreshLoading = ref(false)
const historyLoading = ref(false)
const testLoading = ref(false)
const modelTestLoading = ref(false)
const switchLoading = ref(false)
const chatLoading = ref(false)

// 测试相关
const testResult = ref<any>(null)
const showChat = ref(false)
const testPrompt = ref('')
const chatHistory = ref<any[]>([])

// 格式化时间
const formatTime = (time: string | Date) => {
  if (!time) return '未知'
  const date = typeof time === 'string' ? new Date(time) : time
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString('zh-CN')
}

// 加载当前配置
const loadCurrentConfig = async () => {
  try {
    refreshLoading.value = true
    const response = await apiService.getOllamaConfig()
    
    if (response && (response.data || response)) {
      currentConfig.value = response.data || response
    } else {
      currentConfig.value = null
    }
  } catch (error) {
    console.error('加载Ollama配置失败:', error)
    ElMessage.error('加载配置失败')
  } finally {
    refreshLoading.value = false
  }
}

// 加载配置历史
const loadConfigHistory = async () => {
  try {
    historyLoading.value = true
    const response = await apiService.getOllamaConfigHistory()
    
    if (response?.data?.configs) {
      configHistory.value = response.data.configs
    } else {
      configHistory.value = []
    }
  } catch (error) {
    console.error('加载配置历史失败:', error)
    configHistory.value = []
  } finally {
    historyLoading.value = false
  }
}

// 刷新配置
const refreshConfig = async () => {
  await Promise.all([
    loadCurrentConfig(),
    loadConfigHistory()
  ])
}

// 测试连接
const testConnection = async () => {
  if (!currentConfig.value) return
  
  try {
    testLoading.value = true
    testResult.value = null
    
    const response = await apiService.testOllamaConnection(currentConfig.value)
    
    testResult.value = {
      success: response?.success || false,
      message: response?.message || '连接测试完成',
      details: response?.details || ''
    }
    
    if (testResult.value.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败')
    }
  } catch (error) {
    console.error('连接测试失败:', error)
    testResult.value = {
      success: false,
      message: '连接测试失败',
      details: error instanceof Error ? error.message : '未知错误'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testLoading.value = false
  }
}

// 显示模型测试
const showModelTest = () => {
  showChat.value = true
}

// 发送测试消息
const sendTestMessage = async () => {
  if (!testPrompt.value.trim() || !currentConfig.value) return
  
  try {
    chatLoading.value = true
    
    // 添加用户消息
    const userMessage = {
      role: 'user',
      content: testPrompt.value,
      timestamp: new Date()
    }
    chatHistory.value.push(userMessage)
    
    // 调用API
    const response = await apiService.chatWithOllama({
      message: testPrompt.value,
      config: currentConfig.value
    })
    
    // 添加AI回复
    const aiMessage = {
      role: 'assistant',
      content: response?.data?.response || '模型暂无回复',
      timestamp: new Date()
    }
    chatHistory.value.push(aiMessage)
    
    // 清空输入
    testPrompt.value = ''
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
    
    // 添加错误消息
    chatHistory.value.push({
      role: 'assistant',
      content: '抱歉，模型响应失败，请检查配置和网络连接',
      timestamp: new Date()
    })
  } finally {
    chatLoading.value = false
  }
}

// 清空对话
const clearChat = () => {
  chatHistory.value = []
  testPrompt.value = ''
}

// 切换配置
const switchConfig = async (configId: number) => {
  try {
    switchLoading.value = true
    
    const response = await apiService.setCurrentOllamaConfig(configId)
    
    if (response?.success) {
      ElMessage.success('配置切换成功')
      await refreshConfig()
    } else {
      ElMessage.error(response?.message || '切换失败')
    }
  } catch (error) {
    console.error('切换配置失败:', error)
    ElMessage.error('切换配置失败')
  } finally {
    switchLoading.value = false
  }
}

// 检查可用模型
const checkAvailableModels = async () => {
  if (!currentConfig.value?.apiUrl) return
  
  try {
    const response = await apiService.getOllamaModels(currentConfig.value.apiUrl)
    
    if (response?.success && response?.data?.models) {
      const models = response.data.models
      const modelList = models.map((model: any) => 
        `${model.name} (${formatModelSize(model.size)})`
      ).join('\n')
      
      await ElMessageBox.alert(
        `发现 ${models.length} 个可用模型：\n\n${modelList}`,
        '可用模型列表',
        {
          confirmButtonText: '确定',
          type: 'info',
        }
      )
    } else {
      ElMessage.warning(response?.message || '未找到可用模型')
    }
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  }
}

// 格式化模型大小
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

// 清空历史
const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有配置历史记录吗？当前配置不会被删除。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await apiService.clearOllamaConfigHistory()
    ElMessage.success('历史记录已清空')
    await loadConfigHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空历史失败:', error)
      ElMessage.error('清空历史失败')
    }
  }
}

// 暴露方法给父组件
defineExpose({
  refreshConfig,
  loadCurrentConfig,
  loadConfigHistory
})

// 页面挂载时加载数据
onMounted(() => {
  refreshConfig()
})
</script>

<style scoped lang="scss">
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.current-config {
  .quick-test-section {
    margin-top: 20px;
    
    .test-controls {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
    }
    
    .test-result {
      margin-bottom: 16px;
    }
    
    .model-chat {
      .chat-input {
        margin-bottom: 16px;
        
        .chat-actions {
          display: flex;
          gap: 8px;
          margin-top: 8px;
        }
      }
      
      .chat-history {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid var(--el-border-color);
        border-radius: 6px;
        padding: 12px;
        
        .chat-message {
          margin-bottom: 16px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .message-bubble {
            &.user {
              .message-header {
                color: var(--el-color-primary);
              }
              .message-content {
                background: var(--el-color-primary-light-9);
                margin-left: 24px;
              }
            }
            
            &.assistant {
              .message-header {
                color: var(--el-color-success);
              }
              .message-content {
                background: var(--el-color-success-light-9);
                margin-left: 24px;
              }
            }
            
            .message-header {
              display: flex;
              align-items: center;
              gap: 6px;
              font-size: 13px;
              margin-bottom: 6px;
              
              .role-name {
                font-weight: 500;
              }
              
              .message-time {
                margin-left: auto;
                color: var(--el-text-color-secondary);
                font-size: 12px;
              }
            }
            
            .message-content {
              padding: 8px 12px;
              border-radius: 8px;
              line-height: 1.5;
              white-space: pre-wrap;
            }
          }
        }
      }
    }
  }
}
</style>
