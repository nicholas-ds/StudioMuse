"""Utility functions for processing palettes without LLM dependency."""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from gi.repository import Gimp, Gegl
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from .palette_models import PaletteData, PhysicalPalette, ColorData
from core.utils.file_io import get_plugin_storage_path, save_json_data, load_json_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("palette_processor")

def log_error(message, exception=None):
    """Log an error to the console."""
    if exception:
        logger.error(f"{message}: {str(exception)}")
    else:
        logger.error(message)

class PaletteProcessor:
    """Utility class for palette processing operations."""
    
    @staticmethod
    def save_palette(palette: PaletteData, filename: str = None, base_dir: str = None) -> str:
        """Save a palette to file."""
        try:
            if base_dir is None:
                # Use the centralized utility to get the storage path
                base_dir = get_plugin_storage_path("physical_palettes", "colorBitMagic")
            
            # Use palette name as filename if none provided
            if filename is None:
                # Create a safe filename
                safe_name = "".join(c for c in palette.name if c.isalnum() or c in " _-").rstrip()
                safe_name = safe_name.replace(" ", "_")
                filename = f"{safe_name}.json"
            
            # Create full path
            filepath = os.path.join(base_dir, filename)
            
            # Use the centralized utility to save the file
            if hasattr(palette, 'to_json'):
                # First convert to dict if the palette object has custom serialization
                palette_dict = palette.to_dict() if hasattr(palette, 'to_dict') else json.loads(palette.to_json())
                save_success = save_json_data(palette_dict, filepath, create_dirs=True, indent=2)
            else:
                # If it's already a dict-like object
                save_success = save_json_data(palette, filepath, create_dirs=True, indent=2)
            
            if save_success:
                return filepath
            return None
        except Exception as e:
            log_error("Failed to save palette", e)
            return None
    
    @staticmethod
    def load_palette(palette_name: str, base_dir: str = None) -> PaletteData:
        """Load a palette from file."""
        try:
            if base_dir is None:
                # Use the centralized utility to get the storage path
                base_dir = get_plugin_storage_path("physical_palettes", "colorBitMagic")
            
            # Check if we received a filename with .json extension
            if palette_name.endswith('.json'):
                filename = palette_name
            else:
                filename = f"{palette_name}.json"
            
            # Create full path
            filepath = os.path.join(base_dir, filename)
            
            # Use the centralized utility to load the file
            data = load_json_data(filepath, default=None)
            
            # If loading failed, return None
            if data is None:
                return None
            
            # Determine palette type and create appropriate object
            if isinstance(data, dict) and data.get("palette_type") == "physical":
                return PhysicalPalette.from_dict(data)
            else:
                return PaletteData.from_dict(data)
        except Exception as e:
            log_error(f"Failed to load palette: {palette_name}", e)
            return None
    
    @staticmethod
    def convert_gegl_to_color_data(color: Gegl.Color, name: str = "Unnamed") -> ColorData:
        """Convert a Gegl.Color to a ColorData object."""
        try:
            # Extract RGBA values - already in 0.0-1.0 range
            rgba = color.get_rgba()
            
            # Store floating point RGB values with precision
            r = round(rgba[0], 3)
            g = round(rgba[1], 3)
            b = round(rgba[2], 3)
            
            # Create hex color (converting to 0-255 only for hex generation)
            hex_value = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            Gimp.message(f"Converted Gegl.Color to ColorData: {hex_value}")
            
            # Create RGB dict with floating point values
            rgb = {"r": r, "g": g, "b": b}
            Gimp.message(f"RGB values: {rgb}")
            
            # Return ColorData
            return ColorData(name=name, hex_value=hex_value, rgb=rgb)
        except Exception as e:
            log_error(f"Failed to convert Gegl.Color to ColorData", e)
            return ColorData(name=name, hex_value="#000000", rgb={"r": 0.0, "g": 0.0, "b": 0.0})
            
    @staticmethod
    def get_all_physical_palettes(base_dir: str = None) -> list:
        """Returns a list of all available physical palettes."""
        try:
            if base_dir is None:
                # Use the centralized utility to get the storage path
                base_dir = get_plugin_storage_path("physical_palettes", "colorBitMagic")
            
            # If directory doesn't exist, return empty list
            if not os.path.exists(base_dir):
                return []
            
            # Get all JSON files in the directory
            palette_files = [f for f in os.listdir(base_dir) if f.endswith('.json')]
            
            # Extract palette names (remove .json extension)
            palette_names = [os.path.splitext(f)[0] for f in palette_files]
            
            return sorted(palette_names)
        except Exception as e:
            log_error("Failed to get physical palettes", e)
            return [] 