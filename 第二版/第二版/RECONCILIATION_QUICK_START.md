# 對帳系統快速開始

## 🚀 5 分鐘快速測試

### 1. 確認系統運行
```powershell
docker ps
# 應該看到 ea_trading_backend 正在運行
```

### 2. 執行自動化測試
```powershell
.\test_reconciliation.ps1
```

### 3. 查看結果
測試腳本會自動執行以下操作：
- ✅ 登入系統
- ✅ 創建跟單設定（10% 跟單比例）
- ✅ Master 開倉 1.0 BTC → Follower 自動開倉 0.1 BTC
- ✅ Master 加倉到 2.0 BTC → Follower 自動補單到 0.2 BTC
- ✅ Master 減倉到 0.5 BTC → Follower 自動平倉到 0.05 BTC
- ✅ 查詢交易歷史

---

## 📊 核心概念

### 對帳 (Reconciliation)
系統每 3 秒檢查一次 Master 倉位，自動計算跟隨者應有的倉位，並執行補單或平倉操作。

### 計算公式
```
目標倉位 = Master 倉位 × 跟單比例
調整數量 = 目標倉位 - 當前倉位

如果 調整數量 > 0 → 補單（買入）
如果 調整數量 < 0 → 平倉（賣出）
如果 調整數量 = 0 → 不操作
```

### 範例
- Master 倉位：2.0 BTC
- 跟單比例：0.1 (10%)
- 目標倉位：2.0 × 0.1 = 0.2 BTC
- 當前倉位：0.1 BTC
- 調整數量：0.2 - 0.1 = 0.1 BTC
- 操作：買入 0.1 BTC（補單）

---

## 🔧 常用 API

### 查看跟單狀態
```powershell
$headers = @{ "Authorization" = "Bearer YOUR_TOKEN" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/status" -Headers $headers
```

### 查詢交易歷史
```powershell
# 查詢最近 10 筆交易
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/trades/history?limit=10" -Headers $headers

# 只查詢 BTC/USDT
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/trades/history?symbol=BTC/USDT" -Headers $headers

# 只查詢成功的交易
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/trades/history?status=success" -Headers $headers
```

### 更新跟單設定
```powershell
# 調整跟單比例為 20%
$body = @{ follow_ratio = 0.2 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/settings" `
    -Method PUT -Headers $headers -ContentType "application/json" -Body $body

# 暫停跟單
$body = @{ is_active = $false } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/settings" `
    -Method PUT -Headers $headers -ContentType "application/json" -Body $body
```

---

## 📁 相關文檔

- **詳細測試指南**：`對帳與交易歷史測試指南.md`
- **實作總結**：`對帳系統實作總結.md`
- **自動化測試腳本**：`test_reconciliation.ps1`

---

## ❓ 常見問題

**Q: 為什麼倉位沒有更新？**  
A: 等待至少 3 秒讓監控循環執行，或檢查是否有未解決的錯誤。

**Q: 如何查看詳細日誌？**  
A: `docker logs ea_trading_backend --tail 100`

**Q: 如何重置測試環境？**  
A: 清空資料表後重新測試（參考測試指南）

---

## 🎯 下一步

1. 閱讀完整測試指南了解更多測試場景
2. 查看實作總結了解技術細節
3. 開始整合真實交易所 API
