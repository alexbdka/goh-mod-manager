import logging
import os
from typing import cast

from src.core import constants
from src.core.mod import ModInfo
from src.utils.gem_parser import GemNodeValue, parse_gem_file

logger = logging.getLogger(__name__)


class ModsCatalogueService:
    def __init__(self):
        self._workshop_mods: dict[str, ModInfo] = {}
        self._local_mods: dict[str, ModInfo] = {}

    @property
    def workshop_mods(self) -> list[ModInfo]:
        """Returns a list of all workshop mods."""
        return list(self._workshop_mods.values())

    @property
    def local_mods(self) -> list[ModInfo]:
        """Returns a list of all local mods."""
        return list(self._local_mods.values())

    @property
    def all_mods(self) -> list[ModInfo]:
        """Returns a combined list of both local and workshop mods."""
        return self.local_mods + self.workshop_mods

    def get_mod(self, mod_id: str) -> ModInfo | None:
        """Finds a mod by its ID in either catalogue."""
        if mod_id in self._local_mods:
            return self._local_mods[mod_id]
        return self._workshop_mods.get(mod_id)

    def load_catalogue(self, local_mods_path: str, workshop_path: str) -> None:
        """
        Scans the provided directories and populates the local and workshop catalogues.
        """
        self._local_mods.clear()
        self._workshop_mods.clear()

        # Load Local Mods
        if os.path.exists(local_mods_path) and os.path.isdir(local_mods_path):
            logger.info(f"Scanning local mods directory: {local_mods_path}")
            self._scan_directory(local_mods_path, is_local=True)
        else:
            logger.warning(f"Local mods directory not found: {local_mods_path}")

        # Load Workshop Mods
        if os.path.exists(workshop_path) and os.path.isdir(workshop_path):
            logger.info(f"Scanning workshop directory: {workshop_path}")
            self._scan_directory(workshop_path, is_local=False)
        else:
            logger.warning(f"Workshop directory not found: {workshop_path}")

        logger.info(
            "Catalogue loaded: "
            f"{len(self._local_mods)} local mods, "
            f"{len(self._workshop_mods)} workshop mods."
        )

    def _scan_directory(self, directory_path: str, is_local: bool) -> None:
        """
        Iterate through subdirectories of a given path and try to parse
        ``mod.info`` files.
        """
        for entry in os.scandir(directory_path):
            if not entry.is_dir():
                continue

            mod_id = entry.name
            mod_info_path = os.path.join(entry.path, constants.MOD_INFO_FILE)

            if not os.path.exists(mod_info_path):
                logger.debug(
                    f"Skipping directory without "
                    f"{constants.MOD_INFO_FILE}: {entry.path}"
                )
                continue

            mod_info = self._parse_mod_info(mod_info_path, mod_id, is_local, entry.path)
            if mod_info:
                if is_local:
                    self._local_mods[mod_id] = mod_info
                else:
                    self._workshop_mods[mod_id] = mod_info

    def _parse_mod_info(
        self, file_path: str, mod_id: str, is_local: bool, mod_dir_path: str
    ) -> ModInfo | None:
        """
        Parses a mod.info file and returns a ModInfo object.
        """
        try:
            nodes = parse_gem_file(file_path)
            if not nodes:
                logger.error(
                    f"Failed to parse or empty {constants.MOD_INFO_FILE} at {file_path}"
                )
                return None

            # Find the root {mod ...} node
            mod_node = next((node for node in nodes if node.name == "mod"), None)
            if not mod_node:
                logger.error(f"No {{mod ...}} root node found in {file_path}")
                return None

            raw_data = mod_node.to_dict()
            if not isinstance(raw_data, dict):
                logger.error(f"Unexpected mod.info structure in {file_path}")
                return None
            data = cast(dict[str, GemNodeValue], raw_data)

            # Fall back to the folder ID when badly formatted mods omit a name.
            name = self._coerce_string(data.get("name"), mod_id)

            # Normalize single-string tags and dependencies to lists so the rest
            # of the application can treat them consistently.
            tags_raw = data.get("tags", [])
            tags = tags_raw if isinstance(tags_raw, list) else [tags_raw]

            req_raw = data.get("require", [])
            dependencies = req_raw if isinstance(req_raw, list) else [req_raw]

            # Filter out empty strings from lists
            tags = [str(t) for t in tags if t]
            dependencies = [
                str(d)[len(constants.MOD_PREFIX) :]
                if str(d).startswith(constants.MOD_PREFIX)
                else str(d)
                for d in dependencies
                if d
            ]

            image_name = self._coerce_string(data.get("image"), "").strip('"/\\')
            image_path = None
            if image_name:
                img_path = os.path.join(mod_dir_path, image_name)
                if os.path.exists(img_path):
                    image_path = img_path

            if not image_path:
                for ext in [".jpg", ".png", ".jpeg"]:
                    img_path = os.path.join(mod_dir_path, f"preview{ext}")
                    if os.path.exists(img_path):
                        image_path = img_path
                        break

            return ModInfo(
                id=mod_id,
                name=name,
                desc=self._coerce_string(data.get("desc"), ""),
                tags=tags,
                minGameVersion=self._coerce_optional_string(data.get("minGameVersion")),
                maxGameVersion=self._coerce_optional_string(data.get("maxGameVersion")),
                dependencies=dependencies,
                isLocal=is_local,
                # Keep shader detection disabled until we add a dedicated scan.
                hasShaders=False,
                path=mod_dir_path,
                image_path=image_path,
            )

        except Exception as e:
            logger.error(f"Error parsing mod.info at {file_path}: {e}")
            return None

    @staticmethod
    def _coerce_string(value: GemNodeValue | None, default: str) -> str:
        if isinstance(value, str):
            return value
        return default

    @staticmethod
    def _coerce_optional_string(value: GemNodeValue | None) -> str | None:
        if isinstance(value, str):
            return value
        return None
