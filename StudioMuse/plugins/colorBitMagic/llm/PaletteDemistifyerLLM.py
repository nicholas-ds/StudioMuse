from datetime import datetime
import json
from gi.repository import Gimp
from colorBitMagic_utils import clean_and_verify_json

class PaletteDemistifyerLLM:
    def __init__(self, gimp_palette_colors=None, physical_palette_data=None,
                 gimp_palette_name=None, physical_palette_name=None,
                 llm_provider="gemini", temperature=0.7):
        """
        Initialize the palette demystifier that compares GIMP palettes to physical palettes.
        
        Supports both old and new parameter formats:
        - Old: gimp_palette_colors (dict), physical_palette_data (dict)
        - New: gimp_palette_name (str), physical_palette_name (str)
        
        Args:
            gimp_palette_colors: Dictionary of GIMP palette colors (legacy)
            physical_palette_data: Dictionary of physical palette data (legacy)
            gimp_palette_name: Name of the GIMP palette (new)
            physical_palette_name: Name of the physical palette (new)
            llm_provider: The LLM provider to use (default: "gemini")
            temperature: LLM temperature parameter
        """
        # Import here to avoid circular imports
        from .llm_service_provider import LLMServiceProvider
        
        # Get the LLM instance from the service provider
        self.llm = LLMServiceProvider.get_llm(
            llm_provider,
            temperature=temperature
        )
        
        # Store parameters
        self.llm_provider = llm_provider
        
        # Handle different parameter formats
        if gimp_palette_name and physical_palette_name:
            # New style - load from names
            from colorBitMagic_utils import gimp_palette_to_palette_data, load_physical_palette_data
            self.gimp_palette_name = gimp_palette_name
            self.physical_palette_name = physical_palette_name
            self.gimp_palette = gimp_palette_to_palette_data(gimp_palette_name)
            self.physical_palette = load_physical_palette_data(physical_palette_name)
        else:
            # Legacy style - use provided data directly
            self.gimp_palette_name = None
            self.physical_palette_name = None
            self.gimp_palette = gimp_palette_colors
            self.physical_palette = physical_palette_data
        
        # Analysis results
        self.analysis_result = {}
        self.created_date = datetime.now().isoformat()
        self.raw_response = {}

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
            self.raw_response = response
            
            # For Gemini, the response is already the text content
            if isinstance(response, str):
                content = response
            else:
                # For other providers like Perplexity, extract the text content
                content = response['choices'][0]['message']['content']
            
            # Clean and verify the response
            self.analysis_result = self.clean_and_verify_json(content)
            return self.analysis_result

        except Exception as e:
            Gimp.message(f"Error in palette analysis: {str(e)}")
            raise Exception(f"Error in palette analysis: {str(e)}")