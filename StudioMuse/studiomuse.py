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
import os

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import Gtk, GLib, Gio

from core.window_manager import WindowManager

class StudioMuse(Gimp.PlugIn):
    ## Plugin query definition
    def do_query_procedures(self):
        return ['studio-muse']

    def do_set_i18n(self, procname):
        return False

    ## Plugin create procedure
    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")
        procedure.set_menu_label("StudioMuse Suite")
        procedure.add_menu_path('<Image>/Extensions/StudioMuse/')
        
        procedure.set_documentation(
            "StudioMuse - Art tools suite",
            "A comprehensive suite of tools for digital artists",
            name)
        procedure.set_attribution("StudioMuse", "StudioMuse", "2024")

        return procedure

    ## Main execution logic
    def run(self, procedure, run_mode, image, drawables, config, run_data):
        try:
            GimpUi.init("studio-muse")
            
            window_manager = WindowManager()
            window_manager.load_main_ui()
            
            Gtk.main()

        except Exception as e:
            error_message = f"An error occurred: {e}"
            Gimp.message(error_message)
            print(error_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(StudioMuse.__gtype__, sys.argv)
