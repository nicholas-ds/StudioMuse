import os
import logging
from typing import Dict, Any, Optional
from .base_llm import BaseLLM
from pydantic import PrivateAttr

# Configure logging
logging.basicConfig(level=logging.INFO)
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
            self._types = types
            
            logger.info(f"Initialized Gemini LLM with model: {self.model}")
        except ImportError as e:
            logger.error(f"Failed to import Google Generative AI: {e}")
            logger.error("Please install the required package: pip install google-generativeai")
            raise ImportError(f"Failed to import Google Generative AI: {e}. Please install with: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Error initializing Gemini LLM: {e}")
            raise

    def call_api(self, prompt: str) -> str:
        """
        Override the base call_api method since Gemini uses a different API pattern.
        Instead of REST API calls, this implementation uses Google's genai client library
        which handles authentication and API interaction differently.
        
        Args:
            prompt: The input text to send to Gemini
            
        Returns:
            str: The generated text response
            
        Raises:
            Exception: If there's an error calling the Gemini API
        """
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=[prompt], 
                config=self._types.GenerateContentConfig(
                    max_output_tokens=self.max_output_tokens,
                    temperature=self.temperature
                )
            )
            return response.text

        except Exception as e:
            logger.error(f"Error calling Gemini API: {type(e).__name__}: {e}")
            raise Exception(f"Error calling Gemini API: {type(e).__name__}: {e}") 