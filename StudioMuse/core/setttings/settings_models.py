from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, ClassVar

class UnitType(Enum):
    """Valid measurement units"""
    CM = "cm"
    INCHES = "inches"
    PIXELS = "px"  # Add pixels as a unit type

@dataclass
class CanvasSettings:
    """Physical canvas dimensions and unit settings"""
    width: float
    height: float
    unit: UnitType
    pixel_width: Optional[float] = None
    pixel_height: Optional[float] = None
    physical_width: Optional[float] = None
    physical_height: Optional[float] = None

    # Class-level defaults
    DEFAULT_WIDTH: ClassVar[float] = 800.0
    DEFAULT_HEIGHT: ClassVar[float] = 600.0
    DEFAULT_UNIT: ClassVar[UnitType] = UnitType.CM

    @classmethod
    def get_default_settings(cls) -> 'CanvasSettings':
        """Create default settings instance"""
        return cls(
            width=cls.DEFAULT_WIDTH,
            height=cls.DEFAULT_HEIGHT,
            unit=cls.DEFAULT_UNIT
        )

    def validate(self) -> bool:
        """Validate canvas settings"""
        try:
            return (
                isinstance(self.width, (int, float)) and
                isinstance(self.height, (int, float)) and
                self.width > 0 and
                self.height > 0 and
                isinstance(self.unit, UnitType)
            )
        except Exception:
            return False

    def get_scale_factor(self) -> Optional[float]:
        """Calculate scale factor between physical and pixel dimensions"""
        if None in (self.pixel_width, self.pixel_height, self.physical_width, self.physical_height):
            return None
            
        # Use the larger dimension ratio to ensure everything fits
        width_ratio = self.pixel_width / self.physical_width
        height_ratio = self.pixel_height / self.physical_height
        return max(width_ratio, height_ratio)