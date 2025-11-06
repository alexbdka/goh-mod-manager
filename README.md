# GoH Mod Manager

*A modern mod manager for Call to Arms: Gates of Hell, built with PySide6 and compiled with Nuitka.*

A user-friendly graphical interface for managing mods, presets, configuration sharing, and more.

## Requirements

- Python 3.12
- [uv](https://github.com/astral-sh/uv) (modern Python package manager)

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

To compile the application into a standalone executable:

**Windows**

```bash
nuitka --standalone --onefile --enable-plugin=pyside6 --output-dir=dist --output-filename=goh_mod_manager --nofollow-import-to=tkinter --windows-icon-from-ico=goh_mod_manager/res/icon/logo.ico --windows-console-mode=disable goh_mod_manager/__main__.py
```

**Linux**

```bash
nuitka --standalone --onefile --enable-plugin=pyside6 --output-dir=dist --output-filename=goh_mod_manager --nofollow-import-to=tkinter goh_mod_manager/__main__.py
```

The compiled executable will be available in the `dist` directory.

## Dependencies

- PySide6 - Qt for Python GUI framework
- Nuitka - Python compiler for standalone executables

## Acknowledgments

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager by [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager)
