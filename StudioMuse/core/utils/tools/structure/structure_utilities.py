
"""
Scaling utility functions for measurement conversions.
These functions provide common mathematical scaling operations
that can be reused across different tools in the StudioMuse suite.
"""

import math
from typing import Callable, Dict, Union, Optional

# Common mathematical constants used in artistic scaling
SQRT_2 = math.sqrt(2)
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
SQRT_3 = math.sqrt(3)

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