import os
import logging
from typing import Any, Dict, Optional, List
from pydantic import PrivateAttr
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)

class GeminiLLM(BaseLLM):
    """
    Simple wrapper for Google Gemini API. 
    Focused on providing text completion capabilities.
    """
    _client: Any = PrivateAttr()  # Use PrivateAttr for the genai client

    def __init__(self, 
                 temperature: float = 1.0, 
                 model: str = "gemini-2.0-flash", 
                 api_key: Optional[str] = None,
                 max_output_tokens: int = 2048):
        """
        Initialize the Gemini LLM client.
        
        Args:
            temperature: Controls randomness in response (0.0-1.0)
            model: Gemini model to use
            api_key: Optional API key (defaults to GEMINI_API_KEY env variable)
            max_output_tokens: Maximum number of tokens to generate
        """
        super().__init__(
            model=model,
            api_url="",  # Gemini doesn't use a REST API URL
            temperature=temperature,
            api_key=api_key or os.getenv('GEMINI_API_KEY'),
            max_output_tokens=max_output_tokens
        )
        
        # Initialize the client
        try:
            from google import genai
            from google.genai import types
            # Initialize client as a private attribute
            self._client = genai.Client(api_key=self.api_key)
            
            logger.info(f"Initialized Gemini LLM with model: {self.model}")
        except ImportError as e:
            logger.error(f"Failed to import Google Genai: {e}")
            logger.error("Please install the required package: pip install -q -U google-genai")
            raise ImportError(f"Failed to import Google Genai: {e}. Please install with: pip install -q -U google-genai")
        except Exception as e:
            logger.error(f"Error initializing Gemini LLM: {e}")
            raise
            
    def call_api(self, prompt: str) -> str:
        """
        Call the Gemini API with the given prompt.
        
        Args:
            prompt: The text prompt to send to the API
            
        Returns:
            The generated text response
        """
        try:
            # Import here to avoid circular imports
            from google.genai import types
            
            # Create a generation config
            generation_config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                top_p=0.95,
                top_k=0
            )
            
            # Generate content
            response = self._client.models.generate_content(
                model=self.model,
                contents=[prompt], 
                config=generation_config
            )
            
            # Return the text
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise 