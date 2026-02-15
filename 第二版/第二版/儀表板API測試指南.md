# 儀表板 API 測試指南

## 功能概述

儀表板聚合 API 專為前端設計，一次性返回所有儀表板所需的資訊：

1. **用戶資訊** - 當前用戶 ID、用戶名、跟單設定
2. **總持倉價值** - 計算所有倉位的總價值
3. **我的倉位** - 跟隨者的所有倉位詳情
4. **Master 最新動作** - Master 最近的倉位變動
5. **Master 倉位** - Master 的所有倉位
6. **引擎狀態** - 跟單引擎運行狀態（Running/Stopped）
7. **最近成功交易** - 最近 5 筆成功的跟單記錄
8. **錯誤狀態** - 是否有未解決的錯誤

---

## API 端點

### GET /api/v1/dashboard/summary

**認證**: 需要 JWT Token

**響應範例**:
```json
{
  "user_id": 2,
  "username": "testuser",
  "is_active": true,
  "follow_ratio": 0.1,
  "master_user_id": 1,
  "total_position_value": 5000.0,
  "my_positions": [
    {
      "symbol": "BTC/USDT",
      "position_size": 0.1,
      "entry_price": 50000.0,
      "current_value": 5000.0
    }
  ],
  "master_latest_activity": {
    "symbol": "BTC/USDT",
    "action": "持倉 1.0",
    "position_size": 1.0,
    "entry_price": 50000.0,
    "timestamp": "2026-02-04T12:00:00"
  },
  "master_positions": [
    {
      "symbol": "BTC/USDT",
      "position_size": 1.0,
      "entry_price": 50000.0,
      "current_value": 50000.0
    }
  ],
  "engine_status": {
    "is_running": true,
    "status": "Running",
    "poll_interval": 3
  },
  "recent_successful_trades": [
    {
      "id": 1,
      "timestamp": "2026-02-04T12:00:00",
      "symbol": "BTC/USDT",
      "action": "補單_增加倉位",
      "side": "buy",
      "amount": 0.1,
      "status": "success",
      "execution_time_ms": 150
    }
  ],
  "has_unresolved_errors": false,
  "unresolved_error_count": 0
}
```

---

## 測試步驟

### 1. 登入並獲取 Token

```powershell
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body @{
        username = "testuser"
        password = "testpass123"
    }

$token = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $token"
}
```

### 2. 查看初始儀表板狀態

```powershell
$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

Write-Host "=== 儀表板摘要 ===" -ForegroundColor Cyan
Write-Host "用戶: $($dashboard.username)" -ForegroundColor White
Write-Host "跟單狀態: $(if ($dashboard.is_active) { '啟用' } else { '停用' })" -ForegroundColor $(if ($dashboard.is_active) { "Green" } else { "Red" })
Write-Host "跟單比例: $($dashboard.follow_ratio * 100)%" -ForegroundColor White
Write-Host "總持倉價值: $($dashboard.total_position_value) USDT" -ForegroundColor Yellow
Write-Host "引擎狀態: $($dashboard.engine_status.status)" -ForegroundColor $(if ($dashboard.engine_status.is_running) { "Green" } else { "Red" })
Write-Host "我的倉位數量: $($dashboard.my_positions.Count)" -ForegroundColor White
Write-Host "Master 倉位數量: $($dashboard.master_positions.Count)" -ForegroundColor White
Write-Host "最近成功交易: $($dashboard.recent_successful_trades.Count) 筆" -ForegroundColor White
```

### 3. 觸發 Master 訂單

```powershell
# 觸發 Master 開倉 1.0 BTC
$trigger = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/test/trigger-master-order" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{
        master_user_id = 1
        master_credential_id = 1
        symbol = "BTC/USDT"
        position_size = 1.0
        entry_price = 50000.0
    } | ConvertTo-Json)

Write-Host "`n=== Master 訂單已觸發 ===" -ForegroundColor Green
Write-Host "倉位變動: $($trigger.master_info.old_position_size) -> $($trigger.master_info.new_position_size)"
Write-Host "跟隨者數量: $($trigger.followers_count)"
Write-Host "預期交易數: $($trigger.expected_trades.Count)"
```

### 4. 立即查看儀表板更新（Master 倉位）

```powershell
# 立即查詢，應該看到 Master 倉位已更新
$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

Write-Host "`n=== Master 倉位已更新 ===" -ForegroundColor Cyan
if ($dashboard.master_latest_activity) {
    Write-Host "最新動作: $($dashboard.master_latest_activity.action)"
    Write-Host "交易對: $($dashboard.master_latest_activity.symbol)"
    Write-Host "倉位: $($dashboard.master_latest_activity.position_size)"
    Write-Host "時間: $($dashboard.master_latest_activity.timestamp)"
}
```

### 5. 等待 3 秒後查看跟隨者倉位更新

```powershell
Write-Host "`n等待 3 秒讓跟單引擎執行對帳..." -ForegroundColor Gray
Start-Sleep -Seconds 3

