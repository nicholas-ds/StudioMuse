from pydantic import BaseModel
from datetime import datetime
from .prompts import add_physical_palette_prompt
from colorBitMagic_utils import clean_and_verify_json

class AnswerFormat(BaseModel):
    colors: list

class LLMPhysicalPalette:
    def __init__(self, physical_palette_name: str = "Default Palette Name", 
                 palette_source: str = "unknown",
                 llm_provider: str = "perplexity",
                 temperature: float = 0.0,
                 top_k: int = 10):
        """
        Initialize a physical palette instance that uses LLM to analyze color data.
        
        Args:
            physical_palette_name: Name of the palette
            palette_source: Source of the palette data (e.g., "user", "perplexity")
            llm_provider: Name of the LLM provider to use ("perplexity", "gemini")
            temperature: LLM temperature parameter
            top_k: LLM top_k parameter (for providers that support it)
        """
        # Import locally to avoid circular imports
        from .llm_service_provider import LLMServiceProvider
        
        # Get LLM instance from service provider
        self.llm = LLMServiceProvider.get_llm(
            llm_provider, 
            temperature=temperature,
            top_k=top_k
        )
        
        # Initialize properties
        self.physical_palette_name = physical_palette_name
        self.colors_listed = []
        self.num_colors = 0
        self.llm_num_colors = 0
        self.created_date = datetime.now().isoformat()
        self.palette_source = palette_source
        self.additional_notes = ""
        self.raw_response = {}
        
        # Store the provider for reference
        self.llm_provider = llm_provider

    def call_llm(self, entry_text):
        """
        Queries the LLM to retrieve physical palette colors.
        """
        try:
            # Format the prompt
            prompt = f"{add_physical_palette_prompt}\n\n The user's physical palette is: {entry_text}"
            
            # Call the API using the LLM instance
            response_data = self.llm.call_api(prompt)
            self.raw_response = response_data

            # Process the response based on LLM provider
            if self.llm_provider == "perplexity":
                content = response_data['choices'][0]['message']['content']
            else:  # Handle Gemini or other providers
                content = response_data
                
            # Clean and verify JSON from the content
            color_json = clean_and_verify_json(content)
            
            # Update instance properties
            self.colors_listed = color_json['colors']
            self.llm_num_colors = color_json['piece_count']
            self.num_colors = len(self.colors_listed)
            self.physical_palette_name = color_json['set_name']
            self.additional_notes = color_json['additional_notes']
            self.palette_source = self.llm_provider
            self.created_date = datetime.now().isoformat()

            return self

        except Exception as e:
            return f"Error processing LLM response: {type(e).__name__}: {e}"