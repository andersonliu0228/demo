# EA Trading System - Docker 停止腳本

Write-Host "🛑 停止 EA Trading System..." -ForegroundColor Cyan
Write-Host ""

# 停止所有服務
Write-Host "📋 停止所有容器..." -ForegroundColor Yellow
docker-compose stop

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 所有服務已停止" -ForegroundColor Green
} else {
    Write-Host "❌ 停止服務時發生錯誤" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💡 提示:" -ForegroundColor Cyan
Write-Host "   重新啟動:    docker-compose start" -ForegroundColor White
Write-Host "   或使用:      .\docker-start.ps1" -ForegroundColor White
Write-Host "   完全清理:    docker-compose down -v" -ForegroundColor White
Write-Host ""
