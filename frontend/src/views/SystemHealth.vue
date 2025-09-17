<template>
  <div class="system-health">
    <el-card class="health-card">
      <template #header>
        <div class="card-header">
          <span>系统健康状态</span>
          <el-button type="primary" @click="fetchHealthData" :loading="loading">
            刷新
          </el-button>
        </div>
      </template>
      
      <div v-if="healthData" class="health-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-descriptions title="基本信息" :column="1" border>
              <el-descriptions-item label="服务名称">{{ healthData.service }}</el-descriptions-item>
              <el-descriptions-item label="版本">{{ healthData.version }}</el-descriptions-item>
              <el-descriptions-item label="环境">{{ healthData.environment }}</el-descriptions-item>
              <el-descriptions-item label="运行时间">{{ formatUptime(healthData.uptime) }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          
          <el-col :span="12">
            <el-descriptions title="组件状态" :column="1" border>
              <el-descriptions-item 
                v-for="(status, component) in healthData.components" 
                :key="component"
                :label="component"
              >
                <el-tag :type="status === 'healthy' ? 'success' : 'danger'">
                  {{ status === 'healthy' ? '健康' : '异常' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiService from '@/services/api'

interface HealthData {
  service: string
  version: string
  environment: string
  uptime: number
  components: Record<string, string>
}

const healthData = ref<HealthData | null>(null)
const loading = ref(false)

// 格式化运行时间
const formatUptime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  return `${hours}小时${minutes}分钟${secs}秒`
}

// 获取健康数据
const fetchHealthData = async () => {
  try {
    loading.value = true
    const response = await apiService.getSystemHealth()
    healthData.value = response.data
  } catch (error) {
    ElMessage.error('获取健康数据失败: ' + (error as Error).message)
    console.error('获取健康数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchHealthData()
})
</script>

<style scoped lang="scss">
.system-health {
  padding: 20px;
  
  .health-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .health-content {
      margin-top: 20px;
    }
    
    .empty-state {
      text-align: center;
      padding: 40px 0;
    }
  }
}
</style>