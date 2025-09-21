@echo off
title 智能监控系统后端服务
echo 🚀 启动智能监控系统后端服务
echo 🔗 数据库: PostgreSQL 192.168.233.133:30199
echo ========================================
set "DATABASE_URL=postgresql+asyncpg://postgres:zalando@192.168.233.133:30199/smart_monitoring"
call conda activate smart-monitoring
cd backend
python main.py
pause
