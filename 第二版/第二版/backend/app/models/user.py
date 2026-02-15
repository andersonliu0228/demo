"""
User Model
用戶資料模型
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.app.database import Base


class UserRole(str, enum.Enum):
    """用戶角色枚舉"""
    MASTER = "master"
    FOLLOWER = "follower"


class User(Base):
    """
    用戶模型
    
    儲存用戶的基本資訊和認證資料
    """
    __tablename__ = "users"
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 用戶資訊
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用戶名稱"
    )
    
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="電子郵件"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="雜湊密碼"
    )
    
    # 用戶角色
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="用戶角色 (master/follower)"
    )
    
    # 狀態
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否啟用"
    )
    
    # 時間戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="創建時間"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新時間"
    )
    
    last_seen: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="最後上線時間（EA 心跳）"
    )
    
    # 關係：一個用戶可以有多個 API 憑證
    api_credentials: Mapped[List["ApiCredential"]] = relationship(
        "ApiCredential",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # 關係：一個用戶有多個倉位快照
    # 暫時註解以解決啟動錯誤
    # position_snapshots: Mapped[List["PositionSnapshot"]] = relationship(
    #     "PositionSnapshot",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin"
    # )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        轉換為字典
        
        Args:
            include_sensitive: 是否包含敏感資訊（如密碼雜湊）
            
        Returns:
            用戶資訊字典
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data["hashed_password"] = self.hashed_password
        
        return data
