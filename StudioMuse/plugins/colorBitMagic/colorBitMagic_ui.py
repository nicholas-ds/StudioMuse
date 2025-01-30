import gi
import os
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk
from colorBitMagic_utils import populate_palette_dropdown, log_palette_colormap

# Global variable to keep track of the dmMain dialog
dm_main_dialog = None

def greet_from_ui():
    Gimp.message("Hello from the UI module!")

def show_color_bit_magic_dialog():
    Gimp.message("Initializing UI...")

    # Determine the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(script_dir, "templates/homeDialog.xml")
    Gimp.message(f"Loading UI file from: {xml_path}")

    builder = Gtk.Builder()
    try:
        builder.add_from_file(xml_path)
    except Exception as e:
        Gimp.message(f"Error loading UI file: {e}")
        return

    # Get the main window from the builder
    dialog = builder.get_object("GtkWindow")
    if dialog is None:
        Gimp.message("Error: Could not find GtkWindow in the XML file.")
        return

    # Connect signals if any
    builder.connect_signals({
        "on_palette_demystifyer_clicked": on_palette_demystifyer_clicked,
        "on_exit_clicked": Gtk.main_quit,
        "on_delete_event": Gtk.main_quit
    })

    # Populate the palette dropdown
    populate_palette_dropdown(builder)

    # Show the dialog
    dialog.show_all()

    # Start the GTK main loop
    Gtk.main()

def on_palette_demystifyer_clicked(button):
    Gimp.message("Palette Demystifyer button clicked. Opening dmMain dialog...")
    try:
        show_dm_main_dialog()
    except Exception as e:
        Gimp.message(f"Error while opening dmMain dialog: {e}")

def on_exit_clicked(button):
    Gimp.message("Exit button clicked!")
    Gtk.main_quit()  # Quit the GTK main loop when the exit button is clicked

def show_dm_main_dialog():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(script_dir, "templates/dmMain.xml")

    builder = Gtk.Builder()
    try:
        builder.add_from_file(xml_path)
        Gimp.message("dmMain UI file loaded successfully.")
    except Exception as e:
        Gimp.message(f"Error loading dmMain UI file: {e}")
        return

    dm_main_dialog = builder.get_object("dmMainWindow")
    if dm_main_dialog is None:
        Gimp.message("Error: Could not find dmMainWindow in the XML file. Check the ID.")
        return

    # Pass builder to handlers that need it
    builder.connect_signals({
    "on_submit_clicked": lambda button: on_submit_clicked(button, builder),
    "on_exit_clicked": lambda button: on_dm_main_dialog_close(dm_main_dialog),
    "on_delete_event": lambda *args: on_dm_main_dialog_close(dm_main_dialog)
})

    populate_palette_dropdown(builder)

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
            Gimp.message("Error: Could not find GtkEntry in the UI. Check XML IDs.")

    except Exception as e:
        Gimp.message(f"Error while logging palette colors and entry text: {e}")

def populate_palette_dropdown(builder):
    Gimp.message("Starting to populate palette dropdown...")

    # Get the dropdown widget
    palette_dropdown = builder.get_object("paletteDropdown")
    if palette_dropdown is None:
        Gimp.message("Error: Could not find 'paletteDropdown' in the UI. Check XML IDs.")
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
        Gimp.message(f"Error in populate_palette_dropdown: {e}")
        palette_dropdown.append_text("Error loading palettes")