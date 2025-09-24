"""
用户管理相关的API端点
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import structlog
from datetime import datetime

from app.models.schemas import APIResponse

logger = structlog.get_logger(__name__)

# 创建路由器
router = APIRouter()

# 模拟用户数据存储
users_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@company.com",
        "role": "admin",
        "status": "active",
        "lastLogin": "2025-09-21 22:30:15",
        "createdAt": "2025-01-01 00:00:00"
    },
    {
        "id": 2,
        "username": "operator",
        "email": "ops@company.com",
        "role": "operator",
        "status": "active",
        "lastLogin": "2025-09-21 20:15:32",
        "createdAt": "2025-01-15 09:00:00"
    },
    {
        "id": 3,
        "username": "viewer",
        "email": "view@company.com",
        "role": "viewer",
        "status": "inactive",
        "lastLogin": "2025-09-20 14:22:10",
        "createdAt": "2025-02-01 16:30:00"
    }
]


@router.get("/", response_model=APIResponse)
async def get_users() -> APIResponse:
    """获取用户列表"""
    try:
        return APIResponse(
            success=True,
            message=f"获取到 {len(users_db)} 个用户",
            data={"users": users_db, "total": len(users_db)}
        )
    except Exception as e:
        logger.error("获取用户列表失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.post("/", response_model=APIResponse)
async def create_user(user_data: Dict[str, Any] = Body(...)) -> APIResponse:
    """创建用户"""
    try:
        # 验证用户名是否已存在
        existing_user = next((u for u in users_db if u["username"] == user_data["username"]), None)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 验证邮箱是否已存在
        existing_email = next((u for u in users_db if u["email"] == user_data["email"]), None)
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱地址已存在")
        
        # 创建新用户
        new_user = {
            "id": max(u["id"] for u in users_db) + 1 if users_db else 1,
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data.get("role", "viewer"),
            "status": user_data.get("status", "active"),
            "lastLogin": "从未登录",
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        users_db.append(new_user)
        
        logger.info("用户创建成功", username=new_user["username"])
        
        return APIResponse(
            success=True,
            message="用户创建成功",
            data={"user": new_user}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("创建用户失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.put("/{user_id}", response_model=APIResponse)
async def update_user(user_id: int, user_data: Dict[str, Any] = Body(...)) -> APIResponse:
    """更新用户信息"""
    try:
        # 查找用户
        user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 如果更新邮箱，检查是否已存在
        if "email" in user_data:
            existing_email = next((u for u in users_db if u["email"] == user_data["email"] and u["id"] != user_id), None)
            if existing_email:
                raise HTTPException(status_code=400, detail="邮箱地址已存在")
        
        # 更新用户信息
        user = users_db[user_index]
        if "email" in user_data:
            user["email"] = user_data["email"]
        if "role" in user_data:
            user["role"] = user_data["role"]
        if "status" in user_data:
            user["status"] = user_data["status"]
        
        logger.info("用户信息更新成功", username=user["username"])
        
        return APIResponse(
            success=True,
            message="用户信息更新成功",
            data={"user": user}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("更新用户失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.delete("/{user_id}", response_model=APIResponse)
async def delete_user(user_id: int) -> APIResponse:
    """删除用户"""
    try:
        # 查找用户
        user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 不允许删除admin用户
        user = users_db[user_index]
        if user["username"] == "admin":
            raise HTTPException(status_code=400, detail="不允许删除管理员用户")
        
        # 删除用户
        deleted_user = users_db.pop(user_index)
        
        logger.info("用户删除成功", username=deleted_user["username"])
        
        return APIResponse(
            success=True,
            message="用户删除成功",
            data={"deletedUser": deleted_user}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("删除用户失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.post("/{user_id}/toggle-status", response_model=APIResponse)
async def toggle_user_status(user_id: int) -> APIResponse:
    """切换用户状态"""
    try:
        # 查找用户
        user_index = next((i for i, u in enumerate(users_db) if u["id"] == user_id), None)
        if user_index is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user = users_db[user_index]
        
        # 不允许禁用admin用户
        if user["username"] == "admin" and user["status"] == "active":
            raise HTTPException(status_code=400, detail="不允许禁用管理员用户")
        
        # 切换状态
        new_status = "inactive" if user["status"] == "active" else "active"
        user["status"] = new_status
        
        status_text = "启用" if new_status == "active" else "禁用"
        logger.info("用户状态切换成功", username=user["username"], status=new_status)
        
        return APIResponse(
            success=True,
            message=f"用户{status_text}成功",
            data={"user": user}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("切换用户状态失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"切换用户状态失败: {str(e)}")


@router.post("/{user_id}/reset-password", response_model=APIResponse)
async def reset_user_password(user_id: int) -> APIResponse:
    """重置用户密码"""
    try:
        # 查找用户
        user = next((u for u in users_db if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 模拟重置密码（实际应该生成新密码并发送邮件）
        logger.info("用户密码重置成功", username=user["username"])
        
        return APIResponse(
            success=True,
            message="密码重置成功，新密码已发送至用户邮箱",
            data={"username": user["username"], "email": user["email"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("重置用户密码失败", error=str(e))
        raise HTTPException(status_code=500, detail=f"重置用户密码失败: {str(e)}")

