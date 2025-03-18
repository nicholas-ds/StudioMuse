import gi
from gi.repository import Gimp
from .base_dialog import BaseDialog
from colorBitMagic_utils import save_json_to_file
from utils.api_client import api_client
import os

class AddPaletteDialog(BaseDialog):
    def __init__(self):
        super().__init__("addPalette.xml", "addPaletteWindow")
        
    def _get_signal_handlers(self):
        handlers = super()._get_signal_handlers()
        handlers.update({
            "on_close_clicked": self.on_close_clicked,
            "on_generate_clicked": self.on_generate_clicked,
            "on_save_clicked": self.on_save_clicked
        })
        return handlers
    
    def on_close_clicked(self, button):
        """Closes the dialog."""
        button.get_toplevel().destroy()
        
    def on_generate_clicked(self, button):
        """Handles generating palette from LLM."""
        Gimp.message("Generate button clicked. Sending text to LLM...")

        # Get the GtkEntry widget containing the user input
        entry_widget = self.builder.get_object("GtkEntry")
        if not entry_widget:
            Gimp.message("GtkEntry not found in addPaletteWindow.")
            return

        entry_text = entry_widget.get_text()
        if not entry_text:
            Gimp.message("No text entered in GtkEntry.")
            return

        Gimp.message(f"Text to send to LLM: {entry_text}")

        # Use the API client to create a physical palette
        try:
            # Call the backend API
            result = api_client.create_physical_palette(entry_text)
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                Gimp.message(f"Error creating palette: {error_msg}")
                return
                
            # Get the raw response from the LLM
            raw_response = result.get("response", "")
            
            # Store the raw response for later access (for saving)
            self.raw_response = raw_response
            self.palette_name = "LLM Generated Palette"

            # Display the results
            self.display_results(raw_response, "GtkTextView")

            # Show success message
            Gimp.message("Received response from LLM")
            
        except Exception as e:
            Gimp.message(f"Error: {str(e)}")
            
    def on_save_clicked(self, button):
        """Handles saving the generated palette."""
        Gimp.message("Save button clicked. This function is being called.")

        # Check if we have a response to save
        if not hasattr(self, 'raw_response'):
            Gimp.message("No LLM response found. Please generate a palette first.")
            return

        palette_name = self.palette_name
        
        palette_data = {
            "name": palette_name,
            "raw_response": self.raw_response,
        }
        
        # Define the output directory for physical palettes
        gimp_dir = Gimp.directory()
        physical_palettes_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
        
        # Save the palette data using the refactored utility function
        filepath = save_json_to_file(
            data=palette_data,
            filename=palette_name,
            directory=physical_palettes_dir
        )
        
        if filepath:
            Gimp.message(f"Palette '{palette_name}' saved successfully.")
        else:
            Gimp.message(f"Failed to save palette '{palette_name}'.")
