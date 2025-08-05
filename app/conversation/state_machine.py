"""
Conversation state machine for managing call flow
"""
from enum import Enum
from typing import Optional, Callable
import logging
import time

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Conversation states"""
    INITIALIZING = "initializing"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"
    ENDING = "ending"
    ENDED = "ended"

class ConversationStateMachine:
    """Manage conversation state transitions"""
    
    def __init__(self, call_sid: str):
        self.call_sid = call_sid
        self.current_state = ConversationState.INITIALIZING
        self.previous_state = None
        self.state_start_time = time.time()
        self.state_history = []
        
        # State transition callbacks
        self.callbacks = {}
        
        # Valid transitions
        self.transitions = {
            ConversationState.INITIALIZING: [
                ConversationState.LISTENING
            ],
            ConversationState.LISTENING: [
                ConversationState.PROCESSING,
                ConversationState.ENDING
            ],
            ConversationState.PROCESSING: [
                ConversationState.SPEAKING,
                ConversationState.LISTENING
            ],
            ConversationState.SPEAKING: [
                ConversationState.LISTENING,
                ConversationState.INTERRUPTED
            ],
            ConversationState.INTERRUPTED: [
                ConversationState.LISTENING
            ],
            ConversationState.ENDING: [
                ConversationState.ENDED
            ],
            ConversationState.ENDED: []
        }
    
    def transition_to(self, new_state: ConversationState) -> bool:
        """Transition to a new state"""
        # Check if transition is valid
        if new_state not in self.transitions.get(self.current_state, []):
            logger.warning(
                f"Invalid transition from {self.current_state} to {new_state}"
            )
            return False
            
        # Record state change
        self.state_history.append({
            'from': self.current_state,
            'to': new_state,
            'timestamp': time.time(),
            'duration': time.time() - self.state_start_time
        })
        
        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_start_time = time.time()
        
        logger.info(f"Call {self.call_sid}: {self.previous_state} -> {self.current_state}")
        
        # Execute callback if registered
        if new_state in self.callbacks:
            try:
                self.callbacks[new_state]()
            except Exception as e:
                logger.error(f"State callback error: {e}")
                
        return True
        
    def register_callback(self, state: ConversationState, callback: Callable):
        """Register a callback for state entry"""
        self.callbacks[state] = callback
        
    def get_state_duration(self) -> float:
        """Get duration in current state"""
        return time.time() - self.state_start_time
        
    def is_in_state(self, state: ConversationState) -> bool:
        """Check if currently in a specific state"""
        return self.current_state == state
        
    def can_transition_to(self, state: ConversationState) -> bool:
        """Check if transition to state is valid"""
        return state in self.transitions.get(self.current_state, [])
        
    def get_summary(self) -> dict:
        """Get state machine summary"""
        return {
            'call_sid': self.call_sid,
            'current_state': self.current_state.value,
            'previous_state': self.previous_state.value if self.previous_state else None,
            'state_duration': self.get_state_duration(),
            'total_states': len(self.state_history)
        }
