#!/bin/bash

# Detect OS and set GIMP plugin directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PLUGIN_DIR="$HOME/Library/Application Support/GIMP/2.10/plug-ins"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    PLUGIN_DIR="$HOME/.gimp-2.10/plug-ins"
else
    # Windows (when running in Git Bash or similar)
    PLUGIN_DIR="$APPDATA/GIMP/2.10/plug-ins"
fi

# Create plugin directory if it doesn't exist
mkdir -p "$PLUGIN_DIR"

# Copy the plugin
cp "colorBitMagic/plugin.py" "$PLUGIN_DIR/colorBitMagic.py"
chmod +x "$PLUGIN_DIR/colorBitMagic.py"

echo "Plugin installed to: $PLUGIN_DIR"

# Check if GIMP is running and close it
if pgrep -x "gimp" > /dev/null; then
    echo "Closing GIMP..."
    pkill gimp
    sleep 2 # Wait for GIMP to fully close
fi

# Restart GIMP
echo "Reopening GIMP..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open -a GIMP
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gimp &
else
    # For Windows, replace this with a valid command to restart GIMP
    start "" "C:/Program Files/GIMP 2/bin/gimp-2.10.exe"
fi

echo "Please wait for GIMP to restart and test the plugin under Filters > ColorBitMagic."
