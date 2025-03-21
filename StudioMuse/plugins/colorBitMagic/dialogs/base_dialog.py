from .dialog_manager import DialogManager
from gi.repository import Gtk, Pango, Gimp


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
    
    def _get_or_create_tags(self, text_buffer):
        """
        Create or retrieve text formatting tags for a buffer.
        Returns a dictionary of tag objects that can be used for styling.
        
        Args:
            text_buffer: The Gtk.TextBuffer to create tags for
            
        Returns:
            Dictionary of tag names to tag objects
        """
        # Define standard tags if they don't exist yet
        tag_definitions = {
            "header": {"weight": Pango.Weight.BOLD, "size": 20 * Pango.SCALE},
            "bold": {"weight": Pango.Weight.BOLD},
            "italic": {"style": Pango.Style.ITALIC},
            "color_blue": {"foreground": "blue"},
            "color_red": {"foreground": "red"},
            "color_green": {"foreground": "green"},
            "monospace": {"family": "monospace"},
            "underline": {"underline": Pango.Underline.SINGLE},
            "h1": {"weight": Pango.Weight.BOLD, "size": 18 * Pango.SCALE},
            "h2": {"weight": Pango.Weight.BOLD, "size": 16 * Pango.SCALE},
            "h3": {"weight": Pango.Weight.BOLD, "size": 14 * Pango.SCALE},
        }
        
        tags = {}
        for tag_name, properties in tag_definitions.items():
            # Check if tag already exists
            tag = text_buffer.get_tag_table().lookup(tag_name)
            if not tag:
                # Create new tag with properties
                tag = text_buffer.create_tag(tag_name, **properties)
            tags[tag_name] = tag
        
        return tags
    
    def insert_styled_text(self, text_buffer, text, tag_names=None):
        """
        Insert text with optional styling tags.
        
        Args:
            text_buffer: The Gtk.TextBuffer to insert into
            text: The text to insert
            tag_names: String or list of tag names to apply
        
        Returns:
            The end iterator after insertion
        """
        iter = text_buffer.get_end_iter()
        
        if not tag_names:
            text_buffer.insert(iter, text)
        else:
            # Convert single tag name to list
            if isinstance(tag_names, str):
                tag_names = [tag_names]
                
            # Get tags from their names
            tags = []
            for name in tag_names:
                tag = text_buffer.get_tag_table().lookup(name)
                if tag:
                    tags.append(tag)
            
            # Insert text with tags
            if tags:
                text_buffer.insert_with_tags(iter, text, *tags)
            else:
                text_buffer.insert(iter, text)
        
        return text_buffer.get_end_iter()
    
    def insert_labeled_value(self, text_buffer, label, value, label_tags=None, value_tags=None):
        """
        Insert a labeled value pair (like "Label: Value") with different styling for each.
        
        Args:
            text_buffer: The Gtk.TextBuffer to insert into
            label: The label text
            value: The value text
            label_tags: Tag name(s) to apply to the label
            value_tags: Tag name(s) to apply to the value
        """
        self.insert_styled_text(text_buffer, label, label_tags)
        self.insert_styled_text(text_buffer, f"{value}\n", value_tags)
    
    def display_results(self, text, text_view_id):
        """
        Display formatted text results in a specified GtkTextView.

        Args:
            text: List of structured dictionaries.
            text_view_id: ID of the GtkTextView widget.
        """
        try:
            # Get the GtkTextView object
            text_view = self.builder.get_object(text_view_id)
            if not text_view:
                Gimp.message(f"Could not find text view with ID: {text_view_id}")
                return

            # Get the GtkTextBuffer
            text_buffer = text_view.get_buffer()

            # Clear existing text
            text_buffer.set_text("")
            
            # Set up tags
            self._get_or_create_tags(text_buffer)

            # Insert header
            self.insert_styled_text(text_buffer, "PALETTE MAPPING RESULTS\n", "header")
            
            # Insert separator
            self.insert_styled_text(text_buffer, "======================\n\n", "monospace")

            # Process each entry in the text list
            for entry in text:
                # Insert GIMP Color with bold label
                self.insert_labeled_value(
                    text_buffer, 
                    "GIMP Color: ", 
                    entry.get('gimp_color_name', 'N/A'),
                    "bold", 
                    None
                )
                
                # Insert RGB Value with bold label and colored value
                self.insert_labeled_value(
                    text_buffer, 
                    "RGB Value: ", 
                    entry.get('rgb_color', 'N/A'),
                    "bold", 
                    "color_red"
                )
                
                # Insert Physical Color with bold label
                self.insert_labeled_value(
                    text_buffer, 
                    "Physical Color: ", 
                    entry.get('physical_color_name', 'N/A'),
                    "bold", 
                    None
                )
                
                # Insert Mixing Suggestion with bold label
                self.insert_labeled_value(
                    text_buffer, 
                    "Mixing Suggestion: ", 
                    entry.get('mixing_suggestions', 'N/A'),
                    "bold", 
                    None
                )
                
                # Insert separator
                self.insert_styled_text(
                    text_buffer, 
                    "==================================\n\n", 
                    "monospace"
                )

        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error displaying formatted results", e)
            Gimp.message(f"Error displaying results: {str(e)}")