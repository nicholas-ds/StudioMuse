# 🚀 StudioMuse Refactor Roadmap

## **Overview**
This roadmap outlines the planned refactoring of the **StudioMuse** codebase to improve maintainability, modularity, and scalability.

### **🔹 Goals of This Refactor**
1. **Refactor LLM API Calls** → Fully utilize `BaseLLM` to remove redundant API logic.
2. **Decouple Palette Processing from LLMs** → Separate LLM API calls from color processing logic.
3. **Optimize Dialog Handling** → Improve `DialogManager` integration to reduce redundant builder calls.
4. **Additional Codebase Improvements** → Enhance error handling, modularize utilities, and improve project structure.

---

## **1️⃣ Refactor LLM API Calls with Dependency Injection**
### **Current Issues**
- Each LLM class (`GeminiLLM`, `PerplexityLLM`, etc.) duplicates `call_api()` logic.
- LLM clients are directly instantiated throughout the codebase, creating tight coupling.
- Some LLMs implement their own response parsing inconsistently.
- ✅ `call_llm.py` is redundant and has been removed.

### **Solution**
- Fully integrate `BaseLLM` to handle **all API calls**, response parsing, and payload preparation.
- ✅ Implement a **service provider/factory** for LLM clients to allow runtime selection of LLM provider.
- Standardize API response validation and parsing across all LLM implementations.
- Modify `GeminiLLM` and `PerplexityLLM` to **only override `prepare_payload()`**.

### **Steps to Implement**
1. ✅ **Create an `LLMServiceProvider` class** that manages LLM client instances.
2. **Refactor `BaseLLM`** to handle `call_api()` for all subclasses.
3. ✅ **Implement dependency injection** for LLM clients throughout the UI code.
4. **Remove duplicate `call_api()` logic** from `GeminiLLM`, `PerplexityLLM`, etc.
5. ✅ **Delete `call_llm.py`** (no longer needed).
6. **Verify API responses** using a common `parse_response()` method.

---

## **2️⃣ Decouple Palette Processing from LLMs with Enhanced Data Models**
### **Current Issues**
- ✅ `LLMPhysicalPalette` and `PaletteDemystifyerLLM` **inherit from LLM classes**, mixing concerns.
- ✅ Palette data is represented as simple dictionaries without encapsulated behavior.
- ✅ Testing palette functions requires **API calls**, making debugging harder.
- ✅ No standardized palette format or operations.

### **Solution**
- ✅ Create a **`PaletteProcessor`** class that handles color processing **without LLM dependency**.
- ✅ Implement proper **class models** for palette data with methods for common operations.
- ✅ Modify `LLMPhysicalPalette` and `PaletteDemystifyerLLM` to **use** LLM classes rather than inherit from them.
- Add support for importing/exporting standard color formats.

### **Steps to Implement**
1. ✅ **Create `PaletteProcessor` class** in `colorBitMagic/utils/`.
2. ✅ **Implement `PaletteData` and `PhysicalPalette` model classes** with appropriate methods.
3. ✅ **Refactor `LLMPhysicalPalette` and `PaletteDemystifyerLLM`** to use `PaletteProcessor`.
4. ✅ **Ensure all palette functions** (like `generate_palette()`) work **independently of LLMs**.
5. **Add version control** for palette formats.
6. ✅ **Update `colorBitMagic_ui.py`** to use the new palette models.

---

## **3️⃣ Optimize Dialog Handling with State Management**
### **Current Issues**
- `colorBitMagic_ui.py` manually retrieves builders from `DialogManager`, creating redundant logic.
- Dialogs share state by storing objects directly in the DialogManager.
- Some dialogs call `Gtk.Builder()` directly instead of using `DialogManager`.
- Event handlers are inconsistently defined across the codebase.

### **Solution**
- Implement a proper **application state manager** class for data sharing between dialogs.
- Standardize `DialogManager` usage so UI elements are retrieved directly from stored dialogs.
- Create an **`EventHandlerRegistry`** to organize dialog event handlers consistently.
- Define clear state transitions between dialogs.

