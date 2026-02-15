"""
Follow Configuration Routes
跟單配置 API 路由
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import get_current_active_user
from backend.app.models.user import User
from backend.app.models.follow_settings import FollowSettings
from backend.app.models.master_position import MasterPosition
from backend.app.models.follower_position import FollowerPosition
from backend.app.models.trade_error import TradeError
from backend.app.repositories.follow_settings_repository import FollowSettingsRepository
from backend.app.repositories.trade_error_repository import TradeErrorRepository
from backend.app.repositories.follower_position_repository import FollowerPositionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/follow-config", tags=["follow-configuration"])


# Pydantic 模型
class FollowSettingsCreate(BaseModel):
    """創建跟單設定請求"""
    master_user_id: int
    master_credential_id: int
    follower_credential_id: int
    follow_ratio: float = 0.1
    is_active: bool = True


class FollowSettingsUpdate(BaseModel):
    """更新跟單設定請求"""
    follow_ratio: Optional[float] = None
    is_active: Optional[bool] = None


class FollowSettingsResponse(BaseModel):
    """跟單設定響應"""
    id: int
    user_id: int
    master_user_id: int
    master_credential_id: int
    follower_credential_id: int
    follow_ratio: float
    is_active: bool
    created_at: str
    updated_at: str


class FollowStatusResponse(BaseModel):
    """跟單狀態響應"""
    user_id: int
    username: str
    is_active: bool
    follow_ratio: float
    master_user_id: int
    has_unresolved_errors: bool
    unresolved_error_count: int
    my_positions: list
    master_positions: list


class TradeErrorResponse(BaseModel):
    """交易錯誤響應"""
    id: int
    user_id: int
    trade_log_id: Optional[int]
    error_type: str
    error_message: str
    is_resolved: bool
    created_at: str


@router.post("/settings", response_model=FollowSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_follow_settings(
    data: FollowSettingsCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    創建跟單設定
    
    設定當前用戶的跟單配置，包括跟隨的 Master、跟單比例等
    """
    try:
        repo = FollowSettingsRepository(db)
        
        # 檢查是否已存在設定
        existing = await repo.get_by_user_id(current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="跟單設定已存在，請使用更新接口"
            )
        
        # 創建設定
        settings = await repo.create(
            user_id=current_user.id,
            master_user_id=data.master_user_id,
            master_credential_id=data.master_credential_id,
            follower_credential_id=data.follower_credential_id,
            follow_ratio=data.follow_ratio,
            is_active=data.is_active
        )
        
        await db.commit()
        
        logger.info(f"用戶 {current_user.id} 創建跟單設定成功")
        
        return FollowSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            master_user_id=settings.master_user_id,
            master_credential_id=settings.master_credential_id,
            follower_credential_id=settings.follower_credential_id,
            follow_ratio=settings.follow_ratio,
            is_active=settings.is_active,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"創建跟單設定失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="創建跟單設定失敗"
        )


@router.get("/settings", response_model=FollowSettingsResponse)
async def get_my_follow_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取我的跟單設定
    
    返回當前用戶的跟單配置
    """
    try:
        repo = FollowSettingsRepository(db)
        settings = await repo.get_by_user_id(current_user.id)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到跟單設定"
            )
        
        return FollowSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            master_user_id=settings.master_user_id,
            master_credential_id=settings.master_credential_id,
            follower_credential_id=settings.follower_credential_id,
            follow_ratio=settings.follow_ratio,
            is_active=settings.is_active,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取跟單設定失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取跟單設定失敗"
        )


@router.put("/settings", response_model=FollowSettingsResponse)
async def update_my_follow_settings(
    data: FollowSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新我的跟單設定
    
    更新跟單比例或啟用/停用跟單
    """
    try:
        repo = FollowSettingsRepository(db)
        
        settings = await repo.update(
            user_id=current_user.id,
            follow_ratio=data.follow_ratio,
            is_active=data.is_active
        )
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到跟單設定"
            )
        
        await db.commit()
        
        logger.info(f"用戶 {current_user.id} 更新跟單設定成功")
        
        return FollowSettingsResponse(
            id=settings.id,
            user_id=settings.user_id,
            master_user_id=settings.master_user_id,
            master_credential_id=settings.master_credential_id,
            follower_credential_id=settings.follower_credential_id,
            follow_ratio=settings.follow_ratio,
            is_active=settings.is_active,
            created_at=settings.created_at.isoformat(),
            updated_at=settings.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新跟單設定失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新跟單設定失敗"
        )


