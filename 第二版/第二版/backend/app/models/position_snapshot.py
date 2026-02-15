"""
Position Snapshot Model
倉位快照模型 - 用於 PnL 統計
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Date, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class PositionSnapshot(Base):
    """
    倉位快照模型
    
    每天定時記錄帳戶總值，用於計算收益統計
    """
    __tablename__ = "position_snapshots"
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 外鍵：關聯到用戶
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用戶 ID"
    )
    
    # 快照日期
    snapshot_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="快照日期"
    )
    
    # 帳戶總值（USDT）
    total_value_usdt: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="帳戶總值（USDT）"
    )
    
    # 持倉數量
    position_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        comment="持倉數量"
    )
    
    # 詳細資訊（JSON 格式存儲各幣種餘額）
    details: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
        comment="詳細資訊（JSON）"
    )
    
    # 時間戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="創建時間"
    )
    
    # 關係：多個快照屬於一個用戶
    # 暫時註解以解決啟動錯誤 - 等 User 模型修復後再啟用
    # user: Mapped["User"] = relationship(
    #     "User",
    #     back_populates="position_snapshots"
    # )
    
    # 索引：用戶 + 日期唯一
    __table_args__ = (
        Index('idx_user_snapshot_date', 'user_id', 'snapshot_date', unique=True),
    )
    
    def __repr__(self) -> str:
        return (
            f"<PositionSnapshot(id={self.id}, user_id={self.user_id}, "
            f"date={self.snapshot_date}, value={self.total_value_usdt})>"
        )
    
    def to_dict(self) -> dict:
        """
        轉換為字典
        
        Returns:
            快照資訊字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "total_value_usdt": self.total_value_usdt,
            "position_count": self.position_count,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
