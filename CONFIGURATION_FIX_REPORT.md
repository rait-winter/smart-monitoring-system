# 配置保存数据库问题修复报告

## 🎯 问题概述

系统管理页面中的Prometheus配置保存功能存在以下问题：
- 配置保存后没有写入数据库
- 前端页面刷新后配置丢失
- API请求返回404/500错误
- 前后端通信异常

## 🔍 问题分析

### 1. 后端问题
- **数据库会话获取失败**：`config_db_service.py`导入了不存在的`get_db_session`函数
- **SQLAlchemy关系冲突**：`User.alerts`关系有多个外键路径冲突
- **字段名冲突**：`Notification.metadata`与SQLAlchemy保留字冲突
- **API响应结构不完整**：`APIResponse`模型缺少`data`字段
- **JSON序列化错误**：datetime对象无法被JSON序列化

### 2. 前端问题
- **API路径错误**：使用了错误的baseURL导致请求路径不正确
- **环境变量覆盖**：`VITE_API_BASE_URL`覆盖了正确的API配置
- **数据解析错误**：没有正确提取API响应中的配置数据
- **页面更新逻辑缺失**：保存成功后没有重新加载配置

## 🔧 修复方案

### 后端修复

#### 1. 修复数据库会话问题
**文件**: `backend/app/core/database.py`

```python
def get_db_session():
    """获取数据库会话的便利函数"""
    return AsyncSessionLocal()
```

#### 2. 修复SQLAlchemy关系冲突
**文件**: `backend/app/models/database.py`

```python
# 修复User模型中的关系定义
alerts: Mapped[List["Alert"]] = relationship("Alert", foreign_keys="Alert.user_id", back_populates="user")

# 重命名冲突字段
# 将 metadata 改为 extra_data
extra_data: Mapped[Dict] = mapped_column(JSON, default=dict)
```

#### 3. 完善API响应模型
**文件**: `backend/app/models/schemas.py`

```python
class APIResponse(BaseSchema):
    """标准API响应格式"""
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="操作成功", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")  # 新增
```

#### 4. 修复JSON序列化错误
**文件**: `backend/app/middleware/error_handler.py`

```python
return JSONResponse(
    status_code=status_code,
    content=api_response.model_dump(mode='json'),  # 修改为支持datetime序列化
    headers={"Content-Type": "application/json; charset=utf-8"}
)
```

### 前端修复

#### 1. 修复API配置
**文件**: `frontend/src/services/api.ts`

```typescript
// 强制使用相对路径，通过Vite代理转发
const API_BASE_URL = '/api/v1'

// Prometheus 配置相关
async getPrometheusConfig() {
  console.log('🔥 [FIXED] 发送Prometheus配置请求: /prometheus/config')
  console.log('🔥 [FIXED] 完整baseURL:', API_BASE_URL)
  return this.get('/prometheus/config?_t=' + Date.now())
}
```

#### 2. 修复配置管理逻辑
**文件**: `frontend/src/composables/useConfigManager.ts`

```typescript
// 加载配置
const loadPrometheusConfig = async () => {
  try {
    const response = await apiService.getPrometheusConfig()
    console.log('API响应:', response)
    
    // 检查响应格式并提取配置数据
    if (response && response.data && response.data.config) {
      prometheusConfig.value = { ...prometheusConfig.value, ...response.data.config }
      console.log('配置加载成功:', prometheusConfig.value)
    } else if (response && response.config) {
      // 兼容直接返回config的情况
      prometheusConfig.value = { ...prometheusConfig.value, ...response.config }
      console.log('配置加载成功(兼容格式):', prometheusConfig.value)
    }
  } catch (error) {
    console.error('加载Prometheus配置失败:', error)
  }
}
```

#### 3. 修复系统管理页面
**文件**: `frontend/src/views/System.vue`

