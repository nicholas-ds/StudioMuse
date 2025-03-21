import gi
from gi.repository import Gimp
from .base_dialog import BaseDialog
from colorBitMagic_utils import save_json_to_file
from utils.api_client import api_client
import os
import json

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
            json_response = json.loads(raw_response)
            
            # Store the raw response for later access (for saving)
            self.palette_name = json_response.get("set_name", "LLM Generated Palette")
            self.raw_response = raw_response
            self.palette_colors = json_response.get('colors', [])
            self.palette_pieces = json_response.get('piece_count', [])

            # Display the results in raw format (custom method for raw text)
            # Replace with a better presentation method
            self.display_formatted_palette(json_response, "GtkTextView")

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

    def display_raw_text(self, text, text_view_id):
        """
        Display raw text in a specified GtkTextView.

        Args:
            text: Raw text string to display.
            text_view_id: ID of the GtkTextView widget.
        """
        try:
            # Parse the JSON data
            palette_data = json.loads(text)
            
            # Format the data in a more readable way
            formatted_text = f"PALETTE: {palette_data.get('set_name', 'Unknown')}\n"
            formatted_text += f"Number of Colors: {palette_data.get('piece_count', 'Unknown')}\n\n"
            formatted_text += "COLORS:\n"
            
            # List each color with a bullet point
            for i, color in enumerate(palette_data.get('colors', []), 1):
                formatted_text += f"  • {color}\n"
            
            # Add any additional notes
            if 'additional_notes' in palette_data and palette_data['additional_notes']:
                formatted_text += f"\nNotes: {palette_data['additional_notes']}\n"
            
            # Update the text view
            text_view = self.builder.get_object(text_view_id)
            buffer = text_view.get_buffer()
            buffer.set_text(formatted_text)
            
        except json.JSONDecodeError:
            # Fallback to showing raw text if not valid JSON
            text_view = self.builder.get_object(text_view_id)
            buffer = text_view.get_buffer()
            buffer.set_text(text)

        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying raw text", e)
            Gimp.message(f"Error displaying results: {str(e)}")

    def display_formatted_palette(self, palette_data, text_view_id):
        """
        Display palette information in a formatted, visually appealing way.

        Args:
            palette_data: Dictionary containing palette information
            text_view_id: ID of the GtkTextView widget
        """
        try:
            # Get text view and its buffer
            text_view = self.builder.get_object(text_view_id)
            buffer = text_view.get_buffer()
            
            # Create tags for formatting
            buffer.create_tag("title", weight=800, size_points=14)
            buffer.create_tag("subtitle", weight=600, size_points=12)
            buffer.create_tag("normal", size_points=10)
            
            # Start with empty buffer
            buffer.set_text("")
            
            # Insert title
            iter = buffer.get_end_iter()
            buffer.insert_with_tags_by_name(iter, f"PALETTE: {palette_data.get('set_name', 'Unknown')}\n", "title")
            
            # Insert piece count
            iter = buffer.get_end_iter()
            buffer.insert_with_tags_by_name(iter, f"Number of Colors: {palette_data.get('piece_count', 'Unknown')}\n\n", "subtitle")
            
            # Insert colors section header
            iter = buffer.get_end_iter()
            buffer.insert_with_tags_by_name(iter, "COLORS:\n", "subtitle")
            
            # Insert each color with a bullet point
            for i, color in enumerate(palette_data.get('colors', []), 1):
                iter = buffer.get_end_iter()
                buffer.insert_with_tags_by_name(iter, f"  • {color}\n", "normal")
            
            # Insert additional notes if available
            if 'additional_notes' in palette_data and palette_data['additional_notes']:
                iter = buffer.get_end_iter()
                buffer.insert_with_tags_by_name(iter, f"\nNotes: ", "subtitle")
                iter = buffer.get_end_iter()
                buffer.insert_with_tags_by_name(iter, f"{palette_data['additional_notes']}\n", "normal")
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying formatted palette", e)
            Gimp.message(f"Error displaying palette: {str(e)}")
            
            # Fallback to simple text display if formatting fails
            text_view = self.builder.get_object(text_view_id)
            buffer = text_view.get_buffer()
            buffer.set_text(f"Palette: {palette_data.get('set_name', 'Unknown')}\n" +
                           f"Colors: {', '.join(palette_data.get('colors', []))}")
