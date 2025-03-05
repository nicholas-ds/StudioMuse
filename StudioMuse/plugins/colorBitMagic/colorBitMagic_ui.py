import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from dialogs.home_dialog import HomeDialog

# Import our new models
from utils.palette_models import PaletteData, PhysicalPalette
from utils.palette_processor import PaletteProcessor

def show_color_bit_magic_dialog():
    """Shows the Color Bit Magic dialog."""
    HomeDialog().show()

# Add utility functions that can be used by dialog handlers
def get_available_palettes():
    """Get lists of both GIMP and physical palettes."""
    # Get GIMP palettes
    gimp_palettes = Gimp.list_palettes()
    
    # Get physical palettes - now uses PaletteProcessor directly
    physical_palettes = PaletteProcessor.get_all_physical_palettes()
    
    return {
        "gimp_palettes": gimp_palettes,
        "physical_palettes": physical_palettes
    }
