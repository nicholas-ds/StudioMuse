import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gtk

def populate_palette_dropdown(builder):
    try:
        Gimp.message("Starting to populate palette dropdown...")

        # Get the dropdown widget
        palette_dropdown = builder.get_object("paletteDropdown")
        if palette_dropdown is None:
            raise ValueError("Could not find 'paletteDropdown' in the UI. Check XML IDs.")

        # Ensure it's a valid GtkComboBoxText
        if not isinstance(palette_dropdown, Gtk.ComboBoxText):
            raise TypeError(f"'paletteDropdown' is not a GtkComboBoxText but a {type(palette_dropdown)}.")

        # Clear existing items
        palette_dropdown.remove_all()

        # Retrieve the list of palettes
        palettes = Gimp.palettes_get_list("")
        if not palettes:
            Gimp.message("No palettes found.")
            palette_dropdown.append_text("No palettes found")
            return

        Gimp.message(f"Retrieved {len(palettes)} palettes.")

        # Extract and append palette names
        for palette in palettes:
            palette_name = palette.get_name() if hasattr(palette, 'get_name') else str(palette)
            palette_dropdown.append_text(palette_name)

        Gimp.message("Palette dropdown populated successfully.")

    except ValueError as ve:
        Gimp.message(f"ValueError in populate_palette_dropdown: {ve}")
        palette_dropdown.append_text("Error: Invalid UI element")

    except TypeError as te:
        Gimp.message(f"TypeError in populate_palette_dropdown: {te}")
        palette_dropdown.append_text("Error: Incorrect UI element type")

    except Exception as e:
        Gimp.message(f"Unexpected error in populate_palette_dropdown: {e}")
        palette_dropdown.append_text("Error loading palettes") 