"""
Cache Service
Redis 快取服務
"""
import json
import logging
from typing import Optional, List, Any
from redis import asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis 快取服務
    
    提供快取管理功能，包含降級處理
    """
    
    # 快取 TTL（秒）
    CREDENTIAL_LIST_TTL = 300  # 5 分鐘
    CREDENTIAL_DETAIL_TTL = 300  # 5 分鐘
    EXCHANGE_LIST_TTL = 3600  # 1 小時
    
    def __init__(self, redis_url: str):
        """
        初始化快取服務
        
        Args:
            redis_url: Redis 連接 URL
        """
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._is_available = True
    
    async def connect(self):
        """建立 Redis 連接"""
        try:
            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 測試連接
            await self._redis.ping()
            self._is_available = True
            logger.info("Redis 連接成功")
        except (RedisError, ConnectionError) as e:
            logger.warning(f"Redis 連接失敗，將使用降級模式: {str(e)}")
            self._is_available = False
            self._redis = None
    
    async def close(self):
        """關閉 Redis 連接"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis 連接已關閉")
    
    async def _execute_with_fallback(self, operation, *args, **kwargs):
        """
        執行 Redis 操作，失敗時降級
        
        Args:
            operation: Redis 操作函數
            *args, **kwargs: 操作參數
            
        Returns:
            操作結果，失敗時返回 None
        """
        if not self._is_available or not self._redis:
            return None
        
        try:
            return await operation(*args, **kwargs)
        except (RedisError, ConnectionError) as e:
            logger.warning(f"Redis 操作失敗，降級處理: {str(e)}")
            self._is_available = False
            return None
    
    # ==================== 用戶憑證列表快取 ====================
    
    def _get_user_credentials_key(self, user_id: int) -> str:
        """獲取用戶憑證列表的快取鍵"""
        return f"user:{user_id}:credentials"
    
    async def get_user_credentials_cache(
        self,
        user_id: int
    ) -> Optional[List[dict]]:
        """
        獲取用戶憑證列表快取
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            憑證列表（字典格式），如果快取不存在或失敗則返回 None
        """
        key = self._get_user_credentials_key(user_id)
        
        async def _get():
            if not self._redis:
                return None
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        
        return await self._execute_with_fallback(_get)
    
    async def set_user_credentials_cache(
        self,
        user_id: int,
        credentials: List[dict],
        ttl: Optional[int] = None
    ) -> bool:
        """
        設定用戶憑證列表快取
        
        Args:
            user_id: 用戶 ID
            credentials: 憑證列表
            ttl: 過期時間（秒），默認使用 CREDENTIAL_LIST_TTL
            
        Returns:
            是否成功設定
        """
        key = self._get_user_credentials_key(user_id)
        ttl = ttl or self.CREDENTIAL_LIST_TTL
        
        async def _set():
            if not self._redis:
                return False
            data = json.dumps(credentials, ensure_ascii=False)
            await self._redis.setex(key, ttl, data)
            return True
        
        result = await self._execute_with_fallback(_set)
        return result if result is not None else False
    
    async def invalidate_user_credentials_cache(self, user_id: int) -> bool:
        """
        清除用戶憑證列表快取
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            是否成功清除
        """
        key = self._get_user_credentials_key(user_id)
        
        async def _delete():
            if not self._redis:
                return False
            await self._redis.delete(key)
            return True
        
        result = await self._execute_with_fallback(_delete)
        return result if result is not None else False
    
    # ==================== 單個憑證快取 ====================
    
    def _get_credential_key(self, credential_id: int) -> str:
        """獲取單個憑證的快取鍵"""
        return f"credential:{credential_id}"
    
    async def get_credential_cache(
        self,
        credential_id: int
    ) -> Optional[dict]:
        """
        獲取單個憑證快取
        
        Args:
            credential_id: 憑證 ID
            
        Returns:
            憑證資訊（字典格式），如果快取不存在或失敗則返回 None
        """
        key = self._get_credential_key(credential_id)
        
        async def _get():
            if not self._redis:
                return None
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        
        return await self._execute_with_fallback(_get)
    
    async def set_credential_cache(
        self,
        credential_id: int,
        credential: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        設定單個憑證快取
        
        Args:
            credential_id: 憑證 ID
            credential: 憑證資訊
            ttl: 過期時間（秒），默認使用 CREDENTIAL_DETAIL_TTL
            
        Returns:
            是否成功設定
        """
        key = self._get_credential_key(credential_id)
        ttl = ttl or self.CREDENTIAL_DETAIL_TTL
        
        async def _set():
            if not self._redis:
                return False
            data = json.dumps(credential, ensure_ascii=False)
            await self._redis.setex(key, ttl, data)
            return True
        
        result = await self._execute_with_fallback(_set)
        return result if result is not None else False
    
    async def invalidate_credential_cache(self, credential_id: int) -> bool:
        """
        清除單個憑證快取
        
        Args:
            credential_id: 憑證 ID
            
        Returns:
            是否成功清除
        """
        key = self._get_credential_key(credential_id)
        
        async def _delete():
            if not self._redis:
                return False
            await self._redis.delete(key)
            return True
        
        result = await self._execute_with_fallback(_delete)
        return result if result is not None else False
    
    # ==================== 交易所列表快取 ====================
    
    def _get_exchanges_key(self) -> str:
        """獲取交易所列表的快取鍵"""
        return "exchanges:supported"
    
    async def get_exchanges_cache(self) -> Optional[List[str]]:
        """
        獲取支援的交易所列表快取
        
        Returns:
            交易所列表，如果快取不存在或失敗則返回 None
        """
        key = self._get_exchanges_key()
        
        async def _get():
            if not self._redis:
                return None
            members = await self._redis.smembers(key)
            return list(members) if members else None
        
        return await self._execute_with_fallback(_get)
    
    async def set_exchanges_cache(
        self,
        exchanges: List[str],
        ttl: Optional[int] = None
    ) -> bool:
        """
        設定支援的交易所列表快取
        
        Args:
            exchanges: 交易所列表
            ttl: 過期時間（秒），默認使用 EXCHANGE_LIST_TTL
            
        Returns:
            是否成功設定
        """
        key = self._get_exchanges_key()
        ttl = ttl or self.EXCHANGE_LIST_TTL
        
        async def _set():
            if not self._redis:
                return False
            # 先刪除舊的集合
            await self._redis.delete(key)
            # 添加新的成員
            if exchanges:
                await self._redis.sadd(key, *exchanges)
            # 設定過期時間
            await self._redis.expire(key, ttl)
            return True
        
        result = await self._execute_with_fallback(_set)
        return result if result is not None else False
    
    # ==================== 通用快取操作 ====================
    
    async def clear_all_cache(self) -> bool:
        """
        清除所有快取（謹慎使用）
        
        Returns:
            是否成功清除
        """
        async def _flush():
            if not self._redis:
                return False
            await self._redis.flushdb()
            return True
        
        result = await self._execute_with_fallback(_flush)
        logger.info("已清除所有快取")
        return result if result is not None else False
    
    async def get_cache_stats(self) -> Optional[dict]:
        """
        獲取快取統計資訊
        
        Returns:
            統計資訊字典
        """
        async def _stats():
            if not self._redis:
                return None
            info = await self._redis.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
            }
        
        result = await self._execute_with_fallback(_stats)
        if result is None:
            return {"connected": False}
        return result


# 全域實例
_cache_service_instance: Optional[CacheService] = None


async def get_cache_service(redis_url: str) -> CacheService:
    """
    獲取 CacheService 單例實例
    
    Args:
        redis_url: Redis 連接 URL
        
    Returns:
        CacheService 實例
    """
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService(redis_url)
        await _cache_service_instance.connect()
    return _cache_service_instance
