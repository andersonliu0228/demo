# 測試觸發 Master 訂單（自動創建憑證）
# 此腳本測試修復後的 trigger-master-order 端點

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試觸發 Master 訂單（自動創建憑證）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# 測試 1: 使用不存在的憑證 ID（應該自動創建）
Write-Host "測試 1: 使用不存在的憑證 ID (應該自動創建)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$body = @{
    master_user_id = 1
    master_credential_id = 999  # 不存在的憑證 ID
    symbol = "BTC/USDT"
    position_size = 1.5
    entry_price = 50000.0
} | ConvertTo-Json

Write-Host "請求參數:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/test/trigger-master-order" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✅ 請求成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "回應內容:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    # 檢查是否自動創建了憑證
    if ($response.credential_info.auto_created -eq $true) {
        Write-Host ""
        Write-Host "✅ 憑證已自動創建！" -ForegroundColor Green
        Write-Host "   憑證 ID: $($response.credential_info.credential_id)" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "ℹ️  使用現有憑證" -ForegroundColor Blue
    }
    
} catch {
    Write-Host "❌ 請求失敗！" -ForegroundColor Red
    Write-Host "錯誤訊息: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "詳細錯誤:" -ForegroundColor Red
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# 測試 2: 再次使用相同的憑證 ID（應該使用現有憑證）
Write-Host ""
Write-Host "測試 2: 再次使用相同的憑證 ID (應該使用現有憑證)" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$body2 = @{
    master_user_id = 1
    master_credential_id = 999  # 剛才創建的憑證 ID
    symbol = "ETH/USDT"
    position_size = 2.0
    entry_price = 3000.0
} | ConvertTo-Json

Write-Host "請求參數:" -ForegroundColor Gray
Write-Host $body2 -ForegroundColor Gray
Write-Host ""

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/api/v1/test/trigger-master-order" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body2
    
    Write-Host "✅ 請求成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "回應內容:" -ForegroundColor Cyan
    $response2 | ConvertTo-Json -Depth 10 | Write-Host
    
    # 檢查是否使用現有憑證
    if ($response2.credential_info.auto_created -eq $false) {
        Write-Host ""
        Write-Host "✅ 使用現有憑證（未重複創建）" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ 請求失敗！" -ForegroundColor Red
    Write-Host "錯誤訊息: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "詳細錯誤:" -ForegroundColor Red
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
