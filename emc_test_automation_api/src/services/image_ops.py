import ctypes
import math
import subprocess
import time
from PIL import ImageGrab, Image
import pygetwindow as gw
import os
from io import BytesIO
import win32gui
import win32ui
import win32con
from pywinauto import Application

class ImageOps:
    # Function to get system DPI scaling
    def get_dpi_scaling():
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        dpi = user32.GetDpiForSystem()
        print(f"Sys DPI {dpi}")
        return dpi / 96  # 96 is the standard DPI, so scaling is dpi/96
    
    def capture_minimized_window(hwnd):
        # Get the window's size and position
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bot - top
        # Get the window's device context
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # Create a bitmap object to store the image
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # Copy the content from the window's device context into our bitmap
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

        # Convert the bitmap into a PIL Image
        bmp_info = save_bitmap.GetInfo()
        bmp_str = save_bitmap.GetBitmapBits(True)
        img = Image.frombuffer("RGB", (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, "raw", "BGRX", 0, 1)
        return img

    @staticmethod
    def generate_schematic_image(schematic_file):
        ltspice_path = "C:/Users/Dilshad/AppData/Local/Programs/ADI/LTspice/LTspice.exe"
        # Step 1: Check if the input file exists
        if not os.path.exists(schematic_file):
            return {'status': 'error', 'error_details': 'Schematic file does not exist.'}
        
        # Step 2: Check if LTSpice exists at the specified path
        if not os.path.exists(ltspice_path):
            return {'status': 'error', 'error_details': 'LTspice executable not found at the specified path.'}

        try:
            # Get the directory of the schematic file
            file_dir = os.path.dirname(schematic_file)
            
            # Generate the PNG output file path based on the input schematic filename
            file_name = os.path.splitext(os.path.basename(schematic_file))[0]  # Get file name without extension
            png_output_path = os.path.join(file_dir, f"{file_name}.png")  # Construct the output PNG path

            # Step 3: Kill any previous LTSpice processes (if any)
            subprocess.call(["taskkill", "/F", "/IM", "LTspice.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)  # Allow time for the process to be killed

            # Step 4: Open LTSpice with the .asc file
            ltspice_process = subprocess.Popen([ltspice_path, schematic_file])
            time.sleep(2)  # Wait for LTSpice to fully load (increase sleep time if needed)
            # Define the title of the window you want to capture
            ltspice_windows = gw.getWindowsWithTitle("LTspice")
            print(f"LTSpice Windows {ltspice_windows}")
            ltspice_window = ltspice_windows[0]

            window_title = ltspice_window.title  # Replace with your window title
            print(f"Test now window {window_title}")
            # Replace 'YourApp.exe' with the name of the executable or window title.
            app = Application().connect(path=ltspice_path)
            target_window = app.window(title=window_title)
            print("Main window title:", target_window.window_text())

            # Capture the window content as an image.
            # target_window.restore()
            target_window.set_focus()
            screenshot = target_window.capture_as_image()
            # Get the original dimensions of the screenshot.
            width, height = screenshot.size
            dpi_scaling_factor = ImageOps.get_dpi_scaling()

            # Calculate the cropping area to trim 10% from the top and 5% from the bottom.
            top_trim = math.ceil(0.10 * height * dpi_scaling_factor)   # Top 10%
            bottom_trim = math.ceil(0.03 * height * dpi_scaling_factor)  # Bottom 2%

            left_trim = math.ceil(0.004 * width * dpi_scaling_factor)
            right_trim = math.ceil(0.004 * width * dpi_scaling_factor)

            # Define the cropping box: (left, top, right, bottom).
            crop_box = (left_trim, top_trim, width - right_trim, height - bottom_trim)
            print("Crop box:", crop_box)
            print(f"Scaling factor {dpi_scaling_factor}")
            print(f"Trim {left_trim, right_trim, top_trim, bottom_trim}")
            print(f"Height {height} and width {width}")

            # Perform cropping
            cropped_screenshot = screenshot.crop(crop_box)
            cropped_width, cropped_height = cropped_screenshot.size
            print("Cropped dimensions:", cropped_width, "x", cropped_height)
            # Convert the image to a byte stream for front-end use
            img_byte_arr = BytesIO()
            cropped_screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            # Step 10: Optional: Close LTSpice after capturing the screenshot
            subprocess.call(["taskkill", "/F", "/IM", "LTspice.exe"])
            time.sleep(1)  # Ensure the process has terminated
            
            # Step 11: Return success with the image data
            return {'status': 'success', 'image': img_byte_arr.getvalue(), 'netlist': ''}

        except Exception as e:
            return {'status': 'error', 'error_details': f"An error occurred: {str(e)}"}

