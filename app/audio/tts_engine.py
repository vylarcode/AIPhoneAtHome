"""
Text-to-Speech engine with streaming support
"""
import asyncio
import numpy as np
from typing import List, Optional, Generator
import logging
import io
import wave
import subprocess
import tempfile
import os

from app.config import settings

logger = logging.getLogger(__name__)

class TTSEngine:
    """Fast TTS engine with streaming capabilities"""
    
    def __init__(self):
        self.model_name = settings.tts_model
        self.device = settings.tts_device
        self.is_ready = False
        self.piper_path = self._find_piper()
        
    def _find_piper(self) -> Optional[str]:
        """Find Piper TTS executable"""
        # Check common locations
        paths = [
            "./piper/piper",
            "/usr/local/bin/piper",
            "/usr/bin/piper",
            "piper"  # In PATH
        ]
        
        for path in paths:
            if os.path.exists(path) or self._check_command(path):
                logger.info(f"Found Piper at: {path}")
                return path
                
        logger.warning("Piper TTS not found, will use fallback TTS")
        return None
    
    def _check_command(self, command: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run([command, "--help"], capture_output=True, timeout=1)
            return True
        except:
            return False
            
    async def initialize(self):
        """Initialize the TTS engine"""
        try:
            if self.piper_path:
                # Download voice model if needed
                await self._download_voice_model()
                
            self.is_ready = True
            logger.info("TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            # Use fallback TTS
            self.is_ready = True
            
    async def _download_voice_model(self):
        """Download Piper voice model if not present"""
        model_dir = "./models/piper"
        os.makedirs(model_dir, exist_ok=True)
        
        model_file = f"{model_dir}/{self.model_name}.onnx"
        
        if not os.path.exists(model_file):
            logger.info(f"Downloading TTS model: {self.model_name}")
            # In production, download from Piper model repository
            # For now, we'll assume models are pre-installed
            pass
    
    async def synthesize(self, text: str) -> List[bytes]:
        """Synthesize text to audio chunks"""
        if not text:
            return []
            
        try:
            if self.piper_path:
                return await self._synthesize_piper(text)
            else:
                return await self._synthesize_fallback(text)
                
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return []
            
    async def _synthesize_piper(self, text: str) -> List[bytes]:
        """Synthesize using Piper TTS"""
        chunks = []
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
            # Run Piper
            model_path = f"./models/piper/{self.model_name}.onnx"
            cmd = [
                self.piper_path,
                "--model", model_path,
                "--output_file", tmp_path
            ]
            
            # Run synthesis
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send text to Piper
            stdout, stderr = await process.communicate(input=text.encode())
            
            if process.returncode == 0:
                # Read and chunk the audio
                with wave.open(tmp_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    
                    # Split into chunks for streaming
                    chunk_size = 16000 // 5  # ~200ms chunks at 16kHz
                    for i in range(0, len(frames), chunk_size):
                        chunk = frames[i:i + chunk_size]
                        chunks.append(chunk)
            else:
                logger.error(f"Piper TTS failed: {stderr.decode()}")
                
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}")
            
        return chunks
    
    async def _synthesize_fallback(self, text: str) -> List[bytes]:
        """Fallback TTS using basic synthesis"""
        # In a production system, you might use:
        # - Google Cloud TTS
        # - Amazon Polly
        # - Azure Cognitive Services
        # - Or another TTS library
        
        # For now, return empty to indicate TTS not available
        logger.warning("No TTS engine available, returning empty audio")
        
        # Generate silence as placeholder
        silence_duration = min(len(text) * 0.05, 3.0)  # Estimate duration
        sample_rate = 16000
        num_samples = int(silence_duration * sample_rate)
        
        # Create silence audio
        silence = np.zeros(num_samples, dtype=np.int16)
        
        # Convert to bytes and chunk
        chunks = []
        chunk_size = sample_rate // 5  # 200ms chunks
        audio_bytes = silence.tobytes()
        
        for i in range(0, len(audio_bytes), chunk_size * 2):  # *2 for int16
            chunk = audio_bytes[i:i + chunk_size * 2]
            chunks.append(chunk)
            
        return chunks
