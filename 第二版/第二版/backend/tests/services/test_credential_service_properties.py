"""
Credential Service 屬性測試
使用 Hypothesis 進行基於屬性的測試
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, assume
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.services.credential_service import CredentialService
from backend.app.services.crypto_service import CryptoService
from backend.app.services.exchange_service import ExchangeService
from backend.app.services.cache_service import CacheService
from backend.app.repositories.credential_repository import CredentialRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.models.user import User
from backend.app.models.api_credential import ApiCredential, Base


# 測試資料庫設定
@pytest_asyncio.fixture
async def test_engine():
    """創建測試用的 SQLite 記憶體資料庫"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """創建測試資料庫會話 - 每次測試都創建新的會話"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        # 測試結束後回滾所有更改
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def test_user(db_session):
    """創建測試用戶"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_123"
    )
    await db_session.commit()
    return user


@pytest.fixture
def crypto_service():
    """創建測試用的加密服務"""
    test_key = CryptoService.generate_key()
    return CryptoService(test_key)


@pytest.fixture
def mock_exchange_service():
    """創建 Mock 的交易所服務"""
    service = MagicMock(spec=ExchangeService)
    # 預設驗證成功
    service.verify_credentials = AsyncMock(return_value={
        'is_valid': True,
        'has_trading_permission': True,
        'account_info': {'balance': 1000.0},
        'error_message': None
    })
    return service


@pytest.fixture
def mock_cache_service():
    """創建 Mock 的快取服務"""
    service = MagicMock(spec=CacheService)
    service.get_user_credentials_cache = AsyncMock(return_value=None)
    service.set_user_credentials_cache = AsyncMock(return_value=True)
    service.invalidate_user_credentials_cache = AsyncMock(return_value=True)
    service.invalidate_credential_cache = AsyncMock(return_value=True)
    return service


@pytest.fixture
async def credential_service(
    db_session,
    crypto_service,
    mock_exchange_service,
    mock_cache_service
):
    """創建 Credential Service"""
    credential_repo = CredentialRepository(db_session)
    return CredentialService(
        credential_repo=credential_repo,
        crypto_service=crypto_service,
        exchange_service=mock_exchange_service,
        cache_service=mock_cache_service
    )


# Hypothesis 策略定義
exchange_strategy = st.sampled_from([
    "binance", "okx", "bybit", "huobi", "kucoin", "gate", "bitget", "mexc"
])

api_key_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=16,
    max_size=64
)

api_secret_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=16,
    max_size=128
)

passphrase_strategy = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(min_codepoint=33, max_codepoint=126),
        min_size=8,
        max_size=32
    )
)


# ============================================================================
# 屬性 2：資料庫中不存儲明文 Secret
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    api_key=api_key_strategy,
    api_secret=api_secret_strategy,
    passphrase=passphrase_strategy
)
async def test_property_2_database_stores_encrypted_secret(
    credential_service,
    test_user,
    db_session,
    exchange,
    api_key,
    api_secret,
    passphrase
):
    """
    Feature: ea-trading-backend, Property 2: 資料庫中不存儲明文 Secret
    
    對於任何存儲在資料庫中的 ApiCredential 記錄，
    encrypted_api_secret 欄位的值應該與原始 API Secret 明文不同，
    且無法直接讀取為有意義的明文。
    
    **驗證需求：2.2, 3.3**
    """
    # 創建憑證
    credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        verify=True
    )
    
    # 驗證：資料庫中的 encrypted_api_secret 不等於明文
    assert credential.encrypted_api_secret != api_secret
    
    # 驗證：加密後的值應該更長（包含加密元數據）
    assert len(credential.encrypted_api_secret) > len(api_secret)
    
    # 驗證：如果有 passphrase，也應該被加密
    if passphrase:
        assert credential.encrypted_passphrase is not None
        assert credential.encrypted_passphrase != passphrase
    
    # 驗證：可以解密回原始值
    decrypted = credential_service.crypto_service.decrypt(
        credential.encrypted_api_secret
    )
    assert decrypted == api_secret


# ============================================================================
# 屬性 7：API Key 明文存儲與查詢一致性
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    api_key=api_key_strategy,
    api_secret=api_secret_strategy
)
async def test_property_7_api_key_plaintext_consistency(
    credential_service,
    test_user,
    exchange,
    api_key,
    api_secret
):
    """
    Feature: ea-trading-backend, Property 7: API Key 明文存儲與查詢一致性
    
    對於任何創建的 ApiCredential，存儲後查詢得到的 api_key 欄位
    應該與創建時提供的原始 API Key 完全相同（明文存儲）。
    
    **驗證需求：3.2**
    """
    # 創建憑證
    created_credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=api_key,
        api_secret=api_secret,
        verify=True
    )
    
    # 查詢憑證
    retrieved_credential = await credential_service.get_credential_by_id(
        credential_id=created_credential.id,
        user_id=test_user.id
    )
    
    # 驗證：API Key 應該完全相同（明文存儲）
    assert retrieved_credential is not None
    assert retrieved_credential.api_key == api_key
    assert retrieved_credential.api_key == created_credential.api_key


# ============================================================================
# 屬性 12：有效憑證驗證成功並存儲
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    api_key=api_key_strategy,
    api_secret=api_secret_strategy
)
async def test_property_12_valid_credential_verified_and_stored(
    credential_service,
    test_user,
    mock_exchange_service,
    exchange,
    api_key,
    api_secret
):
    """
    Feature: ea-trading-backend, Property 12: 有效憑證驗證成功並存儲
    
    對於任何有效的 API 憑證，當驗證成功後進行綁定操作，
    系統應該將憑證存儲到資料庫，並且後續可以查詢到該憑證。
    
    **驗證需求：4.6**
    """
    # 確保驗證返回成功
    mock_exchange_service.verify_credentials.return_value = {
        'is_valid': True,
        'has_trading_permission': True,
        'account_info': {'balance': 1000.0},
        'error_message': None
    }
    
    # 創建憑證（會進行驗證）
    credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=api_key,
        api_secret=api_secret,
        verify=True
    )
    
    # 驗證：憑證已創建
    assert credential is not None
    assert credential.id is not None
    
    # 驗證：可以查詢到該憑證
    retrieved = await credential_service.get_credential_by_id(
        credential_id=credential.id,
        user_id=test_user.id
    )
    assert retrieved is not None
    assert retrieved.id == credential.id
    assert retrieved.exchange_name == exchange
    
    # 驗證：驗證方法被調用
    mock_exchange_service.verify_credentials.assert_called_once()


# ============================================================================
# 屬性 13：API Key 遮蔽顯示
# ============================================================================

@pytest.mark.asyncio
@given(
    api_key=st.text(
        alphabet=st.characters(min_codepoint=33, max_codepoint=126),
        min_size=16,
        max_size=64
    )
)
async def test_property_13_api_key_masking(credential_service, api_key):
    """
    Feature: ea-trading-backend, Property 13: API Key 遮蔽顯示
    
    對於任何查詢憑證的操作，返回的 api_key_masked 欄位應該只顯示
    API Key 的前 4 位和後 4 位字元，中間部分用星號或其他字元遮蔽。
    
    **驗證需求：5.1**
    """
    # 遮蔽 API Key
    masked = credential_service.mask_api_key(api_key, show_chars=4)
    
    # 驗證：遮蔽後的格式正確
    if len(api_key) > 8:
        assert masked.startswith(api_key[:4])
        assert masked.endswith(api_key[-4:])
        assert "..." in masked
        # 驗證：中間部分被遮蔽
        assert len(masked) < len(api_key)
    else:
        # 短 API Key 完全遮蔽
        assert masked == "****"


# ============================================================================
# 屬性 14：刪除憑證後無法查詢
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    api_key=api_key_strategy,
    api_secret=api_secret_strategy
)
async def test_property_14_deleted_credential_not_queryable(
    credential_service,
    test_user,
    exchange,
    api_key,
    api_secret
):
    """
    Feature: ea-trading-backend, Property 14: 刪除憑證後無法查詢
    
    對於任何已刪除的 ApiCredential，刪除操作完成後，
    嘗試查詢該憑證應該返回「不存在」錯誤或空結果。
    
    **驗證需求：5.3**
    """
    # 創建憑證
    credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=api_key,
        api_secret=api_secret,
        verify=True
    )
    
    credential_id = credential.id
    
    # 驗證：創建後可以查詢
    retrieved = await credential_service.get_credential_by_id(
        credential_id=credential_id,
        user_id=test_user.id
    )
    assert retrieved is not None
    
    # 刪除憑證
    deleted = await credential_service.delete_credential(
        credential_id=credential_id,
        user_id=test_user.id
    )
    assert deleted is True
    
    # 驗證：刪除後無法查詢
    retrieved_after_delete = await credential_service.get_credential_by_id(
        credential_id=credential_id,
        user_id=test_user.id
    )
    assert retrieved_after_delete is None


# ============================================================================
# 屬性 15：更新憑證值正確保存
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    original_api_key=api_key_strategy,
    original_api_secret=api_secret_strategy,
    new_api_key=api_key_strategy,
    new_api_secret=api_secret_strategy
)
async def test_property_15_update_credential_saves_correctly(
    credential_service,
    test_user,
    exchange,
    original_api_key,
    original_api_secret,
    new_api_key,
    new_api_secret
):
    """
    Feature: ea-trading-backend, Property 15: 更新憑證值正確保存
    
    對於任何已存在的 ApiCredential，當更新其 API Key 或 Secret 時，
    更新後查詢得到的值應該與更新時提供的新值一致。
    
    **驗證需求：5.4**
    """
    # 確保新舊值不同
    assume(original_api_key != new_api_key or original_api_secret != new_api_secret)
    
    # 創建原始憑證
    credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=original_api_key,
        api_secret=original_api_secret,
        verify=True
    )
    
    credential_id = credential.id
    
    # 更新憑證
    updated = await credential_service.update_credential(
        credential_id=credential_id,
        user_id=test_user.id,
        api_key=new_api_key,
        api_secret=new_api_secret,
        verify=True
    )
    
    # 驗證：更新成功
    assert updated is not None
    assert updated.api_key == new_api_key
    
    # 查詢更新後的憑證
    retrieved = await credential_service.get_credential_by_id(
        credential_id=credential_id,
        user_id=test_user.id
    )
    
    # 驗證：查詢到的值與更新的值一致
    assert retrieved is not None
    assert retrieved.api_key == new_api_key
    
    # 驗證：解密後的 Secret 與新值一致
    decrypted_secret = credential_service.crypto_service.decrypt(
        retrieved.encrypted_api_secret
    )
    assert decrypted_secret == new_api_secret


# ============================================================================
# 屬性 16：更新時重新驗證憑證
# ============================================================================

@pytest.mark.asyncio
@given(
    exchange=exchange_strategy,
    original_api_key=api_key_strategy,
    original_api_secret=api_secret_strategy,
    invalid_api_secret=api_secret_strategy
)
async def test_property_16_update_revalidates_credential(
    credential_service,
    test_user,
    mock_exchange_service,
    exchange,
    original_api_key,
    original_api_secret,
    invalid_api_secret
):
    """
    Feature: ea-trading-backend, Property 16: 更新時重新驗證憑證
    
    對於任何憑證更新操作，如果提供的新憑證無效，
    系統應該拒絕更新並保持原有憑證不變。
    
    **驗證需求：5.5**
    """
    # 確保新舊值不同
    assume(original_api_secret != invalid_api_secret)
    
    # 創建原始憑證（驗證成功）
    mock_exchange_service.verify_credentials.return_value = {
        'is_valid': True,
        'has_trading_permission': True,
        'account_info': {},
        'error_message': None
    }
    
    credential = await credential_service.create_credential(
        user_id=test_user.id,
        exchange_name=exchange,
        api_key=original_api_key,
        api_secret=original_api_secret,
        verify=True
    )
    
    credential_id = credential.id
    original_encrypted_secret = credential.encrypted_api_secret
    
    # 設定驗證失敗
    mock_exchange_service.verify_credentials.return_value = {
        'is_valid': False,
        'has_trading_permission': False,
        'account_info': None,
        'error_message': 'Invalid API credentials'
    }
    
    # 嘗試更新為無效憑證
    with pytest.raises(ValueError, match="憑證驗證失敗"):
        await credential_service.update_credential(
            credential_id=credential_id,
            user_id=test_user.id,
            api_secret=invalid_api_secret,
            verify=True
        )
    
    # 驗證：原有憑證保持不變
    retrieved = await credential_service.get_credential_by_id(
        credential_id=credential_id,
        user_id=test_user.id
    )
    
    assert retrieved is not None
    assert retrieved.api_key == original_api_key
    assert retrieved.encrypted_api_secret == original_encrypted_secret
    
    # 驗證：解密後仍是原始 Secret
    decrypted = credential_service.crypto_service.decrypt(
        retrieved.encrypted_api_secret
    )
    assert decrypted == original_api_secret
