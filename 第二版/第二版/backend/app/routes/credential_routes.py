"""
Credential Routes
API 憑證路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.schemas.credential_schemas import (
    CreateCredentialRequest,
    UpdateCredentialRequest,
    CredentialResponse,
)
from backend.app.services.credential_service import CredentialService
from backend.app.services.crypto_service import get_crypto_service
from backend.app.services.exchange_service import get_exchange_service
from backend.app.services.cache_service import get_cache_service
from backend.app.repositories.credential_repository import CredentialRepository
from backend.app.config import settings

router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])


async def get_credential_service(
    db: AsyncSession = Depends(get_db)
) -> CredentialService:
    """獲取 Credential Service 實例"""
    credential_repo = CredentialRepository(db)
    crypto_service = get_crypto_service(settings.ENCRYPTION_KEY)
    exchange_service = get_exchange_service()
    cache_service = await get_cache_service(settings.REDIS_URL)
    
    return CredentialService(
        credential_repo,
        crypto_service,
        exchange_service,
        cache_service
    )


@router.post("/", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(
    request: CreateCredentialRequest,
    credential_service: CredentialService = Depends(get_credential_service),
    # current_user: User = Depends(get_current_user),  # TODO: 實作認證
):
    """
    綁定新的 API 憑證
    
    - **exchange_name**: 交易所名稱（如 binance, okx）
    - **api_key**: API Key
    - **api_secret**: API Secret
    - **passphrase**: Passphrase（可選，某些交易所需要）
    - **verify**: 是否在創建前驗證憑證（默認 true）
    """
    # TODO: 從認證中獲取 user_id
    user_id = 1  # 臨時使用固定值
    
    try:
        credential = await credential_service.create_credential(
            user_id=user_id,
            exchange_name=request.exchange_name,
            api_key=request.api_key,
            api_secret=request.api_secret,
            passphrase=request.passphrase,
            verify=request.verify
        )
        
        return CredentialResponse(
            id=credential.id,
            exchange_name=credential.exchange_name,
            api_key_masked=credential.mask_api_key(),
            is_active=credential.is_active,
            last_verified_at=credential.last_verified_at,
            created_at=credential.created_at,
            updated_at=credential.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[CredentialResponse])
async def list_credentials(
    include_inactive: bool = False,
    credential_service: CredentialService = Depends(get_credential_service),
    # current_user: User = Depends(get_current_user),
):
    """
    獲取當前用戶的所有憑證
    
    - **include_inactive**: 是否包含已停用的憑證
    """
    user_id = 1  # TODO: 從認證中獲取
    
    credentials = await credential_service.get_user_credentials(
        user_id, include_inactive
    )
    
    return [
        CredentialResponse(
            id=cred.id,
            exchange_name=cred.exchange_name,
            api_key_masked=cred.mask_api_key(),
            is_active=cred.is_active,
            last_verified_at=cred.last_verified_at,
            created_at=cred.created_at,
            updated_at=cred.updated_at
        )
        for cred in credentials
    ]


@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    credential_service: CredentialService = Depends(get_credential_service),
    # current_user: User = Depends(get_current_user),
):
    """獲取特定憑證的詳細資訊"""
    user_id = 1  # TODO: 從認證中獲取
    
    credential = await credential_service.get_credential_by_id(
        credential_id, user_id
    )
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="憑證不存在"
        )
    
    return CredentialResponse(
        id=credential.id,
        exchange_name=credential.exchange_name,
        api_key_masked=credential.mask_api_key(),
        is_active=credential.is_active,
        last_verified_at=credential.last_verified_at,
        created_at=credential.created_at,
        updated_at=credential.updated_at
    )


@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: int,
    request: UpdateCredentialRequest,
    credential_service: CredentialService = Depends(get_credential_service),
    # current_user: User = Depends(get_current_user),
):
    """更新現有憑證"""
    user_id = 1  # TODO: 從認證中獲取
    
    try:
        credential = await credential_service.update_credential(
            credential_id=credential_id,
            user_id=user_id,
            api_key=request.api_key,
            api_secret=request.api_secret,
            passphrase=request.passphrase,
            verify=request.verify
        )
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="憑證不存在"
            )
        
        return CredentialResponse(
            id=credential.id,
            exchange_name=credential.exchange_name,
            api_key_masked=credential.mask_api_key(),
            is_active=credential.is_active,
            last_verified_at=credential.last_verified_at,
            created_at=credential.created_at,
            updated_at=credential.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: int,
    credential_service: CredentialService = Depends(get_credential_service),
    # current_user: User = Depends(get_current_user),
):
    """刪除憑證"""
    user_id = 1  # TODO: 從認證中獲取
    
    result = await credential_service.delete_credential(credential_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="憑證不存在"
        )
    
    return None
