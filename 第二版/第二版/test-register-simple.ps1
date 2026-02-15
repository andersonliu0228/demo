# Simple Register Function Test
Write-Host "=== Register Function Test ===" -ForegroundColor Cyan

$API_BASE = "http://localhost:8000"
$testUsername = "testuser_$(Get-Random -Minimum 1000 -Maximum 9999)"
$testEmail = "test_$(Get-Random -Minimum 1000 -Maximum 9999)@example.com"
$testPassword = "testpass123"

# Test 1: Register new user
Write-Host "`n[Test 1] Register new user..." -ForegroundColor Yellow
Write-Host "  Username: $testUsername" -ForegroundColor Gray
Write-Host "  Email: $testEmail" -ForegroundColor Gray

try {
    $registerResponse = Invoke-RestMethod `
        -Uri "$API_BASE/api/v1/auth/register" `
        -Method Post `
        -Body (@{
            username = $testUsername
            email = $testEmail
            password = $testPassword
        } | ConvertTo-Json) `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "Success! User registered" -ForegroundColor Green
    Write-Host "  User ID: $($registerResponse.id)" -ForegroundColor White
    Write-Host "  Username: $($registerResponse.username)" -ForegroundColor White
    Write-Host "  Email: $($registerResponse.email)" -ForegroundColor White
    Write-Host "  Is Active: $($registerResponse.is_active)" -ForegroundColor White
    Write-Host "  Role: $($registerResponse.role)" -ForegroundColor White
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Login with new account
Write-Host "`n[Test 2] Login with new account..." -ForegroundColor Yellow

try {
    $loginResponse = Invoke-RestMethod `
        -Uri "$API_BASE/api/v1/auth/login" `
        -Method Post `
        -Body @{
            username = $testUsername
            password = $testPassword
        } `
        -ErrorAction Stop
    
    $token = $loginResponse.access_token
    Write-Host "Success! Login successful" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0, 20))..." -ForegroundColor White
} catch {
    Write-Host "Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Duplicate username (should fail)
Write-Host "`n[Test 3] Test duplicate username (should fail)..." -ForegroundColor Yellow

try {
    $duplicateResponse = Invoke-RestMethod `
        -Uri "$API_BASE/api/v1/auth/register" `
        -Method Post `
        -Body (@{
            username = $testUsername
            email = "another_$testEmail"
            password = $testPassword
        } | ConvertTo-Json) `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "Error: Should reject duplicate username" -ForegroundColor Red
    exit 1
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "Success! Correctly rejected duplicate username" -ForegroundColor Green
    } else {
        Write-Host "Error: Wrong status code" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n=== ALL TESTS PASSED ===" -ForegroundColor Green
