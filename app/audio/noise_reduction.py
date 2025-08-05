"""
Noise reduction for improving audio quality
"""
import numpy as np
from scipy import signal
import noisereduce as nr
import logging

logger = logging.getLogger(__name__)

class NoiseReducer:
    """Advanced noise reduction using spectral subtraction and filtering"""
    
    def __init__(self, reduction_db: float = 20.0):
        self.reduction_db = reduction_db
        self.sample_rate = 16000
        self.noise_profile = None
        self.frame_count = 0
        self.calibration_frames = 20  # Frames to collect for noise profile
        
    def process(self, audio: np.ndarray) -> np.ndarray:
        """
        Reduce noise in audio signal
        
        Args:
            audio: Input audio with noise
            
        Returns:
            Audio with reduced noise
        """
        try:
            # Convert to float for processing
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Calibrate noise profile if needed
            if self.frame_count < self.calibration_frames:
                self._update_noise_profile(audio_float)
                self.frame_count += 1
                
            # Apply noise reduction
            reduced = self._reduce_noise(audio_float)
            
            # Apply comfort noise
            reduced = self._add_comfort_noise(reduced)
            
            # Convert back to int16
            return (reduced * 32768.0).astype(np.int16)
            
        except Exception as e:
            logger.error(f"Noise reduction error: {e}")
            return audio
    
    def _update_noise_profile(self, audio: np.ndarray):
        """Update noise profile from background audio"""
        # Compute spectrum
        f, t, Zxx = signal.stft(audio, nperseg=256)
        spectrum = np.abs(Zxx)
        
        if self.noise_profile is None:
            self.noise_profile = spectrum
        else:
            # Exponential moving average
            alpha = 0.1
            self.noise_profile = alpha * spectrum + (1 - alpha) * self.noise_profile
            
    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Apply noise reduction algorithm"""
        try:
            # Use noisereduce library for sophisticated reduction
            reduced = nr.reduce_noise(
                y=audio,
                sr=self.sample_rate,
                stationary=True,
                prop_decrease=self.reduction_db / 100.0
            )
            
            return reduced
            
        except:
            # Fallback to simple spectral subtraction
            return self._spectral_gate(audio)
            
    def _spectral_gate(self, audio: np.ndarray) -> np.ndarray:
        """Simple spectral gating for noise reduction"""
        # Compute STFT
        f, t, Zxx = signal.stft(audio, nperseg=256)
        
        # Apply spectral gate
        magnitude = np.abs(Zxx)
        phase = np.angle(Zxx)
        
        # Calculate threshold
        if self.noise_profile is not None:
            threshold = self.noise_profile * (10 ** (self.reduction_db / 20))
        else:
            threshold = np.percentile(magnitude, 20)
            
        # Gate frequencies below threshold
        magnitude[magnitude < threshold] *= 0.1
        
        # Reconstruct signal
        Zxx_cleaned = magnitude * np.exp(1j * phase)
        _, cleaned_audio = signal.istft(Zxx_cleaned, nperseg=256)
        
        return cleaned_audio
        
    def _add_comfort_noise(self, audio: np.ndarray) -> np.ndarray:
        """Add slight comfort noise to avoid unnatural silence"""
        # Generate very quiet white noise
        comfort_noise = np.random.normal(0, 0.0001, len(audio))
        
        # Mix with processed audio
        return audio + comfort_noise
        
    def reset(self):
        """Reset noise profile"""
        self.noise_profile = None
        self.frame_count = 0
        logger.debug("Noise reducer reset")
