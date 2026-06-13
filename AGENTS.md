# Project Guidelines

## Project Structure & Module Organization

This is a Python 3.12 PySide6 desktop app for managing Call to Arms - Gates of Hell mods. Runtime code lives in `src/`: `main.py` launches the GUI, `core/` contains domain objects and orchestration, `services/` handles persistence and file operations, `application/` exposes use cases and query surfaces, `ui/` contains Qt windows, dialogs, widgets, controllers, workers, and translations, and `utils/` holds shared helpers. CLI entry points are in `src/cli/`. Tests live in `tests/`, with fixtures under `tests/resources/`. Static resources are in `assets/`, hand-written docs live in `docs/`, the Zensical config is `zensical.toml`, the GitHub Pages site root is `www/`, and helper scripts are in `scripts/`.

## Build, Test, and Lint Commands

Use `uv` for all local workflows.

```bash
# install dependencies
uv sync --group dev --group docs
uv sync --group dev --group docs --frozen   # match CI lockfile behavior

# run GUI app
uv run python -m src.main

# run CLI entrypoint
uv run python -m src.cli.main status

# quality checks (matches CI)
uv run pre-commit validate-config
uv run python -m compileall -q src tests scripts
uv run python scripts/validate_translations.py
uv run python scripts/build_translations.py --no-update
uv run deptry .
uv run ruff check .
uv run ruff format --check .
uv run basedpyright

# tests
uv run pytest -q
uv run pytest -q tests/test_manager.py
uv run pytest -q tests/test_manager.py::TestModManager::test_import_mod_reloads_on_success_by_default
uv run pytest -q tests/test_cli_main.py::test_status_lines_use_state_surface

# docs build
uv run --group docs zensical build
uv run --group docs zensical serve

# release-style build helper
uv run python scripts/build_app.py
```

## High-Level Architecture

- `src/main.py` (GUI) and `src/cli/main.py` (CLI) both go through `src.core.manager.ModManager` as the application facade.
- `ModManager` composes services (`src/services/*`), read queries (`src/application/queries/query_service.py`), and mutating use cases (`src/application/use_cases/*`), then emits coarse-grained `EventBus` events (`CATALOGUE_CHANGED`, `ACTIVE_MODS_CHANGED`, `PRESETS_CHANGED`) for UI refresh.
- Read flow: services/domain objects → `ApplicationQueryService` → immutable UI-facing dataclasses in `src/application/state.py` (`SettingsState`, `CatalogueState`, `ActiveModsState`, `PresetsState`, etc.).
- Write flow: UI controllers → `ModManager` facade methods → application use cases (`load_order`, `settings`, `share_code`) → services → facade events when change flags indicate state changed. Some blocked UI corrections, such as invalid drag/drop load-order rollback, may also emit `ACTIVE_MODS_CHANGED` to force a view refresh without a persisted state transition.
- The UI (`src/ui/main_window.py`) is thin orchestration: it wires widgets and controllers, injects facade callables into controllers, subscribes to facade events, and repopulates widgets from query-state snapshots.
- Domain parsing/serialization lives in services and utils:
  - `ModsCatalogueService` parses `mod.info` files into `ModInfo`
  - `ActiveModsService` loads/saves `options.set` and preserves block structure when writing
  - `src/utils/gem_parser.py` handles GEM format parsing
- Active mod dependency safety is enforced in the application/service layer: dependencies are activated before dependents, active dependencies cannot be removed while required by another active mod, and load-order mutations must keep dependencies before their dependents. UI widgets may highlight these relationships, but they must not be the only enforcement point.
- The public static site is under `www/`; Zensical writes generated docs to `www/doc/`, which is ignored by Git and rebuilt in CI before Pages uploads `www/`.
- Runtime/resource paths differ for dev vs frozen builds; always resolve through `src/utils/app_paths.py`.

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation, descriptive snake_case functions and modules, PascalCase classes, and UPPER_CASE constants. Keep UI code in `src/ui/`, business logic out of widgets, and filesystem or Steam-specific behavior in services or utilities. Prefer type-friendly, explicit data surfaces over loosely shaped dictionaries. Do not commit generated caches, logs, local config, build output, or virtual environments.

## Key Development Conventions

- Keep business logic out of Qt widgets: UI controllers should depend on injected callables/use cases, not reach directly into low-level services.
- Use explicit mutation result objects (`LoadOrderMutationResult`, `LoadOrderActivationResult`, `SettingsUpdateResult`, `ShareCodeImportResult`) and rely on their `changed`/delta fields to drive UI behavior.
- Emit facade events for real state transitions (`if result.changed: emit(...)` pattern in `ModManager`). If a blocked mutation leaves a widget temporarily out of sync, prefer an explicit refresh event over mutating state just to satisfy the UI.
- Configuration is machine-local JSON managed through `ConfigService`; do not hardcode user-specific paths.
- For writes affecting config/profile data, use existing atomic paths (`atomic_write_text`) rather than direct writes.
- Translation files in `src/ui/i18n` must follow Qt/Weblate locale naming (`en.ts`, `en_US.ts`, `fr.ts`, `zh_Hans.ts`, etc.) and valid `<TS language="...">` metadata; run `scripts/validate_translations.py` before/with translation updates.
- Mod names can contain GEM/engine markup from modders; use `src/utils/markup_parser.py` before showing names in plain-text UI surfaces such as toasts, logs intended for users, or status messages.

## Testing Guidelines

Tests use `pytest`. Name files `test_*.py` and test functions `test_*`. Add focused unit tests near the behavior being changed, especially for services, use cases, parsers, CLI output, and path handling. Use `tests/resources/` for stable sample files such as `mod.info` and `options.set`. Run `uv run pytest -q` before opening a pull request.

## Commit & Pull Request Guidelines

Recent history uses short, imperative subjects with conventional prefixes such as `feat:`, `refactor:`, and `change`. Keep commits scoped to one logical change. Pull requests should describe the user-visible behavior, list tests run, link related issues, and include screenshots or short clips for UI changes. Mention translation updates when `.ts` or `.qm` files change.

## Security & Configuration Tips

Treat `config.json`, `logs/`, build artifacts, and local game/profile paths as machine-local data. Avoid hard-coding personal paths; use helpers in `src/utils/app_paths.py` and existing configuration services.
