"""
Centralized file I/O utilities for StudioMuse.
Provides standardized functions for reading and writing JSON data
with consistent error handling and file path management.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union

# Set up logging
logger = logging.getLogger("file_io")

def get_plugin_storage_path(sub_path: str = "", plugin_name: str = None) -> str:
    """
    Get the standardized storage path for plugin data.
    
    Args:
        sub_path: Optional relative path within the plugin directory
        plugin_name: Optional plugin name for plugin-specific storage
        
    Returns:
        Absolute path to the requested storage location
    """
    from gi.repository import Gimp
    
    base_path = os.path.join(Gimp.directory(), "plug-ins")
    
    if plugin_name:
        base_path = os.path.join(base_path, plugin_name)
    
    if sub_path:
        return os.path.join(base_path, sub_path)
        
    return base_path

def save_json_data(
    data: Any, 
    file_path: str, 
    create_dirs: bool = True, 
    indent: int = None
) -> bool:
    """
    Save JSON-serializable data to a file with consistent error handling.
    
    Args:
        data: Any JSON-serializable data (dict, list, etc.)
        file_path: Full path to the target JSON file
        create_dirs: Whether to create parent directories if they don't exist
        indent: Number of spaces for pretty-printing (None for compact JSON)
        
    Returns:
        True if save was successful, False otherwise
    """
    try:
        # Ensure directory exists if requested
        if create_dirs:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
            
        logger.info(f"Data successfully saved to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        return False

def load_json_data(
    file_path: str, 
    default: Any = None,
    required_fields: List[str] = None
) -> Any:
    """
    Load and validate JSON data from a file with consistent error handling.
    
    Args:
        file_path: Path to the JSON file
        default: Value to return if file doesn't exist or has errors
        required_fields: Optional list of field names that must exist in the data
        
    Returns:
        Loaded data structure or default value if loading fails or validation fails
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return default
            
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate required fields if specified
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"Missing required fields in {file_path}: {missing_fields}")
                return default
                
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in {file_path}: {e}")
        return default
        
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return default

def normalize_measurement_data(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize measurement data to a consistent format.
    Handles both list format and dictionary format for backward compatibility.
    
    Args:
        data: Raw data loaded from a measurements file
        
    Returns:
        List of measurement dictionaries with normalized format
    """
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
