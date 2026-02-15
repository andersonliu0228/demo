"""
API Credential Model
API 憑證資料模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class ApiCredential(Base):
    """
    API 憑證模型
    
    儲存用戶的交易所 API 憑證（加密存儲）
    """
    __tablename__ = "api_credentials"
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 外鍵：關聯到用戶
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用戶 ID"
    )
    
    # 交易所資訊
    exchange_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="交易所名稱（如 binance, okx）"
    )
    
    # API 憑證（明文存儲 API Key，加密存儲 Secret）
    api_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="API Key（明文）"
    )
    
    encrypted_api_secret: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="加密的 API Secret"
    )
    
    encrypted_passphrase: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="加密的 Passphrase（某些交易所需要）"
    )
    
    # 狀態
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否啟用"
    )
    
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="最後驗證時間"
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
    
    # 關係：多個憑證屬於一個用戶
    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_credentials"
    )
    
    # 唯一性約束：一個用戶在同一交易所只能有一個相同的 API Key
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'exchange_name',
            'api_key',
            name='uq_user_exchange_key'
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<ApiCredential(id={self.id}, user_id={self.user_id}, "
            f"exchange='{self.exchange_name}', api_key='{self.mask_api_key()}')>"
        )
    
    def mask_api_key(self, show_chars: int = 4) -> str:
        """
        遮蔽 API Key，只顯示前後幾位
        
        Args:
            show_chars: 顯示的字元數
            
        Returns:
            遮蔽後的 API Key
        """
        if not self.api_key or len(self.api_key) <= show_chars * 2:
            return "****"
        
        return f"{self.api_key[:show_chars]}...{self.api_key[-show_chars:]}"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        轉換為字典
        
        Args:
            include_sensitive: 是否包含敏感資訊（加密的 Secret）
            
        Returns:
            憑證資訊字典
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "exchange_name": self.exchange_name,
            "api_key_masked": self.mask_api_key(),
            "is_active": self.is_active,
            "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data["api_key"] = self.api_key
            data["encrypted_api_secret"] = self.encrypted_api_secret
            data["encrypted_passphrase"] = self.encrypted_passphrase
        
        return data
