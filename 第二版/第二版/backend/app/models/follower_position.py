"""
Follower Position Model
跟隨者倉位模型 - 追蹤每個跟隨者的當前倉位
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.database import Base


class FollowerPosition(Base):
    """跟隨者倉位表"""
    __tablename__ = "follower_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    credential_id = Column(Integer, ForeignKey("api_credentials.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(50), nullable=False, index=True)
    
    # 倉位資訊
    position_size = Column(Float, nullable=False, default=0.0)  # 正數=多倉，負數=空倉，0=無倉位
    entry_price = Column(Float, nullable=True)  # 平均開倉價格
    
    # 時間戳
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關聯
    user = relationship("User", backref="follower_positions")
    credential = relationship("ApiCredential")
