import os
from google import genai
from typing import Dict, Any

class GeminiLLM:
    def __init__(self, temperature: float = 0.7):
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY environment variable is not set")
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)
        self.temperature = temperature

    def call_api(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            raise Exception(f"Error calling Gemini API: {type(e).__name__}: {e}")

# Test entry point
if __name__ == "__main__":
    try:
        # Create instance
        llm = GeminiLLM()
        
        # Test simple prompt
        test_prompt = "What is the meaning of life in 10 words or less?"
        print(f"\nTesting with prompt: {test_prompt}")
        
        result = llm.call_api(test_prompt)
        print(f"\nResult: {result}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
