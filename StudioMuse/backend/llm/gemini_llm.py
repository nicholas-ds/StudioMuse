import os
from typing import Dict, Any, Optional
from .base_llm import BaseLLM

class GeminiLLM(BaseLLM):
    """
    Simple wrapper for Google Gemini API. 
    Focused on providing text completion capabilities.
    """
    def __init__(self, 
                 temperature: float = 1.0, 
                 model: str = "gemini-1.5-flash", 
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
            api_url="",  # Gemini doesn't use a REST API URL directly
            temperature=temperature,
            api_key=api_key or os.getenv('GEMINI_API_KEY'),
            max_output_tokens=max_output_tokens
        )
        # We'll initialize the Google client when needed to avoid
        # importing google.generativeai during module loading

    def call_api(self, prompt: str) -> str:
        """
        Override the base call_api method since Gemini uses a different API pattern.
        
        Args:
            prompt: The input text to send to Gemini
            
        Returns:
            str: The generated text response
            
        Raises:
            Exception: If there's an error calling the Gemini API
        """
        try:
            # Import here to avoid requiring the package until it's needed
            import google.generativeai as genai
            from google.generativeai import types
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Create a model instance
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens
                )
            )
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Return the text response
            return response.text

        except Exception as e:
            raise Exception(f"Error calling Gemini API: {type(e).__name__}: {e}") 