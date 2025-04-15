import logging
import os
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk, GLib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("harmonic_measure")

# Import shared UI utilities
from core.utils.ui import (
    connect_signals,
    collect_widgets,
    get_widget_value,
    show_message,
    populate_dropdown,
    cleanup_resources,
    load_css_for_plugin
)

# Import file I/O utilities
from core.utils.file_io import (
    get_plugin_storage_path,
    save_json_data,
    load_json_data
)

# Import validation utilities
from core.utils.validation import (
    validate_required_field,
    validate_numeric,
    validate_and_show_errors
)

# Import measurement models
from core.models.measurement_models import Measurement, MeasurementCollection

class HarmonicMeasureUI:
    """
    Handles the Harmonic Measure popup UI interactions
    """
    
    def __init__(self, builder, parent_widget=None, parent_ui=None):
        """
        Initialize the Harmonic Measure UI
        
        Args:
            builder: GTK builder instance with loaded UI
            parent_widget: Widget that triggered the popup
            parent_ui: Parent UI instance for data sharing
        """
        self.builder = builder
        self.parent_widget = parent_widget
        self.parent_ui = parent_ui
        self.is_active = True
        
        # Initialize CSS for the popup
        css_path = os.path.join(os.path.dirname(__file__), "../../ui/structure/harmonic_measure.css")
        fallback_css = """
        .measurement-header { 
            background-color: #e0e0e0; 
            padding: 8px; 
            border-radius: 4px;
        }
        .measurement-value { 
            font-weight: bold; 
            color: #2a7fff;
        }
        """
        css_loaded = load_css_for_plugin(css_path, fallback_css)
        logger.info(f"CSS loading result: {css_loaded}")
        
        # Collect widgets using the shared utility
        widget_ids = [
            "saveButton",
            "cancelButton",
            "measurementValueLabel",
            "measurementNameEntry",
            "measurementUnitDropdown",
            "groupDropdown",
            "newGroupEntry"
        ]
        self.widgets = collect_widgets(builder, widget_ids)
        
        # Connect signals using shared utility
        custom_handlers = {
            "saveButton": [("clicked", self.on_save_clicked)],
            "cancelButton": [("clicked", self.on_cancel_clicked)],
            "groupDropdown": [("changed", self.on_group_dropdown_changed)]
        }
        connect_signals(self.builder, self, custom_handlers)
        
        # Initialize UI state
        self.initialize_ui()
        
        logger.info("Harmonic Measure UI initialized successfully")
    
    def initialize_ui(self):
        """Initialize the UI state with default values and populate dropdowns"""
        # Ensure the new group entry is hidden by default
        if self.widgets.get("newGroupEntry"):
            self.widgets["newGroupEntry"].set_visible(False)
            self.widgets["newGroupEntry"].hide()
        
        # Populate the unit dropdown if it exists
        if self.widgets.get("measurementUnitDropdown"):
            units = ["cm", "mm", "in", "px"]
            populate_dropdown(self.widgets["measurementUnitDropdown"], units)
        
        # Populate the group dropdown if it exists and parent_ui has a collection
        if self.widgets.get("groupDropdown") and hasattr(self.parent_ui, "collection"):
            groups = self.parent_ui.collection.get_groups()
            populate_dropdown(
                self.widgets["groupDropdown"], 
                ["-- Select Group --", "+ New Group"] + groups
            )
    
    def on_group_dropdown_changed(self, combo):
        """Handle group dropdown selection changes"""
        selected = get_widget_value(combo)
        logger.info(f"Group dropdown changed to: '{selected}'")
        
        # Show/hide the new group entry field based on selection
        if selected == "+ New Group" and self.widgets.get("newGroupEntry"):
            self.widgets["newGroupEntry"].set_visible(True)
            self.widgets["newGroupEntry"].show()
        elif self.widgets.get("newGroupEntry"):
            self.widgets["newGroupEntry"].set_visible(False)
            self.widgets["newGroupEntry"].hide()
    
    def set_measurement_value(self, value, unit="px"):
        """Set the measurement value in the UI"""
        if self.widgets.get("measurementValueLabel"):
            self.widgets["measurementValueLabel"].set_text(f"{value:.2f} {unit}")
    
    def on_save_clicked(self, button):
        """Handle save button click"""
        # Validate inputs using shared validation utilities
        name = get_widget_value(self.widgets.get("measurementNameEntry"))
        value_text = get_widget_value(self.widgets.get("measurementValueLabel"))
        
        validations = [
            validate_required_field(name, "Measurement name"),
            validate_required_field(value_text, "Measurement value")
        ]
        
        if not validate_and_show_errors(validations):
            return
        
        # Extract numeric value from text (format: "123.45 px")
        value_parts = value_text.split()
        if len(value_parts) >= 1:
            try:
                value = float(value_parts[0])
                unit = value_parts[1] if len(value_parts) > 1 else "px"
            except (ValueError, IndexError):
                show_message("Invalid measurement value format", Gtk.MessageType.ERROR)
                return
        
        # Get the selected group
        group = self.get_selected_group()
        
        # Create new measurement using the shared model
        new_measurement = Measurement(
            name=name,
            value=value,
            group=group,
            unit=unit
        )
        
        # Save to parent UI's collection if available
        if self.parent_ui and hasattr(self.parent_ui, "collection"):
            self.parent_ui.collection.add_measurement(new_measurement)
            
            # Save to file using shared file_io utility
            file_path = self.parent_ui.get_measurements_file_path()
            if save_json_data(self.parent_ui.collection.to_dict(), file_path, indent=2):
                show_message(f"Measurement '{name}' saved successfully", Gtk.MessageType.INFO)
                self.parent_ui.load_and_display_measurements()
                self.parent_ui.populate_group_dropdown()
                self.close_window()
            else:
                show_message("Failed to save measurement", Gtk.MessageType.ERROR)
        else:
            # Log warning if parent UI or collection not available
            logger.warning("Cannot save measurement: parent UI or collection not available")
            show_message("Cannot save measurement: integration error", Gtk.MessageType.WARNING)
    
    def get_selected_group(self):
        """Get the selected group or create a new one"""
        if not self.widgets.get("groupDropdown"):
            return "Default"
            
        selected = get_widget_value(self.widgets["groupDropdown"])
        
        if selected == "+ New Group":
            # Get text from new group entry
            new_group = get_widget_value(self.widgets.get("newGroupEntry"))
            if new_group:
                return new_group
            else:
                return "Default"
        elif selected and selected != "-- Select Group --":
            return selected
        else:
            return "Default"
    
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        self.close_window()
    
    def close_window(self):
        """Close the window"""
        # Find the window in the builder
        window = None
        for obj in self.builder.get_objects():
            if isinstance(obj, Gtk.Window):
                window = obj
                break
        
        if window:
            window.hide()
    
    def cleanup(self):
        """Clean up resources when the UI is being closed"""
        cleanup_resources(self)
        self.is_active = False
        logger.info("HarmonicMeasureUI resources cleaned up")


