# StudioMuse Project Plan: Phase 2 — Plugin Suite & Measurement Tools

## Overview
This document outlines the next stage of development for the StudioMuse GIMP plugin, transitioning it from a single-tool prototype (ColorBitMagic) to a modular, extensible suite of creative tools. This plan prioritizes reusing existing code while establishing a sustainable architecture for future development.

The project consists of two main components:
1. **GIMP Plugin**: The GTK-based frontend that integrates with GIMP
2. **Backend Service**: A FastAPI-based service that handles LLM integration and complex processing

Both components will be modularized for better maintainability, with clearly defined interfaces between them.

---

## 1. UI Overhaul: Foundation for Plugin Suite

### Goals
- Present plugins as a cohesive suite of tools within a unified interface.
- Establish a scalable, modern GTK architecture using GIMP 3.0-compatible components.
- Reuse existing UI patterns and code from ColorBitMagic.

### Architecture
- **Main Container**: `Gtk.Stack` with `Gtk.StackSwitcher` for navigating high-level plugin groups.
- **Plugin Groups**: Each group (VisionLab, Structure, Analysis, Settings) is represented as a `Gtk.Box` containing a `Gtk.Notebook`.
- **Sub-Containers**: `Gtk.Notebook` inside each plugin view holds tool-specific tabs.
- Shared styling, menu behavior, and exit handling via `BaseDialog` and `DialogManager`.

### File Structure
``` 
Reference updatedTree.txt in the docs directory of the project.
```

## 2. Existing Code Reuse Strategy

### Core Components Reuse
The following existing components will be directly migrated with minimal changes:

#### Dialog System
- **BaseDialog** (`base_dialog.py`):
  - Move to `studiomuse/core/base_dialog.py`
  - Preserve all existing text formatting methods: `_get_or_create_tags()`, `insert_styled_text()`, `insert_labeled_value()`, `display_results()`
  - These methods will be used across all plugins for consistent text presentation

- **DialogManager** (`dialog_manager.py`):
  - Move to `studiomuse/core/dialog_manager.py`
  - Extend to support the stacked UI architecture
  - Maintain existing dialog registration and management logic

#### API Client
- **BackendAPIClient** (`api_client.py`):
  - Move to `studiomuse/core/utils/api/api_client.py`
  - Keep all existing error handling, logging, and connection retry logic
  - Extend with versioning support for all plugin endpoints
  - Extract specific ColorBitMagic endpoints to extension methods if needed

#### Palette Processing
- **Palette Models** (`palette_models.py`):
  - Move to `studiomuse/core/utils/palette/models.py`
  - Maintain `ColorData`, `PaletteData`, and `PhysicalPalette` classes
  - These will serve as data models for both ColorBitMagic and new tools

- **PaletteProcessor** (`palette_processor.py`):
  - Move to `studiomuse/core/utils/palette/processor.py`
  - Keep methods for loading/saving palettes, converting GEGL colors
  - Add extension points for new palette functionality

#### UI Utilities
- **UI Utilities** (`colorBitMagic_utils.py`):
  - Split into appropriate utility modules:
    - `core/utils/ui/widgets.py`: `populate_dropdown()`, color swatch rendering
    - `core/utils/ui/text.py`: Text processing utilities
  - Generalize functions to be reusable across plugins while maintaining existing functionality

### ColorBitMagic Migration
ColorBitMagic will be migrated as the first plugin in the analysis tool group:

1. **Dialog Conversion**:
   - Convert `demystifyer_dialog.py` → `tools/analysis/colorbitmagic/demystifyer.py`
   - Adapt to use the new plugin architecture while preserving all functionality
   - Rename XML files with consistent naming: `dmMain_update_populated.xml` → `ui/analysis/colorbitmagic/demystify.ui`

2. **UI Adaptation**:
   - Modify UI to work within a tab of the Analysis stack
   - Preserve all custom UI components (color swatches, result displays)

3. **Plugin Registration**:
   - Create ColorBitMagic plugin class implementing `PluginBase`
   - Register with the plugin system in `analysis_stack.py`

