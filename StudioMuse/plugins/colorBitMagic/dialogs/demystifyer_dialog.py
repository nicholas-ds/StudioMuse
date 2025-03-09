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

        try:
            # Get both dropdown selections
            palette_dropdown = self.builder.get_object("paletteDropdown")
            physical_palette_dropdown = self.builder.get_object("physicalPaletteDropdown")

            if palette_dropdown is None or physical_palette_dropdown is None:
                log_error("Could not find dropdowns in the UI. Check XML IDs.")
                return

            # Get selected values directly from the ComboBoxText widgets
            selected_palette = palette_dropdown.get_active_text()
            selected_physical_palette = physical_palette_dropdown.get_active_text()

            if selected_palette and selected_physical_palette:
                # Show loading message
                Gimp.message(f"Processing palettes: {selected_palette} and {selected_physical_palette}")
                
                # FALLBACK TO ORIGINAL CODE FOR NOW
                # This is the code that was working before
                demystifier = PaletteDemistifyerLLM(
                    gimp_palette_name=selected_palette,
                    physical_palette_name=selected_physical_palette
                )
                
                result = demystifier.call_llm()
                self.display_results(result)
                
                """
                # NEW CODE: Use API client - COMMENTED OUT UNTIL BACKEND IS FIXED
                # Get palette data - using the proper methods that return serializable data
                palette_data = gimp_palette_to_palette_data(selected_palette)
                if not palette_data:
                    Gimp.message(f"Failed to load GIMP palette: {selected_palette}")
                    return
                
                # Convert PaletteData to serializable dictionary
                gimp_palette_colors = {}
                for color in palette_data.colors:
                    gimp_palette_colors[color.name] = {
                        "R": color.rgb["r"] / 255.0,  # Convert to 0-1 range for API
                        "G": color.rgb["g"] / 255.0,
                        "B": color.rgb["b"] / 255.0,
                        "A": 1.0
                    }
                
                # Load physical palette data
                try:
                    from utils.palette_processor import PaletteProcessor
                    physical_palette = PaletteProcessor.load_palette(selected_physical_palette)
                    if physical_palette and hasattr(physical_palette, 'colors'):
                        physical_color_names = [color.name for color in physical_palette.colors]
                    else:
                        Gimp.message(f"Failed to load physical palette: {selected_physical_palette}")
                        return
                except Exception as e:
                    log_error(f"Failed to load physical palette: {selected_physical_palette}", e)
                    Gimp.message(f"Error loading physical palette: {str(e)}")
                    return
                
                client = BackendAPIClient()
                
                response = client.demystify_palette(
                    gimp_palette_colors=gimp_palette_colors,
                    physical_palette_data=physical_color_names
                )
                
                if response.get("success"):
                    result = response.get("result")
                    # Process result same as before
                    self.display_results(result)
                    Gimp.message("Successfully demystified palette!")
                else:
                    error_msg = response.get("error", "Unknown error")
                    Gimp.message(f"Error demystifying palette: {error_msg}")
                """
                
            else:
                Gimp.message("Please select both a GIMP palette and a physical palette.")
            
        except Exception as e:
            log_error("Error in demystification", e)
            Gimp.message(f"Error: {str(e)}")
            
    def on_add_physical_palette_clicked(self, button):
        from .add_palette_dialog import AddPaletteDialog
        AddPaletteDialog().show()

    def display_results(self, result):
        """Display the demystification results in the UI"""
        try:
            from gi.repository import Gimp
            
            # Get the text view for displaying results
            text_view = self.builder.get_object("resultTextView")
            if not text_view:
                Gimp.message("Could not find resultTextView in the UI")
                return
            
            # Get the buffer
            buffer = text_view.get_buffer()
            
            # Format the results for display
            if isinstance(result, list):
                # Format as a readable list
                formatted_text = ""
                for item in result:
                    if isinstance(item, dict):
                        gimp_color = item.get("gimp_color_name", "Unknown")
                        rgb_color = item.get("rgb_color", "Unknown")
                        physical_color = item.get("physical_color_name", "Unknown")
                        mixing = item.get("mixing_suggestions", "")
                        
                        formatted_text += f"GIMP Color: {gimp_color} ({rgb_color})\n"
                        formatted_text += f"Physical Match: {physical_color}\n"
                        if mixing:
                            formatted_text += f"Mixing Suggestions: {mixing}\n"
                        formatted_text += "\n"
                    else:
                        formatted_text += f"{item}\n"
            elif isinstance(result, dict) and "raw_text" in result:
                # Display raw text if JSON parsing failed
                formatted_text = f"JSON parsing failed. Raw response:\n\n{result['raw_text']}"
            else:
                # Format as JSON string with indentation
                import json
                formatted_text = json.dumps(result, indent=2)
            
            # Set the text in the text view
            buffer.set_text(formatted_text)
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying results", e)
            Gimp.message(f"Error displaying results: {str(e)}")
