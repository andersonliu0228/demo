# 創建測試用戶

Write-Host "🔧 創建測試用戶..." -ForegroundColor Cyan
Write-Host ""

# 測試帳號資訊
$username = "demo2026"
$email = "demo2026@example.com"
$password = "demo123456"

Write-Host "📋 測試帳號資訊:" -ForegroundColor Yellow
Write-Host "   用戶名: $username" -ForegroundColor White
Write-Host "   Email: $email" -ForegroundColor White
Write-Host "   密碼: $password" -ForegroundColor White
Write-Host ""

# 創建請求體
$body = @{
    username = $username
    email = $email
    password = $password
} | ConvertTo-Json

Write-Host "🌐 正在註冊用戶..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing
    
    Write-Host "✅ 註冊成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "回應:" -ForegroundColor Gray
    Write-Host $response.Content -ForegroundColor Gray
    Write-Host ""
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "⚠️  用戶可能已存在，嘗試登入..." -ForegroundColor Yellow
    } else {
        Write-Host "❌ 註冊失敗" -ForegroundColor Red
        Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 請確認:" -ForegroundColor Yellow
        Write-Host "   1. 後端是否運行: docker-compose ps backend" -ForegroundColor White
        Write-Host "   2. 查看後端日誌: docker-compose logs backend" -ForegroundColor White
        exit 1
    }
}

Write-Host ""
Write-Host "🔐 測試登入..." -ForegroundColor Yellow

$loginBody = "username=$username&password=$password"

try {
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $loginBody `
        -UseBasicParsing
    
    Write-Host "✅ 登入成功！" -ForegroundColor Green
    Write-Host ""
    
    $token = ($response.Content | ConvertFrom-Json).access_token
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
    
} catch {
    Write-Host "❌ 登入失敗" -ForegroundColor Red
    Write-Host "   錯誤: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    測試帳號資訊                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  用戶名: $username" -ForegroundColor White
Write-Host "  密碼: $password" -ForegroundColor White
Write-Host "  Email: $email" -ForegroundColor White
Write-Host ""
Write-Host "💡 使用此帳號登入前端: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
