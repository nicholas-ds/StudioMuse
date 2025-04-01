#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Gimp

class WindowManager:
    """Manages the main application window and UI components."""
    
    def __init__(self):
        self.builder = Gtk.Builder()
        self.main_window = None
        self.main_stack = None
        self.notebooks = {}

    def load_main_ui(self):
        """Load the main window shell and initialize UI components"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            notebook_categories = {
                "analysis": "Analysis",
                "structure": "Structure", 
                "visionlab": "VisionLab",
                "settings": "Settings"
            }
            
            for category_id, display_name in notebook_categories.items():
                try:
                    notebook_path = os.path.join(script_dir, "ui", category_id, f"{category_id}_notebook.xml")
                    
                    notebook_builder = Gtk.Builder()
                    notebook_builder.add_from_file(notebook_path)
                    
                    notebook = notebook_builder.get_object(f"{category_id}Notebook")
                    
                    if notebook:
                        self.main_stack.add_titled(notebook, category_id, display_name)
                        self.notebooks[category_id] = notebook_builder
                        notebook_builder.connect_signals(self)
                    else:
                        Gimp.message(f"Could not find notebook object for {category_id}")
                        
                except Exception as e:
                    Gimp.message(f"Error loading {category_id} notebook: {e}")
                    print(f"Error loading {category_id} notebook: {e}")
                    
        except Exception as e:
            Gimp.message(f"Error in load_notebooks: {e}")
            print(f"Error in load_notebooks: {e}")

    # Signal handlers
    def on_dmMainWindow_destroy(self, widget):
        Gtk.main_quit()
    
    def on_submit_clicked(self, button):
        Gimp.message("Submit button clicked")
    
    def on_add_physical_palette_clicked(self, button):
        Gimp.message("Add physical palette button clicked")
    
    def on_exit_clicked(self, button):
        self.main_window.destroy() 