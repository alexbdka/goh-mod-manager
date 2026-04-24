# GoH Mod Manager

GoH Mod Manager is a PySide6 desktop application for managing mods for
[Call to Arms: Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/).
It focuses on local and Workshop mod discovery, load order management, presets,
share codes, and a polished desktop workflow.

## Requirements

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/alexbdka/goh-mod-manager.git
cd goh-mod-manager
uv sync
```

For development, quality tooling, and documentation:

```bash
uv sync --group dev --group docs
```

## Usage

Run the application locally with:

```bash
uv run python -m src.main
```

## Development Guidelines

Common local checks:

```bash
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev basedpyright
uv run --group dev deptry .
uv run --group dev pytest -q
uv run pre-commit validate-config
```

Install git hooks locally:

```bash
uv run pre-commit install
```

The repository uses:
- `ruff` for linting and formatting
- `basedpyright` for type checking
- `pytest` for tests
- `deptry` for dependency validation

## Documentation

Build the documentation locally:

```bash
uv run --group docs mkdocs build
```

Serve it during development:

```bash
uv run --group docs mkdocs serve
```

The documentation site is deployed automatically to GitHub Pages from `main`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Translations

UI translations are managed through **Weblate** and stored in
`src/ui/i18n/*.ts`. Runtime `.qm` files are generated from those source files.

- Translation source files follow Qt/Weblate locale naming such as
  `en_US.ts`, `fr.ts`, or `zh_Hans.ts`
- Runtime language availability is discovered dynamically by the app
- Translation metadata and filenames are validated in CI

Useful commands:

```bash
uv run python scripts/validate_translations.py
uv run python scripts/build_translations.py
```

Additional translation workflow details are documented in
[src/ui/i18n/README.md](src/ui/i18n/README.md) and [docs/translations.md](docs/translations.md).

## Releases

Prebuilt Windows and Linux binaries are published in
[GitHub Releases](https://github.com/alexbdka/goh-mod-manager/releases).

## Builds

Use the local build helper:

```bash
uv run python scripts/build_app.py
```

Useful variants:

```bash
uv run python scripts/build_app.py --onedir
uv run python scripts/build_app.py --onefile --package
uv run python scripts/build_app.py --skip-tests
```

The script rebuilds translations, runs compile checks, optionally runs tests,
and packages the application with PyInstaller using the same conventions as CI.

## Dependencies

Main runtime dependencies:

- `PySide6` for the desktop UI
- `pyqtdarktheme` for light and dark themes
- `qtawesome` for icon integration
- `py7zr`, `rarfile`, and `vdf` for archive and Steam-related workflows

## Acknowledgements

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager concept by
  [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager) as an
  acknowledged predecessor; this repository is an independent implementation
  and does not reuse its code
