from pathlib import Path

from src.utils import app_paths


def test_read_version_from_project_file():
    expected = Path(".app-version").read_text(encoding="utf-8").strip()
    assert app_paths.read_version() == expected


def test_log_file_path_uses_project_logs_in_dev_mode():
    log_path = app_paths.get_log_file_path()
    assert log_path.name == "mod_manager.log"
    assert log_path.parent == app_paths.get_project_root() / "logs"


def test_config_file_path_uses_project_root_in_dev_mode():
    config_path = app_paths.get_config_file_path()
    assert config_path.name == "config.json"
    assert config_path.parent == app_paths.get_project_root()


def test_resource_root_uses_meipass_when_frozen(monkeypatch):
    frozen_root = Path("C:/temp/frozen-root")
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app_paths.sys, "_MEIPASS", str(frozen_root), raising=False)

    assert app_paths.is_frozen() is True
    assert app_paths.get_resource_root() == frozen_root
    assert app_paths.get_resource_path("assets", "icons").parts[-2:] == (
        "assets",
        "icons",
    )


def test_data_root_uses_user_home_when_frozen(monkeypatch):
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app_paths.os.path, "expanduser", lambda value: "C:/Users/test")

    assert app_paths.get_data_root() == Path("C:/Users/test") / ".goh-mod-manager"


def test_config_file_path_uses_data_root_when_frozen(monkeypatch):
    monkeypatch.setattr(app_paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(app_paths.os.path, "expanduser", lambda value: "C:/Users/test")
    monkeypatch.setattr(app_paths, "ensure_directory", lambda path: path)

    assert app_paths.get_config_file_path() == (
        Path("C:/Users/test") / ".goh-mod-manager" / "config.json"
    )
