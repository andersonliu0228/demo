"""
Credential Repository
API 憑證資料存取層
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from backend.app.models.api_credential import ApiCredential


class CredentialRepository:
    """API 憑證資料存取層"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化 Repository
        
        Args:
            db: 資料庫會話
        """
        self.db = db
    
    async def create_credential(
        self,
        user_id: int,
        exchange_name: str,
        api_key: str,
        encrypted_api_secret: str,
        encrypted_passphrase: Optional[str] = None,
        is_active: bool = True
    ) -> ApiCredential:
        """
        創建新的 API 憑證
        
        Args:
            user_id: 用戶 ID
            exchange_name: 交易所名稱
            api_key: API Key（明文）
            encrypted_api_secret: 加密的 API Secret
            encrypted_passphrase: 加密的 Passphrase（可選）
            is_active: 是否啟用
            
        Returns:
            創建的憑證物件
            
        Raises:
            ValueError: 如果憑證已存在（唯一性約束違反）
        """
        credential = ApiCredential(
            user_id=user_id,
            exchange_name=exchange_name,
            api_key=api_key,
            encrypted_api_secret=encrypted_api_secret,
            encrypted_passphrase=encrypted_passphrase,
            is_active=is_active,
            last_verified_at=datetime.utcnow()
        )
        
        try:
            self.db.add(credential)
            await self.db.flush()
            await self.db.refresh(credential)
            return credential
        except IntegrityError as e:
            await self.db.rollback()
            if "uq_user_exchange_key" in str(e.orig):
                raise ValueError(
                    f"用戶已在交易所 '{exchange_name}' 綁定了相同的 API Key"
                )
            else:
                raise ValueError(f"創建憑證失敗：{str(e.orig)}")
    
    async def get_credential_by_id(
        self,
        credential_id: int,
        user_id: Optional[int] = None
    ) -> Optional[ApiCredential]:
        """
        根據 ID 獲取憑證
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（可選，用於權限檢查）
            
        Returns:
            憑證物件，如果不存在則返回 None
        """
        stmt = select(ApiCredential).where(ApiCredential.id == credential_id)
        
        if user_id is not None:
            stmt = stmt.where(ApiCredential.user_id == user_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_credentials(
        self,
        user_id: int,
        exchange_name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> list[ApiCredential]:
        """
        獲取用戶的所有憑證
        
        Args:
            user_id: 用戶 ID
            exchange_name: 過濾條件：交易所名稱（可選）
            is_active: 過濾條件：是否啟用（可選）
            
        Returns:
            憑證列表
        """
        stmt = select(ApiCredential).where(ApiCredential.user_id == user_id)
        
        if exchange_name is not None:
            stmt = stmt.where(ApiCredential.exchange_name == exchange_name)
        
        if is_active is not None:
            stmt = stmt.where(ApiCredential.is_active == is_active)
        
        stmt = stmt.order_by(ApiCredential.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_credential_by_exchange_and_key(
        self,
        user_id: int,
        exchange_name: str,
        api_key: str
    ) -> Optional[ApiCredential]:
        """
        根據交易所和 API Key 獲取憑證
        
        Args:
            user_id: 用戶 ID
            exchange_name: 交易所名稱
            api_key: API Key
            
        Returns:
            憑證物件，如果不存在則返回 None
        """
        stmt = select(ApiCredential).where(
            and_(
                ApiCredential.user_id == user_id,
                ApiCredential.exchange_name == exchange_name,
                ApiCredential.api_key == api_key
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_credential(
        self,
        credential_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[ApiCredential]:
        """
        更新憑證
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（用於權限檢查）
            **kwargs: 要更新的欄位
            
        Returns:
            更新後的憑證物件，如果不存在則返回 None
            
        Raises:
            ValueError: 如果更新違反唯一性約束
        """
        credential = await self.get_credential_by_id(credential_id, user_id)
        if not credential:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(credential, key):
                    setattr(credential, key, value)
            
            # 更新最後驗證時間
            if any(k in kwargs for k in ['api_key', 'encrypted_api_secret', 'encrypted_passphrase']):
                credential.last_verified_at = datetime.utcnow()
            
            await self.db.flush()
            await self.db.refresh(credential)
            return credential
        except IntegrityError as e:
            await self.db.rollback()
            if "uq_user_exchange_key" in str(e.orig):
                raise ValueError("此 API Key 已經綁定到該交易所")
            else:
                raise ValueError(f"更新憑證失敗：{str(e.orig)}")
    
    async def delete_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> bool:
        """
        刪除憑證
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（用於權限檢查）
            
        Returns:
            是否成功刪除
        """
        credential = await self.get_credential_by_id(credential_id, user_id)
        if not credential:
            return False
        
        await self.db.delete(credential)
        await self.db.flush()
        return True
    
    async def update_last_verified_at(
        self,
        credential_id: int,
        verified_at: Optional[datetime] = None
    ) -> bool:
        """
        更新最後驗證時間
        
        Args:
            credential_id: 憑證 ID
            verified_at: 驗證時間（默認為當前時間）
            
        Returns:
            是否成功更新
        """
        credential = await self.get_credential_by_id(credential_id)
        if not credential:
            return False
        
        credential.last_verified_at = verified_at or datetime.utcnow()
        await self.db.flush()
        return True
    
    async def deactivate_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> bool:
        """
        停用憑證（軟刪除）
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（用於權限檢查）
            
        Returns:
            是否成功停用
        """
        credential = await self.get_credential_by_id(credential_id, user_id)
        if not credential:
            return False
        
        credential.is_active = False
        await self.db.flush()
        return True
    
    async def activate_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> bool:
        """
        啟用憑證
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（用於權限檢查）
            
        Returns:
            是否成功啟用
        """
        credential = await self.get_credential_by_id(credential_id, user_id)
        if not credential:
            return False
        
        credential.is_active = True
        await self.db.flush()
        return True
