#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Gimp
from .utils.ui import UILoader  # New utility class we should create

class WindowManager:
    """
    Manages the main application window and UI components.
    Implements the suite-style UI architecture as defined in suiteUpdate.md
    """
    
    def __init__(self):
        self.ui_loader = UILoader()
        self.main_builder = None
        self.main_window = None
        self.main_stack = None
        self.notebooks = {}

    def load_main_ui(self):
        """
        Loads the main window shell and initializes UI components.
        Following the "Main UI Rule" from suiteUpdate.md for instant loading.
        """
        try:
            # Load the main shell and get both builder and widgets
            self.main_builder, self.main_window, self.main_stack = self.ui_loader.load_main_shell()
            
            # Connect main window signals
            self.main_builder.connect_signals(self)
            
            # Load notebooks
            self.load_notebooks()
            
            self.main_window.show_all()
            
        except Exception as e:
            Gimp.message(f"Error loading main UI: {e}")
            print(f"Error loading main UI: {e}")
    
    def load_notebooks(self):
        """
        Dynamically loads each notebook following the modular XML plan.
        Each notebook is loaded from its respective XML file in the ui/ directory.
        """
        try:
            notebook_categories = {
                "analysis": "Analysis",
                "structure": "Structure", 
                "visionlab": "VisionLab",
                "settings": "Settings"
            }
            
            for category_id, display_name in notebook_categories.items():
                try:
                    notebook_builder = self.ui_loader.load_notebook(category_id)
                    if notebook_builder:
                        notebook = notebook_builder.get_object(f"{category_id}Notebook")
                        if notebook:
                            self.main_stack.add_titled(notebook, category_id, display_name)
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

    # Signal handlers with debug prints
    def on_main_window_destroy(self, widget):
        """Handle window destruction and cleanup"""
        print("Window destroy signal received")
        try:
            # Add any cleanup code here
            # For example:
            # - Save any pending changes
            # - Close open file handles
            # - Stop any running background processes
            
            Gtk.main_quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Ensure we still quit even if cleanup fails
            Gtk.main_quit()
    
    def on_submit_clicked(self, button):
        print("Submit button clicked")
        Gimp.message("Submit button clicked")
    
    def on_add_physical_palette_clicked(self, button):
        print("Add physical palette button clicked")
        Gimp.message("Add physical palette button clicked")
    
    # Additional handlers from analysis_notebook.xml
    def on_save_clicked(self, button):
        print("Save button clicked")
        Gimp.message("Save button clicked")
    
    def on_generate_clicked(self, button):
        print("Generate button clicked")
        Gimp.message("Generate button clicked")
    
    def on_close_clicked(self, button):
        print("Close button clicked")
        Gimp.message("Close button clicked") 