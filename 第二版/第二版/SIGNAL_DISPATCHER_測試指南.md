# Signal Dispatcher 跟單核心引擎測試指南

## 概述

Signal Dispatcher（跟單核心引擎）是一個完整的自動化跟單系統，具備以下核心功能：

1. **監控循環 (Monitoring Loop)** - 每 5 秒檢查一次 Master 持倉
2. **倉位變動檢測** - 智能檢測 Master 倉位變化
3. **跟單邏輯 (Copy Logic)** - 根據 Ratio 計算目標倉位
4. **同步下單** - 完整的 try-except 保護
5. **資料庫持久化** - trade_logs 詳細記錄每次操作

## 核心改進

### 1. 更快的輪詢間隔
- 從 10 秒改為 **5 秒**
- 更快響應 Master 的倉位變化

### 2. 智能變動檢測
- 追蹤上次檢查的倉位狀態
- 只在倉位真正變動時執行跟單
- 避免重複下單

### 3. 詳細的 Trade Logs
新增 `trade_logs` 表，記錄：
- **下單時間** (timestamp)
- **Master 動作** (master_action: open_long, open_short, close_position)
- **跟隨者動作** (follower_action: follow_long, follow_short, follow_close)
- **執行狀態** (status: success, failed, pending)
- **執行耗時** (execution_time_ms)
- **錯誤訊息** (error_message)

### 4. 完整的錯誤處理
- 每個跟單操作都有 try-except 保護
- 失敗不會影響其他跟隨者
- 詳細記錄錯誤原因

## 測試流程

### 步驟 1: 創建測試憑證

```powershell
# Master 憑證
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"exchange_name\":\"mock\",\"api_key\":\"master_key\",\"api_secret\":\"master_secret\",\"label\":\"Master\"}'

# Follower 1 憑證 (ratio=0.1)
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":2,\"exchange_name\":\"mock\",\"api_key\":\"follower1_key\",\"api_secret\":\"follower1_secret\",\"label\":\"Follower1\"}'

# Follower 2 憑證 (ratio=0.2)
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":3,\"exchange_name\":\"mock\",\"api_key\":\"follower2_key\",\"api_secret\":\"follower2_secret\",\"label\":\"Follower2\"}'
```

### 步驟 2: 創建跟隨關係

```powershell
# Follower 1 (10% 跟隨)
curl.exe -X POST http://localhost:8000/api/v1/follower/relationships `
  -H "Content-Type: application/json" `
  -d '{\"follower_user_id\":2,\"master_user_id\":1,\"follow_ratio\":0.1,\"follower_credential_id\":2,\"master_credential_id\":1}'

# Follower 2 (20% 跟隨)
curl.exe -X POST http://localhost:8000/api/v1/follower/relationships `
  -H "Content-Type: application/json" `
  -d '{\"follower_user_id\":3,\"master_user_id\":1,\"follow_ratio\":0.2,\"follower_credential_id\":3,\"master_credential_id\":1}'
```

### 步驟 3: 啟動監控引擎

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/engine/start
```

### 步驟 4: 模擬 Master 開多倉

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/master-position `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"BTC/USDT\",\"position_size\":1.0,\"entry_price\":50000.0}'
```

**預期結果**：
- Master 開 1.0 BTC 多倉
- Follower 1 自動開 0.1 BTC 多倉
- Follower 2 自動開 0.2 BTC 多倉

### 步驟 5: 等待並查看結果

```powershell
# 等待 6 秒（讓引擎檢測並執行）
Start-Sleep -Seconds 6

# 查看 Trade Logs
curl.exe http://localhost:8000/api/v1/follower/trade-logs
```

**預期輸出**：
```json
[
  {
    "id": 1,
    "timestamp": "2026-02-03T...",
    "master_user_id": 1,
    "master_action": "open_long",
    "master_symbol": "BTC/USDT",
    "master_position_size": 1.0,
    "master_entry_price": 50000.0,
    "follower_user_id": 2,
    "follower_action": "follow_long",
    "follower_ratio": 0.1,
    "follower_amount": 0.1,
    "order_id": "mock-order-xxx",
    "status": "success",
    "is_success": true,
    "execution_time_ms": 15
  },
  {
    "id": 2,
    "timestamp": "2026-02-03T...",
    "master_user_id": 1,
    "master_action": "open_long",
    "master_symbol": "BTC/USDT",
    "master_position_size": 1.0,
    "follower_user_id": 3,
    "follower_action": "follow_long",
    "follower_ratio": 0.2,
    "follower_amount": 0.2,
    "order_id": "mock-order-yyy",
    "status": "success",
    "is_success": true,
    "execution_time_ms": 18
  }
]
```

### 步驟 6: 查看統計資訊

```powershell
curl.exe http://localhost:8000/api/v1/follower/trade-logs/stats
```

**預期輸出**：
```json
{
  "total_trades": 2,
  "successful_trades": 2,
  "failed_trades": 0,
  "success_rate": 100.0,
  "average_execution_time_ms": 16.5
}
```

## 進階測試場景

### 場景 1: Master 增加倉位

```powershell
# Master 增加到 2.0 BTC
curl.exe -X POST http://localhost:8000/api/v1/follower/master-position `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"BTC/USDT\",\"position_size\":2.0,\"entry_price\":51000.0}'

# 等待 6 秒
Start-Sleep -Seconds 6

