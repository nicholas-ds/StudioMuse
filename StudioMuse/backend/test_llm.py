# Simple test script to verify the LLM functionality
from llm.base_llm import BaseLLM
from llm.llm_service_provider import LLMServiceProvider
import json
import os

def run_tests():
    """Run a series of tests to verify LLM functionality"""
    test_results = {
        "base_llm_creation": False,
        "service_provider_registration": False,
        "service_provider_get_llm": False,
        "prompts_import": False,
        "perplexity_llm_import": False,
        "gemini_llm_import": False
    }
    
    # Test 1: Create a BaseLLM instance
    try:
        test_llm = BaseLLM(
            model="test-model",
            api_url="https://example.com/api",
            temperature=0.5
        )
        print(f"✅ Created LLM instance: {test_llm}")
        print(f"Model: {test_llm.model}")
        print(f"Temperature: {test_llm.temperature}")
        test_results["base_llm_creation"] = True
    except Exception as e:
        print(f"❌ Failed to create BaseLLM instance: {e}")
    
    # Test 2: Register a provider with the service provider
    try:
        LLMServiceProvider.register_provider("test-provider", BaseLLM)
        print(f"✅ Registered BaseLLM as 'test-provider'")
        test_results["service_provider_registration"] = True
    except Exception as e:
        print(f"❌ Failed to register provider: {e}")
    
    # Test 3: Get an LLM instance through the service provider
    try:
        provider_llm = LLMServiceProvider.get_llm(
            "test-provider", 
            model="provider-model",
            api_url="https://provider-example.com/api",
            temperature=0.7
        )
        print(f"\n✅ Created provider LLM instance: {provider_llm}")
        print(f"Provider Model: {provider_llm.model}")
        print(f"Provider Temperature: {provider_llm.temperature}")
        test_results["service_provider_get_llm"] = True
    except Exception as e:
        print(f"❌ Failed to get LLM from service provider: {e}")
    
    # Test 4: Import prompts (if available)
    try:
        from llm.prompts import palette_dm_prompt, add_physical_palette_prompt
        print(f"\n✅ Successfully imported prompts")
        print(f"Palette prompt length: {len(palette_dm_prompt)} characters")
        print(f"Add palette prompt length: {len(add_physical_palette_prompt)} characters")
        test_results["prompts_import"] = True
    except ImportError:
        print(f"❌ Prompts module not found or incomplete")
    except Exception as e:
        print(f"❌ Error importing prompts: {e}")
    
    # Test 5: Import and create Perplexity LLM
    try:
        from llm.perplexity_llm import PerplexityLLM
        
        # Only create instance if API key is available (for CI/CD environments)
        if os.getenv('PERPLEXITY_KEY'):
            perplexity = PerplexityLLM(temperature=0.2)
            print(f"\n✅ Created Perplexity LLM instance: {perplexity}")
            print(f"Perplexity Model: {perplexity.model}")
            
            # Test payload preparation
            test_prompt = "Test prompt"
            payload = perplexity.prepare_payload(test_prompt)
            print(f"Payload contains top_k: {payload.get('top_k') is not None}")
        else:
            print(f"\n⚠️ Skipped Perplexity LLM creation (no API key)")
            
        test_results["perplexity_llm_import"] = True
    except ImportError:
        print(f"❌ PerplexityLLM module not found")
    except Exception as e:
        print(f"❌ Error with PerplexityLLM: {e}")
    
    # Test 6: Import and create Gemini LLM
    try:
        from llm.gemini_llm import GeminiLLM
        
        # Only create instance if API key is available
        if os.getenv('GEMINI_API_KEY'):
            gemini = GeminiLLM(temperature=0.2)
            print(f"\n✅ Created Gemini LLM instance: {gemini}")
            print(f"Gemini Model: {gemini.model}")
            
            # We don't test call_api here as it would make an actual API call
            print(f"Gemini API key is set: {bool(gemini.api_key)}")
        else:
            print(f"\n⚠️ Skipped Gemini LLM creation (no API key)")
            
        test_results["gemini_llm_import"] = True
    except ImportError:
        print(f"❌ GeminiLLM module not found")
    except Exception as e:
        print(f"❌ Error with GeminiLLM: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Overall result
    all_passed = all(test_results.values())
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️ Some tests failed. See details above.")
    print("="*50)
    
    return all_passed

def test_live_llm_responses():
    """Test that we can get actual responses from LLMs."""
    print("\n==== Testing Live LLM Responses ====")
    
    # Test Perplexity if API key is available
    if os.getenv('PERPLEXITY_KEY'):
        print("\nTesting Perplexity:")
        try:
            perplexity = LLMServiceProvider.get_llm("perplexity", temperature=0.3)
            response = perplexity.call_api("Respond with one sentence: What is the capital of France?")
            print(f"Perplexity response: {response.strip()}")
            assert len(response) > 5, "Response should not be empty or very short"
            print("✅ Perplexity test passed")
        except Exception as e:
            print(f"❌ Perplexity test failed: {e}")
    else:
        print("⚠️ Skipping Perplexity test (no API key)")
    
    # Test Gemini if API key is available
    if os.getenv('GEMINI_API_KEY'):
        print("\nTesting Gemini:")
        try:
            gemini = LLMServiceProvider.get_llm("gemini", temperature=0.3)
            response = gemini.call_api("Respond with one sentence: What is the capital of France?")
            print(f"Gemini response: {response.strip()}")
            assert len(response) > 5, "Response should not be empty or very short"
            print("✅ Gemini test passed")
        except Exception as e:
            print(f"❌ Gemini test failed: {e}")
    else:
        print("⚠️ Skipping Gemini test (no API key)")

if __name__ == "__main__":
    run_tests()
    test_live_llm_responses() 