# Architecture Overview

## Runtime entry point

The desktop app starts in `src/main.py`:

1. configure logging
2. create `QApplication`
3. load appearance and translations from config
4. create `ModManager`
5. initialize catalogue/profile state
6. create `MainWindow`

`src/core/manager.py` is the top-level facade used by the UI. It owns the core services, exposes application use cases, and emits coarse-grained events when state changes.

## Main layers

### `src/core/`

Core defines stable domain-facing concepts:

- `config.py`: persistent app config model
- `constants.py`: application constants and Steam IDs
- `events.py`: small event bus used by the facade
- `exceptions.py`: domain/application exceptions
- `manager.py`: facade used by UI and CLI
- `mod.py`: mod model objects

### `src/services/`

Services handle persistence, parsing, file access, and external system interactions:

- `config_service.py`: JSON config I/O
- `mods_catalogue_service.py`: scans local and Workshop mods
- `active_mods_service.py`: reads/writes `options.set`
- `preset_service.py`: stores named load orders in config
- `share_code_service.py`: import/export encoding
- `mod_import_service.py`: imports directories and archives safely

These modules should stay UI-agnostic.

### `src/application/`

The application layer converts service/domain behavior into UI-friendly contracts:

- `state.py`: immutable read/result models
- `queries/query_service.py`: read-only state builders
- `use_cases/*.py`: write-side workflows for settings, load order, share code, and debug reporting

This is the best layer to document behavior for future generated API docs.

### `src/ui/`

Qt-specific presentation code:

- `main_window.py`: composition root for the desktop UI
- `controllers/`: action orchestration and dialog flow
- `widgets/`: reusable UI sections
- `dialogs/`: modal flows
- `workers/`: background work wrappers
- `onboarding_overlay.py`: guided first-run tour

`MainWindow` should coordinate widgets and controllers, not contain business rules.

## Data flow

Read flow:

1. UI asks `ModManager`
2. `ModManager` delegates to `ApplicationQueryService`
3. query service builds `state.py` objects from services
4. widgets render those state objects

Write flow:

1. UI event is handled by a controller
2. controller calls a `ModManager` command
3. facade delegates to an application use case
4. use case updates services and persistence
5. facade emits an event
6. `MainWindow` refreshes the affected widgets

## Design constraints

- Keep business logic out of widgets and dialogs.
- Prefer adding behavior in `src/application/` instead of growing `ModManager`.
- Treat config, logs, and detected paths as machine-local state.
- Keep Qt dependencies out of `src/services/` and `src/application/`.

## Documentation notes

For future MkDocs integration, the best auto-documented targets are:

- `src/core/manager.py`
- `src/application/state.py`
- `src/application/queries/query_service.py`
- `src/application/use_cases/*.py`
- `src/services/*.py`
