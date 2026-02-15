# 完整 PnL 與通知系統 - 實作計劃

## 概述

本文檔詳細說明 PnL 統計、Telegram 通知整合、CCXT 抽象層和前端數據補完的完整實作計劃。

## 已完成的工作 ✅

### 1. PositionSnapshot 模型
- ✅ `backend/app/models/position_snapshot.py` - 數據模型
- ✅ `alembic/versions/007_add_position_snapshots.py` - 數據庫遷移
- ✅ `backend/app/models/user.py` - 關係更新

### 2. Telegram 通知服務
- ✅ `backend/app/services/notifier.py` - 完整通知服務
- ✅ 支持 4 種通知類型（交易成功、對帳補單、錯誤警告、每日摘要）
- ✅ 異步發送機制

## 待完成的工作 ⏳

### 階段 1: PnL 計算 API

#### 1.1 未實現盈虧計算
**公式**: `(當前市價 - 入場均價) × 持倉數量`

**實作位置**: `backend/app/services/pnl_service.py`

**功能**:
```python
class PnLService:
    async def calculate_unrealized_pnl(
        self,
        user_id: int,
        current_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        計算未實現盈虧
        
        Args:
            user_id: 用戶 ID
            current_prices: 當前市價字典 {"BTC/USDT": 50000.0, ...}
            
        Returns:
            {
                "total_unrealized_pnl": 1250.50,
                "total_unrealized_pnl_percent": 12.5,
                "positions": [
                    {
                        "symbol": "BTC/USDT",
                        "entry_price": 48000.0,
                        "current_price": 50000.0,
                        "position_size": 0.5,
                        "unrealized_pnl": 1000.0,
                        "unrealized_pnl_percent": 4.17
                    }
                ]
            }
        """
```

#### 1.2 已實現盈虧計算
**來源**: 從 `trade_logs` 表計算已平倉的盈虧

**實作位置**: `backend/app/services/pnl_service.py`

**功能**:
```python
async def calculate_realized_pnl(
    self,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    計算已實現盈虧
    
    Returns:
        {
            "total_realized_pnl": 500.25,
            "total_realized_pnl_percent": 5.0,
            "trades_count": 10,
            "winning_trades": 7,
            "losing_trades": 3
        }
    """
```

#### 1.3 PnL API 路由
**實作位置**: `backend/app/routes/pnl_routes.py`

**端點**:
1. `GET /api/v1/pnl/unrealized` - 獲取未實現盈虧
2. `GET /api/v1/pnl/realized` - 獲取已實現盈虧
3. `GET /api/v1/pnl/summary` - 獲取 PnL 摘要
4. `GET /api/v1/pnl/history` - 獲取歷史快照

### 階段 2: Telegram 通知整合到 FollowerEngine

#### 2.1 FollowerEngineV2 整合
**實作位置**: `backend/app/services/follower_engine_v2.py`

**整合點**:
1. **交易成功時**:
```python
async def _execute_trade(self, ...):
    try:
        order = await exchange.create_order(...)
        
        # 發送成功通知
        asyncio.create_task(
            self.notifier.notify_trade_success(
                user_id=user_id,
                username=username,
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                order_id=order['id']
            )
        )
    except Exception as e:
        # 發送失敗通知
        asyncio.create_task(
            self.notifier.notify_error(
                user_id=user_id,
                username=username,
                error_type=type(e).__name__,
                error_message=str(e),
                context={"symbol": symbol, "side": side}
            )
        )
```

2. **對帳補單時**:
```python
async def _reconcile_position(self, ...):
    if abs(delta) > threshold:
        # 發送補單通知
        asyncio.create_task(
            self.notifier.notify_reconciliation(
                user_id=user_id,
                username=username,
                symbol=symbol,
                master_size=master_size,
                follower_size=current_size,
                target_size=target_size,
                action=f"{'買入' if delta > 0 else '賣出'} {abs(delta)}"
            )
        )
```

