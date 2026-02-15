"""
Notifier Service
通知服務 - 支持 Telegram 等多種通知方式
"""
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram 通知服務
    
    使用 Telegram Bot API 發送通知訊息
    """
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        初始化 Telegram Notifier
        
        Args:
            bot_token: Telegram Bot Token
            chat_id: Telegram Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if not self.enabled:
            logger.warning("Telegram 通知未啟用：缺少 bot_token 或 chat_id")
        else:
            logger.info(f"Telegram 通知已啟用 - Chat ID: {chat_id}")
    
    async def send_message(
        self,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        發送 Telegram 訊息
        
        Args:
            message: 訊息內容
            parse_mode: 解析模式（HTML, Markdown, MarkdownV2）
            disable_notification: 是否靜音通知
            
        Returns:
            是否發送成功
        """
        if not self.enabled:
            logger.debug(f"Telegram 通知未啟用，跳過發送: {message[:50]}...")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"✅ Telegram 訊息發送成功")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Telegram 訊息發送失敗: {response.status} - {error_text}")
                        return False
        
        except asyncio.TimeoutError:
            logger.error("❌ Telegram 訊息發送超時")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram 訊息發送異常: {str(e)}")
            return False
    
    async def send_trade_success(
        self,
        user_id: int,
        username: str,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        order_id: str
    ) -> bool:
        """
        發送交易成功通知
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            symbol: 交易對
            side: 買賣方向
            amount: 數量
            price: 價格
            order_id: 訂單 ID
            
        Returns:
            是否發送成功
        """
        side_emoji = "🟢" if side.lower() == "buy" else "🔴"
        
        message = f"""
{side_emoji} <b>交易成功通知</b>

👤 用戶: {username} (ID: {user_id})
📊 交易對: <b>{symbol}</b>
📈 方向: <b>{side.upper()}</b>
💰 數量: <b>{amount}</b>
💵 價格: <b>${price:,.2f}</b>
🆔 訂單: <code>{order_id}</code>

⏰ 時間: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        return await self.send_message(message.strip())
    
    async def send_reconciliation_alert(
        self,
        user_id: int,
        username: str,
        symbol: str,
        master_size: float,
        follower_size: float,
        target_size: float,
        action: str
    ) -> bool:
        """
        發送對帳補單通知
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            symbol: 交易對
            master_size: Master 倉位
            follower_size: Follower 當前倉位
            target_size: Follower 目標倉位
            action: 執行動作
            
        Returns:
            是否發送成功
        """
        message = f"""
⚠️ <b>對帳補單通知</b>

👤 用戶: {username} (ID: {user_id})
📊 交易對: <b>{symbol}</b>

📍 Master 倉位: <b>{master_size}</b>
📍 Follower 當前: <b>{follower_size}</b>
🎯 Follower 目標: <b>{target_size}</b>

🔧 執行動作: <b>{action}</b>

