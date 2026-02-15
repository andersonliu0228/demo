"""
EA Routes
EA 專用 API 路由 - 供 MT4/MT5 EA 調用
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.user import User
from backend.app.models.follower_relation import FollowerRelation
from backend.app.models.global_setting import GlobalSetting

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/ea", tags=["ea"])


# Pydantic 模型
class EAConfigResponse(BaseModel):
    """EA 配置回應"""
    user_id: int
    username: str
    is_active: bool
    copy_ratio: float
    emergency_stop: bool
    last_seen: str | None
    message: str


@router.get("/config", response_model=EAConfigResponse)
async def get_ea_config(
    user_id: int = Query(..., description="用戶 ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取 EA 配置
    
    供 MT4/MT5 EA 調用，獲取該用戶的跟單配置
    
    重要：每次調用會自動更新該用戶的 last_seen 時間
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        用戶的跟單配置（copy_ratio, is_active, emergency_stop）
    """
    try:
        logger.info(f"📡 EA 請求配置: user_id={user_id}")
        
        # 1. 查詢用戶
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到用戶 ID: {user_id}"
            )
        
        # 2. 更新 last_seen（心跳）
        user.last_seen = datetime.utcnow()
        await db.commit()
        logger.info(f"💓 更新心跳: user={user.username}, last_seen={user.last_seen}")
        
        # 3. 查詢跟單關係（如果是 follower）
        copy_ratio = 1.0
        relation_active = True
        
        if user.role == "follower":
            stmt = select(FollowerRelation).where(
                FollowerRelation.follower_id == user_id
            )
            result = await db.execute(stmt)
            relation = result.scalar_one_or_none()
            
            if relation:
                copy_ratio = relation.copy_ratio
                relation_active = (relation.status == "active")
                logger.info(f"📊 跟單關係: copy_ratio={copy_ratio}, status={relation.status}")
        
        # 4. 查詢全局緊急停止設定
        stmt = select(GlobalSetting).where(
            GlobalSetting.key == "emergency_stop_all"
        )
        result = await db.execute(stmt)
        emergency_setting = result.scalar_one_or_none()
        
        emergency_stop = False
        if emergency_setting:
            emergency_stop = emergency_setting.value_bool or False
            logger.info(f"🚨 緊急全停狀態: {emergency_stop}")
        
        # 5. 計算最終狀態
        final_active = user.is_active and relation_active and not emergency_stop
        
        response = EAConfigResponse(
            user_id=user.id,
            username=user.username,
            is_active=final_active,
            copy_ratio=copy_ratio,
            emergency_stop=emergency_stop,
            last_seen=user.last_seen.isoformat() if user.last_seen else None,
            message="配置獲取成功" if final_active else "跟單已停用"
        )
        
        logger.info(f"✅ EA 配置回應: user={user.username}, active={final_active}, ratio={copy_ratio}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 獲取 EA 配置失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取 EA 配置失敗: {str(e)}"
        )


@router.get("/heartbeat")
async def ea_heartbeat(
    user_id: int = Query(..., description="用戶 ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    EA 心跳端點
    
    簡單的心跳檢查，只更新 last_seen
    
    Args:
        user_id: 用戶 ID
        
    Returns:
        心跳確認
    """
    try:
        # 查詢用戶
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到用戶 ID: {user_id}"
            )
        
        # 更新 last_seen
        user.last_seen = datetime.utcnow()
        await db.commit()
        
        return {
            "status": "ok",
            "user_id": user.id,
            "username": user.username,
            "last_seen": user.last_seen.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 心跳失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"心跳失敗: {str(e)}"
        )
