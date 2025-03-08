# Test script for the API endpoints
import requests
import json
import sys

def test_health():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        response.raise_for_status()
        data = response.json()
        
        print("✅ Health check successful")
        print(f"Status: {data.get('status')}")
        print(f"Available LLM providers: {data.get('llm_providers')}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_config():
    """Test the config endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/config")
        response.raise_for_status()
        data = response.json()
        
        print("\n✅ Config check successful")
        print(f"API config: {data.get('api')}")
        print(f"LLM config: {data.get('llm')}")
        return True
    except Exception as e:
        print(f"❌ Config check failed: {e}")
        return False

def test_palette_demystify():
    """Test the palette demystification endpoint with a simple example"""
    try:
        # Simple test data
        test_data = {
            "gimp_palette_colors": {
                "color1": {"R": 1.0, "G": 0.0, "B": 0.0, "A": 1.0},
                "color2": {"R": 0.0, "G": 1.0, "B": 0.0, "A": 1.0},
                "color3": {"R": 0.0, "G": 0.0, "B": 1.0, "A": 1.0}
            },
            "physical_palette_data": [
                "Crimson Red",
                "Forest Green",
                "Royal Blue"
            ],
            "llm_provider": "test-provider",  # Use test provider for initial testing
            "temperature": 0.2
        }
        
        print("\n🔄 Testing palette demystification...")
        print(f"Using provider: {test_data['llm_provider']}")
        
        response = requests.post(
            "http://127.0.0.1:8000/palette/demystify",
            json=test_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                print("✅ Palette demystification successful")
                print(f"Provider used: {data.get('provider')}")
                print("Results:")
                print(json.dumps(data.get("result"), indent=2))
                return True
            else:
                print(f"❌ API returned error: {data.get('error')}")
                print(f"Raw response: {data.get('raw_response')}")
                return False
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Palette demystification test failed: {e}")
        return False

def run_tests():
    """Run all API tests"""
    print("="*50)
    print("TESTING STUDIOMUSE BACKEND API")
    print("="*50)
    
    # Run tests
    health_result = test_health()
    config_result = test_config()
    
    # Only test palette demystification if health and config checks pass
    if health_result and config_result:
        palette_result = test_palette_demystify()
    else:
        palette_result = False
        print("\n⚠️ Skipping palette demystification test due to failed prerequisites")
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"{'✅' if health_result else '❌'} Health Check")
    print(f"{'✅' if config_result else '❌'} Config Check")
    print(f"{'✅' if palette_result else '❌'} Palette Demystification")
    
    # Overall result
    all_passed = health_result and config_result and palette_result
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All API tests passed successfully!")
    else:
        print("⚠️ Some API tests failed. See details above.")
    print("="*50)
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 