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
        
    def display_results(self, result, text_view_id):
        """
        Display text results in a specified text view
        
        Args:
            result: The result data to display (string or dict with 'response' key)
            text_view_id: ID of the text view to display results in
        """
        try:
            from gi.repository import Gimp
            
            # Get the text view for displaying results
            text_view = self.builder.get_object(text_view_id)
            if not text_view:
                Gimp.message(f"Could not find text view with ID: {text_view_id}")
                return
            
            # Get the buffer
            buffer = text_view.get_buffer()
            
            # Process the result to get displayable text
            if isinstance(result, dict) and "response" in result:
                # If response is available from the API
                raw_text = result["response"]
            else:
                # Convert any result to string representation
                raw_text = str(result)
            
            # Set the text in the text view
            buffer.set_text(raw_text)
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying results", e)
            Gimp.message(f"Error displaying results: {str(e)}")