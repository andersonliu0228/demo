"""
初始化測試數據腳本
確保系統有必要的測試數據，避免 ForeignKeyViolationError
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from backend.app.config import settings
from backend.app.models.user import User
from backend.app.models.api_credential import ApiCredential
from backend.app.services.crypto_service import CryptoService


async def init_test_data():
    """初始化測試數據"""
    print("=" * 60)
    print("初始化測試數據")
    print("=" * 60)
    
    # 創建資料庫引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 1. 檢查並創建 testuser
            print("\n[1/2] 檢查測試用戶...")
            result = await session.execute(
                select(User).where(User.username == "testuser")
            )
            testuser = result.scalar_one_or_none()
            
            if not testuser:
                print("   ⚠️  testuser 不存在，創建中...")
                from backend.app.services.auth_service import AuthService
                from backend.app.repositories.user_repository import UserRepository
                
                user_repo = UserRepository(session)
                auth_service = AuthService(user_repo)
                
                testuser = await auth_service.register_user(
                    username="testuser",
                    email="test@example.com",
                    password="testpass123"
                )
                await session.commit()
                print(f"   ✅ testuser 創建成功 (ID: {testuser.id})")
            else:
                print(f"   ✅ testuser 已存在 (ID: {testuser.id})")
            
            # 2. 檢查並創建 ID=1 的測試憑證
            print("\n[2/2] 檢查測試憑證 (ID=1)...")
            result = await session.execute(
                select(ApiCredential).where(ApiCredential.id == 1)
            )
            credential = result.scalar_one_or_none()
            
            if not credential:
                print("   ⚠️  ID=1 的憑證不存在，創建中...")
                
                # 使用 CryptoService 加密
                crypto_service = CryptoService(settings.ENCRYPTION_KEY)
                encrypted_secret = crypto_service.encrypt("test_secret_12345")
                
                # 創建憑證
                credential = ApiCredential(
                    id=1,  # 明確指定 ID
                    user_id=testuser.id,
                    exchange_name="mock",
                    api_key="test_api_key_12345",
                    encrypted_api_secret=encrypted_secret,
                    is_active=True
                )
                
                session.add(credential)
                await session.commit()
                await session.refresh(credential)
                
                print(f"   ✅ 測試憑證創建成功 (ID: {credential.id})")
                print(f"      - User ID: {credential.user_id}")
                print(f"      - Exchange: {credential.exchange_name}")
                print(f"      - API Key: {credential.api_key}")
            else:
                print(f"   ✅ ID=1 的憑證已存在")
                print(f"      - User ID: {credential.user_id}")
                print(f"      - Exchange: {credential.exchange_name}")
                print(f"      - API Key: {credential.api_key}")
            
            print("\n" + "=" * 60)
            print("✅ 測試數據初始化完成！")
            print("=" * 60)
            print("\n可以開始測試系統了：")
            print("  1. 使用 testuser / testpass123 登入")
            print("  2. 觸發 Master 訂單不會再出現 ForeignKeyViolationError")
            print("  3. 系統已準備好進行完整測試")
            print()
            
        except Exception as e:
            print(f"\n❌ 初始化失敗: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_test_data())
