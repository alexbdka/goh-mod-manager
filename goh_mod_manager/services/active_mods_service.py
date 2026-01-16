from pathlib import Path
from typing import List

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.mod_manager_logger import logger
from goh_mod_manager.infrastructure.options_set_parser import OptionsSetParser


class ActiveModsService:
    def load_active_mod_ids(self, options_file: str) -> List[str]:
        if not options_file:
            return []

        options_path = Path(options_file)
        if not options_path.exists():
            return []

        parser = OptionsSetParser(str(options_path))
        return parser.get_mods()

    def save_active_mods(self, options_file: str, mods: List[Mod]) -> bool:
        if not options_file:
            logger.error("Options file path is empty")
            return False

        parser = OptionsSetParser(options_file)
        return parser.set_mods(mods)

    def clear_active_mods(self, options_file: str) -> bool:
        if not options_file:
            logger.error("Options file path is empty")
            return False

        parser = OptionsSetParser(options_file)
        return parser.clear_mods_section()
