import os
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk
from colorBitMagic_utils import log_error

class DialogManager:
    """Handles loading, displaying, and managing any GIMP dialog dynamically."""
    
    gtk_running = False  # Tracks if Gtk.main() is running
    dialogs = {}  # Stores open dialogs

    def __init__(self, ui_file, window_id, signal_handlers=None):
        """
        Initializes the dialog from an XML file.

        :param ui_file: XML filename (e.g., "homeDialog.xml")
        :param window_id: The main window ID in the XML (e.g., "GtkWindow")
        :param signal_handlers: (Optional) Dictionary of signal handlers for this dialog
        """
        self.ui_file = ui_file
        self.window_id = window_id
        self.builder = Gtk.Builder()

        # Load the XML UI file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        xml_path = os.path.join(script_dir, "../templates", ui_file)  # Go up one level and into templates
        xml_path = os.path.abspath(xml_path)  # Ensure absolute path

        Gimp.message(f"Loading UI file from: {xml_path}")

        try:
            self.builder.add_from_file(xml_path)
        except Exception as e:
            log_error(f"Error loading UI file: {ui_file}", e)
            return

        # Get the main dialog window
        self.dialog = self.builder.get_object(window_id)
        if self.dialog is None:
            log_error(f"Could not find '{window_id}' in {ui_file}.")
            return

        # Store dialog reference
        DialogManager.dialogs[window_id] = self.dialog

        # Connect signals dynamically
        default_signals = {
            "on_exit_clicked": self.close,
            "on_delete_event": self.close
        }
        if signal_handlers:
            default_signals.update(signal_handlers)

        self.builder.connect_signals(default_signals)

    def show(self):
        """Displays the dialog and starts Gtk main loop if necessary."""
        if self.dialog:
            self.dialog.show_all()
            if not DialogManager.gtk_running:
                DialogManager.gtk_running = True
                Gtk.main()

    def close(self, *args):
        """Closes the dialog and quits Gtk main loop if necessary."""
        if self.dialog:
            self.dialog.destroy()

        # Remove from tracking
        if self.window_id in DialogManager.dialogs:
            del DialogManager.dialogs[self.window_id]

        # Quit Gtk main if no more dialogs are open
        if not DialogManager.dialogs:
            DialogManager.gtk_running = False
            Gtk.main_quit()
