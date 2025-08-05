# PowerShell Quick Reference for Phone AI Agent

## 🚀 Quick Start

```powershell
# Complete setup and run
.\setup.ps1       # One-time setup
.\run.ps1         # Run the application
```

## 📋 Prerequisites Check

```powershell
# Check Python version
python --version

# Check if Ollama is installed
Get-Command ollama -ErrorAction SilentlyContinue

# Check if ngrok is installed
Get-Command ngrok -ErrorAction SilentlyContinue

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

## 🔧 Installation Commands

### Install Required Software

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install via Chocolatey
choco install python311 -y
choco install ngrok -y
choco install ollama -y

# Or install via winget
winget install Python.Python.3.11
winget install ngrok
winget install Ollama.Ollama
```

## 🛠️ Common PowerShell Commands

### Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Deactivate virtual environment
deactivate
```

### Environment Configuration

```powershell
# Copy environment template
Copy-Item config\.env.example .env

# Edit environment file
notepad .env
# or
code .env  # VS Code

# View environment variables
Get-Content .env

# Update a specific value programmatically
$content = Get-Content .env
$content = $content -replace 'TWILIO_ACCOUNT_SID=.*', 'TWILIO_ACCOUNT_SID=your_actual_sid'
Set-Content .env -Value $content
```

## 🏃 Running Services

### Ollama

```powershell
# Start Ollama service
ollama serve

# Start in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve"

# Check if Ollama is running
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"

# List available models
ollama list

# Pull a model
ollama pull llama3.2
```

### ngrok

```powershell
# Start ngrok tunnel
ngrok http 8000

# Start in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8000"

# Get ngrok URL programmatically
$tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"
$publicUrl = $tunnels.tunnels[0].public_url
Write-Host "Public URL: $publicUrl"
```

## 📊 Monitoring & Testing

### Health Checks

```powershell
# Check API health
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json

# Check specific endpoint
(Invoke-WebRequest -Uri "http://localhost:8000/").Content

# Test WebSocket connection
Test-NetConnection -ComputerName localhost -Port 8000
```

### Logs

```powershell
# View logs in real-time
Get-Content phone_agent.log -Tail 50 -Wait

# Search logs for errors
Select-String -Path phone_agent.log -Pattern "ERROR"

# View logs in grid view
Get-Content phone_agent.log | Out-GridView

# Clear old logs
Clear-Content phone_agent.log
```

### Process Management

```powershell
# Find Python processes
Get-Process python* | Format-Table Id, ProcessName, CPU, WS

# Find process using port
netstat -ano | findstr :8000

# Kill process by name
Stop-Process -Name python -Force

# Kill process by ID
Stop-Process -Id 1234 -Force
```

## 🧪 Testing

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests\

# Run specific test file
pytest tests\test_audio.py -v

# Run with coverage
pytest --cov=app tests\

# Run health check
python scripts\health_check.py

# Test audio system
python scripts\test_audio.py
```

## 🐛 Troubleshooting

### Common Issues and Fixes

```powershell
# Fix execution policy issues
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Fix pip SSL issues
pip config set global.trusted-host "pypi.org files.pythonhosted.org"

# Reinstall requirements
pip install --force-reinstall -r requirements.txt

# Clear Python cache
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force .pytest_cache

# Check Python path
$env:Path -split ';' | Where-Object {$_ -like '*Python*'}

# Add Python to PATH
$env:Path += ";C:\Python311;C:\Python311\Scripts"
```

### Network Diagnostics

```powershell
# Test Twilio connection
Test-NetConnection -ComputerName api.twilio.com -Port 443

# Check firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Python*"}

# Allow Python through firewall
New-NetFirewallRule -DisplayName "Python" -Direction Inbound -Program "C:\Python311\python.exe" -Action Allow
```

## 💡 PowerShell Tips

### Useful Aliases

```powershell
# Create useful aliases
Set-Alias -Name activate -Value .\venv\Scripts\Activate.ps1
Set-Alias -Name runapp -Value "python app\main.py"

# Save aliases to profile
Add-Content $PROFILE "`nSet-Alias -Name activate -Value .\venv\Scripts\Activate.ps1"
```

### Environment Variables

```powershell
# Set environment variable for session
$env:LOG_LEVEL = "DEBUG"

# Set permanent environment variable
[System.Environment]::SetEnvironmentVariable("LOG_LEVEL", "DEBUG", "User")

# View all environment variables
Get-ChildItem Env:
```

### Automation Script

```powershell
# Create a simple automation function
function Start-PhoneAgent {
    Write-Host "Starting Phone AI Agent..." -ForegroundColor Cyan
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Start Ollama in background
    Start-Job -ScriptBlock { ollama serve }
    
    # Start ngrok in background
    Start-Job -ScriptBlock { ngrok http 8000 }
    
    # Wait a moment for services to start
    Start-Sleep -Seconds 3
    
    # Run the application
    python app\main.py
}

# Use the function
Start-PhoneAgent
```

## 📚 Additional Resources

- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Python on Windows](https://docs.python.org/3/using/windows.html)
- [Twilio Docs](https://www.twilio.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [ngrok Documentation](https://ngrok.com/docs)

## 🔑 Quick Commands Reference

| Task | Command |
|------|---------|
| Setup | `.\setup.ps1` |
| Run | `.\run.ps1` |
| Activate venv | `.\venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r requirements.txt` |
| Start Ollama | `ollama serve` |
| Start ngrok | `ngrok http 8000` |
| Run app | `python app\main.py` |
| View logs | `Get-Content phone_agent.log -Tail 50 -Wait` |
| Run tests | `pytest tests\` |
| Check health | `Invoke-RestMethod http://localhost:8000/health` |

---

**Note:** This guide assumes PowerShell 5.1 or later (included with Windows 10/11).
For PowerShell Core 7+, most commands remain the same with enhanced cross-platform support.
