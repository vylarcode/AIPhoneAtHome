# Phone AI Agent - PowerShell Run Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Phone AI Agent" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Run .\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor White
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Run .\setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Check if Ollama is running
Write-Host "`nChecking Ollama service..." -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction Stop
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not running" -ForegroundColor Yellow
    Write-Host "Starting Ollama in new window..." -ForegroundColor White
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve" -WindowStyle Normal
    Write-Host "Waiting for Ollama to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# Start ngrok in new window
Write-Host "`nStarting ngrok tunnel..." -ForegroundColor White
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if ($ngrokPath) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8000" -WindowStyle Normal
    Write-Host "✅ ngrok started in new window" -ForegroundColor Green
    Start-Sleep -Seconds 3
    
    # Try to get ngrok URL
    try {
        $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get -ErrorAction Stop
        $publicUrl = $tunnels.tunnels[0].public_url
        if ($publicUrl) {
            Write-Host "`n🌐 Public URL: $publicUrl" -ForegroundColor Green
            Write-Host "📞 Configure Twilio webhook to: $publicUrl/twiml" -ForegroundColor Cyan
            
            # Optionally update .env file
            Write-Host "`nDo you want to update PUBLIC_URL in .env? (Y/N): " -ForegroundColor Yellow -NoNewline
            $response = Read-Host
            if ($response -eq 'Y' -or $response -eq 'y') {
                $domain = $publicUrl -replace 'https?://', ''
                $envContent = Get-Content ".env" -Raw
                $envContent = $envContent -replace 'PUBLIC_URL=.*', "PUBLIC_URL=$domain"
                Set-Content ".env" -Value $envContent
                Write-Host "✅ Updated PUBLIC_URL in .env" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "⚠️  Could not get ngrok URL automatically" -ForegroundColor Yellow
        Write-Host "Check ngrok interface at: http://localhost:4040" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ ngrok not found. Please install from: https://ngrok.com" -ForegroundColor Red
    Write-Host "Or install via Chocolatey: choco install ngrok" -ForegroundColor Gray
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Server..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 API: http://localhost:8000" -ForegroundColor White
Write-Host "📊 Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "📈 Metrics: http://localhost:9090/metrics" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the application
python app\main.py

# Cleanup on exit
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Server stopped" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
