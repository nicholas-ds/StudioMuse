#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gimp
from core.utils.api_client import api_client
from core.utils.colorBitMagic_utils import (
    save_json_to_file,
    populate_palette_dropdown,
    populate_physical_palette_dropdown,
    load_physical_palette_data,
    get_palette_colors,
    log_error
)
import json
import os

class ColorBitMagic:
    """
    Handles the analysis functionality for color palette operations.
    Controls the UI interactions for the Analysis notebook tab.
    """
    
    def __init__(self):
        """Initialize the ColorBitMagic tool."""
        self.builder = None
        self.palette_name = None
        self.results_view = None
        self.widgets = {}  # Store widget references
        self.color_results = []  # Store color mapping results
        self.is_active = True

    def set_builder(self, builder):
        """
        Set the GTK builder instance for this tool.
        
        Args:
            builder (Gtk.Builder): The builder instance containing analysis UI elements
        """
        self.builder = builder
        # Initialize widget references
        widget_ids = [
            'submitButton',
            'paletteDropdown',
            'physicalPaletteDropdown',
            'paletteNameEntry',
            'resultListBox',  # Updated from resultsTextView
            'rightPanel',
            'colorSwatch',
            'colorNameLabel',
            'rgbLabel',
            'physicalColorLabel',
            'mixingSuggestionsLabel'
        ]
        for widget_id in widget_ids:
            self.widgets[widget_id] = self.builder.get_object(widget_id)
            
        # Initialize dropdowns
        populate_palette_dropdown(self.builder)
        populate_physical_palette_dropdown(self.builder)
        
        # Connect list box selection handler
        if self.widgets['resultListBox']:
            self.widgets['resultListBox'].connect('row-selected', self.on_color_selected)

    def log_message(self, message, level="info"):
        """Centralized logging function with active check"""
        if self.is_active:
            Gimp.message(message)

    def format_palette_mapping(self, result):
        """
        Format the API response for display.
        
        Args:
            result: JSON string or dictionary containing color mapping data
        Returns:
            List of formatted color mapping entries
        """
        if isinstance(result, str):
            try:
                clean_result = result.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_result)
            except json.JSONDecodeError as e:
                self.log_message(f"JSON parsing error: {str(e)}")
                return [{"error": result}]
        else:
            data = result

        if not isinstance(data, list):
            self.log_message("API response format unexpected (not a list)")
            return [{"error": "Unexpected API response format"}]

        formatted_data = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                self.log_message(f"Malformed entry at index {index}: {str(item)}")
                continue
            
            entry = {
                "gimp_color_name": item.get("gimp_color_name", f"Unknown-{index}"),
                "rgb_color": item.get("rgb_color", "N/A"),
                "physical_color_name": item.get("physical_color_name", "Unknown"),
                "mixing_suggestions": item.get("mixing_suggestions", "N/A")
            }
            formatted_data.append(entry)

        return formatted_data if formatted_data else [{
            "gimp_color_name": "Error",
            "rgb_color": "N/A",
            "physical_color_name": "Error",
            "mixing_suggestions": "No valid color mappings received from API"
        }]

    def _create_color_swatch(self, color_data, width=30, height=20):
        """Create a color swatch with the specified color data"""
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(width, height)
        
        # Use the original RGB values from color_data (0.0-1.0 range)
        def draw_callback(widget, cr, rgb=color_data["rgb"]):
            # Use RGB values directly - they're already in the 0.0-1.0 range that GTK expects
            cr.set_source_rgb(rgb["r"], rgb["g"], rgb["b"])
            cr.rectangle(0, 0, width, height)
            cr.fill()
            return False
        
        drawing_area.connect("draw", draw_callback)
        return drawing_area

    def on_color_selected(self, listbox, row):
        """Handle color selection from the list box"""
        if row is None:
            return
            
        # Get index from the row and use it to access the color data
        index = row.get_index()
        if 0 <= index < len(self.color_results):
            color_data = self.color_results[index]
            self.update_right_panel(color_data)
            self.log_message(f"Selected color: {color_data['name']}")

    def update_right_panel(self, color_data):
        """Update the right panel with the selected color's information"""
        # Update color swatch
        def draw_callback(widget, cr):
            cr.set_source_rgb(color_data["rgb"]["r"], color_data["rgb"]["g"], color_data["rgb"]["b"])
            cr.rectangle(0, 0, widget.get_allocated_width(), widget.get_allocated_height())
            cr.fill()
            return False
            
        self.widgets['colorSwatch'].connect("draw", draw_callback)
        self.widgets['colorSwatch'].queue_draw()
        
        # Update labels
        self.widgets['colorNameLabel'].set_markup(f"<b>{color_data['name']}</b>")
        self.widgets['rgbLabel'].set_markup(f"<b>RGB:</b> {color_data['rgb_color']}")
        self.widgets['physicalColorLabel'].set_markup(f"<b>Physical:</b> {color_data['physical_color_name']}")
        self.widgets['mixingSuggestionsLabel'].set_markup(f"<b>Mixing Suggestions:</b>\n{color_data['mixing_suggestions']}")

    def display_results(self, formatted_data, result_widget_id):
        """
        Display formatted color mapping results in a selectable list with color swatches.
        
        Args:
            formatted_data: List of dictionaries containing color mapping info
            result_widget_id: ID of the GtkScrolledWindow to populate
        """
        # Get the list box
        list_box = self.widgets['resultListBox']
        if not list_box:
            self.log_message("Error: Could not find resultListBox")
            return
            
        # Clear existing content
        for child in list_box.get_children():
            list_box.remove(child)
            
        # Store color results
        self.color_results = []
        
        # Process each color entry
        for item in formatted_data:
            # Parse RGB values with maximum precision
            try:
                rgb_values = item['rgb_color'].replace("rgb(", "").replace(")", "").split(",")
                rgb_dict = {
                    "r": float(rgb_values[0].strip()),  # Maintains full float precision
                    "g": float(rgb_values[1].strip()),
                    "b": float(rgb_values[2].strip())
                }
                # Use full precision hex conversion
                hex_value = "#{:02x}{:02x}{:02x}".format(
                    round(rgb_dict['r'] * 255),
                    round(rgb_dict['g'] * 255),
                    round(rgb_dict['b'] * 255)
                )
            except Exception as e:
                self.log_message(f"Error parsing RGB values: {e}")
                rgb_dict = {"r": 0.0, "g": 0.0, "b": 0.0}
                hex_value = "#000000"
                
            # Create color entry
            color_entry = {
                "name": item['gimp_color_name'],
                "rgb_color": item['rgb_color'],
                "rgb": rgb_dict,
                "hex_value": hex_value,
                "physical_color_name": item['physical_color_name'],
                "mixing_suggestions": item['mixing_suggestions']
            }
            self.color_results.append(color_entry)
            
            # Create list box row
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_start(10)
            hbox.set_margin_end(10)
            hbox.set_margin_top(5)
            hbox.set_margin_bottom(5)
            
            # Add color name label
            name_label = Gtk.Label(xalign=0)
            name_label.set_markup(f"<b>{color_entry['name']}</b>")
            hbox.pack_start(name_label, True, True, 0)
            
            # Add color swatch
            swatch = self._create_color_swatch(color_entry)
            hbox.pack_end(swatch, False, False, 0)
            
            row.add(hbox)
            list_box.add(row)
            
        # Show all widgets
        list_box.show_all()
        
        # Select first row if available
        if len(self.color_results) > 0:
            first_row = list_box.get_row_at_index(0)
            if first_row:
                list_box.select_row(first_row)
                self.on_color_selected(list_box, first_row)

    # Signal handlers for Analysis notebook
    def on_submit_clicked(self, button):
        """Handle submission of palette comparison."""
        self.log_message("Submit button clicked. Loading selected palettes...")
        
        # Get selected palettes from dropdowns
        selected_palette = self.widgets['paletteDropdown'].get_active_text()
        selected_physical_palette = self.widgets['physicalPaletteDropdown'].get_active_text()
        
        if not selected_palette or not selected_physical_palette:
            self.log_message("Please select both a GIMP palette and a physical palette.")
            return
            
        try:
            # Get palette data
            gimp_palette_colors = get_palette_colors(selected_palette)
            if not gimp_palette_colors:
                self.log_message(f"Failed to load GIMP palette: {selected_palette}")
                return
                
            # Load physical palette data
            physical_palette_data = load_physical_palette_data(selected_physical_palette)
            if not physical_palette_data:
                self.log_message(f"Failed to load physical palette: {selected_physical_palette}")
                return
                
            # Extract physical color names
            physical_color_names = self._extract_physical_color_names(physical_palette_data)
            
            # Process through API
            try:
                response = api_client.demystify_palette(
                    gimp_palette_colors=gimp_palette_colors,
                    physical_palette_data=physical_color_names
                )
                
                if response.get("success"):
                    result = response.get("response")
                    formatted_result = self.format_palette_mapping(result)
                    self.display_results(formatted_result, "resultListBox")
                else:
                    error_msg = response.get("error", "Unknown error")
                    self.log_message(f"API error: {error_msg}")
                    
            except Exception as e:
                log_error("API communication error", e)
                self.log_message(f"Error: {str(e)}")
                
        except Exception as e:
            log_error("Error in palette demystification", e)
            self.log_message(f"Error: {str(e)}")
    
    def _extract_physical_color_names(self, physical_palette_data):
        """Extract physical color names from different data formats"""
        physical_color_names = []
        
        # Handle different formats of physical_palette_data
        if isinstance(physical_palette_data, dict) and 'colors' in physical_palette_data:
            # Extract color names from dictionary
            physical_color_names = physical_palette_data['colors']
        elif isinstance(physical_palette_data, list):
            # Already a list of color names
            physical_color_names = physical_palette_data
        else:
            # Fallback to string representation as a single item
            physical_color_names = [str(physical_palette_data)]
            
        return physical_color_names

    def on_add_physical_palette_clicked(self, button):
        """Handle adding a new physical palette."""
        print("Add physical palette button clicked")
        if self.widgets.get('paletteNameEntry'):
            palette_name = self.widgets['paletteNameEntry'].get_text()
            Gimp.message(f"Adding new palette: {palette_name}")
        else:
            Gimp.message("Error: Palette name entry not found")
    
    def on_save_clicked(self, button):
        """Handle saving the current palette configuration."""
        print("Save button clicked")
        Gimp.message("Saving palette configuration...")
    
    def on_generate_clicked(self, button):
        """Handle palette generation request."""
        print("Generate button clicked")
        Gimp.message("Generating palette...")
    
    def on_close_clicked(self, button):
        """Handle closing the current view."""
        print("Close button clicked")
        Gimp.message("Closing current view...")

    def cleanup(self):
        """Clean up resources when the tool is being closed"""
        try:
            # Clear any stored data
            self.color_results.clear()
            
            # Clear widget references
            self.widgets.clear()
            
            # Mark as inactive
            self.is_active = False
            
            # Clear builder reference
            self.builder = None
            
        except Exception as e:
            print(f"Error during ColorBitMagic cleanup: {e}")
