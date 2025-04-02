"""Basic data models for palette processing."""
from datetime import datetime
import json
from typing import List, Dict, Optional, Any

class ColorData:
    """Model for a single color with metadata."""
    def __init__(self, name: str, hex_value: str, rgb: Optional[Dict[str, float]] = None, notes: Optional[str] = None):
        self.name = name
        self.hex_value = hex_value
        self.rgb = rgb or {}
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "hex_value": self.hex_value,
            "rgb": self.rgb,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColorData":
        """Create from dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            hex_value=data.get("hex_value", "#000000"),
            rgb=data.get("rgb", {}),
            notes=data.get("notes")
        )

class PaletteData:
    """Base model for all palette types."""
    def __init__(self, name: str, colors: List[ColorData], description: Optional[str] = None, 
                 created_date: Optional[str] = None, version: str = "1.0.0"):
        self.name = name
        self.colors = colors
        self.description = description
        self.created_date = created_date or datetime.now().isoformat()
        self.version = version
    
    def get_color_count(self) -> int:
        """Return the number of colors in the palette."""
        return len(self.colors)
    
    def add_color(self, color: ColorData) -> None:
        """Add a color to the palette."""
        self.colors.append(color)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert palette to a dictionary."""
        return {
            "name": self.name,
            "colors": [color.to_dict() for color in self.colors],
            "description": self.description,
            "created_date": self.created_date,
            "version": self.version
        }
    
    def to_json(self) -> str:
        """Convert palette to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaletteData":
        """Create a PaletteData from a dictionary."""
        colors = [ColorData.from_dict(color_data) for color_data in data.get("colors", [])]
        return cls(
            name=data.get("name", "Unknown"),
            colors=colors,
            description=data.get("description"),
            created_date=data.get("created_date"),
            version=data.get("version", "1.0.0")
        )

class PhysicalPalette(PaletteData):
    """Model for physical paint/color palettes."""
    def __init__(self, name: str, colors: List[ColorData], source: str, 
                 additional_notes: Optional[str] = None, manufacturer: Optional[str] = None,
                 **kwargs):
        super().__init__(name, colors, **kwargs)
        self.source = source
        self.additional_notes = additional_notes
        self.manufacturer = manufacturer
        self.palette_type = "physical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including physical palette specific fields."""
        data = super().to_dict()
        data.update({
            "source": self.source,
            "additional_notes": self.additional_notes,
            "manufacturer": self.manufacturer,
            "palette_type": self.palette_type
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhysicalPalette":
        """Create from dictionary."""
        palette = super().from_dict(data)
        return cls(
            name=palette.name,
            colors=palette.colors,
            source=data.get("source", "unknown"),
            additional_notes=data.get("additional_notes"),
            manufacturer=data.get("manufacturer"),
            description=palette.description,
            created_date=palette.created_date,
            version=palette.version
        ) 