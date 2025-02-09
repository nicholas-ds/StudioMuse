from pydantic import BaseModel
import os
import requests
from .prompts import add_physical_palette_prompt
from datetime import datetime

class AnswerFormat(BaseModel):
    colors: list  # Assuming the response will include a list of colors

class LLMPhysicalPalette(BaseModel):
    physical_palette_name: str
    colors_listed: list
    num_colors: int
    created_date: str
    palette_source: str

    def __init__(self, physical_palette_name: str, palette_source: str):
        super().__init__(physical_palette_name=physical_palette_name, colors_listed=[], num_colors=0, created_date=datetime.now().isoformat(), palette_source=palette_source)

    def call_llm(self, entry_text):
        """
        Queries the Perplexity Sonar API to retrieve physical palette colors.
        """
        try:
            url = "https://api.perplexity.ai/chat/completions"

            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": f"{add_physical_palette_prompt}\n\n The user's physical palette is: {entry_text}"
                    }
                ],
                "top_k": 5,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"schema": AnswerFormat.model_json_schema()},
                },
            }

            headers = {
                "Authorization": f"Bearer {os.getenv('PERPLEXITY_KEY')}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Extract colors from the response
            response_data = response.json()
            self.colors_listed = response_data['choices'][0]['message']['content']  # Assuming this is where the colors are
            self.num_colors = len(self.colors_listed)

            return self

        except Exception as e:
            return f"Error sending data to Sonar: {type(e).__name__}: {e}"

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