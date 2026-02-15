"""
Follower Engine Service V2 (使用 FollowSettings)
跟單核心引擎 - 監控 Master 倉位並自動執行跟單
支援用戶級別的跟單配置和錯誤處理
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.app.models.follow_settings import FollowSettings
from backend.app.models.master_position import MasterPosition
from backend.app.models.follower_position import FollowerPosition
from backend.app.models.trade_history import TradeHistory
from backend.app.models.trade_log import TradeLog
from backend.app.models.trade_error import TradeError
from backend.app.models.user import User
from backend.app.services.credential_service import CredentialService
from backend.app.services.exchanges.mock_exchange import MockExchange
from backend.app.repositories.trade_error_repository import TradeErrorRepository
from backend.app.repositories.follower_position_repository import FollowerPositionRepository
from backend.app.services.notifier import get_notifier_service

logger = logging.getLogger(__name__)


class FollowerEngineV2:
    """跟單核心引擎 V2 (使用 FollowSettings)"""
    
    def __init__(
        self,
        db: AsyncSession,
        credential_service: CredentialService,
        poll_interval: int = 3,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        """
        初始化跟單引擎
        
        Args:
            db: 資料庫 session
            credential_service: 憑證服務
            poll_interval: 輪詢間隔（秒），預設 3 秒
            telegram_bot_token: Telegram Bot Token（可選）
            telegram_chat_id: Telegram Chat ID（可選）
        """
        self.db = db
        self.credential_service = credential_service
        self.poll_interval = poll_interval
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        
        # 初始化通知服務
        self.notifier = get_notifier_service(telegram_bot_token, telegram_chat_id)
        
        # 追蹤上次檢查的倉位狀態
        self._last_positions: Dict[Tuple[int, int, str], float] = {}
        
        logger.info(f"Follower Engine V2 初始化完成，輪詢間隔: {poll_interval} 秒")
        if telegram_bot_token and telegram_chat_id:
            logger.info("Telegram 通知已啟用")
        else:
            logger.info("Telegram 通知未啟用")
    
    async def start(self):
        """啟動監控引擎"""
        if self.is_running:
            logger.warning("Follower Engine V2 已經在運行中")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Follower Engine V2 已啟動")
    
    async def stop(self):
        """停止監控引擎"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Follower Engine V2 已停止")
    
    async def _monitoring_loop(self):
        """監控循環"""
        logger.info("監控循環已啟動")
        
        while self.is_running:
            try:
                loop_start = datetime.utcnow()
                logger.debug(f"[{loop_start.strftime('%H:%M:%S')}] 開始新一輪監控檢查")
                
                await self._check_and_follow_positions()
                
                loop_end = datetime.utcnow()
                duration = (loop_end - loop_start).total_seconds()
                logger.debug(f"本輪監控完成，耗時: {duration:.2f} 秒")
                
            except Exception as e:
                logger.error(f"監控循環發生錯誤: {str(e)}", exc_info=True)
            
            await asyncio.sleep(self.poll_interval)
    
    async def _check_and_follow_positions(self):
        """檢查並執行跟單"""
        # 獲取所有啟用的跟單設定
        result = await self.db.execute(
            select(FollowSettings).where(FollowSettings.is_active == True)
        )
        settings_list = result.scalars().all()
        
        if not settings_list:
            logger.debug("沒有啟用的跟單設定")
            return
        
        logger.info(f"檢查 {len(settings_list)} 個跟單設定")
        
        # 按 Master 分組處理
        master_groups: Dict[Tuple[int, int], List[FollowSettings]] = {}
        for settings in settings_list:
            key = (settings.master_user_id, settings.master_credential_id)
            if key not in master_groups:
                master_groups[key] = []
            master_groups[key].append(settings)
        
        # 處理每個 Master 的倉位
        for (master_user_id, master_credential_id), followers in master_groups.items():
            try:
                await self._process_master_positions(
                    master_user_id,
                    master_credential_id,
                    followers
                )
            except Exception as e:
                logger.error(
                    f"處理 Master {master_user_id} 的倉位時發生錯誤: {str(e)}",
                    exc_info=True
                )
    
    async def _process_master_positions(
        self,
        master_user_id: int,
        master_credential_id: int,
        followers: List[FollowSettings]
    ):
        """處理單個 Master 的所有倉位"""
        # 獲取 Master 的所有倉位
        result = await self.db.execute(
            select(MasterPosition).where(
                and_(
                    MasterPosition.master_user_id == master_user_id,
                    MasterPosition.master_credential_id == master_credential_id
                )
            )
        )
        master_positions = result.scalars().all()
        
        if not master_positions:
            logger.debug(f"Master {master_user_id} 沒有倉位")
            return
        
        logger.info(f"Master {master_user_id} 有 {len(master_positions)} 個倉位")
        
        # 檢查每個倉位是否有變動
        for position in master_positions:
            position_key = (master_user_id, master_credential_id, position.symbol)
            last_size = self._last_positions.get(position_key, None)
            current_size = position.position_size
            
            # 檢測倉位變動
            if last_size is None:
                logger.info(
                    f"首次檢測到 Master {master_user_id} 的倉位: "
                    f"{position.symbol} = {current_size}"
                )
                self._last_positions[position_key] = current_size
                
                if current_size != 0:
                    await self._dispatch_signal_to_followers(position, followers)
                    
            elif last_size != current_size:
                logger.info(
                    f"檢測到 Master {master_user_id} 倉位變動: "
                    f"{position.symbol} {last_size} -> {current_size}"
                )
                self._last_positions[position_key] = current_size
                await self._dispatch_signal_to_followers(position, followers)
    
    async def _dispatch_signal_to_followers(
        self,
        master_position: MasterPosition,
        followers: List[FollowSettings]
    ):
        """分發信號給所有跟隨者"""
        logger.info(
            f"分發信號給 {len(followers)} 個跟隨者 - "
            f"交易對: {master_position.symbol}, "
            f"Master 倉位: {master_position.position_size}"
        )
        
        # 並行處理所有跟隨者
        tasks = []
        for follower_settings in followers:
            task = self._execute_follower_trade(follower_settings, master_position)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        failed_count = sum(1 for r in results if isinstance(r, Exception) or r is False)
        
        logger.info(f"跟單完成 - 成功: {success_count}, 失敗: {failed_count}")
    
    async def _execute_follower_trade(
        self,
        settings: FollowSettings,
        master_position: MasterPosition
    ) -> bool:
        """
        執行跟隨者交易
        包含錯誤處理和自動停止機制
        """
        start_time = datetime.utcnow()
        error_repo = TradeErrorRepository(self.db)
        position_repo = FollowerPositionRepository(self.db)
        
        # 檢查是否有未解決的錯誤
        has_errors = await error_repo.has_unresolved_errors(settings.user_id)
        if has_errors:
            logger.warning(
                f"[跟隨者 {settings.user_id}] 有未解決的錯誤，跳過本次跟單"
            )
            return False
        
        # 獲取當前跟隨者倉位
        current_position = await position_repo.get_position(
            user_id=settings.user_id,
            credential_id=settings.follower_credential_id,
            symbol=master_position.symbol
        )
        current_size = current_position.position_size if current_position else 0.0
        
        # 計算目標倉位大小（根據 Master 倉位和跟單比例）
        target_size = master_position.position_size * settings.follow_ratio
        
        # 計算需要調整的數量（對帳 Reconciliation）
        size_diff = target_size - current_size
        
        # 如果差異很小（< 0.0001），不需要調整
        if abs(size_diff) < 0.0001:
            logger.debug(
                f"[跟隨者 {settings.user_id}] 倉位已同步，無需調整 - "
                f"當前: {current_size}, 目標: {target_size}"
            )
            return True
        
        # 判斷操作類型
        if size_diff > 0:
            # 需要增加倉位（補單）
            side = "buy"
            action = "補單_增加倉位"
        else:
            # 需要減少倉位（平倉）
            side = "sell"
            action = "平倉_減少倉位"
        
        follower_amount = abs(size_diff)
        
        logger.info(
            f"[跟隨者 {settings.user_id}] 對帳調整 - "
            f"交易對: {master_position.symbol}, "
            f"當前倉位: {current_size}, "
            f"目標倉位: {target_size}, "
            f"調整數量: {size_diff}, "
            f"操作: {action}"
        )
        
        # 計算預估滑價
        estimated_slippage = 0.001 * (1 + follower_amount * 0.1)
        
        # 創建 trade_log
        trade_log = TradeLog(
            timestamp=start_time,
            master_user_id=master_position.master_user_id,
            master_credential_id=master_position.master_credential_id,
            master_action=f"position_{master_position.position_size}",
            master_symbol=master_position.symbol,
            master_position_size=master_position.position_size,
            master_entry_price=master_position.entry_price,
            follower_user_id=settings.user_id,
            follower_credential_id=settings.follower_credential_id,
            follower_action=action,
            follower_ratio=settings.follow_ratio,
            follower_amount=follower_amount,
            order_type="market",
            side=side,
            status="pending",
            is_success=False
        )
        self.db.add(trade_log)
        await self.db.commit()
        await self.db.refresh(trade_log)
        
        try:
            # 獲取跟隨者的解密憑證
            decrypted_cred = await self.credential_service.get_decrypted_credential(
                credential_id=settings.follower_credential_id,
                user_id=settings.user_id
            )
            
            if not decrypted_cred:
                raise Exception("無法獲取跟隨者憑證")
            
            # 創建 MockExchange 實例
            exchange = MockExchange(
                api_key=decrypted_cred['api_key'],
                api_secret=decrypted_cred['api_secret'],
                passphrase=decrypted_cred.get('passphrase')
            )
            
            # 執行下單
            order = exchange.create_order(
                symbol=master_position.symbol,
                order_type="market",
                side=side,
                amount=follower_amount,
                price=None
            )
            
            # 計算執行時間
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新跟隨者倉位
            await position_repo.update_position(
                user_id=settings.user_id,
                credential_id=settings.follower_credential_id,
                symbol=master_position.symbol,
                position_size=target_size,
                entry_price=master_position.entry_price
            )
            
            # 更新 trade_log 為成功
            trade_log.order_id = order['id']
            trade_log.status = "success"
            trade_log.is_success = True
            trade_log.execution_time_ms = execution_time_ms
            
            await self.db.commit()
            
            logger.info(
                f"[跟隨者 {settings.user_id}] 對帳成功 - "
                f"訂單ID: {order['id']}, "
                f"新倉位: {target_size}, "
                f"耗時: {execution_time_ms}ms"
            )
            
            # 發送成功通知（異步，不阻塞主流程）
            asyncio.create_task(
                self._send_trade_success_notification(
                    settings=settings,
                    symbol=master_position.symbol,
                    side=side,
                    amount=follower_amount,
                    price=master_position.entry_price or 0.0,
                    order_id=order['id']
                )
            )
            
            return True
            
        except Exception as e:
            # 計算執行時間
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新 trade_log 為失敗
            trade_log.status = "failed"
            trade_log.is_success = False
            trade_log.error_message = str(e)
            trade_log.execution_time_ms = execution_time_ms
            
            # 創建錯誤記錄
            error_details = {
                "symbol": master_position.symbol,
                "side": side,
                "amount": follower_amount,
                "current_position": current_size,
                "target_position": target_size,
                "master_position": master_position.position_size,
                "follow_ratio": settings.follow_ratio
            }
            
            await error_repo.create(
                user_id=settings.user_id,
                trade_log_id=trade_log.id,
                error_type="exchange_error",
                error_message=str(e),
                error_details=json.dumps(error_details)
            )
            
            # 自動停止該用戶的跟單
            settings.is_active = False
            
            await self.db.commit()
            
            logger.error(
                f"[跟隨者 {settings.user_id}] 對帳失敗，已自動停止跟單 - "
                f"錯誤: {str(e)}, 耗時: {execution_time_ms}ms"
            )
            
            # 發送錯誤通知（異步，不阻塞主流程）
            asyncio.create_task(
                self._send_error_notification(
                    settings=settings,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={
                        "symbol": master_position.symbol,
                        "side": side,
                        "amount": follower_amount,
                        "current_position": current_size,
                        "target_position": target_size
                    }
                )
            )
            
            return False
    
    async def _send_trade_success_notification(
        self,
        settings: FollowSettings,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        order_id: str
    ):
        """
        發送交易成功通知
        
        Args:
            settings: 跟單設定
            symbol: 交易對
            side: 買賣方向
            amount: 數量
            price: 價格
            order_id: 訂單 ID
        """
        try:
            # 獲取用戶資訊
            result = await self.db.execute(
                select(User).where(User.id == settings.user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                await self.notifier.notify_trade_success(
                    user_id=user.id,
                    username=user.username,
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    price=price,
                    order_id=order_id
                )
        except Exception as e:
            logger.error(f"發送交易成功通知失敗: {str(e)}")
    
    async def _send_error_notification(
        self,
        settings: FollowSettings,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ):
        """
        發送錯誤通知
        
        Args:
            settings: 跟單設定
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 上下文資訊
        """
        try:
            # 獲取用戶資訊
            result = await self.db.execute(
                select(User).where(User.id == settings.user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                await self.notifier.notify_error(
                    user_id=user.id,
                    username=user.username,
                    error_type=error_type,
                    error_message=error_message,
                    context=context
                )
        except Exception as e:
            logger.error(f"發送錯誤通知失敗: {str(e)}")
    
    async def update_master_position(
        self,
        master_user_id: int,
        master_credential_id: int,
        symbol: str,
        position_size: float,
        entry_price: Optional[float] = None
    ):
        """更新 Master 倉位"""
        result = await self.db.execute(
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
            position.position_size = position_size
            if entry_price is not None:
                position.entry_price = entry_price
            position.last_updated = datetime.utcnow()
        else:
            position = MasterPosition(
                master_user_id=master_user_id,
                master_credential_id=master_credential_id,
                symbol=symbol,
                position_size=position_size,
                entry_price=entry_price
            )
            self.db.add(position)
        
        await self.db.commit()
        logger.info(
            f"Master 倉位已更新 - 用戶: {master_user_id}, "
            f"交易對: {symbol}, 倉位: {position_size}"
        )


# 全域引擎實例
_follower_engine_v2_instance: Optional[FollowerEngineV2] = None


def get_follower_engine_v2(
    db: AsyncSession,
    credential_service: CredentialService,
    telegram_bot_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None
) -> FollowerEngineV2:
    """獲取 Follower Engine V2 單例"""
    global _follower_engine_v2_instance
    if _follower_engine_v2_instance is None:
        _follower_engine_v2_instance = FollowerEngineV2(
            db=db,
            credential_service=credential_service,
            poll_interval=3,
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id
        )
    return _follower_engine_v2_instance
