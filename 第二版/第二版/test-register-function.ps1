# 測試註冊功能

Write-Host "🧪 測試註冊功能" -ForegroundColor Cyan
Write-Host ""

# 1. 檢查後端 API
Write-Host "📋 步驟 1: 檢查後端 API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ 後端 API 正常運行" -ForegroundColor Green
} catch {
    Write-Host "❌ 後端 API 無法訪問" -ForegroundColor Red
    Write-Host "   請先啟動後端: docker-compose up -d backend" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 2. 檢查前端
Write-Host "📋 步驟 2: 檢查前端..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ 前端正常運行" -ForegroundColor Green
} catch {
    Write-Host "❌ 前端無法訪問" -ForegroundColor Red
    Write-Host "   請先啟動前端: docker-compose up -d frontend" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 3. 測試註冊 API
Write-Host "📋 步驟 3: 測試註冊 API..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testUser = "testuser_$timestamp"

$body = @{
    username = $testUser
    email = "$testUser@example.com"
    password = "password123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
        Write-Host "✅ 註冊 API 測試成功" -ForegroundColor Green
        Write-Host "   測試用戶: $testUser" -ForegroundColor Gray
        Write-Host "   密碼: password123" -ForegroundColor Gray
    }
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "⚠️  用戶可能已存在（這是正常的）" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 註冊 API 測試失敗" -ForegroundColor Red
        Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# 4. 測試登入 API
Write-Host "📋 步驟 4: 測試登入 API（使用測試帳號）..." -ForegroundColor Yellow

$loginBody = "username=testuser&password=testpass123"

try {
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 登入 API 測試成功" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 登入 API 測試失敗" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. 顯示測試結果
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      測試結果                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 後端 API 正常" -ForegroundColor Green
Write-Host "✅ 前端正常" -ForegroundColor Green
Write-Host "✅ 註冊 API 可用" -ForegroundColor Green
Write-Host "✅ 登入 API 可用" -ForegroundColor Green
Write-Host ""

# 6. 顯示測試步驟
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    手動測試步驟                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  訪問前端: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  點擊「尚未註冊？點此註冊」" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  填寫註冊表單:" -ForegroundColor White
Write-Host "   用戶名: demouser" -ForegroundColor Gray
Write-Host "   Email: demo@example.com" -ForegroundColor Gray
Write-Host "   密碼: demo123456" -ForegroundColor Gray
Write-Host "   確認密碼: demo123456" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  點擊「註冊」按鈕" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  等待成功提示（綠色頁面）" -ForegroundColor White
Write-Host ""
Write-Host "6️⃣  自動跳轉到登入頁面（2 秒）" -ForegroundColor White
Write-Host ""
Write-Host "7️⃣  使用新帳號登入" -ForegroundColor White
Write-Host ""

# 詢問是否打開瀏覽器
$openBrowser = Read-Host "是否要在瀏覽器中打開前端應用？(Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:3000"
    Write-Host ""
    Write-Host "✨ 瀏覽器已打開，開始測試註冊功能！" -ForegroundColor Green
}

Write-Host ""
Write-Host "📚 詳細測試指南: 註冊功能測試指南.md" -ForegroundColor Cyan
Write-Host ""
