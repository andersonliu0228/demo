"""
Database Configuration
配置 SQLAlchemy 非同步引擎和會話管理
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from backend.app.config import settings

# 創建 Base 類別用於模型定義
Base = declarative_base()

# 創建非同步引擎
# 使用 asyncpg 驅動（postgresql+asyncpg://）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 在開發模式下顯示 SQL 語句
    future=True,
    pool_size=10,  # 連接池大小
    max_overflow=20,  # 最大溢出連接數
    pool_pre_ping=True,  # 在使用連接前檢查連接是否有效
    pool_recycle=3600,  # 連接回收時間（秒）
    poolclass=QueuePool,  # 使用隊列池
)

# 創建非同步會話工廠
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交後不過期對象
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依賴注入函數：提供資料庫會話
    
    使用方式：
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: 資料庫會話
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化資料庫
    創建所有資料表（僅用於開發/測試，生產環境使用 Alembic）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    關閉資料庫連接
    在應用程式關閉時調用
    """
    await engine.dispose()


# 測試用的引擎和會話工廠
def get_test_engine(database_url: str):
    """
    創建測試用的資料庫引擎
    
    Args:
        database_url: 測試資料庫 URL
        
    Returns:
        測試引擎
    """
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
        poolclass=NullPool,  # 測試時不使用連接池
    )


def get_test_session_factory(test_engine):
    """
    創建測試用的會話工廠
    
    Args:
        test_engine: 測試引擎
        
    Returns:
        測試會話工廠
    """
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
