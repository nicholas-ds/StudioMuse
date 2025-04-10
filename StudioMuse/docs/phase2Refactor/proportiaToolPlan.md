# Proportia Measurement Tool — Planning Document

## Overview

**Proportia** is a measurement and scaling tool designed to work within the GIMP 3.0 plugin suite *StudioMuse*. It enables artists to capture, annotate, organize, and scale dimensions from digital images to real-world canvas sizes. Inspired by the `scaleArt.py` prototype, it brings structured canvas planning and measuring directly into GIMP with future AI integration.

---

## Implementation Status

### ✅ Completed Features
- Structured data models with `Measurement` and `MeasurementCollection` classes
- File path standardization using centralized utilities
- JSON persistence with proper error handling
- Grouping and organization of measurements
- Inline measurement editing
- √2 scaling conversion
- Input validation with shared utilities
- Consistent CSS styling with shared management
- UI architecture improvements (widget collection, signal handling)

### 🚧 In Progress / Planned Features
- Canvas measurement capture mode
- Visual overlay layer generation
- Project selection integration
- Advanced measurement tools
- AI-assisted features

---

## Goals

- Assist artists in accurately translating image proportions to physical formats.
- Capture GIMP vector measurements or manual values.
- Organize measurements by group (e.g., Face, Body, Frame).
- Provide conversion utilities (e.g., √2 multiplier, ratio scaling).
- Visualize measurements on canvas with toggleable overlays.
- Support persistent data with import/export.

---

## Core Features

### 🧹 Measurement Input ✅
- Add name, value, and group for each measurement.
- Optionally input real-world unit (cm, in).
- **IMPLEMENTED**: Basic measurement input, validation, and storage.

### 📏 Automatic Capture 🚧
- Extract measurements from GIMP's vectors and guides.
- Auto-name common features (future AI assist).
- **PLANNED**: Capture mode implementation.

### 📂 Grouping & Organization ✅
- Measurements are grouped (Face, Frame, etc).
- Groups are collapsible and reorderable.
- Drag-and-drop measurement sorting.
- **IMPLEMENTED**: Group functionality with collapsible UI.

### 🛠️ Conversion Tools ⚙️
- √2 multiplier. ✅
- Golden ratio checker. 🚧
- Ratio-based resizing (canvas-to-image scaling). 🚧
- **IMPLEMENTED**: Basic √2 scaling.

### 🖼️ Visual Layer Overlay 🚧
- Toggleable annotation layer on the image.
- Show measurement lines with labels and dimensions.
- Each group has its own dedicated overlay layer.
- User can choose line color and thickness.
- **PLANNED**: Next implementation priority.

### 💾 Persistence ✅
- Save and load from JSON.
- Import from existing `saved_dimensions.json`.
- Sync changes live (optionally).
- **IMPLEMENTED**: Full JSON persistence with error handling.

---

## Measurement Mode Workflow

### Activation 🚧
- User clicks a button to enter **Measurement Mode**.
- In this mode, clicking two points on the image creates a measurement.
- **PLANNED**: Upcoming implementation.

### Capture Flow 🚧
- A line is drawn between the two points.
- When the user completes the second click, a **popup dialog appears near the cursor** with:
  - The detected pixel measurement: `112 px`
  - Converted real-world dimensions: `3.5 cm` (based on current scaling settings)
  - A dropdown for selecting or creating a measurement group
  - Two action buttons:
    - **[Save]**: Finalizes the measurement and adds it to the selected group
    - **[Cancel]**: Discards the current measurement, allowing the user to start over
- The popup is positioned contextually near where the measurement was taken, minimizing mouse travel
- Once saved, the measurement is added to the corresponding group and its markup layer
- If a markup layer doesn't exist for the group, it is auto-created.
- **PLANNED**: Core functionality for next implementation phase.

### Overlay Layers 🚧
- Each group has its **own markup layer** (e.g., "Face Measurements").
- Lines are added to the corresponding group layer.
- User can toggle visibility of any group's overlay.
- **PLANNED**: To be implemented with measurement mode.

### Customization 🚧
- Line color and thickness are configurable.
- Optional: Add **label text** (e.g., "Chin to NoseTip") near each line.
- **PLANNED**: UI elements in place but functionality pending.

---

## Measurement Entry Popup UI 🚧

- When the user finishes their second click, a popup window appears near the cursor.
- This window contains:
  - `Gtk.Entry`: Measurement name
  - `Gtk.ComboBoxText`: Select or create a group
  - `Gtk.CheckButton`: Toggle to add visual label
  - `Gtk.ColorButton`: Choose line color
  - `Gtk.Scale` or `Gtk.SpinButton`: Select line thickness
  - `Gtk.ButtonBox`: [Save] and [Cancel] buttons
- The popup is positioned with `Gtk.Window(type=Gtk.WindowType.POPUP)` and `.move(x, y)` based on the click.
- If popup fails, fallback to sidebar input with pre-filled data.
- **PLANNED**: Core popup functionality designed but not yet implemented.

---

## Smart Additions

