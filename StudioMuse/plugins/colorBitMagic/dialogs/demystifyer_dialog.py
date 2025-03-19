import gi
from gi.repository import Gimp
import json
from .base_dialog import BaseDialog
from colorBitMagic_utils import (
    populate_palette_dropdown, 
    populate_physical_palette_dropdown,
    load_physical_palette_data,
    get_palette_colors,
    log_error
)
import json
from utils.api_client import BackendAPIClient

class DemystifyerDialog(BaseDialog):
    def __init__(self):
        super().__init__("dmMain_update_populated.xml", "dmMainWindow")
        # Initialize dropdowns
        populate_palette_dropdown(self.builder)
        populate_physical_palette_dropdown(self.builder)
        
    def _get_signal_handlers(self):
        handlers = super()._get_signal_handlers()
        handlers.update({
            "on_submit_clicked": self.on_submit_clicked,
            "on_add_physical_palette_clicked": self.on_add_physical_palette_clicked
        })
        return handlers
        
    def on_submit_clicked(self, button):
        Gimp.message("Submit button clicked. Loading selected palettes...")
        
        # Get selected palettes from dropdowns
        selected_palette = self.builder.get_object("paletteDropdown").get_active_text()
        selected_physical_palette = self.builder.get_object("physicalPaletteDropdown").get_active_text()
        
        if not selected_palette or not selected_physical_palette:
            Gimp.message("Please select both a GIMP palette and a physical palette.")
            return
        
        try:
            # Get palette data
            gimp_palette_colors = get_palette_colors(selected_palette)
            if not gimp_palette_colors:
                Gimp.message(f"Failed to load GIMP palette: {selected_palette}")
                return
            
            # Log the GIMP palette colors for debugging
            Gimp.message(f"Original GIMP palette '{selected_palette}' contains {len(gimp_palette_colors)} colors:")
            for i, color in enumerate(gimp_palette_colors):
                if isinstance(color, dict):
                    color_name = color.get('name', 'Unnamed')
                    color_value = color.get('rgb_color', 'No RGB value')
                    Gimp.message(f"  Color {i+1}: {color_name} - {color_value}")
                else:
                    Gimp.message(f"  Color {i+1}: {color}")
            
            # Load physical palette data
            physical_palette_data = load_physical_palette_data(selected_physical_palette)
            if not physical_palette_data:
                Gimp.message(f"Failed to load physical palette: {selected_physical_palette}")
                return
            
            # Show loading message
            Gimp.message(f"Processing palettes: {selected_palette} and {selected_physical_palette}")
            
            # Try API client first, fall back to local LLM if API fails
            try:
                Gimp.message("Attempting to connect to backend API...")
                client = BackendAPIClient()
                
                # Test API connection first
                Gimp.message("Calling health_check()...")
                health_check = client.health_check()
                
                # Debug the health_check response
                if isinstance(health_check, dict):
                    Gimp.message(f"Health check result (dict): {health_check.get('status', 'unknown')}")
                else:
                    Gimp.message(f"Health check result (not dict): {health_check}")
                    health_check = {"status": health_check}
                
                # Check for either "ok" or "healthy" status
                if health_check.get("status") in ["ok", "healthy"]:
                    Gimp.message("Connected to backend API. Processing request...")
                    
                    # Extract physical color names - following the pattern in PaletteDemistifyerLLM.format_prompt()
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
                    
                    Gimp.message(f"Sending request with {len(gimp_palette_colors)} GIMP colors and {len(physical_color_names)} physical colors")
                    
                    # Call the demystify_palette method
                    Gimp.message("Calling demystify_palette()...")
                    response = client.demystify_palette(
                        gimp_palette_colors=gimp_palette_colors,
                        physical_palette_data=physical_color_names
                    )
                    
                    # Process API response
                    if not isinstance(response, dict):
                        Gimp.message(f"Unexpected response format: {type(response).__name__}")
                        response = {"success": False, "error": f"Unexpected response type: {type(response).__name__}"}
                    
                    if response.get("success"):
                        # Handle successful API response
                        result = response.get("response")
                        provider = response.get("provider", "unknown")
                        Gimp.message(f"API request successful! Received response from {provider} provider.")
                        
                        # Format the result for display
                        formatted_result = self.format_palette_mapping(result)
                        self.display_results(formatted_result, "resultTextView")
                        return
                    else:
                        # Handle API error
                        error_msg = response.get("error", "Unknown error")
                        Gimp.message(f"API error: {error_msg}. Unable to process palette.")
                else:
                    # Handle failed health check
                    error_msg = health_check.get("error", "Unknown error")
                    Gimp.message(f"Backend API not available: {error_msg}. Please try again later.")
                    return
            
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                Gimp.message(f"API communication error: {str(e)}. Unable to process palette.")
                from colorBitMagic_utils import log_error
                log_error("API communication error", e)
                log_error("Traceback", tb)
                return
            
        except Exception as e:
            from colorBitMagic_utils import log_error
            log_error("Error in palette demystification", e)
            Gimp.message(f"Error: {str(e)}")
            
    def on_add_physical_palette_clicked(self, button):
        from .add_palette_dialog import AddPaletteDialog
        AddPaletteDialog().show()

    def format_palette_mapping(self, result):
        """
        Ensure the result is correctly parsed into a list of dictionaries.

        Args:
            result: JSON string or dictionary object.
            
        Returns:
            A list of structured data for display_results.
        """
        # Log the raw response for debugging
        Gimp.message(f"Raw API response: {str(result)}")

        # If result is a string, attempt to parse it
        if isinstance(result, str):
            try:
                # Remove markdown code block markers if present
                clean_result = result.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_result)  # Convert JSON string to dictionary
            except json.JSONDecodeError as e:
                Gimp.message(f"JSON parsing error: {str(e)}")
                # If parsing fails, try to render a plain text version
                cleaned_text = self.clean_json_string(result)
                return [{"error": cleaned_text}]
        else:
            data = result

        # Ensure the data is a list
        if not isinstance(data, list):
            Gimp.message("API response format unexpected (not a list)")
            return [{"error": "Unexpected API response format"}]

        formatted_data = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                Gimp.message(f"Malformed entry at index {index}: {str(item)}")
                continue  # Skip invalid entries
            
            # Make sure all required keys exist with default values
            entry = {
                "gimp_color_name": item.get("gimp_color_name", f"Unknown-{index}"),
                "rgb_color": item.get("rgb_color", "N/A"),
                "physical_color_name": item.get("physical_color_name", "Unknown"),
                "mixing_suggestions": item.get("mixing_suggestions", "N/A")
            }
            formatted_data.append(entry)

        if not formatted_data:
            # Return a list with a single error entry that has all required keys
            return [{
                "gimp_color_name": "Error",
                "rgb_color": "N/A",
                "physical_color_name": "Error",
                "mixing_suggestions": "No valid color mappings received from API"
            }]

        return formatted_data

    def clean_json_string(self, json_string):
        """
        Simple function to clean up a JSON string for display when parsing fails
        """
        # Remove any markdown code block markers
        cleaned = json_string.replace('```json', '').replace('```', '')
        
        # Remove the JSON formatting characters
        cleaned = cleaned.replace('[', '').replace(']', '')
        cleaned = cleaned.replace('{', '').replace('}', '')
        cleaned = cleaned.replace('"', '')
        
        # Replace JSON field names with more readable labels
        cleaned = cleaned.replace('gimp_color_name:', 'GIMP Color:')
        cleaned = cleaned.replace('rgb_color:', 'RGB Value:')
        cleaned = cleaned.replace('physical_color_name:', 'Physical Color:')
        cleaned = cleaned.replace('mixing_suggestions:', 'Mixing Suggestion:')
        
        # Clean up commas and formatting
        cleaned = cleaned.replace(',', '')
        
        # Remove excessive whitespace and empty lines
        lines = [line.strip() for line in cleaned.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        
        # Format with separators
        result = "PALETTE MAPPING RESULTS\n======================\n\n"
        
        # Group lines by color entry (assuming 4 lines per color)
        i = 0
        while i < len(lines):
            # Add as many lines as we can for this color entry
            color_entry = []
            while i < len(lines) and not lines[i].startswith("GIMP Color:"):
                if color_entry:  # Only add if we've already started a color entry
                    color_entry.append(lines[i])
                i += 1
            
            # Start a new color entry if we found a GIMP Color line
            if i < len(lines):
                color_entry = [lines[i]]
                i += 1
                # Add the remaining lines for this color
                while i < len(lines) and not lines[i].startswith("GIMP Color:"):
                    color_entry.append(lines[i])
                    i += 1
            
            # Add the formatted color entry with separator
            if color_entry:
                result += "\n".join(color_entry) + "\n==================================\n\n"
        
        return result

    def display_results(self, formatted_data, result_widget_id):
        """
        Display formatted color mapping results in a selectable list with color swatches.
        
        Args:
            formatted_data: List of dictionaries containing color mapping info
            result_widget_id: ID of the GtkScrolledWindow to populate
        """
        # Import required Gtk components
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk, Pango
        
        # Get required UI elements
        result_container = self.builder.get_object(result_widget_id)  # GtkScrolledWindow
        right_panel = self.builder.get_object("colorSwatch")  # Drawing area for color display
        
        if not result_container or not right_panel:
            Gimp.message("Error: Could not find required UI elements.")
            return
        
        # Remove existing content from scrolled window
        existing_list = result_container.get_child()
        if existing_list:
            result_container.remove(existing_list)
        
        # Create a new selectable GtkListBox
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        result_container.add(list_box)
        
        # Store color_results at class level for access in row selection handler
        self.color_results = []
        
        for item in formatted_data:
            # Convert RGB string to hex
            hex_value = "#000000"  # Default black
            rgb_str = item['rgb_color']
            try:
                # Parse RGB string like "rgb(0.020, 0.027, 0.039)"
                rgb_values = rgb_str.replace("rgb(", "").replace(")", "").split(",")
                r = int(float(rgb_values[0].strip()) * 255)
                g = int(float(rgb_values[1].strip()) * 255)
                b = int(float(rgb_values[2].strip()) * 255)
                hex_value = f"#{r:02x}{g:02x}{b:02x}"
            except (ValueError, IndexError) as e:
                log_error("RGB parsing error", e)
            
            # Create a color entry with all needed information
            color_entry = {
                "name": item['gimp_color_name'],
                "hex_value": hex_value,
                "rgb_color": item['rgb_color'],
                "physical_color_name": item['physical_color_name'],
                "mixing_suggestions": item['mixing_suggestions']
            }
            self.color_results.append(color_entry)
        
        # Define the callback outside so we can trigger it manually for the first item
        def on_row_selected(listbox, row):
            if row is None:
                return
            # Get index from the row and use it to access the color data
            index = row.get_index()
            if 0 <= index < len(self.color_results):
                color_data = self.color_results[index]
                self.update_right_panel(right_panel, color_data)
                Gimp.message(f"Selected color: {color_data['name']}")  # Debug message
        
        # Connect the callback to the list box
        list_box.connect("row-selected", on_row_selected)
        
        # Populate the list with colors
        for color in self.color_results:
            row = Gtk.ListBoxRow()
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            vbox.set_margin_start(10)
            vbox.set_margin_end(10)
            vbox.set_margin_top(5)
            vbox.set_margin_bottom(5)
            
            # Top row with color name and swatch
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            # Create name label
            label = Gtk.Label(xalign=0)
            label.set_markup(f"<b>{color['name']}</b>")
            label.set_ellipsize(Pango.EllipsizeMode.END)
            
            # Create color preview swatch
            drawing_area = Gtk.DrawingArea()
            drawing_area.set_size_request(30, 20)
            
            # Use a class to store the hex value for the closure
            class DrawParams:
                def __init__(self, hex_val):
                    self.hex_val = hex_val
                    
            draw_params = DrawParams(color["hex_value"])
            
            def draw_callback(widget, cr, draw_params):
                color_rgba = Gdk.RGBA()
                color_rgba.parse(draw_params.hex_val)
                cr.set_source_rgba(color_rgba.red, color_rgba.green, color_rgba.blue, color_rgba.alpha)
                cr.rectangle(0, 0, widget.get_allocated_width(), widget.get_allocated_height())
                cr.fill()
                return False
            
            drawing_area.connect("draw", draw_callback, draw_params)
            
            # Add physical color information
            physical_label = Gtk.Label(xalign=0)
            physical_label.set_markup(f"<i>Physical:</i> {color['physical_color_name']}")
            physical_label.set_ellipsize(Pango.EllipsizeMode.END)
            
            # Pack widgets into containers
            hbox.pack_start(label, True, True, 0)
            hbox.pack_end(drawing_area, False, False, 0)
            
            vbox.pack_start(hbox, False, False, 0)
            vbox.pack_start(physical_label, False, False, 0)
            
            row.add(vbox)
            list_box.add(row)
        
        # Show all widgets before selecting the first row
        list_box.show_all()
        
        # Select the first row by default to display initial color
        if len(self.color_results) > 0:
            first_row = list_box.get_row_at_index(0)
            if first_row:
                list_box.select_row(first_row)
                # Force update with the first item
                on_row_selected(list_box, first_row)
    
    def update_right_panel(self, drawing_area, color_data):
        """
        Updates the right panel to display the selected color and information.
        
        Args:
            drawing_area: GtkDrawingArea for color display
            color_data: Dictionary containing color information
        """
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk
        
        # Log what we're updating to for debugging
        Gimp.message(f"Updating right panel with: {color_data['name']} ({color_data['hex_value']})")
        
        # The colorSwatch is a drawing area, not a container
        # We need to get the rightPanel which is the container for everything
        right_panel = self.builder.get_object("rightPanel")
        
        if not right_panel:
            Gimp.message("Error: Could not find rightPanel in UI")
            return
            
        # Remove any existing children
        for child in right_panel.get_children():
            right_panel.remove(child)
        
        # Create new container for color swatch and info
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        
        # Create a larger color swatch
        new_drawing_area = Gtk.DrawingArea()
        new_drawing_area.set_size_request(200, 100)
        
        # Use a class to store the hex value for the closure
        class DrawParams:
            def __init__(self, hex_val):
                self.hex_val = hex_val
                
        draw_params = DrawParams(color_data["hex_value"])
        
        def draw_color(widget, cr, params):
            color_rgba = Gdk.RGBA()
            color_rgba.parse(params.hex_val)
            cr.set_source_rgba(color_rgba.red, color_rgba.green, color_rgba.blue, color_rgba.alpha)
            cr.rectangle(0, 0, widget.get_allocated_width(), widget.get_allocated_height())
            cr.fill()
            return False
        
        new_drawing_area.connect("draw", draw_color, draw_params)
        
        # Create labels for color information
        name_label = Gtk.Label(xalign=0)
        name_label.set_markup(f"<big><b>{color_data['name']}</b></big>")
        
        rgb_label = Gtk.Label(xalign=0)
        rgb_label.set_markup(f"<b>RGB:</b> {color_data['rgb_color']}")
        
        physical_label = Gtk.Label(xalign=0)
        physical_label.set_markup(f"<b>Physical color:</b> {color_data['physical_color_name']}")
        
        mixing_label = Gtk.Label(xalign=0)
        mixing_label.set_markup(f"<b>Mixing suggestions:</b>\n{color_data['mixing_suggestions']}")
        mixing_label.set_line_wrap(True)
        mixing_label.set_justify(Gtk.Justification.FILL)
        
        # Add all elements to the vbox
        vbox.pack_start(name_label, False, False, 0)
        vbox.pack_start(new_drawing_area, False, False, 0)
        vbox.pack_start(rgb_label, False, False, 0)
        vbox.pack_start(physical_label, False, False, 0)
        vbox.pack_start(mixing_label, False, False, 0)
        
        # Add the vbox to the right panel
        right_panel.add(vbox)
        right_panel.show_all()
        
        # Force redraw of the drawing area
        new_drawing_area.queue_draw()
