"""
Twilio WebSocket handler for media streams
"""
import json
import asyncio
import base64
from typing import Optional, Dict, Any
from fastapi import WebSocket
import logging

from app.audio.processor import AudioProcessor
from app.conversation.state_machine import ConversationStateMachine
from app.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class TwilioWebSocketHandler:
    """Handles Twilio Media Stream WebSocket connections"""
    
    def __init__(self, websocket: WebSocket, metrics: MetricsCollector):
        self.websocket = websocket
        self.metrics = metrics
        self.call_sid: Optional[str] = None
        self.stream_sid: Optional[str] = None
        self.audio_processor: Optional[AudioProcessor] = None
        self.conversation_state: Optional[ConversationStateMachine] = None
        self.is_connected = True
        self.tasks = []
        
    async def handle_connection(self) -> Optional[str]:
        """Handle the WebSocket connection lifecycle"""
        try:
            while self.is_connected:
                message = await self.websocket.receive_text()
                await self._process_message(json.loads(message))
                
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            await self.close()
            
        return self.call_sid
    
    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming WebSocket messages"""
        event = message.get("event")
        
        if event == "connected":
            logger.info("WebSocket connected")
            
        elif event == "start":
            await self._handle_start(message)
            
        elif event == "media":
            await self._handle_media(message)
            
        elif event == "stop":
            await self._handle_stop(message)
            
        elif event == "mark":
            await self._handle_mark(message)
            
    async def _handle_start(self, message: Dict[str, Any]):
        """Handle stream start event"""
        start = message.get("start", {})
        self.call_sid = start.get("callSid")
        self.stream_sid = start.get("streamSid")
        
        logger.info(f"Stream started - Call SID: {self.call_sid}")
        
        # Initialize audio processor and conversation state
        self.audio_processor = AudioProcessor(self)
        self.conversation_state = ConversationStateMachine(self.call_sid)
        
        # Start audio processing pipeline
        process_task = asyncio.create_task(self.audio_processor.start())
        self.tasks.append(process_task)
        
        # Record metrics
        self.metrics.record_call_start(self.call_sid)
    
    async def _handle_media(self, message: Dict[str, Any]):
        """Handle incoming audio media"""
        media = message.get("media", {})
        
        if self.audio_processor:
            # Decode base64 audio
            audio_data = base64.b64decode(media.get("payload", ""))
            timestamp = media.get("timestamp")
            
            # Process audio chunk
            await self.audio_processor.process_audio_chunk(audio_data, timestamp)
            
    async def _handle_stop(self, message: Dict[str, Any]):
        """Handle stream stop event"""
        logger.info(f"Stream stopped - Call SID: {self.call_sid}")
        self.is_connected = False
        
        # Record metrics
        if self.call_sid:
            self.metrics.record_call_end(self.call_sid)
            
    async def _handle_mark(self, message: Dict[str, Any]):
        """Handle mark events for audio playback tracking"""
        mark = message.get("mark", {})
        mark_name = mark.get("name")
        
        if self.audio_processor:
            await self.audio_processor.handle_mark(mark_name)
            
    async def send_audio(self, audio_data: bytes, track: str = "outbound"):
        """Send audio to Twilio"""
        if not self.is_connected:
            return
            
        # Encode audio as base64
        audio_payload = base64.b64encode(audio_data).decode("utf-8")
        
        message = {
            "event": "media",
            "streamSid": self.stream_sid,
            "media": {
                "track": track,
                "chunk": "1",
                "timestamp": "0",
                "payload": audio_payload
            }
        }
        
        try:
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            
    async def send_mark(self, name: str):
        """Send a mark event to track audio playback"""
        if not self.is_connected:
            return
            
        message = {
            "event": "mark",
            "streamSid": self.stream_sid,
            "mark": {
                "name": name
            }
        }
        
        try:
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending mark: {e}")
            
    async def close(self):
        """Clean up and close the connection"""
        self.is_connected = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        # Clean up processors
        if self.audio_processor:
            await self.audio_processor.stop()
            
        logger.info(f"WebSocket handler closed for call {self.call_sid}")
