import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def open_path(path: str) -> bool:
    """Open a local path with the platform default handler."""
    if not path or not os.path.exists(path):
        return False
    return _open_target(path)


def open_url(url: str) -> bool:
    """Open an external URL with the platform default handler."""
    if not url:
        return False
    return _open_target(url)


def launch_executable(executable_path: str, *, cwd: str | None = None) -> bool:
    """Launch an executable directly, optionally from a specific working directory."""
    if not executable_path or not os.path.exists(executable_path):
        return False

    working_dir = cwd or os.path.dirname(executable_path)
    try:
        subprocess.Popen([executable_path], cwd=working_dir)
        return True
    except Exception:
        logger.exception("Failed to launch executable: %s", executable_path)
        return False


def _open_target(target: str) -> bool:
    try:
        if os.name == "nt":
            os.startfile(target)
        elif os.uname().sysname == "Darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])
        return True
    except Exception:
        logger.exception("Failed to open target: %s", target)
        return False