$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

Write-Host "`n=== 跟隨者倉位已更新 ===" -ForegroundColor Cyan
Write-Host "總持倉價值: $($dashboard.total_position_value) USDT" -ForegroundColor Yellow

foreach ($pos in $dashboard.my_positions) {
    Write-Host "`n倉位: $($pos.symbol)"
    Write-Host "  數量: $($pos.position_size)"
    Write-Host "  開倉價: $($pos.entry_price)"
    Write-Host "  價值: $($pos.current_value) USDT"
}

Write-Host "`n最近成功交易: $($dashboard.recent_successful_trades.Count) 筆" -ForegroundColor Green
foreach ($trade in $dashboard.recent_successful_trades | Select-Object -First 3) {
    Write-Host "  [$($trade.timestamp)] $($trade.action) - $($trade.amount) $($trade.symbol)"
}
```

---

## 完整測試腳本

創建 `test_dashboard.ps1` 檔案：

```powershell
# 儀表板 API 完整測試腳本

Write-Host "=== EA Trading 儀表板 API 測試 ===" -ForegroundColor Cyan

# 1. 登入
Write-Host "`n[1/5] 登入系統..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body @{
        username = "testuser"
        password = "testpass123"
    }

$token = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $token"
}
Write-Host "✓ 登入成功" -ForegroundColor Green

# 2. 查看初始狀態
Write-Host "`n[2/5] 查看初始儀表板狀態..." -ForegroundColor Yellow
$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

Write-Host "✓ 用戶: $($dashboard.username)" -ForegroundColor Green
Write-Host "  跟單狀態: $(if ($dashboard.is_active) { '啟用 ✓' } else { '停用 ✗' })"
Write-Host "  引擎狀態: $($dashboard.engine_status.status)"
Write-Host "  總持倉價值: $($dashboard.total_position_value) USDT"

# 3. 觸發 Master 訂單
Write-Host "`n[3/5] 觸發 Master 開倉 2.0 BTC..." -ForegroundColor Yellow
$trigger = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/test/trigger-master-order" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{
        master_user_id = 1
        master_credential_id = 1
        symbol = "BTC/USDT"
        position_size = 2.0
        entry_price = 50000.0
    } | ConvertTo-Json)

Write-Host "✓ Master 訂單已觸發" -ForegroundColor Green
Write-Host "  倉位變動: $($trigger.master_info.old_position_size) -> $($trigger.master_info.new_position_size)"

# 4. 立即查看 Master 倉位更新
Write-Host "`n[4/5] 立即查看儀表板（Master 倉位應已更新）..." -ForegroundColor Yellow
$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

if ($dashboard.master_latest_activity) {
    Write-Host "✓ Master 最新動作: $($dashboard.master_latest_activity.action)" -ForegroundColor Green
    Write-Host "  交易對: $($dashboard.master_latest_activity.symbol)"
    Write-Host "  倉位: $($dashboard.master_latest_activity.position_size)"
}

# 5. 等待 3 秒後查看跟隨者倉位更新
Write-Host "`n[5/5] 等待 3 秒讓跟單引擎執行對帳..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

$dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
    -Method GET `
    -Headers $headers

Write-Host "✓ 跟隨者倉位已更新" -ForegroundColor Green
Write-Host "  總持倉價值: $($dashboard.total_position_value) USDT"
Write-Host "  我的倉位數量: $($dashboard.my_positions.Count)"
Write-Host "  最近成功交易: $($dashboard.recent_successful_trades.Count) 筆"

# 顯示詳細資訊
Write-Host "`n=== 我的倉位 ===" -ForegroundColor Cyan
foreach ($pos in $dashboard.my_positions) {
    Write-Host "$($pos.symbol): $($pos.position_size) @ $($pos.entry_price) = $($pos.current_value) USDT"
}

Write-Host "`n=== Master 倉位 ===" -ForegroundColor Cyan
foreach ($pos in $dashboard.master_positions) {
    Write-Host "$($pos.symbol): $($pos.position_size) @ $($pos.entry_price) = $($pos.current_value) USDT"
}

Write-Host "`n=== 最近交易 ===" -ForegroundColor Cyan
foreach ($trade in $dashboard.recent_successful_trades | Select-Object -First 3) {
    Write-Host "[$($trade.timestamp)] $($trade.action) - $($trade.amount) $($trade.symbol) ($($trade.execution_time_ms)ms)"
}

