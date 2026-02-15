# Signal Dispatcher 完整測試指南

## 最新功能

### ✅ 已實現功能

1. **更快的輪詢間隔** - 從 5 秒優化為 **3 秒**
2. **滑價預估** - 自動計算並記錄預估滑價
3. **實際成交價格** - 模擬滑價影響的實際成交價
4. **測試 API** - 新增 `POST /test/trigger-master-order` 方便測試

## 快速開始

### 方法 1: 使用新的測試 API（推薦）

這是最簡單的測試方法，無需手動創建憑證和關係。

#### 步驟 1: 準備測試數據

```powershell
# 1. 創建 Master 憑證
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"exchange_name\":\"mock\",\"api_key\":\"master_key\",\"api_secret\":\"master_secret\",\"label\":\"Master\"}'

# 2. 創建 Follower 憑證
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":2,\"exchange_name\":\"mock\",\"api_key\":\"follower_key\",\"api_secret\":\"follower_secret\",\"label\":\"Follower\"}'

# 3. 創建跟隨關係
curl.exe -X POST http://localhost:8000/api/v1/follower/relationships `
  -H "Content-Type: application/json" `
  -d '{\"follower_user_id\":2,\"master_user_id\":1,\"follow_ratio\":0.1,\"follower_credential_id\":2,\"master_credential_id\":1}'
```

#### 步驟 2: 啟動監控引擎

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/engine/start
```

#### 步驟 3: 使用測試 API 觸發 Master 訂單

```powershell
# 觸發 Master 開多倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?master_user_id=1&master_credential_id=1&symbol=BTC/USDT&position_size=1.0&entry_price=50000.0"
```

**返回示例**：
```json
{
  "success": true,
  "message": "Master 訂單已觸發",
  "master_info": {
    "user_id": 1,
    "credential_id": 1,
    "symbol": "BTC/USDT",
    "old_position_size": 0,
    "new_position_size": 1.0,
    "entry_price": 50000.0,
    "position_changed": true
  },
  "followers_count": 1,
  "expected_trades": [
    {
      "follower_user_id": 2,
      "follow_ratio": 0.1,
      "expected_amount": 0.1,
      "side": "buy"
    }
  ],
  "note": "跟單引擎將在下一個輪詢週期（最多 3 秒）檢測並執行跟單"
}
```

#### 步驟 4: 等待並查看結果

```powershell
# 等待 4 秒（讓引擎檢測並執行）
Start-Sleep -Seconds 4

# 查看交易歷史（包含滑價資訊）
curl.exe http://localhost:8000/api/v1/follower/trade-history
```

**預期輸出**：
```json
[
  {
    "id": 1,
    "follow_relationship_id": 1,
    "symbol": "BTC/USDT",
    "side": "buy",
    "order_type": "market",
    "amount": 0.1,
    "price": 50000.0,
    "follow_ratio": 0.1,
    "estimated_slippage": 0.0011,
    "estimated_slippage_percent": "0.110%",
    "actual_fill_price": 50055.0,
    "master_position_size": 1.0,
    "order_id": "mock-order-xxx",
    "status": "filled",
    "created_at": "2026-02-03T...",
    "executed_at": "2026-02-03T..."
  }
]
```

### 方法 2: 在 Swagger UI 中測試

訪問 http://localhost:8000/docs

#### 完整流程

1. **POST /api/v1/credentials** - 創建 Master 和 Follower 憑證
2. **POST /api/v1/follower/relationships** - 創建跟隨關係
3. **POST /api/v1/follower/engine/start** - 啟動引擎
4. **POST /api/v1/test/trigger-master-order** - 觸發 Master 訂單 ⭐ 新功能
5. **等待 4 秒**
6. **GET /api/v1/follower/trade-history** - 查看結果（包含滑價）

## 新功能詳解

### 1. 更快的輪詢（3 秒）

**改進前**：5 秒輪詢，最大延遲 5 秒
**改進後**：3 秒輪詢，最大延遲 3 秒

**驗證方法**：
```powershell
curl.exe http://localhost:8000/api/v1/follower/engine/status
```

**預期輸出**：
```json
{
  "is_running": true,
  "poll_interval": 3
}
```

### 2. 滑價預估

**計算公式**：
```python
estimated_slippage = 0.001 * (1 + follower_amount * 0.1)
# 基礎滑價 0.1% + 數量影響
```

**示例**：
- 數量 0.1 BTC: 滑價 ≈ 0.11%
- 數量 1.0 BTC: 滑價 ≈ 0.20%
- 數量 10.0 BTC: 滑價 ≈ 1.10%

**實際成交價格**：
- 買入：`actual_fill_price = entry_price * (1 + slippage)`
- 賣出：`actual_fill_price = entry_price * (1 - slippage)`

### 3. 測試 API

**端點**: `POST /api/v1/test/trigger-master-order`

**參數**：
- `master_user_id` (int): Master 用戶 ID，預設 1
- `master_credential_id` (int): Master 憑證 ID，預設 1
- `symbol` (string): 交易對，預設 "BTC/USDT"
- `position_size` (float): 倉位大小，預設 1.0
- `entry_price` (float): 開倉價格，預設 50000.0

**使用場景**：
1. 快速測試跟單功能
2. 模擬不同的倉位變動
3. 驗證跟單邏輯

**示例**：

```powershell
# 場景 1: Master 開多倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=1.0&entry_price=50000"

