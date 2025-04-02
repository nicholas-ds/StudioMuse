# StudioMuse Architecture: Suite-Style UI Development Plan

## Overview
This document outlines the plan for transitioning StudioMuse from a dialog-based plugin (ColorBitMagic) to a unified suite of tools with a consistent interface. This architectural shift will establish a foundation for future extensions while preserving existing functionality.

## Progress Update (Current Status)

### Completed Items ✓
- Basic stack-based UI structure implementation
- Core utility functions migration to core/utils/
- Initial tool integration framework
- Main window shell with stack switcher
- Basic notebook loading system

### In Progress ⚠️
- Dialog to notebook conversion (60% complete)
- Tool registration system (40% complete)
- Error handling standardization (30% complete)
- Event handling system (50% complete)

### Not Started ❌
- Complete plugin system implementation
- Shared services integration
- UI template system
- Hot-swappable tool support
- Developer documentation

## 1. UI Architecture Transition

### From Dialog-Based to Suite-Based UI
- **Current State**: Hybrid system (both dialog and stack-based)
- **Target State**: Fully unified stack-based interface
- **Progress**: 60% Complete

### New UI Architecture
- **Main Container**: ✓ Implemented
- **Plugin Groups**: ⚠️ Partially Implemented
- **Sub-Containers**: ⚠️ In Progress

### UI Component Hierarchy
```
├── Gtk.StackSwitcher (✓ Implemented)
├── Gtk.Stack (✓ Implemented)
│ ├── Analysis Stack (⚠️ Partial)
│ │ └── Gtk.Notebook
│ │ ├── ColorBitMagic Tab (⚠️ Converting from Dialog)
│ │ └── [Other Analysis Tools] Tabs (❌ Not Started)
│ ├── Structure Stack (❌ Not Started)
│ ├── VisionLab Stack (❌ Not Started)
│ └── Settings Stack (❌ Not Started)
└── Common Controls (⚠️ Partial)
```

## 2. Modular XML Plan

### XML Files Status
1. **`main_window.xml`** ✓ Complete
    - Contains: `GtkApplicationWindow`, `GtkStackSwitcher`, and `GtkStack`

2. **`visionlab_notebook.xml`** ❌ Not Started
    - Planned but not implemented

3. **`structure_notebook.xml`** ❌ Not Started
    - Planned but not implemented

4. **`analysis_notebook.xml`** ⚠️ In Progress
    - Partial implementation for ColorBitMagic

5. **`settings_box.xml`** ❌ Not Started
    - Not yet implemented

## 3. File Structure Reorganization

### Current Structure Status
```
StudioMuse/
├── studiomuse/
│   ├── studiomuse.py
├── core/
│   ├── base_dialog.py
│   ├── dialog_manager.py
│   ├── plugin_base.py
│   └── utils/
│       ├── config.py
│       ├── api/
│       ├── palette/
│       └── ui/
├── tools/
│   ├── analysis/
│   ├── structure/
│   ├── visionlab/
│   └── settings/
├── ui/
│   ├── templates/
│   ├── analysis/
│   ├── structure/
│   ├── visionlab/
│   └── settings/
└── config/
```

## 4. ColorBitMagic Migration Plan

### Migration Status
- UI Conversion: ⚠️ 60% Complete
  - `dmMain_update_populated.xml` → Partially converted
  - `addPalette.xml` → Needs conversion

### Remaining Tasks
1. Complete notebook integration
2. Standardize event handling
3. Implement state management
4. Add error handling system

## 5. Plugin System Implementation

### Status Overview
- Plugin Base Class: ❌ Not Started
- Plugin Registry: ❌ Not Started
- Shared Services: ❌ Not Started

## 6. Main UI Implementation

### Current Status
- Stack + Notebook: ✓ Basic implementation complete
- UI Templates: ❌ Not started
- Navigation Flow: ⚠️ Basic implementation, needs refinement

## 7. Updated Timeline
| Phase | Original Days | Status | Remaining Days |
|-------|--------------|---------|----------------|
| Core Infrastructure | 4-5 | 70% Complete | 1-2 |
| ColorBitMagic Migration | 3-4 | 60% Complete | 2-3 |
| Main UI Implementation | 3-4 | 40% Complete | 2-3 |
| Testing & Polish | 2-3 | Not Started | 2-3 |
| **Total Remaining** | **12-16** | **~55% Complete** | **7-11** |

## 8. QA Notes
- Lazy UI loading: ⚠️ Partially implemented
- Error logging: ⚠️ Basic implementation
- Debug messaging: ⚠️ Basic implementation
- Plugin failure isolation: ❌ Not started
- Developer documentation: ❌ Not started

## 9. Next Steps Priority List
1. Complete ColorBitMagic notebook conversion
2. Implement standardized tool registration
3. Add proper state management
4. Create shared services framework
5. Develop UI templates
6. Add comprehensive error handling
7. Create developer documentation

## 10. Known Issues
1. Mixed dialog and notebook-based approaches
2. Inconsistent event handling
3. Incomplete state management
4. Missing error handling standardization
5. Lack of proper tool cleanup handlers

