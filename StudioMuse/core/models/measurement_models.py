"""Data models for measurement and proportion tools."""
from datetime import datetime
import json
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field, asdict

@dataclass
class Measurement:
    """Model for a single measurement with metadata."""
    name: str
    value: float
    unit: str = "cm"
    group: str = "Default"
    visible: bool = True
    color: str = "#FFFFFF"
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Measurement":
        """Create a Measurement from a dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            value=float(data.get("value", 0.0)),
            unit=data.get("unit", "cm"),
            group=data.get("group", "Default"),
            visible=data.get("visible", True),
            color=data.get("color", "#FFFFFF"),
            notes=data.get("notes")
        )

@dataclass
class MeasurementCollection:
    """Model for a collection of related measurements."""
    name: str
    measurements: List[Measurement] = field(default_factory=list)
    description: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
    
    def add_measurement(self, measurement: Measurement) -> None:
        """Add a measurement to the collection."""
        self.measurements.append(measurement)
    
    def get_measurement_count(self) -> int:
        """Return the number of measurements in the collection."""
        return len(self.measurements)
    
    def get_groups(self) -> List[str]:
        """Get a unique list of measurement groups."""
        return sorted(list(set(m.group for m in self.measurements)))
    
    def get_measurements_by_group(self, group: str) -> List[Measurement]:
        """Get all measurements in a specific group."""
        return [m for m in self.measurements if m.group == group]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "measurements": [m.to_dict() for m in self.measurements],
            "description": self.description,
            "created_date": self.created_date,
            "version": self.version
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeasurementCollection":
        """Create a MeasurementCollection from a dictionary."""
        # Handle older format which was just a list of measurements
        if isinstance(data, list):
            measurements = [Measurement.from_dict(m) for m in data]
            return cls(
                name="Imported Measurements",
                measurements=measurements
            )
        
        # Handle collection format
        measurements = [Measurement.from_dict(m) for m in data.get("measurements", [])]
        return cls(
            name=data.get("name", "Unknown"),
            measurements=measurements,
            description=data.get("description"),
            created_date=data.get("created_date", datetime.now().isoformat()),
            version=data.get("version", "1.0.0")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "MeasurementCollection":
        """Create a MeasurementCollection from a JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            # Return empty collection on error
            return cls(name="Error Loading")
