# Swagger UI 測試指南 - Follower Engine

## 訪問 Swagger UI

打開瀏覽器訪問：http://localhost:8000/docs

## 完整測試流程

### 步驟 1: 創建 Master 憑證

1. 找到 **POST /api/v1/credentials** 端點
2. 點擊 "Try it out"
3. 輸入以下 JSON：

```json
{
  "user_id": 1,
  "exchange_name": "mock",
  "api_key": "master_key_123",
  "api_secret": "master_secret_456",
  "label": "Master Mock"
}
```

4. 點擊 "Execute"
5. 記下返回的 `credential_id`（應該是 1）

### 步驟 2: 創建 Follower 憑證

1. 再次使用 **POST /api/v1/credentials**
2. 輸入以下 JSON：

```json
{
  "user_id": 2,
  "exchange_name": "mock",
  "api_key": "follower_key_789",
  "api_secret": "follower_secret_012",
  "label": "Follower Mock"
}
```

3. 記下返回的 `credential_id`（應該是 2）

### 步驟 3: 創建跟隨關係

1. 找到 **POST /api/v1/follower/relationships** 端點
2. 點擊 "Try it out"
3. 輸入以下 JSON：

```json
{
  "follower_user_id": 2,
  "master_user_id": 1,
  "follow_ratio": 0.1,
  "follower_credential_id": 2,
  "master_credential_id": 1
}
```

參數說明：
- `follow_ratio: 0.1` 表示跟隨 10% 倍數
- Master 開 1 BTC，Follower 自動開 0.1 BTC

4. 點擊 "Execute"
5. 記下返回的 `relationship_id`

### 步驟 4: 啟動監控引擎

1. 找到 **POST /api/v1/follower/engine/start** 端點
2. 點擊 "Try it out"
3. 點擊 "Execute"
4. 確認返回 `"message": "Follower Engine 已啟動"`

### 步驟 5: 模擬 Master 下單（關鍵步驟！）

1. 找到 **POST /api/v1/follower/master-position** 端點
2. 點擊 "Try it out"
3. 輸入以下 JSON：

```json
{
  "master_user_id": 1,
  "master_credential_id": 1,
  "symbol": "BTC/USDT",
  "position_size": 1.0,
  "entry_price": 50000.0
}
```

參數說明：
- `position_size: 1.0` = 開多倉 1 BTC
- `position_size: -1.0` = 開空倉 1 BTC
- `position_size: 0` = 平倉

4. 點擊 "Execute"
5. **等待 10-15 秒**（讓監控引擎檢測並執行跟單）

### 步驟 6: 查看跟單結果

#### 6.1 查看交易歷史

1. 找到 **GET /api/v1/follower/trade-history** 端點
2. 點擊 "Try it out"
3. 點擊 "Execute"
4. 查看返回結果，應該看到：

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
    "master_position_size": 1.0,
    "order_id": "mock-order-xxx",
    "status": "filled",
    "error_message": null,
    "created_at": "2026-02-03T...",
    "executed_at": "2026-02-03T..."
  }
]
```

關鍵欄位：
- `amount: 0.1` - Follower 跟單數量（Master 1.0 × ratio 0.1）
- `status: "filled"` - 訂單已成交
- `order_id` - MockExchange 返回的訂單 ID

#### 6.2 查看 Master 倉位

1. 找到 **GET /api/v1/follower/master-positions** 端點
2. 輸入 `master_user_id: 1`
3. 點擊 "Execute"
4. 確認 Master 的倉位記錄

#### 6.3 查看跟隨關係

1. 找到 **GET /api/v1/follower/relationships** 端點
2. 點擊 "Execute"
3. 確認跟隨關係狀態

### 步驟 7: 測試其他場景

#### 場景 A: Master 平倉

```json
{
  "master_user_id": 1,
  "master_credential_id": 1,
  "symbol": "BTC/USDT",
  "position_size": 0,
  "entry_price": null
}
```

等待 10-15 秒後查看交易歷史，應該看到 Follower 也執行了平倉。

#### 場景 B: Master 開空倉

```json
{
  "master_user_id": 1,
  "master_credential_id": 1,
  "symbol": "ETH/USDT",
  "position_size": -2.0,
  "entry_price": 3000.0
}
```

Follower 應該自動開空倉 -0.2 ETH。

#### 場景 C: 不同交易對

```json
{
  "master_user_id": 1,
  "master_credential_id": 1,
  "symbol": "SOL/USDT",
  "position_size": 10.0,
  "entry_price": 100.0
}
```

Follower 應該自動開多倉 1.0 SOL。

### 步驟 8: 停止引擎（可選）

1. 找到 **POST /api/v1/follower/engine/stop** 端點
2. 點擊 "Execute"

## 觀察跟隨者反應的關鍵點

### 時間延遲
- 監控引擎每 10 秒輪詢一次
- 執行 Master 下單後，需要等待 10-15 秒
- 然後查看交易歷史確認跟單是否執行

### 成功指標
1. **交易歷史** 中出現新記錄
2. `status: "filled"` 表示成交
3. `amount` 正確計算（= master_position × follow_ratio）
4. `order_id` 不為空（MockExchange 返回的訂單 ID）

### 失敗排查
如果沒有看到跟單記錄：
1. 確認引擎已啟動（GET /api/v1/follower/engine/status）
2. 確認跟隨關係 `is_active: true`
3. 確認 Master 倉位 `position_size != 0`
4. 查看後端日誌：`docker logs -f ea_trading_backend`

## 快速測試命令

如果不想手動點擊，可以運行測試腳本：

```powershell
.\test_follower_engine.ps1
```

這個腳本會自動執行所有步驟並顯示結果。

## 進階測試

### 多個跟隨者

創建多個跟隨關係，測試一個 Master 對應多個 Follower：

```json
// Follower 2 (ratio=0.2)
{
  "follower_user_id": 3,
  "master_user_id": 1,
  "follow_ratio": 0.2,
  "follower_credential_id": 3,
  "master_credential_id": 1
}

// Follower 3 (ratio=0.05)
{
  "follower_user_id": 4,
  "master_user_id": 1,
  "follow_ratio": 0.05,
  "follower_credential_id": 4,
  "master_credential_id": 1
}
```

當 Master 開 1 BTC 時：
- Follower 1 開 0.1 BTC
- Follower 2 開 0.2 BTC
- Follower 3 開 0.05 BTC

## 注意事項

1. **credential_id 從 1 開始**：第一個憑證 ID 是 1，第二個是 2，依此類推
2. **等待時間**：執行 Master 下單後，務必等待 10-15 秒再查看結果
3. **Mock 模式**：當前使用 MockExchange，不會發起真實網路請求
4. **日誌查看**：`docker logs -f ea_trading_backend` 可以看到詳細的執行日誌

## 常見問題

**Q: 為什麼沒有看到跟單記錄？**
A: 等待 10-15 秒，監控引擎需要時間輪詢和執行。

**Q: 如何確認引擎正在運行？**
A: 使用 GET /api/v1/follower/engine/status 查看狀態。

**Q: 可以修改輪詢間隔嗎？**
A: 可以，修改 `follower_engine.py` 中的 `poll_interval` 參數。

**Q: 如何測試真實交易所？**
A: 將 `exchange_name` 從 "mock" 改為真實交易所名稱（如 "binance"），並提供真實的 API 憑證。
