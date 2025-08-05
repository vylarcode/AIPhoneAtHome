"""
Main audio processing pipeline
"""
import asyncio
import numpy as np
from typing import Optional, Tuple
import logging
from collections import deque
import time

from app.audio.whisper_turbo import WhisperTurbo
from app.audio.tts_engine import TTSEngine
from app.audio.vad import VoiceActivityDetector
from app.audio.echo_cancellation import EchoCanceller
from app.audio.noise_reduction import NoiseReducer
from app.llm.response_generator import ResponseGenerator
from app.conversation.turn_manager import TurnManager
from app.utils.audio_utils import mulaw_decode, mulaw_encode, resample_audio
from app.config import settings

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Main audio processing pipeline"""
    
    def __init__(self, websocket_handler):
        self.websocket_handler = websocket_handler
        self.whisper = WhisperTurbo()
        self.tts = TTSEngine()
        self.vad = VoiceActivityDetector()
        self.echo_canceller = EchoCanceller()
        self.noise_reducer = NoiseReducer()
        self.response_generator = ResponseGenerator()
        self.turn_manager = TurnManager()
        
        # Audio buffers
        self.audio_buffer = deque(maxlen=50)  # ~1 second of audio at 20ms chunks
        self.processed_audio = bytearray()
        self.output_buffer = deque()
        
        # State tracking
        self.is_processing = False
        self.is_speaking = False
        self.last_speech_time = 0
        self.current_transcript = ""
        
        # Timing metrics
        self.process_start_time = 0
        self.first_response_time = 0
        
    async def start(self):
        """Start the audio processing pipeline"""
        self.is_processing = True
        
        # Start concurrent processing tasks
        tasks = [
            asyncio.create_task(self._process_input_audio()),
            asyncio.create_task(self._process_output_audio()),
            asyncio.create_task(self._monitor_silence())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
        finally:
            self.is_processing = False
    
    async def process_audio_chunk(self, audio_data: bytes, timestamp: int):
        """Process incoming audio chunk from Twilio"""
        # Add to buffer for processing
        self.audio_buffer.append((audio_data, timestamp))
        
    async def _process_input_audio(self):
        """Process input audio for speech recognition"""
        while self.is_processing:
            if len(self.audio_buffer) >= 10:  # Process ~200ms chunks
                # Collect audio chunks
                chunks = []
                for _ in range(10):
                    if self.audio_buffer:
                        chunk, _ = self.audio_buffer.popleft()
                        chunks.append(chunk)
                
                if chunks:
                    # Combine and decode audio
                    combined_audio = b''.join(chunks)
                    pcm_audio = mulaw_decode(combined_audio)
                    
                    # Apply audio processing
                    if settings.enable_echo_cancellation:
                        pcm_audio = self.echo_canceller.process(pcm_audio)
                    if settings.enable_noise_reduction:
                        pcm_audio = self.noise_reducer.process(pcm_audio)
                    
                    # Resample for Whisper (8kHz -> 16kHz)
                    resampled_audio = resample_audio(pcm_audio, 8000, 16000)
                    
                    # Check for voice activity
                    if self.vad.is_speech(resampled_audio):
                        self.last_speech_time = time.time()
                        self.processed_audio.extend(resampled_audio)
                        
                        # Process if we have enough audio
                        if len(self.processed_audio) >= 16000 * 0.3:  # 300ms
                            await self._transcribe_audio()
                    
            await asyncio.sleep(0.02)  # 20ms loop
    
    async def _transcribe_audio(self):
        """Transcribe accumulated audio"""
        if not self.processed_audio:
            return
            
        # Convert to numpy array
        audio_array = np.frombuffer(self.processed_audio, dtype=np.int16)
        
        # Clear buffer for next chunk
        self.processed_audio.clear()
        
        # Transcribe with Whisper
        start_time = time.time()
        transcript = await self.whisper.transcribe(audio_array)
        transcription_time = (time.time() - start_time) * 1000
        
        logger.info(f"Transcription: '{transcript}' (took {transcription_time:.0f}ms)")
        
        if transcript:
            self.current_transcript += " " + transcript
            
            # Check for turn completion
            if self.turn_manager.is_turn_complete(transcript, time.time() - self.last_speech_time):
                await self._generate_response()
                
    async def _generate_response(self):
        """Generate and queue response for the current transcript"""
        if not self.current_transcript.strip():
            return
            
        logger.info(f"Generating response for: {self.current_transcript}")
        
        # Record timing
        self.process_start_time = time.time()
        
        # Generate response
        response_text = await self.response_generator.generate(
            self.current_transcript,
            self.websocket_handler.call_sid
        )
        
        # Clear transcript for next turn
        self.current_transcript = ""
        
        if response_text:
            # Generate TTS audio
            audio_chunks = await self.tts.synthesize(response_text)
            
            # Queue audio for output
            for chunk in audio_chunks:
                self.output_buffer.append(chunk)
                
            # Record first response time
            if self.first_response_time == 0:
                self.first_response_time = (time.time() - self.process_start_time) * 1000
                logger.info(f"First response time: {self.first_response_time:.0f}ms")
    
    async def _process_output_audio(self):
        """Send TTS audio to Twilio"""
        while self.is_processing:
            if self.output_buffer:
                audio_chunk = self.output_buffer.popleft()
                
                # Resample back to 8kHz
                resampled = resample_audio(audio_chunk, 16000, 8000)
                
                # Encode to mulaw
                mulaw_audio = mulaw_encode(resampled)
                
                # Send to Twilio
                await self.websocket_handler.send_audio(mulaw_audio)
                
                # Mark as speaking
                self.is_speaking = True
                
                # Small delay for smooth streaming
                await asyncio.sleep(0.02)
            else:
                self.is_speaking = False
                await asyncio.sleep(0.01)
                
    async def _monitor_silence(self):
        """Monitor for extended silence and prompt if needed"""
        while self.is_processing:
            current_time = time.time()
            silence_duration = current_time - self.last_speech_time
            
            # Check for extended silence (e.g., 3 seconds)
            if silence_duration > 3.0 and not self.is_speaking:
                if self.current_transcript:
                    # User started speaking but stopped
                    await self._generate_response()
                elif silence_duration > 5.0:
                    # Long silence, prompt user
                    logger.info("Extended silence detected, prompting user")
                    prompt_text = "Hello? Are you still there?"
                    audio_chunks = await self.tts.synthesize(prompt_text)
                    for chunk in audio_chunks:
                        self.output_buffer.append(chunk)
                    self.last_speech_time = current_time  # Reset timer
                    
            await asyncio.sleep(0.5)
            
    async def handle_interruption(self):
        """Handle user interruption"""
        if self.is_speaking:
            logger.info("User interruption detected")
            # Clear output buffer
            self.output_buffer.clear()
            self.is_speaking = False
            
            # Send stop mark to Twilio
            await self.websocket_handler.send_mark("interrupted")
            
    async def handle_mark(self, mark_name: str):
        """Handle mark events from Twilio"""
        logger.debug(f"Received mark: {mark_name}")
        
    async def stop(self):
        """Stop audio processing"""
        self.is_processing = False
        logger.info("Audio processor stopped")
