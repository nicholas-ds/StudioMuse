# StudioMuse

## Overview

StudioMuse is a plugin based suite of tools and mini applications built to enhance artistic workflows with physical media such as oil paint, pastels, or watercolors, by integrating advanced color analysis and AI features. The tools are designed and built with traditional artists in mind. The first complete tool, **colorBitMagic**, assists artists in coordinating colors from reference images to their physical palettes, such as a particular set of oil pastels or a specific set of watercolor paints.

Physical palettes are generated using Perplexity's web search API. Physical palettes are saved as JSON files to store for repeated use and future tools to utilize.


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
2. Navigate to Extensions > StudioMuse > StudioMuse Suite to open the main application window.
3. The suite contains several tools organized into categories:
   - **Analysis**: Color matching and palette tools
   - **Structure**: Image composition tools
   - **VisionLab**: Advanced visualization features
   - **Settings**: Configuration options

### ColorBitMagic Analysis Tools

#### Palette Demystifyer
This tool teaches you practical color matching theory by bridging the gap between your physical art supplies and
your reference photos.

1. In the Analysis tab, select the "Palette Demystifyer" tool
2. Select your GIMP palette from the dropdown
3. Select your physical palette from the second dropdown
4. Click "Submit" to analyze
5. Results will show:
   - Color swatches for visual reference
   - RGB values for digital colors
   - Matching physical colors from your art supplies
   - Mixing suggestions for complex colors

#### Physical Palette Creator

1. Click "Add Physical Palette" in the Analysis tab
2. Enter a description of your art supplies, including:
   - Brand name
   - Number of colors in the set
   - Product name/line
   Example: "Mont Marte 52 Piece Oil Pastel Kit"
3. Click "Generate" to create a digital version of your physical palette
4. Review the results and click "Save" to store for future use

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

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

### Environment Variables

Required API keys:
- `PERPLEXITY_KEY`: For color matching and physical palette generation
- `GEMINI_API_KEY`: For advanced AI features and analysis

You can set these using:
```bash
export PERPLEXITY_KEY='your-perplexity-key'
export GEMINI_API_KEY='your-gemini-key'
```

### Development Status

- **ColorBitMagic Plugin**: ✅ Complete!
  - Full palette analysis and matching
  - Physical palette generation
  - LLM-powered color theory assistance

- **Proportia Plugin**: 🚧 In Development
  - Measurement and scaling tools
  - Canvas planning features
  - Expected release: TBD

- **VisionLab**: 📋 Planned
  - Vision model based tools TBD
  

### Configuration

Configuration files are stored in:
- Windows: `%APPDATA%\GIMP\3.0\studiomuse\`
- Mac: `~/Library/Application Support/GIMP/3.0/studiomuse\`

The plugin supports configuration through:
1. Environment variables (highest priority)
2. User configuration files
3. Default configurations