4. **Configuration Migration**:
   - Move settings from any existing JSON files to `config/plugins/analysis/colorbitmagic.json`
   - Add configuration migration code to handle first-run upgrades

---

## 3. Measuring & Scaling Tool Plugin

### Goals
- Enable precise measurement, annotation, and scaling within GIMP.
- Support translation from image dimensions to real-world canvas dimensions.
- Build on the structure of the user's previous Flask web app for grouped, named, and reorderable measurements.

### Features
- Read from GIMP's built-in measuring data (e.g., vector lines).
- Store measurements with names, descriptions, and grouping.
- Auto-convert measurements using a pixel-to-inch/cm ratio.
- Toggleable overlay layer for visual markup of each measurement.
- Export/import functionality (JSON-based) for persistence and reuse.

### Implementation
- Reuse palette storage patterns from ColorBitMagic for measurement data
- Adapt UI presentation patterns from `BaseDialog` to show measurement results
- Leverage configuration system from core utilities

---

## 4. Plugin Architecture & Extensibility

### Goals
- Support multiple independently developed plugins under the StudioMuse umbrella.
- Allow shared utilities, settings, and state management across all plugins.
- Ensure a modular, maintainable architecture for both plugin and backend components.

### Plugin Base Class
```python
class PluginBase:
    """Base class for all StudioMuse plugins."""
    
    def __init__(self):
        self.name = self.get_name()
        self.version = self.get_version()
        self.description = self.get_description()
        self.category = self.get_category()
        
    @abstractmethod
    def get_name(self) -> str:
        """Get the plugin name for menus and UI."""
        pass
        
    @abstractmethod
    def get_stack(self) -> Gtk.Box:
        """Return the main UI container for this plugin."""
        pass
        
    def get_version(self) -> str:
        """Get plugin version."""
        return "1.0.0"
        
    def get_description(self) -> str:
        """Get plugin description for UI."""
        return ""
        
    def get_category(self) -> str:
        """Get plugin category (analysis, visionlab, etc.)."""
        return "misc"
        
    def get_config(self) -> dict:
        """Get plugin-specific configuration."""
        # Implementation will use the hierarchical config system
        return {}
        
    def save_config(self, config: dict) -> None:
        """Save plugin-specific configuration."""
        # Implementation will use the hierarchical config system
        pass
        
    def on_activate(self) -> None:
        """Called when the plugin is activated."""
        pass
        
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated."""
        pass
```

### Plugin Registration

```python
class PluginRegistry:
    """Registry for all StudioMuse plugins."""
    
    def __init__(self):
        self.plugins = {}
        
    def register_plugin(self, plugin_class):
        """Register a plugin class with the registry."""
        instance = plugin_class()
        category = instance.get_category()
        
        if category not in self.plugins:
            self.plugins[category] = {}
            
        self.plugins[category][instance.get_name()] = instance
        
    def get_plugin_categories(self):
        """Get all plugin categories."""
        return self.plugins.keys()
        
    def get_plugins_in_category(self, category):
        """Get all plugins in a category."""
        return self.plugins.get(category, {}).values()
        
    def get_plugin_stack(self, category, name):
        """Get the UI stack for a specific plugin."""
        return self.plugins.get(category, {}).get(name).get_stack()
```

### Configuration System

The configuration system will be hierarchical, with defaults overridden by user-specific and plugin-specific settings:

1. **Global**: `config/default.json` - StudioMuse-wide settings
2. **User**: `config/user.json` - User overrides for global settings
3. **Plugin**: `config/plugins/[category]/[plugin].json` - Plugin-specific settings

This system will be implemented in `core/utils/config.py` and will reuse the JSON parsing patterns from ColorBitMagic.

---

## 5. Vision Lab (Experimental Tools)

A modular container for tools powered by vision models. Each tool is designed to enhance the physical art-making process through digital assistance — not to replace the artist, but to support decision-making, ideation, and technical execution.

### Implementation Approach
- Reuse API client from ColorBitMagic to communicate with AI services
- Adapt palette selection UI patterns for image selection
- Use the text formatting system from BaseDialog to present AI insights

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

## 6. Implementation Plan

### Step 1: Core Infrastructure (4-5 days)

