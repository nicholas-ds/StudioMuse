#!/bin/bash

# Define GIMP plugin directory for macOS
GIMP_PLUGIN_DIR="$HOME/Library/Application Support/GIMP/3.0/plug-ins"

# Remove any existing plugin installation
rm -rf "$GIMP_PLUGIN_DIR/colorBitMagic"

# Create plugin directory
mkdir -p "$GIMP_PLUGIN_DIR/colorBitMagic"

# Copy plugin files
cp "$(dirname "$0")/colorBitMagic/colorBitMagic.py" "$GIMP_PLUGIN_DIR/colorBitMagic/"

# Make the plugin executable
chmod +x "$GIMP_PLUGIN_DIR/colorBitMagic/colorBitMagic.py"

echo "Plugin installed successfully to: $GIMP_PLUGIN_DIR/colorBitMagic"
echo "Please restart GIMP for the changes to take effect."
