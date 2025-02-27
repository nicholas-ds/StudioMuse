from gi.repository import Gimp
from .base_dialog import BaseDialog
from .demystifyer_dialog import DemystifyerDialog

class HomeDialog(BaseDialog):
    def __init__(self):
        super().__init__("homeDialog.xml", "GtkWindow")
        
    def _get_signal_handlers(self):
        handlers = super()._get_signal_handlers()
        handlers.update({
            "on_palette_demystifyer_clicked": self.on_palette_demystifyer_clicked
        })
        return handlers
        
    def on_palette_demystifyer_clicked(self, button):
        """Opens the Palette Demystifier dialog."""
        Gimp.message("Opening Palette Demystifier dialog...")
        DemystifyerDialog().show()
