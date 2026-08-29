from pathlib import Path

from src.utils import system_actions


def test_launch_executable_uses_executable_directory_by_default(
    tmp_path: Path, monkeypatch
):
    executable = tmp_path / "Game Folder" / "binaries" / "x64" / "editor.exe"
    executable.parent.mkdir(parents=True)
    executable.write_text("", encoding="utf-8")
    calls = []

    def fake_popen(command, cwd=None):
        calls.append((command, cwd))

    monkeypatch.setattr(system_actions.subprocess, "Popen", fake_popen)

    assert system_actions.launch_executable(str(executable)) is True
    assert calls == [([str(executable)], str(executable.parent))]


def test_launch_executable_returns_false_for_missing_path():
    assert system_actions.launch_executable("") is False
    assert system_actions.launch_executable("missing.exe") is False


def test_launch_steam_game_prefers_native_linux_client(monkeypatch):
    calls = []
    monkeypatch.setattr(system_actions.os, "name", "posix")
    monkeypatch.setattr(
        system_actions.os,
        "uname",
        lambda: type("Uname", (), {"sysname": "Linux"})(),
        raising=False,
    )
    monkeypatch.setattr(system_actions.shutil, "which", lambda name: "/usr/bin/steam")
    monkeypatch.setattr(
        system_actions.subprocess,
        "Popen",
        lambda command: calls.append(command),
    )
    monkeypatch.setattr(
        system_actions,
        "open_url",
        lambda _url: (_ for _ in ()).throw(AssertionError("unexpected fallback")),
    )

    assert system_actions.launch_steam_game("400750") is True
    assert calls == [["/usr/bin/steam", "-applaunch", "400750"]]


def test_launch_steam_game_falls_back_to_flatpak_then_protocol(monkeypatch):
    calls = []
    opened_urls = []
    monkeypatch.setattr(system_actions.os, "name", "posix")
    monkeypatch.setattr(
        system_actions.os,
        "uname",
        lambda: type("Uname", (), {"sysname": "Linux"})(),
        raising=False,
    )
    monkeypatch.setattr(system_actions.shutil, "which", lambda _name: None)

    def failing_popen(command):
        calls.append(command)
        raise OSError("not available")

    monkeypatch.setattr(system_actions.subprocess, "Popen", failing_popen)
    monkeypatch.setattr(
        system_actions,
        "open_url",
        lambda url: (opened_urls.append(url), True)[1],
    )

    assert system_actions.launch_steam_game("400750") is True
    assert calls == [
        ["flatpak", "run", "com.valvesoftware.Steam", "-applaunch", "400750"]
    ]
    assert opened_urls == ["steam://rungameid/400750"]
