import gi
from gi.repository import Gimp
import json
from .base_dialog import BaseDialog
from colorBitMagic_utils import (
    populate_palette_dropdown, 
    populate_physical_palette_dropdown,
    load_physical_palette_data,
    get_palette_colors,
    log_error
)
from llm.PaletteDemistifyerLLM import PaletteDemistifyerLLM

class DemystifyerDialog(BaseDialog):
    def __init__(self):
        super().__init__("dmMain.xml", "dmMainWindow")
        # Initialize dropdowns
        populate_palette_dropdown(self.builder)
        populate_physical_palette_dropdown(self.builder)
        
    def _get_signal_handlers(self):
        handlers = super()._get_signal_handlers()
        handlers.update({
            "on_submit_clicked": self.on_submit_clicked,
            "on_add_physical_palette_clicked": self.on_add_physical_palette_clicked
        })
        return handlers
        
    def on_submit_clicked(self, button):
        Gimp.message("Submit button clicked. Loading selected palettes...")

        try:
            # Get both dropdown selections
            palette_dropdown = self.builder.get_object("paletteDropdown")
            physical_palette_dropdown = self.builder.get_object("physicalPaletteDropdown")

            if palette_dropdown is None or physical_palette_dropdown is None:
                log_error("Could not find dropdowns in the UI. Check XML IDs.")
                return

            # Get selected values directly from the ComboBoxText widgets
            selected_palette = palette_dropdown.get_active_text()
            selected_physical_palette = physical_palette_dropdown.get_active_text()

            if selected_palette and selected_physical_palette:
                Gimp.message(f"Selected GIMP palette: {selected_palette}")

                # Load physical palette data
                physical_palette_data = load_physical_palette_data(selected_physical_palette)
                if physical_palette_data:
                    Gimp.message(f"Selected physical palette: {selected_physical_palette}")
                    Gimp.message(f"Loaded physical palette data: {json.dumps(physical_palette_data, indent=2)}")

                # Get GIMP palette colors
                palette_colors = get_palette_colors(selected_palette)
                rgb_palette_colors = {}
                for i, color in enumerate(palette_colors, 1):
                    rgba = color.get_rgba()
                    color_data = {
                        "R": round(rgba[0], 3),
                        "G": round(rgba[1], 3),
                        "B": round(rgba[2], 3),
                        "A": round(rgba[3], 3)
                    }
                    rgb_palette_colors[f"color{i}"] = color_data

                # Create a dictionary to store all data
                all_data = {
                    "gimp_palette_colors": rgb_palette_colors,
                    "physical_palette_data": physical_palette_data["colors"]
                }
                
                # Create an instance of PaletteDemistifyerLLM and call the LLM
                demystifyer = PaletteDemistifyerLLM(
                    gimp_palette_colors=all_data["gimp_palette_colors"], 
                    physical_palette_data=all_data["physical_palette_data"]
                )
                result = demystifyer.call_llm()

                if isinstance(result, list):  # Check if result is a list of color matches
                    # Get the TextView widget
                    text_view = self.builder.get_object("resultTextView")
                    if text_view is None:
                        log_error("Could not find TextView in the UI.")
                        return

                    # Format the results for display
                    display_text = "Color Matching Results:\n\n"
                    for match in result:
                        display_text += f"GIMP Color: {match['gimp_color_name']}\n"
                        display_text += f"RGB Values: {match['rgb_color']}\n"
                        display_text += f"Physical Color: {match['physical_color_name']}\n"
                        display_text += f"Mixing Tips: {match['mixing_suggestions']}\n"
                        display_text += "-" * 40 + "\n\n"

                    # Update the TextView
                    text_buffer = text_view.get_buffer()
                    text_buffer.set_text(display_text)
                    
                    Gimp.message("Analysis complete! Results displayed in the dialog.")
                else:
                    Gimp.message(f"Error during analysis: {result}")

            else:
                Gimp.message("Please select both a GIMP palette and a physical palette.")

        except Exception as e:
            log_error("Error while processing selected palettes", e)
            
    def on_add_physical_palette_clicked(self, button):
        from .add_palette_dialog import AddPaletteDialog
        AddPaletteDialog().show()
