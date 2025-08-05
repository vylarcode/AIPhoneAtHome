"""
Audio utility functions for format conversion and processing
"""
import numpy as np
import audioop
from scipy import signal
import struct
import logging

logger = logging.getLogger(__name__)

def mulaw_decode(mulaw_bytes: bytes) -> np.ndarray:
    """Decode mu-law encoded audio to PCM"""
    try:
        # Use audioop to decode mu-law to linear PCM
        pcm_bytes = audioop.ulaw2lin(mulaw_bytes, 2)
        
        # Convert to numpy array
        pcm_array = np.frombuffer(pcm_bytes, dtype=np.int16)
        
        return pcm_array
        
    except Exception as e:
        logger.error(f"Mu-law decode error: {e}")
        return np.array([], dtype=np.int16)

def mulaw_encode(pcm_array: np.ndarray) -> bytes:
    """Encode PCM audio to mu-law"""
    try:
        # Ensure int16 type
        if pcm_array.dtype != np.int16:
            pcm_array = pcm_array.astype(np.int16)
            
        # Convert to bytes
        pcm_bytes = pcm_array.tobytes()
        
        # Use audioop to encode to mu-law
        mulaw_bytes = audioop.lin2ulaw(pcm_bytes, 2)
        
        return mulaw_bytes
        
    except Exception as e:
        logger.error(f"Mu-law encode error: {e}")
        return b''

def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to target sample rate"""
    if orig_sr == target_sr:
        return audio
        
    try:
        # Calculate resampling ratio
        ratio = target_sr / orig_sr
        
        # Calculate new length
        new_length = int(len(audio) * ratio)
        
        # Use scipy for resampling
        resampled = signal.resample(audio, new_length)
        
        # Ensure int16 type
        return resampled.astype(np.int16)
        
    except Exception as e:
        logger.error(f"Resample error: {e}")
        return audio

def normalize_audio(audio: np.ndarray, target_level: float = 0.8) -> np.ndarray:
    """Normalize audio volume"""
    try:
        # Calculate current peak
        peak = np.max(np.abs(audio))
        
        if peak > 0:
            # Calculate scaling factor
            scale = (target_level * 32767) / peak
            
            # Apply scaling
            normalized = audio * scale
            
            # Clip to prevent overflow
            normalized = np.clip(normalized, -32768, 32767)
            
            return normalized.astype(np.int16)
        
        return audio
        
    except Exception as e:
        logger.error(f"Normalize error: {e}")
        return audio

def chunk_audio(audio: bytes, chunk_size_ms: int, sample_rate: int) -> list:
    """Split audio into chunks"""
    try:
        # Calculate chunk size in bytes
        bytes_per_sample = 2  # 16-bit audio
        samples_per_chunk = int(sample_rate * chunk_size_ms / 1000)
        bytes_per_chunk = samples_per_chunk * bytes_per_sample
        
        # Split into chunks
        chunks = []
        for i in range(0, len(audio), bytes_per_chunk):
            chunk = audio[i:i + bytes_per_chunk]
            if chunk:
                chunks.append(chunk)
                
        return chunks
        
    except Exception as e:
        logger.error(f"Chunk error: {e}")
        return []
