# Simple test script to verify the BaseLLM class works
from llm.base_llm import BaseLLM
from llm.llm_service_provider import LLMServiceProvider

# Create a test instance
test_llm = BaseLLM(
    model="test-model",
    api_url="https://example.com/api",
    temperature=0.5
)

# Print the instance to verify
print(f"Created LLM instance: {test_llm}")
print(f"Model: {test_llm.model}")
print(f"Temperature: {test_llm.temperature}") 

# Register the BaseLLM as a test provider
LLMServiceProvider.register_provider("test-provider", BaseLLM)

# Get an instance through the service provider
provider_llm = LLMServiceProvider.get_llm(
    "test-provider", 
    model="provider-model",
    api_url="https://provider-example.com/api",
    temperature=0.7
)

print(f"\nCreated provider LLM instance: {provider_llm}")
print(f"Provider Model: {provider_llm.model}")
print(f"Provider Temperature: {provider_llm.temperature}") 