"""
Follower Position Repository
跟隨者倉位資料存取層
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.follower_position import FollowerPosition


class FollowerPositionRepository:
    """跟隨者倉位資料存取層"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_position(
        self,
        user_id: int,
        credential_id: int,
        symbol: str
    ) -> Optional[FollowerPosition]:
        """獲取用戶的特定交易對倉位"""
        stmt = select(FollowerPosition).where(
            and_(
                FollowerPosition.user_id == user_id,
                FollowerPosition.credential_id == credential_id,
                FollowerPosition.symbol == symbol
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_positions(self, user_id: int) -> List[FollowerPosition]:
        """獲取用戶的所有倉位"""
        stmt = select(FollowerPosition).where(FollowerPosition.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update_position(
        self,
        user_id: int,
        credential_id: int,
        symbol: str,
        position_size: float,
        entry_price: Optional[float] = None
    ) -> FollowerPosition:
        """更新或創建倉位"""
        position = await self.get_position(user_id, credential_id, symbol)
        
        if position:
            # 更新現有倉位
            position.position_size = position_size
            if entry_price is not None:
                position.entry_price = entry_price
        else:
            # 創建新倉位
            position = FollowerPosition(
                user_id=user_id,
                credential_id=credential_id,
                symbol=symbol,
                position_size=position_size,
                entry_price=entry_price
            )
            self.db.add(position)
        
        await self.db.flush()
        await self.db.refresh(position)
        return position
    
    async def delete_position(
        self,
        user_id: int,
        credential_id: int,
        symbol: str
    ) -> bool:
        """刪除倉位"""
        position = await self.get_position(user_id, credential_id, symbol)
        if not position:
            return False
        
        await self.db.delete(position)
        await self.db.flush()
        return True
