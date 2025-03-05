import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gtk, Gegl

import json
import os

from utils.palette_models import PaletteData, PhysicalPalette, ColorData
from utils.palette_processor import PaletteProcessor

def log_error(message, exception=None):
    """Helper function to log errors with optional exception details."""
    if exception:
        Gimp.message(f"Error: {message} - Exception: {exception}")
    else:
        Gimp.message(f"Error: {message}")

def populate_dropdown(builder, dropdown_id, items, error_message="No items found"):
    """
    Generic function to populate any GtkComboBoxText dropdown.
    
    Args:
        builder: Gtk.Builder instance
        dropdown_id: str, the ID of the dropdown in the UI
        items: list, items to populate the dropdown with
        error_message: str, message to show when no items are found
    """
    try:
        Gimp.message(f"Starting to populate {dropdown_id}...")

        # Get the dropdown widget
        dropdown = builder.get_object(dropdown_id)
        if dropdown is None:
            raise ValueError(f"Could not find '{dropdown_id}' in the UI. Check XML IDs.")

        # Ensure it's a valid GtkComboBoxText
        if not isinstance(dropdown, Gtk.ComboBoxText):
            raise TypeError(f"'{dropdown_id}' is not a GtkComboBoxText but a {type(dropdown)}.")

        # Clear existing items
        dropdown.remove_all()

        # Check if we have items
        if not items:
            Gimp.message(error_message)
            dropdown.append_text(error_message)
            return

        Gimp.message(f"Retrieved {len(items)} items for {dropdown_id}.")

        # Add items to dropdown
        for item in items:
            item_text = item.get_name() if hasattr(item, 'get_name') else str(item)
            dropdown.append_text(item_text)

        Gimp.message(f"{dropdown_id} populated successfully.")

    except Exception as e:
        Gimp.message(f"Error in populate_dropdown for {dropdown_id}: {e}")
        dropdown.append_text(f"Error loading {dropdown_id}")

def log_palette_colormap(builder):
    try:
        Gimp.message("Starting log_palette_colormap()...")

        palette_dropdown = builder.get_object("paletteDropdown")
        if palette_dropdown is None:
            Gimp.message("Error: Could not find 'paletteDropdown' in the UI. Check XML IDs.")
            return

        selected_palette_name = palette_dropdown.get_active_text()
        if not selected_palette_name:
            Gimp.message("No palette selected.")
            return

        Gimp.message(f"User selected palette: '{selected_palette_name}'")

        # Get the list of palettes
        palette_objects = Gimp.palettes_get_list("")
        if not palette_objects:
            Gimp.message("No palettes found in GIMP.")
            return

        # Extract actual palette names from objects
        palette_names = {p.get_name().strip().lower(): p for p in palette_objects}
        Gimp.message(f"Available palette names: {list(palette_names.keys())}")

        selected_palette_name = selected_palette_name.strip().lower()

        if selected_palette_name not in palette_names:
            Gimp.message(f"Palette '{selected_palette_name}' not found. Available: {list(palette_names.keys())}")
            return

        # Get the actual palette object
        palette = palette_names[selected_palette_name]

        # Get colors
        colors = palette.get_colors()
        Gimp.message(f"Colors retrieved: {colors}")  # Debug message to check the colors list

        if not colors:
            Gimp.message(f"No colors found in palette '{palette.get_name()}'.")
            return

        Gimp.message(f"Logging colors for palette '{palette.get_name()}':")
        for index, color in enumerate(colors):
            Gimp.message(f"Processing color at index {index}: {color}")

            if isinstance(color, list):
                Gimp.message(f"Found a list instead of a Gegl.Color at index {index}: {color}")
                continue

            if isinstance(color, Gegl.Color):  # Ensure it's a Gegl.Color object
                rgba = color.get_rgba()  # Get RGBA values
                Gimp.message(f"Color: R={rgba[0]:.3f}, G={rgba[1]:.3f}, B={rgba[2]:.3f}, A={rgba[3]:.3f}")
            else:
                Gimp.message(f"Unexpected color type at index {index}: {type(color)}. Skipping this color.")


        Gimp.message("log_palette_colormap() completed successfully.")

    except Exception as e:
        Gimp.message(f"Unexpected error in log_palette_colormap: {e}")


def get_palette_colors(palette_name):
    # Retrieve the palette by name
    palette = Gimp.Palette.get_by_name(palette_name)
    
    if not palette:
        Gimp.message(f"Palette '{palette_name}' not found.")
        return []

    # Retrieve all colors in the palette
    colors = palette.get_colors()

    return colors

