from .dialog_manager import DialogManager

class BaseDialog:
    def __init__(self, ui_file, window_id):
        self.dialog_manager = DialogManager(ui_file, window_id, self._get_signal_handlers())
        self.builder = self.dialog_manager.builder
        
    def show(self):
        self.dialog_manager.show()
        
    def _get_signal_handlers(self):
        return {
            "on_exit_clicked": self.on_exit_clicked
        }
        
    def on_exit_clicked(self, button):
        self.dialog_manager.on_exit_clicked(button)
