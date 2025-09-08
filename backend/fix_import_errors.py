#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复导入错误的脚本
"""

import os
import sys
from pathlib import Path

def fix_alembic_env():
    """修复Alembic环境文件"""
    alembic_env_path = Path("alembic/env.py")
    if alembic_env_path.exists():
        content = alembic_env_path.read_text(encoding='utf-8')
        # 确保导入语句正确
        fixed_content = content.replace(
            "from alembic import context",
            "from alembic import context\nfrom sqlalchemy import engine_from_config, pool"
        )
        alembic_env_path.write_text(fixed_content, encoding='utf-8')
        print("✅ 修复 alembic/env.py 完成")

def fix_config_imports():
    """修复配置文件导入"""
    config_path = Path("app/core/config.py")
    if config_path.exists():
        content = config_path.read_text(encoding='utf-8')
        # 确保pydantic导入正确
        if "from pydantic import" in content and "from pydantic_settings import" not in content:
            content = content.replace(
                "from pydantic import BaseModel, Field, field_validator, model_validator",
                "from pydantic import BaseModel, Field, field_validator, model_validator\nfrom pydantic_settings import BaseSettings"
            )
        config_path.write_text(content, encoding='utf-8')
        print("✅ 修复 app/core/config.py 完成")

def fix_database_imports():
    """修复数据库文件导入"""
    database_path = Path("app/core/database.py")
    if database_path.exists():
        content = database_path.read_text(encoding='utf-8')
        # 确保SQLAlchemy导入正确
        fixed_content = content.replace(
            "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker",
            "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker"
        )
        database_path.write_text(fixed_content, encoding='utf-8')
        print("✅ 修复 app/core/database.py 完成")

def fix_rule_engine_imports():
    """修复规则引擎导入"""
    rule_engine_path = Path("app/services/rule_engine.py")
    if rule_engine_path.exists():
        content = rule_engine_path.read_text(encoding='utf-8')
        # 确保NotificationChannel正确导入
        if "from app.models.schemas import" in content:
            # 检查NotificationChannel是否在导入列表中
            if "NotificationChannel" not in content.split("from app.models.schemas import")[1].split(")")[0]:
                # 添加NotificationChannel到导入列表
                content = content.replace(
                    "from app.models.schemas import (",
                    "from app.models.schemas import (\n    NotificationChannel,"
                )
        rule_engine_path.write_text(content, encoding='utf-8')
        print("✅ 修复 app/services/rule_engine.py 完成")

def fix_main_imports():
    """修复主文件导入"""
    main_path = Path("main.py")
    if main_path.exists():
        content = main_path.read_text(encoding='utf-8')
        # 确保dotenv导入正确
        if "from dotenv import load_dotenv" not in content:
            content = content.replace(
                "# 确保在导入其他模块之前加载环境变量",
                "# 确保在导入其他模块之前加载环境变量\nfrom dotenv import load_dotenv"
            )
        main_path.write_text(content, encoding='utf-8')
        print("✅ 修复 main.py 完成")

def fix_scss_syntax():
    """修复SCSS语法错误"""
    # 修复mixins.scss
    mixins_path = Path("frontend/src/styles/mixins.scss")
    if mixins_path.exists():
        content = mixins_path.read_text(encoding='utf-8')
        # 修复color.mix函数调用
        content = content.replace("color.mix(", "mix(")
        mixins_path.write_text(content, encoding='utf-8')
        print("✅ 修复 frontend/src/styles/mixins.scss 完成")
    
    # 修复responsive.scss
    responsive_path = Path("frontend/src/styles/responsive.scss")
    if responsive_path.exists():
        content = responsive_path.read_text(encoding='utf-8')
        # 修复map函数调用
        content = content.replace("map.has-key(", "map-has-key(")
        content = content.replace("map.get(", "map-get(")
        responsive_path.write_text(content, encoding='utf-8')
        print("✅ 修复 frontend/src/styles/responsive.scss 完成")

def fix_vue_imports():
    """修复Vue导入问题"""
    # 修复components/index.ts
    index_path = Path("frontend/src/components/index.ts")
    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
        # 确保正确的Vue导入
        if "import { type App } from 'vue'" in content:
            content = content.replace(
                "import { type App } from 'vue'",
                "import type { App } from 'vue'"
            )
        index_path.write_text(content, encoding='utf-8')
        print("✅ 修复 frontend/src/components/index.ts 完成")

def main():
    """主函数"""
    print("🔧 开始修复导入错误...")
    
    # 切换到后端目录
    backend_dir = Path("backend")
    if backend_dir.exists():
        os.chdir(backend_dir)
        print(f"📂 切换到目录: {os.getcwd()}")
    
    # 修复各种导入问题
    fix_alembic_env()
    fix_config_imports()
    fix_database_imports()
    fix_rule_engine_imports()
    fix_main_imports()
    
    # 切换到前端目录
    frontend_dir = Path("../frontend")
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        print(f"📂 切换到目录: {os.getcwd()}")
        
        # 修复SCSS和Vue导入问题
        fix_scss_syntax()
        fix_vue_imports()
    
    print("🎉 所有导入错误修复完成！")

if __name__ == "__main__":
    main()