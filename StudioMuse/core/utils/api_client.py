import os
import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPIClient:
    """Client for communicating with the StudioMuse backend API"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        logger.info(f"Initialized API client with base URL: {base_url}")

    def health_check(self) -> Dict[str, Any]:
        try:
            import requests
            logger.info(f"Attempting health check to {self.base_url}/health")
            response = requests.get(f"{self.base_url}/health", timeout=3)
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "error", "error": f"Invalid JSON response: {response.text}"}
            else:
                return {"status": "error", "error": f"API returned status code: {response.status_code}"}
        except ImportError:
            return {"status": "error", "error": "'requests' module is missing in this GIMP environment."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_config(self) -> Dict[str, Any]:
        try:
            import requests
            response = requests.get(f"{self.base_url}/config")
            response.raise_for_status()
            return response.json()
        except ImportError:
            raise Exception("'requests' module is missing in this GIMP environment.")
        except Exception as e:
            raise Exception(f"Failed to get backend config: {str(e)}")

    def demystify_palette(self, gimp_palette_colors, physical_palette_data):
        try:
            import requests
            from core.models.palette_processor import PaletteProcessor

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
            response = requests.post(f"{self.base_url}/palette/demystify", json=payload)

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.text}"}

            try:
                return response.json()
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse API response as JSON: {str(e)}",
                    "raw_response": response.text
                }

        except ImportError:
            return {"success": False, "error": "'requests' module is not available in this GIMP environment."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_physical_palette(self, entry_text: str, llm_provider: str = "perplexity", temperature: float = 0.7):
        try:
            import requests
        except ImportError:
            return {"success": False, "error": "'requests' module is not available in this GIMP environment."}

        try:
            payload = {
                "entry_text": entry_text,
                "llm_provider": llm_provider,
                "temperature": temperature
            }

            logger.info(f"Sending request to: {self.base_url}/palette/create")
            logger.info(f"Payload:\n{json.dumps(payload, indent=2)}")

            response = requests.post(f"{self.base_url}/palette/create", json=payload)

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.text}"}

            try:
                return response.json()
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse API response as JSON: {str(e)}",
                    "raw_response": response.text
                }

        except Exception as e:
            logger.error(f"Exception during API call: {e}")
            return {"success": False, "error": str(e)}

