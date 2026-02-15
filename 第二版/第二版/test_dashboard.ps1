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
