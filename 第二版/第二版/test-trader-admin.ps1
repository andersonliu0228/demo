# 測試客戶管理系統
# Test Trader Admin System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  客戶管理系統測試腳本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查 Docker 容器狀態
Write-Host "1. 檢查 Docker 容器狀態..." -ForegroundColor Yellow
docker ps --filter "name=ea_trading" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 2. 執行資料庫遷移
Write-Host "2. 執行資料庫遷移..." -ForegroundColor Yellow
docker exec ea_trading_backend alembic upgrade head
Write-Host ""

# 3. 重啟後端容器
Write-Host "3. 重啟後端容器..." -ForegroundColor Yellow
docker-compose restart backend
Start-Sleep -Seconds 5
Write-Host ""

# 4. 檢查後端日誌
Write-Host "4. 檢查後端日誌（最後 20 行）..." -ForegroundColor Yellow
docker logs ea_trading_backend --tail 20
Write-Host ""

# 5. 測試健康檢查
Write-Host "5. 測試後端健康檢查..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing
    Write-Host "✅ 後端健康檢查成功: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ 後端健康檢查失敗: $_" -ForegroundColor Red
}
Write-Host ""

# 6. 測試前端連接
Write-Host "6. 測試前端連接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ 前端連接成功: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ 前端連接失敗: $_" -ForegroundColor Red
}
Write-Host ""

# 7. 顯示訪問資訊
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  訪問資訊" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Green
Write-Host "客戶管理: http://localhost:3000/trader-admin" -ForegroundColor Green
Write-Host "後端 API: http://localhost:8000" -ForegroundColor Green
Write-Host "API 文檔: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# 8. 顯示測試步驟
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  測試步驟" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. 訪問 http://localhost:3000/login" -ForegroundColor White
Write-Host "2. 使用現有帳號登入" -ForegroundColor White
Write-Host "3. 點擊導航欄的「客戶管理」按鈕" -ForegroundColor White
Write-Host "4. 查看客戶列表（會顯示 Mock 數據）" -ForegroundColor White
Write-Host "5. 測試核准、暫停、刪除功能" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
