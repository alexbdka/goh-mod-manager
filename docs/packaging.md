# Packaging and Release Flow

## Local development commands

Install dependencies:

```bash
uv sync
```

Run the app:

```bash
uv run python -m src.main
```

Run tests:

```bash
uv run pytest -q
```

Update translations:

```bash
uv run python scripts/build_translations.py
```

## Local build helper

Use the local wrapper in `scripts/build_app.py`:

```bash
uv run python scripts/build_app.py
```

Useful options:

```bash
uv run python scripts/build_app.py --onedir
uv run python scripts/build_app.py --onefile --package
uv run python scripts/build_app.py --skip-tests --skip-translations
```

By default the script:

- rebuilds translations
- runs `compileall`
- runs `pytest`
- builds a PyInstaller package
- includes fonts, icons, `.app-version`, and compiled `.qm` files

## CI build pipeline

The release workflow lives in `.github/workflows/build.yml`.

Current build sequence:

1. install Python 3.12
2. install `uv`
3. `uv sync --frozen`
4. show tool versions
5. run static checks with `python -m compileall -q src tests scripts`
6. run `pytest -q`
7. build with PyInstaller on Windows and Linux
8. package generated binaries as zip artifacts
9. publish GitHub release assets for version tags

## Packaging inputs

The PyInstaller build includes:

- `src/main.py`
- `assets/fonts`
- `assets/icons`
- `.app-version`
- `src/ui/i18n/*.qm`

The app version is read from `.app-version` through `src/utils/app_paths.py`.

## Release outputs

Expected outputs:

- Windows: `dist/goh_mod_manager.exe`
- Linux: `dist/goh_mod_manager`
- packaged zips in `out/`

## Notes for future docs automation

When MkDocs is added later, this page should remain mostly hand-written. It documents process and repository conventions rather than Python API surface.
