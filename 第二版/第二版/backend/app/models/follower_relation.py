"""
Follower Relation Model
跟隨者關係模型 - 記錄交易員與客戶的跟單關係
"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.app.database import Base


class RelationStatus(str, enum.Enum):
    """關係狀態枚舉"""
    PENDING = "pending"    # 待核准
    ACTIVE = "active"      # 已啟用
    BLOCKED = "blocked"    # 已封鎖


class FollowerRelation(Base):
    """
    跟隨者關係模型
    
    記錄交易員（Master）與客戶（Follower）之間的跟單關係
    """
    __tablename__ = "follower_relations"
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 外鍵
    master_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="交易員 ID"
    )
    
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="跟隨者 ID"
    )
    
    # 跟單設定
    copy_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="跟單倍率"
    )
    
    # 狀態
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RelationStatus.PENDING.value,
        comment="關係狀態"
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
    
    # 關聯
    master: Mapped["User"] = relationship(
        "User",
        foreign_keys=[master_id],
        lazy="selectin"
    )
    
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<FollowerRelation(id={self.id}, master_id={self.master_id}, follower_id={self.follower_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "master_id": self.master_id,
            "follower_id": self.follower_id,
            "copy_ratio": self.copy_ratio,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
