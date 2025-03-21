# StudioMuse

## Overview

StudioMuse is a GIMP plugin-based application designed to enhance artistic workflows with physical media such as oil paint, pastels, or watercolors, by integrating advanced color analysis and AI features. The primary plugin, **colorBitMagic**, assists artists in matching colors from reference images to their personal palettes, such as a particular set of oil pastels or a specific set of watercolor paints.

The integrated LLM also gives advice and insights into how to use the colors in your physical palette. Perplexity Sonar is used for this as their sonar model has built-in web search functionality that will be important for identifying particular physical palettes.

## Current Development

### Features

- **colorBitMagic Plugin**:
  - Extracts color data from user-created palettes.
  - Sends color data to the Perplexity Sonar API for color matching and art tips.
  - Integrates with GIMP's palette editor for enhanced user interaction.

### Technical Requirements

- **Platform**: GIMP 3.x
- **Backend**: Python, Perplexity Sonar API, Google Gemini API

### Installation

1. Ensure GIMP 3.x is installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/nicholas-ds/StudioMuse.git
   ```
3. Navigate to the `StudioMuse/plugins` directory and run the installation script:
   ```bash
   cd StudioMuse/plugins
   ./install.sh
   ```
4. Set the `PERPLEXITY_KEY` environment variable with your API key:
   ```bash
   export PERPLEXITY_KEY='your-api-key-here'
   ```
5. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Open a reference photo in GIMP.
2. Use GIMP selection tools (such as the lasso tool or Ellipse select tool) to select an area of the image you would like to extract colors from.
3. Create a new palette in GIMP's palette editor (Colors > Palettes > New Palette).
4. Open colorBitMagic plugin via Filters > ColorBitMagic > ColorBitMagic

### Palette Demystifyer

This is a tool that will help you approximate the colors in your physical art palette to the colors in the GIMP palette you generated with GIMP's palette editor.

## How it works

### Step 1: Create a physical palette

1. Click "Add Physical Palette" button.
2. In the dialog that appears, describe the art kit you are using. It is helpful to include the brand, number of items in the set, and (if the kit has it) the names of the kit itself.
 ex. "Mont Marte 52 Piece Oil Pastel Kit"
3. Click "generate", wait for LLM response.
4. The LLM will return a list of colors that are in the physical palette.
5. If you are happy with the results, click "Save".

### Step 2: Demystify your physical palette

1. Once you have saved at least one physical palette, navigate to the home page of the Palette Demystifyer function.
2. Select the GIMP palette you generated earlier in the first palette dropdown.
3. Select the physical paletted you saved in the previous step.
4. Click "Submit", wait for LLM response.
5. The LLM will return the list of colors in your GIMP palette, matched with the closest physical palette color in your set.

Future development will include a nicer UI for displaying the result of this process so you don't have to keep the window open to see the results. For now the LLM will respond and display the results in the GIMP console. The GIMP console can be added via the arrow button on the top right, above the GIMP control panel. By default, the control panel holds your layers tab.

"Menu Arrow" > Add Tab > Error Console



## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

