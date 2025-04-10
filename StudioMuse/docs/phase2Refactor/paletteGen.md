# StudioMuse Native Palette Generator

## 🌟 Goal

Build a native StudioMuse tool for creating GIMP palettes from image selections or layers, scoped to the active project. This replaces GIMP’s native "Import Palette" dialog with a fully controlled experience aligned to StudioMuse's project-aware architecture.

---

## 🔄 Motivation

- GIMP’s native palette importer lacks project metadata and integration
- User-generated palettes can’t be tracked or filtered per project
- StudioMuse requires scoped palette management for ColorBitMagic and future tools

---

## 💼 Features

### 1. Palette Source Options
- ✅ Selected area (default)
- ✅ Active layer
- ✅ Entire image

### 2. User Input Fields
- Palette name (auto-filled with current project prefix)
- Number of colors (slider or spinbox)
- Sampling interval (for spread-based sampling)
- Optional preview (basic swatch grid)

### 3. Actions
- [Create] → Generates GIMP palette via API and adds to active project
- [Cancel]

---

## 💡 Behavior Flow

1. User selects image region (or defaults to entire image)
2. Opens "Generate Palette" tool from ColorBitMagic or Analysis tab
3. UI shows palette preview + options
4. On "Create":
   - Palette name = `{project_id}: [user_name]`
   - Colors are extracted from pixels (average or sampled)
   - `gimp.palettes_new()` + `gimp.palettes_add_entry()` used to create palette
   - Palette saved to `~/.config/GIMP/3.0/palettes/*.gpl`
   - Entry logged in `projects/{id}/linked_palettes.json`

---

## 🔍 Palette Extraction Strategy

Use pixel-level sampling:
- Extract pixel data from selection/layer/image
- Cluster colors (e.g., k-means or median cut optional)
- Limit total entries by user-specified amount
- Optional: deduplicate visually similar colors

---

## 🔧 GIMP API Calls

```python
# Create palette
gimp.palettes_new("SunRa: Base Colors")

# Add entries
gimp.palettes_add_entry("SunRa: Base Colors", (r, g, b), "Dark Umber")
```

---

## 🏦 File Output

- GIMP handles `.gpl` creation
- We add entry to:
```json
projects/sun_ra_portrait/linked_palettes.json
[
  { "name": "SunRa: Base Colors", "gpl": "SunRa: Base Colors.gpl" }
]
```

---

## 🌀 Integration Points

- Add a "Create Palette" button inside **ColorBitMagic** and **Analysis → Palettes** section
- Only enabled if project is selected
- Optionally accessible from Settings stack in future

---

## 📆 Development Tasks

1. [ ] Build GTK dialog UI (`palette_generator.ui`)
2. [ ] Implement color extraction from selection/layer
3. [ ] Add GIMP palette creation logic
4. [ ] Write project tracking JSON entry
5. [ ] Wire into ColorBitMagic sidebar
6. [ ] Validate palette shows up in filtered dropdowns

---

## 🔎 Future Enhancements

- AI naming of colors ("Sunlit Ochre")
- Smart suggestions: generate multiple palettes
- Export palette preview as PNG
- Use palette for selection-based filtering (VisionLab tool crossover)

---

