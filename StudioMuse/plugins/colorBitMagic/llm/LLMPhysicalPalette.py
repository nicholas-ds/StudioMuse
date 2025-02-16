from pydantic import BaseModel
from datetime import datetime
from .perplexity_llm import PerplexityLLM
from .prompts import add_physical_palette_prompt
from colorBitMagic_utils import clean_and_verify_json

class AnswerFormat(BaseModel):
    colors: list

class LLMPhysicalPalette(PerplexityLLM):
    physical_palette_name: str = "Default Palette Name"
    colors_listed: list = []
    num_colors: int = 0
    llm_num_colors: int = 0
    created_date: str = datetime.now().isoformat()
    palette_source: str = "unknown"
    additional_notes: str = ""
    raw_response: dict = {}

    def __init__(self, physical_palette_name: str = "Default Palette Name", palette_source: str = "unknown"):
        super().__init__()
        self.physical_palette_name = physical_palette_name
        self.colors_listed = []
        self.num_colors = 0
        self.created_date = datetime.now().isoformat()
        self.palette_source = palette_source
        self.raw_response = {}

    def call_llm(self, entry_text):
        """
        Queries the LLM to retrieve physical palette colors.
        """
        try:
            prompt = f"{add_physical_palette_prompt}\n\n The user's physical palette is: {entry_text}"
            response_data = self.call_api(prompt)
            self.raw_response = response_data

            color_json = clean_and_verify_json(response_data['choices'][0]['message']['content'])
            self.colors_listed = color_json['colors']
            self.llm_num_colors = color_json['piece_count']
            self.num_colors = len(self.colors_listed)
            self.physical_palette_name = color_json['set_name']
            self.additional_notes = color_json['additional_notes']
            self.palette_source = "Perplexity"
            self.created_date = datetime.now().isoformat()

            return self

        except Exception as e:
            return f"Error processing LLM response: {type(e).__name__}: {e}"

# Example usage
def main():
    # Example entry text and palette name
    entry_text = "Example palette entry text"
    palette_name = "My Physical Palette"

    llm_palette = LLMPhysicalPalette(physical_palette_name=palette_name, palette_source="user")
    result = llm_palette.call_llm(entry_text)

    if isinstance(result, LLMPhysicalPalette):
        print("Palette Name:", result.physical_palette_name)
        print("Colors Listed:", result.colors_listed)
        print("Number of Colors:", result.num_colors)
        print("Created Date:", result.created_date)
        print("Palette Source:", result.palette_source)
    else:
        print(result)

if __name__ == "__main__":
    main()