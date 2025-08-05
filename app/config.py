"""
Configuration management for the Phone AI Agent
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Twilio Configuration
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., env="TWILIO_PHONE_NUMBER")
    twilio_api_key: Optional[str] = Field(None, env="TWILIO_API_KEY")
    twilio_api_secret: Optional[str] = Field(None, env="TWILIO_API_SECRET")
    
    # Server Configuration
    server_host: str = Field("0.0.0.0", env="SERVER_HOST")
    server_port: int = Field(8000, env="SERVER_PORT")
    websocket_path: str = Field("/media-stream", env="WEBSOCKET_PATH")
    public_url: Optional[str] = Field(None, env="PUBLIC_URL")
    
    # Ollama Configuration
    ollama_host: str = Field("http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field("llama3.2:latest", env="OLLAMA_MODEL")
    ollama_temperature: float = Field(0.7, env="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(150, env="OLLAMA_MAX_TOKENS")
    ollama_timeout: int = Field(30, env="OLLAMA_TIMEOUT")
    
    # Audio Configuration
    whisper_model: str = Field("turbo", env="WHISPER_MODEL")
    whisper_device: str = Field("cuda", env="WHISPER_DEVICE")
    whisper_compute_type: str = Field("int8", env="WHISPER_COMPUTE_TYPE")
    tts_model: str = Field("en_US-amy-medium", env="TTS_MODEL")
    tts_device: str = Field("cuda", env="TTS_DEVICE")
    audio_chunk_ms: int = Field(200, env="AUDIO_CHUNK_MS")
    audio_sample_rate: int = Field(8000, env="AUDIO_SAMPLE_RATE")
    
    # Performance Tuning
    max_concurrent_calls: int = Field(10, env="MAX_CONCURRENT_CALLS")
    enable_gpu: bool = Field(True, env="ENABLE_GPU")
    num_worker_threads: int = Field(4, env="NUM_WORKER_THREADS")
    response_timeout_ms: int = Field(5000, env="RESPONSE_TIMEOUT_MS")
    vad_aggressiveness: int = Field(3, env="VAD_AGGRESSIVENESS")
    
    # Features
    enable_echo_cancellation: bool = Field(True, env="ENABLE_ECHO_CANCELLATION")
    enable_noise_reduction: bool = Field(True, env="ENABLE_NOISE_REDUCTION")
    enable_interruption_handling: bool = Field(True, env="ENABLE_INTERRUPTION_HANDLING")
    enable_backchannel_detection: bool = Field(True, env="ENABLE_BACKCHANNEL_DETECTION")
    
    # Monitoring
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("phone_agent.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
settings = Settings()
