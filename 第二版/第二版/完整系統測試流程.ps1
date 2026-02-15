# 完整系統自動化流水線測試流程
# 包含數據初始化、系統啟動、功能測試

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完整系統自動化流水線測試" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步驟 1: 啟動 Docker 系統
Write-Host "[1/5] 啟動 Docker 系統..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
.\docker-start.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker 啟動失敗！" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "等待服務啟動完成（30秒）..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# 步驟 2: 初始化測試數據
Write-Host ""
Write-Host "[2/5] 初始化測試數據..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
.\init-test-data.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 數據初始化失敗！" -ForegroundColor Red
    exit 1
}

# 步驟 3: 檢查系統狀態
Write-Host ""
Write-Host "[3/5] 檢查系統狀態..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
.\check-system-status.ps1

# 步驟 4: 測試觸發 Master 訂單
Write-Host ""
Write-Host "[4/5] 測試觸發 Master 訂單..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$triggerBody = @{
    master_user_id = 1
    master_credential_id = 1
    symbol = "BTC/USDT"
    position_size = 1.5
    entry_price = 50000.0
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/test/trigger-master-order" `
        -Method Post `
        -ContentType "application/json" `
        -Body $triggerBody
    
    Write-Host "✅ Master 訂單觸發成功！" -ForegroundColor Green
    Write-Host "   - 交易對: $($response.master_info.symbol)" -ForegroundColor Gray
    Write-Host "   - 倉位: $($response.master_info.new_position_size)" -ForegroundColor Gray
    Write-Host "   - 跟隨者數量: $($response.followers_count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Master 訂單觸發失敗！" -ForegroundColor Red
    Write-Host "錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

# 步驟 5: 測試前端訪問
Write-Host ""
Write-Host "[5/5] 測試前端訪問..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ 前端訪問成功！" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 前端訪問失敗！" -ForegroundColor Red
    Write-Host "錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

# 總結
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "系統訪問地址：" -ForegroundColor Yellow
Write-Host "  前端: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  後端 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Swagger 文檔: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "測試帳號：" -ForegroundColor Yellow
Write-Host "  用戶名: testuser" -ForegroundColor Cyan
Write-Host "  密碼: testpass123" -ForegroundColor Cyan
Write-Host ""
Write-Host "功能測試：" -ForegroundColor Yellow
Write-Host "  1. 使用測試帳號登入前端" -ForegroundColor Gray
Write-Host "  2. 查看儀表板實時數據（每3秒自動更新）" -ForegroundColor Gray
Write-Host "  3. 點擊「跟單狀態」開關測試啟用/停用" -ForegroundColor Gray
Write-Host "  4. 觀察 Master 倉位和 Follower 倉位對比" -ForegroundColor Gray
Write-Host "  5. 檢查錯誤通知是否正常顯示" -ForegroundColor Gray
Write-Host ""
