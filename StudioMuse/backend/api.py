from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="StudioMuse Backend API")

# Import LLM service provider
from llm.llm_service_provider import LLMServiceProvider
from llm.base_llm import BaseLLM
from llm.perplexity_llm import PerplexityLLM
from llm.gemini_llm import GeminiLLM

# Register providers
LLMServiceProvider.register_provider("test-provider", BaseLLM)
LLMServiceProvider.register_provider("perplexity", PerplexityLLM)
LLMServiceProvider.register_provider("gemini", GeminiLLM)

# Health check endpoint
@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "llm_providers": list(LLMServiceProvider._providers.keys())}

# Configuration endpoint
@app.get("/config")
def get_config():
    """Return the current configuration (excluding sensitive data)"""
    # Create a sanitized version of the config
    safe_config = {
        "api": {
            "host": "127.0.0.1",
            "port": 8000
        },
        "llm": {
            "default_provider": "test-provider",
            "temperature": 0.5
        }
    }
    return safe_config

# Run the server if executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
