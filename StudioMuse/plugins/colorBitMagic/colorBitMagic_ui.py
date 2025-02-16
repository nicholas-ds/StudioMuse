import gi
import os
import sys
import json
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk
from colorBitMagic_utils import populate_palette_dropdown, log_palette_colormap, log_error, get_palette_colors, save_palette_to_file, save_json_to_file, populate_physical_palette_dropdown, load_physical_palette_data
from ui.dialogManager import DialogManager
from llm.LLMPhysicalPalette import LLMPhysicalPalette
from llm.PaletteDemistifyerLLM import PaletteDemistifyerLLM

# Global variable to keep track of the dmMain dialog
dm_main_dialog = None



def show_color_bit_magic_dialog():
    """Shows the Color Bit Magic dialog."""
    DialogManager("homeDialog.xml", "GtkWindow", {
        "on_palette_demystifyer_clicked": on_palette_demystifyer_clicked
    }).show()

def on_palette_demystifyer_clicked(button):
    """Opens the Palette Demystifier dialog and populates the dropdowns."""
    Gimp.message("Opening Palette Demystifier dialog...")
    
    dm_dialog = DialogManager("dmMain.xml", "dmMainWindow", {
        "on_submit_clicked": on_submit_clicked,
        "on_add_physical_palette_clicked": on_add_physical_palette_clicked
    })
    
    # Populate both dropdowns
    populate_palette_dropdown(dm_dialog.builder)
    populate_physical_palette_dropdown(dm_dialog.builder)

    dm_dialog.show()


def on_submit_clicked(button):
    Gimp.message("Submit button clicked. Loading selected palettes...")

    try:
        # Retrieve the builder instance from the DialogManager
        builder = DialogManager.dialogs.get("dmMainWindow")
        if builder is None:
            log_error("DialogManager did not provide a valid builder for dmMainWindow.")
            return

        # Get both dropdown selections
        palette_dropdown = builder.builder.get_object("paletteDropdown")
        physical_palette_dropdown = builder.builder.get_object("physicalPaletteDropdown")

        if palette_dropdown is None or physical_palette_dropdown is None:
            log_error("Could not find dropdowns in the UI. Check XML IDs.")
            return

        # Get selected values
        selected_palette = palette_dropdown.get_active_text()
        selected_physical_palette = physical_palette_dropdown.get_active_text()

        if selected_palette and selected_physical_palette:
            Gimp.message(f"Selected GIMP palette: {selected_palette}")

            # Load physical palette data
            physical_palette_data = load_physical_palette_data(selected_physical_palette)
            if physical_palette_data:
                Gimp.message(f"Selected physical palette: {selected_physical_palette}")
                Gimp.message(f"Loaded physical palette data: {json.dumps(physical_palette_data, indent=2)}")

            # Get GIMP palette colors (existing functionality)
            palette_colors = get_palette_colors(selected_palette)
            rgb_palette_colors = {}
            for i, color in enumerate(palette_colors, 1):
                rgba = color.get_rgba()
                color_data = {
                    "R": round(rgba[0], 3),
                    "G": round(rgba[1], 3),
                    "B": round(rgba[2], 3),
                    "A": round(rgba[3], 3)
                }
                rgb_palette_colors[f"color{i}"] = color_data

            # Create a dictionary to store all data
            all_data = {
                "gimp_palette": selected_palette,
                "physical_palette": selected_physical_palette,
                "gimp_palette_colors": rgb_palette_colors,
                "physical_palette_data": physical_palette_data["colors"]
            }
            
            # Create an instance of PaletteDemistifyerLLM and call the LLM
            demystifyer = PaletteDemistifyerLLM()
            result = demystifyer.call_llm(all_data)

            if isinstance(result, PaletteDemistifyerLLM):
                Gimp.message("Analysis complete! Here are the results:")
                Gimp.message(json.dumps(result.analysis_result, indent=2))
            else:
                Gimp.message(f"Error during analysis: {result}")

        else:
            Gimp.message("Please select both a GIMP palette and a physical palette.")

    except Exception as e:
        log_error("Error while processing selected palettes", e)

def on_add_physical_palette_clicked(button):
    Gimp.message("Add Physical Palette button clicked. Opening addPalette dialog...")
    try:
        DialogManager("addPalette.xml", "addPaletteWindow", {
            "on_close_clicked": on_close_clicked,
            "on_generate_clicked": on_generate_clicked,
            "on_save_clicked": on_save_clicked  # Add the save handler here
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
        "on_save_clicked": on_save_clicked,
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

    # Store the instance in the DialogManager for later access
    builder.llm_palette_instance = llm_palette

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

def on_save_clicked(button):
    Gimp.message("Save button clicked. This function is being called.")

    # Retrieve the builder instance for addPaletteWindow
    builder = DialogManager.dialogs.get("addPaletteWindow")
    if builder is None:
        Gimp.message("DialogManager did not provide a valid builder for addPaletteWindow.")
        return

    # Access the stored LLMPhysicalPalette instance
    llm_palette = getattr(builder, 'llm_palette_instance', None)
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
