#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发环境启动脚本

自动启动后端开发服务器和相关服务
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT

def signal_handler(sig, frame):
    """信号处理函数"""
    print("\n正在停止开发服务器...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 启动智能监控预警系统开发环境...")
    print(f"项目路径: {PROJECT_ROOT}")
    
    # 检查虚拟环境
    if not os.path.exists(BACKEND_DIR / "venv"):
        print("⚠️  虚拟环境未找到，建议先创建虚拟环境:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate   # Windows")
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 启动FastAPI开发服务器
    print("🔧 启动FastAPI开发服务器...")
    print("📖 API文档: http://localhost:8000/api/docs")
    print("📊 健康检查: http://localhost:8000/health")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 使用uvicorn启动开发服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=BACKEND_DIR)
    except KeyboardInterrupt:
        print("\n👋 开发服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()