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