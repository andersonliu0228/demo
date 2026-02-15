# EA Trading System - 系統狀態檢查

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        EA Trading System - 系統狀態檢查                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker
Write-Host "🐳 Docker 狀態" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Docker 正在運行" -ForegroundColor Green
} else {
    Write-Host "  ❌ Docker 未運行" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 檢查容器狀態
Write-Host "📦 容器狀態" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

$containers = @(
    @{Name="ea_trading_postgres"; Display="PostgreSQL"; Port="5432"},
    @{Name="ea_trading_redis"; Display="Redis"; Port="6379"},
    @{Name="ea_trading_backend"; Display="Backend API"; Port="8000"},
    @{Name="ea_trading_frontend"; Display="Frontend"; Port="3000"}
)

foreach ($container in $containers) {
    $status = docker ps --filter "name=$($container.Name)" --format "{{.Status}}" 2>$null
    if ($status) {
        Write-Host "  ✅ $($container.Display) (Port $($container.Port))" -ForegroundColor Green
        Write-Host "     狀態: $status" -ForegroundColor Gray
    } else {
        Write-Host "  ❌ $($container.Display) (Port $($container.Port))" -ForegroundColor Red
        Write-Host "     狀態: 未運行" -ForegroundColor Gray
    }
}
Write-Host ""

# 檢查服務可訪問性
Write-Host "🌐 服務可訪問性" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray

# 檢查後端
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✅ 後端 API (http://localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 後端 API (http://localhost:8000)" -ForegroundColor Red
}

# 檢查前端
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✅ 前端應用 (http://localhost:3000)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 前端應用 (http://localhost:3000)" -ForegroundColor Red
}

# 檢查 API 文檔
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✅ API 文檔 (http://localhost:8000/docs)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ API 文檔 (http://localhost:8000/docs)" -ForegroundColor Red
}
Write-Host ""

# 檢查資源使用
Write-Host "💻 資源使用" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
$stats = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>$null
if ($stats) {
    $stats | ForEach-Object {
        if ($_ -match "ea_trading") {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  無法獲取資源使用資訊" -ForegroundColor Yellow
}
Write-Host ""

# 顯示最近的日誌錯誤
Write-Host "📋 最近的錯誤日誌" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
$errors = docker-compose logs --tail=50 2>&1 | Select-String -Pattern "ERROR|Error|error|WARN|Warning" | Select-Object -First 5
if ($errors) {
    foreach ($error in $errors) {
        Write-Host "  $error" -ForegroundColor Red
    }
} else {
    Write-Host "  ✅ 沒有發現錯誤" -ForegroundColor Green
}
Write-Host ""

# 顯示訪問資訊
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      訪問資訊                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  前端應用:  http://localhost:3000" -ForegroundColor White
Write-Host "  後端 API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API 文檔:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# 顯示快速命令
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      快速命令                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  查看日誌:      .\docker-logs.ps1" -ForegroundColor White
Write-Host "  重啟前端:      .\docker-restart-frontend.ps1" -ForegroundColor White
Write-Host "  測試系統:      .\test-docker-frontend.ps1" -ForegroundColor White
Write-Host "  停止服務:      docker-compose stop" -ForegroundColor White
Write-Host "  重啟服務:      docker-compose restart" -ForegroundColor White
Write-Host ""
