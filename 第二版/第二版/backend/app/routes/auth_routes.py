"""
Authentication Routes
認證 API 路由 - 註冊、登入、Token 驗證
"""
import logging
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.auth_service import AuthService, get_current_active_user
from backend.app.repositories.user_repository import UserRepository
from backend.app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/auth", tags=["authentication"])


# Pydantic 模型
class UserRegister(BaseModel):
    """用戶註冊請求"""
    username: str
    email: EmailStr
    password: str
    role: str | None = None  # 可選的角色欄位


class UserResponse(BaseModel):
    """用戶響應"""
    id: int
    username: str
    email: str
    role: str | None = None
    is_active: bool
    created_at: str


class Token(BaseModel):
    """Token 響應"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token 數據"""
    username: str | None = None


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """獲取認證服務"""
    user_repo = UserRepository(db)
    return AuthService(user_repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    註冊新用戶
    
    創建新的用戶帳號
    """
    try:
        user = await auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        logger.info(f"新用戶註冊成功: {user.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        
    except ValueError as e:
        logger.warning(f"註冊失敗: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"註冊錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="註冊失敗"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用戶登入
    
    使用用戶名和密碼登入，返回 JWT Token
    """
    try:
        logger.info(f"🔐 登入請求: username={form_data.username}")
        
        user = await auth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )
        
        if not user:
            logger.warning(f"❌ 登入失敗: 用戶名或密碼錯誤 - {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶名或密碼錯誤",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ 用戶驗證成功: {user.username}, is_active={user.is_active}")
        
        # 創建 access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ Token 生成成功: {user.username}, expires_in={settings.ACCESS_TOKEN_EXPIRE_MINUTES}min")
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 登入錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登入失敗: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    獲取當前用戶資訊
    
    返回當前登入用戶的詳細資訊
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用戶登出
    
    注意：JWT Token 是無狀態的，實際的登出需要在客戶端刪除 Token
    """
    logger.info(f"用戶登出: {current_user.username}")
    return {"message": "登出成功"}
