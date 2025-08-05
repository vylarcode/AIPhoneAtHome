# Phone AI Agent Docker Configuration
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    git \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create models directory
RUN mkdir -p models/whisper models/piper

# Download Whisper model
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', download_root='./models')"

# Expose ports
EXPOSE 8000 9090

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV WHISPER_DEVICE=cpu
ENV TTS_DEVICE=cpu

# Run the application
CMD ["python", "app/main.py"]
