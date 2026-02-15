"""
Authentication Service
認證服務 - 處理用戶註冊、登入、JWT Token 生成和驗證
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# 密碼加密上下文
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    logger.info("✅ Passlib bcrypt 初始化成功")
except Exception as e:
    logger.error(f"❌ Passlib bcrypt 初始化失敗: {e}")
    raise

# OAuth2 密碼流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


class AuthService:
    """認證服務"""
    
    def __init__(self, user_repo: UserRepository):
        """
        初始化認證服務
        
        Args:
            user_repo: 用戶資料庫操作
        """
        self.user_repo = user_repo
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        驗證密碼
        
        Args:
            plain_password: 明文密碼
            hashed_password: 雜湊密碼
            
        Returns:
            是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        生成密碼雜湊
        
        Args:
            password: 明文密碼
            
        Returns:
            雜湊密碼
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        創建 JWT Access Token
        
        Args:
            data: 要編碼的數據
            expires_delta: 過期時間
            
        Returns:
            JWT Token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        驗證用戶
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            用戶對象，如果驗證失敗則返回 None
        """
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def register_user(self, username: str, email: str, password: str, role: Optional[str] = None) -> User:
        """
        註冊新用戶
        
        Args:
            username: 用戶名
            email: 電子郵件
            password: 密碼
            role: 用戶角色 (master/follower)
            
        Returns:
            新創建的用戶
            
        Raises:
            ValueError: 如果用戶名或郵件已存在
        """
        # 檢查用戶名是否已存在
        existing_user = await self.user_repo.get_user_by_username(username)
        if existing_user:
            raise ValueError("用戶名已存在")
        
        # 檢查郵件是否已存在
        existing_email = await self.user_repo.get_user_by_email(email)
        if existing_email:
            raise ValueError("電子郵件已存在")
        
        # 創建新用戶
        hashed_password = self.get_password_hash(password)
        user = await self.user_repo.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        
        return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    獲取當前登入用戶
    
    Args:
        token: JWT Token
        db: 資料庫 session
        
    Returns:
        當前用戶
        
    Raises:
        HTTPException: 如果 token 無效或用戶不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(username)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用戶已被停用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    獲取當前活躍用戶
    
    Args:
        current_user: 當前用戶
        
    Returns:
        當前活躍用戶
        
    Raises:
        HTTPException: 如果用戶未啟用
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用戶未啟用")
    return current_user
