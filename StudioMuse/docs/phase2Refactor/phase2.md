# StudioMuse Project Plan: Phase 2 — Plugin Suite & Measurement Tools

## Overview
This document outlines the next stage of development for the StudioMuse GIMP plugin, which has successfully transitioned from a single-tool prototype (ColorBitMagic) to a modular, extensible suite of creative tools. This plan focuses on the remaining work to build upon the new architecture.

The project consists of two main components:
1. **GIMP Plugin**: The GTK-based frontend that integrates with GIMP
2. **Backend Service**: A FastAPI-based service that handles LLM integration and complex processing

Both components have been modularized for better maintainability, with clearly defined interfaces between them.

---

## 1. UI Architecture: Current Status ✅

### Completed
- Successfully implemented a unified interface with cohesive suite of tools
- Established a scalable, modern GTK architecture using GIMP 3.0-compatible components
- Migrated and repurposed existing UI patterns and code from ColorBitMagic
- Implemented stack-based navigation with category notebooks

### Architecture
- **WindowManager**: Central class managing the main application window and UI components:
  - Handles main window initialization and lifecycle
  - Manages `Gtk.Stack` with `Gtk.StackSwitcher` for navigation
  - Dynamically loads notebooks for plugin categories
  - Maintains tool handlers for plugin registration
- **Plugin Groups**: Each group (VisionLab, Structure, Analysis, Settings) loaded as a `Gtk.Notebook`
- **Sub-Containers**: Individual plugin UIs loaded into their respective category notebooks
- **Tool Registration**: Plugins register with WindowManager via the tool_handlers system

## 2. Measuring & Scaling Tool Plugin (Proportia)

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
- Adapt UI presentation patterns for the notebook-based architecture
- Leverage configuration system from core utilities

---

## 3. Project Selection System

### Goals
- Enable users to select the current active art project from the main UI
- Keep all tools (e.g., ColorBitMagic, Proportia) scoped to project-specific data
- Prevent clutter and improve UX with project-based data isolation

### Key Features
- Project selector in the main UI next to the `GtkStackSwitcher` 
- Project-specific directories to store palettes, measurements, etc.
- Persistence via `config/user.json` to auto-load the last selected project
- Configurable project metadata and structure

### Implementation
- Create `ProjectContext` module to manage active project state
- Update file I/O in all plugins to use project-specific paths
- Implement project creation, selection, and management UI
- Store project data in `~/.config/GIMP/3.0/studiomuse/projects/{project_id}/`

---

## 4. Native Palette Generator

### Goals
- Build a native StudioMuse tool for creating GIMP palettes from image selections or layers
- Replace GIMP's native "Import Palette" dialog with a fully controlled experience
- Integrate palette generation with the project-aware architecture

### Key Features
- Multiple palette source options (selected area, active layer, entire image)
- Customizable palette generation parameters (number of colors, sampling interval)
- Project-aware palette naming and storage
- Preview functionality for generated palettes

### Implementation
- Create a UI for palette generation options
- Implement color extraction logic from selections/layers
- Use GIMP API to create native palettes
- Track project-specific palette references
- Integrate with ColorBitMagic for seamless workflow

---

## 5. Plugin Architecture & Extensibility ✅

### Current Status
- Successfully migrated to a modular architecture
- Created shared utilities, settings, and state management across plugin components
- Established maintainable architecture for both plugin and backend components

### Key Components
- **Module Structure**: Well-organized directory hierarchy for different components
- **Configuration System**: Hierarchical config management with proper overrides
- **UI Templates**: Reusable patterns for consistent plugin UI

---

## 6. Vision Lab (Experimental Tools)

A container for vision model-powered tools to enhance physical art-making processes. These tools will be developed after the core productivity features are complete.

### Implementation Approach
- Reuse API client from ColorBitMagic to communicate with AI services
- Adapt notebook-based UI patterns for image selection and processing
- Use the text formatting system to present AI insights

