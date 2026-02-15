"""
Global Setting Model
全局設定模型 - 用於緊急全停等系統級控制
"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class GlobalSetting(Base):
    """
    全局設定模型
    
    儲存系統級別的設定，如緊急全停開關
    """
    __tablename__ = "global_settings"
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 設定鍵
    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="設定鍵"
    )
    
    # 設定值（布林值）
    value_bool: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        comment="布林值"
    )
    
    # 設定值（字串）
    value_str: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="字串值"
    )
    
    # 設定值（文本）
    value_text: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="文本值"
    )
    
    # 描述
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="設定描述"
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
    
    def __repr__(self) -> str:
        return f"<GlobalSetting(key='{self.key}', value_bool={self.value_bool})>"
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "key": self.key,
            "value_bool": self.value_bool,
            "value_str": self.value_str,
            "value_text": self.value_text,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
