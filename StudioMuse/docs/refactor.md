# 🚀 StudioMuse Refactor Roadmap

## **Overview**
This roadmap outlines the planned refactoring of the **StudioMuse** codebase to improve maintainability, modularity, and scalability.

### **🔹 Goals of This Refactor**
1. **Refactor LLM API Calls** → Fully utilize `BaseLLM` to remove redundant API logic.
2. **Decouple Palette Processing from LLMs** → Separate LLM API calls from color processing logic.
3. **Optimize Dialog Handling** → Improve `DialogManager` integration to reduce redundant builder calls.
4. **Additional Codebase Improvements** → Enhance error handling, modularize utilities, and improve project structure.

---

## **1️⃣ Refactor LLM API Calls**
### **Current Issues**
- Each LLM class (`GeminiLLM`, `PerplexityLLM`, etc.) duplicates `call_api()` logic.
- Some LLMs implement their own response parsing inconsistently.
- `call_llm.py` is redundant and should be removed.

### **Solution**
- Fully integrate `BaseLLM` to handle **all API calls**, response parsing, and payload preparation.
- Modify `GeminiLLM` and `PerplexityLLM` to **only override `prepare_payload()`**.

### **Steps to Implement**
1. **Refactor `BaseLLM`** to handle `call_api()` for all subclasses.
2. **Remove duplicate `call_api()` logic** from `GeminiLLM`, `PerplexityLLM`, etc.
3. **Delete `call_llm.py`** (no longer needed).
4. **Verify API responses** using a common `parse_response()` method.

---

## **2️⃣ Decouple Palette Processing from LLMs**
### **Current Issues**
- `LLMPhysicalPalette` and `PaletteDemystifyerLLM` **inherit from LLM classes**, mixing concerns.
- This **hardcodes** LLM selection inside palette-processing logic.
- Testing palette functions requires **API calls**, making debugging harder.

### **Solution**
- Create a **`PaletteProcessor`** class that handles color processing **without LLM dependency**.
- Modify `LLMPhysicalPalette` and `PaletteDemystifyerLLM` to **use** LLM classes rather than inherit from them.

### **Steps to Implement**
1. **Create `PaletteProcessor` class** in `colorBitMagic/utils/`.
2. **Refactor `LLMPhysicalPalette` and `PaletteDemystifyerLLM`** to use `PaletteProcessor`.
3. **Ensure all palette functions** (like `generate_palette()`) work **independently of LLMs**.
4. **Update `colorBitMagic_ui.py`** to call `PaletteProcessor` instead of mixing LLM logic.

---

## **3️⃣ Optimize Dialog Handling**
### **Current Issues**
- `colorBitMagic_ui.py` manually retrieves builders from `DialogManager`, creating redundant logic.
- Some dialogs call `Gtk.Builder()` directly instead of using `DialogManager`.

### **Solution**
- Standardize `DialogManager` usage so UI elements are retrieved directly from stored dialogs.

### **Steps to Implement**
1. **Ensure all UI functions** use `DialogManager.dialogs[window_id]`.
2. **Remove direct `Gtk.Builder()` calls** in UI scripts.
3. **Refactor event handlers** (`on_submit_clicked`, etc.) to interact with `DialogManager` cleanly.

---

## **4️⃣ Additional Codebase Improvements**
### **🔹 Improve Error Handling**
✅ **Standardize logging:** Ensure **all errors** are logged using `log_error()`.
✅ **Refactor error handling:** Remove direct `print()` statements inside LLM classes.

### **🔹 Modularize Utility Functions**
✅ **Split `colorBitMagic_utils.py`** into:
   - `logger.py` → Handles error logging.
   - `dropdowns.py` → Handles dropdown population.
   - `file_utils.py` → Handles JSON and file operations.

### **🔹 Restructure XML Files for Reusability**
✅ **Move `templates/` to `StudioMuse/ui/`** for **future plugin compatibility**.

---

## **✅ Next Steps**
### **Phase 1: LLM Refactor** (Estimated: 1-2 days)
- [ ] Implement `BaseLLM` improvements.
- [ ] Remove duplicate `call_api()` functions.
- [ ] Delete `call_llm.py`.

### **Phase 2: Palette Processing Refactor** (Estimated: 2-3 days)
- [ ] Implement `PaletteProcessor` class.
- [ ] Update `LLMPhysicalPalette` and `PaletteDemystifyerLLM`.
- [ ] Test palette functions independently of LLMs.

### **Phase 3: UI & Dialog Optimization** (Estimated: 1 day)
- [ ] Refactor UI event handlers.
- [ ] Improve `DialogManager` calls in `colorBitMagic_ui.py`.

### **Phase 4: Additional Improvements** (Ongoing)
- [ ] Standardize error handling.
- [ ] Modularize utilities.
- [ ] Restructure XML files.

---

### **Final Notes**
📌 **Goal:** Ensure StudioMuse remains maintainable as it grows. These changes will make future feature additions **easier, cleaner, and more scalable**.

🚀 **Let's refactor!**