### 1. "Active Group" Concept ✅
- Active group is selected before measurement.
- Ensures markup layer context is known.
- **IMPLEMENTED**: Group dropdown selection.

  ```text
  🟢 Measuring in: [Face ▼] | [Set Active Group]
  ```

### 2. Visual Marker Label (Optional) 🚧
- Toggle to display text label alongside measurement line.
- Helps with documentation and clarity.
- **PLANNED**: To be implemented with overlay system.

### 3. Measurement Preview (Before Save) 🚧
- Show preview of line and distance before saving.
- Prevents clutter from accidental or discarded lines.
- **PLANNED**: Part of measurement mode.

### 4. Measurement Mode Exit 🚧
- User can choose to:
  - Exit after each measurement automatically
  - Or click [Exit Measurement Mode] manually
- **PLANNED**: Part of measurement mode implementation.

### 5. Group Layer Safeguards 🚧
- If a group's markup layer is missing, warn and offer to recreate.
- Prevent silent failure or misplacement of lines.
- **PLANNED**: Part of overlay system.

### 6. Optional Future Tools 🚧
- Snap to guides
- Lock overlay layer
- Export markup as image
- AI suggestions for measurement names
- **PLANNED**: Future enhancements after core functionality.

---

## Future Integration Considerations

To ensure Proportia works seamlessly with the upcoming Project Selection System and Palette Generator, we need to build forward-compatibility into the initial design. This preemptive planning will minimize refactoring later and create a more cohesive experience across the StudioMuse suite.

### 🌟 Project Selection System Integration

#### 1. Path Abstraction Layer ✅
- Implement a `get_storage_path()` method that centralizes all file path logic
- This approach prevents hardcoding paths throughout the codebase
- **IMPLEMENTED**: Using `get_plugin_storage_path()` from `file_io.py`

```python
def get_measurements_file_path(self) -> str:
    """Get the path to the measurements file"""
    file_path = get_plugin_storage_path("data/tools/structure/saved_dimensions.json", "studiomuse")
    return file_path
```

**Why this matters now:**
Without this abstraction, we would hardcode paths throughout the codebase. When the Project Selection System is implemented later, we would need to update every file operation to include project-specific paths (e.g., `.../projects/{project_id}/measurements/...`). By using `get_storage_path()` from the beginning, we'll only need to update this single method to make all file operations project-aware. This is a classic example of the "Single Responsibility Principle" that significantly reduces future refactoring effort.

#### 2. Project-Aware Data Models ✅
- Include `project_id` field in measurement data structures
- Group measurements with metadata that allows filtering by project
- **IMPLEMENTED**: `MeasurementCollection` class supports project metadata

```python
@dataclass
class MeasurementCollection:
    """Model for a collection of related measurements."""
    name: str
    measurements: List[Measurement] = field(default_factory=list)
    description: Optional[str] = None
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0.0"
```

#### 3. UI Design Considerations ⚙️
- Reserve UI space for displaying active project context
- Design list views to support future filtering by project
- Create a standardized toolbar area where project selector could later appear
- **PARTIALLY IMPLEMENTED**: UI architecture allows for future extensions

### 🎨 Palette Generator Integration 🚧

#### 1. Color System Compatibility 🚧
- Use consistent color models that will work with Palette Generator
- Implement shared color utilities for both tools
- **PLANNED**: CSS structure in place for future implementation

```python
def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color string"""
    return f"#{r:02x}{g:02x}{b:02x}"
    
def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
```

#### 2. Measurement-Color Association 🚧
- Allow measurements to optionally link to palette colors
- Create data structure for cross-referencing measurements with palette entries
- Enables coordinated visual presentation (e.g., colored measurement lines that match palette)
- **PLANNED**: Data models support extension for this feature

#### 3. Shared Resource System ✅
- Design measurement storage to be compatible with palette storage conventions
- Implement helpers for cross-tool asset discovery
- **IMPLEMENTED**: Consistent asset handling system

### ⚙️ Cross-Tool Architecture

#### 1. Event Communication System 🚧
- Implement basic observer pattern for tool events
- **PLANNED**: Designed but deferred until needed for specific cross-tool communication
```python
class EventBus:
    _subscribers = {}
    
    @classmethod
    def subscribe(cls, event_type, callback):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)
        
    @classmethod
    def publish(cls, event_type, data=None):
        for callback in cls._subscribers.get(event_type, []):
            callback(data)
```

#### 2. Consistent Data Structures ✅
- Use JSON schemas that will be compatible across tools
- Include version fields in all data files to support future migrations
- Create data validators that can be reused by other tools
- **IMPLEMENTED**: Structured data models with validation

#### 3. Configuration System Integration ⚙️
- Structure Proportia's configuration to fit within the larger StudioMuse hierarchy
- **PARTIALLY IMPLEMENTED**: Foundation in place
```json
{
  "proportia": {
    "default_unit": "cm",
    "precision": 2,
    "show_overlay": true
  },
  "projects": {
    "active_project": "my_project"
  }
}
```

### Why Plan Ahead?

Planning for these integrations now offers several key advantages:

