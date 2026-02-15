"""
Trade Error Repository
交易錯誤資料存取層
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.trade_error import TradeError


class TradeErrorRepository:
    """交易錯誤資料存取層"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        error_type: str,
        error_message: str,
        trade_log_id: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> TradeError:
        """創建交易錯誤記錄"""
        error = TradeError(
            user_id=user_id,
            trade_log_id=trade_log_id,
            error_type=error_type,
            error_message=error_message,
            error_details=error_details
        )
        self.db.add(error)
        await self.db.flush()
        await self.db.refresh(error)
        return error
    
    async def get_by_id(self, error_id: int) -> Optional[TradeError]:
        """根據 ID 獲取錯誤"""
        stmt = select(TradeError).where(TradeError.id == error_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_unresolved_by_user(self, user_id: int) -> List[TradeError]:
        """獲取用戶未解決的錯誤"""
        stmt = select(TradeError).where(
            TradeError.user_id == user_id,
            TradeError.is_resolved == False
        ).order_by(TradeError.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def has_unresolved_errors(self, user_id: int) -> bool:
        """檢查用戶是否有未解決的錯誤"""
        errors = await self.get_unresolved_by_user(user_id)
        return len(errors) > 0
    
    async def resolve(
        self,
        error_id: int,
        resolved_by: int
    ) -> Optional[TradeError]:
        """解決錯誤"""
        error = await self.get_by_id(error_id)
        if not error:
            return None
        
        error.is_resolved = True
        error.resolved_at = datetime.utcnow()
        error.resolved_by = resolved_by
        
        await self.db.flush()
        await self.db.refresh(error)
        return error
    
    async def get_recent_errors(
        self,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[TradeError]:
        """獲取最近的錯誤"""
        stmt = select(TradeError).order_by(TradeError.created_at.desc()).limit(limit)
        
        if user_id is not None:
            stmt = stmt.where(TradeError.user_id == user_id)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
