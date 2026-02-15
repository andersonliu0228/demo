# PnL 與 Telegram 通知 - 快速啟動指南

## 🚀 快速開始

### 1. 配置 Telegram Bot（可選）

如果要啟用 Telegram 通知，請先配置 Bot：

```bash
# 1. 在 Telegram 中找到 @BotFather
# 2. 發送 /newbot 創建新 Bot
# 3. 獲取 Bot Token

# 4. 獲取 Chat ID
# 方法 1：發送訊息給 Bot，然後訪問：
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

# 方法 2：使用 @userinfobot 獲取你的 Chat ID
```

### 2. 更新環境變數

編輯 `.env` 文件：

```bash
# Telegram 通知配置（可選）
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ENABLED=true
```

### 3. 啟動系統

```powershell
# 停止現有容器
docker compose down

# 重新啟動
docker compose up -d

# 查看日誌
docker compose logs -f backend
```

### 4. 測試功能

#### 4.1 測試登入/登出
```powershell
# 1. 訪問前端
Start-Process "http://localhost:5173"

# 2. 使用測試帳號登入
# 用戶名: testuser
# 密碼: testpass123

# 3. 點擊右上角「登出」按鈕
# 4. 確認導向登入頁
```

#### 4.2 測試 PnL 顯示
```powershell
# 1. 登入 Dashboard
# 2. 查看「未實現盈虧」卡片
# 3. 確認顯示正確的數字和顏色
```

#### 4.3 測試 Telegram 通知
```powershell
# 觸發 Master 訂單
.\test-trigger-master-order.ps1

# 檢查 Telegram 是否收到通知
```

---

## 📊 功能展示

### 1. Navbar 與登出
- 顯示「EA Trading Dashboard」標題
- 顯示當前用戶名
- 點擊「登出」按鈕清除 Token 並導向登入頁

### 2. PnL 統計
- **未實現盈虧**：顯示當前持倉的盈虧
- **顏色標示**：
  - 綠色 = 盈利
  - 紅色 = 虧損
- **百分比顯示**：顯示盈虧百分比

### 3. Telegram 通知
- **交易成功**：下單成功時發送通知
- **交易失敗**：下單失敗時發送錯誤通知
- **對帳補單**：倉位對帳時發送通知
- **異步發送**：不阻塞主流程

### 4. CCXT 抽象層
- **統一介面**：所有交易所使用相同介面
- **易於切換**：切換交易所不需改動核心邏輯
- **Mock 模式**：開發測試使用 MockExchange

---

## 🔧 常見問題

### Q1: Telegram 通知沒有收到？

**檢查步驟**：
1. 確認 `.env` 中的 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` 正確
2. 確認 `TELEGRAM_ENABLED=true`
3. 重啟後端：`docker compose restart backend`
4. 查看日誌：`docker compose logs backend | Select-String "Telegram"`

### Q2: PnL 顯示為 0？

**原因**：
- 沒有持倉
- 持倉數據未同步

**解決方法**：
```powershell
# 1. 初始化測試數據
.\init-test-data.ps1

# 2. 觸發 Master 訂單
.\test-trigger-master-order.ps1

# 3. 等待 3 秒後刷新 Dashboard
```

### Q3: 登出後仍然可以訪問 Dashboard？

**原因**：
- 瀏覽器緩存

**解決方法**：
1. 清除瀏覽器緩存
2. 使用無痕模式測試
3. 手動清除 localStorage：
   ```javascript
   localStorage.clear()
   ```

### Q4: 前端顯示「後端連線：失敗」？

**檢查步驟**：
1. 確認後端運行：`docker compose ps`
2. 確認後端健康：`curl http://localhost:8000/health`
3. 查看後端日誌：`docker compose logs backend`

---

## 📝 API 端點

### Dashboard API
```bash
GET /api/v1/dashboard/summary
Authorization: Bearer <token>

# 回應包含 PnL 資訊
{
  "unrealized_pnl": 1250.50,
  "unrealized_pnl_percent": 12.5,
  "realized_pnl": 500.25,
  "realized_pnl_percent": 5.0,
  "total_pnl": 1750.75,
  "total_pnl_percent": 17.5,
  ...
}
```

### 認證 API
```bash
# 登入
POST /api/v1/auth/login
{
  "username": "testuser",
  "password": "testpass123"
}

# 回應
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "testuser"
}
```

---

## 🎯 測試腳本

### 完整系統測試
```powershell
# 1. 初始化數據
.\init-test-data.ps1

# 2. 觸發 Master 訂單
.\test-trigger-master-order.ps1

# 3. 檢查系統狀態
.\check-system-status.ps1

# 4. 查看 Dashboard
Start-Process "http://localhost:5173/dashboard"
```

### 單獨測試 Telegram
```powershell
# 使用 Python 測試
docker compose exec backend python -c "
from backend.app.services.notifier import get_notifier_service
import asyncio
import os

async def test():
    notifier = get_notifier_service(
        os.getenv('TELEGRAM_BOT_TOKEN'),
        os.getenv('TELEGRAM_CHAT_ID')
    )
    await notifier.notify_trade_success(
        user_id=1,
        username='testuser',
        symbol='BTC/USDT',
        side='buy',
        amount=0.1,
        price=50000.0,
        order_id='test_order_123'
    )

asyncio.run(test())
"
```

---

## 📚 相關文檔

- [PnL與Telegram通知完整實作總結.md](./PnL與Telegram通知完整實作總結.md) - 詳細實作說明
- [完整系統快速啟動指南.md](./完整系統快速啟動指南.md) - 系統啟動指南
- [完整系統自動化流水線_實作總結.md](./完整系統自動化流水線_實作總結.md) - 自動化流程

---

## ✅ 驗證清單

完成以下檢查確保系統正常運行：

- [ ] 後端啟動成功
- [ ] 前端啟動成功
- [ ] 可以正常登入
- [ ] 可以正常登出
- [ ] Dashboard 顯示 PnL 資訊
- [ ] PnL 顏色正確（綠色/紅色）
- [ ] Telegram 通知正常（如果啟用）
- [ ] 路由守衛正常工作

---

## 🎉 完成！

系統已經完整配置好 PnL 統計和 Telegram 通知功能！

如有問題，請查看：
- 後端日誌：`docker compose logs backend`
- 前端日誌：瀏覽器開發者工具 Console

---

**文檔版本**: 1.0.0  
**最後更新**: 2024-01-01  
**作者**: Kiro AI Assistant
