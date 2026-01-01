"""
Gemini Fallback Client
Fallback to Google Gemini API when Phi-3 is unavailable or for comparison
"""

from typing import Optional, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Try importing the new SDK first, fall back to old one
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
    logger.info("Using new google-genai SDK")
except ImportError:
    import google.generativeai as genai
    USE_NEW_SDK = False
    logger.info("Using legacy google-generativeai SDK")


class GeminiClient:
    """
    Fallback client for Google Gemini API.
    Provides dual API key fallback for reliability.
    """
    
    def __init__(self):
        self.client = None
        self.model_name = None
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
            if USE_NEW_SDK:
                self._init_new_sdk()
            else:
                self._init_legacy_sdk()
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    
    def _init_new_sdk(self):
        """Initialize with new google-genai SDK"""
        self.client = genai.Client(api_key=self.api_keys[0])
        # Prioritize models with better free tier limits
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
        for model_name in model_names:
            self.model_name = model_name
            self._initialized = True
            logger.info(f"Gemini client initialized with model: {model_name}")
            break
    
    def _init_legacy_sdk(self):
        """Initialize with legacy google-generativeai SDK"""
        genai.configure(api_key=self.api_keys[0])
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        for model_name in model_names:
            try:
                self.client = genai.GenerativeModel(model_name)
                self.model_name = model_name
                self._initialized = True
                logger.info(f"Gemini client initialized with model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Model {model_name} not available: {e}")
                continue
    
    def _switch_api_key(self):
        """Switch to the next available API key"""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        if USE_NEW_SDK:
            self.client = genai.Client(api_key=self.api_keys[self.current_key_index])
        else:
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
        """Generate a response using Gemini API."""
        if not self._initialized:
            self.initialize()
        
        if not self._initialized:
            raise RuntimeError("Gemini client not available")
        
        max_tokens = max_tokens or settings.max_tokens
        temperature = temperature or settings.temperature
        
        system_text = system_prompt or "You are an intelligent AI Study Buddy, an educational assistant designed to help students learn effectively. You provide clear, accurate, and helpful explanations on various academic topics. Be encouraging, patient, and thorough in your responses."
        full_prompt = f"{system_text}\n\nUser: {prompt}\n\nAssistant:"
        
        for attempt in range(len(self.api_keys)):
            try:
                if USE_NEW_SDK:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=max_tokens,
                            temperature=temperature
                        )
                    )
                    response_text = response.text
                else:
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    )
                    response = self.client.generate_content(
                        full_prompt,
                        generation_config=generation_config
                    )
                    response_text = response.text
                
                token_usage = {
                    "input": int(len(full_prompt.split()) * 1.3),
                    "output": int(len(response_text.split()) * 1.3)
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


_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get the Gemini client singleton"""
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    
    return _gemini_client
