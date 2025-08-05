"""
Test audio processing functionality
"""
import pytest
import numpy as np
import asyncio
from app.audio.vad import VoiceActivityDetector
from app.audio.echo_cancellation import EchoCanceller
from app.audio.noise_reduction import NoiseReducer
from app.utils.audio_utils import mulaw_encode, mulaw_decode, resample_audio

class TestVAD:
    """Test Voice Activity Detection"""
    
    def test_silence_detection(self):
        """Test that silence is not detected as speech"""
        vad = VoiceActivityDetector()
        silence = np.zeros(16000, dtype=np.int16)
        assert not vad.is_speech(silence)
        
    def test_noise_detection(self):
        """Test that random noise is handled properly"""
        vad = VoiceActivityDetector()
        noise = (np.random.randn(16000) * 1000).astype(np.int16)
        # Should not consistently detect as speech
        detections = [vad.is_speech(noise) for _ in range(5)]
        assert not all(detections)
        
    def test_aggressiveness_levels(self):
        """Test different aggressiveness levels"""
        vad = VoiceActivityDetector()
        test_audio = (np.random.randn(16000) * 5000).astype(np.int16)
        
        results = []
        for level in range(4):
            vad.set_aggressiveness(level)
            results.append(vad.is_speech(test_audio))
            
        # Higher aggressiveness should be more strict
        assert results[0] >= results[3] or results[1] >= results[3]

class TestEchoCancellation:
    """Test echo cancellation"""
    
    def test_echo_removal(self):
        """Test basic echo cancellation"""
        canceller = EchoCanceller()
        
        # Create test signal with echo
        original = (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 10000).astype(np.int16)
        echo = original * 0.5  # Simulated echo
        mixed = (original + echo).astype(np.int16)
        
        # Process
        result = canceller.process(mixed, original)
        
        # Should reduce amplitude
        assert np.max(np.abs(result)) < np.max(np.abs(mixed))
        
    def test_no_reference(self):
        """Test processing without reference signal"""
        canceller = EchoCanceller()
        audio = (np.random.randn(16000) * 5000).astype(np.int16)
        result = canceller.process(audio)
        
        # Should still return valid audio
        assert len(result) == len(audio)
        assert result.dtype == np.int16

class TestNoiseReduction:
    """Test noise reduction"""
    
    def test_noise_reduction(self):
        """Test basic noise reduction"""
        reducer = NoiseReducer()
        
        # Create noisy signal
        signal = (np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000)) * 10000).astype(np.int16)
        noise = (np.random.randn(16000) * 2000).astype(np.int16)
        noisy = (signal + noise).astype(np.int16)
        
        # Process
        result = reducer.process(noisy)
        
        # Should maintain signal shape
        assert len(result) == len(noisy)
        assert result.dtype == np.int16
        
    def test_calibration(self):
        """Test noise profile calibration"""
        reducer = NoiseReducer()
        
        # Send multiple frames for calibration
        for _ in range(25):
            noise = (np.random.randn(16000) * 1000).astype(np.int16)
            reducer.process(noise)
            
        # Should have calibrated
        assert reducer.noise_profile is not None

class TestAudioUtils:
    """Test audio utility functions"""
    
    def test_mulaw_conversion(self):
        """Test mulaw encode/decode"""
        original = np.array([0, 1000, -1000, 5000, -5000], dtype=np.int16)
        
        encoded = mulaw_encode(original)
        decoded = mulaw_decode(encoded)
        
        # Should preserve relative values
        assert len(decoded) == len(original)
        assert decoded.dtype == np.int16
        
    def test_resampling(self):
        """Test audio resampling"""
        original = np.random.randn(8000).astype(np.int16)
        
        # Upsample
        upsampled = resample_audio(original, 8000, 16000)
        assert len(upsampled) == len(original) * 2
        
        # Downsample
        downsampled = resample_audio(original, 16000, 8000)
        assert len(downsampled) == len(original) // 2
        
    def test_same_rate_resampling(self):
        """Test resampling with same rate"""
        original = np.random.randn(8000).astype(np.int16)
        resampled = resample_audio(original, 8000, 8000)
        
        # Should return unchanged
        assert np.array_equal(resampled, original)
