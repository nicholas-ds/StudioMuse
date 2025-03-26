# StudioMuse Project Plan: Phase 2 — Plugin Suite & Measurement Tools

## Overview
This document outlines the next stage of development for the StudioMuse GIMP plugin, transitioning it from a single-tool prototype to a modular, extensible suite of creative tools.

---

## 1. UI Overhaul: Foundation for Plugin Suite

### Goals
- Present plugins as a cohesive suite of tools within a unified interface.
- Establish a scalable, modern GTK architecture using GIMP 3.0-compatible components.

### Architecture
- **Main Container**: `Gtk.Stack` with `Gtk.StackSwitcher` for navigating high-level plugin groups.
- **Plugin Groups**: Each group (VisionLab, Structure, Analysis, Settings) is represented as a `Gtk.Box` containing a `Gtk.Notebook`.
- **Sub-Containers**: `Gtk.Notebook` inside each plugin view holds tool-specific tabs.
- Shared styling, menu behavior, and exit handling via `BaseDialog` and `DialogManager`.

### File Structure
```
studiomuse/
├── studiomuse.py              # Main entry point
├── tools/                     # All plugin tool logic
│   ├── visionlab/             # Vision-model-powered tools
│   │   ├── __init__.py
│   │   ├── base.py            # BaseVisionTool class
│   │   ├── scene_abstraction.py
│   │   ├── depth_viewer.py
│   │   └── visionlab_stack.py
│   ├── structure/             # Measurement, annotation, scaling tools
│   │   ├── __init__.py
│   │   ├── measuring_tool.py
│   │   └── structure_stack.py
│   ├── analysis/              # Color parsing, image analysis tools
│   │   ├── __init__.py
│   │   ├── colorbitmagic.py
│   │   └── analysis_stack.py
│   └── settings/              # Global preferences and config
│       ├── __init__.py
│       └── settings_stack.py
├── utils/                     # Shared backend logic
│   ├── __init__.py
│   ├── config.py              # JSON config loading/saving
│   └── ui_loader.py           # Utility to load .ui files
├── ui/                        # All static UI files
│   ├── visionlab/
│   │   └── scene_abstraction.ui
│   ├── structure/
│   │   └── measuring_tool.ui
│   ├── analysis/
│   │   └── colorbitmagic.ui
│   └── settings/
│       └── preferences.ui
└── settings.json              # Shared config file
```

### Implementation Notes (From Research)
- Each tool's UI is defined statically: the main plugin file (`studiomuse.py`) manually imports each plugin group and adds its stack to the root `Gtk.Stack`.
- Each plugin group (e.g. VisionLab) provides a `get_stack()` function that returns a `Gtk.Box` with a `Gtk.Notebook` containing its tools.
- Tools can load their UIs from `.ui` files stored under `ui/{group}/`.
- Utility functions (e.g., `load_ui()`, JSON I/O) are placed in `utils/`.

---

## 2. Measuring & Scaling Tool Plugin

### Goals
- Enable precise measurement, annotation, and scaling within GIMP.
- Support translation from image dimensions to real-world canvas dimensions.
- Build on the structure of the user’s previous Flask web app for grouped, named, and reorderable measurements.

### Features
- Read from GIMP’s built-in measuring data (e.g., vector lines).
- Store measurements with names, descriptions, and grouping.
- Auto-convert measurements using a pixel-to-inch/cm ratio.
- Toggleable overlay layer for visual markup of each measurement.
- Export/import functionality (JSON-based) for persistence and reuse.

---

## 3. Plugin Architecture & Extensibility

### Goals
- Support multiple independently developed plugins under the StudioMuse umbrella.
- Allow shared utilities, settings, and state management across all plugins.

### Tasks
- [ ] Create `BasePlugin` class/interface.
- [ ] Add metadata system (name, icon, description) to each plugin.
- [ ] Build optional configuration system (shared JSON file or per-plugin config).
- [ ] Refactor `DialogManager` to work seamlessly with stacked plugin views.

### Architecture Guidance (From Research)
- **Plugin Discovery**: Plugins are statically defined. Avoid auto-loading files — manually import and register each plugin.
- **Shared State & Utilities**:
  - Shared config should be stored in a JSON file (e.g., `settings.json`) in the plugin directory.
  - Utility functions (e.g., JSON I/O, logging) should be stored in `utils.py` and imported across plugins.
  - Use a shared `State` object or singleton to pass common data across tools.

---

## 4. Vision Lab (Experimental Tools)

A modular container for tools powered by vision models. Each tool is designed to enhance the physical art-making process through digital assistance — not to replace the artist, but to support decision-making, ideation, and technical execution.

### A. Composition & Structure Tools
- **Scene Abstraction Tool**: Convert complex reference photos into simplified shapes, figures, and depth layers.
- **Anatomy Refiner**: Overlay skeletal pose estimation on a sketch to improve anatomical accuracy.
- **Depth & Form Viewer**: Highlight spatial planes with depth maps for guiding focus and atmospheric perspective.

### B. Lighting & Enhancement Tools
- **Lighting Modifier**: Alter light direction and tone in a reference image to explore alternate moods.
- **Reference Enhancer**: Fill gaps in incomplete references (e.g., finish shadows, suggest back of figure).

### C. Visual Memory Support
- **Memory Refresher**: Use partial sketches or prompts to generate alternate views or missing angles of a subject.
- **Sketch-to-Reference Generator**: Upload a sketch and prompt an LLM-guided diffusion model to generate coherent reference images.

### D. Conceptual & Planning Tools
- **LLM Project Companion**: Chat with a language model about color theory, materials, composition, and emotional goals for a piece.
- **Prompted Composition Generator**: Start with a theme or phrase and receive suggestive layouts, palettes, or form studies (no finished image generation).

---

## Timeline

| Phase                        | Estimated Duration |
|-----------------------------|--------------------|
| UI Overhaul & Refactor      | 3–5 days           |
| Measurement Tool MVP        | 4–6 days           |
| Plugin Architecture Cleanup | 2–3 days           |
| Vision Lab Prototypes       | Ongoing            |

