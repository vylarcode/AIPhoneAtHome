"""
Interruption handling for natural conversation flow
"""
import asyncio
import time
from typing import Optional, Callable
from collections import deque
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class InterruptionHandler:
    """Handle user interruptions during assistant speech"""
    
    def __init__(self):
        self.is_assistant_speaking = False
        self.speech_start_time = 0
        self.interruption_callbacks = []
        self.backchannel_patterns = [
            "uh huh",
            "mm hmm",
            "yeah",
            "okay",
            "right",
            "sure",
            "yes",
            "no",
            "hmm"
        ]
        self.interruption_history = deque(maxlen=10)
        
    def start_assistant_speech(self):
        """Mark when assistant starts speaking"""
        self.is_assistant_speaking = True
        self.speech_start_time = time.time()
        logger.debug("Assistant started speaking")
    
    def end_assistant_speech(self):
        """Mark when assistant stops speaking"""
        if self.is_assistant_speaking:
            duration = time.time() - self.speech_start_time
            self.is_assistant_speaking = False
            logger.debug(f"Assistant stopped speaking after {duration:.2f}s")
            
    def detect_interruption(self, user_transcript: str, user_speaking: bool) -> bool:
        """
        Detect if user is interrupting
        
        Returns:
            True if this is an interruption, False otherwise
        """
        if not self.is_assistant_speaking:
            return False
            
        if not user_speaking:
            return False
            
        # Check if it's just a backchannel (not a real interruption)
        if settings.enable_backchannel_detection:
            if self._is_backchannel(user_transcript):
                logger.debug(f"Backchannel detected: {user_transcript}")
                return False
                
        # Record interruption
        self.interruption_history.append({
            'timestamp': time.time(),
            'transcript': user_transcript,
            'assistant_speech_duration': time.time() - self.speech_start_time
        })
        
        logger.info(f"Interruption detected: {user_transcript}")
        
        # Trigger callbacks
        for callback in self.interruption_callbacks:
            try:
                asyncio.create_task(callback())
            except Exception as e:
                logger.error(f"Interruption callback error: {e}")
                
        return True
    
    def _is_backchannel(self, text: str) -> bool:
        """Check if text is just a backchannel utterance"""
        if not text:
            return False
            
        text_lower = text.lower().strip()
        
        # Check length (backchannels are usually short)
        if len(text_lower.split()) > 3:
            return False
            
        # Check against known patterns
        for pattern in self.backchannel_patterns:
            if text_lower == pattern or text_lower == pattern + ".":
                return True
                
        return False
        
    def register_callback(self, callback: Callable):
        """Register a callback for interruption events"""
        self.interruption_callbacks.append(callback)
        
    def should_stop_speaking(self, interruption_duration: float) -> bool:
        """
        Determine if assistant should stop speaking
        
        Args:
            interruption_duration: How long user has been interrupting
            
        Returns:
            True if should stop, False if should continue
        """
        # Stop if interruption is sustained
        if interruption_duration > 0.5:
            return True
            
        # Check interruption frequency
        recent_interruptions = [
            i for i in self.interruption_history
            if time.time() - i['timestamp'] < 10
        ]
        
        # If user interrupts frequently, be more responsive
        if len(recent_interruptions) > 3:
            return interruption_duration > 0.2
            
        return False
        
    def get_interruption_stats(self) -> dict:
        """Get statistics about interruptions"""
        if not self.interruption_history:
            return {
                'total_interruptions': 0,
                'average_duration': 0,
                'recent_rate': 0
            }
            
        total = len(self.interruption_history)
        
        # Calculate average duration before interruption
        durations = [i['assistant_speech_duration'] for i in self.interruption_history]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate recent rate (last 60 seconds)
        current_time = time.time()
        recent = [
            i for i in self.interruption_history
            if current_time - i['timestamp'] < 60
        ]
        recent_rate = len(recent) / 60 if recent else 0
        
        return {
            'total_interruptions': total,
            'average_duration': avg_duration,
            'recent_rate': recent_rate
        }
        
    def reset(self):
        """Reset interruption tracking"""
        self.is_assistant_speaking = False
        self.speech_start_time = 0
        self.interruption_history.clear()
        logger.debug("Interruption handler reset")
