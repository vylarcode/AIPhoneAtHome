#!/bin/bash

# Phone AI Agent - Automated Setup Script

echo "=========================================="
echo "Phone AI Agent - Automated Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "success" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "error" ]; then
        echo -e "${RED}❌ $2${NC}"
    elif [ "$1" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    else
        echo "$2"
    fi
}

# Check Python version
print_status "" "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_status "success" "Python $python_version OK"
else
    print_status "error" "Python 3.10+ required. Found: $python_version"
    exit 1
fi

# Create virtual environment
print_status "" "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "success" "Virtual environment created"
else
    print_status "warning" "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null

# Upgrade pip
print_status "" "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
print_status "" "Installing Python dependencies..."
if pip install -r requirements.txt; then
    print_status "success" "Dependencies installed"
else
    print_status "error" "Failed to install dependencies"
    exit 1
fi

# Check for CUDA
print_status "" "Checking for CUDA support..."
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    print_status "success" "CUDA available"
else
    print_status "warning" "CUDA not available - will use CPU (slower)"
fi

# Check Ollama
print_status "" "Checking Ollama..."
if command -v ollama &> /dev/null; then
    print_status "success" "Ollama found"
    
    # Pull default model
    print_status "" "Pulling llama3.2 model..."
    if ollama pull llama3.2; then
        print_status "success" "Model downloaded"
    else
        print_status "warning" "Failed to pull model - run manually: ollama pull llama3.2"
    fi
else
    print_status "error" "Ollama not found. Install from: https://ollama.ai"
fi

# Create necessary directories
print_status "" "Creating directories..."
mkdir -p models/whisper models/piper logs
print_status "success" "Directories created"

# Setup environment file
print_status "" "Setting up environment..."
if [ ! -f ".env" ]; then
    cp config/.env.example .env
    print_status "success" "Created .env file from template"
    print_status "warning" "Please edit .env with your Twilio credentials"
else
    print_status "success" ".env file already exists"
fi

# Install models
print_status "" "Installing models..."
python scripts/install_models.py

# Check ngrok
print_status "" "Checking ngrok..."
if command -v ngrok &> /dev/null; then
    print_status "success" "ngrok found"
else
    print_status "warning" "ngrok not found. Install from: https://ngrok.com/download"
fi

# Run health check
print_status "" "Running health check..."
python scripts/health_check.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Twilio credentials"
echo "2. Start Ollama: ollama serve"
echo "3. Run the application: python app/main.py"
echo "4. Start ngrok: ngrok http 8000"
echo "5. Update PUBLIC_URL in .env with ngrok URL"
echo "6. Configure Twilio webhook to point to: https://your-ngrok-url/twiml"
echo ""
print_status "success" "Ready to run!"
