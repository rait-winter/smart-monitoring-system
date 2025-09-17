import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # 尝试导入并运行主应用
    from backend.main import app
    print("应用导入成功")
    
    # 尝试导入配置
    from backend.app.core.config import settings
    print("配置加载成功")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"Prometheus URL: {settings.PROMETHEUS_URL}")
    
except Exception as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()