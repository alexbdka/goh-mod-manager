from PySide6.QtGui import QFont

from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.services.font_service import FontService


class AppearanceViewModel:
    def __init__(self, config: ConfigManager):
        self._config = config
        self._fonts = FontService()

    def apply_saved_font(self) -> QFont:
        font_name = self._config.get_font()
        return self._fonts.load_font(font_name)

    def set_font(self, font_name: str) -> QFont:
        self._config.set_font(font_name)
        return self._fonts.load_font(font_name)
