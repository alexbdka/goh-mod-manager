"""
Global pytest configuration and fixtures for test isolation.

Ensures tests do not pollute local directories, registries, or configuration.
All app paths are redirected to temporary directories during test execution.
"""

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def isolate_app_paths(monkeypatch, tmp_path, request):
    """
    Redirect app_paths functions to use temporary directories during tests.

    This prevents tests from creating files in:
    - ~/.goh-mod-manager/ (user config directory)
    - Project root (logs, etc.)

    Instead, all paths resolve to the pytest tmp_path for complete isolation.

    Exception: Tests in test_app_paths.py are not isolated (they test app_paths logic).
    """
    # Skip isolation for app_paths unit tests (they test the logic itself)
    if "test_app_paths.py" in str(request.fspath):
        return

    app_data_dir = tmp_path / "app_data"
    config_dir = tmp_path / "config"
    logs_dir = tmp_path / "logs"

    app_data_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Redirect app_paths functions
    monkeypatch.setattr(
        "src.utils.app_paths.get_data_root",
        lambda: app_data_dir,
    )
    monkeypatch.setattr(
        "src.utils.app_paths.get_config_dir",
        lambda: config_dir,
    )
    monkeypatch.setattr(
        "src.utils.app_paths.get_logs_dir",
        lambda: logs_dir,
    )
    monkeypatch.setattr(
        "src.utils.app_paths.get_config_file_path",
        lambda: config_dir / "config.json",
    )
    monkeypatch.setattr(
        "src.utils.app_paths.get_log_file_path",
        lambda: logs_dir / "mod_manager.log",
    )


@pytest.fixture(autouse=True)
def isolate_qsettings_registry(monkeypatch, tmp_path):
    """
    Prevent QSettings from accessing the real Windows registry during tests.

    Redirects QSettings to use a temporary INI file instead of the registry.
    This avoids leaving test artifacts in HKEY_CURRENT_USER.
    """
    try:
        from PySide6.QtCore import QSettings
    except ImportError:
        # Qt not available in non-GUI test contexts
        return

    qsettings_cls: Any = QSettings
    ini_format = qsettings_cls.IniFormat
    user_scope = qsettings_cls.UserScope
    native_format = qsettings_cls.NativeFormat

    settings_dir = tmp_path / "qt_settings"
    settings_dir.mkdir(parents=True, exist_ok=True)

    # Force INI format and point to temp directory
    qsettings_cls.setDefaultFormat(ini_format)
    qsettings_cls.setPath(ini_format, user_scope, str(settings_dir))

    yield

    # Restore native format after test
    try:
        qsettings_cls.setDefaultFormat(native_format)
    except Exception:
        pass
