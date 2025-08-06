from loguru import logger

LOG_PATH = "logs/goh-mod-manager.log"

logger.add(
    LOG_PATH,
)

__all__ = ["logger"]
