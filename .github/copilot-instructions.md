# Copilot Instructions for GoH Mod Manager

## Build, test, and lint commands

Use `uv` for all local workflows.

```bash
# install dependencies
uv sync --group dev --group docs

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

# docs build
uv run --group docs mkdocs build

# release-style build helper
uv run python scripts/build_app.py
```

## High-level architecture

- `src/main.py` (GUI) and `src/cli/main.py` (CLI) both go through `src.core.manager.ModManager` as the application facade.
- `ModManager` composes services (`src/services/*`), read queries (`src/application/queries/query_service.py`), and mutating use cases (`src/application/use_cases/*`), and exposes coarse-grained events via `EventBus` (`CATALOGUE_CHANGED`, `ACTIVE_MODS_CHANGED`, `PRESETS_CHANGED`).
- The UI (`src/ui/main_window.py`) is intentionally thin orchestration: Qt widgets + controllers in `src/ui/controllers/*` call facade methods, then refresh from facade query state when events fire.
- Read models are view-neutral immutable dataclasses in `src/application/state.py`; UI should consume these instead of raw service/domain objects.
- Domain parsing/serialization lives in services and utils:
  - `ModsCatalogueService` parses `mod.info` files into `ModInfo`
  - `ActiveModsService` loads/saves `options.set` and preserves block structure when writing
  - `src/utils/gem_parser.py` handles GEM format parsing
- Runtime/resource paths differ for dev vs frozen builds; always resolve through `src/utils/app_paths.py`.

## Key conventions for this repository

- Keep business logic out of Qt widgets: UI controllers should depend on injected callables/use cases, not reach directly into low-level services.
- For mutating operations, return explicit result objects (for example `LoadOrderMutationResult`, `SettingsUpdateResult`) with `changed`/delta fields; emit facade events only when state actually changed.
- Configuration is machine-local JSON managed through `ConfigService`; do not hardcode user-specific paths.
- For file writes affecting config/profile data, use existing atomic write paths (`atomic_write_text`) instead of ad-hoc writes.
- Translation files in `src/ui/i18n` must follow locale naming (`en_US.ts`, `fr.ts`, `zh_Hans.ts` etc.); run `scripts/validate_translations.py` before/with translation updates. Runtime language availability is driven by compiled `.qm` files discovered at runtime.
