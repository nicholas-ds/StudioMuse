import gi
import os
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk
from colorBitMagic_utils import populate_palette_dropdown, log_palette_colormap, log_error
from ui.dialogManager import DialogManager

# Global variable to keep track of the dmMain dialog
dm_main_dialog = None



def show_color_bit_magic_dialog():
    DialogManager("homeDialog.xml", "GtkWindow", {
        "on_palette_demystifyer_clicked": on_palette_demystifyer_clicked
    }).show()

def on_palette_demystifyer_clicked(button):
    """Opens the Palette Demystifier dialog and populates the palette dropdown."""
    Gimp.message("Opening Palette Demystifier dialog...")
    
    dm_dialog = DialogManager("dmMain.xml", "dmMainWindow", {
        "on_submit_clicked": on_submit_clicked,
        "on_exit_clicked": on_dm_main_dialog_close,
        "on_delete_event": on_dm_main_dialog_close,
        "on_add_physical_palette_clicked": on_add_physical_palette_clicked
    })
    
    # Populate palette dropdown
    populate_palette_dropdown(dm_dialog.builder)

    dm_dialog.show()

def on_exit_clicked(button):
    Gimp.message("Exit button clicked!")
    Gtk.main_quit()  # Quit the GTK main loop when the exit button is clicked


    Gimp.message("dmMainWindow found, displaying dialog.")
    dm_main_dialog.show_all()

def on_dm_main_dialog_close(*args):
    global dm_main_dialog
    Gimp.message("Closing dmMain dialog.")
    dm_main_dialog.destroy()
    dm_main_dialog = None
    Gtk.main_quit()

def on_submit_clicked(button, builder):
    Gimp.message("Submit button clicked. Logging palette colors and entry text...")
    try:
        # Log palette colors
        log_palette_colormap(builder)  # Assuming this function logs the palette colors

        # Retrieve the GtkEntry widget
        entry = builder.get_object("physicalPaletteEntry")  # Use the ID from the XML
        if entry is not None:
            entry_text = entry.get_text()
            Gimp.message(f"Entry text: {entry_text}")
        else:
            log_error("Could not find GtkEntry in the UI. Check XML IDs.")

    except Exception as e:
        log_error("Error while logging palette colors and entry text", e)

def populate_palette_dropdown(builder):
    Gimp.message("Starting to populate palette dropdown...")

    # Get the dropdown widget
    palette_dropdown = builder.get_object("paletteDropdown")
    if palette_dropdown is None:
        log_error("Could not find 'paletteDropdown' in the UI. Check XML IDs.")
        return

    try:
        # Ensure it's a valid GtkComboBoxText
        if not isinstance(palette_dropdown, Gtk.ComboBoxText):
            Gimp.message(f"Error: 'paletteDropdown' is not a GtkComboBoxText but a {type(palette_dropdown)}.")
            return

        # Clear existing items
        palette_dropdown.remove_all()

        # Retrieve the list of palettes
        palettes = Gimp.palettes_get_list("")
        if not palettes:
            Gimp.message("No palettes found.")
            palette_dropdown.append_text("No palettes found")
            return

        Gimp.message(f"Retrieved {len(palettes)} palettes.")

        # Extract and append palette names
        for palette in palettes:
            palette_name = palette.get_name() if hasattr(palette, 'get_name') else str(palette)
            palette_dropdown.append_text(palette_name)

        Gimp.message("Palette dropdown populated successfully.")

    except Exception as e:
        log_error("Error in populate_palette_dropdown", e)
        palette_dropdown.append_text("Error loading palettes")

def on_add_physical_palette_clicked(button):
    Gimp.message("Add Physical Palette button clicked. Opening addPalette dialog...")
    try:
        show_add_palette_dialog()
    except Exception as e:
        Gimp.message(f"Error while opening addPalette dialog: {e}")

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