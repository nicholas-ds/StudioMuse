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
import traceback

# Get the absolute path to the plugin directory
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)  # Add plugin dir to path

# Add vendored packages
vendored_path = os.path.join(plugin_dir, "vendored")
if os.path.exists(vendored_path) and vendored_path not in sys.path:
    sys.path.insert(0, vendored_path)

# Add core module path explicitly
core_path = os.path.join(plugin_dir, "core")
if os.path.exists(core_path) and core_path not in sys.path:
    sys.path.insert(0, core_path)

try:
    import gi
    gi.require_version('Gimp', '3.0')
    from gi.repository import Gimp
    gi.require_version('GimpUi', '3.0')
    from gi.repository import GimpUi
    from gi.repository import Gtk, GLib, Gio
    
    # Only import after paths are set
    from core.window_manager import WindowManager
except Exception as e:
    # Print detailed import error to help with debugging
    error_trace = traceback.format_exc()
    print(f"Import error: {e}\n{error_trace}")
    # Exit early if we can't import basics
    sys.exit(1)

class StudioMuse(Gimp.PlugIn):
    ## Plugin query definition
    def do_query_procedures(self):
        return ['studio-muse', 'studio-muse-test']  # Add test procedure

    def do_set_i18n(self, procname):
        return False

    ## Plugin create procedure
    def do_create_procedure(self, name):
        if name == 'studio-muse-test':
            # Simple test procedure that doesn't rely on UI
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                self.run_test, None)
            procedure.set_image_types("*")
            procedure.set_menu_label("StudioMuse Test")
            procedure.add_menu_path('<Image>/Extensions/StudioMuse/')
            return procedure
        else:
            # Regular procedure
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                self.run, None)
            procedure.set_image_types("*")
            procedure.set_menu_label("StudioMuse Suite")
            procedure.add_menu_path('<Image>/Extensions/StudioMuse/')
            
            procedure.set_documentation(
                "StudioMuse - Art tools suite",
                "A comprehensive suite of tools for traditional artists",
                name)
            procedure.set_attribution("StudioMuse", "StudioMuse", "2024")
            return procedure

    ## Test procedure for basic functionality check
    def run_test(self, procedure, run_mode, image, drawables, config, run_data):
        try:
            Gimp.message("StudioMuse test procedure executed successfully!")
            print("StudioMuse test procedure executed successfully!")
            
            # Print path info for debugging
            Gimp.message(f"Python path: {sys.path}")
            
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
        except Exception as e:
            error_trace = traceback.format_exc()
            error_message = f"Test error: {e}\n{error_trace}"
            Gimp.message(error_message)
            print(error_message)
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

    ## Main execution logic
    def run(self, procedure, run_mode, image, drawables, config, run_data):
        try:
            # Initialize UI
            GimpUi.init("studio-muse")
            
            # Print debug info
            print(f"Plugin directory: {plugin_dir}")
            print(f"Python path: {sys.path}")
            
            try:
                window_manager = WindowManager()
                window_manager.load_main_ui()
                Gtk.main()
            except Exception as e:
                error_trace = traceback.format_exc()
                error_message = f"UI error: {e}\n{error_trace}"
                Gimp.message(error_message)
                print(error_message)
                return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        except Exception as e:
            error_trace = traceback.format_exc()
            error_message = f"An error occurred: {e}\n{error_trace}"
            Gimp.message(error_message)
            print(error_message)
            return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error())

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(StudioMuse.__gtype__, sys.argv)
