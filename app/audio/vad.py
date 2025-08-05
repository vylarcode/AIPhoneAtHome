"""
Voice Activity Detection for speech/silence detection
"""
import numpy as np
import webrtcvad
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Multi-level VAD for accurate speech detection"""
    
    def __init__(self):
        self.aggressiveness = settings.vad_aggressiveness
        self.vad = webrtcvad.Vad(self.aggressiveness)
        self.energy_threshold = 0.01
        self.zcr_threshold = 0.1
        
    def is_speech(self, audio: np.ndarray, sample_rate: int = 16000) -> bool:
        """Detect if audio contains speech"""
        try:
            # Level 1: Energy-based detection
            if not self._check_energy(audio):
                return False
                
            # Level 2: Zero-crossing rate
            if not self._check_zcr(audio):
                return False
                
            # Level 3: WebRTC VAD
            return self._check_webrtc_vad(audio, sample_rate)
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def _check_energy(self, audio: np.ndarray) -> bool:
        """Check audio energy level"""
        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        normalized_energy = energy / 32768.0  # Normalize for int16
        
        return normalized_energy > self.energy_threshold
        
    def _check_zcr(self, audio: np.ndarray) -> bool:
        """Check zero-crossing rate"""
        # Calculate zero-crossing rate
        signs = np.sign(audio)
        signs[signs == 0] = -1
        zcr = len(np.where(np.diff(signs))[0]) / len(audio)
        
        return zcr < self.zcr_threshold
        
    def _check_webrtc_vad(self, audio: np.ndarray, sample_rate: int) -> bool:
        """Check using WebRTC VAD"""
        # WebRTC VAD requires specific sample rates and frame sizes
        supported_rates = [8000, 16000, 32000, 48000]
        
        if sample_rate not in supported_rates:
            # Resample or skip WebRTC VAD
            return True
            
        # Frame must be 10, 20, or 30 ms
        frame_duration_ms = 20
        frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        # Process frames
        num_speech_frames = 0
        num_frames = 0
        
        audio_bytes = audio.astype(np.int16).tobytes()
        
        for i in range(0, len(audio_bytes) - frame_size * 2, frame_size * 2):
            frame = audio_bytes[i:i + frame_size * 2]
            
            try:
                if self.vad.is_speech(frame, sample_rate):
                    num_speech_frames += 1
                num_frames += 1
            except:
                continue
                
        # Consider speech if >30% frames contain speech
        if num_frames > 0:
            speech_ratio = num_speech_frames / num_frames
            return speech_ratio > 0.3
            
        return False
        
    def set_aggressiveness(self, level: int):
        """Update VAD aggressiveness (0-3)"""
        if 0 <= level <= 3:
            self.aggressiveness = level
            self.vad = webrtcvad.Vad(level)
            logger.info(f"VAD aggressiveness set to {level}")
