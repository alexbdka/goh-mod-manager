# GoH Mod Manager

GoH Mod Manager is a PySide6 desktop app for managing mods for
[Call to Arms: Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/).

It is built for the everyday Gates of Hell modding loop: find installed mods,
shape a load order, save presets, share setups with friends, and get back into
the game without hand-editing `options.set`.

## What It Does

- Discovers local and Steam Workshop mods.
- Reads and writes the active load order from the game profile.
- Keeps named presets for different play sessions.
- Imports mods from folders and archives.
- Exports and imports share codes.
- Supports translated UI strings through Qt `.ts` / `.qm` files.

## Quick Start

Requirements:

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

Install dependencies:

```bash
uv sync
```

Run the desktop app:

```bash
uv run python -m src.main
```

Run the CLI status command:

```bash
uv run python -m src.cli.main status
```

## Development

Install development and documentation tools:

```bash
uv sync --group dev --group docs
```

Common checks:

```bash
uv run pre-commit validate-config
uv run python -m compileall -q src tests scripts
uv run python scripts/validate_translations.py
uv run python scripts/build_translations.py --no-update
uv run deptry .
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest -q
```

Install local git hooks:

```bash
uv run pre-commit install
```

## Project Map

- `src/core/`: domain-facing facade, events, config model, constants
- `src/application/`: query surfaces, use cases, immutable state objects
- `src/services/`: persistence, parsing, Steam discovery, imports, share codes
- `src/ui/`: PySide6 windows, widgets, controllers, workers, translations
- `src/cli/`: command-line entry point
- `tests/`: pytest suite and stable fixtures
- `docs/`: hand-written project documentation and static site pages
- `www/`: static GitHub Pages site root; Zensical writes docs to `www/doc/`
- `scripts/`: build, packaging, and translation helpers

The architecture overview lives in [docs/architecture.md](docs/architecture.md).

## Translations

Translations are hosted on Weblate, which makes contributing UI translations
possible without setting up a local development environment:
[GoH Mod Manager - Qt UI on Weblate](https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/).

- Source files: `src/ui/i18n/*.ts`
- Runtime files: `src/ui/i18n/*.qm`
- Validation: `scripts/validate_translations.py`
- Build helper: `scripts/build_translations.py`

For the actual translation workflow, naming rules, and maintainer checklist,
see [src/ui/i18n/README.md](src/ui/i18n/README.md).

## Documentation

Build the docs site:

```bash
uv run --group docs zensical build
```

Serve it locally:

```bash
uv run --group docs zensical serve
```

The public project site is deployed from `main` to GitHub Pages from `www/`,
with the docs generated under `/doc/`.

## Releases

Prebuilt Windows and Linux binaries are published in
[GitHub Releases](https://github.com/alexbdka/goh-mod-manager/releases).

Local release-style builds use:

```bash
uv run python scripts/build_app.py
```

Useful variants:

```bash
uv run python scripts/build_app.py --onedir
uv run python scripts/build_app.py --onefile --package
uv run python scripts/build_app.py --skip-tests
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Acknowledgements

- Logo design by [awasde](https://www.linkedin.com/in/amélie-rakowiecki-970818350)
- Original mod manager concept by
  [Elaindil (MrCookie)](https://github.com/Elaindil/ModManager). This project
  is an independent implementation and does not reuse its code.
