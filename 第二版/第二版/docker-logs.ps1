# EA Trading System - 查看日誌腳本

param(
    [string]$Service = "",
    [int]$Lines = 100
)

Write-Host "📋 EA Trading System - 日誌查看器" -ForegroundColor Cyan
Write-Host ""

if ($Service -eq "") {
    Write-Host "📊 查看所有服務日誌 (最近 $Lines 行)..." -ForegroundColor Yellow
    Write-Host "   按 Ctrl+C 停止" -ForegroundColor Gray
    Write-Host ""
    docker-compose logs -f --tail=$Lines
} else {
    Write-Host "📊 查看 $Service 服務日誌 (最近 $Lines 行)..." -ForegroundColor Yellow
    Write-Host "   按 Ctrl+C 停止" -ForegroundColor Gray
    Write-Host ""
    docker-compose logs -f --tail=$Lines $Service
}
