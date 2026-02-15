# 測試前端路由和白屏問題
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "前端路由測試腳本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查容器狀態
Write-Host "1. 檢查 Docker 容器狀態..." -ForegroundColor Yellow
docker ps --filter "name=ea_trading"
Write-Host ""

# 2. 測試後端健康
Write-Host "2. 測試後端健康檢查..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✅ 後端狀態: $($response.StatusCode) - $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "❌ 後端連線失敗: $_" -ForegroundColor Red
}
Write-Host ""

# 3. 測試前端首頁
Write-Host "3. 測試前端首頁..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($response.Content -match "EA Trading") {
        Write-Host "✅ 前端首頁載入成功" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 前端首頁載入但內容異常" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 前端連線失敗: $_" -ForegroundColor Red
}
Write-Host ""

# 4. 檢查前端日誌
Write-Host "4. 檢查前端容器日誌（最後 20 行）..." -ForegroundColor Yellow
docker logs ea_trading_frontend --tail 20
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 在瀏覽器打開 http://localhost:3000" -ForegroundColor White
Write-Host "2. 應該會自動跳轉到 /login 頁面（因為沒有 token）" -ForegroundColor White
Write-Host "3. 使用測試帳號登入：testuser / testpass123" -ForegroundColor White
Write-Host "4. 登入後應該會跳轉到 /dashboard" -ForegroundColor White
Write-Host ""
Write-Host "如果看到白屏，請按 F12 打開開發者工具查看 Console 錯誤" -ForegroundColor Yellow
