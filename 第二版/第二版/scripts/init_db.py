"""
初始化資料庫腳本
執行 Alembic 遷移來創建資料表
"""
import asyncio
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app.database import engine, Base
from backend.app.models import User, ApiCredential


async def init_database():
    """初始化資料庫"""
    print("正在初始化資料庫...")
    
    async with engine.begin() as conn:
        # 創建所有資料表
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 資料庫初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_database())
