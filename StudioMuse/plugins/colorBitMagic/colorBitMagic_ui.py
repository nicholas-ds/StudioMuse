import gi
import os
import sys
import json
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk
from colorBitMagic_utils import populate_palette_dropdown, log_palette_colormap, log_error, get_palette_colors
from ui.dialogManager import DialogManager
from llm.LLMPhysicalPalette import LLMPhysicalPalette

# Global variable to keep track of the dmMain dialog
dm_main_dialog = None



def show_color_bit_magic_dialog():
    """Shows the Color Bit Magic dialog."""
    DialogManager("homeDialog.xml", "GtkWindow", {
        "on_palette_demystifyer_clicked": on_palette_demystifyer_clicked
    }).show()

def on_palette_demystifyer_clicked(button):
    """Opens the Palette Demystifier dialog and populates the palette dropdown."""
    Gimp.message("Opening Palette Demystifier dialog...")
    
    dm_dialog = DialogManager("dmMain.xml", "dmMainWindow", {
        "on_submit_clicked": on_submit_clicked,
        "on_add_physical_palette_clicked": on_add_physical_palette_clicked
    })
    
    # Populate palette dropdown
    populate_palette_dropdown(dm_dialog.builder)

    dm_dialog.show()


def on_submit_clicked(button):
    Gimp.message("Submit button clicked. Logging selected palette...")

    try:
        Gimp.message("Entered on_submit_clicked function.")

        # Retrieve the builder instance from the DialogManager
        builder = DialogManager.dialogs.get("dmMainWindow")
        if builder is None:
            log_error("DialogManager did not provide a valid builder for dmMainWindow.")
            return

        palette_dropdown = builder.builder.get_object("paletteDropdown")
        if palette_dropdown is not None:
            # Get the active text from the dropdown
            selected_palette = palette_dropdown.get_active_text()
            if selected_palette:
                Gimp.message(f"Selected palette: {selected_palette}")
                print(get_palette_colors(selected_palette))
            else:
                Gimp.message("No palette selected.")
        else:
            log_error("Could not find GtkComboBoxText in the UI. Check XML IDs.")

    except Exception as e:
        log_error("Error while logging selected palette", e)

def on_add_physical_palette_clicked(button):
    Gimp.message("Add Physical Palette button clicked. Opening addPalette dialog...")
    Gimp.message(sys.executable)
    try:
        DialogManager("addPalette.xml", "addPaletteWindow", {
            "on_close_clicked": on_close_clicked,
            "on_generate_clicked": on_generate_clicked  # Connect the new handler
        }).show()
    except Exception as e:
        Gimp.message(f"Error while opening addPalette dialog: {e}")

def on_close_clicked(button):
    """Handles the close button click by only closing the dialog."""
    Gimp.message("Closing addPalette dialog.")
    button.get_toplevel().destroy()

def show_add_palette_dialog():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(script_dir, "templates/addPalette.xml")

    builder = Gtk.Builder()
    try:
        builder.add_from_file(xml_path)
        Gimp.message("addPalette UI file loaded successfully.")
    except Exception as e:
        log_error(f"Error loading addPalette UI file from {xml_path}", e)
        return

    add_palette_dialog = builder.get_object("addPaletteWindow")
    if add_palette_dialog is None:
        log_error("Could not find addPaletteWindow in the XML file. Check the ID.")
        return

    # Connect signals for the addPalette dialog buttons
    builder.connect_signals({
        "on_save_clicked": lambda button: on_save_palette(button, builder),
        "on_generate_clicked": lambda button: on_generate_palette(button, builder),
        "on_close_clicked": lambda button: add_palette_dialog.destroy()
    })

    Gimp.message("addPaletteWindow found, displaying dialog.")
    add_palette_dialog.show_all()

def on_generate_clicked(button):
    Gimp.message("Generate button clicked. Sending text to LLM...")

    # Retrieve the builder instance for addPaletteWindow
    builder = DialogManager.dialogs.get("addPaletteWindow")
    if builder is None:
        Gimp.message("DialogManager did not provide a valid builder for addPaletteWindow.")
        return

    # Get the GtkEntry widget containing the user input
    entry_widget = builder.builder.get_object("GtkEntry")
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

    # Check if the result is an instance of LLMPhysicalPalette
    if isinstance(result, LLMPhysicalPalette):
        # Get the GtkTextView to display the response
        text_view = builder.builder.get_object("GtkTextView")
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
