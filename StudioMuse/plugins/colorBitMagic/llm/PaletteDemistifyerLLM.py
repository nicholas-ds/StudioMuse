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
        self.temperature = temperature
        
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
        
        # Format the GIMP palette data
        if hasattr(self.gimp_palette, 'colors') and isinstance(self.gimp_palette.colors, list):
            # Extract color information from PaletteData object
            formatted_colors = []
            for color in self.gimp_palette.colors:
                if hasattr(color, 'name') and hasattr(color, 'rgb'):
                    color_info = f"{color.name}: RGB({color.rgb.get('r', 0)}, {color.rgb.get('g', 0)}, {color.rgb.get('b', 0)})"
                    formatted_colors.append(color_info)
            
            rgb_colors_str = "\n".join(formatted_colors)
        else:
            # Fallback to string representation
            rgb_colors_str = str(self.gimp_palette)
        
        # Format the physical palette data
        if isinstance(self.physical_palette, dict) and 'colors' in self.physical_palette:
            # Extract color names from dictionary
            physical_colors_str = "\n".join(self.physical_palette['colors'])
        elif isinstance(self.physical_palette, list):
            # List of color names
            physical_colors_str = "\n".join(self.physical_palette)
        else:
            # Fallback to string representation
            physical_colors_str = str(self.physical_palette)
        
        # Format the prompt
        return palette_dm_prompt.format(
            rgb_colors=rgb_colors_str,
            entry_text=physical_colors_str
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

    def call_llm(self):
        """Call the LLM API and process the response"""
        try:
            # Import at function level to avoid circular imports
            from colorBitMagic_utils import log_error
            from gi.repository import Gimp
            
            # Format the prompt
            prompt = self.format_prompt()
            
            # Log the prompt for debugging
            Gimp.message(f"Sending prompt to LLM (first 100 chars): {prompt[:100]}...")
            
            # For debugging, save the prompt to a file
            import os
            debug_dir = os.path.join(os.path.expanduser("~"), "llm_debug")
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, "llm_prompt.txt")
            with open(debug_file, "w") as f:
                f.write(prompt)
            Gimp.message(f"Saved prompt to {debug_file}")
            
            # Log the palette data for debugging
            Gimp.message(f"GIMP palette data type: {type(self.gimp_palette)}")
            Gimp.message(f"Physical palette data type: {type(self.physical_palette)}")
            
            # Call the LLM API
            if self.llm_provider == "gemini":
                from .gemini_llm import GeminiLLM
                llm = GeminiLLM(temperature=self.temperature)
            else:
                # Default to Gemini
                from .gemini_llm import GeminiLLM
                llm = GeminiLLM(temperature=self.temperature)
            
            # Call the API
            response = llm.call_api(prompt)
            
            # Save the raw response for debugging
            self.raw_response = response
            
            # Log the raw response
            Gimp.message(f"Raw LLM Response (first 100 chars): {response[:100]}...")
            
            # For debugging, save the raw response to a file
            debug_file = os.path.join(debug_dir, "raw_llm_response.txt")
            with open(debug_file, "w") as f:
                f.write(response)
            Gimp.message(f"Saved raw response to {debug_file}")
            
            # Try to parse the response as JSON
            try:
                self.analysis_result = self.clean_and_verify_json(response)
                return self.analysis_result
            except Exception as e:
                log_error("Failed to parse response as JSON", e)
                # Return a simplified result with the raw text
                return {
                    "success": False,
                    "error": f"Failed to parse response as JSON: {str(e)}",
                    "raw_text": response
                }
        except Exception as e:
            Gimp.message(f"Error in palette analysis: {e}")
            raise