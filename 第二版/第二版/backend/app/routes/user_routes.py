"""
User Routes
用戶 API 路由 - 我的專區
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import get_current_active_user
from backend.app.models.user import User
from backend.app.models.trade_log import TradeLog
from backend.app.models.trade_history import TradeHistory
from backend.app.models.follow_relationship import FollowRelationship
from backend.app.models.api_credential import ApiCredential

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/user", tags=["user"])


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    查看我的帳號狀態
    
    返回當前用戶的詳細資訊和統計數據
    """
    try:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat()
        }
    except Exception as e:
        logger.error(f"獲取用戶資訊失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="獲取用戶資訊失敗")


@router.get("/trades")
async def get_my_trades(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    as_master: bool = None,
    as_follower: bool = None
):
    """
    查看我的跟單歷史紀錄
    
    返回當前用戶作為 Master 或 Follower 的所有交易記錄
    
    Args:
        limit: 返回記錄數量限制
        as_master: 只查看作為 Master 的記錄
        as_follower: 只查看作為 Follower 的記錄
    """
    try:
        query = select(TradeLog).order_by(TradeLog.timestamp.desc()).limit(limit)
        
        # 根據參數過濾
        if as_master and not as_follower:
            query = query.where(TradeLog.master_user_id == current_user.id)
        elif as_follower and not as_master:
            query = query.where(TradeLog.follower_user_id == current_user.id)
        else:
            # 預設：查看所有相關記錄（作為 Master 或 Follower）
            query = query.where(
                or_(
                    TradeLog.master_user_id == current_user.id,
                    TradeLog.follower_user_id == current_user.id
                )
            )
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return {
            "total": len(logs),
            "trades": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "role": "master" if log.master_user_id == current_user.id else "follower",
                    "master_user_id": log.master_user_id,
                    "master_action": log.master_action,
                    "master_symbol": log.master_symbol,
                    "master_position_size": log.master_position_size,
                    "master_entry_price": log.master_entry_price,
                    "follower_user_id": log.follower_user_id,
                    "follower_action": log.follower_action,
                    "follower_ratio": log.follower_ratio,
                    "follower_amount": log.follower_amount,
                    "order_id": log.order_id,
                    "order_type": log.order_type,
                    "side": log.side,
                    "status": log.status,
                    "is_success": log.is_success,
                    "error_message": log.error_message,
                    "execution_time_ms": log.execution_time_ms
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"獲取交易記錄失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="獲取交易記錄失敗")


@router.get("/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查看我的統計資訊
    
    返回當前用戶的交易統計、跟隨關係等資訊
    """
    try:
        # 查詢作為 Master 的交易記錄
        master_query = select(TradeLog).where(TradeLog.master_user_id == current_user.id)
        master_result = await db.execute(master_query)
        master_logs = master_result.scalars().all()
        
        # 查詢作為 Follower 的交易記錄
        follower_query = select(TradeLog).where(TradeLog.follower_user_id == current_user.id)
        follower_result = await db.execute(follower_query)
        follower_logs = follower_result.scalars().all()
        
        # 查詢跟隨關係
        following_query = select(FollowRelationship).where(
            and_(
                FollowRelationship.follower_user_id == current_user.id,
                FollowRelationship.is_active == True
            )
        )
        following_result = await db.execute(following_query)
        following = following_result.scalars().all()
        
        followers_query = select(FollowRelationship).where(
            and_(
                FollowRelationship.master_user_id == current_user.id,
                FollowRelationship.is_active == True
            )
        )
        followers_result = await db.execute(followers_query)
        followers = followers_result.scalars().all()
        
        # 查詢 API 憑證
        credentials_query = select(ApiCredential).where(ApiCredential.user_id == current_user.id)
        credentials_result = await db.execute(credentials_query)
        credentials = credentials_result.scalars().all()
        
        # 計算統計
        master_success = sum(1 for log in master_logs if log.is_success)
        follower_success = sum(1 for log in follower_logs if log.is_success)
        
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "as_master": {
                "total_trades": len(master_logs),
                "successful_trades": master_success,
                "failed_trades": len(master_logs) - master_success,
                "success_rate": (master_success / len(master_logs) * 100) if master_logs else 0,
                "followers_count": len(followers)
            },
            "as_follower": {
                "total_trades": len(follower_logs),
                "successful_trades": follower_success,
                "failed_trades": len(follower_logs) - follower_success,
                "success_rate": (follower_success / len(follower_logs) * 100) if follower_logs else 0,
                "following_count": len(following)
            },
            "credentials_count": len(credentials)
        }
        
    except Exception as e:
        logger.error(f"獲取統計資訊失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="獲取統計資訊失敗")


@router.get("/following")
async def get_my_following(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查看我正在跟隨的 Master
    
    返回當前用戶作為 Follower 的所有跟隨關係
    """
    try:
        query = select(FollowRelationship).where(
            and_(
                FollowRelationship.follower_user_id == current_user.id,
                FollowRelationship.is_active == True
            )
        )
        result = await db.execute(query)
        relationships = result.scalars().all()
        
        return {
            "total": len(relationships),
            "following": [
                {
                    "id": rel.id,
                    "master_user_id": rel.master_user_id,
                    "follow_ratio": rel.follow_ratio,
                    "created_at": rel.created_at.isoformat()
                }
                for rel in relationships
            ]
        }
        
    except Exception as e:
        logger.error(f"獲取跟隨列表失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="獲取跟隨列表失敗")


@router.get("/followers")
async def get_my_followers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查看我的跟隨者
    
    返回當前用戶作為 Master 的所有跟隨者
    """
    try:
        query = select(FollowRelationship).where(
            and_(
                FollowRelationship.master_user_id == current_user.id,
                FollowRelationship.is_active == True
            )
        )
        result = await db.execute(query)
        relationships = result.scalars().all()
        
        return {
            "total": len(relationships),
            "followers": [
                {
                    "id": rel.id,
                    "follower_user_id": rel.follower_user_id,
                    "follow_ratio": rel.follow_ratio,
                    "created_at": rel.created_at.isoformat()
                }
                for rel in relationships
            ]
        }
        
    except Exception as e:
        logger.error(f"獲取跟隨者列表失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="獲取跟隨者列表失敗")
