import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gtk, Gegl

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

        # Get the list of palettes (now handling it correctly)
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
        if not colors:
            Gimp.message(f"No colors found in palette '{palette.get_name()}'.")
            return

        Gimp.message(f"Logging colors for palette '{palette.get_name()}':")
        for color in colors:
            if isinstance(color, Gegl.Color):  # Ensure it's a Gegl.Color object
                rgba = color.get_rgba()  # Get RGBA values
                Gimp.message(f"Color: R={rgba[0]:.3f}, G={rgba[1]:.3f}, B={rgba[2]:.3f}, A={rgba[3]:.3f}")
            else:
                Gimp.message(f"Unexpected color type: {type(color)}")

        # Free memory
        Gimp.color_array_free(colors)

        Gimp.message("log_palette_colormap() completed successfully.")

    except Exception as e:
        Gimp.message(f"Unexpected error in log_palette_colormap: {e}")