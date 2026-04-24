from dataclasses import dataclass, field


@dataclass(frozen=True)
class SettingsState:
    game_path: str | None
    workshop_path: str | None
    profile_path: str | None
    language: str
    theme: str
    font: str


@dataclass(frozen=True)
class SettingsUpdateResult:
    path_changed: bool = False
    language_changed: bool = False
    appearance_changed: bool = False


@dataclass(frozen=True)
class ShareCodeExportResult:
    has_active_mods: bool = False
    code: str = ""


@dataclass(frozen=True)
class ShareCodeImportResult:
    success: bool = False
    missing_mods: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class LoadOrderActivationResult:
    changed: bool = False
    activated_mod_ids: list[str] = field(default_factory=list)
    missing_dependencies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LoadOrderMutationResult:
    changed: bool = False
    active_mod_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ModState:
    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    min_game_version: str | None = None
    max_game_version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    missing_dependencies: list[str] = field(default_factory=list)
    is_local: bool = False
    has_shaders: bool = False
    path: str = ""
    image_path: str | None = None
    is_active: bool = False
    load_order: int | None = None


@dataclass(frozen=True)
class CatalogueState:
    items: list[ModState] = field(default_factory=list)


@dataclass(frozen=True)
class ActiveModsState:
    items: list[ModState] = field(default_factory=list)


@dataclass(frozen=True)
class PresetsState:
    preset_names: list[str] = field(default_factory=list)
    current_preset_name: str | None = None
    is_unsaved: bool = False
