"""
Follower Engine Routes
跟單引擎 API 路由
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.follower_engine import get_follower_engine, FollowerEngine
from backend.app.services.credential_service import CredentialService
from backend.app.services.crypto_service import get_crypto_service
from backend.app.services.exchange_service import get_exchange_service
from backend.app.services.cache_service import get_cache_service
from backend.app.repositories.credential_repository import CredentialRepository
from backend.app.models.follow_relationship import FollowRelationship
from backend.app.models.trade_history import TradeHistory
from backend.app.models.master_position import MasterPosition
from backend.app.models.trade_log import TradeLog
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/follower", tags=["follower"])


# Pydantic 模型
class CreateFollowRelationshipRequest(BaseModel):
    """創建跟隨關係請求"""
    follower_user_id: int
    master_user_id: int
    follow_ratio: float
    follower_credential_id: int
    master_credential_id: int


class UpdateMasterPositionRequest(BaseModel):
    """更新 Master 倉位請求"""
    master_user_id: int
    master_credential_id: int
    symbol: str
    position_size: float
    entry_price: float = None


def get_credential_service(db: AsyncSession = Depends(get_db)) -> CredentialService:
    """獲取 Credential Service"""
    credential_repo = CredentialRepository(db)
    crypto_service = get_crypto_service(settings.ENCRYPTION_KEY)
    exchange_service = get_exchange_service()
    cache_service = get_cache_service(settings.REDIS_URL)
    
    return CredentialService(
        credential_repo=credential_repo,
        crypto_service=crypto_service,
        exchange_service=exchange_service,
        cache_service=cache_service
    )


def get_engine(
    db: AsyncSession = Depends(get_db),
    credential_service: CredentialService = Depends(get_credential_service)
) -> FollowerEngine:
    """獲取 Follower Engine"""
    return get_follower_engine(db, credential_service)


@router.post("/relationships", response_model=Dict[str, Any])
async def create_follow_relationship(
    request: CreateFollowRelationshipRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    創建跟隨關係
    
    建立跟隨者與 Master 之間的跟單關係
    """
    try:
        relationship = FollowRelationship(
            follower_user_id=request.follower_user_id,
            master_user_id=request.master_user_id,
            follow_ratio=request.follow_ratio,
            follower_credential_id=request.follower_credential_id,
            master_credential_id=request.master_credential_id,
            is_active=True
        )
        
        db.add(relationship)
        await db.commit()
        await db.refresh(relationship)
        
        logger.info(f"創建跟隨關係成功 - ID: {relationship.id}")
        
        return {
            "success": True,
            "relationship_id": relationship.id,
            "follower_user_id": relationship.follower_user_id,
            "master_user_id": relationship.master_user_id,
            "follow_ratio": relationship.follow_ratio,
            "is_active": relationship.is_active
        }
        
    except Exception as e:
        logger.error(f"創建跟隨關係失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"創建失敗: {str(e)}")


@router.get("/relationships", response_model=List[Dict[str, Any]])
async def list_follow_relationships(
    db: AsyncSession = Depends(get_db),
    follower_user_id: int = None,
    master_user_id: int = None
):
    """
    列出跟隨關係
    
    可選擇性過濾跟隨者或 Master
    """
    try:
        query = select(FollowRelationship)
        
        if follower_user_id:
            query = query.where(FollowRelationship.follower_user_id == follower_user_id)
        if master_user_id:
            query = query.where(FollowRelationship.master_user_id == master_user_id)
        
        result = await db.execute(query)
        relationships = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "follower_user_id": r.follower_user_id,
                "master_user_id": r.master_user_id,
                "follow_ratio": r.follow_ratio,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat()
            }
            for r in relationships
        ]
        
    except Exception as e:
        logger.error(f"列出跟隨關係失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.post("/master-position", response_model=Dict[str, Any])
async def update_master_position(
    request: UpdateMasterPositionRequest,
    engine: FollowerEngine = Depends(get_engine)
):
    """
    更新 Master 倉位（模擬 Master 下單）
    
    此接口用於模擬 Master 開倉/平倉，觸發跟單引擎執行跟單
    """
    try:
        await engine.update_master_position(
            master_user_id=request.master_user_id,
            master_credential_id=request.master_credential_id,
            symbol=request.symbol,
            position_size=request.position_size,
            entry_price=request.entry_price
        )
        
        return {
            "success": True,
            "message": "Master 倉位已更新",
            "master_user_id": request.master_user_id,
            "symbol": request.symbol,
            "position_size": request.position_size,
            "entry_price": request.entry_price
        }
        
    except Exception as e:
        logger.error(f"更新 Master 倉位失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新失敗: {str(e)}")


@router.get("/master-positions", response_model=List[Dict[str, Any]])
async def list_master_positions(
    db: AsyncSession = Depends(get_db),
    master_user_id: int = None
):
    """列出 Master 倉位"""
    try:
        query = select(MasterPosition)
        
        if master_user_id:
            query = query.where(MasterPosition.master_user_id == master_user_id)
        
        result = await db.execute(query)
        positions = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "master_user_id": p.master_user_id,
                "symbol": p.symbol,
                "position_size": p.position_size,
                "entry_price": p.entry_price,
                "last_updated": p.last_updated.isoformat()
            }
            for p in positions
        ]
        
    except Exception as e:
        logger.error(f"列出 Master 倉位失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get("/trade-history", response_model=List[Dict[str, Any]])
async def list_trade_history(
    db: AsyncSession = Depends(get_db),
    follow_relationship_id: int = None,
    limit: int = 50
):
    """
    列出交易歷史
    
    查看跟單執行的詳細記錄，包含跟單比例、成交價格、滑價預估
    """
    try:
        query = select(TradeHistory).order_by(TradeHistory.created_at.desc()).limit(limit)
        
        if follow_relationship_id:
            query = query.where(TradeHistory.follow_relationship_id == follow_relationship_id)
        
        result = await db.execute(query)
        trades = result.scalars().all()
        
        return [
            {
                "id": t.id,
                "follow_relationship_id": t.follow_relationship_id,
                "symbol": t.symbol,
                "side": t.side,
                "order_type": t.order_type,
                "amount": t.amount,
                "price": t.price,
                "follow_ratio": t.follow_ratio,
                "estimated_slippage": t.estimated_slippage,
                "estimated_slippage_percent": f"{t.estimated_slippage * 100:.3f}%" if t.estimated_slippage else None,
                "actual_fill_price": t.actual_fill_price,
                "master_position_size": t.master_position_size,
                "order_id": t.order_id,
                "status": t.status,
                "error_message": t.error_message,
                "created_at": t.created_at.isoformat(),
                "executed_at": t.executed_at.isoformat() if t.executed_at else None
            }
            for t in trades
        ]
        
    except Exception as e:
        logger.error(f"列出交易歷史失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.post("/engine/start", response_model=Dict[str, Any])
async def start_engine(engine: FollowerEngine = Depends(get_engine)):
    """啟動跟單監控引擎"""
    try:
        await engine.start()
        return {
            "success": True,
            "message": "Follower Engine 已啟動",
            "poll_interval": engine.poll_interval
        }
    except Exception as e:
        logger.error(f"啟動引擎失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"啟動失敗: {str(e)}")


@router.post("/engine/stop", response_model=Dict[str, Any])
async def stop_engine(engine: FollowerEngine = Depends(get_engine)):
    """停止跟單監控引擎"""
    try:
        await engine.stop()
        return {
            "success": True,
            "message": "Follower Engine 已停止"
        }
    except Exception as e:
        logger.error(f"停止引擎失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"停止失敗: {str(e)}")


@router.get("/engine/status", response_model=Dict[str, Any])
async def get_engine_status(engine: FollowerEngine = Depends(get_engine)):
    """獲取引擎狀態"""
    return {
        "is_running": engine.is_running,
        "poll_interval": engine.poll_interval
    }


@router.get("/trade-logs", response_model=List[Dict[str, Any]])
async def list_trade_logs(
    db: AsyncSession = Depends(get_db),
    master_user_id: int = None,
    follower_user_id: int = None,
    status: str = None,
    limit: int = 100
):
    """
    列出交易日誌 (Trade Logs)
    
    查看詳細的跟單執行日誌，包含 Master 動作和跟隨者動作
    """
    try:
        query = select(TradeLog).order_by(TradeLog.timestamp.desc()).limit(limit)
        
        if master_user_id:
            query = query.where(TradeLog.master_user_id == master_user_id)
        if follower_user_id:
            query = query.where(TradeLog.follower_user_id == follower_user_id)
        if status:
            query = query.where(TradeLog.status == status)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
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
        
    except Exception as e:
        logger.error(f"列出交易日誌失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get("/trade-logs/stats", response_model=Dict[str, Any])
async def get_trade_logs_stats(
    db: AsyncSession = Depends(get_db),
    master_user_id: int = None,
    follower_user_id: int = None
):
    """
    獲取交易日誌統計
    
    統計成功率、總交易次數等
    """
    try:
        query = select(TradeLog)
        
        if master_user_id:
            query = query.where(TradeLog.master_user_id == master_user_id)
        if follower_user_id:
            query = query.where(TradeLog.follower_user_id == follower_user_id)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        total_count = len(logs)
        success_count = sum(1 for log in logs if log.is_success)
        failed_count = sum(1 for log in logs if not log.is_success)
        
        avg_execution_time = None
        if logs:
            execution_times = [log.execution_time_ms for log in logs if log.execution_time_ms is not None]
            if execution_times:
                avg_execution_time = sum(execution_times) / len(execution_times)
        
        return {
            "total_trades": total_count,
            "successful_trades": success_count,
            "failed_trades": failed_count,
            "success_rate": (success_count / total_count * 100) if total_count > 0 else 0,
            "average_execution_time_ms": avg_execution_time
        }
        
    except Exception as e:
        logger.error(f"獲取交易統計失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")
