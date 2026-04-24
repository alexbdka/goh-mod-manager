import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return ``True`` when running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


def get_project_root() -> Path:
    """Return the repository root in development mode."""
    return Path(__file__).resolve().parents[2]


def get_resource_root() -> Path:
    """Return the directory that contains packaged runtime assets."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return get_project_root()


def get_data_root() -> Path:
    """Return the base directory for machine-local writable application data."""
    if is_frozen():
        return Path(os.path.expanduser("~")) / ".goh-mod-manager"
    return get_project_root()


def ensure_directory(path: Path) -> Path:
    """Create a directory tree if needed and return the same path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_resource_path(*parts: str) -> Path:
    """Build an absolute path under the runtime resource root."""
    return get_resource_root().joinpath(*parts)


def get_logs_dir() -> Path:
    """Return the log directory, creating it if needed."""
    return ensure_directory(get_data_root() / "logs")


def get_log_file_path() -> Path:
    """Return the main application log file path."""
    return get_logs_dir() / "mod_manager.log"


def get_config_dir() -> Path:
    """Return the directory that stores the user config file."""
    return ensure_directory(get_data_root())


def get_config_file_path() -> Path:
    """Return the path to the JSON configuration file."""
    return get_config_dir() / "config.json"


def get_version_file_path() -> Path:
    """Return the packaged application version file path."""
    return get_resource_path(".app-version")


def read_version(default: str = "Unknown") -> str:
    """Read the packaged version string, or return ``default`` on failure."""
    try:
        return get_version_file_path().read_text(encoding="utf-8").strip()
    except OSError:
        return default
