# Mock Exchange 使用指南

## 概述

Mock Exchange 是一個模擬交易所，用於開發和測試環境，**不會發起任何真實的網路請求**。它完整實現了加密流程，確保整個「加密 → 存儲 → 取出 → 解密」的鏈條是完整的。

## 特點

✅ **完整的加密流程**：即使是 Mock 模式，也必須經過 crypto_service 加密 Secret 存入 DB  
✅ **無網路請求**：不會連接真實交易所，安全可靠  
✅ **模擬真實行為**：模擬 fetch_balance()、create_order() 等 API  
✅ **開發友好**：快速測試，無需真實 API Key  

## 快速開始

### 步驟 1：綁定 Mock Exchange 憑證

使用任意的 API Key 和 Secret（會被加密存儲）：

```powershell
curl -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{
    "exchange_name": "mock",
    "api_key": "mock_api_key_12345",
    "api_secret": "mock_api_secret_67890",
    "verify": true
  }'
```

**回應範例**：
```json
{
  "id": 1,
  "exchange_name": "mock",
  "api_key_masked": "mock...2345",
  "is_active": true,
  "last_verified_at": "2026-02-03T14:00:00",
  "created_at": "2026-02-03T14:00:00",
  "updated_at": "2026-02-03T14:00:00"
}
```

### 步驟 2：測試 Mock 餘額查詢

```powershell
curl "http://localhost:8000/api/v1/test/mock-balance?credential_id=1&user_id=1"
```

**回應範例**：
```json
{
  "success": true,
  "credential_info": {
    "id": 1,
    "exchange": "mock",
    "api_key_masked": "mock...2345",
    "created_at": "2026-02-03T14:00:00",
    "last_verified_at": "2026-02-03T14:00:00"
  },
  "encryption_flow": {
    "step_1": "從資料庫取出加密憑證 ✓",
    "step_2": "使用 CryptoService 解密 ✓",
    "step_3": "創建 MockExchange 實例 ✓",
    "step_4": "調用 fetch_balance() ✓",
    "encrypted_secret_length": 156,
    "decrypted_secret_length": 21,
    "encryption_verified": true
  },
  "balance": {
    "total": {
      "USDT": 10000.0,
      "BTC": 0.5,
      "ETH": 5.0,
      "BNB": 10.0
    },
    "free": {
      "USDT": 8000.0,
      "BTC": 0.3,
      "ETH": 3.0,
      "BNB": 8.0
    },
    "used": {
      "USDT": 2000.0,
      "BTC": 0.2,
      "ETH": 2.0,
      "BNB": 2.0
    },
    "info": {
      "mock": true,
      "timestamp": "2026-02-03T14:00:00"
    }
  },
  "note": "這是 Mock 數據，不是真實交易所餘額"
}
```

### 步驟 3：測試 Mock 下單

```powershell
curl -X POST "http://localhost:8000/api/v1/test/mock-order?credential_id=1&user_id=1&symbol=BTC/USDT&order_type=limit&side=buy&amount=0.01&price=50000"
```

**回應範例**：
```json
{
  "success": true,
  "credential_info": {
    "id": 1,
    "exchange": "mock",
    "api_key_masked": "mock...2345"
  },
  "encryption_flow": {
    "decryption_verified": true,
    "api_key_used": "mock_api...",
    "secret_length": 21
  },
  "order": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "clientOrderId": "mock_a1b2c3d4",
    "timestamp": 1738579200000,
    "datetime": "2026-02-03T14:00:00",
    "symbol": "BTC/USDT",
    "type": "limit",
    "side": "buy",
    "price": 50000.0,
    "amount": 0.01,
    "cost": 500.0,
    "filled": 0.01,
    "remaining": 0.0,
    "status": "closed",
    "fee": {
      "cost": 0.5,
      "currency": "USDT"
    },
    "trades": [],
    "info": {
      "mock": true,
      "api_key_used": "mock_api...",
      "decrypted_secret_length": 21
    }
  },
  "note": "這是 Mock 訂單，不會在真實交易所執行"
}
```

## 加密流程驗證

### 測試加密解密

```powershell
curl "http://localhost:8000/api/v1/test/encryption-flow?test_secret=my_secret_123"
```

**回應範例**：
```json
{
  "success": true,
  "original_text": "my_secret_123",
  "original_length": 13,
  "encrypted_text": "gAAAAABpgfQ2D9-U4ypiSRoZ21Md5nRXEhkRE5znKDd7C...",
  "encrypted_length": 156,
  "decrypted_text": "my_secret_123",
  "decrypted_length": 13,
  "verification": {
    "match": true,
    "encryption_adds_overhead": true,
    "roundtrip_successful": true
  }
}
```

## API 端點說明

### 1. GET /api/v1/test/mock-balance

查詢 Mock Exchange 餘額，展示完整的加密流程。

**參數**：
- `credential_id` (必填): 憑證 ID
- `user_id` (必填): 用戶 ID

**流程**：
1. 從資料庫取出加密的憑證
2. 使用 CryptoService 解密 API Secret
3. 使用解密後的憑證創建 MockExchange 實例
4. 調用 fetch_balance() 獲取模擬餘額
5. 返回餘額和加密流程資訊

### 2. POST /api/v1/test/mock-order

創建 Mock 訂單，驗證加密流程。

