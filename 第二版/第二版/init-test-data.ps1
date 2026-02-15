# 初始化測試數據腳本
# 在 Docker 容器中執行 Python 腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "初始化測試數據" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "正在 Docker 容器中執行初始化腳本..." -ForegroundColor Yellow
Write-Host ""

docker compose exec backend python scripts/init_test_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 初始化完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 初始化失敗！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}
