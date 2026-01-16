from pathlib import Path
from typing import List, Optional

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.mod_info_parser import ModInfoParser
from goh_mod_manager.infrastructure.mod_manager_logger import logger


class ModsCatalogService:
    def scan_installed_mods(
        self, mods_directory: str | None, game_mods_directory: str | None
    ) -> List[Mod]:
        installed_mods: List[Mod] = []
        directories_to_scan: list[Path] = []

        if mods_directory:
            mods_path = Path(mods_directory)
            if mods_path.exists():
                directories_to_scan.append(mods_path)

        if game_mods_directory:
            game_path = Path(game_mods_directory)
            if game_path.exists() and game_path not in directories_to_scan:
                directories_to_scan.append(game_path)

        if directories_to_scan:
            logger.info(
                "Scanning mods in: {}",
                ", ".join(str(path) for path in directories_to_scan),
            )

        for directory in directories_to_scan:
            for item in directory.iterdir():
                if item.is_dir():
                    mod = self._load_mod_from_directory(item)
                    if mod:
                        installed_mods.append(mod)

        if directories_to_scan:
            logger.info(
                "Installed mods scan complete: {} mods found",
                len(installed_mods),
            )

        return installed_mods

    @staticmethod
    def _load_mod_from_directory(mod_path: Path) -> Optional[Mod]:
        mod_info_file = mod_path / "mod.info"

        if not mod_info_file.exists():
            return None

        try:
            parser = ModInfoParser(str(mod_info_file))
            return parser.parse()
        except Exception as e:
            logger.error(f"Error while parsing {mod_info_file}: {e}")
            return None

    @staticmethod
    def resolve_active_mods(
        active_mod_ids: List[str], installed_mods: List[Mod]
    ) -> List[Mod]:
        installed_by_id = {mod.id: mod for mod in installed_mods}
        resolved: List[Mod] = []

        for mod_id in active_mod_ids:
            mod = installed_by_id.get(mod_id)
            if mod:
                resolved.append(mod)
            else:
                logger.warning(
                    f"Active mod with ID '{mod_id}' not found in installed mods"
                )

        return resolved

    @staticmethod
    def find_installed_mod_by_id(
        installed_mods: List[Mod], mod_id: str
    ) -> Optional[Mod]:
        for mod in installed_mods:
            if mod.id == mod_id:
                return mod
        return None
