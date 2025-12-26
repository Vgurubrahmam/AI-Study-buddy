"""
Gemini Fallback Client
Fallback to Google Gemini API when Phi-3 is unavailable or for comparison
"""

import google.generativeai as genai
from typing import Optional, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Fallback client for Google Gemini API.
    Provides dual API key fallback for reliability.
    """
    
    def __init__(self):
        self.model = None
        self.current_key_index = 0
        self.api_keys = []
        self._initialized = False
    
    def initialize(self):
        """Initialize Gemini API with available keys"""
        if self._initialized:
            return
        
        # Collect available API keys
        if settings.gemini_api_key_1:
            self.api_keys.append(settings.gemini_api_key_1)
        if settings.gemini_api_key_2:
            self.api_keys.append(settings.gemini_api_key_2)
        
        if not self.api_keys:
            logger.warning("No Gemini API keys configured")
            return
        
        try:
            genai.configure(api_key=self.api_keys[0])
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self._initialized = True
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    
    def _switch_api_key(self):
        """Switch to the next available API key"""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        genai.configure(api_key=self.api_keys[self.current_key_index])
        logger.info(f"Switched to Gemini API key {self.current_key_index + 1}")
        return True
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, dict]:
        """
        Generate a response using Gemini API.
        
        Args:
            prompt: User's input message
            system_prompt: Optional system context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple of (response_text, token_usage)
        """
        if not self._initialized:
            self.initialize()
        
        if not self._initialized or not self.model:
            raise RuntimeError("Gemini client not available")
        
        max_tokens = max_tokens or settings.max_tokens
        temperature = temperature or settings.temperature
        
        # Build full prompt with system context
        system_text = system_prompt or "You are an intelligent AI Study Buddy, an educational assistant designed to help students learn effectively. You provide clear, accurate, and helpful explanations on various academic topics. Be encouraging, patient, and thorough in your responses."
        full_prompt = f"{system_text}\n\nUser: {prompt}\n\nAssistant:"
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        # Try generation with fallback
        for attempt in range(len(self.api_keys)):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                # Extract text
                response_text = response.text
                
                # Token usage (approximate)
                token_usage = {
                    "input": len(full_prompt.split()) * 1.3,  # Approximate
                    "output": len(response_text.split()) * 1.3
                }
                
                return response_text, token_usage
                
            except Exception as e:
                logger.warning(f"Gemini generation failed (attempt {attempt + 1}): {e}")
                if not self._switch_api_key():
                    raise
        
        raise RuntimeError("All Gemini API keys exhausted")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        if not self._initialized:
            self.initialize()
        return self._initialized and bool(self.api_keys)


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get the Gemini client singleton"""
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    
    return _gemini_client
