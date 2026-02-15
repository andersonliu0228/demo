"""
Dashboard Routes
儀表板聚合 API 路由 - 專供前端使用
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import get_current_active_user
from backend.app.models.user import User
from backend.app.models.follow_settings import FollowSettings
from backend.app.models.master_position import MasterPosition
from backend.app.models.follower_position import FollowerPosition
from backend.app.models.trade_log import TradeLog
from backend.app.models.trade_error import TradeError
from backend.app.repositories.follow_settings_repository import FollowSettingsRepository
from backend.app.repositories.trade_error_repository import TradeErrorRepository
from backend.app.repositories.follower_position_repository import FollowerPositionRepository
from backend.app.services.follower_engine_v2 import _follower_engine_v2_instance
from backend.app.services.pnl_service import get_pnl_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["dashboard"])


# Pydantic 模型
class PositionSummary(BaseModel):
    """倉位摘要"""
    symbol: str
    position_size: float
    entry_price: Optional[float]
    current_value: float  # 假設價值（實際應從交易所獲取）


class MasterActivity(BaseModel):
    """Master 最新動作"""
    symbol: str
    action: str
    position_size: float
    entry_price: Optional[float]
    timestamp: str


class EngineStatus(BaseModel):
    """引擎狀態"""
    is_running: bool
    status: str  # "Running" or "Stopped"
    poll_interval: int


class RecentTrade(BaseModel):
    """最近交易記錄"""
    id: int
    timestamp: str
    symbol: str
    action: str
    side: str
    amount: float
    status: str
    execution_time_ms: Optional[int]


class DashboardSummary(BaseModel):
    """儀表板摘要響應"""
    # 用戶資訊
    user_id: int
    username: str
    
    # 跟單設定
    is_active: bool
    follow_ratio: float
    master_user_id: Optional[int]
    
    # 總持倉價值
    total_position_value: float
    my_positions: list[PositionSummary]
    
    # Master 最新動作
    master_latest_activity: Optional[MasterActivity]
    master_positions: list[PositionSummary]
    
    # 引擎狀態
    engine_status: EngineStatus
    
    # 最近 5 筆成功交易
    recent_successful_trades: list[RecentTrade]
    
    # 錯誤狀態
    has_unresolved_errors: bool
    unresolved_error_count: int
    
    # PnL 相關（新增）
    unrealized_pnl: float
    unrealized_pnl_percent: float
    realized_pnl: float
    realized_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    獲取儀表板摘要
    
    一次性返回所有儀表板所需的資訊：
    - 當前用戶的總持倉價值
    - Master 目前的最新動作與持倉
    - 跟單引擎的運行狀態
    - 最近 5 筆跟單成功的記錄
    """
    try:
        # 1. 獲取跟單設定
        settings_repo = FollowSettingsRepository(db)
        settings = await settings_repo.get_by_user_id(current_user.id)
        
        is_active = settings.is_active if settings else False
        follow_ratio = settings.follow_ratio if settings else 0.0
        master_user_id = settings.master_user_id if settings else None
        master_credential_id = settings.master_credential_id if settings else None
        
        # 2. 獲取跟隨者倉位
        position_repo = FollowerPositionRepository(db)
        follower_positions = await position_repo.get_all_positions(current_user.id)
        
        # 計算總持倉價值（簡化版：使用開倉價格 × 倉位大小）
        total_position_value = sum(
            abs(pos.position_size) * (pos.entry_price or 0)
            for pos in follower_positions
        )
        
        my_positions = [
            PositionSummary(
                symbol=pos.symbol,
                position_size=pos.position_size,
                entry_price=pos.entry_price,
                current_value=abs(pos.position_size) * (pos.entry_price or 0)
            )
            for pos in follower_positions
        ]
        
        # 3. 獲取 Master 倉位和最新動作
        master_positions_list = []
        master_latest_activity = None
        
        if master_user_id and master_credential_id:
            # 獲取 Master 倉位
            master_result = await db.execute(
                select(MasterPosition).where(
                    and_(
                        MasterPosition.master_user_id == master_user_id,
                        MasterPosition.master_credential_id == master_credential_id
                    )
                ).order_by(desc(MasterPosition.last_updated))
            )
            master_positions = master_result.scalars().all()
            
            master_positions_list = [
                PositionSummary(
                    symbol=pos.symbol,
                    position_size=pos.position_size,
                    entry_price=pos.entry_price,
                    current_value=abs(pos.position_size) * (pos.entry_price or 0)
                )
                for pos in master_positions
            ]
            
            # 獲取 Master 最新動作（最近更新的倉位）
            if master_positions:
                latest_pos = master_positions[0]
                master_latest_activity = MasterActivity(
                    symbol=latest_pos.symbol,
                    action=f"持倉 {latest_pos.position_size}",
                    position_size=latest_pos.position_size,
                    entry_price=latest_pos.entry_price,
                    timestamp=latest_pos.last_updated.isoformat()
                )
        
        # 4. 獲取引擎狀態
        engine_is_running = False
        poll_interval = 3
        
        if _follower_engine_v2_instance:
            engine_is_running = _follower_engine_v2_instance.is_running
            poll_interval = _follower_engine_v2_instance.poll_interval
        
        engine_status = EngineStatus(
            is_running=engine_is_running,
            status="Running" if engine_is_running else "Stopped",
            poll_interval=poll_interval
        )
        
        # 5. 獲取最近 5 筆成功的交易
        trades_result = await db.execute(
            select(TradeLog).where(
                and_(
                    TradeLog.follower_user_id == current_user.id,
                    TradeLog.is_success == True
                )
            ).order_by(desc(TradeLog.timestamp)).limit(5)
        )
        successful_trades = trades_result.scalars().all()
        
        recent_successful_trades = [
            RecentTrade(
                id=trade.id,
                timestamp=trade.timestamp.isoformat(),
                symbol=trade.master_symbol,
                action=trade.follower_action,
                side=trade.side,
                amount=trade.follower_amount,
                status=trade.status,
                execution_time_ms=trade.execution_time_ms
            )
            for trade in successful_trades
        ]
        
        # 6. 檢查未解決的錯誤
        error_repo = TradeErrorRepository(db)
        unresolved_errors = await error_repo.get_unresolved_by_user(current_user.id)
        
        # 7. 計算 PnL（新增）
        pnl_service = get_pnl_service(db)
        follower_credential_id = settings.follower_credential_id if settings else None
        
        pnl_summary = {
            "unrealized_pnl": 0.0,
            "unrealized_pnl_percent": 0.0,
            "realized_pnl": 0.0,
            "realized_pnl_percent": 0.0,
            "total_pnl": 0.0,
            "total_pnl_percent": 0.0
        }
        
        if follower_credential_id:
            try:
                pnl_summary = await pnl_service.get_pnl_summary(
                    user_id=current_user.id,
                    credential_id=follower_credential_id
                )
            except Exception as e:
                logger.error(f"計算 PnL 失敗: {str(e)}")
        
        # 構建響應
        return DashboardSummary(
            user_id=current_user.id,
            username=current_user.username,
            is_active=is_active,
            follow_ratio=follow_ratio,
            master_user_id=master_user_id,
            total_position_value=total_position_value,
            my_positions=my_positions,
            master_latest_activity=master_latest_activity,
            master_positions=master_positions_list,
            engine_status=engine_status,
            recent_successful_trades=recent_successful_trades,
            has_unresolved_errors=len(unresolved_errors) > 0,
            unresolved_error_count=len(unresolved_errors),
            unrealized_pnl=pnl_summary["unrealized_pnl"],
            unrealized_pnl_percent=pnl_summary["unrealized_pnl_percent"],
            realized_pnl=pnl_summary["realized_pnl"],
            realized_pnl_percent=pnl_summary["realized_pnl_percent"],
            total_pnl=pnl_summary["total_pnl"],
            total_pnl_percent=pnl_summary["total_pnl_percent"]
        )
        
    except Exception as e:
        logger.error(f"獲取儀表板摘要失敗: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取儀表板摘要失敗"
        )
