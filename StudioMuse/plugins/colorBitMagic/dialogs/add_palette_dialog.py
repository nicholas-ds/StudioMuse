import gi
from gi.repository import Gimp
from .base_dialog import BaseDialog
from colorBitMagic_utils import save_json_to_file
from llm.LLMPhysicalPalette import LLMPhysicalPalette

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

        # Create an instance of LLMPhysicalPalette
        llm_palette = LLMPhysicalPalette()

        # Call the call_llm method with the entry text
        result = llm_palette.call_llm(entry_text)

        # Store the instance in the dialog for later access
        self.llm_palette_instance = llm_palette

        # Check if the result is an instance of LLMPhysicalPalette
        if isinstance(result, LLMPhysicalPalette):
            # Get the GtkTextView to display the response
            text_view = self.builder.get_object("GtkTextView")
            if not text_view:
                Gimp.message("GtkTextView not found in addPaletteWindow.")
                return
            
            # Set the response in the GtkTextView
            text_buffer = text_view.get_buffer()
            text_buffer.set_text("\n".join(result.colors_listed))  # Display the colors listed with line breaks

            # Save the palette logic
            Gimp.message(f"Palette saved: {result}")
        else:
            Gimp.message(result)  # Handle error message
            
    def on_save_clicked(self, button):
        """Handles saving the generated palette."""
        Gimp.message("Save button clicked. This function is being called.")

        # Access the stored LLMPhysicalPalette instance
        llm_palette = getattr(self, 'llm_palette_instance', None)
        if llm_palette is None:
            Gimp.message("No LLMPhysicalPalette instance found. Please generate a palette first.")
            return

        # Prepare the palette data
        palette_data = {
            "name": llm_palette.physical_palette_name,
            "colors": llm_palette.colors_listed,
            "num_colors": llm_palette.num_colors,
            "additional_notes": llm_palette.additional_notes,
        }

        # Save the palette data using the utility function
        save_json_to_file(palette_data, palette_data['name'])