### Core Tool Concepts
- **Scene Abstraction Tool**: Convert complex reference photos into simplified shapes
- **Lighting Modifier**: Alter light direction and tone in a reference image
- **LLM Project Companion**: Chat with a language model about color theory and composition

---

## 7. Implementation Plan

### Step 1: Core Infrastructure ✅
- [x] Create basic directory structure
- [x] Migrate UI components to modular structure
- [x] Migrate utility functions
- [x] Implement hierarchical config system
- [x] Create default configuration files
- [x] Create modular API client system
- [x] Implement specialized clients for different domains
- [x] Create API manager factory

### Step 2: ColorBitMagic Migration ✅
- [x] Convert dialog-based UIs to notebook architecture
- [x] Integrate with plugin system
- [x] Test all existing functionality within new framework
- [x] Update file paths and dependencies

### Step 3: Main UI Implementation ✅
- [x] Implement main `Gtk.Stack` with `Gtk.StackSwitcher`
- [x] Create category stacks for each plugin group
- [x] Implement plugin tab navigation
- [x] Create base templates for plugin pages
- [x] Implement shared styles
- [x] Create reusable widget patterns

### Step 4: Proportia - Measurement Tool (4-6 days)
- [ ] Implement measurement data models
- [ ] Create UI for creating and editing measurements
- [ ] Implement pixel-to-real-world conversion
- [ ] Integrate with GIMP's measurement tools
- [ ] Implement overlay rendering
- [ ] Create export/import functionality

### Step 5: Project Selection System (3-4 days)
- [ ] Implement `ProjectContext` class
- [ ] Create project selector UI component
- [ ] Add project-specific data paths to all plugins
- [ ] Implement project creation/selection dialogs
- [ ] Test with multiple projects

### Step 6: Native Palette Generator (3-4 days)
- [ ] Build GTK dialog UI for palette generation
- [ ] Implement color extraction from selection/layer
- [ ] Add GIMP palette creation logic
- [ ] Write project tracking JSON entry
- [ ] Wire into ColorBitMagic sidebar
- [ ] Test palette generation workflow

### Step 7: Advanced Quality Improvements (3-4 days)
- [ ] Create `ServiceProvider` for dependency injection
- [ ] Implement `LogManager` for centralized logging
- [ ] Create standardized error hierarchy
- [ ] Add consistent error handling patterns

### Step 8: Initial VisionLab Tools (when core features complete)
- [ ] Implement Scene Abstraction Tool MVP
- [ ] Create image processing pipeline
- [ ] Develop result visualization UI

---

## 8. Advanced Code Quality Strategies

### 8.1 Dependency Injection System

To enhance modularity and testability, we'll implement a lightweight dependency injection system:

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
class PaletteModule:
    def __init__(self):
        self.api_client = ServiceProvider.get(IApiClient).get_palette_client()
        self.logger = ServiceProvider.get(ILogger).get_logger("palette")
```

### 8.2 Unified Logging System

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

### 8.3 Error Types Taxonomy

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
   - Each component implements standard error handlers
   - Graceful degradation when services are unavailable
   - Clear user communication about errors and next steps

3. **User Communication Strategy**:
   - Technical details logged for developers
   - User-friendly messages displayed in the UI
   - Actionable suggestions when possible

---

## Revised Timeline

| Phase                       | Estimated Duration |
|-----------------------------|--------------------|
| Proportia (Measurement Tool)| 4-6 days           |
| Project Selection System    | 3-4 days           |
| Native Palette Generator    | 3-4 days           |
| Advanced Quality Systems    | 3-4 days           |
| **Total**                   | **13-18 days**     |

This timeline focuses on the remaining work now that the core infrastructure and migration has been completed. The advanced quality systems can be implemented in parallel with the feature development as they enhance the architecture but don't block initial functionality. VisionLab tools will be developed after these core productivity features are complete.