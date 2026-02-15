# Follower Engine 測試腳本
# 此腳本演示完整的跟單流程

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Follower Engine 跟單引擎測試" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000"

# 步驟 1: 創建 Master 憑證
Write-Host "步驟 1: 創建 Master 憑證..." -ForegroundColor Yellow
$masterCredResponse = curl.exe -X POST "$baseUrl/api/v1/credentials" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"exchange_name\":\"mock\",\"api_key\":\"master_key_123\",\"api_secret\":\"master_secret_456\",\"label\":\"Master Mock\"}'
Write-Host $masterCredResponse -ForegroundColor Green
Write-Host ""

# 步驟 2: 創建 Follower 憑證
Write-Host "步驟 2: 創建 Follower 憑證..." -ForegroundColor Yellow
$followerCredResponse = curl.exe -X POST "$baseUrl/api/v1/credentials" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":2,\"exchange_name\":\"mock\",\"api_key\":\"follower_key_789\",\"api_secret\":\"follower_secret_012\",\"label\":\"Follower Mock\"}'
Write-Host $followerCredResponse -ForegroundColor Green
Write-Host ""

# 步驟 3: 創建跟隨關係
Write-Host "步驟 3: 創建跟隨關係 (follow_ratio=0.1)..." -ForegroundColor Yellow
$relationshipResponse = curl.exe -X POST "$baseUrl/api/v1/follower/relationships" `
  -H "Content-Type: application/json" `
  -d '{\"follower_user_id\":2,\"master_user_id\":1,\"follow_ratio\":0.1,\"follower_credential_id\":2,\"master_credential_id\":1}'
Write-Host $relationshipResponse -ForegroundColor Green
Write-Host ""

# 步驟 4: 啟動監控引擎
Write-Host "步驟 4: 啟動監控引擎..." -ForegroundColor Yellow
$startEngineResponse = curl.exe -X POST "$baseUrl/api/v1/follower/engine/start"
Write-Host $startEngineResponse -ForegroundColor Green
Write-Host ""

# 步驟 5: 模擬 Master 開多倉
Write-Host "步驟 5: 模擬 Master 開多倉 BTC/USDT (1.0 BTC @ 50000 USDT)..." -ForegroundColor Yellow
$masterPositionResponse = curl.exe -X POST "$baseUrl/api/v1/follower/master-position" `
  -H "Content-Type: application/json" `
  -d '{\"master_user_id\":1,\"master_credential_id\":1,\"symbol\":\"BTC/USDT\",\"position_size\":1.0,\"entry_price\":50000.0}'
Write-Host $masterPositionResponse -ForegroundColor Green
Write-Host ""

# 等待監控引擎處理
Write-Host "等待 12 秒讓監控引擎處理..." -ForegroundColor Yellow
Start-Sleep -Seconds 12

# 步驟 6: 查看交易歷史
Write-Host "步驟 6: 查看交易歷史..." -ForegroundColor Yellow
$tradeHistoryResponse = curl.exe "$baseUrl/api/v1/follower/trade-history"
Write-Host $tradeHistoryResponse -ForegroundColor Green
Write-Host ""

# 步驟 7: 查看 Master 倉位
Write-Host "步驟 7: 查看 Master 倉位..." -ForegroundColor Yellow
$masterPositionsResponse = curl.exe "$baseUrl/api/v1/follower/master-positions?master_user_id=1"
Write-Host $masterPositionsResponse -ForegroundColor Green
Write-Host ""

# 步驟 8: 查看跟隨關係
Write-Host "步驟 8: 查看跟隨關係..." -ForegroundColor Yellow
$relationshipsResponse = curl.exe "$baseUrl/api/v1/follower/relationships"
Write-Host $relationshipsResponse -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示：" -ForegroundColor Yellow
Write-Host "- 訪問 http://localhost:8000/docs 使用 Swagger UI" -ForegroundColor White
Write-Host "- 查看後端日誌：docker logs -f ea_trading_backend" -ForegroundColor White
Write-Host "- 停止引擎：curl.exe -X POST http://localhost:8000/api/v1/follower/engine/stop" -ForegroundColor White