1. **Reduced Technical Debt**: Building with future components in mind prevents costly refactoring later
2. **Consistent User Experience**: Creates a unified feel across all StudioMuse tools
3. **Faster Development**: Future tools can leverage patterns established in Proportia
4. **Data Integrity**: Ensures measurements remain associated with the correct projects and palettes
5. **Extensibility**: Makes it easier to add new features that span multiple tools

By incorporating these considerations into Proportia's initial design, we'll establish a strong foundation for the entire StudioMuse plugin suite while minimizing integration challenges later in development.

---

## UI Structure

- **Left Column**: Entry fields for new measurement + tools panel. ✅
- **Right Column**: Scrollable grouped list of saved measurements. ✅
- **Top Tab**: "Measuring Tool" tab inside the `Structure` notebook. ✅
- **Annotation Toggle**: Button to show/hide overlay layer. 🚧

---

## Architecture

- Plugin Class: `ProportiaPlugin` ✅
- UI XML: `proportia.ui` ✅
- Config: `config/plugins/structure/proportia.json` ⚙️
- Data Model: `MeasurementData`, `MeasurementGroup` ✅ (Renamed to `Measurement` and `MeasurementCollection`)
- Storage: JSON files, same as `scaleArt.py` ✅

## Data Model Specifications

### Measurement Object Structure ✅
- `name`: String (e.g., "Shoulder to Shoulder") ✅
- `value`: Float (stored with precision of 2 decimal places) ✅
- `group`: String (category such as "Face", "Body", "Frame Dimensions") ✅
- Additional fields implemented:
  - `unit`: String (e.g., "cm", "in") ✅
  - `visible`: Boolean (toggle visibility in overlay) ✅
  - `color`: String (hex code for visual representation) ✅
  - `notes`: String (optional notes about the measurement) ✅

### Backward Compatibility ✅
- Ensure import compatibility with existing `saved_dimensions.json` format ✅
- Support automatic migration of legacy data formats ✅
- Preserve group structure during import/export operations ✅

## Enhanced Group Management

### Group Features ⚙️
- **Collapsible Groups**: Toggle visibility of measurements within a group ✅
- **Group Reordering**: Drag-and-drop interface to reorganize groups 🚧
- **Group Creation**: Create new groups on-the-fly during measurement saving ✅
- **Group Assignment**: Move measurements between groups 🚧
- **Visual Differentiation**: Each group has distinct visual styling in the UI and overlay layers ✅

### Group Persistence ✅
- Save group state (expanded/collapsed) across sessions ✅
- Maintain group order when saving/loading data ✅
- Provide group filtering options in the measurement list ⚙️

## UI Implementation

### Measurement List View ✅
- **Hierarchical View**: Grouped measurements in collapsible sections ✅
- **Drag-Handle Interface**: Intuitive reordering with visual handles 🚧
- **Inline Actions**: Edit, move, and delete actions accessible directly in list ✅
- **Visual Status Indicators**: Clear feedback for save/update operations ✅

### Measurement Actions ✅
- **Edit Mode**: In-place editing of measurement names and values ✅
- **Quick Group Change**: Dropdown to quickly change a measurement's group 🚧
- **Batch Operations**: Select multiple measurements for bulk actions (future enhancement) 🚧
- **Visual Confirmation**: Animation/highlight to confirm user actions ⚙️

## Migration from scaleArt Prototype

### Architecture Transition ✅
- Refactor from standalone Flask app to integrated GIMP plugin ✅
- Preserve core measurement storage and grouping logic ✅
- Convert web UI patterns to GTK equivalents ✅
- Add direct GIMP canvas integration for measurement capture 🚧

### User Workflow Continuity ✅
- Maintain familiar dimension organization concepts ✅
- Ensure users can seamlessly import existing measurements ✅
- Preserve group structure during migration ✅
- Provide visual guides for transitioning users ⚙️

### Technical Considerations ✅
- Replace Flask templating with GTK/XML UI definitions ✅
- Convert JS drag-and-drop to GTK widget interactions 🚧
- Integrate GIMP image coordinate system with measurement system 🚧

## Example Workflows

### Portrait Measurement Scenario
Using measurements from the example project's "Face" group:

1. **Capture Face Elements**:
   - Create measurements for "Chin to Hairline" (14.98 cm)
   - Add "NoseTip to Hairline" (9.35 cm)
   - Measure "Chin to NoseTip" (5.4 cm)

2. **Group and Organize**:
   - Assign all measurements to "Face" group
   - Position related measurements together (e.g., all lip measurements)
   - Toggle overlay to visualize proportions on the image

3. **Scale for New Canvas**:
   - Select target canvas size
   - Apply scaling to maintain face proportions
   - Export new dimensions for physical artwork planning

- The popup remains open until the user chooses an action
- If [Save] is clicked, the line is permanently added to the measurement list and appropriate overlay layer
- If [Cancel] is clicked, the temporary line is removed and the user can start a new measurement
- Optional: The popup could also include a checkbox to "Add Visual Label" for displaying the name beside the line

## Implementation Status Legend
- ✅ Completed
- ⚙️ Partially Implemented
- 🚧 Planned/Not Yet Implemented

