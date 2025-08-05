"""
Turn management for natural conversation flow
"""
import time
import re
from typing import Optional, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class TurnManager:
    """Manage conversation turns and detect when to respond"""
    
    def __init__(self):
        self.min_speech_duration_ms = 300
        self.max_pause_before_response_ms = 800
        self.interruption_threshold_ms = 100
        
        # Track speech patterns
        self.last_speech_end = 0
        self.speech_start = 0
        self.is_user_speaking = False
        
        # Turn-ending indicators
        self.turn_end_phrases = [
            "what do you think",
            "can you help",
            "do you know",
            "tell me",
            "explain",
            "how about",
            "what about",
            "right?",
            "okay?",
            "you know?"
        ]
    
    def is_turn_complete(self, transcript: str, silence_duration: float) -> bool:
        """Determine if user has finished their turn"""
        silence_ms = silence_duration * 1000
        
        # Check minimum speech duration
        if self.speech_start > 0:
            speech_duration = (time.time() - self.speech_start) * 1000
            if speech_duration < self.min_speech_duration_ms:
                return False
                
        # Check for explicit turn-ending phrases
        if self._contains_turn_end(transcript):
            logger.debug(f"Turn end phrase detected: {transcript}")
            return True
            
        # Check for question marks
        if '?' in transcript:
            logger.debug("Question detected, ending turn")
            return True
            
        # Check silence duration
        if silence_ms > self.max_pause_before_response_ms:
            logger.debug(f"Silence threshold reached: {silence_ms}ms")
            return True
            
        # Check prosodic cues (simplified)
        if self._check_prosody(transcript):
            return True
            
        return False
        
    def _contains_turn_end(self, text: str) -> bool:
        """Check if text contains turn-ending phrases"""
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.turn_end_phrases)
    
    def _check_prosody(self, transcript: str) -> bool:
        """Check prosodic cues for turn completion"""
        # Simplified prosody check based on punctuation and pattern
        
        # Sentences ending with period usually indicate completion
        if transcript.rstrip().endswith('.'):
            return True
            
        # Multiple short sentences often indicate completion
        sentences = re.split(r'[.!?]', transcript)
        if len(sentences) > 2:
            return True
            
        return False
        
    def start_speech(self):
        """Mark the start of user speech"""
        self.speech_start = time.time()
        self.is_user_speaking = True
        logger.debug("User started speaking")
        
    def end_speech(self):
        """Mark the end of user speech"""
        self.last_speech_end = time.time()
        self.is_user_speaking = False
        logger.debug("User stopped speaking")
        
    def is_interruption(self, assistant_speaking: bool) -> bool:
        """Detect if user is interrupting"""
        if assistant_speaking and self.is_user_speaking:
            time_since_start = (time.time() - self.speech_start) * 1000
            if time_since_start > self.interruption_threshold_ms:
                logger.info("User interruption detected")
                return True
        return False
        
    def reset(self):
        """Reset turn tracking"""
        self.last_speech_end = 0
        self.speech_start = 0
        self.is_user_speaking = False
        logger.debug("Turn manager reset")