⏰ 時間: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        return await self.send_message(message.strip())
    
    async def send_error_alert(
        self,
        user_id: int,
        username: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        發送錯誤警告通知
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 額外上下文資訊
            
        Returns:
            是否發送成功
        """
        context_str = ""
        if context:
            context_str = "\n\n📋 詳細資訊:\n"
            for key, value in context.items():
                context_str += f"  • {key}: {value}\n"
        
        message = f"""
🚨 <b>錯誤警告</b>

👤 用戶: {username} (ID: {user_id})
❌ 錯誤類型: <b>{error_type}</b>

💬 錯誤訊息:
<code>{error_message}</code>
{context_str}
⏰ 時間: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        return await self.send_message(message.strip())
    
    async def send_daily_summary(
        self,
        user_id: int,
        username: str,
        total_value: float,
        daily_pnl: float,
        daily_pnl_percent: float,
        position_count: int
    ) -> bool:
        """
        發送每日摘要通知
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            total_value: 總持倉價值
            daily_pnl: 每日盈虧
            daily_pnl_percent: 每日盈虧百分比
            position_count: 持倉數量
            
        Returns:
            是否發送成功
        """
        pnl_emoji = "📈" if daily_pnl >= 0 else "📉"
        pnl_sign = "+" if daily_pnl >= 0 else ""
        
        message = f"""
📊 <b>每日摘要報告</b>

👤 用戶: {username} (ID: {user_id})

💰 總持倉價值: <b>${total_value:,.2f}</b>
{pnl_emoji} 今日盈虧: <b>{pnl_sign}${daily_pnl:,.2f}</b> ({pnl_sign}{daily_pnl_percent:.2f}%)
📦 持倉數量: <b>{position_count}</b>

⏰ 時間: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        return await self.send_message(message.strip())


class NotifierService:
    """
    通知服務統一介面
    
    支持多種通知方式（Telegram, Email, Webhook 等）
    """
    
    def __init__(
        self,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        """
        初始化 Notifier Service
        
        Args:
            telegram_bot_token: Telegram Bot Token
            telegram_chat_id: Telegram Chat ID
        """
        self.telegram = TelegramNotifier(telegram_bot_token, telegram_chat_id)
        logger.info("NotifierService 初始化完成")
    
    async def notify_trade_success(
        self,
        user_id: int,
        username: str,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        order_id: str
    ) -> None:
        """
        通知交易成功（異步，不阻塞主流程）
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            symbol: 交易對
            side: 買賣方向
            amount: 數量
            price: 價格
            order_id: 訂單 ID
        """
        try:
            await self.telegram.send_trade_success(
                user_id, username, symbol, side, amount, price, order_id
            )
        except Exception as e:
            logger.error(f"發送交易成功通知失敗: {str(e)}")
    
    async def notify_reconciliation(
        self,
        user_id: int,
        username: str,
        symbol: str,
        master_size: float,
        follower_size: float,
        target_size: float,
        action: str
    ) -> None:
        """
        通知對帳補單（異步，不阻塞主流程）
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            symbol: 交易對
            master_size: Master 倉位
            follower_size: Follower 當前倉位
            target_size: Follower 目標倉位
            action: 執行動作
        """
        try:
            await self.telegram.send_reconciliation_alert(
                user_id, username, symbol, master_size, follower_size, target_size, action
            )
        except Exception as e:
            logger.error(f"發送對帳補單通知失敗: {str(e)}")
    
    async def notify_error(
        self,
        user_id: int,
        username: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        通知錯誤警告（異步，不阻塞主流程）
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            error_type: 錯誤類型
            error_message: 錯誤訊息
            context: 額外上下文資訊
        """
        try:
            await self.telegram.send_error_alert(
                user_id, username, error_type, error_message, context
            )
        except Exception as e:
            logger.error(f"發送錯誤警告通知失敗: {str(e)}")
    
    async def notify_daily_summary(
        self,
        user_id: int,
        username: str,
        total_value: float,
        daily_pnl: float,
        daily_pnl_percent: float,
        position_count: int
    ) -> None:
        """
        通知每日摘要（異步，不阻塞主流程）
        
        Args:
            user_id: 用戶 ID
            username: 用戶名
            total_value: 總持倉價值
            daily_pnl: 每日盈虧
            daily_pnl_percent: 每日盈虧百分比
            position_count: 持倉數量
        """
        try:
            await self.telegram.send_daily_summary(
                user_id, username, total_value, daily_pnl, daily_pnl_percent, position_count
            )
        except Exception as e:
            logger.error(f"發送每日摘要通知失敗: {str(e)}")


# 全域實例
_notifier_service_instance: Optional[NotifierService] = None


def get_notifier_service(
    telegram_bot_token: Optional[str] = None,
    telegram_chat_id: Optional[str] = None
) -> NotifierService:
    """
    獲取 NotifierService 單例實例
    
    Args:
        telegram_bot_token: Telegram Bot Token
        telegram_chat_id: Telegram Chat ID
        
    Returns:
        NotifierService 實例
    """
    global _notifier_service_instance
    if _notifier_service_instance is None:
        _notifier_service_instance = NotifierService(telegram_bot_token, telegram_chat_id)
    return _notifier_service_instance
