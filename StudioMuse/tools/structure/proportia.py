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
    group_measurements,
    get_unique_groups,
    apply_css_class
)

# Import new file I/O utilities
from core.utils.file_io import (
    get_plugin_storage_path,
    save_json_data,
    load_json_data,
    normalize_measurement_data
)

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

# Import measurement models
from core.models.measurement_models import Measurement, MeasurementCollection

# Import validation utilities
from core.utils.validation import validate_required_field, validate_numeric, validate_and_show_errors

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
        # Initialize CSS using the shared utility
        css_path = os.path.join(os.path.dirname(__file__), "../../ui/structure/proportia.css")
        
        # Define fallback CSS in case the file doesn't exist
        fallback_css = """
        .group-header { 
            background-color: #e0e0e0; 
            padding: 8px; 
            border-radius: 4px 4px 0 0;
        }
        .group-content { 
            background-color: #f5f5f5; 
            border-radius: 0 0 4px 4px;
        }
        .measurement-item { 
            border-bottom: 1px solid #ddd; 
            padding: 5px;
        }
        .measurement-name { font-weight: bold; }
        .measurement-value { color: #333; }
        .measurement-name-edit { 
            background-color: #fff;
            border: 1px solid #3584e4;
            border-radius: 3px;
            padding: 2px 5px;
        }
        """
        
        css_loaded = load_css_for_plugin(css_path, fallback_css)
        logger.info(f"CSS loading result: {css_loaded}")
        
        self.calculator = ProportiaCalculator()
        self.builder = builder
        
        # Use collect_widgets to get all UI elements
        widget_ids = [
            "unitDropdown",
            "measurementValueEntry",
            "addMeasurementButton",
            "generatedDimension",
            "measurementNameEntry",
            "saveDimensionButton",
            "groupDropdownSidebar",
            "newGroupName",
            "measurementGroupBox"
        ]
        self.widgets = collect_widgets(builder, widget_ids)
        
        # Set default unit
        if self.widgets["unitDropdown"].get_active() == -1:
            self.widgets["unitDropdown"].set_active(0)
        
        # IMPORTANT: Force visibility even if XML failed
        self.widgets["newGroupName"].set_visible(False)
        self.widgets["newGroupName"].hide()
        
        # Store current measurements for easier access and updates
        self.current_measurements = []
        
        # Schedule initialization tasks
        GLib.idle_add(self.verify_entry_visibility)
        GLib.idle_add(self.load_and_display_measurements)
        GLib.idle_add(self.populate_group_dropdown)
        
        # Connect signals using shared utility
        custom_handlers = {
            "addMeasurementButton": [("clicked", self.on_calculate_clicked)],
            "measurementValueEntry": [("activate", self.on_calculate_clicked)],
            "saveDimensionButton": [("clicked", self.on_save_dimension_clicked)],
            "groupDropdownSidebar": [("changed", self.on_group_dropdown_changed)]
        }
        connect_signals(self.builder, self, custom_handlers)
    
    def verify_entry_visibility(self):
        """Force verify the entry visibility after UI is loaded"""
        print("Verifying entry visibility...")
        # Double-check that entry is hidden
        self.widgets["newGroupName"].set_visible(False)
        self.widgets["newGroupName"].hide()
        return False  # Don't repeat
    
    def on_group_dropdown_changed(self, combo):
        """Handle dropdown changes"""
        selected = get_widget_value(combo)
        print(f"Dropdown changed to: '{selected}'")
        
        if selected == "+ New Group":
            self.widgets["newGroupName"].set_visible(True)
            self.widgets["newGroupName"].show()
        else:
            self.widgets["newGroupName"].set_visible(False)
            self.widgets["newGroupName"].hide()
    
    def get_selected_unit(self) -> str:
        """Get the selected unit from dropdown"""
        return get_widget_value(self.widgets["unitDropdown"]) or "cm"
        
    def on_calculate_clicked(self, widget):
        """Handle calculation button click or Enter key"""
        # Get input value using shared utility
        input_value = get_widget_value(self.widgets["measurementValueEntry"])
        
        # Basic validation
        if not input_value:
            self.widgets["generatedDimension"].set_text("Enter a value first")
            self.widgets["measurementValueEntry"].grab_focus()
            return
            
        # Get selected unit
        unit = self.get_selected_unit()
        
        # Calculate scaled measurement
        _, formatted_result = self.calculator.calculate_scaled_measurement(input_value, unit)
        
        # Display result
        self.widgets["generatedDimension"].set_text(formatted_result)

    def get_measurements_file_path(self) -> str:
        """Get the path to the measurements file"""
        # Match the actual installed path structure
        file_path = get_plugin_storage_path("data/tools/structure/saved_dimensions.json", "studiomuse")
        
        # Add debugging output
        logger.info(f"Measurements file path: {file_path}")
        logger.info(f"File exists: {os.path.exists(file_path)}")
        
        return file_path
    
    def populate_group_dropdown(self):
        """Populate the group dropdown with existing groups"""
        dropdown = self.widgets["groupDropdownSidebar"]
        
        # Clear current items except the first two (default and + New Group)
        model = dropdown.get_model()
        if model is not None:
            while len(model) > 2:
                model.remove(len(model) - 1)  # Remove the last item
        
        # Get groups directly from the collection
        groups = self.collection.get_groups()
        
        # Add groups to dropdown
        for group in groups:
            dropdown.append_text(group)
        
        # Set active item to the first one
        if dropdown.get_active() == -1:
            dropdown.set_active(0)
    
    def load_and_display_measurements(self) -> None:
        """Load measurements from JSON file and display them in the UI"""
        # Clear existing content
        for child in self.widgets["measurementGroupBox"].get_children():
            self.widgets["measurementGroupBox"].remove(child)
        
        # Load measurements using the file_io utilities and convert to MeasurementCollection
        file_path = self.get_measurements_file_path()
        raw_data = load_json_data(file_path, default=[])
        
        # Convert to structured model
        self.collection = MeasurementCollection.from_dict(raw_data)
        self.current_measurements = self.collection.measurements
        
        if not self.current_measurements:
            # Display message when no measurements are found
            label = Gtk.Label(label="No saved measurements found")
            label.set_halign(Gtk.Align.START)
            label.set_margin_top(10)
            label.show()
            self.widgets["measurementGroupBox"].add(label)
            return
        
        # Get grouped measurements using the collection's method
        grouped_measurements = {}
        for group in self.collection.get_groups():
            grouped_measurements[group] = self.collection.get_measurements_by_group(group)
        
        # Display each group
        for group_name, items in grouped_measurements.items():
            self.create_group_ui(group_name, items)
        
        # Show all widgets
        self.widgets["measurementGroupBox"].show_all()
    
    def on_save_dimension_clicked(self, button):
        """Handle save dimension button click"""
        # Get values
        name = get_widget_value(self.widgets["measurementNameEntry"])
        value_text = get_widget_value(self.widgets["generatedDimension"])
        
        # Validate inputs using the shared validation utilities
        validations = [
            validate_required_field(name, "Dimension name"),
            validate_required_field(value_text, "Measurement value")
        ]
        
        if not validate_and_show_errors(validations):
            return
        
        # Validate numeric value
        is_valid, error_message, value = validate_numeric(
            value_text.split()[0] if ' ' in value_text else value_text,
            "Measurement value",
            min_value=0
        )
        
        if not is_valid:
            show_message(error_message, Gtk.MessageType.WARNING)
            return
        
        # Get the group
        group = self.get_selected_group()
        unit = self.get_selected_unit()
        
        # Create the new measurement using the Measurement model
        new_measurement = Measurement(
            name=name,
            value=value,
            group=group,
            unit=unit
        )
        
        # Initialize collection if it doesn't exist
        if not hasattr(self, 'collection'):
            self.collection = MeasurementCollection(name="Proportia Measurements")
            self.current_measurements = self.collection.measurements
        
        # Add to collection
        self.collection.add_measurement(new_measurement)
        
        # Save to file
        file_path = self.get_measurements_file_path()
        if save_json_data(self.collection.to_dict(), file_path, indent=2):
            # Show success message
            show_message(f"Measurement '{name}' saved successfully", Gtk.MessageType.INFO)
            
            # Clear input fields
            self.widgets["measurementNameEntry"].set_text("")
            self.widgets["measurementValueEntry"].set_text("")
            self.widgets["generatedDimension"].set_text("")
            
            # Refresh the display
            self.load_and_display_measurements()
            self.populate_group_dropdown()
        else:
            show_message("Failed to save measurement", Gtk.MessageType.ERROR)
    
    def get_selected_group(self) -> str:
        """Get the selected group or create a new one"""
        selected = get_widget_value(self.widgets["groupDropdownSidebar"])
        
        if selected == "+ New Group":
            # Get text from new group entry
            new_group = get_widget_value(self.widgets["newGroupName"])
            if new_group:
                return new_group
            else:
                return "Default"
        elif selected and selected != "-- Select Group --":
            return selected
        else:
            return "Default"
    
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
        self.widgets["measurementGroupBox"].add(group_container)
    
    def on_group_header_clicked(self, button, expander):
        """Toggle the expander when the header is clicked"""
        expanded = expander.get_expanded()
        expander.set_expanded(not expanded)
    
    def create_measurement_item_ui(self, measurement: Measurement) -> Gtk.Box:
        """Create UI for a single measurement item with improved styling"""
        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        item_box.set_margin_top(0)
        item_box.set_margin_bottom(0)
        apply_css_class(item_box, "measurement-item")
        
        # Add name with styling
        name_label = Gtk.Label(label=measurement.name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        apply_css_class(name_label, "measurement-name")
        item_box.pack_start(name_label, True, True, 5)
        
        # Add value with unit and styling
        value_text = f"{measurement.value:.2f} {measurement.unit}"
        value_label = Gtk.Label(label=value_text)
        value_label.set_halign(Gtk.Align.END)
        apply_css_class(value_label, "measurement-value")
        
        # Create button box for the actions
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(2)
        
        # Add edit button with tooltip
        edit_button = Gtk.Button()
        edit_button.set_relief(Gtk.ReliefStyle.NONE)
        edit_button.set_tooltip_text(f"Edit {measurement.name}")
        edit_icon = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        edit_button.add(edit_icon)
        edit_button.connect("clicked", self.on_edit_measurement, measurement)
        
        # Add delete button with tooltip
        delete_button = Gtk.Button()
        delete_button.set_relief(Gtk.ReliefStyle.NONE)
        delete_button.set_tooltip_text(f"Delete {measurement.name}")
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
        """Handle edit button click by enabling inline editing"""
        # Find the parent item_box containing this measurement
        item_box = button.get_parent().get_parent()
        
        # Get the name label (first child of the item_box)
        name_label = item_box.get_children()[0]
        
        # Replace label with an entry for editing
        entry = Gtk.Entry()
        entry.set_text(measurement.name)
        entry.set_has_frame(False)
        apply_css_class(entry, "measurement-name-edit")
        
        # Replace the label with entry in the same position
        item_box.remove(name_label)
        item_box.pack_start(entry, True, True, 5)
        item_box.reorder_child(entry, 0)  # Ensure it's the first child
        
        # Replace the edit button with a save button
        button_box = button.get_parent()
        button_box.remove(button)
        
        # Create save button
        save_button = Gtk.Button()
        save_button.set_relief(Gtk.ReliefStyle.NONE)
        save_button.set_tooltip_text("Save changes")
        save_icon = Gtk.Image.new_from_icon_name("document-save-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        save_button.add(save_icon)
        
        # Add save handler
        save_button.connect("clicked", self.on_save_edit, measurement, entry)
        
        # Add cancel button
        cancel_button = Gtk.Button()
        cancel_button.set_relief(Gtk.ReliefStyle.NONE)
        cancel_button.set_tooltip_text("Cancel editing")
        cancel_icon = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        cancel_button.add(cancel_icon)
        cancel_button.connect("clicked", self.on_cancel_edit, measurement, item_box)
        
        # Add buttons to box
        button_box.pack_start(save_button, False, False, 0)
        button_box.pack_start(cancel_button, False, False, 0)
        
        # Show all new widgets
        item_box.show_all()
        
        # Give focus to the entry
        entry.grab_focus()
        
        # Connect Enter key to save
        entry.connect("activate", self.on_save_edit, measurement, entry)

    def on_save_edit(self, widget, measurement, entry):
        """Save the edited measurement name"""
        new_name = entry.get_text().strip()
        
        if new_name and new_name != measurement.name:
            # Update the measurement name
            old_name = measurement.name
            measurement.name = new_name
            
            # Save the collection
            file_path = self.get_measurements_file_path()
            if save_json_data(self.collection.to_dict(), file_path, indent=2):
                # Refresh display
                self.load_and_display_measurements()
                logger.info(f"Renamed measurement from '{old_name}' to '{new_name}'")
            else:
                show_message("Failed to save changes", Gtk.MessageType.ERROR)
        else:
            # Just refresh to revert the UI
            self.load_and_display_measurements()

    def on_cancel_edit(self, widget, measurement, item_box):
        """Cancel editing and revert to normal view"""
        # Just refresh the UI to its normal state
        self.load_and_display_measurements()

    def on_delete_measurement(self, button, measurement):
        """Handle delete button click"""
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete measurement '{measurement.name}'?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Remove from current measurements list
            self.current_measurements = [m for m in self.current_measurements 
                                         if not (m.name == measurement.name and m.value == measurement.value)]
            
            # Update the collection directly
            self.collection.measurements = self.current_measurements
            
            # Save to file
            file_path = self.get_measurements_file_path()
            if save_json_data(self.collection.to_dict(), file_path, indent=2):
                self.load_and_display_measurements()
                self.populate_group_dropdown()
            else:
                show_message("Failed to save changes", Gtk.MessageType.ERROR)

    def cleanup(self):
        """Clean up resources when the plugin is unloaded"""
        # Use shared cleanup utility
        cleanup_resources(self)
        logger.info("ProportiaUI resources cleaned up")
