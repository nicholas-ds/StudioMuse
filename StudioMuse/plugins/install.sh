#!/bin/bash

# Detect operating system
OS="$(uname -s)"
case "$OS" in
    "Darwin")
        GIMP_PLUGIN_DIR="$HOME/Library/Application Support/GIMP/3.0/plug-ins"
        ;;
    "Linux")
        GIMP_PLUGIN_DIR="$HOME/.config/GIMP/3.0/plug-ins"
        ;;
    "MINGW"*|"MSYS"*|"CYGWIN"*)
        GIMP_PLUGIN_DIR="$APPDATA/GIMP/3.0/plug-ins"
        ;;
    *)
        echo "Unsupported operating system: $OS"
        exit 1
        ;;
esac

# Check if GIMP is running
if pgrep -x "gimp" > /dev/null; then
    echo "GIMP is currently running. Closing GIMP..."
    case "$OS" in
        "Darwin")
            osascript -e 'quit app "GIMP"'
            ;;
        "Linux")
            pkill gimp
            ;;
        "MINGW"*|"MSYS"*|"CYGWIN"*)
            taskkill /IM gimp.exe /F
            ;;
    esac
    # Wait for GIMP to close
    sleep 2
fi

# Remove any existing plugin installation
rm -rf "$GIMP_PLUGIN_DIR/colorBitMagic"

# Create plugin directory
mkdir -p "$GIMP_PLUGIN_DIR/colorBitMagic"

# Copy plugin files
cp "$(dirname "$0")/colorBitMagic/colorBitMagic.py" "$GIMP_PLUGIN_DIR/colorBitMagic/"

# Make the plugin executable
chmod +x "$GIMP_PLUGIN_DIR/colorBitMagic/colorBitMagic.py"

echo "Plugin installed successfully to: $GIMP_PLUGIN_DIR/colorBitMagic"

# Start GIMP
echo "Starting GIMP..."
case "$OS" in
    "Darwin")
        open -a GIMP
        ;;
    "Linux")
        gimp &
        ;;
    "MINGW"*|"MSYS"*|"CYGWIN"*)
        start gimp
        ;;
esac
