#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 快速启动脚本
一键初始化开发环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command: str, description: str = None):
    """执行命令"""
    if description:
        print(f"🔄 {description}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {command}")
        print(f"错误信息: {result.stderr}")
        sys.exit(1)
    
    if description:
        print(f"✅ {description} 完成")
    
    return result.stdout


def check_requirements():
    """检查环境要求"""
    print("🔍 检查环境要求...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 11:
        print("❌ 需要Python 3.11或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}")
    
    # 检查Node.js版本
    try:
        node_version = run_command("node --version").strip()
        print(f"✅ Node.js版本: {node_version}")
    except:
        print("❌ 需要安装Node.js 22.11或更高版本")
        sys.exit(1)
    
    # 检查Docker
    try:
        docker_version = run_command("docker --version").strip()
        print(f"✅ Docker版本: {docker_version}")
    except:
        print("⚠️ Docker未安装，容器化部署将不可用")


def setup_backend():
    """设置后端环境"""
    print("\n🐍 设置Python后端环境...")
    
    backend_dir = Path("backend")
    
    # 创建虚拟环境
    if not (backend_dir / "venv").exists():
        run_command(
            f"cd {backend_dir} && python -m venv venv",
            "创建Python虚拟环境"
        )
    
    # 激活虚拟环境并安装依赖
    if sys.platform == "win32":
        activate_cmd = f"cd {backend_dir} && venv\\Scripts\\activate &&"
    else:
        activate_cmd = f"cd {backend_dir} && source venv/bin/activate &&"
    
    run_command(
        f"{activate_cmd} pip install --upgrade pip && pip install -r requirements.txt",
        "安装Python依赖"
    )


def setup_frontend():
    """设置前端环境"""
    print("\n🎨 设置Vue.js前端环境...")
    
    frontend_dir = Path("frontend")
    
    # 安装npm依赖
    run_command(
        f"cd {frontend_dir} && npm install",
        "安装Node.js依赖"
    )


def setup_env_files():
    """设置环境配置文件"""
    print("\n⚙️ 设置环境配置...")
    
    # 后端环境配置
    if not Path(".env").exists():
        shutil.copy(".env.example", ".env")
        print("✅ 创建后端环境配置文件 .env")
    
    # 前端环境配置
    frontend_env = Path("frontend") / ".env"
    frontend_env_example = Path("frontend") / ".env.example"
    
    if not frontend_env.exists() and frontend_env_example.exists():
        shutil.copy(frontend_env_example, frontend_env)
        print("✅ 创建前端环境配置文件 frontend/.env")


def setup_database():
    """设置数据库"""
    print("\n🗄️ 设置数据库...")
    
    # 检查是否有Docker
    try:
        run_command("docker --version > nul 2>&1" if sys.platform == "win32" else "docker --version > /dev/null 2>&1")
        
        # 启动PostgreSQL容器
        run_command(
            "docker run -d --name smart-monitoring-postgres "
            "-e POSTGRES_USER=monitoring "
            "-e POSTGRES_PASSWORD=monitoring123 "
            "-e POSTGRES_DB=smart_monitoring "
            "-p 5432:5432 "
            "postgres:15-alpine",
            "启动PostgreSQL数据库容器"
        )
        
        # 启动Redis容器
        run_command(
            "docker run -d --name smart-monitoring-redis "
            "-p 6379:6379 "
            "redis:7-alpine redis-server --requirepass redis123",
            "启动Redis缓存容器"
        )
        
        print("✅ 数据库容器已启动")
        
    except:
        print("⚠️ Docker不可用，请手动安装PostgreSQL和Redis")


def main():
    """主函数"""
    print("🚀 智能监控预警系统 - 开发环境初始化")
    print("=" * 50)
    
    # 检查环境要求
    check_requirements()
    
    # 设置环境配置
    setup_env_files()
    
    # 设置后端
    setup_backend()
    
    # 设置前端
    setup_frontend()
    
    # 设置数据库
    setup_database()
    
    print("\n" + "=" * 50)
    print("🎉 开发环境初始化完成！")
    print("\n📋 下一步操作:")
    print("1. 检查并修改 .env 文件中的配置")
    print("2. 启动后端: cd backend && python main.py")
    print("3. 启动前端: cd frontend && npm run dev")
    print("4. 访问应用: http://localhost:3000")
    print("\n📚 更多信息请查看 README.md")


if __name__ == "__main__":
    main()