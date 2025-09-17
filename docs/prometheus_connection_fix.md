# Prometheus连接问题修复文档

本文档详细说明了如何修复智能监控预警系统中的Prometheus连接问题和CORS跨域访问问题。

## 问题描述

在系统运行过程中，遇到了以下两个主要问题：

1. **CORS跨域访问被阻止**：
   ```
   Access to XMLHttpRequest at 'http://localhost:8000/prometheus/test' from origin 'http://192.168.10.35:3000' has been blocked by CORS policy
   ```

2. **Prometheus连接测试失败**：
   ```
   API响应错误: AxiosError
   Message: Network Error
   ```

## 问题分析

### 1. CORS跨域问题
前端运行在 `http://192.168.10.35:3000`，而后端的CORS配置只允许 `http://localhost:3000` 和 `http://127.0.0.1:3000`。

### 2. Prometheus API端点缺失
前端尝试访问 `/prometheus/test` 端点，但后端没有实现相应的API端点。

### 3. 环境配置不匹配
前端环境配置中的API地址与实际运行地址不匹配。

## 解决方案

### 1. 修复CORS配置

修改后端 [.env](file:///d%3A/autocode/20250902/backend/.env) 文件，添加前端地址到允许的CORS源：

```bash
# 跨域配置 (前端开发服务器地址)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.10.35:3000"]
```

### 2. 实现Prometheus配置管理API

创建新的API端点文件 [prometheus.py](file:///d%3A/autocode/20250902/backend/app/api/v1/endpoints/prometheus.py)：

- `GET /prometheus/config` - 获取Prometheus配置
- `POST /prometheus/config` - 更新Prometheus配置
- `POST /prometheus/test` - 测试Prometheus连接

### 3. 注册新的API路由

更新 [api.py](file:///d%3A/autocode/20250902/backend/app/api/v1/api.py) 文件，注册Prometheus路由：

```python
api_router.include_router(
    prometheus.router,
    prefix="/prometheus",
    tags=["Prometheus配置"]
)
```

### 4. 更新前端环境配置

修改前端 [.env.development](file:///d%3A/autocode/20250902/frontend/.env.development) 文件，确保API地址正确：

```bash
# API配置
VITE_API_BASE_URL=http://192.168.10.35:8000
```

## 验证修复

### 1. 启动后端服务

```bash
cd backend
conda activate smart-monitoring
python main.py
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

### 3. 运行测试脚本

```bash
python test_prometheus_fix.py
```

### 4. 在前端界面测试

1. 打开浏览器访问 `http://192.168.10.35:3000`
2. 进入系统配置页面
3. 配置Prometheus地址（如：http://localhost:9090）
4. 点击"测试连接"按钮

## 预期结果

1. **CORS错误消失** - 前端可以正常访问后端API
2. **Prometheus连接测试成功** - 能够正确测试Prometheus连接状态
3. **API文档完整** - 在 `http://192.168.10.35:8000/docs` 中可以看到新的Prometheus API端点

## 注意事项

1. 确保后端服务和前端服务都在运行
2. 确保Prometheus服务在指定地址可访问
3. 如果前端运行在不同IP地址，需要相应更新CORS配置
4. 生产环境中应使用更严格的CORS策略

## 相关文件

- 后端配置文件：[backend/.env](file:///d%3A/autocode/20250902/backend/.env)
- 前端配置文件：[frontend/.env.development](file:///d%3A/autocode/20250902/frontend/.env.development)
- Prometheus API实现：[backend/app/api/v1/endpoints/prometheus.py](file:///d%3A/autocode/20250902/backend/app/api/v1/endpoints/prometheus.py)
- API路由注册：[backend/app/api/v1/api.py](file:///d%3A/autocode/20250902/backend/app/api/v1/api.py)
- 测试脚本：[test_prometheus_fix.py](file:///d%3A/autocode/20250902/test_prometheus_fix.py)