#!/usr/bin/env python3
"""
Test Runner for Minimal Bot
Simple script to test basic functionality without GUI
"""

import sys
import os
import time
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from minimal_bot import MinimalBot


def load_config():
    """Load configuration from minimal_config.json"""
    try:
        with open('minimal_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found, using defaults")
        return {
            "game_settings": {
                "package_name": "com.ifun.google.kingdom",
                "detection_threshold": 0.8
            },
            "detection_images": {
                "home_button": "resource\\home_button.png"
            }
        }


def test_device_connection():
    """Test basic device connection"""
    print("=== Testing Device Connection ===")
    
    bot = MinimalBot()
    success, message = bot.connect_device(host="127.0.0.1", port=5555)
    
    if success:
        print(f"✓ Device connected: {message}")
        return bot
    else:
        print(f"✗ Connection failed: {message}")
        print("Troubleshooting tips:")
        print("  1. Make sure Android emulator is running")
        print("  2. Check 'adb devices' command works")
        print("  3. Enable USB Debugging on device")
        print("  4. Try different port (5554, 5556, etc.)")
        return None


def test_game_detection(bot, config):
    """Test game detection and launch"""
    print("\n=== Testing Game Detection ===")
    
    package_name = config["game_settings"]["package_name"]
    
    # Check if game is running
    is_running = bot.is_game_running(package_name)
    print(f"Game running status: {is_running}")
    
    if not is_running:
        print(f"Attempting to launch {package_name}...")
        success, message = bot.launch_game(package_name)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            return False
    
    return True


def test_screenshot(bot):
    """Test screenshot functionality"""
    print("\n=== Testing Screenshot ===")
    
    screenshot = bot.take_screenshot()
    if screenshot:
        filename = f"test_screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        print(f"✓ Screenshot saved as {filename}")
        print(f"  Screenshot size: {screenshot.size}")
        return True
    else:
        print("✗ Failed to take screenshot")
        return False


def test_ui_detection(bot, config):
    """Test UI element detection"""
    print("\n=== Testing UI Detection ===")
    
    detection_images = config.get("detection_images", {})
    threshold = config["game_settings"].get("detection_threshold", 0.8)
    
    for name, image_path in detection_images.items():
        print(f"Testing detection of {name} ({image_path})...")
        
        found, result = bot.detect_ui_element(image_path, threshold)
        
        if found:
            if isinstance(result, tuple):
                x, y = result
                print(f"  ✓ Found at position ({x}, {y})")
            else:
                print(f"  ✓ Detected successfully")
        else:
            print(f"  ✗ Not found")
            if isinstance(result, str):
                print(f"    Error: {result}")


def run_basic_loop(bot, config, duration=60):
    """Run a basic automation loop for testing"""
    print(f"\n=== Running Basic Loop for {duration} seconds ===")
    
    package_name = config["game_settings"]["package_name"]
    start_time = time.time()
    loop_count = 0
    
    while time.time() - start_time < duration:
        loop_count += 1
        print(f"\nLoop {loop_count}:")
        
        # Check game status
        if not bot.is_game_running(package_name):
            print("  Game not running, attempting to launch...")
            bot.launch_game(package_name)
        else:
            print("  ✓ Game is running")
        
        # Test one detection
        detection_images = config.get("detection_images", {})
        if detection_images:
            first_image = list(detection_images.values())[0]
            found, result = bot.detect_ui_element(first_image)
            if found:
                print(f"  ✓ UI element detected")
            else:
                print(f"  - UI element not visible")
        
        # Wait before next loop
        print("  Waiting 10 seconds...")
        time.sleep(10)
    
    print(f"\nCompleted {loop_count} loops")


def main():
    """Main test function"""
    print("Minimal Bot Test Runner")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    print(f"Loaded config for package: {config['game_settings']['package_name']}")
    
    # Test device connection
    bot = test_device_connection()
    if not bot:
        print("Cannot proceed without device connection")
        return 1
    
    # Test screenshot
    if not test_screenshot(bot):
        print("Screenshot test failed - check device connection")
        return 1
    
    # Test game detection
    if not test_game_detection(bot, config):
        print("Game detection failed - check package name")
    
    # Test UI detection
    test_ui_detection(bot, config)
    
    # Ask user if they want to run the basic loop
    user_input = input("\nRun basic automation loop for 60 seconds? (y/n): ").lower()
    if user_input == 'y':
        run_basic_loop(bot, config, 60)
    
    print("\nTest completed!")
    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
