#!/usr/bin/env python3
"""
Minimal Bot Script
A simplified version to test basic functionality:
- Launch GUI
- Connect to device
- Launch game
- Basic image detection
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, simpledialog, messagebox
import threading
import time
import traceback
import json
import os
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
import io

# Import core modules
import adb
from bot_related.device_gui_detector import GuiDetector
from utils import resource_path
from city_manager import CityManager


class MinimalBot:
    def __init__(self):
        self.device = None
        self.gui_detector = None
        self.is_running = False
        self.bot_thread = None
        
    def connect_device(self, device_serial=None, host='127.0.0.1', port=5555):
        """Connect to Android device via ADB"""
        try:
            # Initialize ADB bridge
            adb.bridge = adb.enable_adb()
            
            # Get available devices using the correct method
            devices = adb.bridge.get_client_devices()
            
            if not devices:
                # Try to connect to default emulator/device
                self.device = adb.bridge.get_device(host, port)
                if self.device is None:
                    return False, "No devices found. Make sure device/emulator is running and ADB is enabled."
            else:
                # Use first device if no specific serial provided
                if device_serial is None:
                    self.device = devices[0]
                else:
                    self.device = next((d for d in devices if d.serial == device_serial), None)
                    if not self.device:
                        return False, f"Device {device_serial} not found"
            
            # Verify device connection by testing a simple command
            try:
                test_result = self.device.shell('echo test')
                if 'test' not in test_result:
                    return False, "Device connected but not responding properly"
            except Exception as e:
                return False, f"Device not responding: {str(e)}"
            
            self.gui_detector = GuiDetector(self.device)
            return True, f"Connected to device: {self.device.serial}"
            
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def launch_game(self, package_name="com.ifun.google.kingdom"):
        """Launch the target game"""
        try:
            if not self.device:
                return False, "No device connected"
            
            # Check if game is already running
            if self.is_game_running(package_name):
                return True, f"Game {package_name} is already running"
            
            # Launch the game
            cmd = f'am start -n {package_name}/u3dsdk.kvmba.com.u3dsdk.MainSDKActivity'
            result = self.device.shell(cmd)
            
            # Wait a bit for the game to start
            time.sleep(5)
            
            if self.is_game_running(package_name):
                return True, f"Successfully launched {package_name}"
            else:
                return False, f"Failed to launch {package_name}"
                
        except Exception as e:
            return False, f"Launch error: {str(e)}"
    
    def is_game_running(self, package_name="com.ifun.google.kingdom"):
        """Check if the game is currently running"""
        try:
            if not self.device:
                return False
            
            cmd = 'dumpsys window windows'
            output = self.device.shell(cmd)
            return 'mCurrentFocus=Window{' in output and package_name in output
            
        except Exception as e:
            print(f"Error checking game status: {e}")
            return False
    
    def take_screenshot(self):
        """Take a screenshot and return as PIL Image"""
        try:
            if not self.device:
                return None
            
            screenshot_bytes = self.device.screencap()
            return Image.open(io.BytesIO(screenshot_bytes))
            
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def detect_ui_element(self, image_path, threshold=0.5):
        """Basic UI element detection using template matching"""
        try:
            if not self.gui_detector:
                return False, None
            
            # Get current screen
            screenshot_bytes = self.device.screencap()
            screen_img = cv2.imdecode(np.asarray(screenshot_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            # Load template image
            template_path = resource_path(image_path)
            template_img = cv2.imread(template_path)
            
            if template_img is None:
                return False, f"Template image not found: {template_path}"
            
            # Perform template matching
            result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Calculate center position
                h, w = template_img.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return True, (center_x, center_y)
            
            return False, None
            
        except Exception as e:
            return False, f"Detection error: {str(e)}"
    
    def detect_ui_element_in_area(self, image_path, search_area=None, threshold=0.5):
        """Detect UI element with optional search area constraint"""
        try:
            if not self.gui_detector:
                return False, None
            
            # Get current screen
            screenshot_bytes = self.device.screencap()
            screen_img = cv2.imdecode(np.asarray(screenshot_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            # If search area is specified, crop the screen to that area
            if search_area:
                x1, y1, x2, y2 = search_area
                screen_img = screen_img[y1:y2, x1:x2]
            
            # Load template image
            template_path = resource_path(image_path)
            template_img = cv2.imread(template_path)
            
            if template_img is None:
                return False, f"Template image not found: {template_path}"
            
            # Perform template matching
            result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Calculate center position
                h, w = template_img.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                # Adjust coordinates if search area was used
                if search_area:
                    center_x += search_area[0]
                    center_y += search_area[1]
                
                return True, (center_x, center_y)
            
            return False, None
            
        except Exception as e:
            return False, f"Detection error: {str(e)}"
    
    def detect_ui_element_with_area(self, image_path, search_area=None, threshold=0.8):
        """Detect UI element with optional search area constraint"""
        if not self.device:
            return False, None
            
        # Take screenshot
        screenshot = self.take_screenshot()
        if not screenshot:
            return False, None
        
        # Convert to OpenCV format
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Crop to search area if specified
        if search_area:
            x1, y1, x2, y2 = search_area
            # Ensure coordinates are within image bounds
            x1 = max(0, min(x1, screenshot_cv.shape[1]))
            y1 = max(0, min(y1, screenshot_cv.shape[0]))
            x2 = max(x1, min(x2, screenshot_cv.shape[1]))
            y2 = max(y1, min(y2, screenshot_cv.shape[0]))
            
            search_screenshot = screenshot_cv[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
        else:
            search_screenshot = screenshot_cv
            offset_x, offset_y = 0, 0
        
        # Load and detect template
        try:
            template = cv2.imread(image_path)
            if template is None:
                print(f"Could not load template image: {image_path}")
                return False, None
            
            # Perform template matching
            result = cv2.matchTemplate(search_screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # Adjust coordinates back to full screenshot
                x = max_loc[0] + offset_x
                y = max_loc[1] + offset_y
                w = template.shape[1]
                h = template.shape[0]
                return True, (x, y, w, h)
            else:
                return False, None
                
        except Exception as e:
            print(f"Error in template matching: {e}")
            return False, None
    
    def tap_screen(self, x, y, duration=0.1):
        """Tap the screen at given coordinates"""
        try:
            if not self.device:
                return False
            
            cmd = f'input tap {x} {y}'
            self.device.shell(cmd)
            time.sleep(duration)
            return True
            
        except Exception as e:
            print(f"Tap error: {e}")
            return False
        
    def click_coordinate(self, x, y):
        """Click at specific coordinates on the device screen"""
        if not self.device:
            print("No device connected")
            return False
        
        try:
            # Use ADB to send tap command
            result = self.device.shell(f"input tap {x} {y}")
            print(f"Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Error clicking coordinate ({x}, {y}): {e}")
            return False


class MinimalBotGUI:
    def __init__(self):
        self.bot = MinimalBot()
        self.root = tk.Tk()
        
        # Initialize city manager
        self.city_manager = CityManager(self.bot)
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI interface"""
        self.root.title("Minimal Bot - Game Automation")
        self.root.geometry("550x850")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Device connection section
        device_frame = ttk.LabelFrame(main_frame, text="Device Connection", padding="5")
        device_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Connection parameters
        conn_params_frame = ttk.Frame(device_frame)
        conn_params_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(conn_params_frame, text="Host:").grid(row=0, column=0, sticky=tk.W)
        self.host_entry = ttk.Entry(conn_params_frame, width=15)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(conn_params_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(conn_params_frame, width=8)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=0, column=3, padx=(5, 10))
        
        ttk.Button(conn_params_frame, text="Connect Device", command=self.connect_device).grid(row=0, column=4, padx=(10, 0))
        
        self.device_status = ttk.Label(device_frame, text="No device connected")
        self.device_status.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Game control section
        game_frame = ttk.LabelFrame(main_frame, text="Game Control", padding="5")
        game_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Package name entry
        ttk.Label(game_frame, text="Package Name:").grid(row=0, column=0, sticky=tk.W)
        self.package_entry = ttk.Entry(game_frame, width=40)
        self.package_entry.insert(0, "com.ifun.google.kingdom")  # Default RoK package
        self.package_entry.grid(row=0, column=1, padx=(5, 0))
        
        # Game control buttons
        button_frame = ttk.Frame(game_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Launch Game", command=self.launch_game).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Check Game", command=self.check_game).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Screenshot", command=self.take_screenshot).grid(row=0, column=2, padx=(0, 5))
        
        # Detection section
        detect_frame = ttk.LabelFrame(main_frame, text="UI Detection", padding="5")
        detect_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Image selection dropdown
        ttk.Label(detect_frame, text="Select Image:").grid(row=0, column=0, sticky=tk.W)
        self.image_var = tk.StringVar()
        self.image_combobox = ttk.Combobox(detect_frame, textvariable=self.image_var, width=35, state="readonly")
        self.image_combobox.grid(row=0, column=1, padx=(5, 0))
        
        # Refresh button for image list
        ttk.Button(detect_frame, text="Refresh", command=self.refresh_image_list).grid(row=0, column=2, padx=(5, 0))
        
        ttk.Button(detect_frame, text="Detect Element", command=self.detect_element).grid(row=1, column=0, pady=(5, 0))
        
        # Detection action buttons
        detect_buttons_frame = ttk.Frame(detect_frame)
        detect_buttons_frame.grid(row=1, column=1, pady=(5, 0), padx=(10, 0))
        
        ttk.Button(detect_buttons_frame, text="Highlight Element", command=self.highlight_element).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(detect_buttons_frame, text="Click Element", command=self.click_element).grid(row=0, column=1)
        
        # UI Capture section
        capture_frame = ttk.LabelFrame(main_frame, text="UI Element Capture", padding="5")
        capture_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Element name entry
        ttk.Label(capture_frame, text="Element Name:").grid(row=0, column=0, sticky=tk.W)
        self.element_name_entry = ttk.Entry(capture_frame, width=30)
        self.element_name_entry.grid(row=0, column=1, padx=(5, 10))
        
        # Capture buttons
        capture_buttons_frame = ttk.Frame(capture_frame)
        capture_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(capture_buttons_frame, text="Capture UI Element", command=self.capture_ui_element).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(capture_buttons_frame, text="Load Config", command=self.load_config).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(capture_buttons_frame, text="Save Config", command=self.save_config).grid(row=0, column=2)
        
        # Bot control section
        control_frame = ttk.LabelFrame(main_frame, text="Bot Control", padding="5")
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Basic Loop", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1)
        
        # City Actions section
        city_frame = ttk.LabelFrame(main_frame, text="City Actions", padding="5")
        city_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Navigation buttons
        nav_frame = ttk.Frame(city_frame)
        nav_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(nav_frame, text="Research Area", command=self.go_to_research).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(nav_frame, text="Check Ruins", command=self.count_available_marches).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(nav_frame, text="Shipment Collect", command=self.go_to_shipment).grid(row=0, column=2)
        
        # Panel buttons
        panel_frame = ttk.Frame(city_frame)
        panel_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(panel_frame, text="Buildings", command=self.click_buildings).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(panel_frame, text="Troops", command=self.click_troops).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(panel_frame, text="March", command=self.click_march).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(panel_frame, text="Reset City", command=self.reset_city).grid(row=0, column=3)
        
        # Periodic tasks
        tasks_frame = ttk.Frame(city_frame)
        tasks_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(tasks_frame, text="Explore Ruins", command=self.explore_ruins, width=12).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(tasks_frame, text="Run All Tasks", command=self.run_periodic_tasks, width=12).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(tasks_frame, text="Check City Status", command=self.check_city_status, width=12).grid(row=0, column=2)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Initialize image list
        self.refresh_image_list()
    
    def log(self, message):
        """Add message to log output"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def connect_device(self):
        """Connect to Android device"""
        self.log("Attempting to connect to device...")
        
        # Get host and port from GUI
        host = self.host_entry.get().strip() or "127.0.0.1"
        try:
            port = int(self.port_entry.get().strip() or "5555")
        except ValueError:
            self.log("✗ Invalid port number")
            return
        
        success, message = self.bot.connect_device(host=host, port=port)
        
        if success:
            self.device_status.config(text=f"Connected: {self.bot.device.serial}")
            self.log(f"✓ {message}")
        else:
            self.device_status.config(text="Connection failed")
            self.log(f"✗ {message}")
    
    def launch_game(self):
        """Launch the target game"""
        package_name = self.package_entry.get().strip()
        if not package_name:
            self.log("✗ Please enter a package name")
            return
        
        self.log(f"Launching game: {package_name}")
        success, message = self.bot.launch_game(package_name)
        
        if success:
            self.log(f"✓ {message}")
        else:
            self.log(f"✗ {message}")
    
    def check_game(self):
        """Check if game is running"""
        package_name = self.package_entry.get().strip()
        if not package_name:
            self.log("✗ Please enter a package name")
            return
        
        is_running = self.bot.is_game_running(package_name)
        if is_running:
            self.log(f"✓ Game {package_name} is running")
        else:
            self.log(f"✗ Game {package_name} is not running")
    
    def take_screenshot(self):
        """Take and save a screenshot"""
        self.log("Taking screenshot...")
        screenshot = self.bot.take_screenshot()
        
        if screenshot:
            # Save screenshot
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot.save(filename)
            self.log(f"✓ Screenshot saved as {filename}")
        else:
            self.log("✗ Failed to take screenshot")
    
    def detect_element(self):
        """Detect UI element using template matching with area constraints"""
        image_path = self.image_var.get().strip()
        if not image_path:
            self.log("✗ Please select an image")
            return
        
        self.log(f"Detecting element: {image_path}")
        
        # Check if this element has area constraints in config
        search_area = None
        try:
            if os.path.exists("minimal_config.json"):
                with open("minimal_config.json", 'r') as f:
                    config = json.load(f)
                    
                # Extract element name from path
                element_name = os.path.splitext(os.path.basename(image_path))[0]
                
                if "ui_elements" in config and element_name in config["ui_elements"]:
                    search_area = config["ui_elements"][element_name].get("search_area")
                    if search_area:
                        self.log(f"Using search area: {search_area}")
        except:
            pass
        
        # Use enhanced detection method
        if search_area:
            found, result = self.bot.detect_ui_element_in_area(image_path, search_area)
        else:
            found, result = self.bot.detect_ui_element(image_path)
        
        if found:
            if isinstance(result, tuple):
                x, y = result
                self.log(f"✓ Element found at position ({x}, {y})")
                # Optionally, you could add a tap feature here
                # self.bot.tap_screen(x, y)
            else:
                self.log(f"✓ Element detected")
        else:
            self.log(f"✗ Element not found. {result if isinstance(result, str) else ''}")
    
    def capture_ui_element(self):
        """Capture a UI element with area selection"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        
        element_name = self.element_name_entry.get().strip()
        if not element_name:
            self.log("✗ Please enter an element name")
            return
        
        self.log("Taking screenshot for UI element capture...")
        screenshot = self.bot.take_screenshot()
        
        if not screenshot:
            self.log("✗ Failed to take screenshot")
            return
        
        # Open area selector for element capture
        selector = AreaSelectorWindow(self.root, screenshot, "Select UI Element to Capture")
        self.root.wait_window(selector.window)
        
        selected_area = selector.get_selection()
        if not selected_area:
            self.log("✗ No area selected")
            return
        
        x1, y1, x2, y2 = selected_area
        self.log(f"Element area selected: ({x1}, {y1}) to ({x2}, {y2})")
        
        # Crop image to selected area
        cropped_image = screenshot.crop(selected_area)
        
        # Create resource directory if it doesn't exist
        resource_dir = "resource"
        os.makedirs(resource_dir, exist_ok=True)
        
        # Save the cropped image
        filename = f"{element_name}.png"
        filepath = os.path.join(resource_dir, filename)
        cropped_image.save(filepath)
        
        self.log(f"✓ UI element saved as: {filepath}")
        self.log(f"  Image size: {cropped_image.size}")
        
        # Ask user if they want to define a custom search area
        self.ask_for_search_area(element_name, filepath, selected_area, screenshot)
    
    def ask_for_search_area(self, element_name, image_path, element_area, screenshot):
        """Ask user if they want to define a custom search area"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Area Selection")
        dialog.grab_set()
        dialog.geometry("400x250")
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=f"Element '{element_name}' captured successfully!", 
                              font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Info
        info_text = (f"Element saved as: {image_path}\n"
                    f"Element size: {element_area[2]-element_area[0]} x {element_area[3]-element_area[1]} pixels\n\n"
                    "Would you like to define a custom search area?\n"
                    "This limits where the bot looks for this element,\n"
                    "making detection faster and more accurate.")
        
        info_label = tk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        
        # Result storage
        self.search_area_choice = None
        
        def use_automatic():
            """Use automatic search area (element bounds + padding)"""
            self.search_area_choice = "automatic"
            dialog.destroy()
        
        def use_manual():
            """Let user manually select search area"""
            self.search_area_choice = "manual"
            dialog.destroy()
        
        def use_full_screen():
            """Use full screen as search area"""
            self.search_area_choice = "fullscreen"
            dialog.destroy()
        
        # Buttons
        tk.Button(buttons_frame, text="Automatic\n(Recommended)", 
                 command=use_automatic, width=12, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="Manual Selection\n(Custom Area)", 
                 command=use_manual, width=12, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="Full Screen\n(Entire Screen)", 
                 command=use_full_screen, width=12, height=2).pack(side=tk.LEFT, padx=5)
        
        # Wait for user choice
        dialog.wait_window()
        
        # Process the choice
        if self.search_area_choice == "automatic":
            # Use element area with padding
            padding = 50  # pixels of padding around the element
            x1, y1, x2, y2 = element_area
            search_area = [
                max(0, x1 - padding),
                max(0, y1 - padding), 
                min(screenshot.width, x2 + padding),
                min(screenshot.height, y2 + padding)
            ]
            self.log(f"Using automatic search area with {padding}px padding: {search_area}")
            
        elif self.search_area_choice == "manual":
            # Let user select custom search area
            self.log("Please select the search area for this element...")
            selector = AreaSelectorWindow(self.root, screenshot, 
                                        f"Select Search Area for '{element_name}'")
            self.root.wait_window(selector.window)
            
            search_area = selector.get_selection()
            if not search_area:
                self.log("No search area selected, using automatic with padding")
                padding = 50
                x1, y1, x2, y2 = element_area
                search_area = [
                    max(0, x1 - padding),
                    max(0, y1 - padding),
                    min(screenshot.width, x2 + padding),
                    min(screenshot.height, y2 + padding)
                ]
            else:
                self.log(f"Custom search area selected: {search_area}")
                
        elif self.search_area_choice == "fullscreen":
            # Use entire screen
            search_area = [0, 0, screenshot.width, screenshot.height]
            self.log(f"Using full screen search area: {search_area}")
            
        else:
            # Default to automatic if something went wrong
            padding = 50
            x1, y1, x2, y2 = element_area
            search_area = [
                max(0, x1 - padding),
                max(0, y1 - padding),
                min(screenshot.width, x2 + padding),
                min(screenshot.height, y2 + padding)
            ]
            self.log(f"Using default automatic search area: {search_area}")
        
        # Update the image selection with the new path
        self.image_var.set(image_path)
        
        # Save to config with the chosen search area
        self.save_element_to_config(element_name, image_path, search_area)
    
    def save_element_to_config(self, element_name, image_path, search_area):
        """Save UI element to config with search area"""
        try:
            # Load current config
            if os.path.exists("minimal_config.json"):
                with open("minimal_config.json", "r") as f:
                    config = json.load(f)
            else:
                config = {
                    "game_package": "com.example.game",
                    "ui_elements": {}
                }
            
            # Ensure ui_elements section exists
            if "ui_elements" not in config:
                config["ui_elements"] = {}
            
            # Add/update element
            config["ui_elements"][element_name] = {
                "image_path": image_path,
                "search_area": list(search_area)  # Convert to list to ensure JSON serialization
            }
            
            # Save config
            with open("minimal_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            self.log(f"✓ Element '{element_name}' saved to config")
            self.log(f"  Image: {image_path}")
            self.log(f"  Search area: {search_area}")
            
        except Exception as e:
            self.log(f"✗ Error saving to config: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            config_file = filedialog.askopenfilename(
                title="Select Config File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="minimal_config.json"
            )
            
            if not config_file:
                return
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update GUI fields
            if "game_settings" in config and "package_name" in config["game_settings"]:
                self.package_entry.delete(0, tk.END)
                self.package_entry.insert(0, config["game_settings"]["package_name"])
            
            # Show loaded UI elements
            if "ui_elements" in config:
                self.log(f"✓ Loaded config from: {config_file}")
                self.log(f"Available UI elements:")
                for name, details in config["ui_elements"].items():
                    area = details.get("search_area", "Unknown")
                    self.log(f"  - {name}: {details.get('image_path', 'Unknown')} (area: {area})")
            else:
                self.log(f"✓ Config loaded but no UI elements found")
                
        except Exception as e:
            self.log(f"✗ Error loading config: {str(e)}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_file = filedialog.asksaveasfilename(
                title="Save Config File",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="minimal_config.json"
            )
            
            if not config_file:
                return
            
            # Create config with current settings
            config = {
                "game_settings": {
                    "package_name": self.package_entry.get().strip(),
                    "detection_threshold": 0.8
                },
                "detection_images": {},
                "ui_elements": {},
                "bot_settings": {
                    "loop_delay": 30,
                    "screenshot_on_error": True,
                    "debug_mode": False
                }
            }
            
            # Try to preserve existing UI elements
            try:
                if os.path.exists("minimal_config.json"):
                    with open("minimal_config.json", 'r') as f:
                        existing_config = json.load(f)
                        if "ui_elements" in existing_config:
                            config["ui_elements"] = existing_config["ui_elements"]
                        if "detection_images" in existing_config:
                            config["detection_images"] = existing_config["detection_images"]
            except:
                pass
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            self.log(f"✓ Config saved to: {config_file}")
            
        except Exception as e:
            self.log(f"✗ Error saving config: {str(e)}")
    
    def basic_loop(self):
        """Basic bot loop for testing"""
        loop_count = 0
        
        while self.bot.is_running:
            try:
                loop_count += 1
                self.log(f"Loop {loop_count}: Checking game status...")
                
                package_name = self.package_entry.get().strip()
                if not self.bot.is_game_running(package_name):
                    self.log("Game not running, attempting to launch...")
                    self.bot.launch_game(package_name)
                
                self.city_manager.explore_ruins_flow()
                
                # Wait before next loop
                for i in range(30):  # 30 second delay, checking every second for stop
                    if not self.bot.is_running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                self.log(f"✗ Error in bot loop: {str(e)}")
                traceback.print_exc()
                break
        
        self.log("Bot loop stopped")
    
    def start_bot(self):
        """Start the basic bot loop"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        
        self.bot.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.log("Starting basic bot loop...")
        self.bot.bot_thread = threading.Thread(target=self.basic_loop, daemon=True)
        self.bot.bot_thread.start()
    
    def stop_bot(self):
        """Stop the bot loop"""
        self.bot.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Stopping bot...")
    
    def run(self):
        """Start the GUI main loop"""
        self.log("Minimal Bot initialized")
        self.log("1. Connect to your Android device/emulator")
        self.log("2. Enter the package name of your target game")
        self.log("3. Test game launch and detection")
        self.log("4. Start the basic automation loop")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log("Shutting down...")
        finally:
            if self.bot.is_running:
                self.stop_bot()
    
    def highlight_element(self):
        """Highlight the detected UI element on screen"""
        image_path = self.image_var.get().strip()
        if not image_path:
            self.log("✗ Please select an image")
            return
        
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        
        self.log(f"Highlighting element: {image_path}")
        
        # Check if this element has area constraints in config
        search_area = None
        try:
            if os.path.exists("minimal_config.json"):
                with open("minimal_config.json", 'r') as f:
                    config = json.load(f)
                    
                # Extract element name from path
                element_name = os.path.splitext(os.path.basename(image_path))[0]
                
                if "ui_elements" in config and element_name in config["ui_elements"]:
                    search_area = config["ui_elements"][element_name].get("search_area")
                    if search_area:
                        self.log(f"Using search area: {search_area}")
        except:
            pass
        
        # Use enhanced detection method
        if search_area:
            found, result = self.bot.detect_ui_element_in_area(image_path, search_area)
        else:
            found, result = self.bot.detect_ui_element(image_path)
        
        if found:
            if isinstance(result, tuple):
                x, y = result
                self.log(f"✓ Element found at position ({x}, {y})")
                
                # Show highlight overlay
                self.show_highlight_overlay(x, y, search_area)
            else:
                self.log(f"✓ Element detected")
        else:
            self.log(f"✗ Element not found. {result if isinstance(result, str) else ''}")
    
    def click_element(self):
        """Detect and click the UI element"""
        image_path = self.image_var.get().strip()
        if not image_path:
            self.log("✗ Please select an image")
            return
        
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        
        self.log(f"Detecting and clicking element: {image_path}")
        
        # Check if this element has area constraints in config
        search_area = None
        try:
            if os.path.exists("minimal_config.json"):
                with open("minimal_config.json", 'r') as f:
                    config = json.load(f)
                    
                # Extract element name from path
                element_name = os.path.splitext(os.path.basename(image_path))[0]
                
                if "ui_elements" in config and element_name in config["ui_elements"]:
                    search_area = config["ui_elements"][element_name].get("search_area")
                    if search_area:
                        self.log(f"Using search area: {search_area}")
        except:
            pass
        
        # Use enhanced detection method
        if search_area:
            found, result = self.bot.detect_ui_element_in_area(image_path, search_area)
        else:
            found, result = self.bot.detect_ui_element(image_path)
        
        if found:
            if isinstance(result, tuple):
                x, y = result
                self.log(f"✓ Element found at position ({x}, {y})")
                
                # Click the element
                success = self.bot.tap_screen(x, y)
                if success:
                    self.log(f"✓ Clicked element at ({x}, {y})")
                else:
                    self.log(f"✗ Failed to click element")
            else:
                self.log(f"✓ Element detected but no position available")
        else:
            self.log(f"✗ Element not found. {result if isinstance(result, str) else ''}")
    
    def show_highlight_overlay(self, x, y, search_area=None):
        """Show a highlight overlay on the detected element"""
        try:
            # Take current screenshot
            screenshot = self.bot.take_screenshot()
            if not screenshot:
                self.log("✗ Failed to take screenshot for highlight")
                return
            
            # Create highlight overlay window
            highlight_window = tk.Toplevel(self.root)
            highlight_window.title("Element Highlight")
            highlight_window.grab_set()
            
            # Calculate display size
            img_width, img_height = screenshot.size
            max_width, max_height = 1000, 700
            
            if img_width > max_width or img_height > max_height:
                scale = min(max_width / img_width, max_height / img_height)
                display_width = int(img_width * scale)
                display_height = int(img_height * scale)
                scale_factor = scale
                display_image = screenshot.resize((display_width, display_height), Image.Resampling.LANCZOS)
            else:
                display_image = screenshot.copy()
                scale_factor = 1.0
                display_width, display_height = img_width, img_height
            
            # Draw highlight on the image
            draw = ImageDraw.Draw(display_image)
            
            # Scale coordinates for display
            highlight_x = int(x * scale_factor)
            highlight_y = int(y * scale_factor)
            
            # Draw crosshair
            crosshair_size = 20
            draw.line([highlight_x - crosshair_size, highlight_y, highlight_x + crosshair_size, highlight_y], 
                     fill="red", width=3)
            draw.line([highlight_x, highlight_y - crosshair_size, highlight_x, highlight_y + crosshair_size], 
                     fill="red", width=3)
            
            # Draw circle around the point
            circle_size = 15
            draw.ellipse([highlight_x - circle_size, highlight_y - circle_size,
                         highlight_x + circle_size, highlight_y + circle_size],
                        outline="red", width=3)
            
            # If search area exists, highlight it
            if search_area:
                x1, y1, x2, y2 = search_area
                # Scale search area coordinates
                scaled_x1 = int(x1 * scale_factor)
                scaled_y1 = int(y1 * scale_factor)
                scaled_x2 = int(x2 * scale_factor)
                scaled_y2 = int(y2 * scale_factor)
                
                # Draw search area rectangle
                draw.rectangle([scaled_x1, scaled_y1, scaled_x2, scaled_y2],
                              outline="blue", width=2)
            
            # Create canvas and display
            canvas = tk.Canvas(highlight_window, width=display_width, height=display_height)
            canvas.pack(padx=10, pady=10)
            
            photo = ImageTk.PhotoImage(display_image)
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Info label
            info_text = f"Element detected at ({x}, {y})"
            if search_area:
                info_text += f"\nSearch area: {search_area}"
            
            info_label = tk.Label(highlight_window, text=info_text, font=("Arial", 10))
            info_label.pack(pady=5)
            
            # Close button
            close_btn = tk.Button(highlight_window, text="Close", 
                                 command=highlight_window.destroy)
            close_btn.pack(pady=5)
            
            # Keep reference to photo to prevent garbage collection
            highlight_window.photo = photo
            
            # Center window
            highlight_window.update_idletasks()
            window_x = (highlight_window.winfo_screenwidth() // 2) - (highlight_window.winfo_width() // 2)
            window_y = (highlight_window.winfo_screenheight() // 2) - (highlight_window.winfo_height() // 2)
            highlight_window.geometry(f"+{window_x}+{window_y}")
            
            # Auto-close after 5 seconds
            highlight_window.after(5000, highlight_window.destroy)
            
        except Exception as e:
            self.log(f"✗ Error showing highlight: {str(e)}")
    
    def refresh_image_list(self):
        """Refresh the list of available resource images"""
        try:
            # Get all PNG images from resource folder
            resource_dir = "resource"
            if not os.path.exists(resource_dir):
                self.image_combobox['values'] = ()
                return
            
            # Get all PNG files
            png_files = []
            for file in os.listdir(resource_dir):
                if file.lower().endswith('.png'):
                    png_files.append(os.path.join(resource_dir, file))
            
            # Sort the files
            png_files.sort()
            
            # Update combobox
            self.image_combobox['values'] = png_files
            
            # Set default selection if available
            if png_files:
                if not self.image_var.get() or self.image_var.get() not in png_files:
                    self.image_var.set(png_files[0])
            
            self.log(f"Found {len(png_files)} resource images")
            
        except Exception as e:
            self.log(f"Error refreshing image list: {e}")
            self.image_combobox['values'] = ()

    # City Manager Methods
    def go_to_research(self):
        """Navigate to research area"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._go_to_research_thread, daemon=True).start()
    
    def _go_to_research_thread(self):
        """Thread for research navigation"""
        try:
            result = self.city_manager.go_to_research_area()
            if result:
                self.log("✓ Successfully navigated to research area")
            else:
                self.log("✗ Failed to navigate to research area")
        except Exception as e:
            self.log(f"✗ Error navigating to research: {e}")
    
    def count_available_marches(self):
        """Navigate to dragon panel"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._count_available_marches, daemon=True).start()
    
    def _count_available_marches(self):
        """Thread for counting available marches"""
        try:
            result = self.city_manager.count_available_marches()
            if result:
                self.log(f"✓ Successfully counted available marches: {result}")
            else:
                self.log("✗ Failed to count available marches")
        except Exception as e:
            self.log(f"✗ Error counting available marches: {e}")

    def go_to_shipment(self):
        """Navigate to shipment collect"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._go_to_shipment_thread, daemon=True).start()
    
    def _go_to_shipment_thread(self):
        """Thread for shipment navigation"""
        try:
            result = self.city_manager.go_to_shipment_collect()
            if result:
                self.log("✓ Successfully completed shipment collect routine")
            else:
                self.log("✗ Failed to complete shipment collect routine")
        except Exception as e:
            self.log(f"✗ Error in shipment collect: {e}")
    
    def click_buildings(self):
        """Click buildings panel"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._click_buildings_thread, daemon=True).start()
    
    def _click_buildings_thread(self):
        """Thread for buildings click"""
        try:
            result = self.city_manager.click_buildings_panel()
            if result:
                self.log("✓ Successfully clicked buildings panel")
            else:
                self.log("✗ Failed to click buildings panel")
        except Exception as e:
            self.log(f"✗ Error clicking buildings: {e}")
    
    def click_troops(self):
        """Click troops panel"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._click_troops_thread, daemon=True).start()
    
    def _click_troops_thread(self):
        """Thread for troops click"""
        try:
            result = self.city_manager.click_troops_panel()
            if result:
                self.log("✓ Successfully clicked troops panel")
            else:
                self.log("✗ Failed to click troops panel")
        except Exception as e:
            self.log(f"✗ Error clicking troops: {e}")
    
    def click_march(self):
        """Click march panel"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._click_march_thread, daemon=True).start()
    
    def _click_march_thread(self):
        """Thread for march click"""
        try:
            result = self.city_manager.click_march_panel()
            if result:
                self.log("✓ Successfully clicked march panel")
            else:
                self.log("✗ Failed to click march panel")
        except Exception as e:
            self.log(f"✗ Error clicking march: {e}")
    
    def reset_city(self):
        """Reset city position"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._reset_city_thread, daemon=True).start()
    
    def _reset_city_thread(self):
        """Thread for city reset"""
        try:
            result = self.city_manager.reset_to_city()
            if result:
                self.log("✓ Successfully reset to city center")
            else:
                self.log("✗ Failed to reset to city center")
        except Exception as e:
            self.log(f"✗ Error resetting city: {e}")
    
    def run_periodic_tasks(self):
        """Run all periodic city tasks"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._run_periodic_tasks_thread, daemon=True).start()
    
    def _run_periodic_tasks_thread(self):
        """Thread for periodic tasks"""
        try:
            self.city_manager.run_periodic_tasks()
            self.log("✓ All periodic tasks completed")
        except Exception as e:
            self.log(f"✗ Error in periodic tasks: {e}")
    
    def check_city_status(self):
        """Check if we're in the city"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._check_city_status_thread, daemon=True).start()
    
    def _check_city_status_thread(self):
        """Thread for city status check"""
        try:
            is_in_city = self.city_manager.is_in_city()
            if is_in_city:
                self.log("✓ Currently in city")
            else:
                self.log("✗ Not in city")
        except Exception as e:
            self.log(f"✗ Error checking city status: {e}")
    
    def explore_ruins(self):
        """Start ruin exploration flow"""
        if not self.bot.device:
            self.log("✗ Please connect to a device first")
            return
        threading.Thread(target=self._explore_ruins_thread, daemon=True).start()
    
    def _explore_ruins_thread(self):
        """Thread for ruin exploration"""
        try:
            result = self.city_manager.explore_ruins_flow()
            if result:
                self.log("✓ Ruin exploration completed successfully")
            else:
                self.log("✗ Ruin exploration failed or no marches available")
        except Exception as e:
            self.log(f"✗ Error in ruin exploration: {e}")


class AreaSelectorWindow:
    def __init__(self, parent, screenshot, title="Select UI Element Area"):
        self.parent = parent
        self.screenshot = screenshot
        self.title = title
        self.selected_area = None
        self.start_x = None
        self.start_y = None
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.grab_set()  # Make window modal
        
        # Calculate display size (scale down if too large)
        img_width, img_height = screenshot.size
        max_width, max_height = 1000, 700
        
        if img_width > max_width or img_height > max_height:
            scale = min(max_width / img_width, max_height / img_height)
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            self.scale_factor = scale
            display_image = screenshot.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            display_image = screenshot
            self.scale_factor = 1.0
            display_width, display_height = img_width, img_height
        
        # Create canvas
        self.canvas = tk.Canvas(self.window, width=display_width, height=display_height)
        self.canvas.pack(padx=10, pady=10)
        
        # Display image
        self.photo = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Instructions
        instructions = tk.Label(self.window, 
                               text="Click and drag to select the UI element area. Click 'Confirm' when done.",
                               font=("Arial", 10))
        instructions.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)
        
        self.confirm_btn = tk.Button(button_frame, text="Confirm Selection", 
                                   command=self.confirm_selection, state=tk.DISABLED)
        self.confirm_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=self.cancel_selection).pack(side=tk.LEFT, padx=5)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        
        # Selection rectangle
        self.selection_rect = None
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        # Remove previous selection
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
    
    def update_selection(self, event):
        if self.start_x is not None and self.start_y is not None:
            # Remove previous rectangle
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            
            # Draw new rectangle
            self.selection_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline="red", width=2
            )
    
    def end_selection(self, event):
        if self.start_x is not None and self.start_y is not None:
            # Calculate selection area in original image coordinates
            x1 = min(self.start_x, event.x) / self.scale_factor
            y1 = min(self.start_y, event.y) / self.scale_factor
            x2 = max(self.start_x, event.x) / self.scale_factor
            y2 = max(self.start_y, event.y) / self.scale_factor
            
            # Ensure coordinates are within image bounds
            img_width, img_height = self.screenshot.size
            x1 = max(0, min(x1, img_width))
            y1 = max(0, min(y1, img_height))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))
            
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # Minimum size check
                self.selected_area = (int(x1), int(y1), int(x2), int(y2))
                self.confirm_btn.config(state=tk.NORMAL)
            else:
                self.confirm_btn.config(state=tk.DISABLED)
    
    def confirm_selection(self):
        self.window.destroy()
    
    def cancel_selection(self):
        self.selected_area = None
        self.window.destroy()
    
    def get_selection(self):
        return self.selected_area


def main():
    """Main entry point"""
    print("Starting Minimal Bot GUI...")
    app = MinimalBotGUI()
    app.run()


if __name__ == '__main__':
    main()
