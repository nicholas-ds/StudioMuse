# llm/base_llm.py (updated)
from pydantic import BaseModel
import os
import requests
from typing import Dict, Any, Optional, List

class BaseLLM(BaseModel):
    model: str
    temperature: float = 0.0
    top_k: Optional[int] = 10
    api_key: Optional[str] = None
    api_url: str
    
    def __init__(self, 
                 model: str,
                 api_url: str,
                 temperature: float = 0.0, 
                 top_k: Optional[int] = 10,
                 api_key: Optional[str] = None):
        super().__init__(
            model=model,
            temperature=temperature,
            top_k=top_k,
            api_url=api_url,
            api_key=api_key
        )

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

    def parse_response(self, response_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the API response
        Override this method for providers with different response structures
        """
        return response_json

    def call_api(self, prompt: str) -> Dict[str, Any]:
        """
        Generic method to call the LLM API with standard error handling.
        """
        try:
            payload = self.prepare_payload(prompt)
            headers = self.prepare_headers()
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return self.parse_response(response.json())

        except Exception as e:
            raise Exception(f"Error calling API: {type(e).__name__}: {e}")