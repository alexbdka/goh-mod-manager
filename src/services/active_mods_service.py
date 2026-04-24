import logging
import os

from src.core import constants
from src.core.exceptions import ProfileWriteError
from src.core.mod import ModInfo
from src.services.mods_catalogue_service import ModsCatalogueService
from src.utils.file_utils import atomic_write_text
from src.utils.gem_parser import parse_gem_file

logger = logging.getLogger(__name__)


class ActiveModsService:
    """Manage the active load order and its serialization to ``options.set``."""

    def __init__(self, catalogue: ModsCatalogueService):
        self.catalogue = catalogue
        self.active_mods_ids: list[str] = []

    def get_active_mods(self) -> list[ModInfo]:
        """Return active mods in the exact order expected by the game engine."""
        active_mods = []
        for mod_id in self.active_mods_ids:
            mod = self.catalogue.get_mod(mod_id)
            if mod:
                active_mods.append(mod)
            else:
                logger.warning(f"Active mod with ID {mod_id} not found in catalogue.")
        return active_mods

    def activate_mod(self, mod_id: str, _visited: set | None = None) -> list[str]:
        """
        Activate a mod and recursively activate any known dependencies first.

        Returns a list of dependency IDs that were referenced by the target mod
        but are missing from the catalogue.
        """
        if _visited is None:
            _visited = set()

        missing_deps = []
        if mod_id in _visited:
            return missing_deps

        _visited.add(mod_id)

        if mod_id not in self.active_mods_ids:
            mod = self.catalogue.get_mod(mod_id)
            if mod and mod.dependencies:
                for dep in mod.dependencies:
                    if dep not in self.active_mods_ids:
                        dep_mod = self.catalogue.get_mod(dep)
                        if dep_mod:
                            missing_deps.extend(
                                self.activate_mod(dep, _visited=_visited)
                            )
                        else:
                            missing_deps.append(dep)
                            logger.warning(
                                f"Dependency {dep} for mod {mod_id} "
                                "not found in catalogue."
                            )

            self.active_mods_ids.append(mod_id)
            logger.info(f"Activated mod: {mod_id}")

        return missing_deps

    def replace_active_mods(self, mod_ids: list[str]) -> list[str]:
        """
        Replace the current load order while resolving dependencies consistently.

        Returns a de-duplicated list of missing mod or dependency IDs.
        """
        self.active_mods_ids.clear()

        missing_mods: list[str] = []
        seen_missing: set[str] = set()

        for mod_id in mod_ids:
            mod = self.catalogue.get_mod(mod_id)
            if not mod:
                if mod_id not in seen_missing:
                    missing_mods.append(mod_id)
                    seen_missing.add(mod_id)
                logger.warning(f"Requested mod {mod_id} not found in catalogue.")
                continue

            for missing_id in self.activate_mod(mod_id):
                if missing_id not in seen_missing:
                    missing_mods.append(missing_id)
                    seen_missing.add(missing_id)

        return missing_mods

    def deactivate_mod(self, mod_id: str) -> None:
        """Removes a mod from the active list."""
        if mod_id in self.active_mods_ids:
            self.active_mods_ids.remove(mod_id)
            logger.info(f"Deactivated mod: {mod_id}")

    def move_mod_up(self, mod_id: str) -> None:
        """Moves a mod up in the load order (loads earlier, lower priority)."""
        if mod_id in self.active_mods_ids:
            index = self.active_mods_ids.index(mod_id)
            if index > 0:
                self.active_mods_ids.insert(index - 1, self.active_mods_ids.pop(index))

    def move_mod_down(self, mod_id: str) -> None:
        """
        Move a mod down in the load order so it loads later and can override
        earlier entries.
        """
        if mod_id in self.active_mods_ids:
            index = self.active_mods_ids.index(mod_id)
            if index < len(self.active_mods_ids) - 1:
                self.active_mods_ids.insert(index + 1, self.active_mods_ids.pop(index))

    def load_from_profile(self, options_set_path: str) -> None:
        """Load active mods from the game's ``options.set`` profile file."""
        self.active_mods_ids.clear()

        if not os.path.exists(options_set_path):
            logger.warning(f"Profile file not found: {options_set_path}")
            return

        try:
            nodes = parse_gem_file(options_set_path)
            if not nodes:
                return

            options_node = next((n for n in nodes if n.name == "options"), None)
            if not options_node:
                return

            mods_node = next(
                (n for n in options_node.children if n.name == "mods"), None
            )
            if not mods_node:
                return

            for raw_mod_str in mods_node.values:
                clean_str = raw_mod_str.strip('"')
                mod_id_with_prefix = (
                    clean_str.split(":")[0] if ":" in clean_str else clean_str
                )

                if mod_id_with_prefix.startswith(constants.MOD_PREFIX):
                    mod_id = mod_id_with_prefix[len(constants.MOD_PREFIX) :]
                else:
                    mod_id = mod_id_with_prefix

                if mod_id:
                    self.active_mods_ids.append(mod_id)

            logger.info(f"Loaded {len(self.active_mods_ids)} active mods from profile.")

        except Exception as e:
            logger.error(f"Failed to load profile from {options_set_path}: {e}")

    def save_to_profile(self, options_set_path: str, catalogue_service=None) -> None:
        """
        Write the current active load order back to ``options.set``.

        Only the ``{mods ...}`` block is replaced so the rest of the file
        remains untouched.
        """
        if not os.path.exists(options_set_path):
            logger.error(f"Cannot save profile, file not found: {options_set_path}")
            return

        try:
            with open(options_set_path, encoding="utf-8") as f:
                content = f.read()

            if self.active_mods_ids:
                mods_lines_list = []
                for mod_id in self.active_mods_ids:
                    is_local = False
                    if catalogue_service:
                        mod = catalogue_service.get_mod(mod_id)
                        if mod and mod.isLocal:
                            is_local = True

                    if is_local or not mod_id.isdigit():
                        mods_lines_list.append(f'"{mod_id}:0"')
                    else:
                        mods_lines_list.append(f'"{constants.MOD_PREFIX}{mod_id}:0"')

                mods_lines = "\n\t\t".join(mods_lines_list)
                new_mods_block = f"{{mods\n\t\t{mods_lines}\n\t}}"
            else:
                new_mods_block = "{mods}"

            # Brace matching avoids stopping at the wrong closing brace if other
            # nested blocks appear later in the file.
            mods_start = content.find("{mods")
            if mods_start != -1:
                mods_end = self._find_matching_block_end(content, mods_start)
                if mods_end is None:
                    raise ValueError("Malformed options.set: unterminated {mods} block")

                updated_content = (
                    content[:mods_start] + new_mods_block + content[mods_end:]
                )
            else:
                last_brace_idx = content.rfind("}")
                if last_brace_idx != -1:
                    updated_content = (
                        content[:last_brace_idx]
                        + "\t"
                        + new_mods_block
                        + "\n"
                        + content[last_brace_idx:]
                    )
                else:
                    updated_content = content + "\n" + new_mods_block

            atomic_write_text(options_set_path, updated_content)

            logger.info(
                "Successfully saved "
                f"{len(self.active_mods_ids)} active mods to profile."
            )

        except OSError as e:
            logger.error(f"Failed to save profile to {options_set_path}: {e}")
            raise ProfileWriteError(options_set_path, str(e)) from e
        except Exception as e:
            logger.error(f"Failed to save profile to {options_set_path}: {e}")
            raise ProfileWriteError(options_set_path, str(e)) from e

    @staticmethod
    def _find_matching_block_end(content: str, block_start: int) -> int | None:
        """
        Returns the end index (exclusive) of the block that starts at block_start.
        Handles nested braces and quoted strings.
        """
        if (
            block_start < 0
            or block_start >= len(content)
            or content[block_start] != "{"
        ):
            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(block_start, len(content)):
            char = content[index]

            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index + 1

        return None
