import subprocess
import time
import pyautogui
from PIL import ImageGrab
import pygetwindow as gw
# Paths to executables and files
ltspice_path = "C:/Users/saldanha/AppData/Local/Programs/ADI/LTspice/LTspice.exe"  # Path to LTspice executable
# schematic_file = "C:/PythonProjects/emc_test_automation_dashboard/emc_test_automation_api/src/data/Schematics/test1/res_divider.asc"  # Path to the .asc schematic file
schematic_file = "C:/Users/saldanha/OneDrive/Documents/SoW1/Trainsient Immunity Example Circuits/iso_7637-2_pulse_2a.asc"
png_output_path = "C:/PythonProjects/emc_test_automation_dashboard/emc_test_automation_api/src/data/Schematics/test1/output_image.png"  # Path to save the PNG file
autohotkey_path = "C:/Program Files/AutoHotkey/v2/AutoHotkey.exe"  # Path to AutoHotkey executable

# Step 1: Open LTspice with the .asc file
subprocess.Popen([ltspice_path, schematic_file])
time.sleep(2)  # Wait for LTspice to fully open
print(gw.getWindowsWithTitle("LTspice")[0].__dict__)
# Step 2: Find the LTspice window and capture its screenshot
# Move to LTspice window (optional, ensure it's active)
ltspice_window = gw.getWindowsWithTitle("LTspice")[0].__dict__['_rect']  # Get LTspice window
# ltspice_window.activate()  # Bring it to the foreground
time.sleep(1)  # Allow time for window focus

# Get window bounds (left, top, width, height)
left, top, width, height = ltspice_window.left, ltspice_window.top, ltspice_window.width, ltspice_window.height

# Step 3: Capture the screenshot of the window's area
screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
screenshot.save(png_output_path)
print(f"Screenshot saved successfully at {png_output_path}")

# Optional: Close LTspice
time.sleep(1)
subprocess.call(["taskkill", "/F", "/IM", "LTspice.exe"])
