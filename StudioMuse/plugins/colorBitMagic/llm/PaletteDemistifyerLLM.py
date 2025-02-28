from datetime import datetime
import json
from gi.repository import Gimp

class PaletteDemistifyerLLM:
    def __init__(self, gimp_palette_colors: dict, physical_palette_data: dict,
                 llm_provider: str = "gemini", temperature: float = 0.7):
        """
        Initialize the palette demystifier that compares GIMP palettes to physical palettes.
        
        Args:
            gimp_palette_colors: Dictionary of GIMP palette colors
            physical_palette_data: Dictionary of physical palette data
            llm_provider: The LLM provider to use (default: "gemini")
            temperature: LLM temperature parameter
        """
        # Import here to avoid circular imports
        from .llm_service_provider import LLMServiceProvider, initialize_llm_providers
        
        # Ensure LLM providers are initialized
        if not LLMServiceProvider._initialized:
            Gimp.message("Initializing LLM providers from PaletteDemistifyerLLM")
            initialize_llm_providers()
        
        # Get the LLM instance from the service provider
        self.llm = LLMServiceProvider.get_llm(
            llm_provider,
            temperature=temperature
        )
        
        # Store the LLM provider for reference
        self.llm_provider = llm_provider
        
        # Store the palette data
        self.analysis_result = {}
        self.created_date = datetime.now().isoformat()
        self.raw_response = {}
        self.gimp_palette = gimp_palette_colors
        self.physical_palette = physical_palette_data

    def format_prompt(self) -> str:
        """Formats the prompt template with the palette data"""
        from .prompts import palette_dm_prompt
        return palette_dm_prompt.format(
            rgb_colors=self.gimp_palette,
            entry_text=self.physical_palette
        )

    def clean_and_verify_json(self, response: str) -> dict:
        """Cleans and verifies the JSON response from the LLM"""
        try:
            import json
            # Clean the response
            cleaned = (response
                .replace('```json\n', '')
                .replace('```', '')
                .strip())
            
            # Try to parse JSON
            return json.loads(cleaned)
        except json.JSONDecodeError as je:
            Gimp.message(f"JSON error: {str(je)}")
            raise Exception("Failed to parse LLM response as JSON")

    def call_llm(self) -> dict:
        """Queries the LLM to analyze the palette comparison data"""
        try:
            # Get the formatted prompt
            prompt = self.format_prompt()
            
            # Call the API using the LLM instance
            response = self.llm.call_api(prompt)
            
            # Process the response based on LLM provider
            # For gemini, the response is already the text content
            if self.llm_provider != "gemini":
                # For other providers like Perplexity, extract the text content
                # This would need to be adjusted based on the actual provider's response format
                if isinstance(response, dict) and "choices" in response:
                    response = response['choices'][0]['message']['content']
            
            # Clean and verify the response
            self.analysis_result = self.clean_and_verify_json(response)
            return self.analysis_result

        except Exception as e:
            Gimp.message(f"Error in palette analysis: {str(e)}")
            raise Exception(f"Error in palette analysis: {str(e)}")