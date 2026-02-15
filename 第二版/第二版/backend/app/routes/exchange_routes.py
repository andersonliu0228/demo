"""
Exchange Routes
交易所路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.credential_schemas import (
    VerifyCredentialRequest,
    VerifyCredentialResponse,
)
from backend.app.services.exchange_service import get_exchange_service, ExchangeService

router = APIRouter(prefix="/api/v1/exchange", tags=["exchange"])


@router.post("/verify", response_model=VerifyCredentialResponse)
async def verify_credential(
    request: VerifyCredentialRequest,
    exchange_service: ExchangeService = Depends(get_exchange_service),
    # current_user: User = Depends(get_current_user),
):
    """
    驗證 API 憑證但不儲存
    
    用於在綁定前測試憑證是否有效
    """
    result = await exchange_service.verify_credentials(
        exchange_name=request.exchange_name,
        api_key=request.api_key,
        api_secret=request.api_secret,
        passphrase=request.passphrase
    )
    
    return VerifyCredentialResponse(**result)


@router.get("/supported", response_model=List[str])
async def get_supported_exchanges(
    exchange_service: ExchangeService = Depends(get_exchange_service),
):
    """獲取支援的交易所列表"""
    return exchange_service.get_supported_exchanges()
