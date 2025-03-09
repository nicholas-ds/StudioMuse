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
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise Exception(f"Backend API health check failed: {str(e)}")
    
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
            gimp_palette_colors: Dictionary of GIMP palette colors
            physical_palette_data: List of physical palette color names
            
        Returns:
            Dict containing the demystification results
        """
        try:
            # Format the request payload according to the API's expected format
            # Based on test_api.py format
            payload = {
                "gimp_palette_colors": gimp_palette_colors,
                "physical_palette_data": physical_palette_data,
                "llm_provider": "gemini",  # Or get from config
                "temperature": 0.7
            }
            
            logger.info(f"Sending palette demystification request")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(f"{self.base_url}/palette/demystify", json=payload)
            
            if response.status_code != 200:
                logger.error(f"API returned status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return {"success": False, "error": f"API error: {response.text}"}
                
            return response.json()
        except Exception as e:
            logger.error(f"Palette demystification failed: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
api_client = BackendAPIClient()

def test_demystify_palette():
    """Test the palette demystification API endpoint"""
    client = BackendAPIClient()
    
    # Test data - match the format in test_api.py
    gimp_palette_colors = {
        "color1": {"R": 1.0, "G": 0.0, "B": 0.0, "A": 1.0},
        "color2": {"R": 0.0, "G": 1.0, "B": 0.0, "A": 1.0},
        "color3": {"R": 0.0, "G": 0.0, "B": 1.0, "A": 1.0}
    }
    
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