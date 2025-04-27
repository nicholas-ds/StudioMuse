import logging
import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk, GLib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("harmonic_measure")

from core.utils.ui import DialogBuilder, show_message, connect_signals, collect_widgets, get_widget_value

from core.models.measurement_models import Measurement

class HarmonicMeasureUI:
    """Handles the Harmonic Measure mode UI interactions"""
    
    def __init__(self, builder, popup_window, parent_widget=None, proportia_ui=None):
        """Initialize the Harmonic Measure UI handler"""
        self.builder = builder
        self.window = popup_window
        self.parent_widget = parent_widget
        self.proportia_ui = proportia_ui
        
        self.parent_window = parent_widget.get_toplevel() if parent_widget else None
        if self.parent_window and isinstance(self.parent_window, Gtk.Window):
            self.window.set_transient_for(self.parent_window)
            self.parent_window.hide()
            # Connect window destroy signal
            self.window.connect("destroy", lambda w: self.parent_window.show())
        
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
        
        self.init_ui()
        self.connect_signals()
        
        logger.info("HarmonicMeasureUI initialized")
    
    def init_ui(self):
        """Initialize the UI state"""

        units = ["px", "cm", "in"]
        for unit in units:
            self.widgets["measurementUnitDropdown"].append_text(unit)
        self.widgets["measurementUnitDropdown"].set_active(0)
        
        dropdown = self.widgets["groupDropdown"]
        dropdown.remove_all()
        
        # Add default items
        dropdown.append_text("-- Choose a Group -- ")
        dropdown.append_text("++ Add New Group")
        
        if self.proportia_ui:
            groups = self.proportia_ui.collection.get_groups()
            for group in groups:
                dropdown.append_text(group)
        
        dropdown.set_active(0)
    
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
        self.widgets["newGroupEntry"].set_visible(selected == "++ Add New Group")
    
    def on_save_clicked(self, button):
        """Handle save button click"""
        name = get_widget_value(self.widgets["measurementNameEntry"])
        value_text = get_widget_value(self.widgets["measurementValueLabel"])
        
        if not name:
            show_message("Please enter a measurement name", Gtk.MessageType.WARNING)
            return
        
        try:
            value_parts = value_text.split()
            value = float(value_parts[0])
            unit = self.widgets["measurementUnitDropdown"].get_active_text()
        except (ValueError, IndexError):
            show_message("Invalid measurement value", Gtk.MessageType.ERROR)
            return
        
        selected_group = get_widget_value(self.widgets["groupDropdown"])
        group = self.get_group_name(selected_group)
        
        measurement = Measurement(name=name, value=value, group=group, unit=unit)
        
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
        if not self.proportia_ui:
            show_message(f"Measurement '{measurement.name}' created successfully", Gtk.MessageType.INFO)
            return True
        
        self.proportia_ui.collection.add_measurement(measurement)
        
        file_path = self.proportia_ui.get_measurements_file_path()
        from core.utils.file_io import save_json_data
        
        if save_json_data(self.proportia_ui.collection.to_dict(), file_path, indent=2):
            show_message(f"Measurement '{measurement.name}' saved successfully", Gtk.MessageType.INFO)
            
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
