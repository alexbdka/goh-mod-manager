import os
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

from goh_mod_manager.infrastructure.config_manager import TEST_SETTINGS

os.environ["GOH_MM_TESTING"] = "1"


def pytest_sessionstart(session) -> None:
    QSettings.setDefaultFormat(QSettings.IniFormat)


def pytest_sessionfinish(session, exitstatus) -> None:
    QSettings.setDefaultFormat(QSettings.NativeFormat)


def _setup_settings_path(tmp_path) -> None:
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    organization, application = TEST_SETTINGS
    settings = QSettings(organization, application)
    settings.clear()
    settings.sync()


def pytest_configure(config) -> None:
    # Use a fixed temp directory per session to avoid touching user registry.
    cache_dir = config.cache.makedir("qsettings")
    _setup_settings_path(cache_dir)


@pytest.fixture
def sample_options_path() -> Path:
    return Path(__file__).resolve().parent / "options.set"
