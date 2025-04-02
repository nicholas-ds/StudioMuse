#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Gimp
from .utils.ui import UILoader  # New utility class we should create
from tools.analysis.colorbitmagic.colorBitMagic import ColorBitMagic  # Add this import

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
        self.tool_handlers = {}  # Add this to store tool handlers

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
                            
                            # Connect signals based on category
                            if category_id == "analysis":
                                color_bit_magic = ColorBitMagic()
                                color_bit_magic.set_builder(notebook_builder)
                                self.tool_handlers["analysis"] = color_bit_magic
                                notebook_builder.connect_signals(color_bit_magic)
                            else:
                                notebook_builder.connect_signals(self)
                                
                        else:
                            Gimp.message(f"Could not find notebook object for {category_id}")
                        
                except Exception as e:
                    Gimp.message(f"Error loading {category_id} notebook: {e}")
                    print(f"Error loading {category_id} notebook: {e}")
                    
        except Exception as e:
            Gimp.message(f"Error in load_notebooks: {e}")
            print(f"Error in load_notebooks: {e}")

    # Remove all analysis-related handlers from WindowManager
    def on_main_window_destroy(self, widget):
        print("Window destroy signal received")
        Gtk.main_quit()

    # Additional handlers from analysis_notebook.xml
    def on_close_clicked(self, button):
        print("Close button clicked")
        Gimp.message("Close button clicked") 