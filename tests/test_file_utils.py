from pathlib import Path

import pytest
from src.utils.file_utils import atomic_write_text


def test_atomic_write_text_replaces_file_contents(tmp_path: Path):
    target = tmp_path / "config.json"
    target.write_text("old", encoding="utf-8")

    atomic_write_text(target, "new content")

    assert target.read_text(encoding="utf-8") == "new content"
    assert list(tmp_path.glob("config.json.*.tmp")) == []


def test_atomic_write_text_keeps_original_file_when_replace_fails(
    monkeypatch, tmp_path: Path
):
    target = tmp_path / "options.set"
    target.write_text("original", encoding="utf-8")

    def fail_replace(_source, _target):
        raise OSError("locked file")

    monkeypatch.setattr("src.utils.file_utils.os.replace", fail_replace)

    with pytest.raises(OSError, match="locked file"):
        atomic_write_text(target, "updated")

    assert target.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.glob("options.set.*.tmp")) == []
