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

def connect_signals(builder, handler_object, custom_handlers=None):
    """
    Connect signals using builder with optional custom handlers.
    
    Args:
        builder: Gtk.Builder instance
        handler_object: Object containing signal handlers
        custom_handlers: Dictionary of widget_id -> [(signal_name, handler_function)]
    """
    # Connect standard signals through builder
    builder.connect_signals(handler_object)
    
    # Connect any custom handlers not defined in the XML
    if custom_handlers:
        for widget_id, handlers in custom_handlers.items():
            widget = builder.get_object(widget_id)
            if widget:
                for signal_name, handler in handlers:
                    widget.connect(signal_name, handler) 