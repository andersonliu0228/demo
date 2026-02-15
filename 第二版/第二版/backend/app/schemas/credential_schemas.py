"""
Credential Schemas (DTOs)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateCredentialRequest(BaseModel):
    """創建憑證請求"""
    exchange_name: str = Field(..., min_length=1, max_length=50, description="交易所名稱")
    api_key: str = Field(..., min_length=1, description="API Key")
    api_secret: str = Field(..., min_length=1, description="API Secret")
    passphrase: Optional[str] = Field(None, description="Passphrase（某些交易所需要）")
    verify: bool = Field(True, description="是否驗證憑證")


class UpdateCredentialRequest(BaseModel):
    """更新憑證請求"""
    api_key: Optional[str] = Field(None, description="新的 API Key")
    api_secret: Optional[str] = Field(None, description="新的 API Secret")
    passphrase: Optional[str] = Field(None, description="新的 Passphrase")
    verify: bool = Field(True, description="是否重新驗證憑證")


class CredentialResponse(BaseModel):
    """憑證響應"""
    id: int
    exchange_name: str
    api_key_masked: str
    is_active: bool
    last_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VerifyCredentialRequest(BaseModel):
    """驗證憑證請求"""
    exchange_name: str = Field(..., description="交易所名稱")
    api_key: str = Field(..., description="API Key")
    api_secret: str = Field(..., description="API Secret")
    passphrase: Optional[str] = Field(None, description="Passphrase")


class VerifyCredentialResponse(BaseModel):
    """驗證憑證響應"""
    is_valid: bool
    has_trading_permission: bool
    account_info: Optional[dict] = None
    error_message: Optional[str] = None
