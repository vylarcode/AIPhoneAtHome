# Phone AI Agent - PowerShell Setup Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Phone AI Agent - PowerShell Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator (optional but recommended)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Not running as Administrator. Some features may require admin rights." -ForegroundColor Yellow
}

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor White
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-Host "✅ $pythonVersion OK" -ForegroundColor Green
        } else {
            Write-Host "❌ Python 3.10+ required. Found: $pythonVersion" -ForegroundColor Red
            Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor White
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor White
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor White
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor White
Write-Host "This may take a few minutes..." -ForegroundColor Gray
$installResult = pip install -r requirements.txt 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host $installResult -ForegroundColor Red
    exit 1
}

# Check for CUDA
Write-Host "`nChecking for CUDA support..." -ForegroundColor White
$cudaCheck = python -c "import torch; print(torch.cuda.is_available())" 2>&1
if ($cudaCheck -eq "True") {
    $gpuName = python -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1
    Write-Host "✅ CUDA available: $gpuName" -ForegroundColor Green
} else {
    Write-Host "⚠️  CUDA not available - will use CPU (slower)" -ForegroundColor Yellow
    Write-Host "For better performance, install CUDA toolkit and PyTorch with CUDA support" -ForegroundColor Gray
}

# Check Ollama
Write-Host "`nChecking Ollama..." -ForegroundColor White
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaPath) {
    Write-Host "✅ Ollama found at: $($ollamaPath.Path)" -ForegroundColor Green
    
    # Check if Ollama is running
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction SilentlyContinue
        Write-Host "✅ Ollama service is running" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Ollama installed but not running" -ForegroundColor Yellow
        Write-Host "Start it with: ollama serve" -ForegroundColor Gray
    }
    
    # Pull default model
    Write-Host "Pulling llama3.2 model (this may take a while)..." -ForegroundColor White
    $pullResult = ollama pull llama3.2 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model downloaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Failed to pull model. Run manually: ollama pull llama3.2" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Ollama not found" -ForegroundColor Red
    Write-Host "Please install from: https://ollama.ai" -ForegroundColor Yellow
    Write-Host "After installation, run: ollama pull llama3.2" -ForegroundColor Gray
}

# Create necessary directories
Write-Host "`nCreating directories..." -ForegroundColor White
$directories = @("models\whisper", "models\piper", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Setup environment file
Write-Host "`nSetting up environment..." -ForegroundColor White
if (-not (Test-Path ".env")) {
    Copy-Item "config\.env.example" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Edit .env with your Twilio credentials" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Install models
Write-Host "`nInstalling models..." -ForegroundColor White
python scripts\install_models.py

# Check ngrok
Write-Host "`nChecking ngrok..." -ForegroundColor White
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if ($ngrokPath) {
    Write-Host "✅ ngrok found at: $($ngrokPath.Path)" -ForegroundColor Green
} else {
    Write-Host "⚠️  ngrok not found" -ForegroundColor Yellow
    Write-Host "Please install from: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "Or install via Chocolatey: choco install ngrok" -ForegroundColor Gray
}

# Run health check
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Running Health Check..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
python scripts\health_check.py

# Summary
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Edit .env file with your Twilio credentials" -ForegroundColor White
Write-Host "   Use: notepad .env" -ForegroundColor Gray
Write-Host "2. Start Ollama service:" -ForegroundColor White
Write-Host "   In new PowerShell: ollama serve" -ForegroundColor Gray
Write-Host "3. Run the application:" -ForegroundColor White
Write-Host "   .\run.ps1" -ForegroundColor Gray
Write-Host "4. The script will start ngrok automatically" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
