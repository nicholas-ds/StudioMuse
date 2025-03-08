from fastapi import FastAPI, HTTPException
import uvicorn
from config import config

app = FastAPI(title="StudioMuse Backend API")

@app.get("/")
def read_root():
    """Simple health check endpoint"""
    return {"status": "StudioMuse Backend API is running"}

@app.get("/config")
def get_config():
    """Return the current configuration (excluding sensitive data)"""
    # Create a sanitized version of the config (no API keys)
    safe_config = {
        "api": {
            "host": config.get("api.host"),
            "port": config.get("api.port")
        },
        "llm": {
            "default_provider": config.get("llm.default_provider"),
            "temperature": config.get("llm.temperature")
        }
    }
    return safe_config

if __name__ == "__main__":
    host = config.get("api.host")
    port = config.get("api.port")
    uvicorn.run("api:app", host=host, port=port, reload=True)
