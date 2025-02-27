import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from dialogs.home_dialog import HomeDialog

def show_color_bit_magic_dialog():
    """Shows the Color Bit Magic dialog."""
    HomeDialog().show()
