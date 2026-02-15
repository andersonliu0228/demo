"""
Follow Settings Repository
跟單設定資料存取層
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.follow_settings import FollowSettings


class FollowSettingsRepository:
    """跟單設定資料存取層"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        master_user_id: int,
        master_credential_id: int,
        follower_credential_id: int,
        follow_ratio: float = 0.1,
        is_active: bool = True
    ) -> FollowSettings:
        """創建跟單設定"""
        settings = FollowSettings(
            user_id=user_id,
            master_user_id=master_user_id,
            master_credential_id=master_credential_id,
            follower_credential_id=follower_credential_id,
            follow_ratio=follow_ratio,
            is_active=is_active
        )
        self.db.add(settings)
        await self.db.flush()
        await self.db.refresh(settings)
        return settings
    
    async def get_by_user_id(self, user_id: int) -> Optional[FollowSettings]:
        """根據用戶 ID 獲取跟單設定"""
        stmt = select(FollowSettings).where(FollowSettings.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_active(self) -> List[FollowSettings]:
        """獲取所有啟用的跟單設定"""
        stmt = select(FollowSettings).where(FollowSettings.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(
        self,
        user_id: int,
        follow_ratio: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> Optional[FollowSettings]:
        """更新跟單設定"""
        settings = await self.get_by_user_id(user_id)
        if not settings:
            return None
        
        if follow_ratio is not None:
            settings.follow_ratio = follow_ratio
        if is_active is not None:
            settings.is_active = is_active
        
        await self.db.flush()
        await self.db.refresh(settings)
        return settings
    
    async def delete(self, user_id: int) -> bool:
        """刪除跟單設定"""
        settings = await self.get_by_user_id(user_id)
        if not settings:
            return False
        
        await self.db.delete(settings)
        await self.db.flush()
        return True
