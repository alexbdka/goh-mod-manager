# GoH Mod Manager

*A modern mod manager for [Call to Arms: Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/), built with PySide6.*

A user-friendly graphical interface for managing mods, presets, configuration sharing, and more.

## Requirements

- Python **3.12+**
- uv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/alexbdka/goh-mod-manager.git
cd goh-mod-manager
```

2. Install dependencies using uv:

```bash
uv sync
```

## Usage

Run the application:

```bash
uv run python main.py
```

## Releases

Precompiled executables are available for Windows and Linux in the [Releases](https://github.com/alexbdka/goh-mod-manager/releases) section.

## Building

To compile the application into a standalone executable, PyInstaller is the recommended option for public releases (Nuitka builds may trigger AV false positives on Windows).

**PyInstaller (Windows)**

```bash
uv run pyinstaller `
            --onedir `
            --clean `
            --windowed `
            --name "goh_mod_manager" `
            --icon "assets\icons\logo.ico" `
            --add-data "assets\fonts;assets\fonts" `
            --add-data "src\ui\i18n\*.qm;src\ui\i18n" `
            main.py
```

**PyInstaller (Linux)**

```bash
uv run pyinstaller \
            --onedir \
            --clean \
            --windowed \
            --name "goh_mod_manager" \
            --icon "assets/icons/logo.png" \
            --add-data "assets/fonts:assets/fonts" \
            --add-data "src/ui/i18n/*.qm:src/ui/i18n" \
            main.py
```

The compiled executable will be available in the `dist` directory.

**Nuitka (optional)**

Nuitka can produce smaller binaries, but tends to trigger antivirus false positives for public Windows releases. Use at your own discretion.

**Windows**

```bash
uv run nuitka `
            --standalone `
            --enable-plugin=pyside6 `
            --output-dir=dist `
            --output-filename=goh_mod_manager `
            --nofollow-import-to=tkinter `
            --windows-icon-from-ico=assets/icons/logo.ico `
            --windows-console-mode=disable `
            --include-data-dir=assets/fonts=assets/fonts `
            --include-data-dir=src/ui/i18n=src/ui/i18n `
            main.py
```

**Linux**

```bash
uv run nuitka \
            --standalone \
            --enable-plugin=pyside6 \
            --output-dir=dist \
            --output-filename=goh_mod_manager \
            --nofollow-import-to=tkinter \
            --include-data-dir=assets/fonts=assets/fonts \
            --include-data-dir=src/ui/i18n=src/ui/i18n \
            main.py
```

## Dependencies

- PySide6 - Qt for Python GUI framework
- pyqtdarktheme - Modern dark/light themes
- PyInstaller - Standalone executable builder (recommended for releases)

## Credits

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager by [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager)
