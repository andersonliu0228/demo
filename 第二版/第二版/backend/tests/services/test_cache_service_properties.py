"""
Cache Service 屬性測試
"""
import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.services.cache_service import CacheService


@pytest.fixture
def cache_service():
    """創建 CacheService 實例（不連接真實 Redis）"""
    service = CacheService("redis://localhost:6379/0")
    service._is_available = True
    return service


@pytest.fixture
def mock_redis():
    """創建 Mock Redis 客戶端"""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.sadd = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    return redis_mock


@pytest.mark.asyncio
@given(
    user_id=st.integers(min_value=1, max_value=10000),
    credentials=st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=1),
            "exchange_name": st.sampled_from(["binance", "okx", "bybit"]),
            "api_key_masked": st.text(min_size=8, max_size=20)
        }),
        min_size=0,
        max_size=10
    )
)
async def test_property_18_cache_invalidation(
    cache_service, mock_redis, user_id, credentials
):
    """
    Feature: ea-trading-backend, Property 18: 快取失效機制
    
    對於任何憑證的更新或刪除操作，完成後相關的 Redis 快取應該被清除或失效，
    下次查詢時應該從資料庫重新載入最新資料。
    
    驗證需求：7.2
    """
    cache_service._redis = mock_redis
    
    # 設定快取
    await cache_service.set_user_credentials_cache(user_id, credentials)
    
    # 驗證快取已設定
    assert mock_redis.setex.called
    
    # 清除快取
    result = await cache_service.invalidate_user_credentials_cache(user_id)
    
    # 驗證快取已清除
    assert result is True
    assert mock_redis.delete.called


@pytest.mark.asyncio
@given(
    user_id=st.integers(min_value=1, max_value=10000)
)
async def test_property_19_redis_fallback(cache_service, user_id):
    """
    Feature: ea-trading-backend, Property 19: Redis 降級處理
    
    對於任何查詢操作，當 Redis 連接失敗或不可用時，系統應該自動降級到
    直接從資料庫讀取，並且仍能正確返回資料。
    
    驗證需求：7.4
    """
    # 模擬 Redis 不可用
    cache_service._is_available = False
    cache_service._redis = None
    
    # 嘗試獲取快取（應該返回 None 而不是拋出異常）
    result = await cache_service.get_user_credentials_cache(user_id)
    
    # 驗證降級處理：返回 None，不拋出異常
    assert result is None
    
    # 嘗試設定快取（應該返回 False 而不是拋出異常）
    set_result = await cache_service.set_user_credentials_cache(user_id, [])
    
    # 驗證降級處理：返回 False，不拋出異常
    assert set_result is False


@pytest.mark.asyncio
async def test_redis_connection_failure_graceful_degradation(cache_service):
    """
    測試 Redis 連接失敗時的優雅降級
    
    驗證需求：7.4
    """
    # 模擬連接失敗
    with patch('redis.asyncio.from_url', side_effect=Exception("Connection failed")):
        await cache_service.connect()
    
    # 驗證服務標記為不可用
    assert cache_service._is_available is False
    assert cache_service._redis is None
    
    # 驗證操作不會拋出異常
    result = await cache_service.get_user_credentials_cache(1)
    assert result is None


@pytest.mark.asyncio
@given(
    credential_id=st.integers(min_value=1, max_value=10000),
    credential_data=st.fixed_dictionaries({
        "id": st.integers(min_value=1),
        "user_id": st.integers(min_value=1),
        "exchange_name": st.sampled_from(["binance", "okx", "bybit"]),
        "api_key_masked": st.text(min_size=8, max_size=20)
    })
)
async def test_cache_set_and_invalidate_consistency(
    cache_service, mock_redis, credential_id, credential_data
):
    """
    測試快取設定和清除的一致性
    
    驗證需求：7.2
    """
    cache_service._redis = mock_redis
    
    # 設定快取
    set_result = await cache_service.set_credential_cache(
        credential_id, credential_data
    )
    assert set_result is True
    
    # 清除快取
    invalidate_result = await cache_service.invalidate_credential_cache(credential_id)
    assert invalidate_result is True
    
    # 驗證 Redis 操作被調用
    assert mock_redis.setex.called
    assert mock_redis.delete.called
