# 測試 Navbar 顯示功能
# 此腳本驗證登入後 Navbar 是否正確顯示

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  測試 Navbar 顯示功能" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查 Docker 容器狀態
Write-Host "[1/4] 檢查 Docker 容器狀態..." -ForegroundColor Yellow
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "ea-trading"
if ($containers) {
    Write-Host "✅ Docker 容器運行中" -ForegroundColor Green
    $containers | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "❌ Docker 容器未運行，請先執行 docker-start.ps1" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. 測試後端健康檢查
Write-Host "[2/4] 測試後端 API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ 後端 API 正常" -ForegroundColor Green
    Write-Host "   狀態: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "❌ 後端 API 無法連接" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. 測試登入並獲取 Token
Write-Host "[3/4] 測試登入功能..." -ForegroundColor Yellow
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    Write-Host "✅ 登入成功" -ForegroundColor Green
    Write-Host "   用戶名: $($loginResponse.username)" -ForegroundColor Gray
    Write-Host "   用戶ID: $($loginResponse.user_id)" -ForegroundColor Gray
    Write-Host "   Token: $($loginResponse.access_token.Substring(0, 20))..." -ForegroundColor Gray
    
    $token = $loginResponse.access_token
    $username = $loginResponse.username
} catch {
    Write-Host "❌ 登入失敗" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 4. 測試 Dashboard API（驗證 Token）
Write-Host "[4/4] 測試 Dashboard API..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Dashboard API 正常" -ForegroundColor Green
    Write-Host "   用戶名: $($dashboard.username)" -ForegroundColor Gray
    Write-Host "   跟單狀態: $(if ($dashboard.is_active) { '已啟用' } else { '已停用' })" -ForegroundColor Gray
    Write-Host "   總持倉價值: $($dashboard.total_position_value) USDT" -ForegroundColor Gray
} catch {
    Write-Host "❌ Dashboard API 失敗" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 測試結果總結
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  測試結果總結" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 所有後端 API 測試通過" -ForegroundColor Green
Write-Host ""
Write-Host "📋 前端測試步驟：" -ForegroundColor Yellow
Write-Host "   1. 打開瀏覽器訪問: http://localhost:5173" -ForegroundColor White
Write-Host "   2. 使用以下憑證登入：" -ForegroundColor White
Write-Host "      用戶名: testuser" -ForegroundColor Cyan
Write-Host "      密碼: testpass123" -ForegroundColor Cyan
Write-Host "   3. 登入後應該看到：" -ForegroundColor White
Write-Host "      ✓ 頂部藍色導覽列 (Navbar)" -ForegroundColor Green
Write-Host "      ✓ 左側顯示「EA Trading Dashboard」" -ForegroundColor Green
Write-Host "      ✓ 右側顯示用戶名「$username」" -ForegroundColor Green
Write-Host "      ✓ 右側紅色「登出」按鈕" -ForegroundColor Green
Write-Host "   4. 點擊「登出」按鈕應該：" -ForegroundColor White
Write-Host "      ✓ 清除 localStorage" -ForegroundColor Green
Write-Host "      ✓ 跳轉回登入頁面" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 如果看不到 Navbar，請檢查：" -ForegroundColor Yellow
Write-Host "   1. 瀏覽器開發者工具 Console 是否有錯誤" -ForegroundColor White
Write-Host "   2. localStorage 是否正確儲存 user 和 token" -ForegroundColor White
Write-Host "   3. 前端容器是否正常運行 (docker ps)" -ForegroundColor White
Write-Host ""
