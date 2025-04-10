# Proportia Refactoring and Generalization Plan

This document outlines recommended refactors to improve maintainability, extensibility, and code reuse across the Proportia tool and the broader StudioMuse plugin suite.

---

## 1. Event and Signal Handling Generalization

**Problem:** Manual signal connection for each button or event leads to repetitive code.

**Solution:** Create a utility for generalized signal connection.

```python
def connect_button_click(button, callback, *args, **kwargs):
    button.connect("clicked", lambda widget: callback(*args, **kwargs))
```

---

## 2. Widget Value Extraction Utility

**Problem:** Widget-specific value retrieval is repeated and verbose.

**Solution:** Use a unified function to handle common widget value access.

```python
def get_widget_value(widget):
    if isinstance(widget, Gtk.ComboBoxText):
        return widget.get_active_text()
    elif isinstance(widget, Gtk.Entry):
        return widget.get_text().strip()
    elif isinstance(widget, Gtk.CheckButton):
        return widget.get_active()
    return None
```

---

## 3. Validation and Error Handling

**Problem:** Inline validation logic causes duplication and tight coupling with UI.

**Solution:** Centralize input validation into reusable functions.

```python
def validate_measurement_input(value):
    if not value:
        return False, "Input is empty"
    try:
        return float(value) > 0, ""
    except ValueError:
        return False, "Invalid number"
```

---

## 4. Abstracted File Path Handling

**Problem:** File paths are hardcoded and not future-proof.

**Solution:** Implement a shared `get_storage_path()` method.

```python
def get_storage_path(sub_path=""):
    base_path = os.path.join(Gimp.directory(), "plug-ins", "studiomuse", "measurements")
    return os.path.join(base_path, sub_path) if sub_path else base_path
```

---

## 5. Popup Creation and Management

**Problem:** Popup behavior is currently procedural and embedded.

**Solution:** Build a `PopupManager` class to handle dynamic dialogs.

```python
class PopupManager:
    def __init__(self, popup_xml_path):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(popup_xml_path)
        self.popup_window = self.builder.get_object("proportiaPopupWindow")

    def show_popup(self, x, y):
        self.popup_window.move(x, y)
        self.popup_window.show_all()

    def close_popup(self):
        self.popup_window.hide()
```

---

## 6. Reusable UI Component Loading

**Problem:** Repeated manual XML loading and parsing.

**Solution:** Centralize in a `UILoader` utility.

```python
class UILoader:
    @staticmethod
    def load_ui(xml_path):
        builder = Gtk.Builder()
        builder.add_from_file(xml_path)
        return builder
```

---

## 7. CSS Application Utility

**Problem:** CSS loading logic is tool-specific.

**Solution:** Create a generalized CSS loader.

```python
def load_css_for_plugin(css_path):
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(css_path)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
```

---

## 8. Structured Measurement Data Model

**Problem:** Dictionary-based data leads to inconsistency.

**Solution:** Use a data class for measurement structures.

```python
from dataclasses import dataclass

@dataclass
class Measurement:
    name: str
    value: float
    unit: str = "cm"
    group: str = "Default"
    visible: bool = True
    color: str = "#FFFFFF"
```

---

## 9. Event Bus for Cross-Tool Communication

**Problem:** No shared mechanism for tool interaction or messaging.

**Solution:** Implement a simple observer pattern.

```python
class EventBus:
    _subscribers = {}

    @classmethod
    def subscribe(cls, event, callback):
        cls._subscribers.setdefault(event, []).append(callback)

    @classmethod
    def publish(cls, event, data=None):
        for callback in cls._subscribers.get(event, []):
            callback(data)
```

---

## Next Steps

- Break out utility modules (`ui_utils.py`, `validation.py`, etc.)
- Replace embedded logic with reusable calls
- Begin implementing `PopupManager` and `Measurement` dataclass
- Refactor signal connections to use `connect_button_click()`
- Update storage to use `get_storage_path()`

These changes will improve modularity, simplify testing, and reduce future refactor scope as additional tools are integrated into the StudioMuse suite.

