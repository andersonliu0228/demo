"""
Master Position Model
Master 倉位模型 - 記錄 Master 當前的倉位狀態
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class MasterPosition(Base):
    """Master 倉位表"""
    __tablename__ = "master_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Master 用戶和憑證
    master_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    master_credential_id = Column(Integer, ForeignKey("api_credentials.id"), nullable=False, index=True)
    
    # 交易對
    symbol = Column(String(50), nullable=False, index=True)
    
    # 倉位資訊
    position_size = Column(Float, nullable=False, default=0.0)  # 正數=多倉，負數=空倉，0=無倉位
    entry_price = Column(Float, nullable=True)  # 平均開倉價
    
    # 時間戳
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 關聯
    master = relationship("User", foreign_keys=[master_user_id])
    credential = relationship("ApiCredential", foreign_keys=[master_credential_id])
