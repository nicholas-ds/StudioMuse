from datetime import datetime
import json
from gi.repository import Gimp

class PaletteDemistifyerLLM:
    def __init__(self, gimp_palette_colors: dict, physical_palette_data: dict):
        # Import here to avoid circular imports
        from .gemini_llm import GeminiLLM
        
        # Create the LLM instance (composition instead of inheritance)
        self.llm = GeminiLLM(temperature=0.7)
        
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
            
            # Clean and verify the response
            self.analysis_result = self.clean_and_verify_json(response)
            return self.analysis_result

        except Exception as e:
            Gimp.message(f"Error in palette analysis: {str(e)}")
            raise Exception(f"Error in palette analysis: {str(e)}")