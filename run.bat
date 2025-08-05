@echo off
REM Phone AI Agent - Windows Run Script

echo ==========================================
echo Starting Phone AI Agent
echo ==========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo ERROR: Virtual environment not found. Run setup.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found. Run setup.bat first
    pause
    exit /b 1
)

REM Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not running. Please start it in a separate window:
    echo ollama serve
    echo.
    echo Press any key after starting Ollama...
    pause >nul
) else (
    echo Ollama is running
)

REM Start ngrok in new window
echo.
echo Starting ngrok in new window...
start "ngrok" cmd /c "ngrok http 8000"

echo Waiting for ngrok to start...
timeout /t 3 /nobreak >nul

REM Try to get ngrok URL
echo.
echo ngrok started. Check the ngrok window for your public URL
echo Or visit: http://localhost:4040
echo.
echo Configure your Twilio webhook to: https://your-ngrok-url/twiml
echo.

echo ==========================================
echo Starting FastAPI server...
echo ==========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app\main.py

echo.
echo Server stopped.
pause