```typescript
// 添加loadPrometheusConfig到导入
const {
  prometheusConfig,
  ollamaConfig,
  databaseConfig,
  isPrometheusConfigured,
  isOllamaConfigured,
  isDatabaseConfigured,
  loadPrometheusConfig,  // 新增
  savePrometheusConfig,
  testPrometheusConnection: testConnection,
  addPrometheusTarget,
  removePrometheusTarget
} = useConfigManager()

// 修复保存后重新加载逻辑
const savePrometheusConfigLocal = async () => {
  savePrometheusLoading.value = true
  try {
    const success = await savePrometheusConfig()
    if (success) {
      ElMessage.success('Prometheus配置已保存')
      // 保存成功后重新加载配置，更新页面显示
      await loadPrometheusConfig()
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
```

#### 4. 优化Vite代理配置
**文件**: `frontend/vite.config.ts`

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
    timeout: 30000,
    rewrite: (path) => {
      console.log('代理请求:', path)
      return path
    }
  },
}
```

## 📁 修改的文件清单

### 后端文件 (4个)
```
backend/
├── app/core/database.py                 # 添加get_db_session函数
├── app/models/database.py              # 修复SQLAlchemy关系和字段名
├── app/models/schemas.py               # 添加APIResponse.data字段
└── app/middleware/error_handler.py     # 修复JSON序列化
```

### 前端文件 (4个)
```
frontend/
├── src/services/api.ts                 # 修复API baseURL和路径
├── src/views/System.vue               # 添加配置重新加载逻辑
├── src/composables/useConfigManager.ts # 修复数据解析逻辑
└── vite.config.ts                     # 优化代理配置
```

## 🧪 测试验证

### 1. API测试
```powershell
# 测试后端API是否正常
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prometheus/config" -Method Get
```

**预期响应**:
```json
{
  "success": true,
  "message": "获取Prometheus配置成功",
  "timestamp": "2025-09-17T13:27:34.839552",
  "data": {
    "config": {
      "enabled": true,
      "url": "http://192.168.233.137:30090/",
      "timeout": 30000,
      // ... 其他配置项
    }
  }
}
```

### 2. 前端测试
- ✅ 页面加载时正确显示配置
- ✅ 配置保存成功后立即更新页面显示
- ✅ 不再出现404/500错误
- ✅ 浏览器控制台显示正确的API请求路径

### 3. 数据库验证
```sql
-- 检查配置是否保存到数据库
SELECT * FROM prometheus_configs WHERE is_default = true;
```

## 🚀 部署说明

### 1. 后端部署
```bash
cd backend
# 重启后端服务
python main.py
```

### 2. 前端部署
```bash
cd frontend
# 清理缓存并重启
rm -rf node_modules/.vite
npm run dev
```

### 3. 浏览器缓存清理
- 按 `Ctrl + Shift + Delete` 清理浏览器缓存
- 或使用无痕模式测试

## 📊 修复效果

### 修复前
- ❌ 配置保存失败，返回500错误
- ❌ 页面刷新后配置丢失
- ❌ 前后端通信异常
- ❌ 数据库中没有配置记录

### 修复后
- ✅ 配置成功保存到数据库
- ✅ 页面显示正确的配置值
- ✅ 前后端通信正常
- ✅ 保存成功后立即更新页面显示

## 🔄 后续维护

### 1. 监控要点
- 定期检查API响应时间和成功率
- 监控数据库配置表的数据完整性
- 关注前端错误日志中的API请求异常

### 2. 扩展建议
- 考虑添加配置版本管理功能
- 实现配置备份和恢复机制
- 添加配置变更审计日志

## 📝 提交信息

```
feat: 修复配置保存数据库问题

- 后端: 添加get_db_session函数，修复SQLAlchemy关系冲突
- 后端: 完善API响应模型，修复JSON序列化错误
- 前端: 修复API路径配置，优化Vite代理设置
- 前端: 修复配置数据解析和页面更新逻辑
- 测试: 验证配置保存和加载功能正常工作

Closes: 配置保存没有写入数据库问题
```

---

**修复完成时间**: 2025-09-17  
**修复工程师**: AI Assistant  
**测试状态**: ✅ 通过  
**部署状态**: 🚀 准备就绪
