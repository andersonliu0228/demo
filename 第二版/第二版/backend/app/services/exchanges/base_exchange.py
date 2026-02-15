"""
Base Exchange
交易所抽象基類 - 定義統一介面
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseExchange(ABC):
    """
    交易所抽象基類
    
    所有交易所實作必須繼承此類並實作所有抽象方法
    確保切換交易所時核心邏輯不需改動
    """
    
    def __init__(self, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        """
        初始化交易所
        
        Args:
            api_key: API Key
            api_secret: API Secret
            passphrase: Passphrase（某些交易所需要，如 OKX）
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.id = 'base'
    
    @abstractmethod
    def fetch_balance(self) -> Dict[str, Any]:
        """
        獲取帳戶餘額
        
        Returns:
            {
                'total': {'USDT': 10000.0, 'BTC': 0.5, ...},
                'free': {'USDT': 8000.0, 'BTC': 0.3, ...},
                'used': {'USDT': 2000.0, 'BTC': 0.2, ...},
                'info': {...}
            }
        """
        pass
    
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        獲取市場行情（當前價格）
        
        Args:
            symbol: 交易對（如 'BTC/USDT'）
            
        Returns:
            {
                'symbol': 'BTC/USDT',
                'last': 50000.0,
                'bid': 49999.0,
                'ask': 50001.0,
                'high': 51000.0,
                'low': 49000.0,
                'volume': 1000.0,
                'timestamp': 1234567890000
            }
        """
        pass
    
    @abstractmethod
    def fetch_open_orders(self, symbol: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        獲取開放訂單
        
        Args:
            symbol: 交易對（可選）
            limit: 限制數量（可選）
            
        Returns:
            [
                {
                    'id': 'order_id',
                    'symbol': 'BTC/USDT',
                    'type': 'limit',
                    'side': 'buy',
                    'price': 50000.0,
                    'amount': 0.1,
                    'status': 'open',
                    'timestamp': 1234567890000
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
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
        創建訂單
        
        Args:
            symbol: 交易對（如 'BTC/USDT'）
            order_type: 訂單類型（'market' 或 'limit'）
            side: 買賣方向（'buy' 或 'sell'）
            amount: 數量
            price: 價格（限價單需要）
            params: 額外參數（可選）
            
        Returns:
            {
                'id': 'order_id',
                'clientOrderId': 'client_order_id',
                'timestamp': 1234567890000,
                'datetime': '2024-01-01T00:00:00.000Z',
                'symbol': 'BTC/USDT',
                'type': 'market',
                'side': 'buy',
                'price': 50000.0,
                'amount': 0.1,
                'cost': 5000.0,
                'filled': 0.1,
                'remaining': 0.0,
                'status': 'closed',
                'fee': {'cost': 5.0, 'currency': 'USDT'},
                'trades': [],
                'info': {...}
            }
        """
        pass
    
    @abstractmethod
    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        獲取持倉
        
        Args:
            symbols: 交易對列表（可選）
            
        Returns:
            [
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
                    'timestamp': 1234567890000
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        取消訂單
        
        Args:
            order_id: 訂單 ID
            symbol: 交易對
            
        Returns:
            {
                'id': 'order_id',
                'symbol': 'BTC/USDT',
                'status': 'canceled',
                'info': {...}
            }
        """
        pass
    
    def get_exchange_id(self) -> str:
        """
        獲取交易所 ID
        
        Returns:
            交易所 ID（如 'mock', 'binance', 'okx'）
        """
        return self.id
