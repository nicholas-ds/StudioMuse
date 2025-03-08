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
    
    def demystify_palette(self, 
                          gimp_palette_colors: Dict[str, Dict[str, float]],
                          physical_palette_data: List[str],
                          llm_provider: str = "gemini",
                          temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send a palette demystification request to the backend
        
        Args:
            gimp_palette_colors: Dict of GIMP palette colors
            physical_palette_data: List of physical palette color names
            llm_provider: LLM provider to use
            temperature: Temperature for LLM generation
            
        Returns:
            Dict containing the demystification results
        """
        try:
            payload = {
                "gimp_palette_colors": gimp_palette_colors,
                "physical_palette_data": physical_palette_data,
                "llm_provider": llm_provider,
                "temperature": temperature
            }
            
            logger.info(f"Sending palette demystification request to backend using {llm_provider}")
            
            response = requests.post(
                f"{self.base_url}/palette/demystify",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                logger.info("Palette demystification successful")
                return result
            else:
                logger.error(f"Backend returned error: {result.get('error')}")
                raise Exception(f"Backend API error: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Failed to demystify palette: {e}")
            raise Exception(f"Backend API error: {str(e)}")

# Singleton instance
api_client = BackendAPIClient() 

def test_api_connection():
    """Test connection to the backend API"""
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API connection successful: {data}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False

def test_config_endpoint():
    """Test the config endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/config")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Config endpoint returned: {data}")
            return True
        else:
            print(f"✗ Config endpoint returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("Testing StudioMuse Backend API...")
    test_api_connection()
    test_config_endpoint() 