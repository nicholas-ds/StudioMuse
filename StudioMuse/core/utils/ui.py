#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Gimp

class UILoader:
    """Handles UI loading operations following the modular XML plan"""
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.main_builder = None  # Store the main builder
    
    def load_main_shell(self):
        """Loads the main window shell from main_window.xml"""
        self.main_builder = Gtk.Builder()
        main_ui_path = os.path.join(self.base_path, "ui", "main_window.xml")
        self.main_builder.add_from_file(main_ui_path)
        
        return (
            self.main_builder,
            self.main_builder.get_object("mainWindow"),
            self.main_builder.get_object("mainStack")
        )
    
    def load_notebook(self, category_id):
        """Loads a specific notebook from its XML file"""
        notebook_builder = Gtk.Builder()
        notebook_path = os.path.join(
            self.base_path, 
            "ui", 
            category_id, 
            f"{category_id}_notebook.xml"
        )
        
        notebook_builder.add_from_file(notebook_path)
        return notebook_builder 