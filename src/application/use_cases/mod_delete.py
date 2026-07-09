import logging
import shutil

from src.core.events import EventBus, EventType
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService

logger = logging.getLogger(__name__)


class ApplicationModDeleteUseCase:
    """
    Application use case for deleting a locally installed mod.

    The mod is first deactivated if it is part of the active load order, then
    its directory is removed from disk and the in-memory catalogue is updated.
    """

    def __init__(
        self,
        active_mods_service: ActiveModsService,
        catalogue_service: ModsCatalogueService,
        config_service: ConfigService,
        event_bus: EventBus,
    ):
        self._active_mods = active_mods_service
        self._catalogue = catalogue_service
        self._config = config_service
        self._events = event_bus

    def delete_local_mod(self, mod_id: str) -> bool:
        """
        Delete a local mod by ID.

        Returns ``True`` when the mod was found, deactivated if necessary, and
        removed from disk and catalogue. Returns ``False`` when the mod is not a
        local mod, is required by another active mod, or its directory could not
        be removed.
        """
        mod = self._catalogue.get_mod_by_source(mod_id, is_local=True)
        if mod is None:
            logger.warning(
                "Cannot delete mod '%s': not found in local catalogue.", mod_id
            )
            return False

        if not mod.isLocal:
            logger.warning("Cannot delete mod '%s': not a local mod.", mod_id)
            return False

        mod_ref = f"local::{mod_id}"
        was_active = mod_ref in self._active_mods.active_mod_refs

        if was_active:
            dependents = self._active_mods.get_dependents_for_active_mod(mod_ref)
            if dependents:
                logger.warning(
                    "Cannot delete local mod '%s': required by active mods %s.",
                    mod_id,
                    dependents,
                )
                return False

            profile_path = self._config.get_config().profile_path
            if not profile_path:
                logger.error(
                    "Cannot deactivate mod '%s' before deletion: "
                    "profile path not configured.",
                    mod_id,
                )
                return False

            self._active_mods.deactivate_mod(mod_ref)
            self._active_mods.save_to_profile(
                profile_path, catalogue_service=self._catalogue
            )
            self._events.emit(EventType.ACTIVE_MODS_CHANGED)

        try:
            shutil.rmtree(mod.path)
        except OSError as error:
            logger.error(
                "Failed to delete local mod directory '%s': %s", mod.path, error
            )
            return False

        self._catalogue.remove_local_mod(mod_id)
        self._events.emit(EventType.CATALOGUE_CHANGED)
        logger.info("Deleted local mod: %s", mod_id)
        return True
