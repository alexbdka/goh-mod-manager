import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_resource_root() -> Path:
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return get_project_root()


def get_data_root() -> Path:
    if is_frozen():
        return Path(os.path.expanduser("~")) / ".goh-mod-manager"
    return get_project_root()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_resource_path(*parts: str) -> Path:
    return get_resource_root().joinpath(*parts)


def get_logs_dir() -> Path:
    return ensure_directory(get_data_root() / "logs")


def get_log_file_path() -> Path:
    return get_logs_dir() / "mod_manager.log"


def get_config_dir() -> Path:
    return ensure_directory(get_data_root())


def get_config_file_path() -> Path:
    return get_config_dir() / "config.json"


def get_version_file_path() -> Path:
    return get_resource_path(".app-version")


def read_version(default: str = "Unknown") -> str:
    try:
        return get_version_file_path().read_text(encoding="utf-8").strip()
    except OSError:
        return default
