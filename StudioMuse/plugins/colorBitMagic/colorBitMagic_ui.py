import gi
import os
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk

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
        "on_exit_clicked": on_exit_clicked,
        "on_delete_event": Gtk.main_quit  # Connect the delete event to Gtk.main_quit
    })

    # Show the dialog
    dialog.show_all()

    # Start the GTK main loop
    Gtk.main()

def on_palette_demystifyer_clicked(button):
    Gimp.message("Palette Demystifyer button clicked!")

def on_exit_clicked(button):
    Gimp.message("Exit button clicked!")
    Gtk.main_quit()  # Quit the GTK main loop when the exit button is clicked