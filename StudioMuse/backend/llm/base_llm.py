import logging
from pydantic import BaseModel
import os
import requests
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseLLM(BaseModel):
    model: str
    temperature: float = 0.0
    top_k: Optional[int] = 10
    api_key: Optional[str] = None
    api_url: str
    max_output_tokens: Optional[int] = 500
    
    def __init__(self, 
                 model: str,
                 api_url: str,
                 temperature: float = 0.0, 
                 top_k: Optional[int] = 10,
                 api_key: Optional[str] = None,
                 max_output_tokens: Optional[int] = 500):
        super().__init__(
            model=model,
            temperature=temperature,
            top_k=top_k,
            api_url=api_url,
            api_key=api_key,
            max_output_tokens=max_output_tokens
        )
        logger.info(f"Initialized BaseLLM with model: {model}")

    def prepare_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Prepare messages in the format required by the LLM provider
        Override this method for providers with different message formats
        """
        return [{"role": "user", "content": prompt}]

    def prepare_payload(self, prompt: str) -> Dict[str, Any]:
        """
        Prepare the API payload
        Override this method for providers with different payload structures
        """
        return {
            "model": self.model,
            "messages": self.prepare_messages(prompt),
            "temperature": self.temperature,
        }

    def prepare_headers(self) -> Dict[str, str]:
        """
        Prepare the API headers
        Override this method for providers with different header requirements
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def call_api(self, prompt: str) -> str:
        """
        Call the API with the given prompt.
        
        Args:
            prompt: The input text to send to the API
            
        Returns:
            str: The generated text response
            
        Raises:
            Exception: If there's an error calling the API
        """
        logger.info(f"BaseLLM.call_api called with prompt: {prompt[:50]}...")
        payload = self.prepare_payload(prompt)
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Unexpected response format: {result}")
                raise Exception(f"Unexpected response format: {result}")
                
        except Exception as e:
            logger.error(f"Error calling API: {e}")
            raise Exception(f"Error calling API: {e}") 