Write-Host "`n=== 測試完成 ===" -ForegroundColor Cyan
Write-Host "儀表板 API 運作正常！" -ForegroundColor Green
```

---

## CORS 測試

### 從前端測試 CORS

如果你有前端應用（React/Vue/Next.js），可以使用以下代碼測試：

```javascript
// 測試儀表板 API
async function testDashboard() {
  const token = localStorage.getItem('token'); // 假設 token 已存儲
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/dashboard/summary', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include' // 允許發送 cookies
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Dashboard data:', data);
    return data;
  } catch (error) {
    console.error('Error fetching dashboard:', error);
  }
}

// 測試觸發 Master 訂單
async function triggerMasterOrder() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/test/trigger-master-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        master_user_id: 1,
        master_credential_id: 1,
        symbol: 'BTC/USDT',
        position_size: 1.5,
        entry_price: 50000.0
      })
    });
    
    const data = await response.json();
    console.log('Master order triggered:', data);
    
    // 立即刷新儀表板
    setTimeout(() => testDashboard(), 100);
    
    // 3 秒後再次刷新（等待跟單完成）
    setTimeout(() => testDashboard(), 3000);
  } catch (error) {
    console.error('Error triggering order:', error);
  }
}
```

### 驗證 CORS 設定

```powershell
# 使用 curl 測試 CORS preflight
curl -X OPTIONS http://localhost:8000/api/v1/dashboard/summary `
  -H "Origin: http://localhost:3000" `
  -H "Access-Control-Request-Method: GET" `
  -H "Access-Control-Request-Headers: Authorization" `
  -v
```

應該看到以下 Headers：
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

---

## 數據流程

### 觸發 Master 訂單後的數據更新流程

```
1. POST /test/trigger-master-order
   ↓
2. 立即更新 master_positions 表
   ↓
3. GET /dashboard/summary (立即查詢)
   → Master 倉位已更新 ✓
   → 跟隨者倉位尚未更新 (等待引擎)
   ↓
4. 跟單引擎檢測到變動（最多 3 秒）
   ↓
5. 執行對帳並更新 follower_positions 表
   ↓
6. 記錄到 trade_logs 表
   ↓
7. GET /dashboard/summary (3 秒後查詢)
   → Master 倉位 ✓
   → 跟隨者倉位已更新 ✓
   → 最近交易已更新 ✓
```

---

## 前端整合建議

### 1. 定期輪詢儀表板

```javascript
// 每 5 秒刷新一次儀表板
setInterval(async () => {
  const dashboard = await testDashboard();
  updateUI(dashboard);
}, 5000);
```

### 2. 觸發訂單後立即刷新

```javascript
async function handleTriggerOrder() {
  await triggerMasterOrder();
  
  // 立即刷新（顯示 Master 倉位變動）
  await testDashboard();
  
  // 3 秒後再次刷新（顯示跟隨者倉位變動）
  setTimeout(async () => {
    await testDashboard();
  }, 3000);
}
```

### 3. 使用 WebSocket（未來優化）

目前使用輪詢機制，未來可以改用 WebSocket 實現即時推送：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateUI(data);
};
```

---

## 常見問題

### Q1: 為什麼 Master 倉位立即更新，但跟隨者倉位需要等待？

**A**: Master 倉位是直接寫入資料庫的，所以立即可見。跟隨者倉位需要等待跟單引擎的下一個輪詢週期（最多 3 秒）來執行對帳。

### Q2: 如何確認 CORS 設定正確？

**A**: 在瀏覽器開發者工具的 Network 標籤中，檢查 API 請求的 Response Headers，應該包含 `Access-Control-Allow-Origin` 等 CORS 相關 Headers。

### Q3: 儀表板 API 返回的總持倉價值如何計算？

**A**: 目前使用簡化計算：`總價值 = Σ(|倉位大小| × 開倉價格)`。實際應用中應該使用當前市場價格。

### Q4: 如何在前端顯示引擎狀態？

**A**: 使用 `engine_status.status` 字段，值為 "Running" 或 "Stopped"，可以用綠色/紅色指示燈顯示。

---

## API 端點總覽

### 儀表板
- `GET /api/v1/dashboard/summary` - 獲取儀表板摘要 ✨ 新增

### 測試
- `POST /api/v1/test/trigger-master-order` - 觸發 Master 訂單（已優化）

### 其他相關端點
- `GET /api/v1/follow-config/status` - 獲取跟單狀態
- `GET /api/v1/trades/history` - 查詢交易歷史
- `POST /api/v1/follower/start` - 啟動跟單引擎
- `POST /api/v1/follower/stop` - 停止跟單引擎

---

## 下一步

1. 在前端實作儀表板 UI
2. 使用 Chart.js 或 ECharts 顯示倉位圖表
3. 實作即時通知（交易成功/失敗）
4. 加入 WebSocket 支援（未來優化）
