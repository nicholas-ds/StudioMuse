# llm/llm_service_provider.py
from typing import Dict, Type, Optional, Any
from gi.repository import Gimp

class LLMServiceProvider:
    """Factory class for LLM service instances."""
    
    _instances = {}
    _providers = {}
    _initialized = False
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type):
        """Register a new LLM provider."""
        cls._providers[name] = provider_class
        Gimp.message(f"Registered LLM provider: {name}")
    
    @classmethod
    def get_llm(cls, provider_name: str, **kwargs) -> Any:
        """Get an instance of the specified LLM provider."""
        # Ensure providers are initialized
        if not cls._initialized:
            initialize_llm_providers()
            
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        
        # Create a unique key based on provider name and parameters
        param_str = "-".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key = f"{provider_name}:{param_str}"
        
        # Create new instance if not exists
        if key not in cls._instances:
            try:
                provider_class = cls._providers[provider_name]
                cls._instances[key] = provider_class(**kwargs)
                Gimp.message(f"Created new {provider_name} LLM instance")
            except Exception as e:
                Gimp.message(f"Error creating LLM instance: {e}")
                raise
            
        return cls._instances[key]

# Initialize with our providers
def initialize_llm_providers():
    from .perplexity_llm import PerplexityLLM
    from .gemini_llm import GeminiLLM
    
    LLMServiceProvider.register_provider('perplexity', PerplexityLLM)
    LLMServiceProvider.register_provider('gemini', GeminiLLM)
    
    # Mark as initialized
    LLMServiceProvider._initialized = True
    Gimp.message("LLM providers initialized")