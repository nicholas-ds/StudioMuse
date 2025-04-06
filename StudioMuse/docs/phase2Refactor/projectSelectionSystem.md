# StudioMuse Plugin Suite — Project Selection System

## 🎯 Goal

Enable users to select the **current active art project** from the main UI to keep all tools (e.g., ColorBitMagic, Proportia) scoped to project-specific data, preventing clutter and improving UX.

---

## 🧱 Overview

- Display a **project selector** next to the `GtkStackSwitcher` at the top of the main window.
- Use project-specific directories to store palettes, measurements, etc.
- Provide persistence via `config/user.json` to auto-load the last selected project.

---

## 🖼️ UI Changes

### File: `main_window.xml`

Wrap the `GtkStackSwitcher` in a horizontal box:

```xml
<child>
  <object class="GtkBox" id="topBar">
    <property name="orientation">horizontal</property>
    <property name="spacing">10</property>
    <property name="halign">fill</property>
    <property name="margin-top">10</property>
    <property name="margin-bottom">10</property>
    <child>
      <object class="GtkStackSwitcher" id="mainStackSwitcher">
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="stack">mainStack</property>
      </object>
    </child>
    <child>
      <object class="GtkComboBoxText" id="projectSelector">
        <property name="visible">True</property>
        <property name="tooltip-text">Select Active Project</property>
      </object>
    </child>
  </object>
</child>
```

---

## 📁 Project Storage Structure

All project-specific data will live in:

```
~/.config/GIMP/3.0/studiomuse/projects/{project_id}/
```

### Example:
```
projects/
  sun_ra_portrait/
    physical_palettes/
    dimensions.json
  walden_thoreau/
    ...
```

---

## 🧠 ProjectContext Module

```python
class ProjectContext:
    _active_project_id = None

    @classmethod
    def load_active_project(cls):
        # Load from config/user.json
        pass

    @classmethod
    def set_active_project(cls, project_id: str):
        cls._active_project_id = project_id
        # Save to config/user.json
        # Notify listeners if needed

    @classmethod
    def get_active_project_id(cls):
        return cls._active_project_id

    @classmethod
    def get_active_project_path(cls):
        return os.path.join(Gimp.directory(), "plug-ins", "studiomuse", "projects", cls._active_project_id)
```

---

## 🤔 Logic Summary

- Populate dropdown with available project names.
- When user selects a project:
  - Set it as the active context.
  - Plugins automatically read/write to that project’s data folder.
- On startup:
  - Load last selected project.
  - If none, prompt user to select or create one.

---

## 💡 Optional Enhancements

- "[+ New Project]" dropdown item opens a popup with:
  - Project Name
  - Description (optional)
- Metadata stored in `project_meta.json`
- “Switch Project” menu command
- Recent Projects list in dropdown

---

## 📌 Files Touched

- `main_window.xml`: UI changes
- `window_manager.py`: Load and bind dropdown
- `project_context.py`: New utility class
- `config/user.json`: Store last used project ID
- Plugins: Update file I/O to use `ProjectContext.get_active_project_path()`

---

## 🧩 Additional Planning Summary

This integration fits **seamlessly** into the current architecture but introduces a few important considerations:

### ✅ Why It Works Well
- Modular file I/O already supports redirection to project-specific folders
- Centralized context via `ProjectContext`
- Main UI layout easily accommodates selector next to stack switcher

### ⚠️ What to Plan For

| Area                    | Risk   | Solution                                |
|-------------------------|--------|------------------------------------------|
| Plugin data paths       | Low    | Use `ProjectContext.get_active_path()`   |
| Legacy data             | Medium | Auto-migrate or wrap in fallback         |
| Refresh-on-change       | Medium | Add project switch notification hook     |
| User errors (dup names) | Low    | Validate project name input              |
| UX disruption           | Low    | Keep UI simple, default project pre-loaded |

---

