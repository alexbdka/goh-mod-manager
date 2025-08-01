import os

from loguru import logger

log_path = os.path.join(os.path.dirname(__file__), "logs/goh-mod-manager.log")

logger.add(
    log_path,
)

__all__ = ["logger"]
