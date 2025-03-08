# Refactored Project Structure for StudioMuse GIMP Plugin

Based on your existing code and the recommended frontend/backend separation, here's an optimized project structure to clearly separate concerns and simplify development:

```
StudioMuse/
├── backend/                      # Backend server for handling LLM interactions
│   ├── api.py                    # FastAPI backend entry point
│   ├── requirements.txt          # fastapi, uvicorn, requests, pydantic, google-generativeai, etc.
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
        │   └── colorBitMagic_utils.py
        │
        ├── palettes/              # Stored GIMP palette data (.json)
        │   └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
        │
        └── physical_palettes/     # Physical palettes (.json)
            └── Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc.json
```

### Step-by-Step Plan for Cross-Platform Refactor (Windows & Mac)

#### 1️⃣ **Separate Frontend & Backend Clearly**

- Move `llm/` to `backend/` to ensure all LLM processing happens outside GIMP.
- Update imports in `colorBitMagic.py` to request data from the backend via HTTP.
- Ensure `backend/api.py` provides a FastAPI server for handling color processing.

#### 2️⃣ **Update Plugin Execution Paths**

- Ensure `colorBitMagic.py` uses relative paths to locate `templates/`, `utils/`, and `dialogs/` correctly across OS.
- Update `install.py` and `install.sh` to properly detect OS and install in the correct GIMP plugin directory.
  - Mac: `~/Library/Application Support/GIMP/3.0/plug-ins/`
  - Windows: `%APPDATA%\GIMP\3.0\plug-ins\`

#### 3️⃣ **Ensure LLM Dependencies Work on Both OS**

- Modify `backend/requirements.txt` to include only cross-platform dependencies.
- Use Conda (recommended) or `venv` for virtual environments:
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

#### 4️⃣ **Fix File System Issues (Windows/Mac Differences)**

- Use `os.path.join()` in `palette_processor.py` to ensure file paths work across both platforms.
- Ensure JSON file handling (read/write) works correctly for both Windows (`\`) and Mac (`/`).

#### 5️⃣ **Test & Debug on Both Platforms**

- Run backend on both Mac & Windows to verify API calls:
  ```sh
  uvicorn api:app --reload
  ```
- Verify that the GIMP plugin correctly fetches palette data from the backend on both platforms.
- Test JSON saving/loading in `physical_palettes/` on both OS.

#### 6️⃣ **Finalize Windows/Mac Installation Scripts**

- Ensure `install.py` and `install.sh` correctly install the plugin based on OS detection.
- Provide step-by-step setup documentation for Windows users (e.g., enabling scripts in PowerShell).

#### 7️⃣ **Implement Configuration Management System**

- Create a flexible configuration system that works across both plugin and backend
- Support multiple configuration sources with priority order:
  1. Environment variables (highest priority)
  2. User configuration files
  3. Default configurations (lowest priority)
- Store configuration in platform-appropriate locations:
  - Windows: `%APPDATA%\GIMP\3.0\studiomuse\`
  - Mac: `~/Library/Application Support/GIMP/3.0/studiomuse/`
- Implement configuration UI in the plugin settings
- Add sensitive configuration handling for API keys
- Use dotenv (.env) files for development environments
- Ensure cross-platform compatibility for all configuration paths

### ✅ **Final Outcome**

After completing this refactor, your plugin will:

- Work seamlessly on both Windows and macOS.
- Have a clean separation between frontend (GIMP plugin) and backend (LLM processing).
- Ensure cross-platform compatibility in file handling, dependency management, and execution.

Let me know if you need further refinements!
