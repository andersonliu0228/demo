"""
Trade Log Model
交易日誌模型 - 記錄每次跟單的詳細日誌
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class TradeLog(Base):
    """交易日誌表 - 詳細記錄每次跟單操作"""
    __tablename__ = "trade_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 時間戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Master 資訊
    master_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    master_credential_id = Column(Integer, ForeignKey("api_credentials.id"), nullable=False)
    master_action = Column(String(50), nullable=False)  # 例如: "open_long", "close_position", "increase_position"
    master_symbol = Column(String(50), nullable=False, index=True)
    master_position_size = Column(Float, nullable=False)
    master_entry_price = Column(Float, nullable=True)
    
    # 跟隨者資訊
    follower_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    follower_credential_id = Column(Integer, ForeignKey("api_credentials.id"), nullable=False)
    follower_action = Column(String(50), nullable=False)  # 例如: "follow_long", "follow_close"
    follower_ratio = Column(Float, nullable=False)  # 跟隨比例
    follower_amount = Column(Float, nullable=False)  # 實際下單數量
    
    # 訂單資訊
    order_id = Column(String(100), nullable=True)
    order_type = Column(String(20), nullable=False)  # market, limit
    side = Column(String(10), nullable=False)  # buy, sell
    
    # 執行狀態
    status = Column(String(20), nullable=False, index=True)  # success, failed, pending
    is_success = Column(Boolean, nullable=False, default=False)
    
    # 錯誤訊息
    error_message = Column(Text, nullable=True)
    
    # 執行時間
    execution_time_ms = Column(Integer, nullable=True)  # 執行耗時（毫秒）
    
    # 關聯
    master = relationship("User", foreign_keys=[master_user_id])
    follower = relationship("User", foreign_keys=[follower_user_id])
