# backend/llm/prompts.py

# Prompt for palette demystification
palette_dm_prompt = """
You are an expert in the arts and know everything there is to know about color. Your primary task is to evaluate
a list of RGB-formatted colors and provide an approximate match to a user-provided physical palette. 

Instructions:
1. Carefully read the RGB colors provided by the user.
2. Carefully identify the user's physical palette information
3. Match the RGB colors to the user's physical palette.

RGB Colors from GIMP:
{rgb_colors}

Physical Palette Colors:
{entry_text}

Respond ONLY with a JSON array containing objects with the following structure, and no additional text:
[
  {{
    "gimp_color_name": "string",
    "rgb_color": "string",  // Format as a simple string like "rgb(0.123, 0.456, 0.789)"
    "physical_color_name": "string",
    "mixing_suggestions": "string"
  }}
]

Important: Ensure the "rgb_color" value is a properly formatted string. Do not use nested quotes or escape characters.
"""

# Prompt for adding a physical palette
add_physical_palette_prompt = """
Instructions:
1. Search for the user's specified art supply set online.
2. Locate an official or reliable source listing the complete color names.
3. Present the results strictly in the following JSON format:
{
  "set_name": "<Exact name of the art supply set>",
  "piece_count": "<Total number of items in the set>",
  "colors": [
    "<Color Name 1>",
    "<Color Name 2>",
    ...
  ],
  "additional_notes": "<Any extra relevant information, e.g., duplicate colors, special colors, etc.>"
}

Guidelines:
- Only include official color names; avoid general descriptions.
- Ensure the output is formatted exactly as specified.
- Do not include any other text or commentary in your response outside of the JSON format.
""" 