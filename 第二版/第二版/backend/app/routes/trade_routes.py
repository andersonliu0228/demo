"""
Trade Routes
交易歷史 API 路由
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import get_current_active_user
from backend.app.models.user import User
from backend.app.models.trade_log import TradeLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/trades", tags=["trades"])


# Pydantic 模型
class TradeLogResponse(BaseModel):
    """交易記錄響應"""
    id: int
    timestamp: str
    master_user_id: int
    master_credential_id: int
    master_action: str
    master_symbol: str
    master_position_size: float
    master_entry_price: Optional[float]
    follower_user_id: int
    follower_credential_id: int
    follower_action: str
    follower_ratio: float
    follower_amount: float
    order_type: str
    side: str
    order_id: Optional[str]
    status: str
    is_success: bool
    error_message: Optional[str]
    execution_time_ms: Optional[int]


@router.get("/history", response_model=list[TradeLogResponse])
async def get_trade_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    symbol: Optional[str] = Query(None, description="篩選交易對"),
    status: Optional[str] = Query(None, description="篩選狀態 (pending/success/failed)"),
    start_date: Optional[str] = Query(None, description="開始日期 (ISO 8601)"),
    end_date: Optional[str] = Query(None, description="結束日期 (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="返回記錄數量"),
    offset: int = Query(0, ge=0, description="跳過記錄數量")
):
    """
    獲取交易歷史
    
    查詢當前用戶的所有交易記錄（作為 Master 或 Follower）
    支援按交易對、狀態、日期範圍篩選
    """
    try:
        # 構建查詢條件
        conditions = [
            or_(
                TradeLog.master_user_id == current_user.id,
                TradeLog.follower_user_id == current_user.id
            )
        ]
        
        if symbol:
            conditions.append(TradeLog.master_symbol == symbol)
        
        if status:
            conditions.append(TradeLog.status == status)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                conditions.append(TradeLog.timestamp >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="無效的開始日期格式，請使用 ISO 8601 格式"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                conditions.append(TradeLog.timestamp <= end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="無效的結束日期格式，請使用 ISO 8601 格式"
                )
        
        # 執行查詢
        stmt = (
            select(TradeLog)
            .where(and_(*conditions))
            .order_by(desc(TradeLog.timestamp))
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(stmt)
        trades = result.scalars().all()
        
        logger.info(
            f"用戶 {current_user.id} 查詢交易歷史 - "
            f"找到 {len(trades)} 筆記錄"
        )
        
        return [
            TradeLogResponse(
                id=trade.id,
                timestamp=trade.timestamp.isoformat(),
                master_user_id=trade.master_user_id,
                master_credential_id=trade.master_credential_id,
                master_action=trade.master_action,
                master_symbol=trade.master_symbol,
                master_position_size=trade.master_position_size,
                master_entry_price=trade.master_entry_price,
                follower_user_id=trade.follower_user_id,
                follower_credential_id=trade.follower_credential_id,
                follower_action=trade.follower_action,
                follower_ratio=trade.follower_ratio,
                follower_amount=trade.follower_amount,
                order_type=trade.order_type,
                side=trade.side,
                order_id=trade.order_id,
                status=trade.status,
                is_success=trade.is_success,
                error_message=trade.error_message,
                execution_time_ms=trade.execution_time_ms
            )
            for trade in trades
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查詢交易歷史失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查詢交易歷史失敗"
        )
