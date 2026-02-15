"""
Test Routes
測試用 API 路由（僅用於開發環境）
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.services.credential_service import CredentialService
from backend.app.services.crypto_service import get_crypto_service
from backend.app.services.exchange_service import get_exchange_service, MockExchange
from backend.app.services.cache_service import get_cache_service
from backend.app.repositories.credential_repository import CredentialRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/test", tags=["test"])


def get_credential_service(db: AsyncSession = Depends(get_db)) -> CredentialService:
    """獲取 Credential Service 實例"""
    credential_repo = CredentialRepository(db)
    crypto_service = get_crypto_service(settings.ENCRYPTION_KEY)
    exchange_service = get_exchange_service()
    cache_service = get_cache_service()
    
    return CredentialService(
        credential_repo=credential_repo,
        crypto_service=crypto_service,
        exchange_service=exchange_service,
        cache_service=cache_service
    )


@router.get("/mock-balance", response_model=Dict[str, Any])
async def get_mock_balance(
    credential_id: int,
    user_id: int = 1,  # TODO: 從認證中間件獲取
    credential_service: CredentialService = Depends(get_credential_service)
):
    """
    測試 Mock Exchange 餘額查詢
    
    此接口展示完整的加密流程：
    1. 從資料庫取出加密的憑證
    2. 使用 crypto_service 解密
    3. 使用解密後的憑證調用 MockExchange
    4. 返回模擬的餘額資訊
    
    Args:
        credential_id: 憑證 ID
        user_id: 用戶 ID
        
    Returns:
        包含餘額和加密流程資訊的字典
    """
    try:
        # 步驟 1: 從資料庫獲取憑證（加密狀態）
        credential = await credential_service.get_credential_by_id(
            credential_id=credential_id,
            user_id=user_id
        )
        
        if not credential:
            raise HTTPException(status_code=404, detail="憑證不存在")
        
        # 驗證是否為 Mock Exchange
        if credential.exchange_name.lower() != 'mock':
            raise HTTPException(
                status_code=400,
                detail=f"此接口僅支援 Mock Exchange，當前憑證為: {credential.exchange_name}"
            )
        
        logger.info(f"測試 Mock Balance - 憑證 ID: {credential_id}")
        logger.info(f"  - Exchange: {credential.exchange_name}")
        logger.info(f"  - API Key: {credential.api_key[:8]}...")
        logger.info(f"  - Encrypted Secret 長度: {len(credential.encrypted_api_secret)}")
        
        # 步驟 2: 獲取解密後的憑證
        decrypted_cred = await credential_service.get_decrypted_credential(
            credential_id=credential_id,
            user_id=user_id
        )
        
        if not decrypted_cred:
            raise HTTPException(status_code=404, detail="無法解密憑證")
        
        logger.info(f"  - 解密成功！Secret 長度: {len(decrypted_cred['api_secret'])}")
        
        # 步驟 3: 創建 MockExchange 實例（使用解密後的憑證）
        mock_exchange = MockExchange(
            api_key=decrypted_cred['api_key'],
            api_secret=decrypted_cred['api_secret'],
            passphrase=decrypted_cred.get('passphrase')
        )
        
        # 步驟 4: 調用 MockExchange 獲取餘額
        balance = mock_exchange.fetch_balance()
        
        logger.info(f"  - Mock Balance 獲取成功")
        
        # 返回結果，包含加密流程資訊
        return {
            "success": True,
            "credential_info": {
                "id": credential.id,
                "exchange": credential.exchange_name,
                "api_key_masked": credential_service.mask_api_key(credential.api_key),
                "created_at": credential.created_at.isoformat(),
                "last_verified_at": credential.last_verified_at.isoformat() if credential.last_verified_at else None
            },
            "encryption_flow": {
                "step_1": "從資料庫取出加密憑證 ✓",
                "step_2": "使用 CryptoService 解密 ✓",
                "step_3": "創建 MockExchange 實例 ✓",
                "step_4": "調用 fetch_balance() ✓",
                "encrypted_secret_length": len(credential.encrypted_api_secret),
                "decrypted_secret_length": len(decrypted_cred['api_secret']),
                "encryption_verified": len(credential.encrypted_api_secret) > len(decrypted_cred['api_secret'])
            },
            "balance": balance,
            "note": "這是 Mock 數據，不是真實交易所餘額"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"測試 Mock Balance 失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"測試失敗: {str(e)}")


@router.post("/mock-order", response_model=Dict[str, Any])
async def create_mock_order(
    credential_id: int,
    symbol: str = "BTC/USDT",
    order_type: str = "limit",
    side: str = "buy",
    amount: float = 0.01,
    price: float = 50000.0,
    user_id: int = 1,  # TODO: 從認證中間件獲取
    credential_service: CredentialService = Depends(get_credential_service)
):
    """
    測試 Mock Exchange 下單
    
    展示完整的加密流程並創建模擬訂單
    
    Args:
        credential_id: 憑證 ID
        symbol: 交易對
        order_type: 訂單類型（limit/market）
        side: 買賣方向（buy/sell）
        amount: 數量
        price: 價格
        user_id: 用戶 ID
        
    Returns:
        包含訂單資訊和加密流程資訊的字典
    """
    try:
        # 獲取並解密憑證
        credential = await credential_service.get_credential_by_id(
            credential_id=credential_id,
            user_id=user_id
        )
        
        if not credential:
            raise HTTPException(status_code=404, detail="憑證不存在")
        
        if credential.exchange_name.lower() != 'mock':
            raise HTTPException(
                status_code=400,
                detail=f"此接口僅支援 Mock Exchange，當前憑證為: {credential.exchange_name}"
            )
        
        # 解密憑證
        decrypted_cred = await credential_service.get_decrypted_credential(
            credential_id=credential_id,
            user_id=user_id
        )
        
        # 創建 MockExchange 並下單
        mock_exchange = MockExchange(
            api_key=decrypted_cred['api_key'],
            api_secret=decrypted_cred['api_secret'],
            passphrase=decrypted_cred.get('passphrase')
        )
        
        order = mock_exchange.create_order(
            symbol=symbol,
            order_type=order_type,
            side=side,
            amount=amount,
            price=price if order_type == 'limit' else None
        )
        
        logger.info(f"Mock 訂單創建成功 - Order ID: {order['id']}")
        
        return {
            "success": True,
            "credential_info": {
                "id": credential.id,
                "exchange": credential.exchange_name,
                "api_key_masked": credential_service.mask_api_key(credential.api_key)
            },
            "encryption_flow": {
                "decryption_verified": True,
                "api_key_used": decrypted_cred['api_key'][:8] + "...",
                "secret_length": len(decrypted_cred['api_secret'])
            },
            "order": order,
            "note": "這是 Mock 訂單，不會在真實交易所執行"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"創建 Mock 訂單失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"創建訂單失敗: {str(e)}")


@router.get("/encryption-flow", response_model=Dict[str, Any])
async def test_encryption_flow(
    test_secret: str = "my_test_secret_12345"
):
    """
    測試加密解密流程
    
    展示 CryptoService 的加密和解密功能
    
    Args:
        test_secret: 測試用的明文
        
    Returns:
        加密解密流程的結果
    """
    try:
        crypto_service = get_crypto_service(settings.ENCRYPTION_KEY)
        
        # 加密
        encrypted = crypto_service.encrypt(test_secret)
        logger.info(f"加密成功 - 原文長度: {len(test_secret)}, 密文長度: {len(encrypted)}")
        
        # 解密
        decrypted = crypto_service.decrypt(encrypted)
        logger.info(f"解密成功 - 解密後長度: {len(decrypted)}")
        
        # 驗證
        is_match = decrypted == test_secret
        
        return {
            "success": True,
            "original_text": test_secret,
            "original_length": len(test_secret),
            "encrypted_text": encrypted[:50] + "..." if len(encrypted) > 50 else encrypted,
            "encrypted_length": len(encrypted),
            "decrypted_text": decrypted,
            "decrypted_length": len(decrypted),
            "verification": {
                "match": is_match,
                "encryption_adds_overhead": len(encrypted) > len(test_secret),
                "roundtrip_successful": is_match
            }
        }
        
    except Exception as e:
        logger.error(f"測試加密流程失敗: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"測試失敗: {str(e)}")


@router.post("/trigger-master-order", response_model=Dict[str, Any])
async def trigger_master_order(
    master_user_id: int = 1,
    master_credential_id: int = 1,
    symbol: str = "BTC/USDT",
    position_size: float = 1.0,
    entry_price: float = 50000.0,
    db: AsyncSession = Depends(get_db),
    credential_service: CredentialService = Depends(get_credential_service)
):
    """
    觸發 Master 訂單（測試用）
    
    此接口用於手動模擬 Master 發出訊號，方便測試跟單引擎
    會立即更新 Master 倉位，跟單引擎將在下一個輪詢週期（最多 3 秒）檢測並執行跟單
    
    自動創建測試憑證：如果指定的 master_credential_id 不存在，會自動創建一個測試憑證
    
    Args:
        master_user_id: Master 用戶 ID
        master_credential_id: Master 憑證 ID
        symbol: 交易對
        position_size: 倉位大小（正數=多倉，負數=空倉，0=平倉）
        entry_price: 開倉價格
        
    Returns:
        操作結果和預期的跟單資訊
    """
    try:
        from backend.app.models.master_position import MasterPosition
        from backend.app.models.follow_relationship import FollowRelationship
        from backend.app.models.follow_settings import FollowSettings
        from backend.app.models.api_credential import ApiCredential
        from sqlalchemy import select, and_
        from datetime import datetime
        
        # 步驟 1: 檢查憑證是否存在，如果不存在則自動創建
        credential_check = await db.execute(
            select(ApiCredential).where(ApiCredential.id == master_credential_id)
        )
        existing_credential = credential_check.scalar_one_or_none()
        
        credential_auto_created = False
        if not existing_credential:
            logger.info(
                f"⚠️ 憑證 ID {master_credential_id} 不存在，自動創建測試憑證..."
            )
            
            # 自動創建測試憑證（使用 Mock Exchange）
            try:
                test_credential = await credential_service.create_credential(
                    user_id=master_user_id,
                    exchange_name="mock",
                    api_key=f"test_master_key_{master_user_id}_{master_credential_id}",
                    api_secret=f"test_master_secret_{master_user_id}_{master_credential_id}",
                    passphrase=None,
                    verify=False  # 跳過驗證，因為這是測試憑證
                )
                
                # 如果創建的憑證 ID 與請求的不同，需要更新
                if test_credential.id != master_credential_id:
                    logger.warning(
                        f"⚠️ 自動創建的憑證 ID ({test_credential.id}) 與請求的 ID ({master_credential_id}) 不同"
                    )
                    # 使用實際創建的憑證 ID
                    master_credential_id = test_credential.id
                
                credential_auto_created = True
                logger.info(
                    f"✅ 自動創建測試憑證成功 - ID: {test_credential.id}, "
                    f"Exchange: {test_credential.exchange_name}"
                )
                
            except Exception as e:
                logger.error(f"❌ 自動創建測試憑證失敗: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"無法創建測試憑證: {str(e)}"
                )
        
        # 步驟 2: 更新或創建 Master 倉位
        result = await db.execute(
            select(MasterPosition).where(
                and_(
                    MasterPosition.master_user_id == master_user_id,
                    MasterPosition.master_credential_id == master_credential_id,
                    MasterPosition.symbol == symbol
                )
            )
        )
        position = result.scalar_one_or_none()
        
        if position:
            old_size = position.position_size
            position.position_size = position_size
            if entry_price is not None:
                position.entry_price = entry_price
            position.last_updated = datetime.utcnow()
        else:
            old_size = 0
            position = MasterPosition(
                master_user_id=master_user_id,
                master_credential_id=master_credential_id,
                symbol=symbol,
                position_size=position_size,
                entry_price=entry_price
            )
            db.add(position)
        
        await db.commit()
        await db.refresh(position)
        
        # 查詢有多少跟隨者（舊版 FollowRelationship）
        result = await db.execute(
            select(FollowRelationship).where(
                and_(
                    FollowRelationship.master_user_id == master_user_id,
                    FollowRelationship.master_credential_id == master_credential_id,
                    FollowRelationship.is_active == True
                )
            )
        )
        old_followers = result.scalars().all()
        
        # 查詢新版 FollowSettings 的跟隨者
        result = await db.execute(
            select(FollowSettings).where(
                and_(
                    FollowSettings.master_user_id == master_user_id,
                    FollowSettings.master_credential_id == master_credential_id,
                    FollowSettings.is_active == True
                )
            )
        )
        new_followers = result.scalars().all()
        
        # 計算預期的跟單資訊
        expected_trades = []
        
        # 舊版跟隨者
        for follower in old_followers:
            follower_amount = abs(position_size) * follower.follow_ratio
            expected_trades.append({
                "follower_user_id": follower.follower_user_id,
                "follow_ratio": follower.follow_ratio,
                "expected_amount": follower_amount,
                "side": "buy" if position_size > 0 else ("sell" if position_size < 0 else "close"),
                "version": "v1"
            })
        
        # 新版跟隨者（FollowSettings）
        for follower in new_followers:
            follower_amount = abs(position_size) * follower.follow_ratio
            expected_trades.append({
                "follower_user_id": follower.user_id,
                "follow_ratio": follower.follow_ratio,
                "expected_amount": follower_amount,
                "side": "buy" if position_size > 0 else ("sell" if position_size < 0 else "close"),
                "version": "v2"
            })
        
        total_followers = len(old_followers) + len(new_followers)
        
        logger.info(
            f"✨ 觸發 Master 訂單 - "
            f"用戶: {master_user_id}, "
            f"交易對: {symbol}, "
            f"倉位變動: {old_size} -> {position_size}, "
            f"跟隨者數量: {total_followers} (v1: {len(old_followers)}, v2: {len(new_followers)})"
        )
        
        return {
            "success": True,
            "message": "Master 訂單已觸發，儀表板數據將在 3 秒內更新",
            "credential_info": {
                "credential_id": master_credential_id,
                "auto_created": credential_auto_created,
                "note": "測試憑證已自動創建" if credential_auto_created else "使用現有憑證"
            },
            "master_info": {
                "user_id": master_user_id,
                "credential_id": master_credential_id,
                "symbol": symbol,
                "old_position_size": old_size,
                "new_position_size": position_size,
                "entry_price": entry_price,
                "position_changed": old_size != position_size,
                "last_updated": position.last_updated.isoformat()
            },
            "followers_count": total_followers,
            "followers_breakdown": {
                "v1_followers": len(old_followers),
                "v2_followers": len(new_followers)
            },
            "expected_trades": expected_trades,
            "dashboard_update": {
                "note": "儀表板 API (GET /api/v1/dashboard/summary) 將立即反映 Master 倉位變動",
                "follower_positions_update": "跟單引擎將在下一個輪詢週期（最多 3 秒）執行對帳並更新跟隨者倉位",
                "polling_interval": "3 秒"
            }
        }
        
    except Exception as e:
        logger.error(f"觸發 Master 訂單失敗: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"觸發失敗: {str(e)}")
