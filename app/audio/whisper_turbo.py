"""
Optimized Whisper implementation for ultra-low latency STT
"""
import asyncio
import numpy as np
from typing import Optional, Union
import logging
import time
from faster_whisper import WhisperModel
import torch

from app.config import settings

logger = logging.getLogger(__name__)

class WhisperTurbo:
    """Optimized Whisper for fast speech-to-text"""
    
    def __init__(self):
        self.model: Optional[WhisperModel] = None
        self.device = settings.whisper_device
        self.compute_type = settings.whisper_compute_type
        self.model_size = self._get_model_size()
        
    def _get_model_size(self) -> str:
        """Get appropriate model size based on configuration"""
        model_map = {
            "turbo": "turbo",
            "tiny": "tiny",
            "base": "base",
            "small": "small"
        }
        return model_map.get(settings.whisper_model, "tiny")
    
    async def initialize(self):
        """Initialize the Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            
            # Check for CUDA availability
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"
                self.compute_type = "int8"
            
            # Load model with optimizations
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=settings.num_worker_threads,
                download_root="./models"
            )
            
            # Warm up the model
            await self._warmup()
            
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            raise
            
    async def _warmup(self):
        """Warm up the model for faster first inference"""
        # Create dummy audio (1 second of silence)
        dummy_audio = np.zeros(16000, dtype=np.float32)
        
        # Run inference to warm up
        await self.transcribe(dummy_audio)
        logger.info("Whisper model warmed up")
    
    async def transcribe(self, audio: Union[np.ndarray, bytes]) -> str:
        """Transcribe audio to text with minimal latency"""
        if self.model is None:
            await self.initialize()
            
        try:
            start_time = time.time()
            
            # Convert to numpy array if needed
            if isinstance(audio, bytes):
                audio = np.frombuffer(audio, dtype=np.int16)
                
            # Normalize audio to float32 [-1, 1]
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Run transcription with optimized settings
            segments, info = self.model.transcribe(
                audio_float,
                language="en",
                task="transcribe",
                beam_size=1,  # Faster with greedy decoding
                best_of=1,
                patience=1.0,
                length_penalty=1.0,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                condition_on_previous_text=False,  # Faster without context
                vad_filter=True,  # Use VAD to skip silence
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    max_speech_duration_s=30,
                    min_silence_duration_ms=100,
                    window_size_samples=1024,
                    speech_pad_ms=100
                )
            )
            
            # Collect transcription
            transcript = ""
            for segment in segments:
                transcript += segment.text
                
            # Log timing
            latency = (time.time() - start_time) * 1000
            logger.debug(f"Whisper latency: {latency:.0f}ms for {len(audio)/16000:.2f}s audio")
            
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
            
    def is_ready(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model is not None
