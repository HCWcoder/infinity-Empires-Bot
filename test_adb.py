#!/usr/bin/env python3
"""
ADB Connection Test Script
Simple test to verify ADB connectivity before running the main bot
"""

import sys
import os
import subprocess
import time

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import adb
from utils import resource_path
from filepath.file_relative_paths import FilePaths


def test_adb_executable():
    """Test if ADB executable exists and works"""
    print("=== Testing ADB Executable ===")
    
    adb_path = resource_path(FilePaths.ADB_EXE_PATH.value)
    print(f"ADB path: {adb_path}")
    
    if not os.path.exists(adb_path):
        print(f"✗ ADB executable not found at: {adb_path}")
        return False
    
    try:
        # Test ADB version
        result = subprocess.run([adb_path, 'version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✓ ADB executable working")
            print(f"  Version output: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ ADB executable failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing ADB: {e}")
        return False


def test_adb_devices():
    """Test ADB devices command"""
    print("\n=== Testing ADB Devices ===")
    
    adb_path = resource_path(FilePaths.ADB_EXE_PATH.value)
    
    try:
        # List devices
        result = subprocess.run([adb_path, 'devices'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ ADB devices command successful")
            print("Device list:")
            lines = result.stdout.strip().split('\n')
            devices = []
            
            for line in lines[1:]:  # Skip header
                if line.strip() and '\t' in line:
                    device_id, status = line.strip().split('\t')
                    devices.append((device_id, status))
                    print(f"  {device_id} - {status}")
            
            if not devices:
                print("  No devices found")
                return False, []
            
            return True, devices
        else:
            print(f"✗ ADB devices command failed: {result.stderr}")
            return False, []
            
    except Exception as e:
        print(f"✗ Error running ADB devices: {e}")
        return False, []


def test_adb_bridge():
    """Test the project's ADB bridge"""
    print("\n=== Testing ADB Bridge ===")
    
    try:
        # Initialize ADB bridge
        bridge = adb.enable_adb()
        print("✓ ADB bridge initialized")
        
        # Test client connection
        devices = bridge.get_client_devices()
        print(f"✓ Found {len(devices)} devices via bridge")
        
        for i, device in enumerate(devices):
            print(f"  Device {i+1}: {device.serial}")
        
        if not devices:
            print("  Trying to connect to default device...")
            device = bridge.get_device('127.0.0.1', 5555)
            if device:
                print(f"✓ Connected to default device: {device.serial}")
                return True, device
            else:
                print("✗ No devices available")
                return False, None
        
        return True, devices[0] if devices else None
        
    except Exception as e:
        print(f"✗ ADB bridge error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_device_communication(device):
    """Test basic communication with device"""
    print("\n=== Testing Device Communication ===")
    
    if not device:
        print("✗ No device to test")
        return False
    
    try:
        # Test shell command
        result = device.shell('echo "Hello from device"')
        if 'Hello from device' in result:
            print("✓ Device shell communication working")
            
            # Test additional commands
            print("Testing additional commands:")
            
            # Get Android version
            android_version = device.shell('getprop ro.build.version.release').strip()
            print(f"  Android version: {android_version}")
            
            # Get screen size
            screen_size = device.shell('wm size').strip()
            print(f"  Screen size: {screen_size}")
            
            # Test screenshot capability
            try:
                screenshot_data = device.screencap()
                print(f"  ✓ Screenshot test: {len(screenshot_data)} bytes")
            except Exception as e:
                print(f"  ✗ Screenshot failed: {e}")
            
            return True
        else:
            print(f"✗ Unexpected shell response: {result}")
            return False
            
    except Exception as e:
        print(f"✗ Device communication error: {e}")
        return False


def print_troubleshooting_tips():
    """Print common troubleshooting steps"""
    print("\n=== Troubleshooting Tips ===")
    print("If you're having connection issues:")
    print("")
    print("1. Android Emulator:")
    print("   - Make sure emulator is running")
    print("   - Try: adb connect 127.0.0.1:5555")
    print("   - Common ports: 5554, 5555, 5556")
    print("")
    print("2. Physical Device:")
    print("   - Enable Developer Options")
    print("   - Enable USB Debugging")
    print("   - Allow computer when prompted")
    print("   - Try different USB cable/port")
    print("")
    print("3. ADB Server Issues:")
    print("   - Try: adb kill-server")
    print("   - Then: adb start-server")
    print("   - Check no other ADB processes running")
    print("")
    print("4. Firewall/Antivirus:")
    print("   - Allow ADB through firewall")
    print("   - Temporarily disable antivirus")


def main():
    """Main test function"""
    print("ADB Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test ADB executable
    if not test_adb_executable():
        print("\nCannot proceed - ADB executable not working")
        print_troubleshooting_tips()
        return 1
    
    # Test ADB devices command
    devices_ok, device_list = test_adb_devices()
    if not devices_ok:
        print("\nADB devices command failed")
        print_troubleshooting_tips()
        return 1
    
    # Test ADB bridge
    bridge_ok, device = test_adb_bridge()
    if not bridge_ok:
        print("\nADB bridge initialization failed")
        print_troubleshooting_tips()
        return 1
    
    # Test device communication
    if device:
        comm_ok = test_device_communication(device)
        if comm_ok:
            print("\n🎉 All tests passed! Your device connection is working.")
            print("You can now run the minimal bot.")
        else:
            print("\nDevice communication failed")
            print_troubleshooting_tips()
            return 1
    else:
        print("\nNo device available for communication test")
        print_troubleshooting_tips()
        return 1
    
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
