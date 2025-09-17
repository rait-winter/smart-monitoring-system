@echo off
echo 智能监控预警系统 - 服务启动脚本
echo ========================================

REM 激活conda环境
echo 正在激活conda环境...
call conda activate smart-monitoring

REM 启动服务
echo 正在启动服务...
python start_services.py

pause