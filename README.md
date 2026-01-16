# GoH Mod Manager

*A modern mod manager for [Call to Arms: Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/), built with PySide6.*

A user-friendly graphical interface for managing mods, presets, configuration sharing, and more.

## Requirements

- Python **3.12**
- uv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/alexbdka/goh-mod-manager.git
cd goh-mod-manager
```

1. Install dependencies using uv:

```bash
uv sync
```

## Usage

Run the application:

```bash
uv run -m goh_mod_manager
```

## Releases

Precompiled executables are available for Windows and Linux in
the [Releases](https://github.com/alexbdka/goh-mod-manager/releases) section.

## Building

To compile the application into a standalone executable, PyInstaller is the
recommended option for public releases (Nuitka builds may trigger AV false
positives on Windows).

If you have translations, compile them before packaging:

```bash
# Windows
scripts\qt\compile_translations.ps1

# Linux
for f in goh_mod_manager/i18n/*.ts; do uv run pyside6-lrelease "$f"; done
```

**PyInstaller (Windows)**

```bash
uv run pyinstaller ^
            --onefile ^
            --clean ^
            --windowed ^
            --name "goh_mod_manager" ^
            --icon "goh_mod_manager\res\icon\logo.ico" ^
            goh_mod_manager\__main__.py
```

**PyInstaller (Linux)**

```bash
uv run pyinstaller \
            --onefile \
            --clean \
            --windowed \
            --name "goh_mod_manager" \
            --icon "goh_mod_manager/res/icon/logo.png" \
            goh_mod_manager/__main__.py
```

The compiled executable will be available in the `dist` directory.

**Nuitka (optional)**

Nuitka can produce smaller binaries, but tends to trigger antivirus false
positives for public Windows releases. Use at your own discretion.

```bash
# Windows
uv run nuitka ^
            --standalone ^
            --onefile ^
            --enable-plugin=pyside6 ^
            --output-dir=dist ^
            --output-filename=goh_mod_manager ^
            --nofollow-import-to=tkinter ^
            --windows-icon-from-ico=goh_mod_manager/res/icon/logo.ico ^
            --windows-console-mode=disable ^
            goh_mod_manager/__main__.py

# Linux
uv run nuitka \
            --standalone \
            --onefile \
            --enable-plugin=pyside6 \
            --output-dir=dist \
            --output-filename=goh_mod_manager \
            --nofollow-import-to=tkinter \
            goh_mod_manager/__main__.py
```

## Dependencies

- PySide6 - Qt for Python GUI framework
- PyInstaller - Standalone executable builder (recommended for releases)

## Credits

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager by [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager)
