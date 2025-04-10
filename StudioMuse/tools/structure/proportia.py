import logging
from typing import Tuple, Optional, List, Dict, Any
import os

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gimp, Gtk, GLib, Gdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proportia")

# Import our utility functions
from core.utils.tools.structure.structure_utilities import (
    scale_by_sqrt2, 
    load_measurements_from_file,
    save_data_to_json,
    load_json_data,
    group_measurements,
    get_unique_groups,
    load_css_for_proportia,
    apply_css_class
)

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
        # Initialize CSS first, before creating widgets
        css_loaded = load_css_for_proportia()
        logger.info(f"CSS loading result: {css_loaded}")
        
        self.calculator = ProportiaCalculator()
        self.builder = builder
        
        # Get relevant widgets
        self.unit_dropdown = self.builder.get_object("unitDropdown")
        self.measurement_input = self.builder.get_object("measurementValueEntry")
        self.calculate_button = self.builder.get_object("addMeasurementButton")
        self.result_display = self.builder.get_object("generatedDimension")
        self.measurement_name_entry = self.builder.get_object("measurementNameEntry")
        self.save_dimension_button = self.builder.get_object("saveDimensionButton")
        
        # Connect other signals
        self.calculate_button.connect("clicked", self.on_calculate_clicked)
        self.measurement_input.connect("activate", self.on_calculate_clicked)
        self.save_dimension_button.connect("clicked", self.on_save_dimension_clicked)
        
        # Set default unit
        if self.unit_dropdown.get_active() == -1:
            self.unit_dropdown.set_active(0)
        
        # Get widgets
        self.group_dropdown = builder.get_object("groupDropdownSidebar")
        self.new_group_entry = builder.get_object("newGroupName")
        
        # Measurement display box (renamed from measurementGroupBox in XML)
        self.measurement_group_box = builder.get_object("measurementGroupBox")
        
        # IMPORTANT: Force visibility even if XML failed
        self.new_group_entry.set_visible(False)
        self.new_group_entry.hide()  # Use both methods for safety
        
        # Connect to the changed signal
        self.group_dropdown.connect("changed", self.on_group_dropdown_changed)
        
        # Store current measurements for easier access and updates
        self.current_measurements = []
        
        # Schedule a verification check after UI is fully rendered
        GLib.idle_add(self.verify_entry_visibility)
        
        # Load and display saved measurements
        GLib.idle_add(self.load_and_display_measurements)
        
        # Populate group dropdown with existing groups
        GLib.idle_add(self.populate_group_dropdown)
    
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

    def get_measurements_file_path(self) -> str:
        """Get the path to the measurements file"""
        # For testing, use the saved_dimensions.json from the example
        # In production, this would use a path from Gimp.directory()
        return os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "docs", 
            "proportiaExampleProject", 
            "saved_dimensions.json"
        )
    
    def populate_group_dropdown(self):
        """Populate the group dropdown with existing groups"""
        # Clear current items except the first two (default and + New Group)
        model = self.group_dropdown.get_model()
        if model is not None:
            while len(model) > 2:
                model.remove(len(model) - 1)  # Remove the last item
        
        # Get groups from current measurements
        groups = get_unique_groups(self.current_measurements)
        
        # Add groups to dropdown
        for group in groups:
            self.group_dropdown.append_text(group)
        
        # Set active item to the first one
        if self.group_dropdown.get_active() == -1:
            self.group_dropdown.set_active(0)
    
    def load_and_display_measurements(self) -> None:
        """Load measurements from JSON file and display them in the UI"""
        # Clear existing content
        for child in self.measurement_group_box.get_children():
            self.measurement_group_box.remove(child)
        
        # Load measurements using the utility function
        file_path = self.get_measurements_file_path()
        self.current_measurements = load_measurements_from_file(file_path)
        
        if not self.current_measurements:
            # Display message when no measurements are found
            label = Gtk.Label(label="No saved measurements found")
            label.set_halign(Gtk.Align.START)
            label.set_margin_top(10)
            label.show()
            self.measurement_group_box.add(label)
            return
        
        # Group measurements using the utility function
        grouped_measurements = group_measurements(self.current_measurements)
        
        # Display each group
        for group_name, items in grouped_measurements.items():
            self.create_group_ui(group_name, items)
        
        # Show all widgets
        self.measurement_group_box.show_all()
    
    def on_save_dimension_clicked(self, button):
        """Handle save dimension button click"""
        # Get the dimension name and value
        name = self.measurement_name_entry.get_text().strip()
        value_text = self.result_display.get_text().strip()
        
        # Validate inputs
        if not name:
            self.show_message_dialog("Please enter a dimension name", Gtk.MessageType.WARNING)
            self.measurement_name_entry.grab_focus()
            return
        
        if not value_text:
            self.show_message_dialog("Please calculate a measurement first", Gtk.MessageType.WARNING)
            self.measurement_input.grab_focus()
            return
        
        # Parse the value (format is like "10.50 cm")
        try:
            value = float(value_text.split()[0])
        except (ValueError, IndexError):
            self.show_message_dialog("Invalid measurement value", Gtk.MessageType.ERROR)
            return
        
        # Get the group
        group = self.get_selected_group()
        
        # Create the new measurement
        new_measurement = {
            'name': name,
            'value': value,
            'group': group,
            'unit': self.get_selected_unit()
        }
        
        # Add to current measurements
        self.current_measurements.append(new_measurement)
        
        # Save to file
        file_path = self.get_measurements_file_path()
        if save_data_to_json(self.current_measurements, file_path):
            # Show success message
            self.show_message_dialog(f"Measurement '{name}' saved successfully", Gtk.MessageType.INFO)
            
            # Clear input fields
            self.measurement_name_entry.set_text("")
            self.measurement_input.set_text("")
            self.result_display.set_text("")
            
            # Refresh the display
            self.load_and_display_measurements()
            self.populate_group_dropdown()
        else:
            self.show_message_dialog("Failed to save measurement", Gtk.MessageType.ERROR)
    
    def get_selected_group(self) -> str:
        """Get the selected group or create a new one"""
        selected = self.group_dropdown.get_active_text()
        
        if selected == "+ New Group":
            # Get text from new group entry
            new_group = self.new_group_entry.get_text().strip()
            if new_group:
                return new_group
            else:
                return "Default"
        elif selected and selected != "-- Select Group --":
            return selected
        else:
            return "Default"
    
    def show_message_dialog(self, message: str, message_type: Gtk.MessageType = Gtk.MessageType.INFO):
        """Show a message dialog with the given message"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    def create_group_ui(self, group_name: str, measurements: List[Dict[str, Any]]) -> None:
        """Create UI elements for a measurement group with improved styling"""
        # Create main container for the group
        # We don't use a frame directly, as we want more control over the styling
        group_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_container.set_margin_bottom(12)
        
        # Create header with styled appearance
        header = Gtk.Button()
        header.set_relief(Gtk.ReliefStyle.NONE)
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_spacing(8)
        
        # Add expand/collapse icon
        expander = Gtk.Expander()
        expander.set_expanded(True)  # Start expanded
        expander.set_label("")  # Empty label since we manage the header separately
        
        # Create and style the header label
        header_label = Gtk.Label(label=group_name)
        header_label.set_halign(Gtk.Align.START)
        header_label.set_hexpand(True)
        header_box.pack_start(header_label, True, True, 0)
        
        # Add an icon to indicate expandable group
        arrow_icon = Gtk.Image.new_from_icon_name("pan-down-symbolic", Gtk.IconSize.MENU)
        header_box.pack_end(arrow_icon, False, False, 0)
        
        header.add(header_box)
        apply_css_class(header, "group-header")
        
        # Connect toggle for expansion
        header.connect("clicked", self.on_group_header_clicked, expander)
        
        # Add header to the container
        group_container.pack_start(header, False, False, 0)
        
        # Create content box for measurements with styling
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_margin_start(0)
        content_box.set_margin_end(0)
        content_box.set_margin_top(0)
        content_box.set_margin_bottom(0)
        apply_css_class(content_box, "group-content")
        
        # Link the expander to the content
        expander.add(content_box)
        group_container.pack_start(expander, False, False, 0)
        
        # Add measurements to content box
        for i, measurement in enumerate(measurements):
            measurement_box = self.create_measurement_item_ui(measurement)
            # If this is the last item, add a special class for proper border-radius
            if i == len(measurements) - 1:
                measurement_box.get_style_context().add_class("last-item")
            content_box.add(measurement_box)
        
        # Add group to main container
        self.measurement_group_box.add(group_container)
    
    def on_group_header_clicked(self, button, expander):
        """Toggle the expander when the header is clicked"""
        expanded = expander.get_expanded()
        expander.set_expanded(not expanded)
    
    def create_measurement_item_ui(self, measurement: Dict[str, Any]) -> Gtk.Box:
        """Create UI for a single measurement item with improved styling"""
        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item_box.set_margin_top(0)
        item_box.set_margin_bottom(0)
        apply_css_class(item_box, "measurement-item")
        
        # Add name with styling
        name_label = Gtk.Label(label=measurement['name'])
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        apply_css_class(name_label, "measurement-name")
        item_box.pack_start(name_label, True, True, 5)
        
        # Add value with unit and styling
        unit = measurement.get('unit', 'cm')
        value_text = f"{measurement['value']:.2f} {unit}"
        value_label = Gtk.Label(label=value_text)
        value_label.set_halign(Gtk.Align.END)
        apply_css_class(value_label, "measurement-value")
        
        # Create a button box for the actions with minimal spacing
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(2)
        
        # Add edit button with tooltip
        edit_button = Gtk.Button()
        edit_button.set_relief(Gtk.ReliefStyle.NONE)
        edit_button.set_tooltip_text(f"Edit {measurement['name']}")
        edit_icon = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        edit_button.add(edit_icon)
        edit_button.connect("clicked", self.on_edit_measurement, measurement)
        
        # Add delete button with tooltip
        delete_button = Gtk.Button()
        delete_button.set_relief(Gtk.ReliefStyle.NONE)
        delete_button.set_tooltip_text(f"Delete {measurement['name']}")
        delete_icon = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        delete_button.add(delete_icon)
        delete_button.connect("clicked", self.on_delete_measurement, measurement)
        
        # Pack buttons
        button_box.pack_start(edit_button, False, False, 0)
        button_box.pack_start(delete_button, False, False, 0)
        
        # Pack the value and buttons
        item_box.pack_end(button_box, False, False, 5)
        item_box.pack_end(value_label, False, False, 5)
        
        return item_box
    
    def on_edit_measurement(self, button, measurement):
        """Handle edit button click"""
        # This would open a dialog to edit the measurement
        # For now, just log it
        logger.info(f"Editing measurement: {measurement['name']}")
        
        # Future implementation would have a dialog here
    
    def on_delete_measurement(self, button, measurement):
        """Handle delete button click"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete measurement '{measurement['name']}'?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            for i, m in enumerate(self.current_measurements):
                if m.get('name') == measurement['name'] and m.get('value') == measurement['value']:
                    del self.current_measurements[i]
                    break
            
            file_path = self.get_measurements_file_path()
            if save_data_to_json(self.current_measurements, file_path):
                self.load_and_display_measurements()
                self.populate_group_dropdown()
            else:
                self.show_message_dialog("Failed to save changes", Gtk.MessageType.ERROR)

script_dir = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "ui", "structure", "structure_notebook.xml")

# For debugging - print the path and check if file exists
print(f"UI path: {ui_path}")
print(f"File exists: {os.path.exists(ui_path)}")

builder = Gtk.Builder()
builder.add_from_file(ui_path)

# Create the UI instance
proportia_ui = ProportiaUI(builder)
