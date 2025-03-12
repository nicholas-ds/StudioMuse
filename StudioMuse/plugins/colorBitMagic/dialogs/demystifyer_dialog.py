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
                    
                    # Process API response
                    if not isinstance(response, dict):
                        Gimp.message(f"Unexpected response format: {type(response).__name__}")
                        response = {"success": False, "error": f"Unexpected response type: {type(response).__name__}"}
                    
                    if response.get("success"):
                        # Handle successful API response
                        result = response.get("response")
                        provider = response.get("provider", "unknown")
                        Gimp.message(f"API request successful! Received response from {provider} provider.")
                        Gimp.message(f"This is the result: {result}")
                        self.display_results(result, "resultTextView")
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
