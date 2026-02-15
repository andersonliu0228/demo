"""
創建測試跟單關係
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.app.database import async_session_maker
from backend.app.models.user import User
from backend.app.models.follower_relation import FollowerRelation, RelationStatus


async def create_test_relations():
    """創建測試跟單關係"""
    print("=" * 60)
    print("創建測試跟單關係")
    print("=" * 60)
    print()
    
    async with async_session_maker() as session:
        # 1. 獲取或創建 Master 用戶
        print("[1/3] 檢查 Master 用戶...")
        stmt = select(User).where(User.username == "testuser")
        result = await session.execute(stmt)
        master = result.scalar_one_or_none()
        
        if not master:
            print("   ⚠️  testuser 不存在，請先運行 init_test_data.py")
            return
        
        print(f"   ✅ Master 用戶: {master.username} (ID: {master.id})")
        
        # 2. 創建 Follower 用戶
        print("\n[2/3] 創建 Follower 用戶...")
        followers_data = [
            {"username": "follower1", "email": "follower1@test.com", "password": "pass123"},
            {"username": "follower2", "email": "follower2@test.com", "password": "pass123"},
            {"username": "follower3", "email": "follower3@test.com", "password": "pass123"},
        ]
        
        from backend.app.services.crypto_service import CryptoService
        crypto_service = CryptoService()
        
        followers = []
        for data in followers_data:
            # 檢查是否已存在
            stmt = select(User).where(User.username == data["username"])
            result = await session.execute(stmt)
            follower = result.scalar_one_or_none()
            
            if not follower:
                follower = User(
                    username=data["username"],
                    email=data["email"],
                    hashed_password=crypto_service.hash_password(data["password"]),
                    role="follower",
                    is_active=True
                )
                session.add(follower)
                await session.flush()
                print(f"   ✅ 創建 Follower: {follower.username} (ID: {follower.id})")
            else:
                print(f"   ℹ️  Follower 已存在: {follower.username} (ID: {follower.id})")
            
            followers.append(follower)
        
        await session.commit()
        
        # 3. 創建跟單關係
        print("\n[3/3] 創建跟單關係...")
        relations_data = [
            {"follower": followers[0], "copy_ratio": 1.0, "status": RelationStatus.ACTIVE},
            {"follower": followers[1], "copy_ratio": 0.5, "status": RelationStatus.PENDING},
            {"follower": followers[2], "copy_ratio": 2.0, "status": RelationStatus.BLOCKED},
        ]
        
        for data in relations_data:
            # 檢查是否已存在
            stmt = select(FollowerRelation).where(
                FollowerRelation.master_id == master.id,
                FollowerRelation.follower_id == data["follower"].id
            )
            result = await session.execute(stmt)
            relation = result.scalar_one_or_none()
            
            if not relation:
                relation = FollowerRelation(
                    master_id=master.id,
                    follower_id=data["follower"].id,
                    copy_ratio=data["copy_ratio"],
                    status=data["status"].value
                )
                session.add(relation)
                await session.flush()
                print(f"   ✅ 創建關係: {data['follower'].username} -> {master.username} (比例: {data['copy_ratio']}x, 狀態: {data['status'].value})")
            else:
                print(f"   ℹ️  關係已存在: {data['follower'].username} -> {master.username}")
        
        await session.commit()
    
    print()
    print("=" * 60)
    print("✅ 測試跟單關係創建完成！")
    print("=" * 60)
    print()
    print("現在可以測試系統了：")
    print("  1. 使用 testuser / testpass123 登入")
    print("  2. 訪問 /admin 查看客戶列表")
    print("  3. 測試更新跟單比例和狀態")
    print()


if __name__ == "__main__":
    asyncio.run(create_test_relations())
