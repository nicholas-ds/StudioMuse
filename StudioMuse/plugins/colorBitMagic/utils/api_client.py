import os
import requests
from typing import Dict, Any, Optional

class APIClient:
    """
    Client for communicating with the StudioMuse backend API.
    Uses environment variables for configuration with defaults.
    """
    
    def __init__(self):
        self.base_url = os.environ.get("STUDIOMUSE_API_URL", "http://127.0.0.1:8000")
        self.timeout = int(os.environ.get("STUDIOMUSE_API_TIMEOUT", "10"))
    
    def get(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a GET request to the API
        
        Args:
            endpoint: API endpoint (without leading slash)
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API
        
        Args:
            endpoint: API endpoint (without leading slash)
            data: JSON data to send
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

# Singleton instance
api_client = APIClient() 

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