# 用戶認證系統完整測試腳本
# EA Trading Backend - User Authentication System Test

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "用戶認證系統測試開始" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 測試 1: 註冊新用戶
Write-Host "測試 1: 註冊新用戶 Alice" -ForegroundColor Yellow
$registerResponse = curl.exe -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"alice\",\"email\":\"alice@example.com\",\"password\":\"alice123\"}' `
  2>$null

Write-Host "註冊響應:" -ForegroundColor Green
Write-Host $registerResponse
Write-Host ""

# 測試 2: 用戶登入
Write-Host "測試 2: 用戶登入獲取 Token" -ForegroundColor Yellow
$loginResponse = curl.exe -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=alice&password=alice123" `
  2>$null

Write-Host "登入響應:" -ForegroundColor Green
Write-Host $loginResponse
Write-Host ""

# 提取 Token
$token = ($loginResponse | ConvertFrom-Json).access_token
Write-Host "提取的 Token: $token" -ForegroundColor Magenta
Write-Host ""

# 測試 3: 查看我的帳號狀態
Write-Host "測試 3: 查看我的帳號狀態" -ForegroundColor Yellow
$meResponse = curl.exe -X GET http://localhost:8000/api/v1/user/me `
  -H "Authorization: Bearer $token" `
  2>$null

Write-Host "我的帳號:" -ForegroundColor Green
Write-Host $meResponse
Write-Host ""

# 測試 4: 查看我的統計資訊
Write-Host "測試 4: 查看我的統計資訊" -ForegroundColor Yellow
$statsResponse = curl.exe -X GET http://localhost:8000/api/v1/user/stats `
  -H "Authorization: Bearer $token" `
  2>$null

Write-Host "統計資訊:" -ForegroundColor Green
Write-Host $statsResponse
Write-Host ""

# 測試 5: 查看我的交易記錄
Write-Host "測試 5: 查看我的交易記錄" -ForegroundColor Yellow
$tradesResponse = curl.exe -X GET http://localhost:8000/api/v1/user/trades `
  -H "Authorization: Bearer $token" `
  2>$null

Write-Host "交易記錄:" -ForegroundColor Green
Write-Host $tradesResponse
Write-Host ""

# 測試 6: 查看我正在跟隨的 Master
Write-Host "測試 6: 查看我正在跟隨的 Master" -ForegroundColor Yellow
$followingResponse = curl.exe -X GET http://localhost:8000/api/v1/user/following `
  -H "Authorization: Bearer $token" `
  2>$null

Write-Host "跟隨列表:" -ForegroundColor Green
Write-Host $followingResponse
Write-Host ""

# 測試 7: 查看我的跟隨者
Write-Host "測試 7: 查看我的跟隨者" -ForegroundColor Yellow
$followersResponse = curl.exe -X GET http://localhost:8000/api/v1/user/followers `
  -H "Authorization: Bearer $token" `
  2>$null

Write-Host "跟隨者列表:" -ForegroundColor Green
Write-Host $followersResponse
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "接下來可以訪問 Swagger UI 進行更多測試:" -ForegroundColor Yellow
Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "使用以下 Token 進行認證:" -ForegroundColor Yellow
Write-Host $token -ForegroundColor Green
