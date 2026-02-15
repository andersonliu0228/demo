# 對帳與交易歷史完整測試腳本

Write-Host "=== EA Trading 對帳系統測試 ===" -ForegroundColor Cyan

# 1. 登入
Write-Host "`n[1/6] 登入系統..." -ForegroundColor Yellow
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

# 2. 創建跟單設定
Write-Host "`n[2/6] 創建跟單設定..." -ForegroundColor Yellow
$followSettings = @{
    master_user_id = 1
    master_credential_id = 1
    follower_credential_id = 2
    follow_ratio = 0.1
    is_active = $true
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/settings" `
        -Method POST `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $followSettings
    Write-Host "✓ 跟單設定創建成功" -ForegroundColor Green
} catch {
    Write-Host "✓ 跟單設定已存在" -ForegroundColor Green
}

# 3. Master 開倉 1.0 BTC
Write-Host "`n[3/6] Master 開倉 1.0 BTC..." -ForegroundColor Yellow
$masterPosition = @{
    master_user_id = 1
    master_credential_id = 1
    symbol = "BTC/USDT"
    position_size = 1.0
    entry_price = 50000.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follower/master-position" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $masterPosition

Write-Host "等待 3 秒讓系統處理..." -ForegroundColor Gray
Start-Sleep -Seconds 3

$status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/status" `
    -Method GET `
    -Headers $headers

Write-Host "✓ Master: 1.0 BTC → Follower: $($status.my_positions[0].position_size) BTC" -ForegroundColor Green

# 4. Master 加倉到 2.0 BTC
Write-Host "`n[4/6] Master 加倉到 2.0 BTC..." -ForegroundColor Yellow
$masterPosition = @{
    master_user_id = 1
    master_credential_id = 1
    symbol = "BTC/USDT"
    position_size = 2.0
    entry_price = 50000.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follower/master-position" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $masterPosition

Write-Host "等待 3 秒讓系統處理..." -ForegroundColor Gray
Start-Sleep -Seconds 3

$status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/status" `
    -Method GET `
    -Headers $headers

Write-Host "✓ Master: 2.0 BTC → Follower: $($status.my_positions[0].position_size) BTC" -ForegroundColor Green

# 5. Master 減倉到 0.5 BTC
Write-Host "`n[5/6] Master 減倉到 0.5 BTC..." -ForegroundColor Yellow
$masterPosition = @{
    master_user_id = 1
    master_credential_id = 1
    symbol = "BTC/USDT"
    position_size = 0.5
    entry_price = 50000.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follower/master-position" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $masterPosition

Write-Host "等待 3 秒讓系統處理..." -ForegroundColor Gray
Start-Sleep -Seconds 3

$status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/follow-config/status" `
    -Method GET `
    -Headers $headers

Write-Host "✓ Master: 0.5 BTC → Follower: $($status.my_positions[0].position_size) BTC" -ForegroundColor Green

# 6. 查詢交易歷史
Write-Host "`n[6/6] 查詢交易歷史..." -ForegroundColor Yellow
$history = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/trades/history?limit=10" `
    -Method GET `
    -Headers $headers

Write-Host "✓ 找到 $($history.Count) 筆交易記錄" -ForegroundColor Green

Write-Host "`n=== 最近 5 筆交易 ===" -ForegroundColor Cyan
$history | Select-Object -First 5 | ForEach-Object {
    Write-Host "`n[$($_.timestamp)]" -ForegroundColor Gray
    Write-Host "  操作: $($_.follower_action)" -ForegroundColor White
    Write-Host "  方向: $($_.side) | 數量: $($_.follower_amount)" -ForegroundColor White
    Write-Host "  狀態: $($_.status) | 成功: $($_.is_success)" -ForegroundColor $(if ($_.is_success) { "Green" } else { "Red" })
}

Write-Host "`n=== 測試完成 ===" -ForegroundColor Cyan
