# 測試新前端設置
Write-Host "🧪 測試新前端設置" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 1. 檢查 Docker 容器狀態
Write-Host "`n📦 檢查 Docker 容器狀態..." -ForegroundColor Yellow
docker ps --filter "name=ea_trading"

# 2. 重啟前端容器
Write-Host "`n🔄 重啟前端容器..." -ForegroundColor Yellow
docker-compose restart frontend

# 3. 等待容器啟動
Write-Host "`n⏳ 等待前端容器啟動 (15秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 4. 檢查前端日誌
Write-Host "`n📋 檢查前端日誌 (最後 30 行)..." -ForegroundColor Yellow
docker logs ea_trading_frontend --tail 30

# 5. 測試前端連接
Write-Host "`n🌐 測試前端連接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ 前端連接成功! 狀態碼: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ 前端連接失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. 顯示訪問資訊
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✨ 測試完成!" -ForegroundColor Green
Write-Host "`n📍 訪問地址:" -ForegroundColor Yellow
Write-Host "   前端: http://localhost:3000" -ForegroundColor White
Write-Host "   後端: http://localhost:8000" -ForegroundColor White
Write-Host "   API 文檔: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n💡 提示:" -ForegroundColor Yellow
Write-Host "   - 直接訪問 http://localhost:3000 查看交易員管理面板" -ForegroundColor White
Write-Host "   - 使用搜尋和篩選功能測試客戶管理" -ForegroundColor White
Write-Host "   - 點擊狀態按鈕測試即時變色效果" -ForegroundColor White
