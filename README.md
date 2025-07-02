# Call to Arms: Gates of Hell | Mod Manager

A Python application built with PySide6 and compiled with Nuitka.  
A mod manager with a pleasant, intuitive graphical interface featuring mod management, preset management, configuration
sharing and much more.

## Requirements

- Python 3.12
- uv (Python package manager)

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
If you're using macOS and would like a native executable, feel free to contact me — I’d be happy to collaborate or
help with the compilation process.

## Building

To compile the application into a standalone executable:

```bash
nuitka --standalone --onefile --enable-plugin=pyside6 --windows-icon-from-ico=goh_mod_manager/assets/icons/logo.ico --output-dir=dist --nofollow-import-to=tkinter --windows-console-mode=disable goh_mod_manager/__main__.py
```

The compiled executable will be available in the `dist` directory.

## Dependencies

- PySide6 - Qt for Python GUI framework
- Nuitka - Python compiler for standalone executables

## Acknowledgments

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- The very first mod manager created by [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager)
