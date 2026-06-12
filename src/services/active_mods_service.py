import logging
import os

from src.core.exceptions import ProfileWriteError
from src.core.mod import ModInfo
from src.core.mod_reference import (
    ModReference,
    from_profile_mod_token,
    parse_reference_key,
    to_profile_mod_token,
    to_reference_key,
)
from src.services.mods_catalogue_service import ModsCatalogueService
from src.utils.file_utils import atomic_write_text
from src.utils.gem_parser import (
    GemNode,
    GemParseError,
    parse_gem,
    parse_gem_file,
    repair_gem_braces,
)

logger = logging.getLogger(__name__)


class ActiveModsService:
    """Manage the active load order and its serialization to ``options.set``."""

    def __init__(self, catalogue: ModsCatalogueService):
        self.catalogue = catalogue
        self._active_mod_refs: list[str] = []

    @property
    def active_mods_ids(self) -> list[str]:
        return [self._reference_from_key(key).id for key in self._active_mod_refs]

    @active_mods_ids.setter
    def active_mods_ids(self, mod_ids: list[str]) -> None:
        refs: list[str] = []
        for mod_id in mod_ids:
            reference = self._reference_from_identifier(mod_id)
            if reference is None:
                continue
            refs.append(to_reference_key(reference.id, reference.is_local))
        self._active_mod_refs = refs

    @property
    def active_mod_refs(self) -> list[str]:
        return list(self._active_mod_refs)

    @active_mod_refs.setter
    def active_mod_refs(self, refs: list[str]) -> None:
        normalized_refs: list[str] = []
        for ref in refs:
            reference = self._reference_from_identifier(ref)
            if reference is None:
                continue
            normalized_refs.append(to_reference_key(reference.id, reference.is_local))
        self._active_mod_refs = normalized_refs

    def get_active_mods(self) -> list[ModInfo]:
        """Return active mods in the exact order expected by the game engine."""
        active_mods = []
        for mod_ref in self._active_mod_refs:
            mod = self._get_mod_from_ref(mod_ref)
            if mod:
                active_mods.append(mod)
            else:
                logger.warning(
                    f"Active mod with reference {mod_ref} not found in catalogue."
                )
        return active_mods

    def is_active(self, mod_id: str, *, is_local: bool) -> bool:
        return to_reference_key(mod_id, is_local) in self._active_mod_refs

    def get_load_order(self, mod_id: str, *, is_local: bool) -> int | None:
        ref = to_reference_key(mod_id, is_local)
        if ref not in self._active_mod_refs:
            return None
        return self._active_mod_refs.index(ref) + 1

    def normalize_mod_refs(self, mod_identifiers: list[str]) -> list[str]:
        """Resolve mod IDs or reference keys into canonical active reference keys."""
        refs: list[str] = []
        for mod_identifier in mod_identifiers:
            reference = self._reference_from_identifier(mod_identifier)
            if reference is None:
                continue
            refs.append(to_reference_key(reference.id, reference.is_local))
        return refs

    def get_active_dependency_refs(self) -> dict[str, list[str]]:
        """Return active mod references mapped to their active dependency refs."""
        active_refs = set(self._active_mod_refs)
        dependency_refs: dict[str, list[str]] = {}

        for mod_ref in self._active_mod_refs:
            mod = self._get_mod_from_ref(mod_ref)
            if not mod:
                dependency_refs[mod_ref] = []
                continue

            refs: list[str] = []
            for dep_id in mod.dependencies:
                dep_reference = self._resolve_dependency_reference(
                    dep_id, preferred_local=mod.isLocal
                )
                if dep_reference is None:
                    continue

                dep_ref = to_reference_key(dep_reference.id, dep_reference.is_local)
                if dep_ref in active_refs:
                    refs.append(dep_ref)

            dependency_refs[mod_ref] = refs

        return dependency_refs

    def get_active_dependent_refs(self) -> dict[str, list[str]]:
        """Return active mod references mapped to active mods that require them."""
        dependency_refs = self.get_active_dependency_refs()
        dependent_refs = {mod_ref: [] for mod_ref in self._active_mod_refs}

        for mod_ref, dependencies in dependency_refs.items():
            for dep_ref in dependencies:
                dependent_refs.setdefault(dep_ref, []).append(mod_ref)

        return dependent_refs

    def get_dependents_for_active_mod(self, mod_identifier: str) -> list[str]:
        """Return active mods that depend on the given active mod reference."""
        ref = self._resolve_existing_reference(mod_identifier)
        if not ref:
            return []
        return self.get_active_dependent_refs().get(ref, [])

    def find_order_dependency_violations(self, refs: list[str]) -> list[str]:
        """Return refs whose dependencies would load after them in the given order."""
        dependency_refs = self.get_active_dependency_refs()
        positions = {ref: index for index, ref in enumerate(refs)}
        violations: list[str] = []

        for mod_ref, dependencies in dependency_refs.items():
            mod_index = positions.get(mod_ref)
            if mod_index is None:
                continue
            for dep_ref in dependencies:
                dep_index = positions.get(dep_ref)
                if dep_index is not None and dep_index > mod_index:
                    violations.append(mod_ref)
                    break

        return violations

    def activate_mod(
        self, mod_identifier: str, _visited: set[str] | None = None
    ) -> list[str]:
        """
        Activate a mod and recursively activate any known dependencies first.

        Returns a list of dependency IDs that were referenced by the target mod
        but are missing from the catalogue.
        """
        root_call = _visited is None
        snapshot = list(self._active_mod_refs) if root_call else None
        visited = _visited if _visited is not None else set()
        missing_deps = self._activate_mod_recursive(mod_identifier, visited)

        if root_call and missing_deps:
            self._active_mod_refs = snapshot if snapshot is not None else []

        return missing_deps

    def _activate_mod_recursive(
        self, mod_identifier: str, visited: set[str]
    ) -> list[str]:
        missing_deps: list[str] = []
        reference = self._reference_from_identifier(mod_identifier)
        if reference is None:
            logger.warning(f"Requested mod {mod_identifier} not found in catalogue.")
            return [mod_identifier]

        mod_ref = to_reference_key(reference.id, reference.is_local)
        if mod_ref in visited:
            return missing_deps

        visited.add(mod_ref)

        if mod_ref in self._active_mod_refs:
            return missing_deps

        mod = self.catalogue.get_mod_by_source(
            reference.id, is_local=reference.is_local
        )
        if mod and mod.dependencies:
            for dep in mod.dependencies:
                dep_reference = self._resolve_dependency_reference(
                    dep, preferred_local=mod.isLocal
                )
                if dep_reference is None:
                    missing_deps.append(dep)
                    logger.warning(
                        f"Dependency {dep} for mod "
                        f"{reference.id} not found in catalogue."
                    )
                    continue

                dep_ref = to_reference_key(dep_reference.id, dep_reference.is_local)
                if dep_ref in self._active_mod_refs:
                    continue

                missing_deps.extend(self._activate_mod_recursive(dep_ref, visited))

        if missing_deps:
            return missing_deps

        self._active_mod_refs.append(mod_ref)
        source = "local" if reference.is_local else "workshop"
        logger.info(f"Activated mod: {reference.id} ({source})")
        return missing_deps

    def replace_active_mods(self, mod_ids: list[str]) -> list[str]:
        """
        Replace the current load order while resolving dependencies consistently.

        Returns a de-duplicated list of missing mod or dependency IDs.
        """
        self._active_mod_refs.clear()

        missing_mods: list[str] = []
        seen_missing: set[str] = set()

        for mod_id in mod_ids:
            if not self._is_installed(mod_id):
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

    def deactivate_mod(self, mod_identifier: str) -> None:
        """Removes a mod from the active list."""
        ref = self._resolve_existing_reference(mod_identifier)
        if ref:
            self._active_mod_refs.remove(ref)
            reference = self._reference_from_key(ref)
            source = "local" if reference.is_local else "workshop"
            logger.info(f"Deactivated mod: {reference.id} ({source})")

    def move_mod_up(self, mod_identifier: str) -> None:
        """Moves a mod up in the load order (loads earlier, lower priority)."""
        ref = self._resolve_existing_reference(mod_identifier)
        if ref and ref in self._active_mod_refs:
            index = self._active_mod_refs.index(ref)
            if index > 0:
                self._active_mod_refs.insert(
                    index - 1, self._active_mod_refs.pop(index)
                )

    def move_mod_down(self, mod_identifier: str) -> None:
        """
        Move a mod down in the load order so it loads later and can override
        earlier entries.
        """
        ref = self._resolve_existing_reference(mod_identifier)
        if ref and ref in self._active_mod_refs:
            index = self._active_mod_refs.index(ref)
            if index < len(self._active_mod_refs) - 1:
                self._active_mod_refs.insert(
                    index + 1, self._active_mod_refs.pop(index)
                )

    def load_from_profile(self, options_set_path: str) -> None:
        """Load active mods from the game's ``options.set`` profile file."""
        self._active_mod_refs.clear()

        if not os.path.exists(options_set_path):
            logger.warning(f"Profile file not found: {options_set_path}")
            return

        try:
            nodes = self._parse_profile_nodes(options_set_path)
            if not nodes:
                return

            options_node = self._find_node_by_name(nodes, "options")
            if not options_node:
                return

            mods_node = self._find_node_by_name(options_node.children, "mods")
            if not mods_node:
                return

            for raw_mod_str in mods_node.values:
                clean_str = raw_mod_str.strip('"')
                mod_token = clean_str.split(":")[0] if ":" in clean_str else clean_str
                if not mod_token:
                    continue

                reference = from_profile_mod_token(mod_token)
                self._active_mod_refs.append(
                    to_reference_key(reference.id, reference.is_local)
                )

            logger.info(
                f"Loaded {len(self._active_mod_refs)} active mods from profile."
            )

        except Exception as e:
            logger.error(f"Failed to load profile from {options_set_path}: {e}")

    def _parse_profile_nodes(self, options_set_path: str) -> list[GemNode]:
        try:
            return parse_gem_file(options_set_path)
        except GemParseError as original_error:
            with open(options_set_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            repair = repair_gem_braces(content)
            if not repair.changed:
                raise

            try:
                nodes = parse_gem(repair.content)
            except GemParseError as repair_error:
                raise original_error from repair_error

            atomic_write_text(options_set_path, repair.content)
            logger.warning(
                "Auto-repaired profile GEM braces in %s "
                "(added %d closing brace(s), removed %d extra closing brace(s)).",
                options_set_path,
                repair.added_closing_braces,
                repair.removed_extra_closing_braces,
            )
            return nodes

    def save_to_profile(self, options_set_path: str, catalogue_service=None) -> None:
        """
        Write the current active load order back to ``options.set``.

        Only the ``{mods ...}`` block is replaced so the rest of the file
        remains untouched.
        """
        if not os.path.exists(options_set_path):
            reason = "Profile file not found."
            logger.error(f"Cannot save profile {options_set_path}: {reason}")
            raise ProfileWriteError(options_set_path, reason)

        try:
            with open(options_set_path, encoding="utf-8") as f:
                content = f.read()

            if self._active_mod_refs:
                mods_lines_list = []
                for mod_ref in self._active_mod_refs:
                    reference = self._reference_from_key(mod_ref)
                    mods_lines_list.append(f'"{to_profile_mod_token(reference)}:0"')

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
                f"{len(self._active_mod_refs)} active mods to profile."
            )

        except OSError as e:
            logger.error(f"Failed to save profile to {options_set_path}: {e}")
            raise ProfileWriteError(options_set_path, str(e)) from e
        except Exception as e:
            logger.error(f"Failed to save profile to {options_set_path}: {e}")
            raise ProfileWriteError(options_set_path, str(e)) from e

    def _resolve_dependency_reference(
        self, mod_id: str, *, preferred_local: bool
    ) -> ModReference | None:
        preferred_mod = self.catalogue.get_mod_by_source(
            mod_id, is_local=preferred_local
        )
        if preferred_mod:
            return ModReference(id=mod_id, is_local=preferred_local)

        fallback_mod = self.catalogue.get_mod_by_source(
            mod_id, is_local=not preferred_local
        )
        if fallback_mod:
            return ModReference(id=mod_id, is_local=not preferred_local)
        return None

    def _resolve_existing_reference(self, mod_identifier: str) -> str | None:
        parsed = parse_reference_key(mod_identifier)
        if parsed:
            ref = to_reference_key(parsed.id, parsed.is_local)
            if ref in self._active_mod_refs:
                return ref
            return None

        for ref in self._active_mod_refs:
            if self._reference_from_key(ref).id == mod_identifier:
                return ref
        return None

    def _reference_from_identifier(self, mod_identifier: str) -> ModReference | None:
        parsed = parse_reference_key(mod_identifier)
        if parsed:
            if not parsed.id:
                return None
            return parsed

        if not mod_identifier:
            return None

        if self.catalogue.get_mod_by_source(mod_identifier, is_local=True):
            return ModReference(id=mod_identifier, is_local=True)

        if self.catalogue.get_mod_by_source(mod_identifier, is_local=False):
            return ModReference(id=mod_identifier, is_local=False)

        return ModReference(id=mod_identifier, is_local=not mod_identifier.isdigit())

    @staticmethod
    def _reference_from_key(key: str) -> ModReference:
        parsed = parse_reference_key(key)
        if parsed is None:
            raise ValueError(f"Invalid mod reference key: {key}")
        return parsed

    def _get_mod_from_ref(self, mod_ref: str) -> ModInfo | None:
        reference = self._reference_from_key(mod_ref)
        return self.catalogue.get_mod_by_source(
            reference.id, is_local=reference.is_local
        )

    def _is_installed(self, mod_id: str) -> bool:
        parsed = parse_reference_key(mod_id)
        if parsed:
            return bool(
                self.catalogue.get_mod_by_source(parsed.id, is_local=parsed.is_local)
            )

        return bool(
            self.catalogue.get_mod_by_source(mod_id, is_local=True)
            or self.catalogue.get_mod_by_source(mod_id, is_local=False)
        )

    @staticmethod
    def _find_node_by_name(nodes: list[GemNode], node_name: str) -> GemNode | None:
        target = node_name.casefold()
        return next(
            (
                node
                for node in nodes
                if node.name is not None and node.name.casefold() == target
            ),
            None,
        )

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
