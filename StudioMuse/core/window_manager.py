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
        # Add flag to track window state
        self.is_closing = False

    def load_main_ui(self):
        """
        Loads the main window shell and initializes UI components.
        Following the "Main UI Rule" from suiteUpdate.md for instant loading.
        """
        try:
            # Load the main shell and get both builder and widgets
            self.main_builder, self.main_window, self.main_stack = self.ui_loader.load_main_shell()
            
            # Connect destroy signal directly to the window
            self.main_window.connect("destroy", self.on_main_window_destroy)
            
            # Connect other main window signals
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
                    Gimp.message(f"Loading notebook: {category_id}")
                    notebook_builder = self.ui_loader.load_notebook(category_id)
                    if notebook_builder:
                        Gimp.message(f"Successfully loaded builder for {category_id}")
                        notebook = notebook_builder.get_object(f"{category_id}Notebook")
                        if notebook:
                            self.main_stack.add_titled(notebook, category_id, display_name)
                            self.notebooks[category_id] = notebook_builder
                            
                            # Connect signals based on category
                            if category_id == "analysis":
                                Gimp.message("Connecting analysis signals")
                                color_bit_magic = ColorBitMagic()
                                color_bit_magic.set_builder(notebook_builder)
                                self.tool_handlers["analysis"] = color_bit_magic
                                notebook_builder.connect_signals(color_bit_magic)
                            elif category_id == "structure":
                                Gimp.message("Attempting to connect structure signals")
                                try:
                                    # Try direct import first
                                    Gimp.message("Trying direct import of ProportiaUI")
                                    from tools.structure.proportia import ProportiaUI
                                    Gimp.message("Import successful")
                                    proportia_ui = ProportiaUI(notebook_builder)
                                    self.tool_handlers["structure"] = proportia_ui
                                    notebook_builder.connect_signals(proportia_ui)
                                    Gimp.message("Successfully connected proportia signals")
                                except ImportError as ie:
                                    # Log the specific import error
                                    error_msg = f"Import error details: {str(ie)}"
                                    Gimp.message(error_msg)
                                    print(error_msg)
                                    
                                    # Fall back to connecting signals to self
                                    Gimp.message("Falling back to default signal handling for structure")
                                    notebook_builder.connect_signals(self)
                            else:
                                notebook_builder.connect_signals(self)
                                
                        else:
                            error_msg = f"Could not find notebook object for {category_id}"
                            Gimp.message(error_msg)
                            print(error_msg)
                        
                except Exception as e:
                    import traceback
                    tb = traceback.format_exc()
                    error_msg = f"Error loading {category_id} notebook: {str(e)}\n{tb}"
                    Gimp.message(error_msg)
                    print(error_msg)
                    
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_msg = f"Error in load_notebooks: {str(e)}\n{tb}"
            Gimp.message(error_msg)
            print(error_msg)

    def on_main_window_destroy(self, widget):
        """Handle proper cleanup when window is destroyed"""
        try:
            if self.is_closing:
                return
            self.is_closing = True
            
            # Clean up tool handlers
            for handler in self.tool_handlers.values():
                if hasattr(handler, 'cleanup'):
                    handler.cleanup()
            
            # Clear references
            self.tool_handlers.clear()
            self.notebooks.clear()
            self.main_builder = None
            self.main_window = None
            self.main_stack = None
            
            # Quit the GTK main loop
            Gtk.main_quit()
            
        except Exception as e:
            print(f"Error during window cleanup: {e}")
            Gtk.main_quit()

    # Additional handlers from analysis_notebook.xml
    def on_close_clicked(self, button):
        print("Close button clicked")
        Gimp.message("Close button clicked") 