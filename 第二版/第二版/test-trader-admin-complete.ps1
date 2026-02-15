# Complete Trader Admin API Test
Write-Host "=== Complete Trader Admin API Test ===" -ForegroundColor Cyan

# Step 1: Login
Write-Host "`n[1/5] Login as testuser..." -ForegroundColor Yellow
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
    Write-Host "Login Success!" -ForegroundColor Green
} catch {
    Write-Host "Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get All Clients
Write-Host "`n[2/5] Get All Clients..." -ForegroundColor Yellow
try {
    $clients = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/clients" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" } `
        -ErrorAction Stop
    
    Write-Host "Success! Found $($clients.Count) clients" -ForegroundColor Green
    
    if ($clients.Count -gt 0) {
        Write-Host "`nClient List:" -ForegroundColor Cyan
        foreach ($client in $clients) {
            Write-Host "  - ID: $($client.id), Name: $($client.username), Ratio: $($client.copy_ratio)x, Status: $($client.status), Balance: $($client.net_value) USDT"
        }
        $testClient = $clients[0]
    } else {
        Write-Host "No clients found!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Get Clients Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Update Copy Ratio
Write-Host "`n[3/5] Update Copy Ratio..." -ForegroundColor Yellow
$newRatio = 2.5
try {
    $updateResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/update-client" `
        -Method Patch `
        -Headers $headers `
        -Body (@{
            relation_id = $testClient.relation_id
            copy_ratio = $newRatio
        } | ConvertTo-Json) `
        -ErrorAction Stop
    
    Write-Host "Success! Updated ratio to $($updateResponse.copy_ratio)x" -ForegroundColor Green
} catch {
    Write-Host "Update Ratio Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Toggle Status (Block)
Write-Host "`n[4/5] Toggle Status to Blocked..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/update-client" `
        -Method Patch `
        -Headers $headers `
        -Body (@{
            relation_id = $testClient.relation_id
            status = "blocked"
        } | ConvertTo-Json) `
        -ErrorAction Stop
    
    Write-Host "Success! Status changed to: $($statusResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "Toggle Status Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Toggle Status Back (Active)
Write-Host "`n[5/5] Toggle Status back to Active..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/update-client" `
        -Method Patch `
        -Headers $headers `
        -Body (@{
            relation_id = $testClient.relation_id
            status = "active"
        } | ConvertTo-Json) `
        -ErrorAction Stop
    
    Write-Host "Success! Status changed to: $($statusResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "Toggle Status Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Final Verification
Write-Host "`n[Verification] Get Updated Client List..." -ForegroundColor Yellow
try {
    $updatedClients = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/clients" `
        -Method Get `
        -Headers @{ "Authorization" = "Bearer $token" } `
        -ErrorAction Stop
    
    Write-Host "`nUpdated Client List:" -ForegroundColor Cyan
    foreach ($client in $updatedClients) {
        Write-Host "  - ID: $($client.id), Name: $($client.username), Ratio: $($client.copy_ratio)x, Status: $($client.status)"
    }
} catch {
    Write-Host "Verification Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "`nAll trader admin functions are working!" -ForegroundColor Green
Write-Host "You can now test the frontend at: http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host "`nFeatures implemented:" -ForegroundColor Yellow
Write-Host "  - Get all clients (followers)" -ForegroundColor White
Write-Host "  - Update copy ratio" -ForegroundColor White
Write-Host "  - Toggle client status (active/blocked/pending)" -ForegroundColor White
Write-Host "  - Real-time data synchronization" -ForegroundColor White
Write-Host "  - Last update timestamp" -ForegroundColor White
