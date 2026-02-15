# 重啟前端容器（開發模式）

Write-Host "🔄 重啟前端容器..." -ForegroundColor Cyan
Write-Host ""

# 停止並移除前端容器
Write-Host "📋 停止前端容器..." -ForegroundColor Yellow
docker-compose rm -sf frontend

# 重新構建並啟動
Write-Host "🔨 構建並啟動前端（開發模式）..." -ForegroundColor Yellow
docker-compose up -d --build frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 前端容器已啟動" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 訪問地址:" -ForegroundColor Cyan
    Write-Host "   前端應用: http://localhost:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 提示: 修改代碼會自動熱更新" -ForegroundColor Yellow
    Write-Host ""
    
    # 等待幾秒後顯示日誌
    Write-Host "📊 查看日誌..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    docker-compose logs --tail=20 frontend
} else {
    Write-Host ""
    Write-Host "❌ 啟動失敗" -ForegroundColor Red
    Write-Host "   請查看錯誤訊息" -ForegroundColor Red
}

Write-Host ""
