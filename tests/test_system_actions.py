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
