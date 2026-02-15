"""
User Repository 單元測試
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.database import Base
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


# 測試資料庫 URL（使用 SQLite 記憶體資料庫）
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
def user_repository(db_session):
    """創建 UserRepository 實例"""
    return UserRepository(db_session)


class TestUserRepositoryCreate:
    """測試用戶創建"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository, db_session):
        """測試成功創建用戶"""
        user = await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        await db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_error(
        self, user_repository, db_session
    ):
        """
        Feature: ea-trading-backend, Property 5: 用戶名和電子郵件唯一性
        
        測試創建重複用戶名會拋出錯誤
        """
        # 創建第一個用戶
        await user_repository.create_user(
            username="testuser",
            email="test1@example.com",
            hashed_password="password1"
        )
        await db_session.commit()
        
        # 嘗試創建相同用戶名的用戶
        with pytest.raises(ValueError, match="用戶名 'testuser' 已存在"):
            await user_repository.create_user(
                username="testuser",
                email="test2@example.com",
                hashed_password="password2"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(
        self, user_repository, db_session
    ):
        """
        Feature: ea-trading-backend, Property 5: 用戶名和電子郵件唯一性
        
        測試創建重複電子郵件會拋出錯誤
        """
        # 創建第一個用戶
        await user_repository.create_user(
            username="user1",
            email="test@example.com",
            hashed_password="password1"
        )
        await db_session.commit()
        
        # 嘗試創建相同電子郵件的用戶
        with pytest.raises(ValueError, match="電子郵件 'test@example.com' 已存在"):
            await user_repository.create_user(
                username="user2",
                email="test@example.com",
                hashed_password="password2"
            )


class TestUserRepositoryRead:
    """測試用戶查詢"""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_repository, db_session):
        """測試根據 ID 獲取用戶"""
        created_user = await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="password"
        )
        await db_session.commit()
        
        user = await user_repository.get_user_by_id(created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repository):
        """測試獲取不存在的用戶"""
        user = await user_repository.get_user_by_id(99999)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_repository, db_session):
        """測試根據電子郵件獲取用戶"""
        await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="password"
        )
        await db_session.commit()
        
        user = await user_repository.get_user_by_email("test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, user_repository, db_session):
        """測試根據用戶名獲取用戶"""
        await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="password"
        )
        await db_session.commit()
        
        user = await user_repository.get_user_by_username("testuser")
        
        assert user is not None
        assert user.username == "testuser"


class TestUserRepositoryUpdate:
    """測試用戶更新"""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository, db_session):
        """測試更新用戶資訊"""
        user = await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="password"
        )
        await db_session.commit()
        
        updated_user = await user_repository.update_user(
            user.id,
            email="newemail@example.com",
            is_active=False
        )
        await db_session.commit()
        
        assert updated_user is not None
        assert updated_user.email == "newemail@example.com"
        assert updated_user.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, user_repository):
        """測試更新不存在的用戶"""
        result = await user_repository.update_user(99999, email="new@example.com")
        assert result is None


class TestUserRepositoryDelete:
    """測試用戶刪除"""
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repository, db_session):
        """測試刪除用戶"""
        user = await user_repository.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="password"
        )
        await db_session.commit()
        
        result = await user_repository.delete_user(user.id)
        await db_session.commit()
        
        assert result is True
        
        # 驗證用戶已被刪除
        deleted_user = await user_repository.get_user_by_id(user.id)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, user_repository):
        """測試刪除不存在的用戶"""
        result = await user_repository.delete_user(99999)
        assert result is False
