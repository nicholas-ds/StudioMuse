import logging
import os
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("harmonic_measure")

# Import shared UI utilities
from core.utils.ui import DialogBuilder, show_message, connect_signals, collect_widgets, get_widget_value

# Import measurement models
from core.models.measurement_models import Measurement, MeasurementCollection

class HarmonicMeasureUI:
    """Handles the Harmonic Measure mode UI interactions"""
    
    def __init__(self, builder, popup_window, parent_widget, proportia_ui=None):
        """
        Initialize the Harmonic Measure UI handler
        
        Args:
            builder: Gtk.Builder instance with loaded UI
            popup_window: The dialog window
            parent_widget: Widget that triggered the popup
            proportia_ui: Optional reference to parent ProportiaUI instance
        """
        self.builder = builder
        self.window = popup_window
        self.parent_widget = parent_widget
        self.proportia_ui = proportia_ui
        
        # Collect widgets from the builder
        widget_ids = [
            "measurementNameEntry",
            "groupDropdown",
            "newGroupEntry",
            "measurementValueLabel",
            "measurementUnitDropdown",
            "saveButton",
            "cancelButton"
        ]
        
        self.widgets = collect_widgets(builder, widget_ids)
        
        # Set initial state
        self.widgets["newGroupEntry"].set_visible(False)
        
        # Connect signal handlers
        custom_handlers = {
            "groupDropdown": [("changed", self.on_group_dropdown_changed)],
            "saveButton": [("clicked", self.on_save_clicked)],
            "cancelButton": [("clicked", self.on_cancel_clicked)]
        }
        
        connect_signals(self.builder, self, custom_handlers)
        
        # Populate the unit dropdown
        units = ["px", "cm", "in"]
        for unit in units:
            self.widgets["measurementUnitDropdown"].append_text(unit)
        
        # Set active item to first one
        self.widgets["measurementUnitDropdown"].set_active(0)
        
        logger.info("HarmonicMeasureUI initialized")
    
    def on_group_dropdown_changed(self, combo):
        """Handle group dropdown selection change"""
        selected = get_widget_value(combo)
        
        # If "Add New Group" is selected, show the new group entry
        if selected == "++ Add New Group":
            self.widgets["newGroupEntry"].set_visible(True)
            self.widgets["newGroupEntry"].show()
        else:
            self.widgets["newGroupEntry"].set_visible(False)
            self.widgets["newGroupEntry"].hide()
    
    def on_save_clicked(self, button):
        """Handle save button click"""
        # Get values from widgets
        name = get_widget_value(self.widgets["measurementNameEntry"])
        value_text = get_widget_value(self.widgets["measurementValueLabel"])
        
        # Basic validation
        if not name:
            show_message("Please enter a measurement name", Gtk.MessageType.WARNING)
            return
        
        # Process the value (assuming format like "0.00 px")
        try:
            value_parts = value_text.split()
            value = float(value_parts[0])
            unit = self.widgets["measurementUnitDropdown"].get_active_text()
        except (ValueError, IndexError):
            show_message("Invalid measurement value", Gtk.MessageType.ERROR)
            return
        
        # Get the group
        selected_group = get_widget_value(self.widgets["groupDropdown"])
        
        if selected_group == "++ Add New Group":
            group = get_widget_value(self.widgets["newGroupEntry"])
            if not group:
                show_message("Please enter a group name", Gtk.MessageType.WARNING)
                return
        elif selected_group == "-- Choose a Group -- ":
            group = "Default"
        else:
            group = selected_group
        
        # Create a new measurement
        measurement = Measurement(
            name=name,
            value=value,
            group=group,
            unit=unit
        )
        
        # If proportia_ui is available, add to its collection
        if self.proportia_ui and hasattr(self.proportia_ui, 'collection'):
            self.proportia_ui.collection.add_measurement(measurement)
            
            # Save to file
            file_path = self.proportia_ui.get_measurements_file_path()
            from core.utils.file_io import save_json_data
            
            if save_json_data(self.proportia_ui.collection.to_dict(), file_path, indent=2):
                show_message(f"Measurement '{name}' saved successfully", Gtk.MessageType.INFO)
                
                # Close the popup
                self.window.destroy()
                
                # Refresh proportia UI if available
                if hasattr(self.proportia_ui, 'load_and_display_measurements'):
                    self.proportia_ui.load_and_display_measurements()
                    
                if hasattr(self.proportia_ui, 'populate_group_dropdown'):
                    self.proportia_ui.populate_group_dropdown()
            else:
                show_message("Failed to save measurement", Gtk.MessageType.ERROR)
        else:
            # Just show success and close
            show_message(f"Measurement '{name}' created successfully", Gtk.MessageType.INFO)
            self.window.destroy()
    
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        self.window.destroy()

def initialize_popup_window(parent_widget=None):
    """
    Create and display the measurement popup window
    
    Args:
        parent_widget: Widget that triggered the popup (usually the button)
        
    Returns:
        The popup window and builder objects for further interaction
    """
    try:
        # Get parent window if applicable
        parent_window = None
        if parent_widget:
            parent_window = parent_widget.get_toplevel()
            if not isinstance(parent_window, Gtk.Window):
                parent_window = None
        
        # Get path to dialog XML
        popup_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "../../ui/structure/proportiaPopup.xml"
        )
        
        # Use the DialogBuilder to create the dialog
        dialog, builder = DialogBuilder.create_from_file(popup_path, parent_window)
        
        if not dialog or not builder:
            logger.error("Failed to create dialog")
            return None, None
            
        # Make sure dialog is properly displayed
        dialog.set_keep_above(True)  # Keep above other windows
        dialog.present()  # Bring to foreground
        dialog.show_all()  # Ensure all widgets are visible
        
        # Connect basic signals (just the Close button)
        close_button = None
        for obj in builder.get_objects():
            if isinstance(obj, Gtk.Button):
                label = obj.get_label()
                if label == "Close" or label == "Cancel":
                    close_button = obj
                    obj.connect("clicked", lambda btn: dialog.destroy())
        
        # Process pending events to make dialog visible immediately
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
            
        logger.info("Dialog shown successfully")
        return dialog, builder
        
    except Exception as e:
        logger.error(f"Error in initialize_popup_window: {e}")
        return None, None

# For backward compatibility
def show_measurement_popup(measurement_value=0.0, unit="px", parent_widget=None):
    """Simplified wrapper for initialize_popup_window"""
    return initialize_popup_window(parent_widget)