#### 2.2 配置管理
**實作位置**: `backend/app/config.py`

**新增配置**:
```python
class Settings(BaseSettings):
    # ... 現有配置 ...
    
    # Telegram 通知配置
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    TELEGRAM_ENABLED: bool = False
```

### 階段 3: CCXT 抽象層

#### 3.1 BaseExchange 抽象基類
**實作位置**: `backend/app/services/exchanges/base_exchange.py`

**結構**:
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseExchange(ABC):
    """交易所抽象基類"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
    
    @abstractmethod
    async def fetch_balance(self) -> Dict[str, Any]:
        """獲取帳戶餘額"""
        pass
    
    @abstractmethod
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """獲取市場行情"""
        pass
    
    @abstractmethod
    async def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """獲取開放訂單"""
        pass
    
    @abstractmethod
    async def create_order(
        self,
        symbol: str,
        order_type: str,
        side: str,
        amount: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """創建訂單"""
        pass
    
    @abstractmethod
    async def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """獲取持倉"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """取消訂單"""
        pass
```

#### 3.2 MockExchange 重構
**實作位置**: `backend/app/services/exchanges/mock_exchange.py`

**變更**: 繼承 `BaseExchange`，實作所有抽象方法

#### 3.3 BinanceTestnetExchange 骨架
**實作位置**: `backend/app/services/exchanges/binance_testnet_exchange.py`

**結構**:
```python
import ccxt
from backend.app.services.exchanges.base_exchange import BaseExchange

class BinanceTestnetExchange(BaseExchange):
    """Binance Testnet 交易所"""
    
    def __init__(self, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        super().__init__(api_key, api_secret, passphrase)
        
        # 初始化 CCXT Binance Testnet
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # 期貨合約
                'test': True  # 使用 Testnet
            },
            'urls': {
                'api': {
                    'public': 'https://testnet.binancefuture.com',
                    'private': 'https://testnet.binancefuture.com'
                }
            }
        })
    
    async def fetch_balance(self) -> Dict[str, Any]:
        """獲取帳戶餘額"""
        return self.exchange.fetch_balance()
    
    async def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """獲取市場行情"""
        return self.exchange.fetch_ticker(symbol)
    
    # ... 實作其他方法 ...
```

#### 3.4 ExchangeFactory
**實作位置**: `backend/app/services/exchanges/factory.py`

**功能**: 統一創建交易所實例

```python
class ExchangeFactory:
    """交易所工廠類"""
    
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
            exchange_name: 交易所名稱 (mock, binance_testnet, binance, okx, ...)
            
        Returns:
            BaseExchange 實例
        """
        if exchange_name.lower() == 'mock':
            from backend.app.services.exchanges.mock_exchange import MockExchange
            return MockExchange(api_key, api_secret, passphrase)
        
        elif exchange_name.lower() == 'binance_testnet':
            from backend.app.services.exchanges.binance_testnet_exchange import BinanceTestnetExchange
            return BinanceTestnetExchange(api_key, api_secret, passphrase)
        
        # ... 其他交易所 ...
        
        else:
            raise ValueError(f"不支援的交易所: {exchange_name}")
```

### 階段 4: 前端 Dashboard 數據補完

#### 4.1 Dashboard API 更新
**實作位置**: `backend/app/routes/dashboard_routes.py`

**新增欄位**:
```python
class DashboardSummary(BaseModel):
    # ... 現有欄位 ...
    
    # 新增：總資產
    total_balance_usdt: float
    available_balance_usdt: float
    used_balance_usdt: float
    
    # 新增：當前盈虧
    unrealized_pnl: float
    unrealized_pnl_percent: float
    realized_pnl: float
    realized_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float
    
    # 新增：最近通知
    recent_notifications: List[NotificationItem]
```

**NotificationItem 模型**:
```python
class NotificationItem(BaseModel):
    id: int
    type: str  # "trade_success", "reconciliation", "error", "daily_summary"
    message: str
    timestamp: str
    is_read: bool
