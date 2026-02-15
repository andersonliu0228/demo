# PnL 統計與通知功能 - 快速啟動指南

## 🚀 快速開始

### 步驟 1: 執行數據庫遷移

```powershell
# 在 Docker 容器中執行遷移
docker compose exec backend alembic upgrade head
```

**預期輸出**:
```
INFO  [alembic.runtime.migration] Running upgrade 006 -> 007, add position snapshots table
```

### 步驟 2: 配置 Telegram Bot（可選）

#### 2.1 創建 Telegram Bot
1. 在 Telegram 搜索 `@BotFather`
2. 發送 `/newbot`
3. 按提示設置名稱
4. 獲取 Bot Token

#### 2.2 獲取 Chat ID
1. 在 Telegram 搜索 `@userinfobot`
2. 發送任意訊息
3. 獲取 Chat ID

#### 2.3 配置環境變數
編輯 `.env` 文件：

```bash
# Telegram 通知配置
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 步驟 3: 重啟後端服務

```powershell
docker compose restart backend
```

### 步驟 4: 測試功能

#### 4.1 測試 Telegram 通知

```python
# 在 Python 中測試
import asyncio
from backend.app.services.notifier import get_notifier_service

async def test():
    notifier = get_notifier_service(
        telegram_bot_token="YOUR_TOKEN",
        telegram_chat_id="YOUR_CHAT_ID"
    )
    
    await notifier.notify_trade_success(
        user_id=1,
        username="testuser",
        symbol="BTC/USDT",
        side="buy",
        amount=0.5,
        price=50000.0,
        order_id="test123"
    )

asyncio.run(test())
```

#### 4.2 創建測試快照

```python
from backend.app.models.position_snapshot import PositionSnapshot
from datetime import date

snapshot = PositionSnapshot(
    user_id=1,
    snapshot_date=date.today(),
    total_value_usdt=10000.0,
    position_count=3
)

