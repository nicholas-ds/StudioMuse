# llm/perplexity_llm.py (updated)
import os
from typing import Dict, Any
from .base_llm import BaseLLM

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
        """Override to include Perplexity-specific parameters."""
        payload = super().prepare_payload(prompt)
        payload["top_k"] = self.top_k  # Perplexity-specific parameter
        return payload