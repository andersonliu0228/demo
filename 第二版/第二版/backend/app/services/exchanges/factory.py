"""
Exchange Factory
交易所工廠類 - 統一創建交易所實例
"""
import logging
from typing import Optional

from backend.app.services.exchanges.base_exchange import BaseExchange
from backend.app.services.exchanges.mock_exchange import MockExchange

logger = logging.getLogger(__name__)


class ExchangeFactory:
    """
    交易所工廠類
    
    統一創建交易所實例，確保切換交易所時核心邏輯不需改動
    """
    
    # 支援的交易所列表
    SUPPORTED_EXCHANGES = [
        'mock',  # Mock 交易所（開發測試）
        'binance',  # 幣安
        'binance_testnet',  # 幣安測試網
        'okx',  # OKX
        'bybit',  # Bybit
        'huobi',  # 火幣
        'kucoin',  # KuCoin
        'gate',  # Gate.io
        'bitget',  # Bitget
        'mexc'  # MEXC
    ]
    
    @staticmethod
    def create_exchange(
        exchange_name: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None
    ) -> BaseExchange:
        """
        創建交易所實例
        
        Args:
            exchange_name: 交易所名稱（如 'mock', 'binance', 'binance_testnet', 'okx'）
            api_key: API Key
            api_secret: API Secret
            passphrase: Passphrase（某些交易所需要，如 OKX）
            
        Returns:
            BaseExchange 實例
            
        Raises:
            ValueError: 如果交易所不支援
        """
        exchange_name_lower = exchange_name.lower()
        
        if exchange_name_lower not in ExchangeFactory.SUPPORTED_EXCHANGES:
            raise ValueError(
                f"不支援的交易所: {exchange_name}。"
                f"支援的交易所: {', '.join(ExchangeFactory.SUPPORTED_EXCHANGES)}"
            )
        
        # Mock Exchange
        if exchange_name_lower == 'mock':
            logger.info("創建 MockExchange 實例（開發模式）")
            return MockExchange(api_key, api_secret, passphrase)
        
        # Binance Testnet
        elif exchange_name_lower == 'binance_testnet':
            logger.info("創建 BinanceTestnetExchange 實例")
            # TODO: 實作 BinanceTestnetExchange
            raise NotImplementedError("BinanceTestnetExchange 尚未實作")
        
        # Binance
        elif exchange_name_lower == 'binance':
            logger.info("創建 BinanceExchange 實例")
            # TODO: 實作 BinanceExchange
            raise NotImplementedError("BinanceExchange 尚未實作")
        
        # OKX
        elif exchange_name_lower == 'okx':
            logger.info("創建 OKXExchange 實例")
            # TODO: 實作 OKXExchange
            raise NotImplementedError("OKXExchange 尚未實作")
        
        # 其他交易所
        else:
            raise NotImplementedError(f"{exchange_name} 尚未實作")
    
    @staticmethod
    def is_supported(exchange_name: str) -> bool:
        """
        檢查交易所是否支援
        
        Args:
            exchange_name: 交易所名稱
            
        Returns:
            是否支援
        """
        return exchange_name.lower() in ExchangeFactory.SUPPORTED_EXCHANGES
    
    @staticmethod
    def get_supported_exchanges() -> list:
        """
        獲取支援的交易所列表
        
        Returns:
            交易所名稱列表
        """
        return ExchangeFactory.SUPPORTED_EXCHANGES.copy()
