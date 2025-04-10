#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk, Gimp, Gdk

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

def collect_widgets(builder, widget_ids):
    """
    Collect widgets by ID into a dictionary.
    
    Args:
        builder: Gtk.Builder instance
        widget_ids: List of widget IDs to collect
        
    Returns:
        Dictionary mapping widget IDs to their objects
    """
    widgets = {}
    for widget_id in widget_ids:
        widgets[widget_id] = builder.get_object(widget_id)
    return widgets 

def load_css(css_path):
    """
    Load CSS from specified path and apply to application.
    
    Args:
        css_path: Path to the CSS file
        
    Returns:
        True if CSS was loaded successfully, False otherwise
    """
    try:
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(css_path)
        
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, 
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        return True
    except Exception as e:
        print(f"Error loading CSS: {e}")
        return False 

def get_widget_value(widget):
    """
    Extract value from various widget types.
    
    Args:
        widget: Gtk widget to extract value from
        
    Returns:
        Extracted value or None if widget type is not supported
    """
    if isinstance(widget, Gtk.ComboBoxText):
        return widget.get_active_text()
    elif isinstance(widget, Gtk.Entry):
        return widget.get_text().strip()
    elif isinstance(widget, Gtk.CheckButton):
        return widget.get_active()
    elif isinstance(widget, Gtk.Label):
        return widget.get_text()
    return None 

def show_message(message, message_type=Gtk.MessageType.INFO):
    """
    Show a standard message dialog.
    
    Args:
        message: Message to display
        message_type: Type of message (INFO, WARNING, ERROR, etc.)
    """
    dialog = Gtk.MessageDialog(
        transient_for=None,
        flags=0,
        message_type=message_type,
        buttons=Gtk.ButtonsType.OK,
        text=message
    )
    dialog.run()
    dialog.destroy() 

def populate_dropdown(dropdown, items, default_text=None):
    """
    Populate a dropdown with items.
    
    Args:
        dropdown: Gtk.ComboBoxText instance
        items: List of items (strings or objects with get_name method)
        default_text: Optional text to add at beginning of dropdown
    """
    dropdown.remove_all()
    
    if default_text:
        dropdown.append_text(default_text)
        
    for item in items:
        text = item.get_name() if hasattr(item, 'get_name') else str(item)
        dropdown.append_text(text)
    
    # Select first item
    if dropdown.get_model() and len(dropdown.get_model()) > 0:
        dropdown.set_active(0) 

def cleanup_resources(instance):
    """
    Standard cleanup for UI resources.
    
    Args:
        instance: Object instance to clean up
    """
    # Clear collections
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if isinstance(attr, (list, dict)) and not attr_name.startswith('__'):
            if hasattr(attr, 'clear'):
                attr.clear()
    
    # Mark as inactive if applicable
    if hasattr(instance, 'is_active'):
        instance.is_active = False
    
    # Clear builder reference
    if hasattr(instance, 'builder'):
        instance.builder = None 