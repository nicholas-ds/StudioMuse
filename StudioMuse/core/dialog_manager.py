import os
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk
from colorBitMagic_utils import log_error

class DialogManager:
    """Handles loading, displaying, and managing any GIMP dialog dynamically."""
    
    gtk_running = False
    dialogs = {} 

    def __init__(self, ui_file, window_id, signal_handlers=None):
        """
        Initializes the dialog from an XML file.

        :param ui_file: XML filename (e.g., "dmMain.xml")
        :param window_id: The main window ID in the XML (e.g., "GtkWindow")
        :param signal_handlers: (Optional) Dictionary of signal handlers for this dialog
        """
        self.ui_file = ui_file
        self.window_id = window_id
        self.builder = Gtk.Builder()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        xml_path = os.path.join(script_dir, "../templates", ui_file)
        xml_path = os.path.abspath(xml_path)

        Gimp.message(f"Loading UI file from: {xml_path}")

        try:
            self.builder.add_from_file(xml_path)
        except Exception as e:
            log_error(f"Error loading UI file: {ui_file}", e)
            return

        self.dialog = self.builder.get_object(window_id)
        if self.dialog is None:
            log_error(f"Could not find '{window_id}' in {ui_file}.")
            return
        
        self.dialog.set_position(Gtk.WindowPosition.CENTER) 
        self.__class__.dialogs[window_id] = self

        default_signals = {
            "on_exit_clicked": self.on_exit_clicked
        }

        if signal_handlers:
            default_signals.update(signal_handlers)

        self.builder.connect_signals(default_signals)
        
        Gimp.message(f"Connected signals for {window_id}")

    def show(self):
        """Displays the dialog and starts Gtk main loop if necessary."""
        if self.dialog:
            self.dialog.show_all()
            if not self.__class__.gtk_running:
                self.__class__.gtk_running = True
                Gtk.main()

    def on_exit_clicked(self, button):
        """Handles the exit button click by closing the dialog and stopping the GTK loop if needed."""
        Gimp.message(f"Closing dialog: {self.window_id}")
        
        if self.dialog:
            self.dialog.destroy()
        
        # Stop GTK main loop if it's running
        if Gtk.main_level() > 0:
            Gtk.main_quit()
        
        # Remove dialog reference from the class dictionary
        if self.window_id in self.__class__.dialogs:
            del self.__class__.dialogs[self.window_id]
