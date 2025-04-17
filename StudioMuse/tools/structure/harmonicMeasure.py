import logging
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("harmonic_measure")

# Import shared UI utilities
from core.utils.ui import show_message, connect_signals, collect_widgets, get_widget_value

# Import measurement models
from core.models.measurement_models import Measurement

class HarmonicMeasureUI:
    """Handles the Harmonic Measure mode UI interactions"""
    
    def __init__(self, builder, popup_window, parent_widget=None, proportia_ui=None):
        """Initialize the Harmonic Measure UI handler"""
        self.builder = builder
        self.window = popup_window
        self.parent_widget = parent_widget
        self.proportia_ui = proportia_ui
        
        # Collect essential widgets
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
        
        # Initialize UI state
        self.init_ui()
        
        # Connect event handlers
        self.connect_signals()
        
        logger.info("HarmonicMeasureUI initialized")
    
    def init_ui(self):
        """Initialize the UI state"""
        # Hide new group entry by default
        self.widgets["newGroupEntry"].set_visible(False)
        
        # Populate unit dropdown
        units = ["px", "cm", "in"]
        for unit in units:
            self.widgets["measurementUnitDropdown"].append_text(unit)
        
        # Set active unit
        self.widgets["measurementUnitDropdown"].set_active(0)
    
    def connect_signals(self):
        """Connect signal handlers"""
        custom_handlers = {
            "groupDropdown": [("changed", self.on_group_dropdown_changed)],
            "saveButton": [("clicked", self.on_save_clicked)],
            "cancelButton": [("clicked", self.on_cancel_clicked)]
        }
        
        connect_signals(self.builder, self, custom_handlers)
    
    def on_group_dropdown_changed(self, combo):
        """Handle group dropdown selection change"""
        selected = get_widget_value(combo)
        
        # Toggle new group entry visibility
        self.widgets["newGroupEntry"].set_visible(selected == "++ Add New Group")
    
    def on_save_clicked(self, button):
        """Handle save button click"""
        # Get basic values
        name = get_widget_value(self.widgets["measurementNameEntry"])
        value_text = get_widget_value(self.widgets["measurementValueLabel"])
        
        # Validate name
        if not name:
            show_message("Please enter a measurement name", Gtk.MessageType.WARNING)
            return
        
        # Parse value
        try:
            value_parts = value_text.split()
            value = float(value_parts[0])
            unit = self.widgets["measurementUnitDropdown"].get_active_text()
        except (ValueError, IndexError):
            show_message("Invalid measurement value", Gtk.MessageType.ERROR)
            return
        
        # Get group
        selected_group = get_widget_value(self.widgets["groupDropdown"])
        group = self.get_group_name(selected_group)
        
        # Create measurement
        measurement = Measurement(name=name, value=value, group=group, unit=unit)
        
        # Save measurement via proportia_ui
        if self.save_measurement(measurement):
            self.window.destroy()
    
    def get_group_name(self, selected_group):
        """Determine the actual group name from selection"""
        if selected_group == "++ Add New Group":
            new_group = get_widget_value(self.widgets["newGroupEntry"])
            if not new_group:
                show_message("Please enter a group name", Gtk.MessageType.WARNING)
                return None
            return new_group
        elif selected_group == "-- Choose a Group -- ":
            return "Default"
        return selected_group
    
    def save_measurement(self, measurement):
        """Save the measurement via proportia_ui if available"""
        if not self.proportia_ui or not hasattr(self.proportia_ui, 'collection'):
            show_message(f"Measurement '{measurement.name}' created successfully", Gtk.MessageType.INFO)
            return True
        
        # Add to collection
        self.proportia_ui.collection.add_measurement(measurement)
        
        # Save to file
        file_path = self.proportia_ui.get_measurements_file_path()
        from core.utils.file_io import save_json_data
        
        if save_json_data(self.proportia_ui.collection.to_dict(), file_path, indent=2):
            show_message(f"Measurement '{measurement.name}' saved successfully", Gtk.MessageType.INFO)
            
            # Refresh proportia UI
            if hasattr(self.proportia_ui, 'load_and_display_measurements'):
                self.proportia_ui.load_and_display_measurements()
            
            if hasattr(self.proportia_ui, 'populate_group_dropdown'):
                self.proportia_ui.populate_group_dropdown()
            
            return True
        else:
            show_message("Failed to save measurement", Gtk.MessageType.ERROR)
            return False
    
    def on_cancel_clicked(self, button):
        """Handle cancel button click"""
        self.window.destroy()
