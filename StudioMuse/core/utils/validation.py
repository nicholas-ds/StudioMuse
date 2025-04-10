"""
Validation utilities for StudioMuse plugins.
Provides common input validation functions with standardized error messaging.
"""

from typing import Tuple, Union, Any, Optional
import re
from gi.repository import Gtk

def validate_required_field(value: Any, field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that a required field has a value.
    
    Args:
        value: The value to check
        field_name: Name of the field for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value and value != 0:  # Allow 0 as a valid value
        return False, f"{field_name} is required"
    return True, None

def validate_numeric(value: str, field_name: str, 
                    min_value: Optional[float] = None, 
                    max_value: Optional[float] = None) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validates that a value is a valid number and optionally within range.
    
    Args:
        value: The string value to check
        field_name: Name of the field for error message
        min_value: Optional minimum allowed value
        max_value: Optional maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message, parsed_value)
    """
    if not value:
        return False, f"{field_name} is required", None
    
    try:
        # Handle values with units (like "10.5 cm")
        parsed_value = float(value.split()[0]) if ' ' in value else float(value)
        
        if min_value is not None and parsed_value < min_value:
            return False, f"{field_name} must be at least {min_value}", None
            
        if max_value is not None and parsed_value > max_value:
            return False, f"{field_name} must not exceed {max_value}", None
            
        return True, None, parsed_value
    except (ValueError, IndexError):
        return False, f"{field_name} must be a valid number", None

def validate_and_show_errors(validations: list) -> bool:
    """
    Run a series of validations and show error message for the first failure.
    
    Args:
        validations: List of (is_valid, error_message) tuples
        
    Returns:
        True if all validations passed, False otherwise
    """
    for is_valid, error_message in validations:
        if not is_valid and error_message:
            from core.utils.ui import show_message
            show_message(error_message, Gtk.MessageType.WARNING)
            return False
    return True
