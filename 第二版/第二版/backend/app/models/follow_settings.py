"""
Follow Settings Model
跟單設定模型 - 用戶的跟單配置
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from backend.app.database import Base


class FollowSettings(Base):
    """跟單設定表"""
    __tablename__ = "follow_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    master_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    master_credential_id = Column(Integer, ForeignKey("api_credentials.id", ondelete="CASCADE"), nullable=False)
    follower_credential_id = Column(Integer, ForeignKey("api_credentials.id", ondelete="CASCADE"), nullable=False)
    
    # 跟單配置
    follow_ratio = Column(Float, nullable=False, default=0.1)  # 跟單比例（例如 0.1 = 10%）
    is_active = Column(Boolean, nullable=False, default=True)  # 是否啟用跟單
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 關聯
    user = relationship("User", foreign_keys=[user_id], backref="follow_settings")
    master_user = relationship("User", foreign_keys=[master_user_id])
    master_credential = relationship("ApiCredential", foreign_keys=[master_credential_id])
    follower_credential = relationship("ApiCredential", foreign_keys=[follower_credential_id])
