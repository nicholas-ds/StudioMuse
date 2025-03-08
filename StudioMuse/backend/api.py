from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="StudioMuse Backend API")

# Import LLM service provider and providers
from llm.llm_service_provider import LLMServiceProvider
from llm.base_llm import BaseLLM
from llm.perplexity_llm import PerplexityLLM
from llm.gemini_llm import GeminiLLM
from llm.prompts import palette_dm_prompt

# Register providers
LLMServiceProvider.register_provider("test-provider", BaseLLM)
LLMServiceProvider.register_provider("perplexity", PerplexityLLM)
LLMServiceProvider.register_provider("gemini", GeminiLLM)

# Models for API requests
class PaletteDemystifyRequest(BaseModel):
    gimp_palette_colors: Dict[str, Dict[str, float]]
    physical_palette_data: List[str]
    llm_provider: str = "gemini"
    temperature: float = 0.7

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
            "providers": list(LLMServiceProvider._providers.keys()),
            "default_provider": "gemini",
            "temperature": 0.7
        }
    }
    return safe_config

# Palette demystifier endpoint
@app.post("/palette/demystify")
def palette_demystify(request: PaletteDemystifyRequest):
    """Process a palette demystification request"""
    try:
        logger.info(f"Received palette demystification request using provider: {request.llm_provider}")
        
        # Special handling for test-provider
        if request.llm_provider == "test-provider":
            llm = LLMServiceProvider.get_llm(
                request.llm_provider,
                model="test-model",
                api_url="https://example.com/api",
                temperature=request.temperature
            )
        else:
            # For other providers
            llm = LLMServiceProvider.get_llm(
                request.llm_provider,
                temperature=request.temperature
            )
        
        # Format the prompt with the palette data
        prompt = palette_dm_prompt.format(
            rgb_colors=json.dumps(request.gimp_palette_colors, indent=2),
            entry_text=json.dumps(request.physical_palette_data, indent=2)
        )
        
        # Call the LLM API
        response = llm.call_api(prompt)
        
        # Process the response based on LLM provider
        if isinstance(response, str):
            # For Gemini
            content = response
        else:
            # For other providers like Perplexity
            content = response['choices'][0]['message']['content']
        
        # Clean and parse JSON
        cleaned = (content
            .replace('```json\n', '')
            .replace('```', '')
            .strip())
        
        try:
            result = json.loads(cleaned)
            
            return {
                "success": True,
                "result": result,
                "provider": request.llm_provider
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {
                "success": False,
                "error": "Failed to parse LLM response as JSON",
                "raw_response": content
            }
        
    except Exception as e:
        logger.error(f"Error in palette demystification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Run the server if executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
