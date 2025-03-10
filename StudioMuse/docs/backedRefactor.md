# Refactored Project Structure for StudioMuse GIMP Plugin

Based on your existing code and the recommended frontend/backend separation, here's an optimized project structure to clearly separate concerns and simplify development:

```
StudioMuse/
├── backend/                      # Backend server for handling LLM interactions
│   ├── api.py                    # ✅ FastAPI backend entry point
│   ├── requirements.txt          # ✅ fastapi, uvicorn, requests, google-genai
│   ├── test_llm.py               # ✅ Test script for LLM functionality
│   ├── test_api.py               # ✅ Test script for API endpoints
│   └── llm/
│       ├── __init__.py           # ✅ Module initialization
│       ├── base_llm.py           # ✅ Base LLM class
│       ├── gemini_llm.py         # ✅ Gemini implementation
│       ├── perplexity_llm.py     # ✅ Perplexity implementation
│       ├── prompts.py            # ✅ LLM prompts
│       └── llm_service_provider.py # ✅ Factory for LLM instances
│
└── plugins/
    └── colorBitMagic/
        ├── colorBitMagic.py        # Main GIMP plugin frontend script
        ├── colorBitMagic_ui.py
        ├── dialogs/
        │   ├── base_dialog.py
        │   ├── home_dialog.py
        │   ├── demystifyer_dialog.py  # ✅ Updated to display results properly
        │   ├── add_palette_dialog.py
        │   └── dialog_manager.py
        │
        ├── templates/             # UI XML files
        │   ├── addPalette.xml
        │   └── dmMain.xml
        │
        ├── utils/                 # Utility functions and models without external dependencies
        │   ├── palette_models.py
        │   ├── palette_processor.py
        │   ├── api_client.py      # ✅ API client for backend communication
        │   └── colorBitMagic_utils.py  # ✅ Fixed palette loading error handling
        │
        ├── llm/                   # ✅ Fixed LLM integration
        │   ├── __init__.py
        │   ├── PaletteDemistifyerLLM.py  # ✅ Fixed prompt formatting
        │   ├── LLMPhysicalPalette.py
        │   ├── gemini_llm.py
        │   ├── perplexity_llm.py
        │   ├── prompts.py
        │   └── llm_service_provider.py
        │
        ├── palettes/              # Stored GIMP palette data (.json)
        │   └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
        │
        └── physical_palettes/     # Physical palettes (.json)
            └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
```

### Incremental Development & Testing Approach

We're following a test-driven, incremental approach to this refactoring:

1. **Incremental Component Migration**: Moving one component at a time from the plugin to the backend
2. **Comprehensive Test Scripts**: Creating and extending test scripts alongside each component
3. **Verification Before Proceeding**: Testing each component thoroughly before moving to the next
4. **Continuous Integration**: Building a suite of tests that can be run to verify the entire system

This approach ensures we:
- Catch issues early in the development process
- Maintain a working system throughout the refactoring
- Have confidence that previous functionality continues to work
- Create documentation through tests that show how components should be used

### Step-by-Step Plan for Cross-Platform Refactor (Windows & Mac)

#### 1️⃣ **Separate Frontend & Backend Clearly** - 🟡 In Progress

- ✅ Create `backend/api.py` with FastAPI server for handling color processing
- ✅ Set up basic health check and configuration endpoints
- ✅ Create `plugins/colorBitMagic/utils/api_client.py` for HTTP communication
- ✅ Create core LLM infrastructure in backend:
  - ✅ Base LLM class
  - ✅ LLM Service Provider
  - ✅ Prompts module
  - ✅ Test script for LLM components
- ✅ Implement LLM providers in backend:
  - ✅ Perplexity LLM
  - ✅ Gemini LLM
  - ✅ Extended test script to verify providers
- ✅ Test live LLM responses:
  - ✅ Perplexity API calls verified
  - ✅ Gemini API calls verified
- ✅ Create API endpoints for palette processing
  - ✅ Palette demystification endpoint
  - ✅ Test script for API endpoints
- ✅ Fix local LLM integration in plugin:
  - ✅ Fixed `PaletteDemistifyerLLM` to properly format prompts
  - ✅ Fixed palette data loading error handling
  - ✅ Implemented proper display of results in UI
- 🔄 Update plugin dialogs to use API client instead of direct LLM calls
- 🔄 Update imports in `colorBitMagic.py` to request data from the backend via HTTP

#### 2️⃣ **Update Plugin Execution Paths** - ⚪ Not Started

