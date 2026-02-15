"""
Trade Error Model
交易錯誤模型 - 記錄交易失敗和錯誤
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.database import Base


class TradeError(Base):
    """交易錯誤表"""
    __tablename__ = "trade_errors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trade_log_id = Column(Integer, ForeignKey("trade_logs.id", ondelete="SET NULL"), nullable=True)
    
    # 錯誤資訊
    error_type = Column(String(50), nullable=False)  # 錯誤類型：exchange_error, validation_error, etc.
    error_message = Column(Text, nullable=False)  # 錯誤訊息
    error_details = Column(Text, nullable=True)  # 詳細錯誤資訊（JSON 格式）
    
    # 狀態
    is_resolved = Column(Boolean, nullable=False, default=False)  # 是否已解決
    resolved_at = Column(DateTime, nullable=True)  # 解決時間
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 解決者
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 關聯
    user = relationship("User", foreign_keys=[user_id], backref="trade_errors")
    trade_log = relationship("TradeLog", backref="errors")
    resolver = relationship("User", foreign_keys=[resolved_by])
