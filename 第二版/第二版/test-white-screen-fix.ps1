# 測試白屏修復與登出邏輯
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  測試白屏修復與登出邏輯" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查前端容器狀態
Write-Host "[1] 檢查前端容器狀態..." -ForegroundColor Yellow
docker ps --filter "name=frontend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# 2. 重啟前端容器以應用修復
Write-Host "[2] 重啟前端容器..." -ForegroundColor Yellow
docker-compose restart frontend
Start-Sleep -Seconds 3
Write-Host "✅ 前端容器已重啟" -ForegroundColor Green
Write-Host ""

# 3. 檢查前端日誌
Write-Host "[3] 檢查前端日誌（最後 20 行）..." -ForegroundColor Yellow
docker-compose logs --tail=20 frontend
Write-Host ""

# 4. 測試路由配置
Write-Host "[4] 測試路由配置..." -ForegroundColor Yellow
Write-Host ""

Write-Host "測試 1: 訪問根路徑 / (應重定向到 /login)" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    Write-Host "  狀態碼: $($response.StatusCode)" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 302 -or $_.Exception.Response.StatusCode -eq 301) {
        Write-Host "  ✅ 正確重定向" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  狀態: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
Write-Host ""

Write-Host "測試 2: 訪問 /login (應正常顯示)" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/login" -UseBasicParsing
    Write-Host "  ✅ 登入頁面可訪問 (狀態碼: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 登入頁面無法訪問: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "測試 3: 訪問 /register (應正常顯示)" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/register" -UseBasicParsing
    Write-Host "  ✅ 註冊頁面可訪問 (狀態碼: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 註冊頁面無法訪問: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. 修復總結
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修復總結" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 已修復的問題：" -ForegroundColor Green
Write-Host "  1. 路由配置：/ 現在重定向到 /login 而非 /dashboard" -ForegroundColor White
Write-Host "  2. Navbar 位置：移到 App.jsx 層級，只在已登入時顯示" -ForegroundColor White
Write-Host "  3. 用戶資訊：使用安全的可選鏈語法 (username || 'User')" -ForegroundColor White
Write-Host "  4. 登出邏輯：使用 replace: true 避免返回問題" -ForegroundColor White
Write-Host "  5. 錯誤處理：加強 localStorage 解析的錯誤處理" -ForegroundColor White
Write-Host ""

Write-Host "📋 測試步驟：" -ForegroundColor Yellow
Write-Host "  1. 打開瀏覽器訪問 http://localhost:3000" -ForegroundColor White
Write-Host "  2. 應該看到登入頁面（不是白屏）" -ForegroundColor White
Write-Host "  3. 使用測試帳號登入：testuser / password123" -ForegroundColor White
Write-Host "  4. 登入後應該看到 Dashboard 和 Navbar" -ForegroundColor White
Write-Host "  5. 點擊右上角的「登出」按鈕" -ForegroundColor White
Write-Host "  6. 應該返回登入頁面，且無法通過瀏覽器返回鍵回到 Dashboard" -ForegroundColor White
Write-Host ""

Write-Host "🔍 如果仍有問題，請檢查：" -ForegroundColor Yellow
Write-Host "  1. 瀏覽器控制台 (F12) 是否有錯誤訊息" -ForegroundColor White
Write-Host "  2. Network 標籤是否有 API 請求失敗" -ForegroundColor White
Write-Host "  3. localStorage 中是否正確儲存了 token 和 user" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！請在瀏覽器中驗證修復效果" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
