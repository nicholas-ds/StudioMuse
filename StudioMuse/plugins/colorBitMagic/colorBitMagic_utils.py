import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gtk, Gegl

import json
import os

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

def clean_and_verify_json(response_str):
    """
    Converts a JSON-like string from the LLM into a Python dictionary.

    Args:
        response_str (str): The response string from the LLM.

    Returns:
        dict: A dictionary representing the parsed JSON.
    """
    try:
        # Replace escaped newlines and unnecessary backslashes
        cleaned_str = response_str.replace('\\n', '').replace('\\"', '"')
        
        # Load as JSON
        json_data = json.loads(cleaned_str)
        return json_data

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return {}

def save_palette_to_file(llm_palette):
    """Saves the LLMPhysicalPalette instance to a JSON file."""
    palette_data = {
        "name": llm_palette.physical_palette_name,
        "colors": llm_palette.colors_listed,
        "num_colors": llm_palette.num_colors,
        "additional_notes": llm_palette.additional_notes,
    }
    
    # Save to a JSON file
    try:
        with open(f"{palette_data['name']}.json", "w") as f:
            json.dump(palette_data, f)
        Gimp.message(f"Palette '{palette_data['name']}' saved successfully.")
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
        # Get GIMP's user data directory
        gimp_dir = Gimp.directory()
        file_path = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes", f"{palette_name}.json")
        
        with open(file_path, 'r') as f:
            palette_data = json.load(f)
        return palette_data
    except Exception as e:
        log_error(f"Failed to load physical palette data for '{palette_name}'", e)
        return None
    