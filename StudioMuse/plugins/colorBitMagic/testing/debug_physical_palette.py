import os
import sys
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the palette loading function
from utils.palette_processor import load_physical_palette_data

def debug_physical_palette(palette_name):
    """Debug the physical palette data loading"""
    print("="*50)
    print(f"DEBUGGING PHYSICAL PALETTE: {palette_name}")
    print("="*50)
    
    try:
        # Load the physical palette data
        data = load_physical_palette_data(palette_name)
        
        # Print the type and structure
        print(f"Data type: {type(data).__name__}")
        
        if isinstance(data, dict):
            print("\nDictionary keys:")
            for key in data.keys():
                print(f"- {key}")
            
            if "colors" in data:
                print(f"\nNumber of colors: {len(data['colors'])}")
                print("\nSample colors:")
                for i, color in enumerate(data["colors"][:3]):
                    print(f"{i+1}. {color}")
        elif isinstance(data, list):
            print(f"\nList length: {len(data)}")
            print("\nSample items:")
            for i, item in enumerate(data[:3]):
                print(f"{i+1}. {item}")
        elif isinstance(data, str):
            print(f"\nString value: {data}")
        else:
            print(f"\nUnexpected data type: {type(data).__name__}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a known physical palette
    palette_name = "Mont Marte Extra Soft Oil Pastels Vibrant Hues Premium 52pc"
    debug_physical_palette(palette_name) 