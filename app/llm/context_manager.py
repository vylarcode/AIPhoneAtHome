"""
Context manager for conversation history
"""
from typing import Dict, Any, List, Optional
import time
import logging
from collections import defaultdict, deque

from app.config import settings

logger = logging.getLogger(__name__)

class ContextManager:
    """Manage conversation context and history"""
    
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = defaultdict(self._create_context)
        self.max_history_turns = 10
        self.context_window_tokens = 2048
        
    def _create_context(self) -> Dict[str, Any]:
        """Create a new context for a call"""
        return {
            'call_sid': None,
            'start_time': time.time(),
            'history': deque(maxlen=self.max_history_turns),
            'metadata': {},
            'turn_count': 0
        }
        
    def get_context(self, call_sid: str) -> Dict[str, Any]:
        """Get context for a call"""
        if call_sid not in self.contexts:
            self.contexts[call_sid]['call_sid'] = call_sid
        return self.contexts[call_sid]
    
    def add_turn(self, call_sid: str, user_input: str, assistant_response: str):
        """Add a conversation turn to history"""
        context = self.get_context(call_sid)
        
        turn = {
            'user': user_input,
            'assistant': assistant_response,
            'timestamp': time.time(),
            'turn_number': context['turn_count']
        }
        
        context['history'].append(turn)
        context['turn_count'] += 1
        
        logger.debug(f"Added turn {context['turn_count']} for call {call_sid}")
        
    def update_metadata(self, call_sid: str, key: str, value: Any):
        """Update metadata for a call"""
        context = self.get_context(call_sid)
        context['metadata'][key] = value
        
    def get_history_text(self, call_sid: str, max_turns: Optional[int] = None) -> str:
        """Get conversation history as text"""
        context = self.get_context(call_sid)
        history = list(context['history'])
        
        if max_turns:
            history = history[-max_turns:]
            
        text_parts = []
        for turn in history:
            text_parts.append(f"User: {turn['user']}")
            text_parts.append(f"Assistant: {turn['assistant']}")
            
        return "\n".join(text_parts)
        
    def clear_context(self, call_sid: str):
        """Clear context for a call"""
        if call_sid in self.contexts:
            del self.contexts[call_sid]
            logger.info(f"Cleared context for call {call_sid}")
            
    def get_summary(self, call_sid: str) -> Dict[str, Any]:
        """Get summary of conversation"""
        context = self.get_context(call_sid)
        
        duration = time.time() - context['start_time']
        
        return {
            'call_sid': call_sid,
            'duration_seconds': duration,
            'turn_count': context['turn_count'],
            'start_time': context['start_time'],
            'metadata': context['metadata']
        }
