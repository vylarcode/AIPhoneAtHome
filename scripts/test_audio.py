#!/usr/bin/env python3
"""
Test audio functionality
"""
import asyncio
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.audio.whisper_turbo import WhisperTurbo
from app.audio.tts_engine import TTSEngine
from app.audio.vad import VoiceActivityDetector
from app.utils.audio_utils import mulaw_encode, mulaw_decode, resample_audio

async def test_whisper():
    """Test Whisper STT"""
    print("\nTesting Whisper STT...")
    
    try:
        whisper = WhisperTurbo()
        await whisper.initialize()
        
        # Create test audio (sine wave)
        sample_rate = 16000
        duration = 2.0
        frequency = 440
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        
        # Test transcription
        result = await whisper.transcribe(audio)
        print(f"✅ Whisper test passed (transcribed: '{result}')")
        return True
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

async def test_tts():
    """Test TTS synthesis"""
    print("\nTesting TTS...")
    
    try:
        tts = TTSEngine()
        await tts.initialize()
        
        # Test synthesis
        text = "Hello, this is a test of the text to speech system."
        chunks = await tts.synthesize(text)
        
        if chunks:
            total_size = sum(len(chunk) for chunk in chunks)
            print(f"✅ TTS test passed ({len(chunks)} chunks, {total_size} bytes)")
            return True
        else:
            print("⚠️ TTS returned no audio (may not be configured)")
            return False
            
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_vad():
    """Test Voice Activity Detection"""
    print("\nTesting VAD...")
    
    try:
        vad = VoiceActivityDetector()
        
        # Test with silence
        silence = np.zeros(16000, dtype=np.int16)
        is_speech_silence = vad.is_speech(silence)
        
        # Test with noise
        noise = (np.random.randn(16000) * 1000).astype(np.int16)
        is_speech_noise = vad.is_speech(noise)
        
        print(f"   Silence detected as speech: {is_speech_silence}")
        print(f"   Noise detected as speech: {is_speech_noise}")
        
        if not is_speech_silence:
            print("✅ VAD test passed")
            return True
        else:
            print("⚠️ VAD may need tuning")
            return False
            
    except Exception as e:
        print(f"❌ VAD test failed: {e}")
        return False

def test_audio_utils():
    """Test audio utility functions"""
    print("\nTesting audio utilities...")
    
    try:
        # Create test audio
        test_audio = np.array([0, 1000, -1000, 5000, -5000], dtype=np.int16)
        
        # Test mulaw encode/decode
        encoded = mulaw_encode(test_audio)
        decoded = mulaw_decode(encoded)
        
        # Test resampling
        resampled = resample_audio(test_audio, 8000, 16000)
        
        print(f"   Original: {test_audio[:3]}")
        print(f"   Encoded size: {len(encoded)} bytes")
        print(f"   Decoded: {decoded[:3]}")
        print(f"   Resampled size: {len(resampled)}")
        
        print("✅ Audio utilities test passed")
        return True
        
    except Exception as e:
        print(f"❌ Audio utilities test failed: {e}")
        return False

async def main():
    """Run all audio tests"""
    print("=" * 50)
    print("Audio System Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(await test_whisper())
    results.append(await test_tts())
    results.append(test_vad())
    results.append(test_audio_utils())
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All audio tests passed!")
    else:
        print("⚠️ Some tests failed or need attention")
        
    return all(results)

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
