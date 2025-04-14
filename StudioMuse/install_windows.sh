#!/bin/bash

GIMP_PLUGIN_DIR="/c/Users/17174/AppData/Roaming/GIMP/3.0/plug-ins"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Installing StudioMuse from: $SCRIPT_DIR"
echo "→ To: $GIMP_PLUGIN_DIR/studiomuse"

# Remove previous version
rm -rf "$GIMP_PLUGIN_DIR/studiomuse"
mkdir -p "$GIMP_PLUGIN_DIR/studiomuse"

# Copy and set permissions
cp -r "$SCRIPT_DIR"/* "$GIMP_PLUGIN_DIR/studiomuse/"
chmod +x "$GIMP_PLUGIN_DIR/studiomuse/studiomuse.py"

echo "✅ Plugin installed."
echo "🚀 Run GIMP from terminal to view logs:"
echo ""
echo "    gimp"
