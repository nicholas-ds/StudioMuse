#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import Gtk, GLib

class ColorBitMagic(Gimp.PlugIn):
    ## Plugin query definition
    def do_query_procedures(self):
        Gimp.message("Querying plugin procedures...")
        return ['color-bit-magic']

    def do_set_i18n(self, procname):
        return False

    ## Plugin create procedure
    def do_create_procedure(self, name):
        Gimp.message(f"Creating procedure: {name}")
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")
        procedure.set_menu_label("ColorBitMagic")
        procedure.add_menu_path('<Image>/Filters/ColorBitMagic/')
        
        procedure.set_documentation(
            "A color analysis and recommendation plugin",
            "Helps match colors in reference images to physical color palettes",
            name)
        procedure.set_attribution("StudioMuse", "StudioMuse", "2024")

        return procedure

    ## Main execution logic with a dialog box
    def run(self, procedure, run_mode, image, drawables, config, run_data):
        try:
            Gimp.message("Plugin executed. Initializing UI...")
            GimpUi.init("ColorBitMagic")

            # Create a dialog box
            dialog = Gtk.Dialog(title="ColorBitMagic", transient_for=None, flags=0)
            dialog.set_default_size(300, 200)

            # Add buttons to the dialog
            dialog.add_button("_OK", Gtk.ResponseType.OK)
            dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)

            # Add UI elements to the dialog
            label = Gtk.Label(label="Welcome to ColorBitMagic!\nThis tool will help match colors to palettes.")
            dialog.get_content_area().add(label)
            label.show()

            # Run the dialog and handle user interaction
            Gimp.message("Dialog created successfully, waiting for user input...")
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.OK:
                Gimp.message("User clicked OK!")
            elif response == Gtk.ResponseType.CANCEL:
                Gimp.message("User clicked Cancel.")

        except Exception as e:
            error_message = f"An error occurred: {e}"
            Gimp.message(error_message)
            print(error_message)  # Additional logging for external console/debug output

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(ColorBitMagic.__gtype__, sys.argv)
