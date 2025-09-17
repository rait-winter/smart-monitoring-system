-- 智能监控预警系统 - PostgreSQL数据库初始化脚本
-- 数据库版本: 2.0.0
-- 创建时间: 2025-09-08

-- 连接到指定数据库 (请先创建数据库: CREATE DATABASE smart_monitoring;)
-- \c smart_monitoring;

-- ===== 用户管理表 =====
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'operator')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 巡检规则表 =====
-- 巡检规则表
CREATE TABLE IF NOT EXISTS inspection_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    target_metric VARCHAR(100) NOT NULL,
    condition_type VARCHAR(20) NOT NULL CHECK (condition_type IN ('threshold', 'anomaly', 'trend')),
    condition_value JSONB,
    severity VARCHAR(10) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    enabled BOOLEAN DEFAULT TRUE,
    notification_channels JSONB, -- 存储通知渠道配置
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 指标数据表 =====
-- 指标数据表
CREATE TABLE IF NOT EXISTS metrics_data (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    labels JSONB, -- 标签信息，如 {instance: "server1", job: "node"}
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 指标元数据表
CREATE TABLE IF NOT EXISTS metrics_metadata (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    type VARCHAR(20) CHECK (type IN ('gauge', 'counter', 'histogram', 'summary')),
    unit VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 异常检测表 =====
-- 异常检测结果表
CREATE TABLE IF NOT EXISTS anomaly_detections (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    expected_value DOUBLE PRECISION,
    deviation DOUBLE PRECISION,
    algorithm VARCHAR(50) NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    is_confirmed BOOLEAN DEFAULT FALSE,
    confirmed_by INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 通知记录表 =====
-- 通知记录表
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    channel VARCHAR(20) CHECK (channel IN ('email', 'slack', 'webhook', 'sms')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'cancelled')),
    sent_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    related_anomaly_id INTEGER REFERENCES anomaly_detections(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 系统配置表 =====
-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== 索引创建 =====
-- 为提高查询性能创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics_data(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_labels ON metrics_data USING GIN(labels);
CREATE INDEX IF NOT EXISTS idx_anomaly_timestamp ON anomaly_detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomaly_metric ON anomaly_detections(metric_name);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_rules_enabled ON inspection_rules(enabled);

-- ===== 初始数据插入 =====
-- 插入默认管理员用户 (密码需要在应用中加密)
INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES
('admin', 'admin@smart-monitoring.com', '', '系统管理员', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;

-- 插入默认系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('prometheus_config', '{"url": "http://localhost:9090", "timeout": 30}', 'Prometheus配置'),
('notification_channels', '{"email": {"enabled": true}, "slack": {"enabled": false}}', '默认通知渠道配置'),
('ai_detection_config', '{"algorithms": ["isolation_forest", "zscore"], "default_sensitivity": 0.8}', 'AI异常检测配置')
ON CONFLICT (config_key) DO NOTHING;

-- 插入示例巡检规则
INSERT INTO inspection_rules (name, description, target_metric, condition_type, condition_value, severity, enabled) VALUES
('CPU使用率过高', '监控CPU使用率超过阈值', 'cpu_usage_percent', 'threshold', '{"operator": ">", "value": 80.0}', 'high', TRUE),
('内存使用率异常', '监控内存使用率超过阈值', 'memory_usage_percent', 'threshold', '{"operator": ">", "value": 85.0}', 'medium', TRUE),
('磁盘空间不足', '监控磁盘使用率超过阈值', 'disk_usage_percent', 'threshold', '{"operator": ">", "value": 90.0}', 'critical', TRUE)
ON CONFLICT DO NOTHING;

-- 插入示例指标元数据
INSERT INTO metrics_metadata (metric_name, description, type, unit) VALUES
('cpu_usage_percent', 'CPU使用率', 'gauge', 'percent'),
('memory_usage_percent', '内存使用率', 'gauge', 'percent'),
('disk_usage_percent', '磁盘使用率', 'gauge', 'percent'),
('network_io_bytes', '网络IO流量', 'counter', 'bytes'),
('request_count', '请求计数', 'counter', 'count')
ON CONFLICT (metric_name) DO NOTHING;

-- ===== 权限和约束 =====
-- 添加外键约束
ALTER TABLE user_sessions 
    ADD CONSTRAINT fk_user_sessions_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE inspection_rules 
    ADD CONSTRAINT fk_inspection_rules_created_by 
    FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE anomaly_detections 
    ADD CONSTRAINT fk_anomaly_detections_confirmed_by 
    FOREIGN KEY (confirmed_by) REFERENCES users(id);

ALTER TABLE notifications 
    ADD CONSTRAINT fk_notifications_related_anomaly_id 
    FOREIGN KEY (related_anomaly_id) REFERENCES anomaly_detections(id);

-- ===== 创建更新时间触发器函数 =====
-- 创建更新时间戳的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要自动更新时间戳的表创建触发器
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inspection_rules_updated_at 
    BEFORE UPDATE ON inspection_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_metrics_metadata_updated_at 
    BEFORE UPDATE ON metrics_metadata 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===== 数据库统计视图 =====
-- 创建异常统计视图
CREATE OR REPLACE VIEW anomaly_statistics AS
SELECT 
    severity,
    COUNT(*) as count,
    MAX(created_at) as last_occurred
FROM anomaly_detections
GROUP BY severity;

-- 创建指标最新值视图
CREATE OR REPLACE VIEW latest_metrics AS
SELECT 
    metric_name,
    labels,
    MAX(timestamp) as latest_timestamp,
    MAX(value) as latest_value
FROM metrics_data
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY metric_name, labels;

-- ===== 完成信息 =====
-- \dt  -- 查看所有表
-- \dv  -- 查看所有视图
-- SELECT * FROM users;  -- 查看用户表数据
-- SELECT * FROM inspection_rules;  -- 查看巡检规则数据

-- 初始化脚本执行完成信息
SELECT '数据库初始化完成' as message;