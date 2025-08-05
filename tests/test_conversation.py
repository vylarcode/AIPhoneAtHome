"""
Test conversation flow and management
"""
import pytest
import time
from app.conversation.turn_manager import TurnManager
from app.conversation.state_machine import ConversationStateMachine, ConversationState
from app.llm.context_manager import ContextManager

class TestTurnManager:
    """Test turn management"""
    
    def test_turn_detection(self):
        """Test turn completion detection"""
        manager = TurnManager()
        
        # Question should end turn
        assert manager.is_turn_complete("What is your name?", 0.5)
        
        # Turn-ending phrase should end turn
        assert manager.is_turn_complete("Can you help me with this", 0.5)
        
        # Long silence should end turn
        assert manager.is_turn_complete("Hello", 1.0)
        
        # Short silence should not end turn
        assert not manager.is_turn_complete("Hello", 0.2)
        
    def test_interruption_detection(self):
        """Test interruption detection"""
        manager = TurnManager()
        
        # Start speech
        manager.start_speech()
        time.sleep(0.2)  # Wait past threshold
        
        # Should detect interruption
        assert manager.is_interruption(assistant_speaking=True)
        
        # Should not detect if assistant not speaking
        assert not manager.is_interruption(assistant_speaking=False)

class TestStateMachine:
    """Test conversation state machine"""
    
    def test_state_transitions(self):
        """Test valid state transitions"""
        sm = ConversationStateMachine("test_call")
        
        # Initial state
        assert sm.current_state == ConversationState.INITIALIZING
        
        # Valid transition
        assert sm.transition_to(ConversationState.LISTENING)
        assert sm.current_state == ConversationState.LISTENING
        
        # Invalid transition
        assert not sm.transition_to(ConversationState.ENDED)
        assert sm.current_state == ConversationState.LISTENING
        
    def test_state_callbacks(self):
        """Test state transition callbacks"""
        sm = ConversationStateMachine("test_call")
        
        callback_triggered = False
        
        def test_callback():
            nonlocal callback_triggered
            callback_triggered = True
            
        sm.register_callback(ConversationState.LISTENING, test_callback)
        sm.transition_to(ConversationState.LISTENING)
        
        assert callback_triggered
        
    def test_state_duration(self):
        """Test state duration tracking"""
        sm = ConversationStateMachine("test_call")
        sm.transition_to(ConversationState.LISTENING)
        
        time.sleep(0.1)
        duration = sm.get_state_duration()
        
        assert duration >= 0.1

class TestContextManager:
    """Test context management"""
    
    def test_context_creation(self):
        """Test context creation"""
        manager = ContextManager()
        context = manager.get_context("test_call")
        
        assert context['call_sid'] == "test_call"
        assert context['turn_count'] == 0
        assert len(context['history']) == 0
        
    def test_turn_addition(self):
        """Test adding conversation turns"""
        manager = ContextManager()
        
        manager.add_turn("test_call", "Hello", "Hi there!")
        context = manager.get_context("test_call")
        
        assert context['turn_count'] == 1
        assert len(context['history']) == 1
        assert context['history'][0]['user'] == "Hello"
        assert context['history'][0]['assistant'] == "Hi there!"
        
    def test_history_limit(self):
        """Test history size limit"""
        manager = ContextManager()
        
        # Add more than max turns
        for i in range(15):
            manager.add_turn("test_call", f"User {i}", f"Assistant {i}")
            
        context = manager.get_context("test_call")
        
        # Should only keep max_history_turns
        assert len(context['history']) == manager.max_history_turns
        
    def test_metadata(self):
        """Test metadata management"""
        manager = ContextManager()
        
        manager.update_metadata("test_call", "language", "en")
        manager.update_metadata("test_call", "sentiment", "positive")
        
        context = manager.get_context("test_call")
        
        assert context['metadata']['language'] == "en"
        assert context['metadata']['sentiment'] == "positive"
