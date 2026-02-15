"""
User Repository
用戶資料存取層
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.app.models.user import User


class UserRepository:
    """用戶資料存取層"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化 Repository
        
        Args:
            db: 資料庫會話
        """
        self.db = db
    
    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        is_active: bool = True,
        role: Optional[str] = None
    ) -> User:
        """
        創建新用戶
        
        Args:
            username: 用戶名稱
            email: 電子郵件
            hashed_password: 雜湊密碼
            is_active: 是否啟用
            role: 用戶角色 (master/follower)
            
        Returns:
            創建的用戶物件
            
        Raises:
            IntegrityError: 如果用戶名或電子郵件已存在
        """
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            role=role
        )
        
        try:
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except IntegrityError as e:
            await self.db.rollback()
            if "username" in str(e.orig):
                raise ValueError(f"用戶名 '{username}' 已存在")
            elif "email" in str(e.orig):
                raise ValueError(f"電子郵件 '{email}' 已存在")
            else:
                raise ValueError("創建用戶失敗：唯一性約束違反")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根據 ID 獲取用戶
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            用戶物件，如果不存在則返回 None
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根據電子郵件獲取用戶
        
        Args:
            email: 電子郵件
            
        Returns:
            用戶物件，如果不存在則返回 None
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根據用戶名獲取用戶
        
        Args:
            username: 用戶名
            
        Returns:
            用戶物件，如果不存在則返回 None
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """
        更新用戶資訊
        
        Args:
            user_id: 用戶 ID
            **kwargs: 要更新的欄位
            
        Returns:
            更新後的用戶物件，如果不存在則返回 None
            
        Raises:
            IntegrityError: 如果更新違反唯一性約束
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError(f"更新用戶失敗：{str(e.orig)}")
    
    async def delete_user(self, user_id: int) -> bool:
        """
        刪除用戶
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            是否成功刪除
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.flush()
        return True
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> list[User]:
        """
        列出用戶
        
        Args:
            skip: 跳過的記錄數
            limit: 返回的最大記錄數
            is_active: 過濾條件：是否啟用
            
        Returns:
            用戶列表
        """
        stmt = select(User)
        
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
