"""
Echo cancellation for removing audio feedback
"""
import numpy as np
from scipy import signal
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EchoCanceller:
    """Acoustic Echo Cancellation using adaptive filtering"""
    
    def __init__(self, filter_length: int = 256, mu: float = 0.1):
        self.filter_length = filter_length
        self.mu = mu  # Learning rate
        self.weights = np.zeros(filter_length)
        self.reference_buffer = np.zeros(filter_length)
        self.error_threshold = 0.01
        
    def process(self, audio: np.ndarray, reference: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Cancel echo from audio signal
        
        Args:
            audio: Input audio with potential echo
            reference: Reference signal (speaker output)
            
        Returns:
            Audio with echo removed
        """
        try:
            # Convert to float for processing
            audio_float = audio.astype(np.float32) / 32768.0
            
            if reference is not None:
                ref_float = reference.astype(np.float32) / 32768.0
                return self._nlms_filter(audio_float, ref_float)
            else:
                # Simple spectral subtraction if no reference
                return self._spectral_subtraction(audio_float)
                
        except Exception as e:
            logger.error(f"Echo cancellation error: {e}")
            return audio
    
    def _nlms_filter(self, audio: np.ndarray, reference: np.ndarray) -> np.ndarray:
        """Normalized Least Mean Squares adaptive filter"""
        output = np.zeros_like(audio)
        
        for i in range(len(audio)):
            # Update reference buffer
            self.reference_buffer = np.roll(self.reference_buffer, 1)
            if i < len(reference):
                self.reference_buffer[0] = reference[i]
            
            # Predict echo
            echo_estimate = np.dot(self.weights, self.reference_buffer)
            
            # Calculate error
            error = audio[i] - echo_estimate
            output[i] = error
            
            # Update weights (NLMS algorithm)
            norm = np.dot(self.reference_buffer, self.reference_buffer) + 1e-6
            self.weights += self.mu * error * self.reference_buffer / norm
            
        # Convert back to int16
        return (output * 32768.0).astype(np.int16)
        
    def _spectral_subtraction(self, audio: np.ndarray) -> np.ndarray:
        """Simple spectral subtraction for echo reduction"""
        # Compute STFT
        f, t, Zxx = signal.stft(audio, nperseg=256)
        
        # Estimate noise spectrum (simple approach)
        noise_spectrum = np.median(np.abs(Zxx), axis=1, keepdims=True)
        
        # Subtract noise spectrum
        cleaned_spectrum = np.abs(Zxx) - noise_spectrum
        cleaned_spectrum = np.maximum(cleaned_spectrum, 0)
        
        # Preserve phase
        phase = np.angle(Zxx)
        cleaned_complex = cleaned_spectrum * np.exp(1j * phase)
        
        # Inverse STFT
        _, cleaned_audio = signal.istft(cleaned_complex, nperseg=256)
        
        # Convert back to int16
        return (cleaned_audio * 32768.0).astype(np.int16)
        
    def reset(self):
        """Reset the adaptive filter"""
        self.weights = np.zeros(self.filter_length)
        self.reference_buffer = np.zeros(self.filter_length)
        logger.debug("Echo canceller reset")
