import logging
from typing import Tuple, Optional
import os

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk, GLib

# Import our utility functions
from core.utils.tools.structure.structure_utilities import scale_by_sqrt2

# Set up logging
logger = logging.getLogger("proportia")

class ProportiaCalculator:
    """Handles measurement calculations using √2 scaling"""
    
    def calculate_scaled_measurement(self, 
                                    input_value: str, 
                                    unit: str = "cm") -> Tuple[Optional[float], str]:
        """
        Calculate scaled measurement using √2
        
        Args:
            input_value: The input value as string
            unit: The unit string (cm, in, px)
            
        Returns:
            Tuple of (calculated_value, formatted_string)
        """
        # Input validation
        try:
            value = float(input_value)
            if value < 0:
                return None, f"Value must be positive"
        except (ValueError, TypeError):
            return None, f"Invalid input: {input_value}"
            
        # Calculate result using the utility function
        result = scale_by_sqrt2(value)
        
        # Format with 2 decimal places and add unit
        formatted_result = f"{result:.2f} {unit}"
        
        return result, formatted_result

class ProportiaUI:
    """Handles Proportia UI interactions for measurement conversion"""
    
    def __init__(self, builder):
        """Initialize UI with GTK builder"""
        self.calculator = ProportiaCalculator()
        self.builder = builder
        
        # Get relevant widgets
        self.unit_dropdown = self.builder.get_object("unitDropdown")
        self.measurement_input = self.builder.get_object("measurementValueEntry")
        self.calculate_button = self.builder.get_object("addMeasurementButton")
        self.result_display = self.builder.get_object("generatedDimension")
        
        # Connect other signals
        self.calculate_button.connect("clicked", self.on_calculate_clicked)
        self.measurement_input.connect("activate", self.on_calculate_clicked)
        
        # Set default unit
        if self.unit_dropdown.get_active() == -1:
            self.unit_dropdown.set_active(0)
        
        # Get widgets
        self.group_dropdown = builder.get_object("groupDropdownSidebar")
        self.new_group_entry = builder.get_object("newGroupName")
        
        # IMPORTANT: Force visibility even if XML failed
        self.new_group_entry.set_visible(False)
        self.new_group_entry.hide()  # Use both methods for safety
        
        # Connect to the changed signal
        self.group_dropdown.connect("changed", self.on_group_dropdown_changed)
        
        # Schedule a verification check after UI is fully rendered
        GLib.idle_add(self.verify_entry_visibility)
    
    def verify_entry_visibility(self):
        """Force verify the entry visibility after UI is loaded"""
        print("Verifying entry visibility...")
        # Double-check that entry is hidden
        self.new_group_entry.set_visible(False)
        self.new_group_entry.hide()
        return False  # Don't repeat
    
    def on_group_dropdown_changed(self, combo):
        """Handle dropdown changes"""
        selected = combo.get_active_text()
        print(f"Dropdown changed to: '{selected}'")
        
        if selected == "+ New Group":
            self.new_group_entry.set_visible(True)
            self.new_group_entry.show()
        else:
            self.new_group_entry.set_visible(False)
            self.new_group_entry.hide()
    
    def get_selected_unit(self) -> str:
        """Get the selected unit from dropdown"""
        active_index = self.unit_dropdown.get_active()
        if active_index != -1:
            return self.unit_dropdown.get_model()[active_index][0]
        return "cm"  # Default fallback
        
    def on_calculate_clicked(self, widget):
        """Handle calculation button click or Enter key"""
        # Get input value
        input_value = self.measurement_input.get_text().strip()
        
        # Basic validation
        if not input_value:
            self.result_display.set_text("Enter a value first")
            self.measurement_input.grab_focus()
            return
            
        # Get selected unit
        unit = self.get_selected_unit()
        
        # Calculate scaled measurement
        _, formatted_result = self.calculator.calculate_scaled_measurement(input_value, unit)
        
        # Display result
        self.result_display.set_text(formatted_result)

# Load the UI
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "ui", "structure", "structure_notebook.xml")

# For debugging - print the path and check if file exists
print(f"UI path: {ui_path}")
print(f"File exists: {os.path.exists(ui_path)}")

builder = Gtk.Builder()
builder.add_from_file(ui_path)

# Create the UI instance
proportia_ui = ProportiaUI(builder)
