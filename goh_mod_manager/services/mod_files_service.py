import datetime
import os
from typing import List, Tuple

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.mod_manager_logger import logger


class ModFilesService:
    def generate_help_file(
        self,
        options_file: str,
        game_folder: str,
        mods_folder: str,
        load_order: List[Mod],
        output_dir: str = ".",
    ) -> Tuple[bool, str]:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"help-{now}.txt"
            filepath = os.path.join(output_dir, filename)

            logger.info(f"Generating help file: {filepath}")

            if os.path.exists(options_file):
                with open(options_file, "r", encoding="utf-8") as f:
                    config_content = f.read()
            else:
                config_content = f"[!] Options file not found: {options_file}"
                logger.warning(config_content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=== HELP FILE ===\n")
                f.write(f"Generated on: {datetime.datetime.now()}\n\n")

                f.write("=== LOAD ORDER ===\n")
                for i, mod in enumerate(load_order, start=1):
                    f.write(f"{i}. {mod}\n")

                f.write("\n=== CONFIGURATION FILE ===\n")
                f.write(f"Options file: {options_file}\n")
                f.write(f"Game directory: {game_folder}\n")
                f.write(f"Mods directory: {mods_folder}\n\n")
                f.write(f"Options file content:\n\n{config_content}")

            logger.info(f"Help file successfully generated: {filepath}")
            return True, filepath

        except Exception as e:
            logger.error(f"Failed to generate help file: {e}", exc_info=True)
            return False, str(e)
