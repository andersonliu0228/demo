# Follower Engine 跟單監控引擎使用指南

## 概述

Follower Engine 是一個自動化跟單系統，能夠監控 Master 交易者的倉位變化，並根據設定的跟隨比例自動執行跟單交易。

## 核心功能

1. **跟隨關係管理** - 建立跟隨者與 Master 之間的關係
2. **倉位監控** - 每 10 秒輪詢一次 Master 的倉位變化
3. **Kelly 準則計算** - 根據 follow_ratio 自動計算跟隨倉位
4. **自動下單** - 使用 MockExchange 執行跟單交易
5. **交易日誌** - 記錄每次跟單的詳細資訊

## 使用流程

### 步驟 1: 創建 Mock 憑證

首先需要為 Master 和 Follower 創建 Mock Exchange 憑證。

```powershell
# 創建 Master 憑證
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"exchange_name\":\"mock\",\"api_key\":\"master_key_123\",\"api_secret\":\"master_secret_456\",\"label\":\"Master Mock\"}'

# 創建 Follower 憑證
curl.exe -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":2,\"exchange_name\":\"mock\",\"api_key\":\"follower_key_789\",\"api_secret\":\"follower_secret_012\",\"label\":\"Follower Mock\"}'
```

記下返回的 `credential_id`，後續步驟會用到。

### 步驟 2: 創建跟隨關係

建立 Follower 與 Master 之間的跟單關係。

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/relationships `
  -H "Content-Type: application/json" `
  -d '{\"follower_user_id\":2,\"master_user_id\":1,\"follow_ratio\":0.1,\"follower_credential_id\":2,\"master_credential_id\":1}'
```

參數說明：
- `follower_user_id`: 跟隨者用戶 ID
- `master_user_id`: Master 用戶 ID
- `follow_ratio`: 跟隨比例（0.1 = 10%，即 Master 開 1 BTC，Follower 開 0.1 BTC）
- `follower_credential_id`: 跟隨者的憑證 ID
- `master_credential_id`: Master 的憑證 ID

### 步驟 3: 啟動監控引擎

啟動背景監控引擎，開始輪詢 Master 倉位。

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/engine/start
```

### 步驟 4: 模擬 Master 下單

更新 Master 的倉位，觸發跟單引擎執行跟單。

```powershell
# Master 開多倉 BTC/USDT，倉位大小 1.0 BTC
curl.exe -X POST http://localhost:8000/api/v1/follower/master-position `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"BTC/USDT\",\"position_size\":1.0,\"entry_price\":50000.0}'
```

參數說明：
- `position_size`: 正數表示多倉，負數表示空倉，0 表示平倉
- `entry_price`: 開倉價格

### 步驟 5: 查看跟單結果

#### 查看交易歷史

```powershell
curl.exe http://localhost:8000/api/v1/follower/trade-history
```

返回示例：
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
    "order_id": "mock-order-uuid-123",
    "status": "filled",
    "error_message": null,
    "created_at": "2026-02-03T14:30:00",
    "executed_at": "2026-02-03T14:30:01"
  }
]
```

#### 查看 Master 倉位

```powershell
curl.exe http://localhost:8000/api/v1/follower/master-positions?master_user_id=1
```

#### 查看跟隨關係

```powershell
curl.exe http://localhost:8000/api/v1/follower/relationships
```

### 步驟 6: 停止監控引擎

```powershell
curl.exe -X POST http://localhost:8000/api/v1/follower/engine/stop
```

## Swagger UI 操作指南

訪問 http://localhost:8000/docs 使用 Swagger UI 進行測試。

### 完整測試流程

1. **POST /api/v1/credentials** - 創建 Master 和 Follower 憑證
2. **POST /api/v1/follower/relationships** - 創建跟隨關係
3. **POST /api/v1/follower/engine/start** - 啟動監控引擎
4. **POST /api/v1/follower/master-position** - 模擬 Master 下單
5. **GET /api/v1/follower/trade-history** - 查看跟單記錄

### 觀察跟隨者反應

當你執行步驟 4（模擬 Master 下單）後：

1. 監控引擎會在下一個輪詢週期（最多 10 秒）檢測到 Master 倉位變化
2. 自動計算跟隨者應有的倉位：`follower_amount = master_position * follow_ratio`
3. 使用 MockExchange 執行跟單交易
4. 記錄交易歷史到數據庫

你可以通過查看交易歷史來確認跟單是否成功執行。

## API 端點總覽

### 跟隨關係管理
- `POST /api/v1/follower/relationships` - 創建跟隨關係
- `GET /api/v1/follower/relationships` - 列出跟隨關係

### Master 倉位管理
- `POST /api/v1/follower/master-position` - 更新 Master 倉位（模擬下單）
- `GET /api/v1/follower/master-positions` - 列出 Master 倉位

### 交易歷史
- `GET /api/v1/follower/trade-history` - 查看跟單交易記錄

### 引擎控制
- `POST /api/v1/follower/engine/start` - 啟動監控引擎
- `POST /api/v1/follower/engine/stop` - 停止監控引擎
- `GET /api/v1/follower/engine/status` - 查看引擎狀態

## 測試場景

### 場景 1: 基本跟單

1. Master 開多倉 1.0 BTC
2. Follower (ratio=0.1) 自動開多倉 0.1 BTC

### 場景 2: 反向跟單

1. Master 開空倉 -1.0 BTC (position_size=-1.0)
2. Follower 自動開空倉 -0.1 BTC

### 場景 3: 平倉跟單

1. Master 平倉 (position_size=0)
2. Follower 自動平倉

### 場景 4: 多個跟隨者

1. 創建多個跟隨關係（不同的 follow_ratio）
2. Master 下單後，所有跟隨者按各自比例執行跟單

## 注意事項

1. **監控延遲**: 引擎每 10 秒輪詢一次，實際跟單可能有最多 10 秒延遲
2. **Mock 模式**: 當前使用 MockExchange，不會發起真實網路請求
3. **加密流程**: 即使是 Mock 模式，憑證仍會完整執行加密/解密流程
4. **錯誤處理**: 如果跟單失敗，會記錄在 trade_history 的 error_message 欄位

## 故障排除

### 引擎未啟動
```powershell
# 檢查引擎狀態
curl.exe http://localhost:8000/api/v1/follower/engine/status

# 如果未運行，啟動引擎
curl.exe -X POST http://localhost:8000/api/v1/follower/engine/start
```

### 跟單未執行
1. 確認跟隨關係的 `is_active` 為 `true`
2. 確認 Master 倉位已更新（position_size != 0）
3. 檢查後端日誌：`docker logs ea_trading_backend`

### 查看詳細日誌
```powershell
docker logs -f ea_trading_backend
```

## 下一步

- 整合真實交易所 API（替換 MockExchange）
- 實作風險控制（最大倉位限制、止損等）
- 添加 WebSocket 即時推送
- 實作更複雜的跟單策略（部分跟單、延遲跟單等）
