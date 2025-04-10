"""
Scaling utility functions for measurement conversions.
These functions provide common mathematical scaling operations
that can be reused across different tools in the StudioMuse suite.
"""

import math
import json
import os
import logging
from typing import Callable, Dict, Union, Optional, List, Any

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Common mathematical constants used in artistic scaling
SQRT_2 = math.sqrt(2)
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
SQRT_3 = math.sqrt(3)

# Set up logging
logger = logging.getLogger("structure_utilities")

def scale_by_sqrt2(value: Union[int, float]) -> float:
    """
    Scale a value by the square root of 2 (approximately 1.414).
    
    This scaling is commonly used in:
    - Paper sizes (A4, A3, etc.)
    - Traditional artistic scaling for canvas doubling
    
    Args:
        value: The value to scale
        
    Returns:
        The value multiplied by √2
    """
    return value * SQRT_2

def save_data_to_json(data: Any, file_path: str) -> bool:
    """
    Save any JSON-serializable data structure to a file.
    
    Args:
        data: Any JSON-serializable data structure (dict, list, etc.)
        file_path: Path where to save the JSON file
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
        logger.info(f"Data successfully saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        return False

def load_json_data(file_path: str, default: Any = None) -> Any:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        default: Value to return if file doesn't exist or has errors
        
    Returns:
        Loaded data structure or default value if loading fails
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        else:
            logger.warning(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
    
    return default if default is not None else None

def load_measurements_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load measurements from a JSON file.
    
    Handles both new format (list of dictionaries) and old format (name->value mapping).
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of measurement dictionaries with normalized format
    """
    # Use the generic loader first
    data = load_json_data(file_path, default=[])
    
    # Process based on data structure
    if isinstance(data, list):
        # Ensure all items have required fields
        normalized_data = []
        for item in data:
            if 'name' not in item or 'value' not in item:
                continue
            # Create a normalized copy
            normalized_item = dict(item)
            # Ensure values are floats
            try:
                normalized_item['value'] = float(normalized_item['value'])
            except (ValueError, TypeError):
                normalized_item['value'] = 0.0
            # Add group if missing
            if 'group' not in normalized_item:
                normalized_item['group'] = 'Default'
            normalized_data.append(normalized_item)
        
        return normalized_data
    elif isinstance(data, dict):
        # Convert old format (dictionary) to list format
        result = []
        for name, value in data.items():
            try:
                result.append({
                    'name': name,
                    'value': float(value),
                    'group': 'Default'
                })
            except (ValueError, TypeError):
                result.append({
                    'name': name,
                    'value': 0.0,
                    'group': 'Default'
                })
        return result
    
    return []

def group_measurements(measurements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group measurements by their group property.
    
    Args:
        measurements: List of measurement dictionaries
        
    Returns:
        Dictionary mapping group names to lists of measurements
    """
    grouped = {}
    for measurement in measurements:
        group = measurement.get('group', 'Default')
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(measurement)
    
    return grouped

def get_unique_groups(measurements: List[Dict[str, Any]]) -> List[str]:
    """
    Get a sorted list of all unique group names in the measurements.
    
    Args:
        measurements: List of measurement dictionaries
        
    Returns:
        Sorted list of unique group names
    """
    groups = set()
    for measurement in measurements:
        groups.add(measurement.get('group', 'Default'))
    
    return sorted(list(groups))

def load_css_for_proportia() -> bool:
    """
    Load the CSS file for styling the Proportia interface.
    
    Returns:
        bool: True if CSS was loaded successfully, False otherwise
    """
    try:
        # Get the absolute file path of this module
        current_file = os.path.abspath(__file__)
        logger.info(f"Current file path: {current_file}")
        
        # Navigate to the project root (assuming standard folder structure)
        # This file is in core/utils/tools/structure/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
        logger.info(f"Project root path: {project_root}")
        
        # Build the path to the CSS file
        css_path = os.path.join(project_root, "ui", "structure", "proportia.css")
        logger.info(f"Looking for CSS file at: {css_path}")
        
        if not os.path.exists(css_path):
            logger.error(f"CSS file not found: {css_path}")
            
            # Create a basic CSS file if it doesn't exist
            try:
                os.makedirs(os.path.dirname(css_path), exist_ok=True)
                
                # Basic CSS content
                css_content = """/* Proportia Tool Styling */

/* Main title */
.proportia-title {
    font-size: 24px;
    font-weight: bold;
}

/* Action buttons */
.action-button {
    background-image: linear-gradient(to bottom, #3584e4, #1c71d8);
    color: white;
    border-radius: 4px;
    padding: 8px 12px;
}

/* Result display */
.result-display {
    background-color: alpha(#3584e4, 0.1);
    color: #333;
    font-weight: bold;
    padding: 8px;
    border-radius: 4px;
}
"""
                with open(css_path, 'w') as f:
                    f.write(css_content)
                logger.info(f"Created a basic CSS file at: {css_path}")
            except Exception as e:
                logger.error(f"Failed to create CSS file: {e}")
                return False
            
        # Load CSS provider
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(css_path)
        
        # Add CSS to default screen
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, 
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        logger.info(f"Successfully loaded CSS from {css_path}")
        return True
    except Exception as e:
        logger.error(f"Error loading CSS: {e}")
        return False

def apply_css_class(widget, css_class: str) -> None:
    """
    Apply a CSS class to a GTK widget.
    If the widget already has the class, it won't be added again.
    
    Args:
        widget: The GTK widget to apply the class to
        css_class: Name of the CSS class to apply
    """
    if widget is None:
        return
        
    style_context = widget.get_style_context()
    if not style_context.has_class(css_class):
        style_context.add_class(css_class)