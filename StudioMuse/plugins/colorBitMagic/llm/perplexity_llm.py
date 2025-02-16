import os
import requests
from .base_llm import BaseLLM
from typing import Dict, Any

class PerplexityLLM(BaseLLM):
    def __init__(self, 
                 model: str = "sonar-pro",
                 temperature: float = 0.0,
                 top_k: int = 10):
        super().__init__(
            model=model,
            api_url="https://api.perplexity.ai/chat/completions",
            temperature=temperature,
            top_k=top_k,
            api_key=os.getenv('PERPLEXITY_KEY')
        )
        
    def prepare_payload(self, prompt: str) -> Dict[str, Any]:
        payload = super().prepare_payload(prompt)
        payload["top_k"] = self.top_k  # Perplexity-specific parameter
        return payload

    def call_api(self, prompt: str) -> Dict[str, Any]:
        try:
            payload = self.prepare_payload(prompt)
            headers = self.prepare_headers()
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            return self.parse_response(response.json())

        except Exception as e:
            raise Exception(f"Error calling Perplexity API: {type(e).__name__}: {e}")