```

#### 4.2 通知歷史表
**實作位置**: `backend/app/models/notification.py`

**數據模型**:
```python
class Notification(Base):
    """通知歷史模型"""
    __tablename__ = "notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

#### 4.3 前端組件更新
**實作位置**: `frontend/src/components/Dashboard.jsx`

**新增卡片**:
1. **總資產卡片**:
```javascript
<StatCard
  title="總資產"
  value={`$${dashboard.total_balance_usdt.toLocaleString()}`}
  subtitle={`可用: $${dashboard.available_balance_usdt.toLocaleString()}`}
  icon={<Wallet className="w-6 h-6" />}
  color="blue"
/>
```

2. **當前盈虧卡片**:
```javascript
<StatCard
  title="當前盈虧"
  value={`${dashboard.total_pnl >= 0 ? '+' : ''}$${Math.abs(dashboard.total_pnl).toLocaleString()}`}
  subtitle={`${dashboard.total_pnl_percent >= 0 ? '+' : ''}${dashboard.total_pnl_percent.toFixed(2)}%`}
  icon={<TrendingUp className="w-6 h-6" />}
  color={dashboard.total_pnl >= 0 ? 'green' : 'red'}
/>
```

3. **通知列表組件**:
```javascript
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-lg font-semibold mb-4">最近通知</h3>
  <div className="space-y-3">
    {dashboard.recent_notifications.map(notif => (
      <NotificationItem key={notif.id} notification={notif} />
    ))}
  </div>
</div>
```

## 實作順序

### 第 1 週
1. ✅ PositionSnapshot 模型（已完成）
2. ✅ Telegram 通知服務（已完成）
3. ⏳ PnL 計算服務
4. ⏳ PnL API 路由

### 第 2 週
5. ⏳ Telegram 通知整合到 FollowerEngine
6. ⏳ 通知歷史表和 API
7. ⏳ Dashboard API 更新

### 第 3 週
8. ⏳ BaseExchange 抽象基類
9. ⏳ MockExchange 重構
10. ⏳ BinanceTestnetExchange 骨架
11. ⏳ ExchangeFactory

### 第 4 週
12. ⏳ 前端 Dashboard 更新
13. ⏳ 通知列表組件
14. ⏳ PnL 顯示組件
15. ⏳ 整合測試

## 測試計劃

### 單元測試
- [ ] PnL 計算邏輯測試
- [ ] Telegram 通知發送測試
- [ ] Exchange 抽象層測試

### 整合測試
- [ ] FollowerEngine + Telegram 通知
- [ ] Dashboard API 完整數據
- [ ] 前端數據顯示

### 端到端測試
- [ ] 完整交易流程 + 通知
- [ ] PnL 計算準確性
- [ ] 前端實時更新

## 配置文件

### .env 新增配置
```bash
# Telegram 通知
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ENABLED=true

# Binance Testnet
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret
```

### docker-compose.yml 更新
```yaml
services:
  backend:
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - TELEGRAM_ENABLED=${TELEGRAM_ENABLED:-false}
```

## 文檔清單

### 已創建
- ✅ PnL統計與通知模組_實作總結.md
- ✅ PnL與通知功能_快速啟動.md
- ✅ 🎉_PnL與通知模組_完成.txt

### 待創建
- ⏳ CCXT抽象層_實作指南.md
- ⏳ Telegram通知整合_測試指南.md
- ⏳ 前端Dashboard補完_實作總結.md

## 總結

本計劃涵蓋了完整的 PnL 統計、Telegram 通知整合、CCXT 抽象層和前端數據補完。

**已完成**: PositionSnapshot 模型、Telegram 通知服務基礎

**進行中**: PnL 計算 API、FollowerEngine 整合、CCXT 抽象層

**待開始**: 前端 Dashboard 更新、完整測試

預計 4 週完成所有功能！

---

**文檔版本**: 1.0.0  
**最後更新**: 2024-01-01  
**作者**: Kiro AI Assistant
