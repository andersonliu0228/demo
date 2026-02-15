"""
Exchange Service 單元測試
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from ccxt.base.errors import AuthenticationError, NetworkError

from backend.app.services.exchange_service import ExchangeService


@pytest.fixture
def exchange_service():
    """創建 ExchangeService 實例"""
    return ExchangeService()


@pytest.fixture
def mock_exchange():
    """創建 Mock 交易所實例"""
    exchange = Mock()
    exchange.fetch_balance = Mock(return_value={
        'total': {
            'BTC': 1.5,
            'USDT': 10000.0,
            'ETH': 5.0
        }
    })
    exchange.fetch_open_orders = Mock(return_value=[])
    return exchange


class TestExchangeServiceSupport:
    """測試交易所支援"""
    
    def test_get_supported_exchanges(self, exchange_service):
        """測試獲取支援的交易所列表"""
        exchanges = exchange_service.get_supported_exchanges()
        
        assert isinstance(exchanges, list)
        assert len(exchanges) > 0
        assert 'binance' in exchanges
        assert 'okx' in exchanges
    
    def test_is_exchange_supported(self, exchange_service):
        """測試檢查交易所是否支援"""
        assert exchange_service.is_exchange_supported('binance') is True
        assert exchange_service.is_exchange_supported('okx') is True
        assert exchange_service.is_exchange_supported('unknown_exchange') is False
    
    def test_is_exchange_supported_case_insensitive(self, exchange_service):
        """測試交易所名稱不區分大小寫"""
        assert exchange_service.is_exchange_supported('BINANCE') is True
        assert exchange_service.is_exchange_supported('Binance') is True


class TestExchangeInstanceCreation:
    """測試交易所實例創建"""
    
    def test_create_exchange_instance_success(self, exchange_service):
        """測試成功創建交易所實例"""
        with patch('ccxt.binance') as mock_binance:
            mock_binance.return_value = Mock()
            
            exchange = exchange_service._create_exchange_instance(
                'binance',
                'test_key',
                'test_secret'
            )
            
            assert exchange is not None
            mock_binance.assert_called_once()
    
    def test_create_exchange_instance_with_passphrase(self, exchange_service):
        """測試創建帶 Passphrase 的交易所實例"""
        with patch('ccxt.okx') as mock_okx:
            mock_okx.return_value = Mock()
            
            exchange = exchange_service._create_exchange_instance(
                'okx',
                'test_key',
                'test_secret',
                'test_passphrase'
            )
            
            assert exchange is not None
            # 驗證配置包含 password
            call_args = mock_okx.call_args[0][0]
            assert 'password' in call_args
            assert call_args['password'] == 'test_passphrase'
    
    def test_create_exchange_instance_unsupported_exchange(self, exchange_service):
        """測試創建不支援的交易所實例"""
        with pytest.raises(ValueError, match="不支援的交易所"):
            exchange_service._create_exchange_instance(
                'unsupported_exchange',
                'test_key',
                'test_secret'
            )


class TestVerifyCredentials:
    """測試憑證驗證"""
    
    @pytest.mark.asyncio
    async def test_verify_valid_credentials(self, exchange_service, mock_exchange):
        """測試驗證有效憑證"""
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            result = await exchange_service.verify_credentials(
                'binance',
                'valid_key',
                'valid_secret'
            )
            
            assert result['is_valid'] is True
            assert result['has_trading_permission'] is True
            assert result['account_info'] is not None
            assert result['error_message'] is None
    
    @pytest.mark.asyncio
    async def test_verify_invalid_credentials(self, exchange_service):
        """
        Feature: ea-trading-backend, Property 11: 無效憑證驗證失敗
        
        測試驗證無效憑證返回 false
        
        對於任何無效的 API 憑證（錯誤的 API Key 或 Secret），
        當透過 Exchange Service 驗證時，應該返回 is_valid=false 並包含具體的錯誤訊息。
        
        驗證需求：4.4, 4.5
        """
        mock_exchange = Mock()
        mock_exchange.fetch_balance = Mock(
            side_effect=AuthenticationError("Invalid API key")
        )
        
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            result = await exchange_service.verify_credentials(
                'binance',
                'invalid_key',
                'invalid_secret'
            )
            
            assert result['is_valid'] is False
            assert result['has_trading_permission'] is False
            assert result['account_info'] is None
            assert result['error_message'] is not None
            assert "認證失敗" in result['error_message']
    
    @pytest.mark.asyncio
    async def test_verify_credentials_network_error(self, exchange_service):
        """
        測試網路錯誤處理
        
        驗證需求：4.7
        """
        mock_exchange = Mock()
        mock_exchange.fetch_balance = Mock(
            side_effect=NetworkError("Connection timeout")
        )
        
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            result = await exchange_service.verify_credentials(
                'binance',
                'test_key',
                'test_secret'
            )
            
            assert result['is_valid'] is False
            assert "網路連接錯誤" in result['error_message']
    
    @pytest.mark.asyncio
    async def test_verify_credentials_unsupported_exchange(self, exchange_service):
        """測試不支援的交易所"""
        result = await exchange_service.verify_credentials(
            'unsupported_exchange',
            'test_key',
            'test_secret'
        )
        
        assert result['is_valid'] is False
        assert "不支援的交易所" in result['error_message']


class TestGetAccountBalance:
    """測試獲取帳戶餘額"""
    
    @pytest.mark.asyncio
    async def test_get_account_balance_success(
        self, exchange_service, mock_exchange
    ):
        """測試成功獲取帳戶餘額"""
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            balance = await exchange_service.get_account_balance(
                'binance',
                'test_key',
                'test_secret'
            )
            
            assert isinstance(balance, dict)
            assert 'BTC' in balance
            assert 'USDT' in balance
            assert balance['BTC'] == 1.5
            assert balance['USDT'] == 10000.0
    
    @pytest.mark.asyncio
    async def test_get_account_balance_authentication_error(
        self, exchange_service
    ):
        """測試認證失敗"""
        mock_exchange = Mock()
        mock_exchange.fetch_balance = Mock(
            side_effect=AuthenticationError("Invalid credentials")
        )
        
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            with pytest.raises(AuthenticationError):
                await exchange_service.get_account_balance(
                    'binance',
                    'invalid_key',
                    'invalid_secret'
                )


class TestTradingPermission:
    """測試交易權限檢查"""
    
    @pytest.mark.asyncio
    async def test_check_trading_permission_success(
        self, exchange_service, mock_exchange
    ):
        """測試有交易權限"""
        has_permission = await exchange_service._check_trading_permission(
            mock_exchange
        )
        
        assert has_permission is True
    
    @pytest.mark.asyncio
    async def test_check_trading_permission_no_permission(
        self, exchange_service
    ):
        """測試沒有交易權限"""
        mock_exchange = Mock()
        mock_exchange.fetch_open_orders = Mock(
            side_effect=AuthenticationError("No trading permission")
        )
        
        has_permission = await exchange_service._check_trading_permission(
            mock_exchange
        )
        
        assert has_permission is False
    
    @pytest.mark.asyncio
    async def test_check_trading_permission_exchange_not_support(
        self, exchange_service
    ):
        """測試交易所不支援檢查權限"""
        mock_exchange = Mock(spec=[])  # 沒有 fetch_open_orders 方法
        
        has_permission = await exchange_service._check_trading_permission(
            mock_exchange
        )
        
        # 如果交易所不支援，假設有權限
        assert has_permission is True


class TestTestConnection:
    """測試連接測試"""
    
    @pytest.mark.asyncio
    async def test_connection_success(self, exchange_service, mock_exchange):
        """測試連接成功"""
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            result = await exchange_service.test_connection(
                'binance',
                'test_key',
                'test_secret'
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, exchange_service):
        """測試連接失敗"""
        mock_exchange = Mock()
        mock_exchange.fetch_balance = Mock(
            side_effect=AuthenticationError("Invalid credentials")
        )
        
        with patch.object(
            exchange_service,
            '_create_exchange_instance',
            return_value=mock_exchange
        ):
            result = await exchange_service.test_connection(
                'binance',
                'invalid_key',
                'invalid_secret'
            )
            
            assert result is False


class TestCalculateTotalBalance:
    """測試計算總餘額"""
    
    def test_calculate_total_balance_with_usd(self, exchange_service):
        """測試計算包含 USD 的總餘額"""
        balance = {
            'total': {
                'USD': 50000.0,
                'BTC': 1.0,
                'ETH': 10.0
            }
        }
        
        total = exchange_service._calculate_total_balance_usd(balance)
        assert total == 50000.0
    
    def test_calculate_total_balance_without_usd(self, exchange_service):
        """測試計算不包含 USD 的總餘額"""
        balance = {
            'total': {
                'BTC': 1.0,
                'ETH': 10.0
            }
        }
        
        total = exchange_service._calculate_total_balance_usd(balance)
        assert total == 0.0
    
    def test_calculate_total_balance_empty(self, exchange_service):
        """測試計算空餘額"""
        balance = {}
        
        total = exchange_service._calculate_total_balance_usd(balance)
        assert total == 0.0
