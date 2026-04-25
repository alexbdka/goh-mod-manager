# Core API

The core layer defines the facade, shared models, constants, exceptions, and event contracts used by the rest of the application.

## `src.core.config`

::: src.core.config
    options:
      members:
        - AppConfig

## `src.core.constants`

::: src.core.constants
    options:
      members:
        - STEAM_APP_ID
        - MOD_INFO_FILE
        - OPTIONS_SET_FILE
        - MOD_PREFIX
        - MODS_DIR

## `src.core.events`

::: src.core.events
    options:
      members:
        - EventType
        - EventBus

## `src.core.exceptions`

::: src.core.exceptions
    options:
      members:
        - ModManagerError
        - ModImportError
        - ModInfoNotFoundError
        - InvalidModPathError
        - ModAlreadyExistsError
        - ArchiveExtractionError
        - ShareCodeError
        - InvalidShareCodeError
        - ProfileWriteError
        - ConfigError
        - ConfigLoadError
        - ConfigWriteError
        - PresetError
        - PresetNotFoundError

## `src.core.manager`

::: src.core.manager
    options:
      members:
        - ModManager

## `src.core.mod`

::: src.core.mod
    options:
      members:
        - ModInfo
