"""
Main FastAPI application for Phone AI Agent
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from typing import Dict, Any
import logging

from app.config import settings
from app.websocket_handler import TwilioWebSocketHandler
from app.utils.logger import setup_logging
from app.utils.metrics import MetricsCollector

# Setup logging
logger = setup_logging(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Phone AI Agent",
    description="Real-time voice conversation AI agent via Twilio",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize metrics collector
metrics = MetricsCollector()

# Store active WebSocket connections
active_connections: Dict[str, TwilioWebSocketHandler] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Phone AI Agent...")
    
    # Initialize models and services
    from app.audio.whisper_turbo import WhisperTurbo
    from app.llm.ollama_client import OllamaClient
    from app.audio.tts_engine import TTSEngine
    
    # Preload models for faster first response
    logger.info("Preloading models...")
    whisper = WhisperTurbo()
    await whisper.initialize()
    
    ollama = OllamaClient()
    await ollama.test_connection()
    
    tts = TTSEngine()
    await tts.initialize()
    
    logger.info("Phone AI Agent started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down Phone AI Agent...")
    
    # Close all active connections
    for call_sid, handler in active_connections.items():
        await handler.close()
    
    logger.info("Phone AI Agent shutdown complete")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Phone AI Agent",
        "version": "1.0.0",
        "active_calls": len(active_connections)
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    from app.audio.whisper_turbo import WhisperTurbo
    from app.llm.ollama_client import OllamaClient
    
    health_status = {
        "status": "healthy",
        "checks": {
            "whisper": False,
            "ollama": False,
            "tts": False
        }
    }
    
    try:
        # Check Whisper
        whisper = WhisperTurbo()
        if whisper.model:
            health_status["checks"]["whisper"] = True
            
        # Check Ollama
        ollama = OllamaClient()
        if await ollama.test_connection():
            health_status["checks"]["ollama"] = True
            
        # Check TTS
        from app.audio.tts_engine import TTSEngine
        tts = TTSEngine()
        if tts.is_ready:
            health_status["checks"]["tts"] = True
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "degraded"
    
    return health_status

@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    """Twilio Media Stream WebSocket endpoint"""
    await websocket.accept()
    
    call_sid = None
    handler = None
    
    try:
        # Create handler for this connection
        handler = TwilioWebSocketHandler(websocket, metrics)
        
        # Process the WebSocket connection
        call_sid = await handler.handle_connection()
        
        if call_sid:
            active_connections[call_sid] = handler
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if call_sid and call_sid in active_connections:
            del active_connections[call_sid]
        if handler:
            await handler.close()

@app.post("/twiml")
async def twiml_webhook(request: Request):
    """Generate TwiML for incoming calls"""
    from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
    
    response = VoiceResponse()
    response.say("Connecting you to the AI assistant...")
    
    connect = Connect()
    
    # Get the WebSocket URL
    if settings.public_url:
        ws_url = f"wss://{settings.public_url}/media-stream"
    else:
        ws_url = f"ws://{settings.server_host}:{settings.server_port}/media-stream"
    
    stream = Stream(url=ws_url)
    connect.append(stream)
    response.append(connect)
    
    return JSONResponse(
        content=str(response),
        media_type="application/xml"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
