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

For development tooling and documentation:

```bash
uv sync --group dev --group docs
```

## Usage

Run the application:

```bash
uv run python -m src.main
```

## Development Checks

Common local quality commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest -q
uv run deptry .
uv run --group docs mkdocs build
uv run pre-commit validate-config
```

Install git hooks locally:

```bash
uv run pre-commit install
```

## Documentation

Build the documentation locally:

```bash
uv run --group docs mkdocs build
```

The repository also deploys the MkDocs site automatically to GitHub Pages from
`main`. In the repository settings, set `Settings > Pages > Source` to
`GitHub Actions`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Translations

Qt translation sources live in `src/ui/i18n/*.ts`. Runtime binaries
(`.qm`) are generated from those sources.

- Translators should edit `.ts` files, ideally through Weblate once it is
  connected.
- Developers should validate and compile translations with:

```bash
uv run python scripts/validate_translations.py
uv run python scripts/build_translations.py
```

- The settings UI discovers languages dynamically from the available runtime
  translations, so adding `zh_CN.ts` and compiling `zh_CN.qm` is enough to make
  the language selectable.
- The repository enforces locale file naming such as `fr_FR.ts` or `zh_CN.ts`.

## Releases

Precompiled executables are available for Windows and Linux in the [Releases](https://github.com/alexbdka/goh-mod-manager/releases) section.

## Building

To compile the application into a standalone executable, PyInstaller is the recommended option for public releases (Nuitka builds may trigger AV false positives on Windows).

Note: build tools such as PyInstaller and Nuitka still take a script path as input, so packaging commands continue to target `src/main.py`.

**PyInstaller (Windows)**

```bash
uv run pyinstaller `
            --onedir `
            --clean `
            --windowed `
            --paths "." `
            --name "goh_mod_manager" `
            --icon "assets\icons\logo.ico" `
            --add-data "assets\fonts;assets\fonts" `
            --add-data ".app-version;." `
            --add-data "src\ui\i18n\*.qm;src\ui\i18n" `
            src/main.py
```

**PyInstaller (Linux)**

```bash
uv run pyinstaller \
            --onedir \
            --clean \
            --windowed \
            --paths . \
            --name "goh_mod_manager" \
            --icon "assets/icons/logo.png" \
            --add-data "assets/fonts:assets/fonts" \
            --add-data ".app-version:." \
            --add-data "src/ui/i18n/*.qm:src/ui/i18n" \
            src/main.py
```

The compiled executable will be available in the `dist` directory.

## Dependencies

- PySide6 - Qt for Python GUI framework
- pyqtdarktheme - Modern dark/light themes
- PyInstaller - Standalone executable builder (recommended for releases)

## Credits

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager concept by [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager)
  as an acknowledged predecessor. This repository is an independent
  implementation and does not reuse its code.
