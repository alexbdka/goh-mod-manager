# Repository Guidelines

## Project Structure & Module Organization

This is a Python 3.12 PySide6 desktop app for managing Call to Arms - Gates of Hell mods. Runtime code lives in `src/`: `main.py` launches the GUI, `core/` contains domain objects and orchestration, `services/` handles persistence and file operations, `application/` exposes use cases and query surfaces, `ui/` contains Qt windows, dialogs, widgets, controllers, workers, and translations, and `utils/` holds shared helpers. CLI entry points are in `src/cli/`. Tests live in `tests/`, with fixtures under `tests/resources/`. Static resources are in `assets/`, docs in `docs/`, and helper scripts in `scripts/`.

## Build, Test, and Development Commands

- `uv sync` installs locked runtime and development dependencies.
- `uv run python -m src.main` starts the GUI locally.
- `uv run pytest -q` runs the test suite used by CI.
- `uv run python scripts/build_translations.py` updates `.ts` files and compiles `.qm` translations for `en_US`, `fr_FR`, and `ru_RU`.
- `uv run pyinstaller ... src/main.py` builds release binaries; follow the platform-specific examples in `README.md`.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation, descriptive snake_case functions and modules, PascalCase classes, and UPPER_CASE constants. Keep UI code in `src/ui/`, business logic out of widgets, and filesystem or Steam-specific behavior in services or utilities. Prefer type-friendly, explicit data surfaces over loosely shaped dictionaries. Do not commit generated caches, logs, local config, build output, or virtual environments.

## Testing Guidelines

Tests use `pytest`. Name files `test_*.py` and test functions `test_*`. Add focused unit tests near the behavior being changed, especially for services, use cases, parsers, CLI output, and path handling. Use `tests/resources/` for stable sample files such as `mod.info` and `options.set`. Run `uv run pytest -q` before opening a pull request.

## Commit & Pull Request Guidelines

Recent history uses short, imperative subjects with conventional prefixes such as `feat:`, `refactor:`, and `change`. Keep commits scoped to one logical change. Pull requests should describe the user-visible behavior, list tests run, link related issues, and include screenshots or short clips for UI changes. Mention translation updates when `.ts` or `.qm` files change.

## Security & Configuration Tips

Treat `config.json`, `logs/`, build artifacts, and local game/profile paths as machine-local data. Avoid hard-coding personal paths; use helpers in `src/utils/app_paths.py` and existing configuration services.
