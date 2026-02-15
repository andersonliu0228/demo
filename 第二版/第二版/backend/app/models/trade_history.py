"""
Trade History Model
交易歷史模型 - 記錄每次跟單的詳細資訊
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class TradeHistory(Base):
    """交易歷史表"""
    __tablename__ = "trade_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 關聯的跟隨關係
    follow_relationship_id = Column(Integer, ForeignKey("follow_relationships.id"), nullable=False, index=True)
    
    # 交易資訊
    symbol = Column(String(50), nullable=False, index=True)  # 交易對 (如 BTC/USDT)
    side = Column(String(10), nullable=False)  # buy 或 sell
    order_type = Column(String(20), nullable=False)  # limit, market
    
    # 數量與價格
    amount = Column(Float, nullable=False)  # 交易數量
    price = Column(Float, nullable=True)  # 交易價格 (market 單可能為 None)
    
    # 跟單比例
    follow_ratio = Column(Float, nullable=True)  # 跟隨比例
    
    # 滑價預估
    estimated_slippage = Column(Float, nullable=True)  # 預估滑價（百分比）
    actual_fill_price = Column(Float, nullable=True)  # 實際成交價格
    
    # Master 的原始倉位資訊
    master_position_size = Column(Float, nullable=True)  # Master 的倉位大小
    
    # 訂單 ID (來自交易所)
    order_id = Column(String(100), nullable=True)
    
    # 狀態
    status = Column(String(20), nullable=False, default="pending")  # pending, filled, failed
    
    # 錯誤訊息 (如果失敗)
    error_message = Column(Text, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 關聯
    follow_relationship = relationship("FollowRelationship")
