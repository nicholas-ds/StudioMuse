from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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

class PhysicalPaletteRequest(BaseModel):
    entry_text: str
    llm_provider: str = "perplexity"
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
    logger.info("=== RECEIVED PALETTE DEMYSTIFY REQUEST ===")
    logger.info(f"GIMP Colors: {len(request.gimp_palette_colors)} colors")
    logger.info(f"Physical Colors: {len(request.physical_palette_data)} colors")
    logger.info(f"LLM Provider: {request.llm_provider}")
    
    try:
        # Get LLM instance
        llm = LLMServiceProvider.get_llm(
            request.llm_provider, 
            temperature=request.temperature
        )
        logger.info(f"Using LLM: {request.llm_provider}")
        
        # Format the prompt
        prompt = palette_dm_prompt.format(
            rgb_colors=json.dumps(request.gimp_palette_colors, indent=2),
            entry_text=json.dumps(request.physical_palette_data, indent=2)
        )
        logger.info("Prompt formatted successfully")
        
        # Call LLM
        logger.info("Calling LLM API...")
        content = llm.call_api(prompt)
        logger.info("LLM API call completed")
        
        return {
            "success": True,
            "response": content,
            "provider": request.llm_provider
        }
        
    except Exception as e:
        logger.error(f"Error in palette demystification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Physical palette creation endpoint
@app.post("/palette/create")
def create_physical_palette(request: PhysicalPaletteRequest):
    """Process a physical palette creation request"""
    logger.info("=== RECEIVED PHYSICAL PALETTE CREATE REQUEST ===")
    logger.info(f"Entry Text: {request.entry_text}")
    logger.info(f"LLM Provider: {request.llm_provider}")
    
    try:
        # Get LLM instance
        llm = LLMServiceProvider.get_llm(
            request.llm_provider, 
            temperature=request.temperature
        )
        logger.info(f"Using LLM: {request.llm_provider}")
        
        # Import the physical palette prompt
        from llm.prompts import add_physical_palette_prompt
        
        # Format the prompt
        prompt = f"{add_physical_palette_prompt}\n\n The user's physical palette is: {request.entry_text}"
        logger.info("Prompt formatted successfully")
        
        # Call LLM
        logger.info("Calling LLM API...")
        content = llm.call_api(prompt)
        logger.info("LLM API call completed")
        
        return {
            "success": True,
            "response": content,
            "provider": request.llm_provider
        }
        
    except Exception as e:
        logger.error(f"Error in physical palette creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Run the server if executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
