import logging
from typing import Dict, List, Optional

from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService

logger = logging.getLogger(__name__)


class PresetService:
    """
    Manages local mod presets (saving, loading, and applying lists of mods).
    """

    def __init__(
        self,
        config_service: ConfigService,
        catalogue_service: ModsCatalogueService,
        active_mods_service: ActiveModsService,
    ):
        self.config_service = config_service
        self.catalogue = catalogue_service
        self.active_mods = active_mods_service

    def get_all_presets(self) -> Dict[str, List[str]]:
        """Returns a dictionary of all saved presets."""
        config = self.config_service.get_config()
        return config.presets

    def get_preset(self, name: str) -> Optional[List[str]]:
        """Returns the mod IDs for a specific preset, or None if not found."""
        return self.get_all_presets().get(name)

    def save_preset(self, name: str, mod_ids: Optional[List[str]] = None) -> None:
        """
        Saves a list of mod IDs as a preset.
        If mod_ids is not provided, saves the currently active mods.
        """
        if mod_ids is None:
            # Create a copy of the list so it's not by reference
            mod_ids = list(self.active_mods.active_mods_ids)

        config = self.config_service.get_config()
        config.presets[name] = mod_ids
        self.config_service.save()

        logger.info(f"Saved preset '{name}' with {len(mod_ids)} mods.")

    def delete_preset(self, name: str) -> bool:
        """Deletes a preset by name. Returns True if successful."""
        config = self.config_service.get_config()
        if name in config.presets:
            del config.presets[name]
            self.config_service.save()
            logger.info(f"Deleted preset '{name}'.")
            return True

        logger.warning(f"Failed to delete preset '{name}': Not found.")
        return False

    def apply_preset(self, name: str) -> tuple[bool, List[str]]:
        """
        Applies a preset, completely replacing the currently active mods.
        Returns a tuple: (Success bool, List of missing mod IDs).
        """
        preset_mod_ids = self.get_preset(name)
        if preset_mod_ids is None:
            logger.error(f"Attempted to apply unknown preset: '{name}'")
            return False, []

        # Clear currently active mods
        self.active_mods.active_mods_ids.clear()

        # Add mods from the preset, keeping track of any that aren't installed
        missing_mods = []
        for mod_id in preset_mod_ids:
            if self.catalogue.get_mod(mod_id):
                # The active_mods_ids is just a list, we can append directly
                # to avoid triggering the logging noise of 'activate_mod' for every single item
                self.active_mods.active_mods_ids.append(mod_id)
            else:
                missing_mods.append(mod_id)

        if missing_mods:
            logger.warning(
                f"Applied preset '{name}' but {len(missing_mods)} mods are missing from the catalogue."
            )
        else:
            logger.info(f"Successfully applied preset '{name}'.")

        return True, missing_mods
