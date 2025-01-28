import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import Gtk

def greet_from_ui():
    Gimp.message("Hello from the UI module!")

def show_color_bit_magic_dialog():
    Gimp.message("Initializing UI...")

    # Create a dialog box
    dialog = Gtk.Dialog(title="ColorBitMagic", transient_for=None, flags=0)
    dialog.set_default_size(400, 300)

    # Add instructions label
    label = Gtk.Label(label="Select a palette to match:")
    label.set_margin_top(20)  # Add 20px padding at the top
    label.set_margin_bottom(10)  # Add 10px padding below the label
    label.set_margin_start(10)  # Add 10px padding on the left
    label.set_margin_end(10)  # Add 10px padding on the right
    dialog.get_content_area().add(label)
    label.show()

    # Create dropdown and populate with palette names
    combo_box = Gtk.ComboBoxText()
    palette_list = Gimp.palettes_get_list("")  # Retrieve palettes
    for palette in palette_list:
        combo_box.append_text(palette.get_name())  # Add palette names to dropdown

    dialog.get_content_area().add(combo_box)
    combo_box.show()

    # Add dialog buttons
    dialog.add_button("_OK", Gtk.ResponseType.OK)
    dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)

    # Run the dialog and handle user interaction
    Gimp.message("Dialog created successfully, waiting for user input...")
    response = dialog.run()
    selected_palette = combo_box.get_active_text()  # Get selected palette
    dialog.destroy()

    if response == Gtk.ResponseType.OK:
        if selected_palette:
            Gimp.message(f"Selected Palette: {selected_palette}")
        else:
            Gimp.message("No palette selected.")
    elif response == Gtk.ResponseType.CANCEL:
        Gimp.message("Operation canceled.")