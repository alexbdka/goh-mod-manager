class ModManagerError(Exception):
    """Base exception for all Mod Manager domain errors."""

    pass


class ModImportError(ModManagerError):
    """Raised when a mod import fails."""

    pass


class ModInfoNotFoundError(ModImportError):
    """Raised when no mod.info could be found in the imported path."""

    pass


class InvalidModPathError(ModImportError):
    """Raised when the path to import does not exist or is neither a file nor a directory."""

    pass


class ModAlreadyExistsError(ModImportError):
    """Raised when the mod being imported already exists in the destination."""

    pass


class ArchiveExtractionError(ModImportError):
    """Raised when an archive fails to extract (e.g., corrupted or unsupported format)."""

    pass


class ShareCodeError(ModManagerError):
    """Raised when an operation on a share code fails."""

    pass


class InvalidShareCodeError(ShareCodeError):
    """Raised when a share code is malformed or cannot be decoded."""

    pass


class PresetError(ModManagerError):
    """Raised when an operation on a preset fails."""

    pass


class PresetNotFoundError(PresetError):
    """Raised when attempting to access or delete a preset that does not exist."""

    pass
