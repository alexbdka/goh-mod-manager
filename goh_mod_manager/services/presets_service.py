from typing import Dict, List

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.mod_manager_logger import logger


class PresetsService:
    @staticmethod
    def resolve_presets(
        presets: Dict[str, List[str]], installed_mods: List[Mod]
    ) -> Dict[str, List[Mod]]:
        resolved: Dict[str, List[Mod]] = {}
        installed_by_id = {mod.id: mod for mod in installed_mods}

        for preset_name, mod_ids in presets.items():
            preset_mods: List[Mod] = []
            for mod_id in mod_ids:
                mod = installed_by_id.get(mod_id)
                if mod:
                    preset_mods.append(mod)
                else:
                    logger.warning(
                        f"Mod with ID '{mod_id}' not found in installed mods"
                    )
            resolved[preset_name] = preset_mods

        return resolved

    @staticmethod
    def to_config_payload(presets: Dict[str, List[Mod]]) -> Dict[str, List[str]]:
        return {name: [mod.id for mod in mods] for name, mods in presets.items()}
