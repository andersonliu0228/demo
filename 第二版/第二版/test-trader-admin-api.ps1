# Test Trader Admin API
Write-Host "=== Test Trader Admin API ===" -ForegroundColor Cyan

# Step 1: Login
Write-Host "`n[1/3] Login..." -ForegroundColor Yellow
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
    Write-Host "Login Success! Token: $($token.Substring(0, 30))..." -ForegroundColor Green
} catch {
    Write-Host "Login Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Get Clients
Write-Host "`n[2/3] Get Clients..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $clients = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/trader/clients" `
        -Method Get `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "Success! Found $($clients.Count) clients" -ForegroundColor Green
    
    if ($clients.Count -gt 0) {
        Write-Host "`nClient List:" -ForegroundColor Cyan
        foreach ($client in $clients) {
            Write-Host "  - ID: $($client.id), Name: $($client.username), Ratio: $($client.copy_ratio)x, Status: $($client.status)"
        }
    } else {
        Write-Host "No clients found. This is normal for a new account." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Get Clients Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Step 3: Test Update (only if clients exist)
if ($clients.Count -gt 0) {
    Write-Host "`n[3/3] Test Update Client..." -ForegroundColor Yellow
    $testClient = $clients[0]
    
    try {
        $updateResponse = Invoke-RestMethod `
            -Uri "http://localhost:8000/api/v1/trader/update-client" `
            -Method Patch `
            -Headers @{
                "Authorization" = "Bearer $token"
                "Content-Type" = "application/json"
            } `
            -Body (@{
                relation_id = $testClient.relation_id
                copy_ratio = 1.5
            } | ConvertTo-Json) `
            -ErrorAction Stop
        
        Write-Host "Update Success!" -ForegroundColor Green
        Write-Host "  - Relation ID: $($updateResponse.relation_id)"
        Write-Host "  - New Ratio: $($updateResponse.copy_ratio)x"
        Write-Host "  - Status: $($updateResponse.status)"
    } catch {
        Write-Host "Update Failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails) {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "`n[3/3] Skipping update test (no clients)" -ForegroundColor Yellow
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "You can now test the frontend at: http://localhost:3000/admin" -ForegroundColor Green
