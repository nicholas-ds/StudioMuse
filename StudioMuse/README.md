# StudioMuse

## Overview

StudioMuse is a GIMP plugin-based application designed to enhance artistic workflows by integrating advanced color analysis and recommendation features. The primary plugin, **colorBitMagic**, assists artists in matching colors from reference images to their personal palettes, such as Mont Marte's 52 Extra Soft Vibrant oil pastels.

## Current Development

### Features

- **colorBitMagic Plugin**: 
  - Extracts RGB and CMYK color data from selected areas in GIMP.
  - Interfaces with the Claude LLM API to provide color matching and art tips.
  - Integrates with GIMP's palette editor for enhanced user interaction.

### Technical Requirements

- **Platform**: GIMP 3.x
- **Backend**: Python, Claude LLM API

### Installation

1. Ensure GIMP 3.x is installed.
2. Clone the repository.
3. Navigate to the `plugins/colorBitMagic` directory and run the installation script.

### Usage

1. Open a reference photo in GIMP.
2. Use GIMP tools to select image areas and extract color data.
3. Send data to the Claude LLM API for color matching and art tips.
4. View recommendations and interact with GIMP's palette editor.

## Future Development

- **Additional Plugins**: Placeholder for future plugins.
- **Enhanced AI Integration**: Plans to improve AI models for more accurate color matching and recommendations.
- **User Interface Improvements**: Future plans for more intuitive UI elements and better integration with GIMP.
- **Cross-Platform Support**: Expanding compatibility beyond GIMP 3.x is a future goal.

## Directory Structure

- **plugins/**: Contains all GIMP plugins, including `colorBitMagic`.
- **backend/**: Backend server code, including shared utilities and plugin-specific logic.
- **docs/**: Documentation, setup guides, and design notes.
- **assets/**: Reference images and mock data.
- **scripts/**: Utility scripts for testing and deployment.
- **requirements.txt**: Python dependencies for the project.

## License

This project is licensed under the terms of the LICENSE file.
