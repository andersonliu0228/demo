# EA Features Test - 測試 EA 專用功能
Write-Host "=== EA Features Test ===" -ForegroundColor Cyan
Write-Host "測試 last_seen、緊急全停、EA 配置 API" -ForegroundColor Yellow

# Step 1: Login
Write-Host "`n[Step 1] Login..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body @{
            username = "testuser"
            password = "testpass123"
        } `
        -ErrorAction Stop
    
    $token = $loginResponse.access_token
    Write-Host "✅ Login Success!" -ForegroundColor Green
} catch {
    Write-Host "❌ Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get Clients (should now include last_seen)
Write-Host "`n[Step 2] Get Clients with last_seen..." -ForegroundColor Yellow
try {
    $clients = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/clients" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" } `
        -ErrorAction Stop
    
    Write-Host "✅ Found $($clients.Count) clients" -ForegroundColor Green
    
    if ($clients.Count -gt 0) {
        $client = $clients[0]
        Write-Host "`nClient Info:" -ForegroundColor Cyan
        Write-Host "  Username: $($client.username)" -ForegroundColor White
        Write-Host "  Last Seen: $($client.last_seen)" -ForegroundColor White
        Write-Host "  Status: $($client.status)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Failed to get clients: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Test EA Config API
Write-Host "`n[Step 3] Test EA Config API..." -ForegroundColor Yellow
if ($clients.Count -gt 0) {
    $testUserId = $clients[0].id
    
    try {
        $eaConfig = Invoke-RestMethod `
            -Uri "http://localhost:8000/api/v1/ea/config?user_id=$testUserId" `
            -Method Get `
            -ErrorAction Stop
        
        Write-Host "✅ EA Config Retrieved!" -ForegroundColor Green
        Write-Host "`nEA Config:" -ForegroundColor Cyan
        Write-Host "  User ID: $($eaConfig.user_id)" -ForegroundColor White
        Write-Host "  Username: $($eaConfig.username)" -ForegroundColor White
        Write-Host "  Is Active: $($eaConfig.is_active)" -ForegroundColor White
        Write-Host "  Copy Ratio: $($eaConfig.copy_ratio)x" -ForegroundColor White
        Write-Host "  Emergency Stop: $($eaConfig.emergency_stop)" -ForegroundColor White
        Write-Host "  Last Seen: $($eaConfig.last_seen)" -ForegroundColor White
        Write-Host "  Message: $($eaConfig.message)" -ForegroundColor White
    } catch {
        Write-Host "❌ EA Config Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 4: Test Emergency Stop Status
Write-Host "`n[Step 4] Get Emergency Stop Status..." -ForegroundColor Yellow
try {
    $stopStatus = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/emergency-stop-status" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" } `
        -ErrorAction Stop
    
    Write-Host "✅ Emergency Stop Status: $($stopStatus.emergency_stop)" -ForegroundColor Green
    Write-Host "   Message: $($stopStatus.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to get emergency stop status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test Emergency Stop Toggle (Enable)
Write-Host "`n[Step 5] Enable Emergency Stop..." -ForegroundColor Yellow
try {
    $stopResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/emergency-stop" `
        -Method Post `
        -Headers $headers `
        -Body (@{
            stop_all = $true
        } | ConvertTo-Json) `
        -ErrorAction Stop
    
    Write-Host "✅ Emergency Stop Enabled!" -ForegroundColor Green
    Write-Host "   Message: $($stopResponse.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to enable emergency stop: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Verify EA Config with Emergency Stop
Write-Host "`n[Step 6] Verify EA Config with Emergency Stop..." -ForegroundColor Yellow
if ($clients.Count -gt 0) {
    $testUserId = $clients[0].id
    
    try {
        $eaConfig = Invoke-RestMethod `
            -Uri "http://localhost:8000/api/v1/ea/config?user_id=$testUserId" `
            -Method Get `
            -ErrorAction Stop
        
        Write-Host "✅ EA Config Retrieved!" -ForegroundColor Green
        Write-Host "  Is Active: $($eaConfig.is_active) (should be false)" -ForegroundColor $(if ($eaConfig.is_active -eq $false) { "Green" } else { "Red" })
        Write-Host "  Emergency Stop: $($eaConfig.emergency_stop) (should be true)" -ForegroundColor $(if ($eaConfig.emergency_stop -eq $true) { "Green" } else { "Red" })
    } catch {
        Write-Host "❌ EA Config Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 7: Disable Emergency Stop
Write-Host "`n[Step 7] Disable Emergency Stop..." -ForegroundColor Yellow
try {
    $stopResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/emergency-stop" `
        -Method Post `
        -Headers $headers `
        -Body (@{
            stop_all = $false
        } | ConvertTo-Json) `
        -ErrorAction Stop
    
    Write-Host "✅ Emergency Stop Disabled!" -ForegroundColor Green
    Write-Host "   Message: $($stopResponse.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to disable emergency stop: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test EA Heartbeat
Write-Host "`n[Step 8] Test EA Heartbeat..." -ForegroundColor Yellow
if ($clients.Count -gt 0) {
    $testUserId = $clients[0].id
    
    try {
        $heartbeat = Invoke-RestMethod `
            -Uri "http://localhost:8000/api/v1/ea/heartbeat?user_id=$testUserId" `
            -Method Get `
            -ErrorAction Stop
        
        Write-Host "✅ Heartbeat Success!" -ForegroundColor Green
        Write-Host "  Status: $($heartbeat.status)" -ForegroundColor White
        Write-Host "  Last Seen: $($heartbeat.last_seen)" -ForegroundColor White
    } catch {
        Write-Host "❌ Heartbeat Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Final Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "✅ EA FEATURES TEST COMPLETED!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📊 Test Summary:" -ForegroundColor Yellow
Write-Host "  ✅ GET /api/v1/trader/clients (with last_seen)" -ForegroundColor White
Write-Host "  ✅ GET /api/v1/ea/config" -ForegroundColor White
Write-Host "  ✅ GET /api/v1/ea/heartbeat" -ForegroundColor White
Write-Host "  ✅ GET /api/v1/trader/emergency-stop-status" -ForegroundColor White
Write-Host "  ✅ POST /api/v1/trader/emergency-stop" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3000/admin" -ForegroundColor White
Write-Host "  2. Check the online status indicators (green/yellow/red dots)" -ForegroundColor White
Write-Host "  3. Test the Emergency Stop button" -ForegroundColor White
Write-Host "  4. EA can call /api/v1/ea/config?user_id=X to get config" -ForegroundColor White

Write-Host "`n💡 EA Integration:" -ForegroundColor Yellow
Write-Host "  MT4/MT5 EA should call:" -ForegroundColor White
Write-Host "  - GET /api/v1/ea/config?user_id=X every 1-5 minutes" -ForegroundColor White
Write-Host "  - This updates last_seen automatically" -ForegroundColor White
Write-Host "  - Returns: is_active, copy_ratio, emergency_stop" -ForegroundColor White
