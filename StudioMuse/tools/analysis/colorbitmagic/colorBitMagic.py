#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gimp
from core.utils.api_client import api_client
from core.utils.colorBitMagic_utils import (
    save_json_to_file,
    populate_palette_dropdown,
    populate_physical_palette_dropdown,
    load_physical_palette_data,
    get_palette_colors,
    log_error
)
import json
import os

class ColorBitMagic:
    """
    Handles the analysis functionality for color palette operations.
    Controls the UI interactions for the Analysis notebook tab.
    """
    
    def __init__(self):
        """Initialize the ColorBitMagic tool."""
        self.builder = None
        self.palette_name = None
        self.results_view = None
        self.widgets = {}  # Store widget references
        self.color_results = []  # Store color mapping results

    def set_builder(self, builder):
        """
        Set the GTK builder instance for this tool.
        
        Args:
            builder (Gtk.Builder): The builder instance containing analysis UI elements
        """
        self.builder = builder
        # Initialize widget references
        widget_ids = [
            'submitButton',
            'paletteDropdown',
            'physicalPaletteDropdown',
            'paletteNameEntry',
            'resultsTextView',
            'rightPanel',
            'colorSwatch'
        ]
        for widget_id in widget_ids:
            self.widgets[widget_id] = self.builder.get_object(widget_id)
            
        # Initialize dropdowns
        populate_palette_dropdown(self.builder)
        populate_physical_palette_dropdown(self.builder)

    def log_message(self, message, level="info"):
        """Centralized logging function"""
        Gimp.message(message)

    # Signal handlers for Analysis notebook
    def on_submit_clicked(self, button):
        """Handle submission of palette comparison."""
        self.log_message("Submit button clicked. Loading selected palettes...")
        
        # Get selected palettes from dropdowns
        selected_palette = self.widgets['paletteDropdown'].get_active_text()
        selected_physical_palette = self.widgets['physicalPaletteDropdown'].get_active_text()
        
        if not selected_palette or not selected_physical_palette:
            self.log_message("Please select both a GIMP palette and a physical palette.")
            return
            
        try:
            # Get palette data
            gimp_palette_colors = get_palette_colors(selected_palette)
            if not gimp_palette_colors:
                self.log_message(f"Failed to load GIMP palette: {selected_palette}")
                return
                
            # Load physical palette data
            physical_palette_data = load_physical_palette_data(selected_physical_palette)
            if not physical_palette_data:
                self.log_message(f"Failed to load physical palette: {selected_physical_palette}")
                return
                
            # Extract physical color names
            physical_color_names = self._extract_physical_color_names(physical_palette_data)
            
            # Process through API
            try:
                response = api_client.demystify_palette(
                    gimp_palette_colors=gimp_palette_colors,
                    physical_palette_data=physical_color_names
                )
                
                if response.get("success"):
                    result = response.get("response")
                    formatted_result = self.format_palette_mapping(result)
                    self.display_results(formatted_result, "resultsTextView")
                else:
                    error_msg = response.get("error", "Unknown error")
                    self.log_message(f"API error: {error_msg}")
                    
            except Exception as e:
                log_error("API communication error", e)
                self.log_message(f"Error: {str(e)}")
                
        except Exception as e:
            log_error("Error in palette demystification", e)
            self.log_message(f"Error: {str(e)}")
    
    def on_add_physical_palette_clicked(self, button):
        """Handle adding a new physical palette."""
        print("Add physical palette button clicked")
        if self.widgets.get('paletteNameEntry'):
            palette_name = self.widgets['paletteNameEntry'].get_text()
            Gimp.message(f"Adding new palette: {palette_name}")
        else:
            Gimp.message("Error: Palette name entry not found")
    
    def on_save_clicked(self, button):
        """Handle saving the current palette configuration."""
        print("Save button clicked")
        Gimp.message("Saving palette configuration...")
    
    def on_generate_clicked(self, button):
        """Handle palette generation request."""
        print("Generate button clicked")
        Gimp.message("Generating palette...")
    
    def on_close_clicked(self, button):
        """Handle closing the current view."""
        print("Close button clicked")
        Gimp.message("Closing current view...")
