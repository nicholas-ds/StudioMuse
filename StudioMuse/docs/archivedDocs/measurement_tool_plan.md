
# 📏 StudioMuse Measurement Tool – Project Plan

This plan outlines the architecture and implementation of the **Measurement Tool** module for the StudioMuse GIMP plugin. The goal is to build a reusable, modular, and DRY system for recording and organizing measurements using GIMP’s measurement tool API.

---

## 🧠 Objectives

- Integrate with `Gimp.MeasureTool` to extract segment lengths
- Save measurements with metadata: name, value, group, and optional image reference
- Allow users to rename, delete, and reorder measurements and groups
- Support persistence with JSON files under `measurements/`
- Use reusable GTK-based UI patterns compatible with other tools in the project
- Reuse existing utilities (e.g., `log_error`, JSON save/load, dropdown logic)

---

## 📁 Project Structure

```
plugins/colorBitMagic/
├── dialogs/
│   ├── measurement_dialog.py          # Measurement tool GTK interface
│
├── templates/
│   ├── measurement_tool.xml           # Glade UI file for the measurement tool
│
├── utils/
│   ├── dimensions_store.py            # Shared measurement storage & logic (load/save/reorder)
│   ├── measurement_models.py          # Data models for measurement objects
│   └── colorBitMagic_utils.py         # (Reuse JSON helpers, dropdown logic, log_error)
│
├── measurements/                      # Directory for saved dimension JSON files
│   ├── <image-name>.json              # Measurement files (per image or user session)
```

---

## 🧱 Components

### 1. **MeasurementDialog (GTK UI)**
- Reuses `BaseDialog`
- `GtkListBox` for showing dimensions with reordering
- Buttons for delete, rename, and save
- Preview pane for selected measurement (name + value)
- Optionally include √2 conversion button

### 2. **DimensionsStore**
- Load/save/reorder measurement lists as JSON
- Reuse `save_json_to_file()` from `colorBitMagic_utils.py`
- Methods:
  - `load_dimensions(image_name: str = None)`
  - `save_dimensions(dimensions: List[MeasurementData])`
  - `reorder_dimensions(order: List[int])`
  - `delete_dimension(index: int)`
  - `rename_dimension(index: int, new_name: str)`
  - `update_group(index: int, new_group: str)`

### 3. **MeasurementModels**
- `MeasurementData` with fields:
  - `name: str`
  - `value: float`
  - `group: str`
  - `image_name: Optional[str]`

---

## 🔁 Reuse Strategy

- ✅ Use `log_error()` from `colorBitMagic_utils.py`
- ✅ Use `save_json_to_file()` to avoid rewriting file persistence
- ✅ Use `BaseDialog` and `DialogManager` to manage UI
- ⬜ Consider modularizing `DropdownManager` for group selectors

---

## 🛠️ Future Extensibility

- Add "tag" system for measurements
- Link measurements to specific layers or guides
- Export grouped measurements as visual markup on the image
- Convert saved measurements into ratio templates

---

## 🚧 Initial Build Tasks

1. [ ] Create `measurement_models.py` with `MeasurementData`
2. [ ] Build `dimensions_store.py` with load/save/rename logic
3. [ ] Create `measurement_tool.xml` layout in Glade
4. [ ] Scaffold `MeasurementDialog` in `measurement_dialog.py`
5. [ ] Hook dialog into `HomeDialog` for testing
6. [ ] Test measurement reading from `Gimp.MeasureTool.get_segments()`

---

## 🧪 Testing

- Manual testing inside GIMP with mock measurement segments
- Unit tests for `dimensions_store.py` outside GIMP (pure Python)
- Validate file saving with long names and invalid characters

---

## 🧩 Dependencies

- Python 3.x
- GTK 3.x (via GIMP 3.0)
- No external dependencies required