# 查看日誌
curl.exe http://localhost:8000/api/v1/follower/trade-logs
```

**預期**：
- 檢測到倉位從 1.0 變為 2.0
- Follower 1 增加到 0.2 BTC
- Follower 2 增加到 0.4 BTC

### 場景 2: Master 平倉

```powershell
# Master 平倉
curl.exe -X POST http://localhost:8000/api/v1/follower/master-position `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"BTC/USDT\",\"position_size\":0,\"entry_price\":null}'

# 等待 6 秒
Start-Sleep -Seconds 6

# 查看日誌
curl.exe http://localhost:8000/api/v1/follower/trade-logs
```

**預期**：
- master_action: "close_position"
- follower_action: "follow_close"
- 所有跟隨者平倉

### 場景 3: Master 開空倉

```powershell
# Master 開空倉
curl.exe -X POST http://localhost:8000/api/v1/follower/master-position `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"ETH/USDT\",\"position_size\":-5.0,\"entry_price\":3000.0}'

# 等待 6 秒
Start-Sleep -Seconds 6

# 查看日誌
curl.exe http://localhost:8000/api/v1/follower/trade-logs
```

**預期**：
- master_action: "open_short"
- follower_action: "follow_short"
- Follower 1: -0.5 ETH
- Follower 2: -1.0 ETH

## 監控引擎日誌

查看詳細的引擎運行日誌：

```powershell
docker logs -f ea_trading_backend
```

**日誌示例**：
```
INFO: [14:30:00] 開始新一輪監控檢查
INFO: 檢查 2 個跟隨關係
INFO: Master 1 有 1 個倉位
INFO: 檢測到 Master 1 倉位變動: BTC/USDT 0 -> 1.0
INFO: 分發信號給 2 個跟隨者 - 交易對: BTC/USDT, Master 倉位: 1.0
INFO: [跟隨者 2] 準備跟單 - Master動作: open_long, 跟隨數量: 0.1
INFO: [跟隨者 3] 準備跟單 - Master動作: open_long, 跟隨數量: 0.2
INFO: [跟隨者 2] 跟單成功 - 訂單ID: mock-order-xxx, 耗時: 15ms
INFO: [跟隨者 3] 跟單成功 - 訂單ID: mock-order-yyy, 耗時: 18ms
INFO: 跟單完成 - 成功: 2, 失敗: 0
DEBUG: 本輪監控完成，耗時: 0.05 秒
```

## API 端點總覽

### 新增端點

1. **GET /api/v1/follower/trade-logs**
   - 查看詳細的交易日誌
   - 支援過濾：master_user_id, follower_user_id, status
   - 限制返回數量：limit (預設 100)

2. **GET /api/v1/follower/trade-logs/stats**
   - 獲取交易統計
   - 成功率、總交易次數、平均執行時間

### 現有端點

- POST /api/v1/follower/relationships - 創建跟隨關係
- GET /api/v1/follower/relationships - 列出跟隨關係
- POST /api/v1/follower/master-position - 更新 Master 倉位
- GET /api/v1/follower/master-positions - 列出 Master 倉位
- GET /api/v1/follower/trade-history - 查看交易歷史
- POST /api/v1/follower/engine/start - 啟動引擎
- POST /api/v1/follower/engine/stop - 停止引擎
- GET /api/v1/follower/engine/status - 查看引擎狀態

## 在 Swagger UI 中測試

訪問 http://localhost:8000/docs

### 完整測試流程

1. **POST /api/v1/credentials** - 創建 3 個憑證（1 Master + 2 Followers）
2. **POST /api/v1/follower/relationships** - 創建 2 個跟隨關係
3. **POST /api/v1/follower/engine/start** - 啟動引擎
4. **POST /api/v1/follower/master-position** - 模擬 Master 開倉
5. **等待 6 秒**
6. **GET /api/v1/follower/trade-logs** - 查看詳細日誌
7. **GET /api/v1/follower/trade-logs/stats** - 查看統計

## 核心特性驗證

### ✅ 監控循環 (5 秒輪詢)
- 查看日誌確認每 5 秒執行一次檢查

### ✅ 倉位變動檢測
- 只在倉位真正變動時執行跟單
- 避免重複下單

### ✅ Ratio 計算
- Follower 1 (0.1): Master 1.0 → Follower 0.1
- Follower 2 (0.2): Master 1.0 → Follower 0.2

### ✅ 同步下單
- 所有跟隨者並行執行
- 完整的 try-except 保護

### ✅ 資料庫持久化
- trade_logs 記錄所有操作
- 包含時間、動作、狀態、耗時

## 故障排除

### 問題 1: 跟單未執行
**檢查**：
1. 引擎是否啟動：`GET /api/v1/follower/engine/status`
2. 是否等待足夠時間（至少 6 秒）
3. 查看後端日誌：`docker logs -f ea_trading_backend`

### 問題 2: 跟單失敗
**檢查**：
1. 查看 trade_logs 的 error_message
2. 確認憑證是否正確
3. 查看後端日誌的詳細錯誤

### 問題 3: 重複下單
**不應該發生**：
- 引擎會追蹤上次倉位狀態
- 只在倉位變動時執行跟單

## 性能指標

- **輪詢間隔**: 5 秒
- **響應延遲**: 最多 5 秒
- **執行耗時**: 通常 10-30ms
- **並行處理**: 支援多個跟隨者同時執行

## 下一步

- 整合真實交易所 API
- 添加 WebSocket 即時推送（0 延遲）
- 實作風險控制（最大倉位、止損）
- 添加跟單策略（部分跟單、延遲跟單）
