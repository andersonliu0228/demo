# EA Trading System - Docker 快速啟動腳本
# 此腳本會自動啟動所有 Docker 服務並初始化資料庫

Write-Host "🐳 EA Trading System - Docker 啟動中..." -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker 是否運行
Write-Host "📋 檢查 Docker 狀態..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker 未運行！請先啟動 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker 正在運行" -ForegroundColor Green
Write-Host ""

# 檢查 .env 檔案
Write-Host "📋 檢查環境變數..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  未找到 .env 檔案，使用預設配置" -ForegroundColor Yellow
    Write-Host "   建議: 複製 .env.example 並設定 ENCRYPTION_KEY" -ForegroundColor Yellow
} else {
    Write-Host "✅ 找到 .env 檔案" -ForegroundColor Green
}
Write-Host ""

# 停止現有容器
Write-Host "🛑 停止現有容器..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "✅ 已停止現有容器" -ForegroundColor Green
Write-Host ""

# 構建並啟動服務
Write-Host "🔨 構建並啟動所有服務..." -ForegroundColor Yellow
Write-Host "   這可能需要幾分鐘時間（首次運行）..." -ForegroundColor Gray
docker-compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 服務啟動失敗！" -ForegroundColor Red
    Write-Host "   請查看錯誤訊息並檢查配置" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 服務已啟動" -ForegroundColor Green
Write-Host ""

# 等待服務啟動
Write-Host "⏳ 等待服務完全啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 檢查服務狀態
Write-Host "📊 檢查服務狀態..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 執行資料庫遷移
Write-Host "🗄️  執行資料庫遷移..." -ForegroundColor Yellow
docker-compose exec -T backend alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  資料庫遷移失敗，可能需要手動執行" -ForegroundColor Yellow
    Write-Host "   命令: docker-compose exec backend alembic upgrade head" -ForegroundColor Gray
} else {
    Write-Host "✅ 資料庫遷移完成" -ForegroundColor Green
}
Write-Host ""

# 顯示訪問資訊
Write-Host "🎉 系統啟動完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📍 訪問地址:" -ForegroundColor Cyan
Write-Host "   前端應用:    http://localhost:3000" -ForegroundColor White
Write-Host "   後端 API:    http://localhost:8000" -ForegroundColor White
Write-Host "   API 文檔:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 常用命令:" -ForegroundColor Cyan
Write-Host "   查看日誌:    docker-compose logs -f" -ForegroundColor White
Write-Host "   停止服務:    docker-compose stop" -ForegroundColor White
Write-Host "   重啟服務:    docker-compose restart" -ForegroundColor White
Write-Host "   完全清理:    docker-compose down -v" -ForegroundColor White
Write-Host ""
Write-Host "💡 提示: 首次使用請先註冊帳號，然後配置 API 憑證" -ForegroundColor Yellow
Write-Host ""

# 詢問是否打開瀏覽器
$openBrowser = Read-Host "是否要在瀏覽器中打開前端應用？(Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Host "✨ 準備就緒！開始使用 EA Trading System" -ForegroundColor Green
