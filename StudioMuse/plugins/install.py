import os
import shutil
import subprocess
import sys
import time

def get_gimp_plugin_dir():
    """Detect OS and return the correct GIMP plugin directory."""
    if sys.platform == "darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/GIMP/3.0/plug-ins")
    elif sys.platform.startswith("linux"):  # Linux
        return os.path.expanduser("~/.config/GIMP/3.0/plug-ins")
    elif sys.platform.startswith("win"):  # Windows
        return os.path.join(os.getenv("APPDATA"), "GIMP", "3.0", "plug-ins")
    else:
        print(f"Unsupported operating system: {sys.platform}")
        sys.exit(1)

def is_gimp_running():
    """Check if GIMP is running."""
    if sys.platform == "darwin" or sys.platform.startswith("linux"):
        return subprocess.call(["pgrep", "-x", "gimp"], stdout=subprocess.DEVNULL) == 0
    elif sys.platform.startswith("win"):
        return "gimp.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
    return False

def close_gimp():
    """Close GIMP if it's running."""
    print("Closing GIMP...")
    if sys.platform == "darwin":
        subprocess.run(["osascript", "-e", 'quit app "GIMP"'])
    elif sys.platform.startswith("linux"):
        subprocess.run(["pkill", "gimp"])
    elif sys.platform.startswith("win"):
        subprocess.run(["taskkill", "/IM", "gimp.exe", "/F"])
    time.sleep(2)  # Wait for GIMP to close

def install_plugin():
    """Install the colorBitMagic plugin."""
    gimp_plugin_dir = get_gimp_plugin_dir()
    plugin_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "colorBitMagic")
    plugin_dest = os.path.join(gimp_plugin_dir, "colorBitMagic")

    if os.path.exists(plugin_dest):
        print("Removing existing plugin installation...")
        shutil.rmtree(plugin_dest)

    print("Installing plugin...")
    shutil.copytree(plugin_source, plugin_dest)
    
    # Ensure the main plugin script is executable (needed for macOS/Linux)
    main_script = os.path.join(plugin_dest, "colorBitMagic.py")
    if sys.platform != "win":
        os.chmod(main_script, 0o755)

    print(f"Plugin installed successfully to: {plugin_dest}")

def start_gimp():
    """Start GIMP."""
    print("Starting GIMP...")
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "GIMP"])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["gimp"])
    elif sys.platform.startswith("win"):
        subprocess.Popen(["start", "gimp"], shell=True)

def main():
    if is_gimp_running():
        close_gimp()
    
    install_plugin()
    start_gimp()

if __name__ == "__main__":
    main()
