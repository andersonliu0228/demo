"""
Mock Exchange
模擬交易所 - 用於開發和測試
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.app.services.exchanges.base_exchange import BaseExchange

logger = logging.getLogger(__name__)


class MockExchange(BaseExchange):
    """
    模擬交易所類別
    用於開發和測試，不發起真實網路請求
    繼承 BaseExchange 確保介面一致
    """
    
    def __init__(self, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        """
        初始化 Mock Exchange
        
        Args:
            api_key: API Key（用於驗證加密流程）
            api_secret: API Secret（用於驗證加密流程）
            passphrase: Passphrase（可選）
        """
        super().__init__(api_key, api_secret, passphrase)
        self.id = 'mock'
        
        # 模擬市價數據
        self._mock_prices = {
            'BTC/USDT': 50000.0,
            'ETH/USDT': 3000.0,
            'BNB/USDT': 400.0,
            'SOL/USDT': 100.0
        }
        
        logger.info(f"MockExchange 初始化 - API Key: {api_key[:8]}...")
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        模擬獲取帳戶餘額
        
        Returns:
            模擬的餘額資訊
        """
        logger.info("MockExchange: 執行 fetch_balance()")
        
        return {
            'total': {
                'USDT': 10000.0,
                'BTC': 0.5,
                'ETH': 5.0,
                'BNB': 10.0
            },
            'free': {
                'USDT': 8000.0,
                'BTC': 0.3,
                'ETH': 3.0,
                'BNB': 8.0
            },
            'used': {
                'USDT': 2000.0,
                'BTC': 0.2,
                'ETH': 2.0,
                'BNB': 2.0
            },
            'info': {
                'mock': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        模擬獲取市場行情
        
        Args:
            symbol: 交易對（如 'BTC/USDT'）
            
        Returns:
            模擬的行情資訊
        """
        logger.info(f"MockExchange: 執行 fetch_ticker(symbol={symbol})")
        
        # 獲取模擬價格
        last_price = self._mock_prices.get(symbol, 50000.0)
        
        return {
            'symbol': symbol,
            'last': last_price,
            'bid': last_price * 0.9999,
            'ask': last_price * 1.0001,
            'high': last_price * 1.05,
            'low': last_price * 0.95,
            'volume': 1000.0,
            'timestamp': datetime.utcnow().timestamp() * 1000,
            'datetime': datetime.utcnow().isoformat(),
            'info': {'mock': True}
        }
    
    def fetch_open_orders(self, symbol: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        模擬獲取開放訂單
        
        Args:
            symbol: 交易對（可選）
            limit: 限制數量（可選）
            
        Returns:
            模擬的訂單列表
        """
        logger.info(f"MockExchange: 執行 fetch_open_orders(symbol={symbol}, limit={limit})")
        
        return [
            {
                'id': str(uuid.uuid4()),
                'symbol': symbol or 'BTC/USDT',
                'type': 'limit',
                'side': 'buy',
                'price': 50000.0,
                'amount': 0.1,
                'status': 'open',
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'datetime': datetime.utcnow().isoformat(),
                'info': {'mock': True}
            }
        ]
    
    def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        模擬創建訂單
        
        Args:
            symbol: 交易對（如 'BTC/USDT'）
            order_type: 訂單類型（'market' 或 'limit'）
            side: 買賣方向（'buy' 或 'sell'）
            amount: 數量
            price: 價格（限價單需要）
            params: 額外參數
            
        Returns:
            模擬的訂單回執
        """
        order_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().timestamp() * 1000
        
        # 獲取模擬價格
        mock_price = self._mock_prices.get(symbol, 50000.0)
        execution_price = price if price else mock_price
        
        logger.info(
            f"MockExchange: 執行 create_order(symbol={symbol}, type={order_type}, "
            f"side={side}, amount={amount}, price={price})"
        )
        
        order = {
            'id': order_id,
            'clientOrderId': f"mock_{order_id[:8]}",
            'timestamp': timestamp,
            'datetime': datetime.utcnow().isoformat(),
            'symbol': symbol,
            'type': order_type,
            'side': side,
            'price': execution_price,
            'amount': amount,
            'cost': execution_price * amount,
            'filled': amount,  # 模擬立即成交
            'remaining': 0.0,
            'status': 'closed',
            'fee': {
                'cost': (execution_price * amount) * 0.001,  # 0.1% 手續費
                'currency': 'USDT'
            },
            'trades': [],
            'info': {
                'mock': True,
                'api_key_used': self.api_key[:8] + '...',
                'decrypted_secret_length': len(self.api_secret)
            }
        }
        
        return order
    
    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        模擬獲取持倉
        
        Args:
            symbols: 交易對列表（可選）
            
        Returns:
            模擬的持倉列表
        """
        logger.info(f"MockExchange: 執行 fetch_positions(symbols={symbols})")
        
        positions = [
            {
                'symbol': 'BTC/USDT',
                'side': 'long',
                'contracts': 0.5,
                'contractSize': 1,
                'entryPrice': 48000.0,
                'markPrice': 50000.0,
                'notional': 25000.0,
                'leverage': 10,
                'unrealizedPnl': 1000.0,
                'percentage': 4.17,
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'datetime': datetime.utcnow().isoformat(),
                'info': {'mock': True}
            }
        ]
        
        if symbols:
            positions = [p for p in positions if p['symbol'] in symbols]
        
        return positions
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        模擬取消訂單
        
        Args:
            order_id: 訂單 ID
            symbol: 交易對
            
        Returns:
            模擬的取消結果
        """
        logger.info(f"MockExchange: 執行 cancel_order(order_id={order_id}, symbol={symbol})")
        
        return {
            'id': order_id,
            'symbol': symbol,
            'status': 'canceled',
            'timestamp': datetime.utcnow().timestamp() * 1000,
            'datetime': datetime.utcnow().isoformat(),
            'info': {'mock': True}
        }
    
    def set_mock_price(self, symbol: str, price: float):
        """
        設定模擬價格（測試用）
        
        Args:
            symbol: 交易對
            price: 價格
        """
        self._mock_prices[symbol] = price
        logger.info(f"MockExchange: 設定 {symbol} 模擬價格為 {price}")
    
    def get_mock_price(self, symbol: str) -> float:
        """
        獲取模擬價格
        
        Args:
            symbol: 交易對
            
        Returns:
            模擬價格
        """
        return self._mock_prices.get(symbol, 50000.0)
