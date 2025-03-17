import gi
from gi.repository import Gimp
import json
from .base_dialog import BaseDialog
from colorBitMagic_utils import (
    populate_palette_dropdown, 
    populate_physical_palette_dropdown,
    load_physical_palette_data,
    get_palette_colors,
    log_error
)
import json
from llm.PaletteDemistifyerLLM import PaletteDemistifyerLLM
from utils.api_client import BackendAPIClient

class DemystifyerDialog(BaseDialog):
    def __init__(self):
        super().__init__("dmMain.xml", "dmMainWindow")
        # Initialize dropdowns
        populate_palette_dropdown(self.builder)
        populate_physical_palette_dropdown(self.builder)
        
    def _get_signal_handlers(self):
        handlers = super()._get_signal_handlers()
        handlers.update({
            "on_submit_clicked": self.on_submit_clicked,
            "on_add_physical_palette_clicked": self.on_add_physical_palette_clicked
        })
        return handlers
        
    def on_submit_clicked(self, button):
        Gimp.message("Submit button clicked. Loading selected palettes...")
        
        # Get selected palettes from dropdowns
        selected_palette = self.builder.get_object("paletteDropdown").get_active_text()
        selected_physical_palette = self.builder.get_object("physicalPaletteDropdown").get_active_text()
        
        if not selected_palette or not selected_physical_palette:
            Gimp.message("Please select both a GIMP palette and a physical palette.")
            return
        
        try:
            # Get palette data
            gimp_palette_colors = get_palette_colors(selected_palette)
            if not gimp_palette_colors:
                Gimp.message(f"Failed to load GIMP palette: {selected_palette}")
                return
            
            # Load physical palette data
            physical_palette_data = load_physical_palette_data(selected_physical_palette)
            if not physical_palette_data:
                Gimp.message(f"Failed to load physical palette: {selected_physical_palette}")
                return
            
            # Show loading message
            Gimp.message(f"Processing palettes: {selected_palette} and {selected_physical_palette}")
            
            # Try API client first, fall back to local LLM if API fails
            try:
                Gimp.message("Attempting to connect to backend API...")
                client = BackendAPIClient()
                
                # Test API connection first
                Gimp.message("Calling health_check()...")
                health_check = client.health_check()
                
                # Debug the health_check response
                if isinstance(health_check, dict):
                    Gimp.message(f"Health check result (dict): {health_check.get('status', 'unknown')}")
                else:
                    Gimp.message(f"Health check result (not dict): {health_check}")
                    health_check = {"status": health_check}
                
                # Check for either "ok" or "healthy" status
                if health_check.get("status") in ["ok", "healthy"]:
                    Gimp.message("Connected to backend API. Processing request...")
                    
                    # Extract physical color names - following the pattern in PaletteDemistifyerLLM.format_prompt()
                    physical_color_names = []
                    
                    # Handle different formats of physical_palette_data
                    if isinstance(physical_palette_data, dict) and 'colors' in physical_palette_data:
                        # Extract color names from dictionary
                        physical_color_names = physical_palette_data['colors']
                    elif isinstance(physical_palette_data, list):
                        # Already a list of color names
                        physical_color_names = physical_palette_data
                    else:
                        # Fallback to string representation as a single item
                        physical_color_names = [str(physical_palette_data)]
                    
                    Gimp.message(f"Sending request with {len(gimp_palette_colors)} GIMP colors and {len(physical_color_names)} physical colors")
                    
                    # Call the demystify_palette method
                    Gimp.message("Calling demystify_palette()...")
                    response = client.demystify_palette(
                        gimp_palette_colors=gimp_palette_colors,
                        physical_palette_data=physical_color_names
                    )
                    
                    # Process API response
                    if not isinstance(response, dict):
                        Gimp.message(f"Unexpected response format: {type(response).__name__}")
                        response = {"success": False, "error": f"Unexpected response type: {type(response).__name__}"}
                    
                    if response.get("success"):
                        # Handle successful API response
                        result = response.get("response")
                        provider = response.get("provider", "unknown")
                        Gimp.message(f"API request successful! Received response from {provider} provider.")
                        
                        # Format the result for display
                        formatted_result = self.format_palette_mapping(result)
                        self.display_results(formatted_result, "resultTextView")
                        return
                    else:
                        # Handle API error
                        error_msg = response.get("error", "Unknown error")
                        Gimp.message(f"API error: {error_msg}. Unable to process palette.")
                else:
                    # Handle failed health check
                    error_msg = health_check.get("error", "Unknown error")
                    Gimp.message(f"Backend API not available: {error_msg}. Please try again later.")
                    return
            
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                Gimp.message(f"API communication error: {str(e)}. Unable to process palette.")
                from colorBitMagic_utils import log_error
                log_error("API communication error", e)
                log_error("Traceback", tb)
                return
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error in palette demystification", e)
            Gimp.message(f"Error: {str(e)}")
            
    def on_add_physical_palette_clicked(self, button):
        from .add_palette_dialog import AddPaletteDialog
        AddPaletteDialog().show()

    def format_palette_mapping(self, result):
        """
        Ensure the result is correctly parsed into a list of dictionaries.

        Args:
            result: JSON string or dictionary object.
            
        Returns:
            A list of structured data for display_results.
        """
        # Log the raw response for debugging
        Gimp.message(f"Raw API response: {str(result)}")

        # If result is a string, attempt to parse it
        if isinstance(result, str):
            try:
                # Remove markdown code block markers if present
                clean_result = result.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_result)  # Convert JSON string to dictionary
            except json.JSONDecodeError as e:
                Gimp.message(f"JSON parsing error: {str(e)}")
                # If parsing fails, try to render a plain text version
                cleaned_text = self.clean_json_string(result)
                return [{"error": cleaned_text}]
        else:
            data = result

        # Ensure the data is a list
        if not isinstance(data, list):
            Gimp.message("API response format unexpected (not a list)")
            return [{"error": "Unexpected API response format"}]

        formatted_data = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                Gimp.message(f"Malformed entry at index {index}: {str(item)}")
                continue  # Skip invalid entries
            
            # Make sure all required keys exist with default values
            entry = {
                "gimp_color_name": item.get("gimp_color_name", f"Unknown-{index}"),
                "rgb_color": item.get("rgb_color", "N/A"),
                "physical_color_name": item.get("physical_color_name", "Unknown"),
                "mixing_suggestions": item.get("mixing_suggestions", "N/A")
            }
            formatted_data.append(entry)

        if not formatted_data:
            # Return a list with a single error entry that has all required keys
            return [{
                "gimp_color_name": "Error",
                "rgb_color": "N/A",
                "physical_color_name": "Error",
                "mixing_suggestions": "No valid color mappings received from API"
            }]

        return formatted_data

    def clean_json_string(self, json_string):
        """
        Simple function to clean up a JSON string for display when parsing fails
        """
        # Remove any markdown code block markers
        cleaned = json_string.replace('```json', '').replace('```', '')
        
        # Remove the JSON formatting characters
        cleaned = cleaned.replace('[', '').replace(']', '')
        cleaned = cleaned.replace('{', '').replace('}', '')
        cleaned = cleaned.replace('"', '')
        
        # Replace JSON field names with more readable labels
        cleaned = cleaned.replace('gimp_color_name:', 'GIMP Color:')
        cleaned = cleaned.replace('rgb_color:', 'RGB Value:')
        cleaned = cleaned.replace('physical_color_name:', 'Physical Color:')
        cleaned = cleaned.replace('mixing_suggestions:', 'Mixing Suggestion:')
        
        # Clean up commas and formatting
        cleaned = cleaned.replace(',', '')
        
        # Remove excessive whitespace and empty lines
        lines = [line.strip() for line in cleaned.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        
        # Format with separators
        result = "PALETTE MAPPING RESULTS\n======================\n\n"
        
        # Group lines by color entry (assuming 4 lines per color)
        i = 0
        while i < len(lines):
            # Add as many lines as we can for this color entry
            color_entry = []
            while i < len(lines) and not lines[i].startswith("GIMP Color:"):
                if color_entry:  # Only add if we've already started a color entry
                    color_entry.append(lines[i])
                i += 1
            
            # Start a new color entry if we found a GIMP Color line
            if i < len(lines):
                color_entry = [lines[i]]
                i += 1
                # Add the remaining lines for this color
                while i < len(lines) and not lines[i].startswith("GIMP Color:"):
                    color_entry.append(lines[i])
                    i += 1
            
            # Add the formatted color entry with separator
            if color_entry:
                result += "\n".join(color_entry) + "\n==================================\n\n"
        
        return result