**參數**：
- `credential_id` (必填): 憑證 ID
- `user_id` (必填): 用戶 ID
- `symbol` (可選): 交易對，預設 "BTC/USDT"
- `order_type` (可選): 訂單類型，預設 "limit"
- `side` (可選): 買賣方向，預設 "buy"
- `amount` (可選): 數量，預設 0.01
- `price` (可選): 價格，預設 50000.0

**流程**：
1. 從資料庫取出並解密憑證
2. 創建 MockExchange 實例
3. 調用 create_order() 創建模擬訂單
4. 返回訂單資訊和加密流程驗證

### 3. GET /api/v1/test/encryption-flow

測試加密解密功能。

**參數**：
- `test_secret` (可選): 測試用的明文，預設 "my_test_secret_12345"

**功能**：
- 展示 CryptoService 的加密和解密過程
- 驗證加密後的密文長度大於原文
- 驗證解密後能還原原文

## Mock Exchange 模擬數據

### 固定餘額

```json
{
  "USDT": 10000.0,
  "BTC": 0.5,
  "ETH": 5.0,
  "BNB": 10.0
}
```

### 訂單行為

- **立即成交**：所有訂單模擬為立即完全成交
- **手續費**：固定 0.1% 手續費
- **訂單 ID**：隨機生成 UUID
- **狀態**：始終為 "closed"（已成交）

## 使用場景

### 1. 開發階段

在開發新功能時，使用 Mock Exchange 可以：
- 快速測試 API 邏輯
- 驗證加密流程
- 無需真實 API Key
- 避免觸發交易所 API 限制

### 2. 測試階段

在測試時，使用 Mock Exchange 可以：
- 編寫單元測試和整合測試
- 模擬各種交易場景
- 驗證錯誤處理邏輯
- 確保加密解密正確

### 3. 演示階段

在演示系統時，使用 Mock Exchange 可以：
- 展示系統功能
- 無需真實資金
- 安全可靠
- 快速響應

## 安全性說明

### ✅ 安全特性

1. **完整加密流程**：即使是 Mock 模式，Secret 也會被加密存儲
2. **無網路請求**：不會連接任何外部服務
3. **隔離環境**：Mock 數據與真實數據完全隔離
4. **日誌記錄**：所有操作都有詳細日誌

### ⚠️ 注意事項

1. **僅用於開發**：Mock Exchange 僅用於開發和測試環境
2. **不要用於生產**：生產環境應使用真實交易所
3. **數據不持久**：Mock 數據不會保存，每次都是固定值
4. **無真實交易**：所有訂單都是模擬的，不會產生真實交易

## 與真實交易所的對比

| 特性 | Mock Exchange | 真實交易所 |
|------|---------------|-----------|
| 網路請求 | ❌ 無 | ✅ 有 |
| 加密流程 | ✅ 完整 | ✅ 完整 |
| API Key 驗證 | ❌ 不驗證 | ✅ 驗證 |
| 餘額數據 | 固定模擬值 | 真實餘額 |
| 訂單執行 | 模擬成交 | 真實成交 |
| 手續費 | 固定 0.1% | 實際費率 |
| 響應速度 | 極快 | 取決於網路 |
| 使用場景 | 開發/測試 | 生產環境 |

## 常見問題

### Q: Mock Exchange 會連接真實交易所嗎？

A: 不會。Mock Exchange 完全在本地運行，不會發起任何網路請求。

### Q: Mock 模式下的 Secret 會被加密嗎？

A: 會。即使是 Mock 模式，API Secret 也會經過完整的加密流程存儲到資料庫。

### Q: 可以用 Mock Exchange 測試真實交易嗎？

A: 不可以。Mock Exchange 只返回模擬數據，不會執行真實交易。

### Q: Mock 餘額可以修改嗎？

A: 目前是固定值（10000 USDT 等）。如需修改，可以編輯 `MockExchange.fetch_balance()` 方法。

### Q: 如何切換到真實交易所？

A: 只需將 `exchange_name` 從 "mock" 改為真實交易所名稱（如 "binance"），並使用真實的 API Key 和 Secret。

## 下一步

1. 閱讀 `如何使用.md` 了解完整系統使用方法
2. 查看 `ARCHITECTURE.md` 了解系統架構
3. 訪問 http://localhost:8000/docs 查看完整 API 文檔
4. 準備好後，切換到真實交易所進行實際交易

## 技術細節

### MockExchange 類別結構

```python
class MockExchange:
    def __init__(self, api_key, api_secret, passphrase=None)
    def fetch_balance() -> Dict
    def fetch_open_orders(symbol=None, limit=None) -> List[Dict]
    def create_order(symbol, order_type, side, amount, price=None) -> Dict
```

### 加密流程

```
用戶輸入 API Secret
    ↓
CryptoService.encrypt()
    ↓
存儲到資料庫（encrypted_api_secret）
    ↓
從資料庫讀取
    ↓
CryptoService.decrypt()
    ↓
創建 MockExchange(api_key, decrypted_secret)
    ↓
調用 MockExchange API
```

## 總結

Mock Exchange 提供了一個安全、快速、完整的開發測試環境，確保加密流程的正確性，同時避免了真實交易所的風險和限制。在開發階段充分使用 Mock Exchange，可以大大提高開發效率和代碼質量。

祝開發順利！🚀
