"""
Follow Relationship Model
跟隨關係模型 - 記錄跟隨者與 Master 的關係
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.database import Base


class FollowRelationship(Base):
    """跟隨關係表"""
    __tablename__ = "follow_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    master_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 跟隨比例 (例如 0.1 表示 10% 倍數)
    follow_ratio = Column(Float, nullable=False, default=0.1)
    
    # 是否啟用
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 跟隨者使用的憑證 ID
    follower_credential_id = Column(Integer, ForeignKey("api_credentials.id"), nullable=False)
    
    # Master 使用的憑證 ID (用於監控)
    master_credential_id = Column(Integer, ForeignKey("api_credentials.id"), nullable=False)
    
    # 時間戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 關聯
    follower = relationship("User", foreign_keys=[follower_user_id])
    master = relationship("User", foreign_keys=[master_user_id])
    follower_credential = relationship("ApiCredential", foreign_keys=[follower_credential_id])
    master_credential = relationship("ApiCredential", foreign_keys=[master_credential_id])
