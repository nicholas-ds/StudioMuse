#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gimp
from core.utils.api_client import api_client
from core.utils.colorBitMagic_utils import (
    get_palette_colors,
    load_physical_palette_data,
    log_error
)
# Import new file I/O utilities
from core.utils.file_io import (
    get_plugin_storage_path,
    save_json_data,
    load_json_data
)
from core.utils.ui import (
    connect_signals,
    collect_widgets,
    get_widget_value,
    show_message,
    populate_dropdown,
    cleanup_resources
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
        # Initialize widget references for both tabs using collect_widgets utility
        widget_ids = [
            # Demystify tab widgets
            'submitButton',
            'paletteDropdown',
            'physicalPaletteDropdown',
            'resultListBox',
            'rightPanel',
            'colorSwatch',
            'colorNameLabel',
            'rgbLabel',
            'physicalColorLabel',
            'mixingSuggestionsLabel',
            # Add Palette tab widgets
            'paletteNameEntry',
            'resultsTextView',
            'saveButton',
            'generateButton',
            'closeButton'
        ]
        
        self.widgets = collect_widgets(self.builder, widget_ids)
            
        # Initialize dropdowns
        self.populate_palette_dropdown()
        self.populate_physical_palette_dropdown()
        
        # Connect signal handlers using shared utility
        custom_handlers = {
            'resultListBox': [('row-selected', self.on_color_selected)],
            'submitButton': [('clicked', self.on_submit_clicked)],
            'saveButton': [('clicked', self.on_save_clicked)],
            'generateButton': [('clicked', self.on_generate_clicked)],
            'closeButton': [('clicked', self.on_close_clicked)]
        }
        connect_signals(self.builder, self, custom_handlers)

    def log_message(self, message, level="info"):
        """Centralized logging function with active check"""
        if self.is_active:
            if level == "error":
                show_message(message, Gtk.MessageType.ERROR)
            else:
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
        
        # Get selected palettes from dropdowns using get_widget_value utility
        selected_palette = get_widget_value(self.widgets['paletteDropdown'])
        selected_physical_palette = get_widget_value(self.widgets['physicalPaletteDropdown'])
        
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

    def populate_palette_dropdown(self):
        """Populates the GIMP palette dropdown using shared utility."""
        palettes = Gimp.palettes_get_list("")
        populate_dropdown(self.widgets['paletteDropdown'], palettes, "-- Select a palette --")

    def populate_physical_palette_dropdown(self):
        """Populates the physical palette dropdown using shared utility."""
        from core.utils.colorBitMagic_utils import get_all_physical_palettes
        physical_palettes = get_all_physical_palettes()
        populate_dropdown(self.widgets['physicalPaletteDropdown'], physical_palettes, "-- Select a physical palette --")

    def on_add_physical_palette_clicked(self, button):
        """Handle adding a new physical palette."""
        # Using get_widget_value utility
        palette_name = get_widget_value(self.widgets['paletteNameEntry'])
        if palette_name:
            self.log_message(f"Adding new palette: {palette_name}")
        else:
            self.log_message("Error: Please enter a palette name")
    
    def on_save_clicked(self, button):
        """Handle saving the current palette configuration."""
        if not hasattr(self, 'current_palette'):
            self.log_message("No palette to save. Please generate a palette first.")
            return

        try:
            # Define the output directory for physical palettes using the centralized utility
            physical_palettes_dir = get_plugin_storage_path("physical_palettes", "colorBitMagic")
            
            # Ensure filename is valid
            filename = f"{self.current_palette['name']}.json"
            filepath = os.path.join(physical_palettes_dir, filename)
            
            # Save the palette data using the centralized utility
            if save_json_data(
                self.current_palette,
                filepath,
                create_dirs=True,
                indent=2
            ):
                self.log_message(f"Palette '{self.current_palette['name']}' saved successfully.")
                # Refresh the physical palette dropdown
                self.populate_physical_palette_dropdown()
                # Switch back to first tab
                notebook = self.builder.get_object("analysisNotebook")
                if notebook:
                    notebook.set_current_page(0)
            else:
                self.log_message(f"Failed to save palette '{self.current_palette['name']}'.")
                
        except Exception as e:
            log_error("Error saving palette", e)
            self.log_message(f"Error saving palette: {str(e)}")
    
    def on_generate_clicked(self, button):
        """Handle generating palette from LLM."""
        # Use get_widget_value utility
        entry_text = get_widget_value(self.widgets['paletteNameEntry'])
        if not entry_text:
            self.log_message("Please enter a palette description")
            return

        try:
            # Call the backend API
            self.log_message(f"Sending request to API with text: {entry_text}")
            result = api_client.create_physical_palette(entry_text)
            
            if not result:
                self.log_message("Error: Received empty response from API")
                return
                
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                self.log_message(f"API error: {error_msg}")
                return
                
            # Get the raw response and validate it
            raw_response = result.get("response", "")
            if not raw_response:
                self.log_message("Error: Empty response data from API")
                return
                
            # Clean the response if it contains markdown code blocks
            if isinstance(raw_response, str):
                raw_response = raw_response.replace('```json', '').replace('```', '').strip()
            
            try:
                # Parse JSON response
                json_response = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                
                # Validate required fields
                required_fields = ['set_name', 'colors', 'piece_count']
                missing_fields = [field for field in required_fields if field not in json_response]
                if missing_fields:
                    self.log_message(f"Error: Missing required fields in response: {missing_fields}")
                    return
                
                # Store palette data
                self.current_palette = {
                    "name": json_response["set_name"],
                    "raw_response": raw_response,
                    "colors": json_response['colors'],
                    "piece_count": json_response['piece_count']
                }

                # Display the results in the text view
                self.display_palette_text(json_response)
                self.log_message("Palette generated successfully")
                
            except json.JSONDecodeError as e:
                log_error(f"JSON parsing error. Raw response: {raw_response}", e)
                self.log_message(f"Error parsing API response: {str(e)}")
            
        except Exception as e:
            log_error(f"Error in palette generation. Entry text: {entry_text}", e)
            self.log_message(f"Error generating palette: {str(e)}")

    def display_palette_text(self, palette_data):
        """Display palette information in the text view."""
        text_view = self.widgets.get('resultsTextView')
        if not text_view:
            self.log_message("Error: Results text view not found")
            return
            
        try:
            buffer = text_view.get_buffer()
            
            # Format the text
            formatted_text = []
            formatted_text.append(f"PALETTE: {palette_data.get('set_name', 'Unknown')}")
            formatted_text.append(f"Number of Colors: {palette_data.get('piece_count', 'Unknown')}")
            formatted_text.append("\nCOLORS:")
            
            for color in palette_data.get('colors', []):
                formatted_text.append(f"  • {color}")
            
            if notes := palette_data.get('additional_notes'):
                formatted_text.append(f"\nNotes:\n{notes}")
                
            # Set the text
            buffer.set_text('\n'.join(formatted_text))
            
        except Exception as e:
            log_error("Error displaying palette text", e)
            self.log_message(f"Error displaying palette: {str(e)}")

    def on_close_clicked(self, button):
        """Handle closing the current view."""
        notebook = self.builder.get_object("analysisNotebook")
        if notebook:
            notebook.set_current_page(0)  # Switch back to first tab
        self.log_message("Returning to main view...")

    def cleanup(self):
        """Clean up resources when the tool is being closed"""
        # Use shared cleanup utility
        cleanup_resources(self)