@router.get("/status", response_model=FollowStatusResponse)
async def get_follow_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取跟單狀態儀表板
    
    返回當前帳號的持倉與 Master 的持倉對比
    """
    try:
        # 獲取跟單設定
        settings_repo = FollowSettingsRepository(db)
        settings = await settings_repo.get_by_user_id(current_user.id)
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到跟單設定"
            )
        
        # 檢查未解決的錯誤
        error_repo = TradeErrorRepository(db)
        unresolved_errors = await error_repo.get_unresolved_by_user(current_user.id)
        
        # 獲取 Master 的倉位
        master_result = await db.execute(
            select(MasterPosition).where(
                and_(
                    MasterPosition.master_user_id == settings.master_user_id,
                    MasterPosition.master_credential_id == settings.master_credential_id
                )
            )
        )
        master_positions = master_result.scalars().all()
        
        # 獲取跟隨者的倉位
        position_repo = FollowerPositionRepository(db)
        follower_positions = await position_repo.get_all_positions(current_user.id)
        
        # 構建響應
        return FollowStatusResponse(
            user_id=current_user.id,
            username=current_user.username,
            is_active=settings.is_active,
            follow_ratio=settings.follow_ratio,
            master_user_id=settings.master_user_id,
            has_unresolved_errors=len(unresolved_errors) > 0,
            unresolved_error_count=len(unresolved_errors),
            my_positions=[
                {
                    "symbol": pos.symbol,
                    "position_size": pos.position_size,
                    "entry_price": pos.entry_price,
                    "last_updated": pos.last_updated.isoformat()
                }
                for pos in follower_positions
            ],
            master_positions=[
                {
                    "symbol": pos.symbol,
                    "position_size": pos.position_size,
                    "entry_price": pos.entry_price,
                    "last_updated": pos.last_updated.isoformat(),
                    "expected_follower_size": abs(pos.position_size) * settings.follow_ratio
                }
                for pos in master_positions
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取跟單狀態失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取跟單狀態失敗"
        )


@router.get("/errors", response_model=list[TradeErrorResponse])
async def get_my_errors(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """
    獲取我的交易錯誤
    
    返回當前用戶的交易錯誤記錄
    """
    try:
        error_repo = TradeErrorRepository(db)
        errors = await error_repo.get_recent_errors(
            user_id=current_user.id,
            limit=limit
        )
        
        return [
            TradeErrorResponse(
                id=error.id,
                user_id=error.user_id,
                trade_log_id=error.trade_log_id,
                error_type=error.error_type,
                error_message=error.error_message,
                is_resolved=error.is_resolved,
                created_at=error.created_at.isoformat()
            )
            for error in errors
        ]
        
    except Exception as e:
        logger.error(f"獲取錯誤記錄失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取錯誤記錄失敗"
        )


@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    解決錯誤並恢復跟單
    
    標記錯誤為已解決，並重新啟用跟單
    """
    try:
        error_repo = TradeErrorRepository(db)
        
        # 解決錯誤
        error = await error_repo.resolve(error_id, current_user.id)
        
        if not error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到錯誤記錄"
            )
        
        # 檢查是否還有其他未解決的錯誤
        remaining_errors = await error_repo.get_unresolved_by_user(current_user.id)
        
        # 如果沒有其他錯誤，自動恢復跟單
        if len(remaining_errors) == 0:
            settings_repo = FollowSettingsRepository(db)
            await settings_repo.update(
                user_id=current_user.id,
                is_active=True
            )
            logger.info(f"用戶 {current_user.id} 的跟單已自動恢復")
        
        await db.commit()
        
        return {
            "message": "錯誤已解決",
            "auto_resumed": len(remaining_errors) == 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解決錯誤失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解決錯誤失敗"
        )
