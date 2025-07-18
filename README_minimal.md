# Minimal Bot - Quick Start Guide

This is a simplified version of the game automation bot designed for easy testing and adaptation to new games.

## Files Created

1. **`minimal_bot.py`** - Main bot script with GUI
2. **`test_minimal.py`** - Command-line test runner
3. **`minimal_config.json`** - Configuration file
4. **`README_minimal.md`** - This guide

## Quick Setup

### 1. Prerequisites
Make sure you have all the original project dependencies installed:
```bash
pip install opencv-python pytesseract numpy pillow pure-python-adb requests
```

### 2. Device Setup
- Set up Android emulator or connect Android device
- Enable USB Debugging (Developer Options)
- Set emulator resolution to **1280x720** or **720x1280**
- Make sure ADB is working: `adb devices`

### 3. Running the Tests

#### Option A: GUI Version
```bash
python minimal_bot.py
```

#### Option B: Command Line Test
```bash
python test_minimal.py
```

## What the Minimal Bot Does

### Core Features:
1. **Device Connection** - Connects to Android device via ADB
2. **Game Launch** - Starts target game application
3. **Screenshot** - Takes device screenshots
4. **UI Detection** - Basic template matching for UI elements
5. **Simple Loop** - Basic automation cycle

### Test Sequence:
1. Connect to device
2. Check if game is running
3. Launch game if needed
4. Take screenshot
5. Test UI element detection
6. Run basic automation loop

## Adapting to Your Game

### Step 1: Update Package Name
Edit `minimal_config.json`:
```json
{
    "game_settings": {
        "package_name": "your.game.package.name"
    }
}
```

To find your game's package name:
```bash
# Install your game, then run:
adb shell pm list packages | grep -i gamename
```

### Step 2: Add UI Elements
1. Take screenshots of your game's UI
2. Crop important buttons/elements 
3. Save them in the `resource/` folder
4. Update `minimal_config.json`:

```json
{
    "detection_images": {
        "home_button": "resource\\your_home_button.png",
        "menu_button": "resource\\your_menu_button.png"
    }
}
```

### Step 3: Test Detection
Run the test script to verify UI detection works:
```bash
python test_minimal.py
```

### Step 4: Customize Logic
Modify the `basic_loop()` function in `minimal_bot.py` to add your game-specific actions.

## Troubleshooting

### Common Issues:

**Device not found:**
- Check `adb devices` command
- Enable USB Debugging
- Try different USB ports/cables

**Game won't launch:**
- Verify package name is correct
- Check if game requires specific launcher activity
- Some games may have different activity names

**UI detection not working:**
- Screenshots must be exact matches
- Adjust `detection_threshold` in config (lower = more lenient)
- Ensure emulator resolution matches reference images
- Game language should match reference images

**Template matching fails:**
- Take new screenshots at same resolution
- Crop images tightly around UI elements
- Use PNG format for best results
- Avoid images with dynamic content (timers, etc.)

## Next Steps

Once the minimal bot works with your game:

1. **Expand Detection** - Add more UI elements
2. **Add Actions** - Implement tap sequences for common tasks
3. **Error Handling** - Add robustness for unexpected states
4. **Game Logic** - Implement specific game mechanics
5. **Configuration** - Add more customizable options

## Configuration Options

### Game Settings:
- `package_name` - Target game package
- `activity_name` - Launch activity (optional)
- `launch_timeout` - Seconds to wait for game launch
- `detection_threshold` - Image matching sensitivity (0.0-1.0)

### Bot Settings:
- `loop_delay` - Seconds between automation cycles
- `screenshot_on_error` - Save screenshots when errors occur
- `debug_mode` - Enable detailed logging

## Tips for Success

1. **Start Simple** - Test basic connection and screenshots first
2. **Use Emulator** - More reliable than physical device
3. **Consistent Screenshots** - Take reference images under same conditions
4. **Test Frequently** - Verify each change works before adding complexity
5. **Document Changes** - Keep notes of what works for your specific game

## Example Workflow

```bash
# 1. Test device connection
python test_minimal.py

# 2. Update config with your game package
# Edit minimal_config.json

# 3. Test game launch
python test_minimal.py

# 4. Take screenshots of your game UI
# Use the GUI screenshot feature

# 5. Add new detection images
# Update minimal_config.json

# 6. Test detection
python test_minimal.py

# 7. Customize automation logic
# Edit minimal_bot.py basic_loop function
```

Good luck adapting the bot to your game!
