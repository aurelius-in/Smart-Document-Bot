from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.memory_service import MemoryService

router = APIRouter()


class SystemSettings(BaseModel):
    """System settings model"""
    ocr_confidence_threshold: float = 0.8
    max_file_size_mb: int = 50
    allowed_file_types: list[str] = [".pdf", ".docx", ".txt", ".jpg", ".png"]
    processing_timeout_seconds: int = 300
    enable_audit_logging: bool = True
    enable_pii_redaction: bool = True
    default_comparison_type: str = "semantic"
    max_concurrent_processes: int = 4


class UserSettings(BaseModel):
    """User settings model"""
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"
    notifications_enabled: bool = True
    email_notifications: bool = False
    default_page_size: int = 20
    auto_refresh_interval: int = 30


# Mock settings storage - in production, this would be a database
SYSTEM_SETTINGS = SystemSettings()
USER_SETTINGS = {}


@router.get("/system", response_model=SystemSettings)
async def get_system_settings(
    current_user: dict = Depends(require_permissions(["read"]))
):
    """Get system settings"""
    return SYSTEM_SETTINGS


@router.put("/system")
async def update_system_settings(
    settings: SystemSettings,
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """Update system settings (admin only)"""
    global SYSTEM_SETTINGS
    SYSTEM_SETTINGS = settings
    return {"message": "System settings updated successfully"}


@router.get("/user", response_model=UserSettings)
async def get_user_settings(
    current_user: dict = Depends(get_current_user)
):
    """Get user settings"""
    user_id = current_user["id"]
    return USER_SETTINGS.get(user_id, UserSettings())


@router.put("/user")
async def update_user_settings(
    settings: UserSettings,
    current_user: dict = Depends(get_current_user)
):
    """Update user settings"""
    user_id = current_user["id"]
    USER_SETTINGS[user_id] = settings
    return {"message": "User settings updated successfully"}


@router.get("/features")
async def get_feature_flags(
    current_user: dict = Depends(get_current_user)
):
    """Get feature flags"""
    return {
        "document_comparison": True,
        "agent_traces": True,
        "audit_logging": True,
        "real_time_updates": True,
        "export_functionality": True,
        "advanced_analytics": current_user["role"] == "admin",
        "bulk_operations": current_user["role"] == "admin",
        "api_access": current_user["role"] == "admin"
    }


@router.get("/limits")
async def get_system_limits(
    current_user: dict = Depends(get_current_user)
):
    """Get system limits and quotas"""
    user_role = current_user["role"]
    
    base_limits = {
        "max_file_size_mb": 50,
        "max_files_per_upload": 10,
        "max_documents_per_user": 1000,
        "max_comparisons_per_day": 100,
        "max_traces_per_day": 50,
        "retention_days": 90
    }
    
    if user_role == "admin":
        base_limits.update({
            "max_file_size_mb": 200,
            "max_files_per_upload": 50,
            "max_documents_per_user": 10000,
            "max_comparisons_per_day": 1000,
            "max_traces_per_day": 500,
            "retention_days": 365
        })
    
    return base_limits
