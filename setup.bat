@echo off
REM Phone AI Agent - Windows Setup Script

echo ==========================================
echo Phone AI Agent - Windows Setup
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Create directories
echo Creating directories...
if not exist "models\whisper" mkdir models\whisper
if not exist "models\piper" mkdir models\piper
if not exist "logs" mkdir logs

REM Setup environment file
echo Setting up environment...
if not exist ".env" (
    copy config\.env.example .env >nul
    echo Created .env file from template
    echo.
    echo IMPORTANT: Please edit .env with your Twilio credentials
) else (
    echo .env file already exists
)

REM Install models
echo Installing models...
python scripts\install_models.py

REM Check Ollama
echo.
echo Checking for Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama not found
    echo Please install from: https://ollama.ai
    echo Then run: ollama pull llama3.2
) else (
    echo Ollama found
    echo Pulling default model...
    ollama pull llama3.2
)

REM Check ngrok
echo.
echo Checking for ngrok...
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: ngrok not found
    echo Please install from: https://ngrok.com/download
) else (
    echo ngrok found
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Twilio credentials
echo 2. Start Ollama: ollama serve
echo 3. Run the application: python app\main.py
echo 4. Start ngrok: ngrok http 8000
echo 5. Update PUBLIC_URL in .env with ngrok URL
echo.
echo Press any key to run health check...
pause >nul

REM Run health check
python scripts\health_check.py

echo.
echo Press any key to exit...
pause >nul
