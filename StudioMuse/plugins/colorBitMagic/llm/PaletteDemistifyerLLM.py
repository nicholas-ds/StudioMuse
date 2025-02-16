from datetime import datetime
from .gemini_llm import GeminiLLM

class PaletteDemistifyerLLM(GeminiLLM):
    def __init__(self):
        super().__init__(temperature=0.7)
        self.analysis_result = {}
        self.created_date = datetime.now().isoformat()

    def call_llm(self, palette_data: dict) -> dict:
        """
        Queries the LLM to analyze the palette comparison data.
        Returns the analysis results as a dictionary.
        """
        try:
            prompt = f"""Analyze these two palettes and their relationships:
            {palette_data}
            
            Provide a detailed analysis in JSON format that includes:
            1. Color matching suggestions between the physical and digital palettes
            2. Notable differences in color distribution
            3. Recommendations for achieving physical colors in GIMP
            4. Overall palette harmony analysis
            """
            
            response = self.call_api(prompt)
            self.analysis_result = response
            return self.analysis_result

        except Exception as e:
            raise Exception(f"Error in palette analysis: {str(e)}")
