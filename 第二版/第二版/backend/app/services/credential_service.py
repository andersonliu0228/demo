"""
Credential Service
API 憑證業務邏輯層
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime

from backend.app.repositories.credential_repository import CredentialRepository
from backend.app.services.crypto_service import CryptoService
from backend.app.services.exchange_service import ExchangeService
from backend.app.services.cache_service import CacheService
from backend.app.models.api_credential import ApiCredential

logger = logging.getLogger(__name__)


class CredentialService:
    """
    API 憑證業務邏輯服務
    協調加密、驗證、快取和資料存取
    """
    
    def __init__(
        self,
        credential_repo: CredentialRepository,
        crypto_service: CryptoService,
        exchange_service: ExchangeService,
        cache_service: CacheService
    ):
        """
        初始化 Credential Service
        
        Args:
            credential_repo: 憑證資料存取層
            crypto_service: 加密服務
            exchange_service: 交易所服務
            cache_service: 快取服務
        """
        self.credential_repo = credential_repo
        self.crypto_service = crypto_service
        self.exchange_service = exchange_service
        self.cache_service = cache_service
    
    async def create_credential(
        self,
        user_id: int,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        verify: bool = True
    ) -> ApiCredential:
        """
        創建新的 API 憑證
        
        Args:
            user_id: 用戶 ID
            exchange_name: 交易所名稱
            api_key: API Key
            api_secret: API Secret
            passphrase: API Passphrase（可選）
            verify: 是否在創建前驗證憑證
            
        Returns:
            創建的 ApiCredential 物件
            
        Raises:
            ValueError: 憑證驗證失敗或已存在
        """
        # 驗證憑證（如果需要）
        if verify:
            verification_result = await self.exchange_service.verify_credentials(
                exchange_name, api_key, api_secret, passphrase
            )
            
            if not verification_result['is_valid']:
                raise ValueError(
                    f"憑證驗證失敗：{verification_result['error_message']}"
                )
            
            if not verification_result['has_trading_permission']:
                logger.warning(
                    f"用戶 {user_id} 的憑證沒有交易權限（{exchange_name}）"
                )
        
        # 加密 API Secret
        encrypted_secret = self.crypto_service.encrypt(api_secret)
        
        # 加密 Passphrase（如果有）
        encrypted_passphrase = None
        if passphrase:
            encrypted_passphrase = self.crypto_service.encrypt(passphrase)
        
        # 創建憑證
        credential = await self.credential_repo.create_credential(
            user_id=user_id,
            exchange_name=exchange_name,
            api_key=api_key,
            encrypted_api_secret=encrypted_secret,
            encrypted_passphrase=encrypted_passphrase
        )
        
        # 清除用戶憑證列表快取
        await self.cache_service.invalidate_user_credentials_cache(user_id)
        
        logger.info(
            f"用戶 {user_id} 成功創建憑證（交易所：{exchange_name}，ID：{credential.id}）"
        )
        
        return credential
    
    async def get_user_credentials(
        self,
        user_id: int,
        include_inactive: bool = False
    ) -> List[ApiCredential]:
        """
        獲取用戶的所有憑證（使用快取）
        
        Args:
            user_id: 用戶 ID
            include_inactive: 是否包含已停用的憑證
            
        Returns:
            憑證列表
        """
        # 嘗試從快取獲取
        if not include_inactive:
            cached_data = await self.cache_service.get_user_credentials_cache(user_id)
            if cached_data is not None:
                logger.debug(f"從快取獲取用戶 {user_id} 的憑證列表")
                # 這裡需要將字典轉換回 ApiCredential 物件
                # 為簡化，直接從資料庫查詢
        
        # 從資料庫查詢
        is_active = None if include_inactive else True
        credentials = await self.credential_repo.get_user_credentials(
            user_id, is_active=is_active
        )
        
        # 更新快取
        if not include_inactive and credentials:
            credentials_data = [cred.to_dict() for cred in credentials]
            await self.cache_service.set_user_credentials_cache(
                user_id, credentials_data
            )
        
        return credentials
    
    async def get_credential_by_id(
        self,
        credential_id: int,
        user_id: int
    ) -> Optional[ApiCredential]:
        """
        獲取特定憑證
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID（用於權限檢查）
            
        Returns:
            憑證物件，如果不存在則返回 None
        """
        return await self.credential_repo.get_credential_by_id(
            credential_id, user_id
        )
    
    async def update_credential(
        self,
        credential_id: int,
        user_id: int,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        verify: bool = True
    ) -> Optional[ApiCredential]:
        """
        更新現有憑證（重新驗證）
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID
            api_key: 新的 API Key（可選）
            api_secret: 新的 API Secret（可選）
            passphrase: 新的 Passphrase（可選）
            verify: 是否重新驗證憑證
            
        Returns:
            更新後的憑證物件，如果不存在則返回 None
            
        Raises:
            ValueError: 憑證驗證失敗
        """
        # 獲取現有憑證
        credential = await self.credential_repo.get_credential_by_id(
            credential_id, user_id
        )
        if not credential:
            return None
        
        # 準備更新資料
        update_data = {}
        
        # 如果提供了新的 API Key
        if api_key is not None:
            update_data['api_key'] = api_key
        else:
            api_key = credential.api_key
        
        # 如果提供了新的 API Secret
        if api_secret is not None:
            # 驗證新憑證（如果需要）
            if verify:
                verification_result = await self.exchange_service.verify_credentials(
                    credential.exchange_name,
                    api_key,
                    api_secret,
                    passphrase or (
                        self.crypto_service.decrypt(credential.encrypted_passphrase)
                        if credential.encrypted_passphrase else None
                    )
                )
                
                if not verification_result['is_valid']:
                    raise ValueError(
                        f"憑證驗證失敗：{verification_result['error_message']}"
                    )
            
            # 加密新的 Secret
            update_data['encrypted_api_secret'] = self.crypto_service.encrypt(api_secret)
        
        # 如果提供了新的 Passphrase
        if passphrase is not None:
            update_data['encrypted_passphrase'] = self.crypto_service.encrypt(passphrase)
        
        # 更新憑證
        updated_credential = await self.credential_repo.update_credential(
            credential_id, user_id, **update_data
        )
        
        # 清除快取
        await self.cache_service.invalidate_user_credentials_cache(user_id)
        await self.cache_service.invalidate_credential_cache(credential_id)
        
        logger.info(f"用戶 {user_id} 更新憑證 {credential_id}")
        
        return updated_credential
    
    async def delete_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> bool:
        """
        刪除憑證（清除快取）
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID
            
        Returns:
            是否成功刪除
        """
        result = await self.credential_repo.delete_credential(
            credential_id, user_id
        )
        
        if result:
            # 清除快取
            await self.cache_service.invalidate_user_credentials_cache(user_id)
            await self.cache_service.invalidate_credential_cache(credential_id)
            
            logger.info(f"用戶 {user_id} 刪除憑證 {credential_id}")
        
        return result
    
    async def get_decrypted_credential(
        self,
        credential_id: int,
        user_id: int
    ) -> Optional[Dict[str, str]]:
        """
        獲取解密後的憑證（用於實際交易）
        
        Args:
            credential_id: 憑證 ID
            user_id: 用戶 ID
            
        Returns:
            包含 api_key, api_secret, passphrase 的字典
        """
        credential = await self.credential_repo.get_credential_by_id(
            credential_id, user_id
        )
        if not credential:
            return None
        
        # 解密 Secret
        api_secret = self.crypto_service.decrypt(credential.encrypted_api_secret)
        
        # 解密 Passphrase（如果有）
        passphrase = None
        if credential.encrypted_passphrase:
            passphrase = self.crypto_service.decrypt(credential.encrypted_passphrase)
        
        return {
            'exchange_name': credential.exchange_name,
            'api_key': credential.api_key,
            'api_secret': api_secret,
            'passphrase': passphrase
        }
    
    def mask_api_key(self, api_key: str, show_chars: int = 4) -> str:
        """
        遮蔽 API Key，只顯示前後幾位
        
        Args:
            api_key: API Key
            show_chars: 顯示的字元數
            
        Returns:
            遮蔽後的 API Key
        """
        if not api_key or len(api_key) <= show_chars * 2:
            return "****"
        
        return f"{api_key[:show_chars]}...{api_key[-show_chars:]}"
