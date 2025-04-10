import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gtk, Gegl

import json
import os

from core.models.palette_models import PaletteData, PhysicalPalette, ColorData
from core.models.palette_processor import PaletteProcessor, log_error
from core.utils.file_io import get_plugin_storage_path, load_json_data, save_json_data

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
                rgba = color.get_rgba()  # Get RGBA values at full precision
                Gimp.message(f"Color: R={rgba[0]}, G={rgba[1]}, B={rgba[2]}, A={rgba[3]}")
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
    """Converts a GIMP palette to our PaletteData model with maximum precision."""
    try:
        palette = Gimp.Palette.get_by_name(palette_name)
        
        if not palette:
            Gimp.message(f"Palette '{palette_name}' not found.")
            return None

        gimp_colors = palette.get_colors()
        
        if not gimp_colors:
            Gimp.message(f"No colors found in palette '{palette_name}'.")
            return None
            
        colors = []
        for i, color in enumerate(gimp_colors):
            if isinstance(color, Gegl.Color):
                # Get raw RGBA values at full precision
                rgba = color.get_rgba()
                color_data = ColorData(
                    name=f"Color {i+1}",
                    rgb={
                        "r": rgba[0],  # Keep full float precision
                        "g": rgba[1],
                        "b": rgba[2]
                    },
                    alpha=rgba[3],  # Preserve alpha channel
                    # Generate hex with maximum precision
                    hex_value="#{:02x}{:02x}{:02x}".format(
                        round(rgba[0] * 255),
                        round(rgba[1] * 255),
                        round(rgba[2] * 255)
                    )
                )
                colors.append(color_data)
        
        return PaletteData(
            name=palette_name,
            colors=colors,
            description=f"GIMP palette: {palette_name}"
        )
        
    except Exception as e:
        log_error(f"Error converting GIMP palette to PaletteData", e)
        return None

def get_all_physical_palettes():
    """
    Returns a list of all available physical palettes.
    Legacy wrapper around PaletteProcessor.get_all_physical_palettes.
    """
    return PaletteProcessor.get_all_physical_palettes()

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
    """Saves the LLMPhysicalPalette instance to a JSON file using PaletteProcessor."""
    try:
        if hasattr(llm_palette, 'to_dict'):
            palette_data = llm_palette
        else:
            # Create a PhysicalPalette from the old data format
            colors = []
            for color_name in llm_palette.colors_listed:
                colors.append(ColorData(
                    name=color_name,
                    hex_value="#000000"  
                ))
                
            palette_data = PhysicalPalette(
                name=llm_palette.physical_palette_name,
                colors=colors,
                source=llm_palette.palette_source,
                additional_notes=llm_palette.additional_notes
            )
        
        filepath = PaletteProcessor.save_palette(palette_data)
        if filepath:
            Gimp.message(f"Palette '{palette_data.name}' saved successfully.")
        
    except Exception as e:
        log_error("Failed to save palette to file", e)

def save_json_to_file(data, filename, directory=None):
    """
    Saves a given data dictionary to a JSON file.
    
    Args:
        data: Dictionary or object to save as JSON
        filename: Name of the file (without .json extension)
        directory: Optional directory path. If None, uses GIMP's plugin directory
        
    Returns:
        str: Path to the saved file or None if failed
    """
    try:
        from core.utils.file_io import get_plugin_storage_path, save_json_data
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
            
        # Determine the directory path
        if directory is None:
            directory = get_plugin_storage_path("", "colorBitMagic")
        
        # Full path to the file
        filepath = os.path.join(directory, filename)
        
        # Save the data using the centralized utility
        success = save_json_data(data, filepath, create_dirs=True, indent=2)
        
        if success:
            Gimp.message(f"Data saved successfully to '{filepath}'.")
            return filepath
        else:
            return None
            
    except Exception as e:
        log_error(f"Failed to save data to file '{filename}'", e)
        return None

def populate_palette_dropdown(builder):
    """Populates the GIMP palette dropdown."""
    palettes = Gimp.palettes_get_list("")
    populate_dropdown(builder, "paletteDropdown", palettes, "No palettes found")

def populate_physical_palette_dropdown(builder):
    """Populates the physical palette dropdown."""
    physical_palettes = get_all_physical_palettes()
    populate_dropdown(builder, "physicalPaletteDropdown", physical_palettes, "No physical palettes found")

def load_physical_palette_data(palette_name):
    """
    Load physical palette data from a JSON file.
    
    Args:
        palette_name: Name of the palette to load
        
    Returns:
        Dictionary containing palette data or a list of color names
    """
    try:
        # Get the path to the physical palette file using the centralized utility
        palette_path = get_plugin_storage_path(
            f"physical_palettes/{palette_name}.json", 
            "colorBitMagic"
        )
        
        # Load the JSON file using the centralized utility
        palette_data = load_json_data(
            palette_path, 
            default={"colors": [palette_name]}
        )
        
        # Return the palette data
        return palette_data
    except Exception as e:
        from gi.repository import Gimp
        # Log the error but don't raise it
        Gimp.message(f"Error: Failed to load palette: {palette_name} - Exception: {str(e)}")
        # Return a simple dictionary with the palette name as the only color
        return {"colors": [palette_name]}
    