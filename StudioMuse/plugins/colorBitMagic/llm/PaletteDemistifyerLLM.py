from datetime import datetime
from .gemini_llm import GeminiLLM
from .prompts import palette_dm_prompt

class PaletteDemistifyerLLM(GeminiLLM):
    def __init__(self, gimp_palette_colors: dict, physical_palette_data: dict):
        super().__init__(temperature=0.7)
        self.analysis_result = {}
        self.created_date = datetime.now().isoformat()
        self.raw_response = {}
        self.gimp_palette = gimp_palette_colors
        self.physical_palette = physical_palette_data

    def format_prompt(self) -> str:
        """
        Formats the prompt template with the palette data
        """
        return palette_dm_prompt.format(
            rgb_colors=self.gimp_palette,
            entry_text=self.physical_palette
        )

    def clean_and_verify_json(self, response: str) -> dict:
        """
        Cleans and verifies the JSON response from the LLM.
        Args:
            response: Raw response string from LLM
        Returns:
            Parsed JSON dictionary
        Raises:
            Exception: If JSON is invalid
        """
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
            print("=== JSON Cleaning Debug ===")
            print("Raw response:", repr(response))
            print("Cleaned response:", repr(cleaned))
            print("JSON error:", str(je))
            raise Exception("Failed to parse LLM response as JSON")

    def call_llm(self, palette_data: dict = None) -> dict:
        """
        Queries the LLM to analyze the palette comparison data.
        Returns the analysis results as a dictionary.
        """
        try:
            # Get the formatted prompt
            prompt = self.format_prompt()
            
            # Call the API with the formatted prompt
            response = self.call_api(prompt)
            
            # Clean and verify the response
            self.analysis_result = self.clean_and_verify_json(response)
            return self.analysis_result

        except Exception as e:
            raise Exception(f"Error in palette analysis: {str(e)}")
