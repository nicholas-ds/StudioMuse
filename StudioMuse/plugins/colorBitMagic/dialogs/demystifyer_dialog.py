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
                    
                    # Debug the response
                    if isinstance(response, dict):
                        Gimp.message(f"API response (dict): success={response.get('success', False)}")
                    else:
                        Gimp.message(f"API response (not dict): {response}")
                        response = {"success": False, "error": f"Unexpected response type: {type(response).__name__}"}
                    
                    if response.get("success"):
                        result = response.get("raw_response")
                        Gimp.message(f"API request successful! Received response from {response.get('provider', 'unknown')} provider.")
                        self.display_results(result)
                        return
                    else:
                        error_msg = response.get("error", "Unknown error")
                        Gimp.message(f"API error: {error_msg}. Falling back to local processing...")
                else:
                    error_msg = health_check.get("error", "Unknown error")
                    Gimp.message(f"Backend API not available: {error_msg}. Using local LLM processing...")
            
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                Gimp.message(f"API communication error: {str(e)}. Using local LLM processing...")
                from colorBitMagic_utils import log_error
                log_error("API communication error", e)
                log_error("Traceback", tb)
            
            # Fallback to local LLM processing
            Gimp.message("Using local LLM for palette processing...")
            demystifier = PaletteDemistifyerLLM(
                gimp_palette_name=selected_palette,
                physical_palette_name=selected_physical_palette
            )
            
            result = demystifier.call_llm()
            self.display_results(result)
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error in palette demystification", e)
            Gimp.message(f"Error: {str(e)}")
            
    def on_add_physical_palette_clicked(self, button):
        from .add_palette_dialog import AddPaletteDialog
        AddPaletteDialog().show()

    def display_results(self, result):
        """Display the raw demystification results in the UI"""
        try:
            from gi.repository import Gimp
            
            # Get the text view for displaying results
            text_view = self.builder.get_object("resultTextView")
            if not text_view:
                Gimp.message("Could not find resultTextView in the UI")
                return
            
            # Get the buffer
            buffer = text_view.get_buffer()
            
            # Display raw result without any processing
            if isinstance(result, dict) and "raw_response" in result:
                # If raw_response is available from the API
                raw_text = result["raw_response"]
            else:
                # Convert any result to string representation
                raw_text = str(result)
            
            # Set the raw text in the text view
            buffer.set_text(raw_text)
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying results", e)
            Gimp.message(f"Error displaying results: {str(e)}")
