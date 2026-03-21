import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import logging
from typing import Dict, Any

from .settings_manager import SettingsManager
from .settings_models import CanvasSettings, UnitType

logger = logging.getLogger(__name__)

class SettingsController:
    """Controls settings UI interaction"""
    
    def __init__(self, builder: Gtk.Builder, settings_manager: SettingsManager):
        self.builder = builder
        self.settings_manager = settings_manager
        
        self.widgets = {
            'width': builder.get_object('canvasPhysicalWidth'),
            'height': builder.get_object('canvasPhysicalHeight'),
            'unit': builder.get_object('canvasPhysicalUnit')
        }
        
        self._init_ui()
        self._connect_signals()
        logger.info("Settings controller initialized")

    def _init_ui(self) -> None:
        """Initialize UI with current settings or defaults"""
        # Initialize unit dropdown
        for unit in UnitType:
            self.widgets['unit'].append_text(unit.value)
            
        # Load current settings or defaults
        settings = self.settings_manager.canvas_settings or CanvasSettings.get_default_settings()
        self._update_ui_from_settings(settings)

    def _update_ui_from_settings(self, settings: CanvasSettings) -> None:
        """Update UI widgets with settings values"""
        self.widgets['width'].set_text(str(settings.width))
        self.widgets['height'].set_text(str(settings.height))
        self.widgets['unit'].set_active_id(settings.unit.value)
        logger.info(f"UI updated with settings: {settings}")

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers"""
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, (Gtk.Entry, Gtk.ComboBoxText)):
                widget.connect('changed', self._on_setting_changed)
                logger.debug(f"Connected signal for {widget_name}")

    def _get_current_values(self) -> Dict[str, Any]:
        """Get current values from UI widgets"""
        return {
            'width': self.widgets['width'].get_text() or "0",
            'height': self.widgets['height'].get_text() or "0",
            'unit': self.widgets['unit'].get_active_text()
        }

    def _on_setting_changed(self, widget: Gtk.Widget) -> None:
        """Handle settings changes with debouncing"""
        try:
            values = self._get_current_values()
            
            # Basic validation before attempting conversion
            if not all(values.values()):
                logger.debug("Waiting for all values to be set")
                return

            try:
                width = float(values['width'])
                height = float(values['height'])
                unit = UnitType(values['unit'])
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid input values: {e}")
                return
            
            if width <= 0 or height <= 0:
                logger.warning("Width and height must be positive")
                return

            settings = CanvasSettings(
                width=width,
                height=height,
                unit=unit
            )

            if self.settings_manager.set_canvas_settings(settings):
                logger.info(f"Settings updated successfully: {settings}")
            else:
                logger.warning("Failed to update settings - validation failed")

        except Exception as e:
            logger.error(f"Error updating settings: {e}")