class HarmonicMeasureMode:
    """
    Class for handling the Harmonic Measure Mode functionality
    
    This mode allows users to measure directly on the canvas by:
    1. Clicking two points to measure a distance
    2. Converting the pixel measurement to physical units
    3. Showing a popup to save the measurement with additional info
    """
    
    def __init__(self, image, parent_ui=None):
        """
        Initialize the Harmonic Measure Mode
        
        Args:
            image: The GIMP image being edited
            parent_ui: Reference to the parent ProportiaUI for data sharing
        """
        self.image = image
        self.parent_ui = parent_ui
        self.active = False
        self.popup_ui = None
        self.is_active = True
        logger.info("Harmonic Measure Mode initialized")
    
    def start_measuring(self):
        """Start the harmonic measuring mode"""
        if self.active:
            logger.warning("Harmonic Measure Mode is already active")
            return False
            
        logger.info("Starting Harmonic Measure Mode...")
        self.active = True
        
        # Here we would register with GIMP tool system
        # For now, we'll just log that it's been activated
        
        return True
    
    def stop_measuring(self):
        """Stop the harmonic measuring mode"""
        if not self.active:
            logger.warning("Harmonic Measure Mode is not active")
            return False
            
        logger.info("Stopping Harmonic Measure Mode...")
        self.active = False
        
        # Here we would unregister from GIMP tool system
        # For now, we'll just log that it's been deactivated
        
        return True
    
    def show_measurement_popup(self, measurement_value, unit="px", parent_widget=None):
        """
        Show the measurement popup with the given value
        
        Args:
            measurement_value: The measured value to display
            unit: The unit of measurement
            parent_widget: The widget that triggered the popup
        
        Returns:
            True if popup was shown successfully, False otherwise
        """
        try:
            # Initialize popup window
            window, builder = initialize_popup_window(parent_widget)
            
            if not window or not builder:
                logger.error("Failed to initialize popup window")
                show_message("Failed to open measurement popup", Gtk.MessageType.ERROR)
                return False
            
            # Create UI handler
            self.popup_ui = HarmonicMeasureUI(builder, parent_widget, self.parent_ui)
            
            # Set the measurement value
            self.popup_ui.set_measurement_value(measurement_value, unit)
            
            return True
            
        except Exception as e:
            logger.error(f"Error showing measurement popup: {e}")
            show_message(f"Error: {str(e)}", Gtk.MessageType.ERROR)
            return False
    
    def cleanup(self):
        """Clean up resources when the mode is being closed"""
        if self.popup_ui:
            self.popup_ui.cleanup()
            
        self.is_active = False
        logger.info("HarmonicMeasureMode resources cleaned up")


