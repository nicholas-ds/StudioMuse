import logging
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import json
import os

from .settings_models import CanvasSettings, UnitType

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages application-wide settings"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._canvas_settings = None
            self._observers: List[Callable] = []
            self._initialized = True
            self._load_settings()
            logger.info("SettingsManager initialized")
    
    @property
    def canvas_settings(self) -> Optional[CanvasSettings]:
        """Get current canvas settings or None"""
        if self._canvas_settings is None:
            logger.info("No canvas settings available, using defaults")
            self._canvas_settings = CanvasSettings.get_default_settings()
            self._save_settings()
        return self._canvas_settings

    def set_canvas_settings(self, settings: CanvasSettings) -> bool:
        """Set and save canvas settings if valid"""
        if not settings.validate():
            logger.warning("Invalid canvas settings provided")
            return False
            
        self._canvas_settings = settings
        logger.info(f"Canvas settings updated: {settings}")
        self._notify_observers()
        self._save_settings()
        return True

    def add_observer(self, callback: Callable) -> None:
        """Add an observer to be notified of setting changes"""
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Added settings observer: {callback}")

    def _notify_observers(self) -> None:
        """Notify all observers of settings changes"""
        for observer in self._observers:
            try:
                observer()
            except Exception as e:
                logger.error(f"Error notifying observer {observer}: {e}")

    def _get_settings_path(self) -> Path:
        """Get the settings file path"""
        from core.utils.file_io import get_plugin_storage_path
        path = Path(get_plugin_storage_path("settings.json", "studiomuse"))
        logger.debug(f"Settings file path: {path}")
        return path

    def _save_settings(self) -> None:
        """Save settings to file"""
        if not self._canvas_settings:
            logger.warning("No settings to save")
            return

        path = self._get_settings_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            settings_data = {
                'width': self._canvas_settings.width,
                'height': self._canvas_settings.height,
                'unit': self._canvas_settings.unit.value
            }
            with open(path, 'w') as f:
                json.dump(settings_data, f, indent=2)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def _load_settings(self) -> None:
        """Load settings from file or use defaults"""
        path = self._get_settings_path()
        try:
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                    self._canvas_settings = CanvasSettings(
                        width=float(data['width']),
                        height=float(data['height']),
                        unit=UnitType(data['unit'])
                    )
                logger.info(f"Settings loaded successfully: {data}")
            else:
                logger.info("No settings file found, using defaults")
                self._canvas_settings = CanvasSettings.get_default_settings()
                self._save_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self._canvas_settings = CanvasSettings.get_default_settings()