def gimp_palette_to_palette_data(palette_name):
    """Converts a GIMP palette to our PaletteData model."""
    try:
        # Retrieve the palette by name
        palette = Gimp.Palette.get_by_name(palette_name)
        
        if not palette:
            Gimp.message(f"Palette '{palette_name}' not found.")
            return None

        # Retrieve all colors in the palette
        gimp_colors = palette.get_colors()
        
        if not gimp_colors:
            Gimp.message(f"No colors found in palette '{palette_name}'.")
            return None
            
        # Convert colors to our model
        colors = []
        for i, color in enumerate(gimp_colors):
            if isinstance(color, Gegl.Color):
                color_data = PaletteProcessor.convert_gegl_to_color_data(
                    color, 
                    name=f"Color {i+1}"
                )
                colors.append(color_data)
        
        # Create and return PaletteData object
        return PaletteData(
            name=palette_name,
            colors=colors,
            description=f"GIMP palette: {palette_name}"
        )
        
    except Exception as e:
        log_error(f"Error converting GIMP palette to PaletteData", e)
        return None

def get_all_physical_palettes():
    """Returns a list of all available physical palettes."""
    try:
        # Get GIMP's user data directory
        gimp_dir = Gimp.directory()
        plugin_data_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
        
        # If directory doesn't exist, return empty list
        if not os.path.exists(plugin_data_dir):
            return []
        
        # Get all JSON files in the directory
        palette_files = [f for f in os.listdir(plugin_data_dir) if f.endswith('.json')]
        
        # Extract palette names (remove .json extension)
        palette_names = [os.path.splitext(f)[0] for f in palette_files]
        
        return sorted(palette_names)
    except Exception as e:
        log_error("Failed to get physical palettes", e)
        return []

def clean_and_verify_json(json_string):
    """
    Cleans and verifies a JSON string from an LLM response.
    Works independently of any LLM class, supporting the decoupling effort.
    """
    try:
        # Remove markdown code block formatting
        cleaned = json_string.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.split("```json")[1].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0].strip()
            
        # Parse the JSON
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        log_error("Error parsing JSON from LLM response", e)
        return {"error": str(e)}

def save_palette_to_file(llm_palette):
    """Saves the LLMPhysicalPalette instance to a JSON file."""
    try:
        # Check if we have new style palette or old dict format
        if hasattr(llm_palette, 'to_dict'):
            # This is already a PaletteData object
            palette_data = llm_palette
        else:
            # Create a PhysicalPalette from the old data format
            colors = []
            for color_name in llm_palette.colors_listed:
                colors.append(ColorData(
                    name=color_name,
                    hex_value="#000000"  # Default - we don't have hex in old format
                ))
                
            palette_data = PhysicalPalette(
                name=llm_palette.physical_palette_name,
                colors=colors,
                source=llm_palette.palette_source,
                additional_notes=llm_palette.additional_notes
            )
        
        # Save using PaletteProcessor
        filepath = PaletteProcessor.save_palette(palette_data)
        if filepath:
            Gimp.message(f"Palette '{palette_data.name}' saved successfully.")
        
    except Exception as e:
        log_error("Failed to save palette to file", e)

def save_json_to_file(data, filename):
    """Saves a given data dictionary to a JSON file in GIMP's plugin directory."""
    try:
        # Get GIMP's user data directory
        gimp_dir = Gimp.directory()  # This gets GIMP's user data directory
        
        # Create a directory for our plugin data if it doesn't exist
        plugin_data_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
        os.makedirs(plugin_data_dir, exist_ok=True)
        
        # Create the full file path
        file_path = os.path.join(plugin_data_dir, f"{filename}.json")
        
        # Save the file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)  # Use indent for pretty printing
        
        Gimp.message(f"Data saved successfully to '{file_path}'.")
    except Exception as e:
        log_error(f"Failed to save data to file '{filename}.json'", e)

def populate_palette_dropdown(builder):
    """Populates the GIMP palette dropdown."""
    palettes = Gimp.palettes_get_list("")
    populate_dropdown(builder, "paletteDropdown", palettes, "No palettes found")

def populate_physical_palette_dropdown(builder):
    """Populates the physical palette dropdown."""
    physical_palettes_dir = os.path.join(os.path.dirname(__file__), "physical_palettes")
    palette_files = [os.path.splitext(f)[0] for f in os.listdir(physical_palettes_dir) 
                    if f.endswith('.json')]
    populate_dropdown(builder, "physicalPaletteDropdown", palette_files, "No physical palettes found")

def load_physical_palette_data(palette_name):
    """Loads physical palette data from a JSON file."""
    try:
        # Handle legacy format - check if this is a direct file path
        if palette_name.endswith('.json'):
            filename = palette_name
        else:
            filename = palette_name
            
        # Use PaletteProcessor to load the palette
        palette = PaletteProcessor.load_palette(filename)
        
        if palette:
            # For backward compatibility, return as dict
            return palette.to_dict()
        else:
            # Try legacy loading method as fallback
            gimp_dir = Gimp.directory()
            plugin_data_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
            
            # Try with and without .json extension
            for test_name in [palette_name, f"{palette_name}.json"]:
                path = os.path.join(plugin_data_dir, test_name)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            
            log_error(f"Physical palette not found: {palette_name}")
            return None
    except Exception as e:
        log_error(f"Failed to load physical palette data for '{palette_name}'", e)
        return None
    