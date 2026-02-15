# EA Trading System - 完整重啟腳本
# 此腳本會停止所有容器，清理，然後重新啟動

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EA Trading System - 完整重啟" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 停止所有容器
Write-Host "[1/5] 停止所有容器..." -ForegroundColor Yellow
docker compose stop
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 容器已停止" -ForegroundColor Green
} else {
    Write-Host "⚠️  停止容器時出現警告（可能沒有運行中的容器）" -ForegroundColor Yellow
}
Write-Host ""

# 2. 移除容器（保留數據卷）
Write-Host "[2/5] 移除容器..." -ForegroundColor Yellow
docker compose down
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 容器已移除" -ForegroundColor Green
} else {
    Write-Host "⚠️  移除容器時出現警告" -ForegroundColor Yellow
}
Write-Host ""

# 3. 清理未使用的資源
Write-Host "[3/5] 清理未使用的 Docker 資源..." -ForegroundColor Yellow
docker system prune -f
Write-Host "✅ 清理完成" -ForegroundColor Green
Write-Host ""

# 4. 重新啟動所有服務
Write-Host "[4/5] 啟動所有服務..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 服務啟動成功" -ForegroundColor Green
} else {
    Write-Host "❌ 服務啟動失敗" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 5. 等待服務就緒
Write-Host "[5/5] 等待服務就緒..." -ForegroundColor Yellow
Write-Host "   等待 30 秒讓服務完全啟動..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# 檢查容器狀態
Write-Host ""
Write-Host "📊 容器狀態:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 測試後端健康檢查
Write-Host "🔍 測試後端 API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "✅ 後端 API 正常運行" -ForegroundColor Green
    Write-Host "   狀態: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  後端 API 尚未就緒，可能需要更多時間啟動" -ForegroundColor Yellow
    Write-Host "   請稍後手動測試: http://localhost:8000/health" -ForegroundColor Gray
}
Write-Host ""

# 完成
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  重啟完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 訪問地址:" -ForegroundColor Yellow
Write-Host "   前端: http://localhost:5173" -ForegroundColor White
Write-Host "   後端: http://localhost:8000" -ForegroundColor White
Write-Host "   API 文檔: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📋 下一步:" -ForegroundColor Yellow
Write-Host "   1. 訪問前端: http://localhost:5173" -ForegroundColor White
Write-Host "   2. 登入測試帳號:" -ForegroundColor White
Write-Host "      用戶名: testuser" -ForegroundColor Cyan
Write-Host "      密碼: testpass123" -ForegroundColor Cyan
Write-Host "   3. 檢查 Navbar 是否正常顯示" -ForegroundColor White
Write-Host ""
Write-Host "🔧 管理命令:" -ForegroundColor Yellow
Write-Host "   查看日誌: docker compose logs -f" -ForegroundColor White
Write-Host "   停止服務: docker compose stop" -ForegroundColor White
Write-Host "   查看狀態: docker ps" -ForegroundColor White
Write-Host ""
