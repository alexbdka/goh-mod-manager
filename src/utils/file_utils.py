import os
import tempfile
from pathlib import Path


def atomic_write_text(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> None:
    """
    Atomically replace a text file by writing to a temp file in the same
    directory and swapping it into place.
    """
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path_str = tempfile.mkstemp(
        dir=target_path.parent,
        prefix=f"{target_path.name}.",
        suffix=".tmp",
        text=True,
    )
    temp_path = Path(temp_path_str)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, target_path)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
