"""
Phi-3 Language Model Client
Handles inference with microsoft/Phi-3-mini-4k-instruct model
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Optional, Tuple, Generator
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)


class Phi3Client:
    """
    Client for Phi-3 model inference.
    Supports both base and fine-tuned models with optional quantization.
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self._initialized = False
    
    def initialize(self, use_finetuned: bool = True):
        """
        Initialize the Phi-3 model.
        
        Args:
            use_finetuned: If True, load fine-tuned model if available
        """
        if self._initialized:
            logger.info("Phi-3 model already initialized")
            return
        
        logger.info("Initializing Phi-3 model...")
        
        # Determine device
        if settings.use_gpu and torch.cuda.is_available():
            self.device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = "cpu"
            logger.info("Using CPU")
        
        # Determine model path
        model_path = settings.model_path if use_finetuned and os.path.exists(settings.model_path) else settings.model_name
        logger.info(f"Loading model from: {model_path}")
        
        try:
            # Configure quantization for memory efficiency
            if settings.use_quantization and self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    quantization_config=quantization_config,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16
                )
            else:
                # Load without quantization (for CPU or if disabled)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto" if self.device == "cuda" else None,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                
                if self.device == "cpu":
                    self.model = self.model.to(self.device)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self._initialized = True
            logger.info("Phi-3 model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phi-3 model: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Tuple[str, dict]:
        """
        Generate a response from the model.
        
        Args:
            prompt: User's input message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt for context
            
        Returns:
            Tuple of (response_text, token_usage)
        """
        if not self._initialized:
            self.initialize()
        
        max_tokens = max_tokens or settings.max_tokens
        temperature = temperature or settings.temperature
        
        # Build the conversation format for Qwen
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are an intelligent AI Study Buddy, an educational assistant designed to help students learn effectively. You provide clear, accurate, and helpful explanations on various academic topics. Be encouraging, patient, and thorough in your responses. Use examples when helpful and break down complex concepts into understandable parts."})
        messages.append({"role": "user", "content": prompt})
        
        # Use the tokenizer's chat template
        full_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize input
        inputs = self.tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096 - max_tokens
        ).to(self.device)
        
        input_token_count = inputs["input_ids"].shape[1]
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response (Qwen uses <|im_start|>assistant pattern)
        if "<|im_start|>assistant" in full_output:
            response = full_output.split("<|im_start|>assistant")[-1].strip()
            # Remove trailing end token
            if "<|im_end|>" in response:
                response = response.split("<|im_end|>")[0].strip()
        else:
            # Fallback: remove the input prompt
            response = full_output[len(full_prompt):].strip()
        
        # Clean up any remaining special tokens
        response = response.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()
        
        output_token_count = outputs.shape[1] - input_token_count
        
        token_usage = {
            "input": input_token_count,
            "output": output_token_count
        }
        
        return response, token_usage
    
    def generate_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the model.
        
        Args:
            prompt: User's input message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            
        Yields:
            Response text chunks
        """
        if not self._initialized:
            self.initialize()
        
        # For streaming, we use the same generation but yield chunks
        # Note: True streaming requires TextIteratorStreamer from transformers
        response, _ = self.generate(prompt, max_tokens, temperature, system_prompt)
        
        # Simulate streaming by yielding chunks
        words = response.split()
        chunk_size = 5
        for i in range(0, len(words), chunk_size):
            yield " ".join(words[i:i + chunk_size]) + " "
    
    def is_initialized(self) -> bool:
        """Check if model is initialized"""
        return self._initialized
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_name": settings.model_name,
            "device": self.device,
            "initialized": self._initialized,
            "quantized": settings.use_quantization,
            "max_tokens": settings.max_tokens
        }


# Singleton instance
_phi3_client: Optional[Phi3Client] = None


def get_phi3_client() -> Phi3Client:
    """
    Get the Phi-3 client singleton.
    Lazy initialization - model loads on first use.
    """
    global _phi3_client
    
    if _phi3_client is None:
        _phi3_client = Phi3Client()
    
    return _phi3_client
