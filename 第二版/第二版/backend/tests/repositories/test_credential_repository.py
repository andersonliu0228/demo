"""
Credential Repository 單元測試
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.models.api_credential import ApiCredential
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.credential_repository import CredentialRepository


# 測試資料庫 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_engine():
    """創建測試引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """創建測試資料庫會話"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db_session):
    """創建測試用戶"""
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    await db_session.commit()
    return user


@pytest.fixture
def credential_repository(db_session):
    """創建 CredentialRepository 實例"""
    return CredentialRepository(db_session)


class TestCredentialRepositoryCreate:
    """測試憑證創建"""
    
    @pytest.mark.asyncio
    async def test_create_credential_success(
        self, credential_repository, test_user, db_session
    ):
        """測試成功創建憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_api_key",
            encrypted_api_secret="encrypted_secret"
        )
        await db_session.commit()
        
        assert credential.id is not None
        assert credential.user_id == test_user.id
        assert credential.exchange_name == "binance"
        assert credential.api_key == "test_api_key"
        assert credential.encrypted_api_secret == "encrypted_secret"
        assert credential.is_active is True
        assert credential.last_verified_at is not None
    
    @pytest.mark.asyncio
    async def test_create_credential_with_passphrase(
        self, credential_repository, test_user, db_session
    ):
        """測試創建帶 Passphrase 的憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="okx",
            api_key="test_key",
            encrypted_api_secret="encrypted_secret",
            encrypted_passphrase="encrypted_passphrase"
        )
        await db_session.commit()
        
        assert credential.encrypted_passphrase == "encrypted_passphrase"
    
    @pytest.mark.asyncio
    async def test_create_duplicate_credential_raises_error(
        self, credential_repository, test_user, db_session
    ):
        """
        Feature: ea-trading-backend, Property 10: 防止重複綁定相同憑證
        
        測試創建重複憑證會拋出錯誤
        """
        # 創建第一個憑證
        await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret1"
        )
        await db_session.commit()
        
        # 嘗試創建相同的憑證
        with pytest.raises(ValueError, match="已在交易所 'binance' 綁定了相同的 API Key"):
            await credential_repository.create_credential(
                user_id=test_user.id,
                exchange_name="binance",
                api_key="test_key",
                encrypted_api_secret="secret2"
            )


class TestCredentialRepositoryRead:
    """測試憑證查詢"""
    
    @pytest.mark.asyncio
    async def test_get_credential_by_id_success(
        self, credential_repository, test_user, db_session
    ):
        """測試根據 ID 獲取憑證"""
        created = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret"
        )
        await db_session.commit()
        
        credential = await credential_repository.get_credential_by_id(created.id)
        
        assert credential is not None
        assert credential.id == created.id
    
    @pytest.mark.asyncio
    async def test_get_credential_by_id_with_user_check(
        self, credential_repository, test_user, db_session
    ):
        """測試根據 ID 和用戶 ID 獲取憑證"""
        created = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret"
        )
        await db_session.commit()
        
        # 正確的用戶 ID
        credential = await credential_repository.get_credential_by_id(
            created.id, test_user.id
        )
        assert credential is not None
        
        # 錯誤的用戶 ID
        credential = await credential_repository.get_credential_by_id(
            created.id, 99999
        )
        assert credential is None
    
    @pytest.mark.asyncio
    async def test_get_user_credentials(
        self, credential_repository, test_user, db_session
    ):
        """測試獲取用戶的所有憑證"""
        # 創建多個憑證
        await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="key1",
            encrypted_api_secret="secret1"
        )
        await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="okx",
            api_key="key2",
            encrypted_api_secret="secret2"
        )
        await db_session.commit()
        
        credentials = await credential_repository.get_user_credentials(test_user.id)
        
        assert len(credentials) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_credentials_filtered_by_exchange(
        self, credential_repository, test_user, db_session
    ):
        """測試根據交易所過濾憑證"""
        await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="key1",
            encrypted_api_secret="secret1"
        )
        await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="okx",
            api_key="key2",
            encrypted_api_secret="secret2"
        )
        await db_session.commit()
        
        credentials = await credential_repository.get_user_credentials(
            test_user.id, exchange_name="binance"
        )
        
        assert len(credentials) == 1
        assert credentials[0].exchange_name == "binance"


class TestCredentialRepositoryUpdate:
    """測試憑證更新"""
    
    @pytest.mark.asyncio
    async def test_update_credential_success(
        self, credential_repository, test_user, db_session
    ):
        """測試更新憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="old_key",
            encrypted_api_secret="old_secret"
        )
        await db_session.commit()
        
        updated = await credential_repository.update_credential(
            credential.id,
            test_user.id,
            api_key="new_key",
            encrypted_api_secret="new_secret"
        )
        await db_session.commit()
        
        assert updated is not None
        assert updated.api_key == "new_key"
        assert updated.encrypted_api_secret == "new_secret"
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_credential(
        self, credential_repository, test_user
    ):
        """測試更新不存在的憑證"""
        result = await credential_repository.update_credential(
            99999, test_user.id, api_key="new_key"
        )
        assert result is None


class TestCredentialRepositoryDelete:
    """測試憑證刪除"""
    
    @pytest.mark.asyncio
    async def test_delete_credential_success(
        self, credential_repository, test_user, db_session
    ):
        """測試刪除憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret"
        )
        await db_session.commit()
        
        result = await credential_repository.delete_credential(
            credential.id, test_user.id
        )
        await db_session.commit()
        
        assert result is True
        
        # 驗證憑證已被刪除
        deleted = await credential_repository.get_credential_by_id(credential.id)
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_credential(
        self, credential_repository, test_user
    ):
        """測試刪除不存在的憑證"""
        result = await credential_repository.delete_credential(99999, test_user.id)
        assert result is False


class TestCredentialRepositoryActivation:
    """測試憑證啟用/停用"""
    
    @pytest.mark.asyncio
    async def test_deactivate_credential(
        self, credential_repository, test_user, db_session
    ):
        """測試停用憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret"
        )
        await db_session.commit()
        
        result = await credential_repository.deactivate_credential(
            credential.id, test_user.id
        )
        await db_session.commit()
        
        assert result is True
        
        # 驗證憑證已停用
        updated = await credential_repository.get_credential_by_id(credential.id)
        assert updated.is_active is False
    
    @pytest.mark.asyncio
    async def test_activate_credential(
        self, credential_repository, test_user, db_session
    ):
        """測試啟用憑證"""
        credential = await credential_repository.create_credential(
            user_id=test_user.id,
            exchange_name="binance",
            api_key="test_key",
            encrypted_api_secret="secret",
            is_active=False
        )
        await db_session.commit()
        
        result = await credential_repository.activate_credential(
            credential.id, test_user.id
        )
        await db_session.commit()
        
        assert result is True
        
        # 驗證憑證已啟用
        updated = await credential_repository.get_credential_by_id(credential.id)
        assert updated.is_active is True