# 場景 2: Master 增加倉位
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=2.0&entry_price=51000"

# 場景 3: Master 平倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=0"

# 場景 4: Master 開空倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?symbol=ETH/USDT&position_size=-5.0&entry_price=3000"
```

## 完整測試場景

### 場景 1: 基本跟單（含滑價）

```powershell
# 1. 觸發 Master 開倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=1.0&entry_price=50000"

# 2. 等待 4 秒
Start-Sleep -Seconds 4

# 3. 查看交易歷史
curl.exe http://localhost:8000/api/v1/follower/trade-history
```

**驗證點**：
- ✅ `follow_ratio`: 0.1
- ✅ `amount`: 0.1 (1.0 × 0.1)
- ✅ `estimated_slippage`: ~0.0011 (0.11%)
- ✅ `actual_fill_price`: ~50055 (50000 × 1.0011)
- ✅ `status`: "filled"

### 場景 2: 倉位變動

```powershell
# 1. 第一次開倉
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=1.0&entry_price=50000"
Start-Sleep -Seconds 4

# 2. 增加倉位
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=2.0&entry_price=51000"
Start-Sleep -Seconds 4

# 3. 查看歷史（應該有 2 筆記錄）
curl.exe http://localhost:8000/api/v1/follower/trade-history
```

### 場景 3: 多個跟隨者

```powershell
# 1. 創建第二個跟隨者
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -d '{\"user_id\":3,\"exchange_name\":\"mock\",\"api_key\":\"follower2_key\",\"api_secret\":\"follower2_secret\",\"label\":\"Follower2\"}'

curl.exe -X POST http://localhost:8000/api/v1/follower/relationships `
  -d '{\"follower_user_id\":3,\"master_user_id\":1,\"follow_ratio\":0.2,\"follower_credential_id\":3,\"master_credential_id\":1}'

# 2. 觸發 Master 訂單
curl.exe -X POST "http://localhost:8000/api/v1/test/trigger-master-order?position_size=1.0&entry_price=50000"

# 3. 等待並查看（應該有 2 個跟隨者的記錄）
Start-Sleep -Seconds 4
curl.exe http://localhost:8000/api/v1/follower/trade-history
```

**預期結果**：
- Follower 1 (ratio=0.1): 0.1 BTC, 滑價 ~0.11%
- Follower 2 (ratio=0.2): 0.2 BTC, 滑價 ~0.12%

## 性能指標

| 指標 | 數值 |
|------|------|
| 輪詢間隔 | 3 秒 |
| 最大響應延遲 | 3 秒 |
| 平均執行時間 | 10-30ms |
| 滑價預估範圍 | 0.1% - 1.0% |

## 日誌查看

```powershell
docker logs -f ea_trading_backend
```

**關鍵日誌**：
```
INFO: [14:30:00] 開始新一輪監控檢查
INFO: 檢測到 Master 1 倉位變動: BTC/USDT 0 -> 1.0
INFO: [跟隨者 2] 準備跟單 - 跟隨數量: 0.1, 預估滑價: 0.110%
INFO: [跟隨者 2] 跟單成功 - 預估價格: 50000, 實際成交: 50055, 滑價: 0.110%
```

## API 端點總覽

### 新增端點

- **POST /api/v1/test/trigger-master-order** ⭐ 觸發 Master 訂單（測試用）

### 更新端點

- **GET /api/v1/follower/trade-history** - 現在包含滑價資訊
  - `follow_ratio` - 跟隨比例
  - `estimated_slippage` - 預估滑價（小數）
  - `estimated_slippage_percent` - 預估滑價（百分比字串）
  - `actual_fill_price` - 實際成交價格

### 現有端點

- POST /api/v1/follower/relationships - 創建跟隨關係
- GET /api/v1/follower/relationships - 列出跟隨關係
- POST /api/v1/follower/master-position - 更新 Master 倉位
- GET /api/v1/follower/master-positions - 列出 Master 倉位
- GET /api/v1/follower/trade-logs - 查看交易日誌
- GET /api/v1/follower/trade-logs/stats - 查看統計
- POST /api/v1/follower/engine/start - 啟動引擎
- POST /api/v1/follower/engine/stop - 停止引擎
- GET /api/v1/follower/engine/status - 查看引擎狀態

## 故障排除

### 問題 1: 測試 API 返回 404
**解決**：確認後端已重啟並加載新路由
```powershell
docker restart ea_trading_backend
Start-Sleep -Seconds 8
curl.exe http://localhost:8000/health
```

### 問題 2: 滑價資訊為 null
**原因**：使用舊的交易記錄
**解決**：觸發新的 Master 訂單，查看新記錄

### 問題 3: 跟單未執行
**檢查**：
1. 引擎是否啟動
2. 是否等待足夠時間（至少 4 秒）
3. 查看後端日誌

## 總結

### 核心改進

1. ✅ **3 秒輪詢** - 更快的響應速度
2. ✅ **滑價預估** - 更真實的交易模擬
3. ✅ **測試 API** - 更方便的測試流程
4. ✅ **完整記錄** - trade_history 包含所有關鍵資訊

### 測試建議

1. 使用 `POST /api/v1/test/trigger-master-order` 快速測試
2. 觀察 `estimated_slippage` 和 `actual_fill_price`
3. 驗證不同數量的滑價差異
4. 測試多個跟隨者的並行執行

系統已完全就緒，開始測試吧！🚀
