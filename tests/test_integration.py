"""
Integration tests for the Phone AI Agent
"""
import pytest
import asyncio
import aiohttp
import json
from unittest.mock import Mock, patch, AsyncMock
from app.websocket_handler import TwilioWebSocketHandler
from app.audio.processor import AudioProcessor
from app.llm.response_generator import ResponseGenerator

@pytest.mark.asyncio
class TestWebSocketHandler:
    """Test WebSocket handler integration"""
    
    async def test_connection_handling(self):
        """Test WebSocket connection lifecycle"""
        # Create mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.receive_text = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        # Create mock metrics
        mock_metrics = Mock()
        mock_metrics.record_call_start = Mock()
        mock_metrics.record_call_end = Mock()
        
        # Create handler
        handler = TwilioWebSocketHandler(mock_ws, mock_metrics)
        
        # Test start message
        start_message = {
            "event": "start",
            "start": {
                "callSid": "CA123456",
                "streamSid": "MZ789012"
            }
        }
        
        mock_ws.receive_text.return_value = json.dumps(start_message)
        
        # Process message
        await handler._process_message(start_message)
        
        assert handler.call_sid == "CA123456"
        assert handler.stream_sid == "MZ789012"
        mock_metrics.record_call_start.assert_called_with("CA123456")

@pytest.mark.asyncio
class TestAudioPipeline:
    """Test audio processing pipeline"""
    
    async def test_pipeline_flow(self):
        """Test complete audio pipeline"""
        # Create mock WebSocket handler
        mock_handler = AsyncMock()
        mock_handler.call_sid = "test_call"
        mock_handler.send_audio = AsyncMock()
        
        # Create processor
        processor = AudioProcessor(mock_handler)
        
        # Test audio processing
        test_audio = b'\x00' * 160  # 20ms of mulaw audio at 8kHz
        
        await processor.process_audio_chunk(test_audio, 0)
        
        # Check buffer
        assert len(processor.audio_buffer) > 0
        
    async def test_response_generation(self):
        """Test response generation flow"""
        generator = ResponseGenerator()
        
        # Test simple response
        response = await generator.generate("Hello", "test_call")
        
        assert response is not None
        assert len(response) > 0
        
@pytest.mark.asyncio
class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.mark.skip(reason="Requires running server")
    async def test_api_health(self):
        """Test API health endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] in ['healthy', 'degraded']
                
    @pytest.mark.skip(reason="Requires Ollama running")
    async def test_ollama_connection(self):
        """Test Ollama connection"""
        from app.llm.ollama_client import OllamaClient
        
        client = OllamaClient()
        connected = await client.test_connection()
        assert connected
        
    @pytest.mark.skip(reason="Requires models installed")
    async def test_whisper_initialization(self):
        """Test Whisper model initialization"""
        from app.audio.whisper_turbo import WhisperTurbo
        
        whisper = WhisperTurbo()
        await whisper.initialize()
        assert whisper.is_ready()

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.config import settings
        from app.websocket_handler import TwilioWebSocketHandler
        from app.audio.processor import AudioProcessor
        from app.audio.whisper_turbo import WhisperTurbo
        from app.llm.ollama_client import OllamaClient
        from app.conversation.state_machine import ConversationStateMachine
        
        assert app is not None
        assert settings is not None
        
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")