def initialize_popup_window(parent_widget=None):
    """
    Initialize and show the proportiaPopup window when the Harmonic Measure button is clicked.
    
    Args:
        parent_widget: The parent widget that triggered the popup (usually the button)
        
    Returns:
        The popup window and builder objects for further interaction
    """
    try:
        # Log initialization
        logger.info("Initializing Harmonic Measure popup window...")
        
        # Get the path to the proportiaPopup.xml file using shared utility
        popup_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "../../ui/structure/proportiaPopup.xml"
        )
        
        # Check if the file exists
        if not os.path.exists(popup_path):
            error_message = f"Popup XML file not found at: {popup_path}"
            logger.error(error_message)
            show_message(error_message, Gtk.MessageType.ERROR)
            return None, None
        
        # Create a new GTK builder instance
        builder = Gtk.Builder()
        
        # Load the UI from XML file
        try:
            builder.add_from_file(popup_path)
        except Exception as e:
            error_message = f"Failed to load UI file: {e}"
            logger.error(error_message)
            show_message(error_message, Gtk.MessageType.ERROR)
            return None, None
        
        # Get the window object - find the first window in the builder objects
        window = None
        for obj in builder.get_objects():
            if isinstance(obj, Gtk.Window):
                window = obj
                break
        
        if not window:
            error_message = "Could not find any window in the UI file"
            logger.error(error_message)
            show_message(error_message, Gtk.MessageType.ERROR)
            return None, None
        
        # Position the window relative to the parent if provided
        if parent_widget:
            parent_window = parent_widget.get_toplevel()
            if parent_window and isinstance(parent_window, Gtk.Window):
                window.set_transient_for(parent_window)
                
                # Position near the mouse cursor
                display = parent_window.get_display()
                if display:
                    seat = display.get_default_seat()
                    if seat:
                        pointer = seat.get_pointer()
                        screen, x, y = pointer.get_position()
                        window.move(x + 10, y + 10)  # Offset a bit from cursor
        
        # Show the window
        window.show_all()
        
        # Find and hide the newGroupEntry by default (if it exists)
        new_group_entry = builder.get_object("newGroupEntry")
        if new_group_entry:
            new_group_entry.hide()
        
        logger.info("Harmonic Measure popup window initialized successfully")
        return window, builder
        
    except Exception as e:
        error_message = f"Error initializing popup window: {e}"
        logger.error(error_message)
        show_message(error_message, Gtk.MessageType.ERROR)
        return None, None
