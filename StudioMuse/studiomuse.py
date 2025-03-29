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

class StudioMuseApp:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.main_window = None
        self.main_stack = None
        self.notebooks = {}

    def load_main_ui(self):
        """Load the main window shell and initialize UI components"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_ui_path = os.path.join(script_dir, "ui", "main_window.xml")
            
            self.builder.add_from_file(main_ui_path)
            self.main_window = self.builder.get_object("mainWindow")
            self.main_stack = self.builder.get_object("mainStack")
            
            # Connect signals
            self.builder.connect_signals(self)
            
            # Load each notebook dynamically
            self.load_notebooks()
            
            # Show the window
            self.main_window.show_all()
            
        except Exception as e:
            Gimp.message(f"Error loading main UI: {e}")
            print(f"Error loading main UI: {e}")
    
    def load_notebooks(self):
        """Load each notebook from its respective XML file"""
        try:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Define notebook categories from suiteUpdate.md
            notebook_categories = {
                "analysis": "Analysis",
                "structure": "Structure", 
                "visionlab": "VisionLab",
                "settings": "Settings"
            }
            
            # Load each notebook XML and add it to the main stack
            for category_id, display_name in notebook_categories.items():
                try:
                    notebook_path = os.path.join(script_dir, "ui", category_id, f"{category_id}_notebook.xml")
                    
                    # Create a new builder for this notebook
                    notebook_builder = Gtk.Builder()
                    notebook_builder.add_from_file(notebook_path)
                    
                    # Get the notebook object
                    notebook = notebook_builder.get_object(f"{category_id}Notebook")
                    
                    if notebook:
                        # Add the notebook to the main stack
                        self.main_stack.add_titled(notebook, category_id, display_name)
                        
                        # Store the builder reference for later use
                        self.notebooks[category_id] = notebook_builder
                        
                        # Connect signals for this notebook
                        notebook_builder.connect_signals(self)
                    else:
                        Gimp.message(f"Could not find notebook object for {category_id}")
                        
                except Exception as e:
                    Gimp.message(f"Error loading {category_id} notebook: {e}")
                    print(f"Error loading {category_id} notebook: {e}")
                    
        except Exception as e:
            Gimp.message(f"Error in load_notebooks: {e}")
            print(f"Error in load_notebooks: {e}")
    
    # Signal handlers for main window
    def on_dmMainWindow_destroy(self, widget):
        Gtk.main_quit()
    
    # Sample handler for analysis notebook
    def on_submit_clicked(self, button):
        Gimp.message("Submit button clicked")
    
    def on_add_physical_palette_clicked(self, button):
        Gimp.message("Add physical palette button clicked")
    
    def on_exit_clicked(self, button):
        self.main_window.destroy()


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
            
            app = StudioMuseApp()
            app.load_main_ui()
            
            Gtk.main()

        except Exception as e:
            error_message = f"An error occurred: {e}"
            Gimp.message(error_message)
            print(error_message)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(StudioMuse.__gtype__, sys.argv)
