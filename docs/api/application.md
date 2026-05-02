# Application API

The application layer exposes view-neutral state objects plus use cases and query services that translate domain behavior into UI-facing contracts.

## `src.application.state`

::: src.application.state
    options:
      members:
        - SettingsState
        - SettingsUpdateResult
        - ShareCodeExportResult
        - ShareCodeImportResult
        - LoadOrderActivationResult
        - LoadOrderMutationResult
        - ModState
        - CatalogueState
        - ActiveModsState
        - PresetsState

## `src.application.queries.query_service`

::: src.application.queries.query_service
    options:
      members:
        - ApplicationQueryService

## `src.application.use_cases.debug_report`

::: src.application.use_cases.debug_report
    options:
      members:
        - ApplicationDebugReportUseCase

## `src.application.use_cases.load_order`

::: src.application.use_cases.load_order
    options:
      members:
        - ApplicationLoadOrderUseCase

## `src.application.use_cases.settings`

::: src.application.use_cases.settings
    options:
      members:
        - ApplicationSettingsUseCase

## `src.application.use_cases.share_code`

::: src.application.use_cases.share_code
    options:
      members:
        - ApplicationShareCodeUseCase
