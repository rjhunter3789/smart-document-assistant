# PowerShell script to test the voice endpoint directly

$baseUrl = "https://web-production-4dcb7c.up.railway.app"

Write-Host "Testing Voice Endpoint Directly" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

# Test 1: Just "Impel"
Write-Host "`nTest 1: Just 'Impel'" -ForegroundColor Yellow
$response1 = Invoke-WebRequest -Uri "$baseUrl/voice?user=jeff&q=Impel" -UseBasicParsing
Write-Host "Response: $($response1.Content.Substring(0, [Math]::Min(200, $response1.Content.Length)))..."

# Test 2: "Tell me about Impel"
Write-Host "`nTest 2: 'Tell me about Impel'" -ForegroundColor Yellow
$response2 = Invoke-WebRequest -Uri "$baseUrl/voice?user=jeff&q=Tell%20me%20about%20Impel" -UseBasicParsing
Write-Host "Response: $($response2.Content.Substring(0, [Math]::Min(200, $response2.Content.Length)))..."

# Test 3: Check version endpoint
Write-Host "`nTest 3: Check API Status" -ForegroundColor Yellow
$response3 = Invoke-WebRequest -Uri "$baseUrl/api/status" -UseBasicParsing
Write-Host "Response: $($response3.Content)"

Write-Host "`nDone!" -ForegroundColor Green