db.add(snapshot)
await db.commit()
```

## 📊 功能說明

### 1. PositionSnapshot（倉位快照）

**用途**:
- 每天記錄帳戶總值
- 計算昨日收益
- 計算總持倉盈虧

**數據結構**:
```python
{
    "user_id": 1,
    "snapshot_date": "2024-01-01",
    "total_value_usdt": 10000.0,
    "position_count": 3,
    "details": "{...}",  # JSON 格式
    "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. Telegram 通知

**通知類型**:

1. **交易成功通知**
   ```
   🟢 交易成功通知
   
   👤 用戶: testuser (ID: 1)
   📊 交易對: BTC/USDT
   📈 方向: BUY
   💰 數量: 0.5
   💵 價格: $50,000.00
   🆔 訂單: abc123
   
   ⏰ 時間: 2024-01-01 12:00:00 UTC
   ```

2. **對帳補單通知**
   ```
   ⚠️ 對帳補單通知
   
   👤 用戶: testuser (ID: 1)
   📊 交易對: BTC/USDT
   
   📍 Master 倉位: 1.5
   📍 Follower 當前: 0.5
   🎯 Follower 目標: 0.75
   
   🔧 執行動作: 買入 0.25 BTC
   
   ⏰ 時間: 2024-01-01 12:00:00 UTC
   ```

3. **錯誤警告通知**
   ```
   🚨 錯誤警告
   
   👤 用戶: testuser (ID: 1)
   ❌ 錯誤類型: InsufficientFunds
   
   💬 錯誤訊息:
   餘額不足，無法執行交易
   
   📋 詳細資訊:
     • symbol: BTC/USDT
     • required: 1000 USDT
     • available: 500 USDT
   
   ⏰ 時間: 2024-01-01 12:00:00 UTC
   ```

4. **每日摘要通知**
   ```
   📊 每日摘要報告
   
   👤 用戶: testuser (ID: 1)
   
   💰 總持倉價值: $10,150.50
   📈 今日盈虧: +$150.50 (+1.50%)
   📦 持倉數量: 3
   
   ⏰ 時間: 2024-01-01 12:00:00 UTC
   ```

## 🔧 整合到 FollowerEngine

### 在交易成功時發送通知

```python
# 在 backend/app/services/follower_engine_v2.py 中

from backend.app.services.notifier import get_notifier_service

class FollowerEngineV2:
    def __init__(self, ...):
        # 初始化通知服務
        self.notifier = get_notifier_service(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
    
    async def _execute_trade(self, ...):
        # 執行交易
        order = await exchange.create_order(...)
        
        # 發送通知（異步，不阻塞）
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
```

### 在對帳補單時發送通知

```python
async def _reconcile_position(self, ...):
    # 執行對帳
    delta = target_size - current_size
    
    if abs(delta) > threshold:
        # 發送通知
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
        
        # 執行交易
        await self._execute_trade(...)
```

### 在錯誤時發送通知

```python
async def _handle_error(self, error, context):
    # 記錄錯誤
    await self._log_error(...)
    
    # 發送通知
    asyncio.create_task(
        self.notifier.notify_error(
            user_id=context['user_id'],
            username=context['username'],
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
    )
```

## 📈 前端顯示（待實作）

### Dashboard 新增 PnL 卡片

```javascript
// 昨日收益卡片
<StatCard
  title="昨日收益"
  value={`${dashboard.daily_pnl >= 0 ? '+' : ''}$${Math.abs(dashboard.daily_pnl).toLocaleString()}`}
  subtitle={`${dashboard.daily_pnl_percent >= 0 ? '+' : ''}${dashboard.daily_pnl_percent.toFixed(2)}%`}
  icon={<TrendingUp className="w-6 h-6" />}
  color={dashboard.daily_pnl >= 0 ? 'green' : 'red'}
/>

// 總持倉盈虧卡片
<StatCard
  title="總持倉盈虧"
  value={`${dashboard.total_pnl >= 0 ? '+' : ''}$${Math.abs(dashboard.total_pnl).toLocaleString()}`}
  subtitle={`${dashboard.total_pnl_percent >= 0 ? '+' : ''}${dashboard.total_pnl_percent.toFixed(2)}%`}
  icon={<Activity className="w-6 h-6" />}
  color={dashboard.total_pnl >= 0 ? 'green' : 'red'}
/>
```

### 顯示最後同步時間

```javascript
// 在 StatusBar 中
<div className="text-sm text-gray-600">
  最後同步: {formatRelativeTime(dashboard.last_sync_time)}
</div>

// 格式化相對時間
function formatRelativeTime(timestamp) {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = Math.floor((now - time) / 1000); // 秒
  
  if (diff < 60) return `${diff} 秒前`;
  if (diff < 3600) return `${Math.floor(diff / 60)} 分鐘前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小時前`;
  return `${Math.floor(diff / 86400)} 天前`;
}
```

### Master 倉位變動閃爍特效

```css
/* 在 index.css 中 */
@keyframes flash-green {
  0%, 100% { background-color: transparent; }
  50% { background-color: rgba(34, 197, 94, 0.3); }
}

.position-flash {
  animation: flash-green 2s ease-in-out;
}
```

```javascript
// 在 Dashboard 中
const [flashingPositions, setFlashingPositions] = useState(new Set());

useEffect(() => {
  if (prevMasterPositions && dashboard.master_positions) {
    dashboard.master_positions.forEach(pos => {
      const prevPos = prevMasterPositions.find(p => p.symbol === pos.symbol);
      if (prevPos && prevPos.position_size !== pos.position_size) {
        // 添加閃爍效果
        setFlashingPositions(prev => new Set(prev).add(pos.symbol));
        
        // 2 秒後移除
        setTimeout(() => {
          setFlashingPositions(prev => {
            const next = new Set(prev);
            next.delete(pos.symbol);
            return next;
          });
        }, 2000);
      }
    });
  }
  setPrevMasterPositions(dashboard.master_positions);
}, [dashboard.master_positions]);

// 在渲染時應用 class
<div className={flashingPositions.has(pos.symbol) ? 'position-flash' : ''}>
  {/* 倉位內容 */}
</div>
```

## 🧪 測試清單

### 數據庫測試
- [ ] 執行遷移成功
- [ ] 創建快照成功
- [ ] 查詢快照成功
- [ ] 唯一索引生效

### Telegram 通知測試
- [ ] 交易成功通知發送
- [ ] 對帳補單通知發送
- [ ] 錯誤警告通知發送
- [ ] 每日摘要通知發送
- [ ] HTML 格式正確顯示

### 整合測試
- [ ] FollowerEngine 交易時發送通知
- [ ] 對帳補單時發送通知
- [ ] 錯誤時發送通知
- [ ] 通知不阻塞主流程

### 前端測試
- [ ] PnL 卡片顯示正確
- [ ] 最後同步時間更新
- [ ] 閃爍特效觸發
- [ ] 顏色標示正確

## 📚 相關文檔

- [PnL統計與通知模組_實作總結.md](./PnL統計與通知模組_實作總結.md) - 詳細技術文檔
- [完整系統自動化流水線_實作總結.md](./完整系統自動化流水線_實作總結.md) - 系統整體文檔

## ⚠️ 注意事項

1. **Telegram Bot Token 安全**
   - 不要將 Token 提交到 Git
   - 使用環境變數存儲
   - 定期更換 Token

2. **通知頻率控制**
   - 避免頻繁發送通知
   - 考慮添加通知間隔限制
   - 批量通知合併發送

3. **錯誤處理**
   - 通知失敗不影響主流程
   - 記錄通知失敗日誌
   - 提供重試機制

4. **性能考慮**
   - 使用異步發送
   - 避免阻塞主線程
   - 考慮使用消息隊列

## 🎯 下一步

1. 完成前端 PnL 顯示
2. 實作定時快照任務
3. 整合通知到 FollowerEngine
4. 測試完整流程
5. 優化通知訊息格式

---

**祝您使用愉快！** 🎉
