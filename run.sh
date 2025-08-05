#!/bin/bash

# Phone AI Agent - Run Script

echo "=========================================="
echo "Starting Phone AI Agent"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate || source venv/Scripts/activate 2>/dev/null
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found. Run setup.sh first${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Run setup.sh first${NC}"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Ollama not running. Starting Ollama...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    echo -e "${GREEN}✅ Ollama started (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}✅ Ollama is running${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null
    fi
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup INT TERM

# Start ngrok in background
echo -e "${YELLOW}Starting ngrok...${NC}"
ngrok http 8000 > /dev/null 2>&1 &
NGROK_PID=$!
sleep 2

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -1)

if [ ! -z "$NGROK_URL" ]; then
    echo -e "${GREEN}✅ ngrok started${NC}"
    echo -e "${GREEN}Public URL: $NGROK_URL${NC}"
    echo ""
    echo "Configure your Twilio webhook to: $NGROK_URL/twiml"
else
    echo -e "${YELLOW}⚠️ Could not get ngrok URL. Check http://localhost:4040${NC}"
fi

echo ""
echo "=========================================="
echo "Starting FastAPI server..."
echo "=========================================="
echo ""

# Start the application
python app/main.py

# Cleanup on normal exit
cleanup
