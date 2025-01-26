#!/usr/bin/env python

import gtk
from gimpfu import *

class ColorBitMagicDialog(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("ColorBitMagic")
        
        # Ensure window comes to the front
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_keep_above(True)
        
        # Allow resizing of the window
        self.set_resizable(True)
        
        # Create a VBox to organize the dropdown and text view
        vbox = gtk.VBox(spacing=6)
        
        # Create dropdown (ComboBox) for palettes
        self.palette_dropdown = gtk.combo_box_new_text()
        self.update_palette_dropdown()
        self.palette_dropdown.connect("changed", self.on_palette_selected)
        vbox.pack_start(self.palette_dropdown, False, False, 0)
        
        # Create scrolled window for detailed palette info
        self.scrolled_window = gtk.ScrolledWindow()
        self.color_list_store = gtk.ListStore(str, str, str, str)  # Order, RGB, HSV, Hex
        self.color_tree_view = gtk.TreeView(self.color_list_store)
        
        # Add columns to the tree view
        self.add_tree_view_column("Order", 0)
        self.add_tree_view_column("RGB", 1)
        self.add_tree_view_column("HSV", 2)
        self.add_tree_view_column("Hex", 3)
        
        self.scrolled_window.add(self.color_tree_view)
        vbox.pack_start(self.scrolled_window, True, True, 0)
        
        self.add(vbox)
        
        # Set size
        self.set_default_size(400, 300)
        
        self.show_all()

    def update_palette_dropdown(self):
        try:
            self.palette_dropdown.get_model().clear()
            palette_names = pdb.gimp_palettes_get_list("")[1]
            
            if not palette_names:
                self.palette_dropdown.append_text("No palettes found")
            else:
                for name in palette_names:
                    self.palette_dropdown.append_text(name)
        except Exception as e:
            self.palette_dropdown.append_text("Error loading palettes")

    def add_tree_view_column(self, title, column_id):
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(title, renderer, text=column_id)
        self.color_tree_view.append_column(column)

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        diff = mx - mn

        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / diff) + 240) % 360

        s = 0 if mx == 0 else (diff / mx)
        v = mx

        return h, s, v

    def on_palette_selected(self, widget):
        active_text = widget.get_active_text()
        self.color_list_store.clear()

        if active_text and active_text != "No palettes found" and active_text != "Error loading palettes":
            try:
                colors = pdb.gimp_palette_get_colors(active_text)[1]
                for idx, color in enumerate(colors):
                    r, g, b = color[0], color[1], color[2]
                    h, s, v = self.rgb_to_hsv(r, g, b)
                    hex_color = "#%02X%02X%02X" % (r, g, b)
                    self.color_list_store.append([
                        str(idx + 1),
                        "RGB(%d, %d, %d)" % (r, g, b),
                        "HSV(%.2f, %.2f, %.2f)" % (h, s, v),
                        hex_color
                    ])
            except RuntimeError as e:
                print("Error getting colors for %s: %s" % (active_text, str(e)))
            except Exception as e:
                print("Error: %s" % str(e))


dialog = None

def plugin_main():
    global dialog
    
    if not dialog:
        dialog = ColorBitMagicDialog()
        dialog.connect("destroy", gtk.main_quit)
        
    dialog.show_all()
    gtk.main()

register(
    "python_fu_colorbitmagic",
    "Color analysis tool",
    "Shows color palette information",
    "StudioMuse",
    "StudioMuse",
    "2024",
    "ColorBitMagic",
    "",
    [],
    [],
    plugin_main,
    menu="<Toolbox>/Windows/Dockable Dialogs/ColorBitMagic"
)

main()
