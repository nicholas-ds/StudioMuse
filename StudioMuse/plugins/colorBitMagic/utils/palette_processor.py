"""Utility functions for processing palettes without LLM dependency."""
import os
import json
from gi.repository import Gimp, Gegl

from .palette_models import PaletteData, PhysicalPalette, ColorData

def log_error(message, exception=None):
    """Helper function to log errors with optional exception details."""
    if exception:
        Gimp.message(f"Error: {message} - Exception: {exception}")
    else:
        Gimp.message(f"Error: {message}")

class PaletteProcessor:
    """Utility class for palette processing operations."""
    
    @staticmethod
    def save_palette(palette: PaletteData, filename: str = None, base_dir: str = None) -> str:
        """Save a palette to file."""
        try:
            if base_dir is None:
                # Get GIMP's user data directory
                gimp_dir = Gimp.directory()
                base_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
            
            # Make sure directory exists
            os.makedirs(base_dir, exist_ok=True)
            
            # Use palette name as filename if none provided
            if filename is None:
                # Create a safe filename
                safe_name = "".join(c for c in palette.name if c.isalnum() or c in " _-").rstrip()
                safe_name = safe_name.replace(" ", "_")
                filename = f"{safe_name}.json"
            
            # Create full path
            filepath = os.path.join(base_dir, filename)
            
            # Save to JSON file
            with open(filepath, 'w') as f:
                f.write(palette.to_json())
            
            return filepath
        except Exception as e:
            log_error("Failed to save palette", e)
            return None
    
    @staticmethod
    def load_palette(palette_name: str, base_dir: str = None) -> PaletteData:
        """Load a palette from file."""
        try:
            if base_dir is None:
                # Get GIMP's user data directory
                gimp_dir = Gimp.directory()
                base_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
            
            # Check if we received a filename with .json extension
            if palette_name.endswith('.json'):
                filename = palette_name
            else:
                filename = f"{palette_name}.json"
            
            # Create full path
            filepath = os.path.join(base_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                log_error(f"Palette file not found: {filepath}")
                return None
            
            # Load from JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Make sure we have a dictionary
            if not isinstance(data, dict):
                log_error(f"Invalid palette data format: {type(data)}")
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
            # Extract RGBA values
            rgba = color.get_rgba()
            
            # Convert to 0-255 range
            r = int(rgba[0] * 255)
            g = int(rgba[1] * 255)
            b = int(rgba[2] * 255)
            
            # Create hex color
            hex_value = f"#{r:02x}{g:02x}{b:02x}"
            Gimp.message(f"Converted Gegl.Color to ColorData: {hex_value}")
            
            # Create RGB dict
            rgb = {"r": r, "g": g, "b": b}
            Gimp.message(f"RGB values: {rgb}")
            
            # Return ColorData
            return ColorData(name=name, hex_value=hex_value, rgb=rgb)
        except Exception as e:
            log_error(f"Failed to convert Gegl.Color to ColorData", e)
            return ColorData(name=name, hex_value="#000000", rgb={"r": 0, "g": 0, "b": 0})
            
    @staticmethod
    def get_all_physical_palettes(base_dir: str = None) -> list:
        """Returns a list of all available physical palettes."""
        try:
            if base_dir is None:
                # Get GIMP's user data directory
                gimp_dir = Gimp.directory()
                base_dir = os.path.join(gimp_dir, "plug-ins", "colorBitMagic", "physical_palettes")
            
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