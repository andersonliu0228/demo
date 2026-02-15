# EA Trading System - 清理腳本
# 警告: 此腳本會刪除所有容器、網路和資料卷（包括資料庫資料）

Write-Host "⚠️  EA Trading System - 完全清理" -ForegroundColor Red
Write-Host ""
Write-Host "此操作將會:" -ForegroundColor Yellow
Write-Host "  - 停止並移除所有容器" -ForegroundColor White
Write-Host "  - 刪除所有網路" -ForegroundColor White
Write-Host "  - 刪除所有資料卷（包括資料庫資料）" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "確定要繼續嗎？這將刪除所有資料！(yes/no)"

if ($confirm -ne "yes") {
    Write-Host "❌ 操作已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🗑️  清理中..." -ForegroundColor Yellow

# 停止並移除所有容器、網路、卷
docker-compose down -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 清理完成" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 重新啟動系統:" -ForegroundColor Cyan
    Write-Host "   .\docker-start.ps1" -ForegroundColor White
} else {
    Write-Host "❌ 清理時發生錯誤" -ForegroundColor Red
    exit 1
}

Write-Host ""
