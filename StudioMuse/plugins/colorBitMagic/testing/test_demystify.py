import sys
import os
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the API client
from utils.api_client import BackendAPIClient

def test_demystify():
    """Test the demystify_palette method"""
    print("="*50)
    print("TESTING DEMYSTIFY_PALETTE METHOD")
    print("="*50)
    
    # Create API client
    client = BackendAPIClient()
    
    # Create test data
    gimp_palette_colors = {
        "Red": {"R": 1.0, "G": 0.0, "B": 0.0, "A": 1.0},
        "Green": {"R": 0.0, "G": 1.0, "B": 0.0, "A": 1.0},
        "Blue": {"R": 0.0, "G": 0.0, "B": 1.0, "A": 1.0}
    }
    
    physical_palette_data = [
        "Crimson Red",
        "Forest Green",
        "Royal Blue",
        "Sunny Yellow",
        "Pure White"
    ]
    
    try:
        print("\nTesting demystify_palette method...")
        response = client.demystify_palette(
            gimp_palette_colors=gimp_palette_colors,
            physical_palette_data=physical_palette_data
        )
        
        print(f"Response type: {type(response).__name__}")
        
        if isinstance(response, dict):
            print(f"Success: {response.get('success', False)}")
            
            if response.get("success"):
                result = response.get("result")
                print(f"Number of matches: {len(result)}")
                print("\nSample results:")
                print(json.dumps(result[:2], indent=2))
            else:
                print(f"Error: {response.get('error', 'Unknown error')}")
        else:
            print(f"Unexpected response type: {type(response).__name__}")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_demystify() 