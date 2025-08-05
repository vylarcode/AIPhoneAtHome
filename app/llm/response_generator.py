"""
Response generator for conversation
"""
import asyncio
from typing import Optional, List, Dict, Any
import logging
import yaml
import os

from app.llm.ollama_client import OllamaClient
from app.llm.context_manager import ContextManager

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generate contextual responses using LLM"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.context_manager = ContextManager()
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt from configuration"""
        try:
            config_path = "./config/config.yaml"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('conversation', {}).get('system_prompt', '')
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            
        # Default prompt
        return """You are a helpful and conversational AI phone assistant.
Keep responses concise and natural for voice conversation.
Avoid using special formatting or long explanations.
Be friendly and engaging."""
    
    async def generate(self, user_input: str, call_sid: str) -> str:
        """Generate response for user input"""
        try:
            # Get conversation context
            context = self.context_manager.get_context(call_sid)
            
            # Build prompt
            prompt = self._build_prompt(user_input, context)
            
            # Generate response
            response = await self.ollama.generate(prompt)
            
            if response:
                # Update context
                self.context_manager.add_turn(call_sid, user_input, response)
                
                # Process response for voice
                response = self._process_for_voice(response)
                
                return response
            else:
                return "I'm sorry, I didn't quite catch that. Could you please repeat?"
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I apologize, I'm having trouble processing that. Can you try again?"
            
    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build prompt with context"""
        prompt_parts = [self.system_prompt]
        
        # Add conversation history
        if context.get('history'):
            prompt_parts.append("\nConversation history:")
            for turn in context['history'][-5:]:  # Last 5 turns
                prompt_parts.append(f"User: {turn['user']}")
                prompt_parts.append(f"Assistant: {turn['assistant']}")
                
        # Add current input
        prompt_parts.append(f"\nUser: {user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def _process_for_voice(self, text: str) -> str:
        """Process text for natural voice output"""
        # Remove markdown formatting
        text = text.replace('*', '').replace('_', '')
        text = text.replace('#', '').replace('`', '')
        
        # Remove URLs (hard to speak)
        import re
        text = re.sub(r'http[s]?://\S+', 'link', text)
        
        # Expand common abbreviations
        abbreviations = {
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Ms.': 'Miss',
            'etc.': 'et cetera',
            'vs.': 'versus',
            'e.g.': 'for example',
            'i.e.': 'that is',
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
            
        # Ensure proper sentence ending
        if text and text[-1] not in '.!?':
            text += '.'
            
        return text
        
    async def generate_stream(self, user_input: str, call_sid: str):
        """Stream response generation for lower latency"""
        try:
            context = self.context_manager.get_context(call_sid)
            prompt = self._build_prompt(user_input, context)
            
            response_text = ""
            async for token in self.ollama.generate_stream(prompt):
                response_text += token
                
                # Yield complete sentences for TTS
                if token in '.!?':
                    sentence = self._process_for_voice(response_text)
                    if sentence:
                        yield sentence
                        response_text = ""
                        
            # Yield any remaining text
            if response_text:
                yield self._process_for_voice(response_text)
                
            # Update context with complete response
            complete_response = "".join([response_text])
            self.context_manager.add_turn(call_sid, user_input, complete_response)
            
        except Exception as e:
            logger.error(f"Stream generation error: {e}")
            yield "I'm having trouble with that request."
