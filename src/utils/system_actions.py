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
