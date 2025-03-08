# Refactored Project Structure for StudioMuse GIMP Plugin

Based on your existing code and the recommended frontend/backend separation, here's an optimized project structure to clearly separate concerns and simplify development:

```
StudioMuse/
├── backend/                      # Backend server for handling LLM interactions
│   ├── api.py                    # ✅ FastAPI backend entry point
│   ├── requirements.txt          # ✅ fastapi, uvicorn, requests
│   └── llm/
│       ├── base_llm.py
│       ├── gemini_llm.py
│       ├── perplexity_llm.py
│       ├── LLMPhysicalPalette.py
│       └── llm_service_provider.py
│
└── plugins/
    └── colorBitMagic/
        ├── colorBitMagic.py        # Main GIMP plugin frontend script
        ├── colorBitMagic_ui.py
        ├── dialogs/
        │   ├── base_dialog.py
        │   ├── home_dialog.py
        │   ├── demystifyer_dialog.py
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
        │   └── colorBitMagic_utils.py
        │
        ├── palettes/              # Stored GIMP palette data (.json)
        │   └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
        │
        └── physical_palettes/     # Physical palettes (.json)
            └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
```

### Step-by-Step Plan for Cross-Platform Refactor (Windows & Mac)

#### 1️⃣ **Separate Frontend & Backend Clearly** - 🟡 In Progress

- ✅ Create `backend/api.py` with FastAPI server for handling color processing
- ✅ Set up basic health check and configuration endpoints
- ✅ Create `plugins/colorBitMagic/utils/api_client.py` for HTTP communication
- 🔄 Move `llm/` to `backend/` to ensure all LLM processing happens outside GIMP
- 🔄 Update imports in `colorBitMagic.py` to request data from the backend via HTTP

#### 2️⃣ **Update Plugin Execution Paths** - ⚪ Not Started

- Ensure `colorBitMagic.py` uses relative paths to locate `templates/`, `utils/`, and `dialogs/` correctly across OS.
- Update `install.py` and `install.sh` to properly detect OS and install in the correct GIMP plugin directory.
  - Mac: `~/Library/Application Support/GIMP/3.0/plug-ins/`
  - Windows: `%APPDATA%\GIMP\3.0\plug-ins\`

#### 3️⃣ **Ensure LLM Dependencies Work on Both OS** - 🟡 In Progress

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

#### 4️⃣ **Fix File System Issues (Windows/Mac Differences)** - ⚪ Not Started

- Use `os.path.join()` in `palette_processor.py` to ensure file paths work across both platforms.
- Ensure JSON file handling (read/write) works correctly for both Windows (`\`) and Mac (`/`).

#### 5️⃣ **Test & Debug on Both Platforms** - 🟡 In Progress

- ✅ Run backend on Windows to verify API calls:
  ```sh
  python api.py  # Uses uvicorn internally
  ```
- ✅ Verify basic API communication with `api_client.py`
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
  - Mac: `~/Library/Application Support/GIMP/3.0/studiomuse/`
- 🔄 Implement configuration UI in the plugin settings
- 🔄 Add sensitive configuration handling for API keys
- 🔄 Use dotenv (.env) files for development environments
- 🔄 Ensure cross-platform compatibility for all configuration paths

### ✅ **Final Outcome**

After completing this refactor, your plugin will:

- Work seamlessly on both Windows and macOS.
- Have a clean separation between frontend (GIMP plugin) and backend (LLM processing).
- Ensure cross-platform compatibility in file handling, dependency management, and execution.

Let me know if you need any modifications to this update!

