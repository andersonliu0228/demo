# Mock Exchange 測試腳本
# 用於快速測試 Mock Exchange 功能

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mock Exchange 測試腳本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 步驟 1: 綁定 Mock Exchange 憑證
Write-Host "步驟 1: 綁定 Mock Exchange 憑證..." -ForegroundColor Yellow
$createResponse = curl -X POST http://localhost:8000/api/v1/credentials `
  -H "Content-Type: application/json" `
  -d '{
    "exchange_name": "mock",
    "api_key": "mock_api_key_12345",
    "api_secret": "mock_api_secret_67890",
    "verify": true
  }' | ConvertFrom-Json

if ($createResponse.id) {
    Write-Host "✓ 憑證創建成功！ID: $($createResponse.id)" -ForegroundColor Green
    $credentialId = $createResponse.id
} else {
    Write-Host "✗ 憑證創建失敗" -ForegroundColor Red
    Write-Host $createResponse
    exit 1
}

Write-Host ""
Start-Sleep -Seconds 1

# 步驟 2: 測試 Mock 餘額查詢
Write-Host "步驟 2: 測試 Mock 餘額查詢..." -ForegroundColor Yellow
$balanceResponse = curl "http://localhost:8000/api/v1/test/mock-balance?credential_id=$credentialId&user_id=1" | ConvertFrom-Json

if ($balanceResponse.success) {
    Write-Host "✓ 餘額查詢成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "加密流程驗證:" -ForegroundColor Cyan
    Write-Host "  - $($balanceResponse.encryption_flow.step_1)" -ForegroundColor White
    Write-Host "  - $($balanceResponse.encryption_flow.step_2)" -ForegroundColor White
    Write-Host "  - $($balanceResponse.encryption_flow.step_3)" -ForegroundColor White
    Write-Host "  - $($balanceResponse.encryption_flow.step_4)" -ForegroundColor White
    Write-Host ""
    Write-Host "餘額資訊:" -ForegroundColor Cyan
    Write-Host "  - USDT: $($balanceResponse.balance.total.USDT)" -ForegroundColor White
    Write-Host "  - BTC: $($balanceResponse.balance.total.BTC)" -ForegroundColor White
    Write-Host "  - ETH: $($balanceResponse.balance.total.ETH)" -ForegroundColor White
    Write-Host "  - BNB: $($balanceResponse.balance.total.BNB)" -ForegroundColor White
} else {
    Write-Host "✗ 餘額查詢失敗" -ForegroundColor Red
    Write-Host $balanceResponse
}

Write-Host ""
Start-Sleep -Seconds 1

# 步驟 3: 測試 Mock 下單
Write-Host "步驟 3: 測試 Mock 下單..." -ForegroundColor Yellow
$orderResponse = curl -X POST "http://localhost:8000/api/v1/test/mock-order?credential_id=$credentialId&user_id=1&symbol=BTC/USDT&order_type=limit&side=buy&amount=0.01&price=50000" | ConvertFrom-Json

if ($orderResponse.success) {
    Write-Host "✓ 訂單創建成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "訂單資訊:" -ForegroundColor Cyan
    Write-Host "  - 訂單 ID: $($orderResponse.order.id)" -ForegroundColor White
    Write-Host "  - 交易對: $($orderResponse.order.symbol)" -ForegroundColor White
    Write-Host "  - 類型: $($orderResponse.order.type)" -ForegroundColor White
    Write-Host "  - 方向: $($orderResponse.order.side)" -ForegroundColor White
    Write-Host "  - 價格: $($orderResponse.order.price)" -ForegroundColor White
    Write-Host "  - 數量: $($orderResponse.order.amount)" -ForegroundColor White
    Write-Host "  - 成本: $($orderResponse.order.cost)" -ForegroundColor White
    Write-Host "  - 狀態: $($orderResponse.order.status)" -ForegroundColor White
    Write-Host "  - 手續費: $($orderResponse.order.fee.cost) $($orderResponse.order.fee.currency)" -ForegroundColor White
} else {
    Write-Host "✗ 訂單創建失敗" -ForegroundColor Red
    Write-Host $orderResponse
}

Write-Host ""
Start-Sleep -Seconds 1

# 步驟 4: 測試加密流程
Write-Host "步驟 4: 測試加密解密流程..." -ForegroundColor Yellow
$encryptionResponse = curl "http://localhost:8000/api/v1/test/encryption-flow?test_secret=my_secret_123" | ConvertFrom-Json

if ($encryptionResponse.success) {
    Write-Host "✓ 加密流程測試成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "加密驗證:" -ForegroundColor Cyan
    Write-Host "  - 原文: $($encryptionResponse.original_text)" -ForegroundColor White
    Write-Host "  - 原文長度: $($encryptionResponse.original_length)" -ForegroundColor White
    Write-Host "  - 密文長度: $($encryptionResponse.encrypted_length)" -ForegroundColor White
    Write-Host "  - 解密後: $($encryptionResponse.decrypted_text)" -ForegroundColor White
    Write-Host "  - 往返成功: $($encryptionResponse.verification.roundtrip_successful)" -ForegroundColor White
} else {
    Write-Host "✗ 加密流程測試失敗" -ForegroundColor Red
    Write-Host $encryptionResponse
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "測試完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示：" -ForegroundColor Yellow
Write-Host "  - 查看完整 API 文檔: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - 查看使用指南: MOCK_EXCHANGE_使用指南.md" -ForegroundColor White
Write-Host ""