#### 1.1 Core Migration
- [ ] Create basic directory structure
- [ ] Migrate `BaseDialog` and `DialogManager` to `core/`
- [ ] Create `PluginBase` and `PluginRegistry` classes
- [ ] Migrate utility functions:
  - Palette models from `palette_models.py`
  - Palette processor from `palette_processor.py`
  - UI utilities from `colorBitMagic_utils.py`

#### 1.2 Configuration System
- [ ] Implement hierarchical config system
- [ ] Create default configuration files
- [ ] Create config migration utilities for existing settings

#### 1.3 API Client Modularization
- [ ] Create `BaseApiClient` class with shared functionality
- [ ] Implement specialized clients for each domain:
  - `PaletteApiClient` (migrated from `BackendAPIClient`)
  - `VisionApiClient` for VisionLab tools
  - `StructureApiClient` for measurement tools
- [ ] Create `ApiClientManager` factory class
- [ ] Implement API versioning support
- [ ] Create shared API models for requests/responses

### Step 2: ColorBitMagic Migration (3-4 days)

#### 2.1 Dialog Conversion
- [ ] Convert `demystifyer_dialog.py` to plugin architecture
- [ ] Convert `add_palette_dialog.py` to plugin architecture
- [ ] Rename and relocate UI XML files

#### 2.2 Integration with Plugin System
- [ ] Create `ColorBitMagicPlugin` class
- [ ] Integrate with `analysis_stack.py`
- [ ] Test all existing functionality within new framework
- [ ] Update file paths and dependencies

### Step 3: Main UI Implementation (3-4 days)

#### 3.1 Main Container
- [ ] Implement main `Gtk.Stack` with `Gtk.StackSwitcher`
- [ ] Create category stacks for each plugin group
- [ ] Implement plugin tab navigation

#### 3.2 UI Templates
- [ ] Create base templates for plugin pages
- [ ] Implement shared styles
- [ ] Create reusable widget patterns

### Step 4: Measurement Tool (4-6 days)

#### 4.1 Core Functionality
- [ ] Implement measurement data models
- [ ] Create UI for creating and editing measurements
- [ ] Implement pixel-to-real-world conversion

#### 4.2 Integration
- [ ] Integrate with GIMP's measurement tools
- [ ] Implement overlay rendering
- [ ] Create export/import functionality

### Step 6: Advanced Quality Improvements (3-4 days)

#### 6.1 Dependency Injection System
- [ ] Create `ServiceProvider` for central service registration
- [ ] Define interfaces for key services
- [ ] Convert existing code to use dependency injection
- [ ] Document patterns for adding new injectable services

#### 6.2 Unified Logging System
- [ ] Create `LogManager` for centralized logging
- [ ] Define standardized log levels and context information
- [ ] Implement GIMP message integration
- [ ] Add component-specific loggers

#### 6.3 Error Types Taxonomy
- [ ] Create error hierarchy with base `StudioMuseError`
- [ ] Define specialized error types for different components
- [ ] Implement user-friendly error messages
- [ ] Add consistent error handling patterns

---

## 7. Advanced Code Quality Strategies

### 7.1 Dependency Injection System

To further enhance modularity and testability, we'll implement a lightweight dependency injection system:

```python
class ServiceProvider:
    """Central registry for application services."""
    
    _services = {}
    
    @classmethod
    def register(cls, service_type, implementation):
        """Register a service implementation."""
        cls._services[service_type] = implementation
        
    @classmethod
    def get(cls, service_type):
        """Get a service implementation."""
        if service_type not in cls._services:
            raise KeyError(f"Service {service_type} not registered")
        return cls._services[service_type]
```

#### Benefits of Dependency Injection:

1. **Loose Coupling**: Components depend on interfaces, not concrete implementations
2. **Testability**: Easy to substitute mock implementations for testing
3. **Configurability**: Switch implementations without modifying consumers
4. **Lifecycle Management**: Centralized control over object creation and lifetime

#### Example Usage:

```python
# Register services during application startup
ServiceProvider.register(IApiClient, ApiClientManager())
ServiceProvider.register(IConfigManager, ConfigManager())
ServiceProvider.register(ILogger, LogManager())

# In components, request dependencies rather than creating them
class PalettePlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.api_client = ServiceProvider.get(IApiClient).get_palette_client()
        self.logger = ServiceProvider.get(ILogger).get_logger("palette")
```

