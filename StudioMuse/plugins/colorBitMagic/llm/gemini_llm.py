import os
from google import genai
from google.genai import types
from typing import Dict, Any, Optional

class GeminiLLM:
    """
    Simple wrapper for Google Gemini API. 
    Focused on providing text completion capabilities.
    """
    def __init__(self, 
                 temperature: float = 0.7, 
                 model: str = "gemini-2.0-flash", 
                 api_key: Optional[str] = None):
        """
        Initialize the Gemini LLM client.
        
        Args:
            temperature: Controls randomness in response (0.0-1.0)
            model: Gemini model to use
            api_key: Optional API key (defaults to GEMINI_API_KEY env variable)
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Store parameters
        self.model = model
        self.temperature = temperature
        
        # Initialize client
        self.client = genai.Client(api_key=self.api_key)

    def call_api(self, prompt: str) -> str:
        """
        Call the Gemini API with a prompt and return the text response.
        
        Args:
            prompt: Text prompt to send to the API
            
        Returns:
            String containing the text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature
                )
            )
            
            # Return just the text response - parsing will be handled elsewhere
            return response.text

        except Exception as e:
            raise Exception(f"Error calling Gemini API: {type(e).__name__}: {e}")