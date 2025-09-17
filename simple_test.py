import sys
import os

# 添加backend目录到Python路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print(f"Python path: {sys.path[:3]}")
print(f"Backend path exists: {os.path.exists(backend_path)}")

try:
    from app.core.config import Settings
    print("✅ 成功导入Settings")
    
    settings = Settings()
    print(f"✅ 成功创建settings实例")
    print(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()