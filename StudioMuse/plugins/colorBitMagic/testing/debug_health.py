import requests
import json

def debug_health_endpoint():
    """Debug the health endpoint response"""
    print("="*50)
    print("DEBUGGING HEALTH ENDPOINT")
    print("="*50)
    
    try:
        url = "http://127.0.0.1:8000/health"
        print(f"Requesting: {url}")
        
        response = requests.get(url, timeout=3)
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('Content-Type', 'unknown')}")
        
        print("\nRaw response text:")
        print("-"*30)
        print(response.text)
        print("-"*30)
        
        try:
            data = response.json()
            print("\nParsed JSON response:")
            print(json.dumps(data, indent=2))
            
            # Check status field
            if "status" in data:
                print(f"\nStatus field value: '{data['status']}'")
            else:
                print("\nNo 'status' field found in response")
                
        except json.JSONDecodeError as e:
            print(f"\nResponse is not valid JSON: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_health_endpoint() 