- Ensure `colorBitMagic.py` uses relative paths to locate `templates/`, `utils/`, and `dialogs/` correctly across OS.
- Update `install.py` and `install.sh` to properly detect OS and install in the correct GIMP plugin directory.
  - Mac: `~/Library/Application Support/GIMP/3.0/plug-ins/`
  - Windows: `%APPDATA%\GIMP\3.0\plug-ins\`

#### 3️⃣ **Ensure LLM Dependencies Work on Both OS** - ✅ Completed

- ✅ Create `backend/requirements.txt` with cross-platform dependencies
- ✅ Use Conda for backend environment:
  ```sh
  # Windows
  conda create -n studiomuse-backend python=3.12
  conda activate studiomuse-backend
  pip install -r requirements.txt
  ```
  ```sh
  # Mac/Linux
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- ✅ Implement comprehensive test scripts to verify functionality

#### 4️⃣ **Fix File System Issues (Windows/Mac Differences)** - ⚪ Not Started

- Use `os.path.join()` in `palette_processor.py` to ensure file paths work across both platforms.
- Ensure JSON file handling (read/write) works correctly for both Windows (`\`) and Mac (`/`).

#### 5️⃣ **Test & Debug on Both Platforms** - 🟡 In Progress

- ✅ Run backend on Windows to verify API calls:
  ```sh
  python api.py  # Uses uvicorn internally
  ```
- ✅ Verify basic API communication with `api_client.py`
- ✅ Create and run test scripts for backend components:
  - ✅ `test_llm.py` for LLM functionality
  - ✅ `test_api.py` for API endpoints
- ✅ Test local LLM functionality in the GIMP plugin:
  - ✅ Fixed palette demystification with proper prompt formatting
  - ✅ Improved error handling for palette loading
  - ✅ Fixed results display in the UI
- 🔄 Test the GIMP plugin with backend communication
- 🔄 Test JSON saving/loading in `physical_palettes/` on both OS

#### 6️⃣ **Finalize Windows/Mac Installation Scripts** - ⚪ Not Started

- Ensure `install.py` and `install.sh` correctly install the plugin based on OS detection.
- Provide step-by-step setup documentation for Windows users (e.g., enabling scripts in PowerShell).

#### 7️⃣ **Implement Configuration Management System** - 🟡 In Progress

- ✅ Create basic configuration endpoint in backend API
- 🔄 Create a flexible configuration system that works across both plugin and backend
- 🔄 Support multiple configuration sources with priority order:
  1. Environment variables (highest priority)
  2. User configuration files
  3. Default configurations (lowest priority)
- 🔄 Store configuration in platform-appropriate locations:
  - Windows: `%APPDATA%\GIMP\3.0\studiomuse\`
  - Mac: `~/Library/Application Support/GIMP/3.0/studiomuse\`
- 🔄 Implement configuration UI in the plugin settings
- 🔄 Add sensitive configuration handling for API keys
- 🔄 Use dotenv (.env) files for development environments
- 🔄 Ensure cross-platform compatibility for all configuration paths

### ✅ **Current Progress Summary**

We've made significant progress in both the backend refactoring and local plugin functionality:

1. **Core LLM Infrastructure**: Successfully moved the base LLM class, service provider, and prompts to the backend.
2. **LLM Providers**: Successfully implemented both Perplexity and Gemini LLM providers in the backend.
3. **Live LLM Testing**: Verified that both LLM providers can make successful API calls and return valid responses.
4. **Testing Framework**: Created comprehensive test scripts that grow with each component.
5. **API Foundation**: Set up the basic FastAPI server with health check and configuration endpoints.
6. **Palette Demystification API**: Successfully implemented and tested the palette demystification endpoint.
7. **API Client**: Created a client for the plugin to communicate with the backend API.
8. **Local LLM Integration**: Fixed the local LLM integration in the plugin:
   - Fixed prompt formatting in `PaletteDemistifyerLLM` to properly extract color data
   - Improved error handling for palette loading
   - Implemented proper display of results in the UI
   - Fixed JSON parsing of LLM responses

### 🔄 **Next Steps**

1. Update the plugin's demystifier dialog to use the API client instead of direct LLM calls
2. Implement the physical palette creation API endpoint with tests
3. Update the plugin's add palette dialog to use the API client
4. Continue with the remaining refactoring tasks for cross-platform compatibility

### ✅ **Final Outcome**

After completing this refactor, your plugin will:

- Work seamlessly on both Windows and macOS.
- Have a clean separation between frontend (GIMP plugin) and backend (LLM processing).
- Ensure cross-platform compatibility in file handling, dependency management, and execution.
- Include a comprehensive test suite that verifies all functionality.
- Support both local LLM processing and backend API communication.

Let me know if you need any modifications to this update!

