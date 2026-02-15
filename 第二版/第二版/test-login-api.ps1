# Test Login API with form-data
Write-Host "=== Test Login API ===" -ForegroundColor Cyan

$username = "testuser"
$password = "testpass123"

Write-Host "`nSending login request..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:8000/api/v1/auth/login"
Write-Host "Username: $username"

try {
    $response = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -Body @{
            username = $username
            password = $password
        } `
        -ErrorAction Stop
    
    Write-Host "`nLogin Success!" -ForegroundColor Green
    Write-Host "Token: $($response.access_token.Substring(0, 50))..."
    Write-Host "Token Type: $($response.token_type)"
    
    Write-Host "`nNow test frontend at: http://localhost:3000/login" -ForegroundColor Cyan
    Write-Host "Use credentials: testuser / testpass123"
} catch {
    Write-Host "`nLogin Failed" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
