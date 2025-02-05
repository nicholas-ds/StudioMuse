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
    """Shows the Color Bit Magic dialog."""
    DialogManager("homeDialog.xml", "GtkWindow", {
        "on_palette_demystifyer_clicked": on_palette_demystifyer_clicked,
        "on_exit_clicked": on_exit_clicked  # Connect the exit button
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
    """Handles the exit button click event."""
    Gimp.message("Exit button clicked!")
    
    # Close all active dialogs using the DialogManager
    DialogManager.close_all()  # This will close all dialogs managed by DialogManager

    # Quit the GTK main loop when the exit button is clicked
    Gtk.main_quit()


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