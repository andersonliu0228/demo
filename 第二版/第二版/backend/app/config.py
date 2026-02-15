"""
Application Configuration
"""
import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """應用程式設定"""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Encryption
    ENCRYPTION_KEY: str
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 小時
    
    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Telegram 通知配置
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    TELEGRAM_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_settings(self):
        """驗證關鍵設定"""
        errors = []
        
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-in-production":
            errors.append("⚠️  WARNING: JWT_SECRET_KEY 未設置或使用預設值，這在生產環境中不安全！")
        
        if not self.ENCRYPTION_KEY or self.ENCRYPTION_KEY == "your-base64-encoded-fernet-key-here":
            errors.append("⚠️  WARNING: ENCRYPTION_KEY 未設置或使用預設值！")
        
        if not self.DATABASE_URL:
            errors.append("❌ ERROR: DATABASE_URL 未設置！")
        
        if not self.REDIS_URL:
            errors.append("❌ ERROR: REDIS_URL 未設置！")
        
        if errors:
            for error in errors:
                logger.warning(error)
                print(error)
        
        return len([e for e in errors if e.startswith("❌")]) == 0


# Global settings instance
settings = Settings()

# 驗證設定
if not settings.validate_settings():
    raise ValueError("關鍵配置缺失，無法啟動應用程式")
