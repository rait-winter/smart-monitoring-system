#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能监控预警系统 - 服务启动脚本
用于同时启动后端和前端服务
"""

import subprocess
import sys
import os
import signal
import time
from threading import Thread

# 全局变量存储进程
backend_process = None
frontend_process = None

def signal_handler(sig, frame):
    """信号处理函数，用于优雅关闭所有进程"""
    print("\n正在关闭所有服务...")
    if backend_process:
        backend_process.terminate()
    if frontend_process:
        frontend_process.terminate()
    sys.exit(0)

def start_backend():
    """启动后端服务"""
    global backend_process
    try:
        print("正在启动后端服务...")
        backend_process = subprocess.Popen([
            "python", "main.py"
        ], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 实时输出后端日志
        def print_backend_output():
            if backend_process.stdout:
                for line in iter(backend_process.stdout.readline, ''):
                    print(f"[后端] {line}", end='')
        
        Thread(target=print_backend_output, daemon=True).start()
        
        # 等待几秒钟看是否有错误
        time.sleep(3)
        if backend_process.poll() is not None:
            print("❌ 后端服务启动失败")
            stderr = backend_process.stderr.read() if backend_process.stderr else ""
            print(f"错误信息: {stderr}")
            return False
        else:
            print("✅ 后端服务启动中...")
            return True
    except Exception as e:
        print(f"❌ 后端服务启动异常: {e}")
        return False

def start_frontend():
    """启动前端服务"""
    global frontend_process
    try:
        print("正在启动前端服务...")
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd="frontend", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 实时输出前端日志
        def print_frontend_output():
            if frontend_process.stdout:
                for line in iter(frontend_process.stdout.readline, ''):
                    print(f"[前端] {line}", end='')
        
        Thread(target=print_frontend_output, daemon=True).start()
        
        # 等待几秒钟看是否有错误
        time.sleep(3)
        if frontend_process.poll() is not None:
            print("❌ 前端服务启动失败")
            stderr = frontend_process.stderr.read() if frontend_process.stderr else ""
            print(f"错误信息: {stderr}")
            return False
        else:
            print("✅ 前端服务启动中...")
            return True
    except Exception as e:
        print(f"❌ 前端服务启动异常: {e}")
        return False

def main():
    """主函数"""
    print("智能监控预警系统 - 服务启动器")
    print("=" * 40)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查目录是否存在
    if not os.path.exists("backend"):
        print("❌ 找不到backend目录")
        return
    
    if not os.path.exists("frontend"):
        print("❌ 找不到frontend目录")
        return
    
    # 启动服务
    backend_ok = start_backend()
    frontend_ok = start_frontend()
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有服务已启动!")
        print("后端服务地址: http://192.168.10.35:8000")
        print("前端服务地址: http://192.168.10.35:3000")
        print("API文档地址: http://192.168.10.35:8000/docs")
        print("按 Ctrl+C 停止所有服务")
        
        # 保持主进程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
    else:
        print("\n❌ 服务启动失败，请检查错误信息")
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()