### **Steps to Implement**
1. **Create an `AppState` class** to manage shared application state.
2. **Implement `EventHandlerRegistry`** to map dialog IDs to sets of handlers.
3. **Group handlers by dialog** in separate files/classes.
4. **Use events for state changes** rather than direct object references.
5. **Ensure all UI functions** use `DialogManager.dialogs[window_id]`.
6. **Remove direct `Gtk.Builder()` calls** in UI scripts.
7. **Refactor event handlers** (`on_submit_clicked`, etc.) to interact with `DialogManager` cleanly.

---

## **4️⃣ API Response Parsing and Validation**
### **Current Issues**
- LLM response handling has some validation but could be more robust.
- Error handling is focused on logging rather than recovery.
- No consistent schema validation for responses.

### **Solution**
- Implement standardized **JSON schema validation** for LLM responses.
- Create **typed response models** with proper validation.
- Implement **retry mechanisms** for API calls.
- Handle partial/incomplete responses gracefully.

### **Steps to Implement**
1. **Define response schemas** for each LLM interaction.
2. **Implement a `ResponseValidator` class** for validating responses.
3. **Add retry logic** for failed API calls.
4. **Create specific exception types** for different validation errors.
5. **Update LLM classes** to use the new validation system.

---

## **5️⃣ Additional Codebase Improvements**
### **🔹 Improve Error Handling**
✅ **Standardize logging:** Ensure **all errors** are logged using `log_error()`.
✅ **Refactor error handling:** Remove direct `print()` statements inside LLM classes.
✅ **Add graceful degradation** for failed palette operations.
✅ **Create a user-facing error recovery system** that guides users through issues.

### **🔹 Modularize Utility Functions**
- ✅ **Centralize JSON processing** in `clean_and_verify_json`.
- ✅ **Centralize palette file operations** in `PaletteProcessor`.
- **Split `colorBitMagic_utils.py`** into:
  - `logger.py` → Handles error logging.
  - `dropdowns.py` → Handles dropdown population.
  - `file_utils.py` → Handles JSON and file operations.

### **🔹 File System Abstraction**
✅ **Create a file system abstraction layer** via `PaletteProcessor`.
✅ **Implement proper path normalization** across platforms.
**Add support for different storage backends** (user directory, plugin directory, etc.).

### **🔹 Restructure XML Files for Reusability**
**Move `templates/` to `StudioMuse/ui/`** for **future plugin compatibility**.
**Consider implementing a UI builder utility** for common UI patterns.

---

## **✅ Next Steps**
### **Phase 1: LLM Service Provider Implementation** (Estimated: 1-2 days remaining)
- [✅] Create `LLMServiceProvider` class.
- [✅] Implement dependency injection for LLM clients.
- [ ] Refactor `BaseLLM` improvements.
- [ ] Standardize API response parsing.
- [✅] Delete `call_llm.py`.

### **Phase 2: Enhanced Palette Data Models** (COMPLETED)
- [✅] Implement `PaletteData` and `PhysicalPalette` model classes.
- [✅] Create `PaletteProcessor` class.
- [✅] Update `LLMPhysicalPalette` and `PaletteDemystifyerLLM`.
- [✅] Test palette functions independently of LLMs.

### **Phase 3: Dialog State Management** (Estimated: 2-3 days)
- [ ] Create `AppState` class.
- [ ] Implement `EventHandlerRegistry`.
- [ ] Refactor UI event handlers.
- [ ] Define state transitions between dialogs.
- [ ] Improve `DialogManager` calls in `colorBitMagic_ui.py`.

### **Phase 4: Response Validation** (Estimated: 1-2 days)
- [ ] Define response schemas.
- [ ] Implement `ResponseValidator` class.
- [ ] Add retry logic for API calls.
- [ ] Update LLM classes to use the new validation system.

### **Phase 5: Additional Improvements** (Ongoing)
- [✅] Standardize error handling.
- [ ] Modularize utilities.
- [✅] Create file system abstraction.
- [ ] Restructure XML files.

---

### **Final Notes**
📌 **Progress:** We've completed Phase 2 and made significant progress on Phase 1. The codebase now has proper palette data models and processing that are independent of LLM functionality. This allows for better testing, maintainability, and future extensibility.

📌 **Next Focus:** Complete Phase 1 (LLM Service Provider) and then move to Phase 3 (Dialog State Management) to improve UI code organization.

🚀 **Let's continue the refactor!**