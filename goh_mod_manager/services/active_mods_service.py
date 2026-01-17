from pathlib import Path
from typing import List, Tuple

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.mod_manager_logger import logger
from goh_mod_manager.infrastructure.options_set_parser import OptionsSetParser


class ActiveModsService:
    @staticmethod
    def load_active_mod_ids(options_file: str) -> Tuple[List[str], List[str]]:
        """
        Load active mod IDs from the options file.

        Returns:
            (mod_ids, invalid_entries): A tuple of valid mod IDs and invalid raw lines
            found inside the mods section.
        """
        if not options_file:
            return [], []

        options_path = Path(options_file)
        if not options_path.exists():
            return [], []

        parser = OptionsSetParser(str(options_path))
        return parser.get_mods(), parser.get_invalid_mod_entries()

    @staticmethod
    def save_active_mods(options_file: str, mods: List[Mod]) -> bool:
        if not options_file:
            logger.error("Options file path is empty")
            return False

        parser = OptionsSetParser(options_file)
        return parser.set_mods(mods)

    @staticmethod
    def clear_active_mods(options_file: str) -> bool:
        if not options_file:
            logger.error("Options file path is empty")
            return False

        parser = OptionsSetParser(options_file)
        return parser.clear_mods_section()
