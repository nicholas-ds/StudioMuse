import os
import json
import logging
from typing import Dict, Any, List, Optional
import sys
from urllib import request, error
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPIClient:
    """Client for communicating with the StudioMuse backend API"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        logger.info(f"Initialized API client with base URL: {base_url}")

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request using urllib"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if data is not None:
                data = json.dumps(data).encode('utf-8')
            
            req = request.Request(
                url,
                data=data,
                headers=headers,
                method=method
            )
            
            with request.urlopen(req, timeout=timeout) as response:
                response_data = response.read().decode('utf-8')
                return {"success": True, "response": json.loads(response_data)}
                
        except error.HTTPError as e:
            logger.error(f"HTTP error: {e.code} - {e.reason}")
            return {"success": False, "error": f"API error: {e.reason}"}
        except error.URLError as e:
            logger.error(f"URL error: {e.reason}")
            return {"success": False, "error": f"Connection error: {e.reason}"}
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        return self._make_request("health", timeout=3)

    def get_config(self) -> Dict[str, Any]:
        try:
            result = self._make_request("config")
            if result["success"]:
                return result["response"]
            raise Exception(result["error"])
        except Exception as e:
            raise Exception(f"Failed to get backend config: {str(e)}")

    def demystify_palette(self, gimp_palette_colors, physical_palette_data):
        try:
            from core.models.palette_processor import PaletteProcessor

            # Convert GIMP palette colors to a serializable format
            serializable_colors = {}
            for i, color in enumerate(gimp_palette_colors):
                name = f"Color {i+1}"
                color_data = PaletteProcessor.convert_gegl_to_color_data(color, name)
                serializable_colors[name] = {
                    "R": color_data.rgb["r"],
                    "G": color_data.rgb["g"],
                    "B": color_data.rgb["b"],
                    "A": 1.0
                }

            payload = {
                "gimp_palette_colors": serializable_colors,
                "physical_palette_data": physical_palette_data,
                "llm_provider": "gemini",
                "temperature": 0.7
            }

            logger.info("Sending palette demystification request")
            api_result = self._make_request("palette/demystify", method="POST", data=payload)
            
            # Return in the original format expected by the rest of the code
            if api_result["success"]:
                return api_result["response"]
            else:
                return {"success": False, "error": api_result["error"]}

        except Exception as e:
            logger.error(f"Palette demystification error: {e}")
            return {"success": False, "error": str(e)}

    def create_physical_palette(self, entry_text: str, llm_provider: str = "perplexity", temperature: float = 0.7):
        try:
            payload = {
                "entry_text": entry_text,
                "llm_provider": llm_provider,
                "temperature": temperature
            }

            logger.info(f"Sending request to: {self.base_url}/palette/create")
            logger.info(f"Payload:\n{json.dumps(payload, indent=2)}")

            result = self._make_request("palette/create", method="POST", data=payload)
            logger.info(f"API Response: {result}")
            return result

        except Exception as e:
            logger.error(f"Exception during API call: {e}")
            return {"success": False, "error": str(e)}

