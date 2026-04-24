# UI Flow

## Window composition

`src/ui/main_window.py` builds the main screen around three core areas:

- `CatalogueWidget`: available mods
- `ActiveModsWidget`: current load order
- `ModDetailsWidget`: details for the selected mod

The main menu, toolbar, onboarding overlay, and status bar sit around those panels.

## Startup flow

1. `src/main.py` creates `ModManager`
2. `ModManager.initialize()` loads config and attempts Steam/profile auto-detection
3. `MainWindow` is created and populated through query-state snapshots
4. if required paths are missing, settings are opened
5. if onboarding has not been seen, `OnboardingOverlay` is shown

## Selection behavior

`SelectionController` keeps the two lists mutually exclusive:

- selecting a catalogue item clears active selection
- selecting an active mod clears catalogue selection
- the details panel always reflects the current selection
- context menus operate on the item under the cursor

## Load-order behavior

`LoadOrderController` handles:

- add selected mods from catalogue
- remove selected active mod
- move up / move down
- clear load order
- drag-and-drop reorder

The controller only manages Qt flow and user feedback. Actual mutations happen through `ModManager` and the load-order use case.

## Preset behavior

`PresetController` handles:

- apply preset
- save current preset
- save as new preset
- delete preset

Preset state is derived by `ApplicationQueryService`. The UI can preserve the selected preset even when the active load order has drifted from it, which is how the "unsaved changes" state is computed.

## Share code flow

Export:

1. UI requests export
2. `ModManager.build_share_code_export()`
3. active mods are encoded
4. result is copied to the clipboard

Import:

1. user pastes a code in `ImportShareCodeDialog`
2. `ModManager.apply_share_code()` resolves known and missing mods
3. active load order is replaced
4. profile is persisted
5. UI shows missing Workshop subscriptions if needed

## Import flow

`ModImportController` starts a background worker so archive extraction and copying do not block the UI thread.

The worker reports:

- progress text and percentage
- overwrite conflicts
- final success or failure

On success, the main window reloads catalogue and active profile state.

## Error handling

The UI has a few important error paths:

- `ProfileWriteError`: profile file is locked or missing
- `ConfigWriteError`: settings/presets/onboarding state could not be saved
- `InvalidShareCodeError`: malformed import code
- import exceptions surfaced by `ModImportService`

Controllers should catch domain/application exceptions and translate them into Qt dialogs or status messages.
