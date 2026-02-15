"""
Exchange Service
交易所整合服務（使用 CCXT）
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import ccxt
from ccxt.base.errors import (
    AuthenticationError,
    NetworkError,
    ExchangeError,
    InvalidOrder,
    InsufficientFunds,
    BadRequest
)

from backend.app.services.exchanges.mock_exchange import MockExchange

logger = logging.getLogger(__name__)


class ExchangeService:
    """
    交易所整合服務
    使用 CCXT 函式庫統一介面
    """
    
    # 支援的交易所列表（可以根據需要擴展）
    SUPPORTED_EXCHANGES = [
        'mock',  # Mock 交易所（用於開發測試）
        'binance',
        'okx',
        'bybit',
        'huobi',
        'kucoin',
        'gate',
        'bitget',
        'mexc'
    ]
    
    def __init__(self):
        """初始化 Exchange Service"""
        pass
    
    def _create_exchange_instance(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ):
        """
        創建交易所實例（支援 Mock Exchange）
        
        Args:
            exchange_name: 交易所名稱
            api_key: API Key
            api_secret: API Secret
            passphrase: Passphrase（某些交易所需要）
            
        Returns:
            交易所實例（CCXT 或 MockExchange）
            
        Raises:
            ValueError: 如果交易所不支援
        """
        exchange_name_lower = exchange_name.lower()
        
        if exchange_name_lower not in self.SUPPORTED_EXCHANGES:
            raise ValueError(f"不支援的交易所: {exchange_name}")
        
        # 如果是 Mock Exchange，返回 MockExchange 實例
        if exchange_name_lower == 'mock':
            logger.info("創建 MockExchange 實例（開發模式）")
            return MockExchange(api_key, api_secret, passphrase)
        
        # 獲取真實交易所類別
        exchange_class = getattr(ccxt, exchange_name_lower)
        
        # 配置參數
        config = {
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'timeout': 30000,  # 30 秒超時
        }
        
        # 某些交易所需要 passphrase（如 OKX）
        if passphrase:
            config['password'] = passphrase
        
        return exchange_class(config)
    
    async def verify_credentials(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        驗證 API 憑證是否有效且具備交易權限
        
        Args:
            exchange_name: 交易所名稱（如 'binance', 'okx'）
            api_key: API Key
            api_secret: API Secret
            passphrase: API Passphrase（某些交易所需要）
            
        Returns:
            驗證結果字典，包含：
            - is_valid: bool - 憑證是否有效
            - has_trading_permission: bool - 是否具備交易權限
            - account_info: dict - 帳戶基本資訊（如有）
            - error_message: str - 錯誤訊息（如有）
        """
        try:
            # 創建交易所實例
            exchange = self._create_exchange_instance(
                exchange_name, api_key, api_secret, passphrase
            )
            
            # 嘗試獲取帳戶餘額（驗證憑證有效性）
            balance = await self._fetch_balance_async(exchange)
            
            # 檢查交易權限（嘗試獲取 API 權限資訊）
            has_trading_permission = await self._check_trading_permission(exchange)
            
            # 提取帳戶基本資訊
            account_info = {
                'exchange': exchange_name,
                'total_balance_usd': self._calculate_total_balance_usd(balance),
                'currencies': list(balance.get('total', {}).keys())[:10]  # 只返回前 10 個幣種
            }
            
            return {
                'is_valid': True,
                'has_trading_permission': has_trading_permission,
                'account_info': account_info,
                'error_message': None
            }
            
        except AuthenticationError as e:
            logger.warning(f"憑證驗證失敗 ({exchange_name}): {str(e)}")
            return {
                'is_valid': False,
                'has_trading_permission': False,
                'account_info': None,
                'error_message': f"認證失敗：API Key 或 Secret 無效"
            }
        
        except NetworkError as e:
            logger.error(f"網路錯誤 ({exchange_name}): {str(e)}")
            return {
                'is_valid': False,
                'has_trading_permission': False,
                'account_info': None,
                'error_message': f"網路連接錯誤，請稍後重試"
            }
        
        except ValueError as e:
            logger.error(f"交易所不支援: {str(e)}")
            return {
                'is_valid': False,
                'has_trading_permission': False,
                'account_info': None,
                'error_message': str(e)
            }
        
        except Exception as e:
            logger.error(f"驗證憑證時發生未預期錯誤 ({exchange_name}): {str(e)}")
            return {
                'is_valid': False,
                'has_trading_permission': False,
                'account_info': None,
                'error_message': f"驗證失敗：{str(e)}"
            }
    
    async def _fetch_balance_async(self, exchange) -> Dict:
        """
        異步獲取帳戶餘額（支援 Mock Exchange）
        
        Args:
            exchange: 交易所實例（CCXT 或 MockExchange）
            
        Returns:
            餘額資訊
        """
        try:
            # MockExchange 和 CCXT 都有 fetch_balance 方法
            if hasattr(exchange, 'fetch_balance'):
                balance = exchange.fetch_balance()
                return balance
            else:
                raise Exception("交易所不支援獲取餘額")
        except Exception as e:
            logger.error(f"獲取餘額失敗: {str(e)}")
            raise
    
    async def _check_trading_permission(self, exchange) -> bool:
        """
        檢查是否具備交易權限（支援 Mock Exchange）
        
        Args:
            exchange: 交易所實例（CCXT 或 MockExchange）
            
        Returns:
            是否具備交易權限
        """
        try:
            # MockExchange 始終返回 True
            if isinstance(exchange, MockExchange):
                return True
            
            # 嘗試獲取開放訂單（需要交易權限）
            if hasattr(exchange, 'fetch_open_orders'):
                # 只是測試權限，不需要實際結果
                exchange.fetch_open_orders(limit=1)
                return True
            else:
                # 如果交易所不支援此 API，假設有權限
                return True
        except AuthenticationError:
            # 認證錯誤表示沒有交易權限
            return False
        except Exception:
            # 其他錯誤（如網路錯誤）不影響權限判斷
            return True
    
    def _calculate_total_balance_usd(self, balance: Dict) -> float:
        """
        計算總餘額（USD）
        
        Args:
            balance: 餘額資訊
            
        Returns:
            總餘額（USD）
        """
        try:
            # 嘗試從 balance 中獲取總價值
            if 'total' in balance and 'USD' in balance['total']:
                return float(balance['total']['USD'])
            
            # 如果沒有直接的 USD 總值，返回 0
            return 0.0
        except Exception:
            return 0.0
    
    async def get_account_balance(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> Dict[str, float]:
        """
        獲取帳戶餘額（用於驗證憑證）
        
        Args:
            exchange_name: 交易所名稱
            api_key: API Key
            api_secret: API Secret
            passphrase: Passphrase（可選）
            
        Returns:
            幣種餘額字典 {'BTC': 0.5, 'USDT': 1000.0, ...}
            
        Raises:
            AuthenticationError: 認證失敗
            NetworkError: 網路錯誤
        """
        try:
            exchange = self._create_exchange_instance(
                exchange_name, api_key, api_secret, passphrase
            )
            
            balance = await self._fetch_balance_async(exchange)
            
            # 提取非零餘額
            total_balance = balance.get('total', {})
            non_zero_balance = {
                currency: amount
                for currency, amount in total_balance.items()
                if amount > 0
            }
            
            return non_zero_balance
            
        except Exception as e:
            logger.error(f"獲取帳戶餘額失敗 ({exchange_name}): {str(e)}")
            raise
    
    def get_supported_exchanges(self) -> List[str]:
        """
        獲取支援的交易所列表
        
        Returns:
            交易所名稱列表
        """
        return self.SUPPORTED_EXCHANGES.copy()
    
    def is_exchange_supported(self, exchange_name: str) -> bool:
        """
        檢查交易所是否支援
        
        Args:
            exchange_name: 交易所名稱
            
        Returns:
            是否支援
        """
        return exchange_name.lower() in self.SUPPORTED_EXCHANGES
    
    async def test_connection(
        self,
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> bool:
        """
        測試連接（簡單驗證）
        
        Args:
            exchange_name: 交易所名稱
            api_key: API Key
            api_secret: API Secret
            passphrase: Passphrase（可選）
            
        Returns:
            連接是否成功
        """
        try:
            result = await self.verify_credentials(
                exchange_name, api_key, api_secret, passphrase
            )
            return result['is_valid']
        except Exception:
            return False


# 全域實例
_exchange_service_instance: Optional[ExchangeService] = None


def get_exchange_service() -> ExchangeService:
    """
    獲取 ExchangeService 單例實例
    
    Returns:
        ExchangeService 實例
    """
    global _exchange_service_instance
    if _exchange_service_instance is None:
        _exchange_service_instance = ExchangeService()
    return _exchange_service_instance
