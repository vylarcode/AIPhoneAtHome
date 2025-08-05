"""
Ollama client for local LLM inference
"""
import aiohttp
import asyncio
import json
from typing import Optional, AsyncGenerator, Dict, Any
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for Ollama local LLM API"""
    
    def __init__(self):
        self.base_url = settings.ollama_host
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens
        self.timeout = aiohttp.ClientTimeout(total=settings.ollama_timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
    
    async def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            await self._ensure_session()
            
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    
                    if self.model in models:
                        logger.info(f"Ollama connection successful. Model {self.model} available.")
                        return True
                    else:
                        logger.warning(f"Model {self.model} not found. Available: {models}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
            
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response from Ollama"""
        await self._ensure_session()
        
        try:
            start_time = time.time()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            if context:
                payload["context"] = context
                
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Log timing
                    latency = (time.time() - start_time) * 1000
                    logger.info(f"Ollama response time: {latency:.0f}ms")
                    
                    return data.get("response", "")
                else:
                    logger.error(f"Ollama generation failed: {response.status}")
                    return ""
                    
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return ""
    
    async def generate_stream(
        self, 
        prompt: str, 
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from Ollama"""
        await self._ensure_session()
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True
            }
            
            if context:
                payload["context"] = context
                
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    yield token
                                    
                                if data.get("done", False):
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                else:
                    logger.error(f"Ollama streaming failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