### 7.2 Unified Logging System

A unified logging system will ensure consistent logging across all plugins:

```python
class LogManager:
    """Centralized logging management."""
    
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    def __init__(self):
        self.default_level = "INFO"
        self.loggers = {}
        
    def get_logger(self, name):
        """Get or create a logger with the given name."""
        if name not in self.loggers:
            self.loggers[name] = Logger(name, self.default_level)
        return self.loggers[name]
        
    def set_global_level(self, level):
        """Set logging level for all loggers."""
        for logger in self.loggers.values():
            logger.set_level(level)
```

#### Key Features:

1. **Consistent Log Levels**:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working
   - WARNING: Something unexpected but not critical
   - ERROR: Something failed, but operation can continue
   - CRITICAL: Application cannot continue

2. **Standardized Context Information**:
   - Timestamp
   - Component name
   - Log level
   - Message
   - Additional context (user operation, affected object)

3. **Output Flexibility**:
   - Console output for development
   - File output for production
   - GIMP message area integration
   - Optional sending of critical errors to backend

#### Example Usage:

```python
# Get a component-specific logger
logger = ServiceProvider.get(ILogger).get_logger("ColorBitMagic")

# Log with appropriate levels
logger.debug("Processing color data", {"color_count": 15})
logger.info("Palette loaded successfully")
logger.warning("Physical color match not found, using closest alternative")
logger.error("Failed to communicate with backend", {"error": str(e)})
```

### 7.3 Error Types Taxonomy

A structured approach to error handling with standardized error types:

```python
class StudioMuseError(Exception):
    """Base class for all StudioMuse errors."""
    
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}
        self.user_message = self._get_user_message()
        
    def _get_user_message(self):
        """Get a user-friendly version of the error message."""
        return str(self)
        
class ConfigurationError(StudioMuseError):
    """Error related to configuration issues."""
    pass
    
class ApiError(StudioMuseError):
    """Error related to API communication."""
    pass
    
class UiError(StudioMuseError):
    """Error related to UI operations."""
    pass
    
class DataProcessingError(StudioMuseError):
    """Error related to data processing."""
    pass
```

#### Error Handling Approach:

1. **Structured Error Types**:
   - API errors (connection, timeout, authentication)
   - Configuration errors (missing settings, invalid values)
   - UI errors (missing widgets, interaction failures)
   - Data processing errors (parsing, validation, transformation)

2. **Consistent Error Recovery**:
   - Each plugin implements standard error handlers
   - Graceful degradation when services are unavailable
   - Clear user communication about errors and next steps

3. **User Communication Strategy**:
   - Technical details logged for developers
   - User-friendly messages displayed in the UI
   - Actionable suggestions when possible

#### Example Usage:

```python
try:
    result = self.api_client.demystify_palette(gimp_colors, physical_colors)
except ApiConnectionError as e:
    # Log technical details
    logger.error("API connection error", {"error": str(e), "endpoint": e.endpoint})
    
    # Show user-friendly message
    show_error_dialog(
        title="Connection Problem",
        message="Could not connect to the StudioMuse service.",
        details="Please check your internet connection and try again."
    )
```

By implementing these advanced code quality strategies, StudioMuse will have a robust foundation that scales with growing complexity while maintaining clean, maintainable code.

---

## Timeline

| Phase                        | Estimated Duration |
|-----------------------------|--------------------|
| Core Infrastructure         | 4-5 days           |
| API Modularization          | 2-3 days           |
| ColorBitMagic Migration     | 3-4 days           |
| Main UI Implementation      | 3-4 days           |
| Measurement Tool MVP        | 4-6 days           |
| Initial VisionLab Features  | 3-5 days           |
| Advanced Quality Systems    | 3-4 days           |
| **Total**                   | **22-31 days**     |

This timeline assumes focused development with minimal interruptions and building in small, testable increments. The API modularization and advanced quality systems phases can overlap with other work if needed, as they enhance the architecture but don't block initial functionality.