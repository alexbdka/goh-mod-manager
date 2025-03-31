# CtA - GoH Mod Manager

A simple and user-friendly mod manager for Gates of Hell, allowing you to easily activate, deactivate, and reorder mods without manually editing configuration files.

![Gates of Hell Mod Manager Screenshot](/resources/logo.png)

## Features

- Easy activation and deactivation of mods with a simple double-click or buttons
- Drag and drop reordering of active mods to control load order
- Save and load mod configurations as presets
- No need to manually edit the options.set file
- Clean and intuitive interface

## Installation

### Option 1: Download the executable

1. Download the latest release from the [Releases](https://github.com/alexbdka/goh-mod-manager/releases) page
2. Extract the ZIP file to a location of your choice
3. Run the `Gates of Hell Mod Manager.exe` file

### Option 2: Run from source

1. Ensure you have Python 3.6+ installed
2. Clone this repository
3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## Usage Guide

### First Launch

When you first start the application, you'll be prompted to select:

1. Your **Mods Folder** - This is typically located at:

   ```bash
   C:\Program Files (x86)\Steam\steamapps\workshop\content\400750
   ```

   (Or wherever your Steam workshop content is stored)

2. Your **options.set file** - This is typically located at:

   ```bash
   C:\Users\[YourUsername]\Documents\My Games\gates of hell\profiles\[YourProfileID]\options.set
   ```

   (For some users, It could be _C:\Users\[YourUsername]\AppData_)

These paths will be saved for future use. You can change them later using the "Change Paths" button.

### Managing Mods

- **Left panel**: Shows all installed but inactive mods
- **Right panel**: Shows all currently active mods

#### Activating Mods

- Double-click a mod in the left panel to activate it
- Or select a mod and click the "Activate →" button

#### Deactivating Mods

- Double-click a mod in the right panel to deactivate it
- Or select a mod and click the "← Deactivate" button

#### Changing Mod Order

Mod order determines the load priority (mods loaded later can override earlier ones):

- Select a mod in the right panel and use the "Move Up ↑" and "Move Down ↓" buttons
- Or drag and drop mods to reorder them

#### Saving Changes

- Click "Apply Changes" to save your current mod configuration to the game
- This updates your options.set file with the current active mods in the order shown

### Using Presets

Presets allow you to save and quickly switch between different mod configurations.

#### Saving a Preset

1. Set up your desired mod configuration in the right panel
2. Click "Save Current" in the Presets section
3. Enter a name for your preset

#### Loading a Preset

1. Select a preset from the dropdown menu
2. Click "Load"
3. The preset will be applied to your active mods list
4. Click "Apply Changes" to save to your game configuration

#### Deleting a Preset

1. Select a preset from the dropdown menu
2. Click "Delete"
3. Confirm the deletion

## Troubleshooting

### The game doesn't recognize my mods

- Make sure you've clicked "Apply Changes" after making modifications
- Try restarting the game

### I can't find my options.set file

- Launch the game at least once to create the file
- Check if you have multiple profiles and select the correct one

### Error loading mod configurations

- Ensure your paths are correctly set
- Verify that the options.set file isn't set to read-only

## Building from Source

To build the executable yourself:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Gates of Hell Mod Manager" main.py
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
