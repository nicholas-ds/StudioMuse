from typing import Dict, Type, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMServiceProvider:
    """Factory class for LLM service instances."""
    
    _instances = {}
    _providers = {}
    _initialized = False
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type):
        """Register a new LLM provider."""
        cls._providers[name] = provider_class
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def get_llm(cls, provider_name: str, **kwargs) -> Any:
        """Get an instance of the specified LLM provider."""
        # Ensure providers are initialized
        if not cls._initialized:
            cls._initialize_providers()
            
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
                logger.info(f"Created new {provider_name} LLM instance")
            except Exception as e:
                logger.error(f"Error creating LLM instance: {e}")
                raise
            
        return cls._instances[key]
    
    @classmethod
    def _initialize_providers(cls):
        """Initialize the available LLM providers."""
        # This will be implemented later when we add specific providers
        cls._initialized = True
        logger.info("LLM providers initialized (placeholder)") 