import os
import shutil
from pathlib import Path

# Get user's AppData path in a Windows-friendly way
gimp_plugin_dir = Path(os.getenv('APPDATA')) / "GIMP" / "3.0" / "plug-ins"
script_dir = Path(__file__).parent.absolute()

print(f"→ Installing StudioMuse from: {script_dir}")
print(f"→ To: {gimp_plugin_dir / 'studiomuse'}")

# Remove previous version if it exists
if (gimp_plugin_dir / "studiomuse").exists():
    shutil.rmtree(gimp_plugin_dir / "studiomuse")

# Create plugin directory
(gimp_plugin_dir / "studiomuse").mkdir(parents=True, exist_ok=True)

# Copy files
shutil.copytree(script_dir, gimp_plugin_dir / "studiomuse", dirs_exist_ok=True)

# Set execute permission on the main plugin file
studiomuse_script = gimp_plugin_dir / "studiomuse" / "studiomuse.py"
if os.name != 'nt':  # Only set execute permission on non-Windows systems
    os.chmod(studiomuse_script, 0o755)

print("✅ Plugin installed.")
print("🚀 Run GIMP from terminal to view logs:")
print("")
print("    gimp") 