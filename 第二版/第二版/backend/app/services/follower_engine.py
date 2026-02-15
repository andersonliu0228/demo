"""
Follower Engine Service (Signal Dispatcher)
跟單核心引擎 - 監控 Master 倉位並自動執行跟單
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.app.models.follow_relationship import FollowRelationship
from backend.app.models.master_position import MasterPosition
from backend.app.models.trade_history import TradeHistory
from backend.app.models.trade_log import TradeLog
from backend.app.services.credential_service import CredentialService
from backend.app.services.exchange_service import MockExchange

logger = logging.getLogger(__name__)


class FollowerEngine:
    """跟單核心引擎 (Signal Dispatcher)"""
    
    def __init__(
        self,
        db: AsyncSession,
        credential_service: CredentialService,
        poll_interval: int = 3  # 改為 3 秒輪詢
    ):
        """
        初始化跟單引擎
        
        Args:
            db: 資料庫 session
            credential_service: 憑證服務
            poll_interval: 輪詢間隔（秒），預設 3 秒
        """
        self.db = db
        self.credential_service = credential_service
        self.poll_interval = poll_interval
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        
        # 追蹤上次檢查的倉位狀態（用於檢測變動）
        self._last_positions: Dict[Tuple[int, int, str], float] = {}
        
        logger.info(f"Follower Engine 初始化完成，輪詢間隔: {poll_interval} 秒")
    
    async def start(self):
        """啟動監控引擎"""
        if self.is_running:
            logger.warning("Follower Engine 已經在運行中")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Follower Engine 已啟動，輪詢間隔: {self.poll_interval} 秒")
    
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
        logger.info("Follower Engine 已停止")
    
    async def _monitoring_loop(self):
        """
        監控循環 (Monitoring Loop)
        每 3 秒檢查一次 Master 的持倉狀況
        """
        logger.info("監控循環已啟動")
        
        while self.is_running:
            try:
                loop_start = datetime.utcnow()
                logger.debug(f"[{loop_start.strftime('%H:%M:%S')}] 開始新一輪監控檢查")
                
                # 執行跟單檢查
                await self._check_and_follow_positions()
                
                loop_end = datetime.utcnow()
                duration = (loop_end - loop_start).total_seconds()
                logger.debug(f"本輪監控完成，耗時: {duration:.2f} 秒")
                
            except Exception as e:
                logger.error(f"監控循環發生錯誤: {str(e)}", exc_info=True)
            
            # 等待下一輪
            await asyncio.sleep(self.poll_interval)
    
    async def _check_and_follow_positions(self):
        """
        檢查並執行跟單
        核心跟單邏輯 (Copy Logic)
        """
        # 獲取所有啟用的跟隨關係
        result = await self.db.execute(
            select(FollowRelationship).where(FollowRelationship.is_active == True)
        )
        relationships = result.scalars().all()
        
        if not relationships:
            logger.debug("沒有啟用的跟隨關係")
            return
        
        logger.info(f"檢查 {len(relationships)} 個跟隨關係")
        
        # 按 Master 分組處理
        master_groups: Dict[Tuple[int, int], List[FollowRelationship]] = {}
        for rel in relationships:
            key = (rel.master_user_id, rel.master_credential_id)
            if key not in master_groups:
                master_groups[key] = []
            master_groups[key].append(rel)
        
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
        followers: List[FollowRelationship]
    ):
        """
        處理單個 Master 的所有倉位
        
        Args:
            master_user_id: Master 用戶 ID
            master_credential_id: Master 憑證 ID
            followers: 該 Master 的所有跟隨者
        """
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
                # 首次檢測到此倉位
                logger.info(
                    f"首次檢測到 Master {master_user_id} 的倉位: "
                    f"{position.symbol} = {current_size}"
                )
                self._last_positions[position_key] = current_size
                
                # 如果倉位不為 0，執行跟單
                if current_size != 0:
                    await self._dispatch_signal_to_followers(position, followers)
                    
            elif last_size != current_size:
                # 倉位發生變動
                logger.info(
                    f"檢測到 Master {master_user_id} 倉位變動: "
                    f"{position.symbol} {last_size} -> {current_size}"
                )
                self._last_positions[position_key] = current_size
                
                # 執行跟單
                await self._dispatch_signal_to_followers(position, followers)
            else:
                # 倉位無變動
                logger.debug(
                    f"Master {master_user_id} 倉位無變動: "
                    f"{position.symbol} = {current_size}"
                )
    
    async def _dispatch_signal_to_followers(
        self,
        master_position: MasterPosition,
        followers: List[FollowRelationship]
    ):
        """
        分發信號給所有跟隨者 (Signal Dispatcher)
        
        Args:
            master_position: Master 的倉位
            followers: 所有跟隨者
        """
        logger.info(
            f"分發信號給 {len(followers)} 個跟隨者 - "
            f"交易對: {master_position.symbol}, "
            f"Master 倉位: {master_position.position_size}"
        )
        
        # 並行處理所有跟隨者
        tasks = []
        for follower in followers:
            task = self._execute_follower_trade(follower, master_position)
            tasks.append(task)
        
        # 等待所有跟單完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 統計結果
        success_count = sum(1 for r in results if r is True)
        failed_count = sum(1 for r in results if isinstance(r, Exception))
        
        logger.info(
            f"跟單完成 - 成功: {success_count}, 失敗: {failed_count}"
        )
    
    async def _execute_follower_trade(
        self,
        relationship: FollowRelationship,
        master_position: MasterPosition
    ) -> bool:
        """
        執行跟隨者交易 (同步下單)
        包含完整的 try-except 保護和滑價預估
        
        Args:
            relationship: 跟隨關係
            master_position: Master 倉位
            
        Returns:
            bool: 是否成功
        """
        start_time = datetime.utcnow()
        
        # 計算跟隨者應有的倉位大小（Position Sizing）
        follower_amount = abs(master_position.position_size) * relationship.follow_ratio
        
        # 計算預估滑價（簡單模型：0.05% - 0.15%）
        # 實際應用中可根據市場深度、交易量等因素動態計算
        estimated_slippage = 0.001 * (1 + follower_amount * 0.1)  # 0.1% - 0.2%
        
        # 判斷方向和動作
        if master_position.position_size > 0:
            side = "buy"
            master_action = "open_long"
            follower_action = "follow_long"
        elif master_position.position_size < 0:
            side = "sell"
            master_action = "open_short"
            follower_action = "follow_short"
        else:
            side = "close"
            master_action = "close_position"
            follower_action = "follow_close"
        
        logger.info(
            f"[跟隨者 {relationship.follower_user_id}] 準備跟單 - "
            f"關係ID: {relationship.id}, "
            f"交易對: {master_position.symbol}, "
            f"Master動作: {master_action}, "
            f"跟隨動作: {follower_action}, "
            f"Master倉位: {master_position.position_size}, "
            f"跟隨比例: {relationship.follow_ratio}, "
            f"跟隨數量: {follower_amount}, "
            f"預估滑價: {estimated_slippage*100:.3f}%"
        )
        
        # 創建交易歷史記錄（pending 狀態）
        trade = TradeHistory(
            follow_relationship_id=relationship.id,
            symbol=master_position.symbol,
            side=side,
            order_type="market",
            amount=follower_amount,
            price=master_position.entry_price,
            follow_ratio=relationship.follow_ratio,
            estimated_slippage=estimated_slippage,
            master_position_size=master_position.position_size,
            status="pending"
        )
        self.db.add(trade)
        await self.db.commit()
        await self.db.refresh(trade)
        
        # 初始化 trade_log
        trade_log = TradeLog(
            timestamp=start_time,
            master_user_id=master_position.master_user_id,
            master_credential_id=master_position.master_credential_id,
            master_action=master_action,
            master_symbol=master_position.symbol,
            master_position_size=master_position.position_size,
            master_entry_price=master_position.entry_price,
            follower_user_id=relationship.follower_user_id,
            follower_credential_id=relationship.follower_credential_id,
            follower_action=follower_action,
            follower_ratio=relationship.follow_ratio,
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
            logger.debug(f"[跟隨者 {relationship.follower_user_id}] 獲取解密憑證...")
            decrypted_cred = await self.credential_service.get_decrypted_credential(
                credential_id=relationship.follower_credential_id,
                user_id=relationship.follower_user_id
            )
            
            if not decrypted_cred:
                raise Exception("無法獲取跟隨者憑證")
            
            logger.debug(f"[跟隨者 {relationship.follower_user_id}] 憑證解密成功")
            
            # 創建 MockExchange 實例
            logger.debug(f"[跟隨者 {relationship.follower_user_id}] 創建 MockExchange 實例...")
            exchange = MockExchange(
                api_key=decrypted_cred['api_key'],
                api_secret=decrypted_cred['api_secret'],
                passphrase=decrypted_cred.get('passphrase')
            )
            
            # 執行下單（同步下單）
            logger.info(f"[跟隨者 {relationship.follower_user_id}] 執行下單...")
            order = exchange.create_order(
                symbol=master_position.symbol,
                order_type="market",
                side=side,
                amount=follower_amount,
                price=None  # market 單不需要價格
            )
            
            # 計算實際成交價格（模擬滑價影響）
            if master_position.entry_price:
                if side == "buy":
                    actual_fill_price = master_position.entry_price * (1 + estimated_slippage)
                else:
                    actual_fill_price = master_position.entry_price * (1 - estimated_slippage)
            else:
                actual_fill_price = None
            
            # 計算執行時間
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新交易記錄為成功
            trade.order_id = order['id']
            trade.status = "filled"
            trade.executed_at = end_time
            trade.actual_fill_price = actual_fill_price
            
            # 更新 trade_log 為成功
            trade_log.order_id = order['id']
            trade_log.status = "success"
            trade_log.is_success = True
            trade_log.execution_time_ms = execution_time_ms
            
            await self.db.commit()
            
            logger.info(
                f"[跟隨者 {relationship.follower_user_id}] 跟單成功 - "
                f"訂單ID: {order['id']}, "
                f"交易對: {master_position.symbol}, "
                f"數量: {follower_amount}, "
                f"預估價格: {master_position.entry_price}, "
                f"實際成交: {actual_fill_price}, "
                f"滑價: {estimated_slippage*100:.3f}%, "
                f"耗時: {execution_time_ms}ms"
            )
            
            return True
            
        except Exception as e:
            # 計算執行時間
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 更新交易記錄為失敗
            trade.status = "failed"
            trade.error_message = str(e)
            
            # 更新 trade_log 為失敗
            trade_log.status = "failed"
            trade_log.is_success = False
            trade_log.error_message = str(e)
            trade_log.execution_time_ms = execution_time_ms
            
            await self.db.commit()
            
            logger.error(
                f"[跟隨者 {relationship.follower_user_id}] 跟單失敗 - "
                f"錯誤: {str(e)}, "
                f"耗時: {execution_time_ms}ms",
                exc_info=True
            )
            
            return False
    
    async def update_master_position(
        self,
        master_user_id: int,
        master_credential_id: int,
        symbol: str,
        position_size: float,
        entry_price: Optional[float] = None
    ):
        """
        更新 Master 倉位
        
        Args:
            master_user_id: Master 用戶 ID
            master_credential_id: Master 憑證 ID
            symbol: 交易對
            position_size: 倉位大小（正數=多倉，負數=空倉，0=無倉位）
            entry_price: 開倉價格
        """
        # 查找現有倉位
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
            # 更新現有倉位
            position.position_size = position_size
            if entry_price is not None:
                position.entry_price = entry_price
            position.last_updated = datetime.utcnow()
        else:
            # 創建新倉位
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
_follower_engine_instance: Optional[FollowerEngine] = None


def get_follower_engine(
    db: AsyncSession,
    credential_service: CredentialService
) -> FollowerEngine:
    """獲取 Follower Engine 單例"""
    global _follower_engine_instance
    if _follower_engine_instance is None:
        _follower_engine_instance = FollowerEngine(
            db=db,
            credential_service=credential_service,
            poll_interval=3  # 3 秒輪詢
        )
    return _follower_engine_instance
