import os
import requests
import json
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPIClient:
    """Client for communicating with the StudioMuse backend API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
        logger.info(f"Initialized API client with base URL: {base_url}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the backend API is healthy
        
        Returns:
            Dict containing health status and available LLM providers
        """
        try:
            # Log the attempt
            logger.info(f"Attempting health check to {self.base_url}/health")
            
            # Set a short timeout to fail fast if server is not available
            response = requests.get(f"{self.base_url}/health", timeout=3)
            
            if response.status_code == 200:
                logger.info(f"Health check successful: {response.status_code}")
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # If response is not JSON, create a dict with the text
                    logger.warning(f"Health check response is not JSON: {response.text}")
                    return {"status": "error", "error": f"Invalid JSON response: {response.text}"}
            else:
                logger.error(f"Health check failed with status code: {response.status_code}")
                return {"status": "error", "error": f"API returned status code: {response.status_code}"}
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during health check: {e}")
            return {"status": "error", "error": "Connection refused. Is the backend server running?"}
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during health check: {e}")
            return {"status": "error", "error": "Connection timed out. Backend server may be unresponsive."}
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the backend configuration
        
        Returns:
            Dict containing backend configuration
        """
        try:
            response = requests.get(f"{self.base_url}/config")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            raise Exception(f"Failed to get backend config: {str(e)}")
            
    def demystify_palette(self, gimp_palette_colors, physical_palette_data):
        """
        Send a palette demystification request to the backend
        
        Args:
            gimp_palette_colors: List of GIMP palette colors (Gegl.Color objects)
            physical_palette_data: List of physical palette color names
            
        Returns:
            Dict containing the demystification results
        """
        try:
            # Import the palette processor here to avoid circular imports
            from .palette_processor import PaletteProcessor
            
            # Convert GIMP palette colors to a serializable format
            serializable_colors = {}
            
            # Process list of colors using the palette processor
            for i, color in enumerate(gimp_palette_colors):
                # Use index as name if no name is provided
                name = f"Color {i+1}"
                
                # Convert Gegl.Color to ColorData using the existing utility function
                color_data = PaletteProcessor.convert_gegl_to_color_data(color, name)
                
                # Format for the API payload
                serializable_colors[name] = {
                    "R": color_data.rgb["r"] / 255.0,  # Convert back to 0-1 range
                    "G": color_data.rgb["g"] / 255.0,
                    "B": color_data.rgb["b"] / 255.0,
                    "A": 1.0
                }
            
            # Format the request payload according to the API's expected format
            payload = {
                "gimp_palette_colors": serializable_colors,
                "physical_palette_data": physical_palette_data,
                "llm_provider": "gemini",  # Or get from config
                "temperature": 0.7
            }
            
            logger.info(f"Sending palette demystification request")
            
            response = requests.post(f"{self.base_url}/palette/demystify", json=payload)
            
            if response.status_code != 200:
                logger.error(f"API returned status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return {"success": False, "error": f"API error: {response.text}"}
            
            try:
                # Parse the JSON response
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse API response as JSON: {e}")
                logger.error(f"Raw response: {response.text}")
                return {
                    "success": False, 
                    "error": f"Failed to parse API response as JSON: {str(e)}",
                    "raw_response": response.text
                }
            
        except Exception as e:
            logger.error(f"Palette demystification failed: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
api_client = BackendAPIClient()

def test_demystify_palette():
    """Test the palette demystification API endpoint"""
    client = BackendAPIClient()
    
    # Test data - match the format in test_api.py
    gimp_palette_colors = [
        {"R": 1.0, "G": 0.0, "B": 0.0, "A": 1.0},
        {"R": 0.0, "G": 1.0, "B": 0.0, "A": 1.0},
        {"R": 0.0, "G": 0.0, "B": 1.0, "A": 1.0}
    ]
    
    physical_palette_data = [
        "Crimson Red",
        "Forest Green",
        "Royal Blue"
    ]
    
    # Call the API
    result = client.demystify_palette(
        gimp_palette_colors=gimp_palette_colors,
        physical_palette_data=physical_palette_data
    )
    
    print("API Response:", result)
    return result.get("success", False)

if __name__ == "__main__":
    success = test_demystify_palette()
    print(f"Test {'passed' if success else 'failed'}") 