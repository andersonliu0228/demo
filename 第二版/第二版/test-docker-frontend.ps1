# 測試 Docker 前端開發模式

Write-Host "🧪 測試 Docker 前端開發模式" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查 Docker 狀態
Write-Host "📋 步驟 1: 檢查 Docker 狀態..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker 未運行！請先啟動 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker 正在運行" -ForegroundColor Green
Write-Host ""

# 2. 檢查容器狀態
Write-Host "📋 步驟 2: 檢查容器狀態..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 3. 測試後端 API
Write-Host "📋 步驟 3: 測試後端 API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 後端 API 正常運行" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 後端 API 無法訪問" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. 測試前端
Write-Host "📋 步驟 4: 測試前端..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 前端正常運行" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 前端無法訪問" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 嘗試重啟前端容器..." -ForegroundColor Yellow
    docker-compose restart frontend
    Start-Sleep -Seconds 5
}
Write-Host ""

# 5. 顯示前端日誌
Write-Host "📋 步驟 5: 查看前端日誌（最近 20 行）..." -ForegroundColor Yellow
docker-compose logs --tail=20 frontend
Write-Host ""

# 6. 顯示訪問資訊
Write-Host "🎉 測試完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📍 訪問地址:" -ForegroundColor Cyan
Write-Host "   前端應用:    http://localhost:3000" -ForegroundColor White
Write-Host "   後端 API:    http://localhost:8000" -ForegroundColor White
Write-Host "   API 文檔:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示:" -ForegroundColor Cyan
Write-Host "   1. 打開瀏覽器訪問 http://localhost:3000" -ForegroundColor White
Write-Host "   2. 檢查右上角的 API 連接狀態指示器" -ForegroundColor White
Write-Host "   3. 修改 frontend/src/App.jsx 測試熱更新" -ForegroundColor White
Write-Host ""
Write-Host "🔧 常用命令:" -ForegroundColor Cyan
Write-Host "   查看日誌:    docker-compose logs -f frontend" -ForegroundColor White
Write-Host "   重啟前端:    .\docker-restart-frontend.ps1" -ForegroundColor White
Write-Host "   停止服務:    docker-compose stop" -ForegroundColor White
Write-Host ""

# 詢問是否打開瀏覽器
$openBrowser = Read-Host "是否要在瀏覽器中打開前端應用？(Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:3000"
}
