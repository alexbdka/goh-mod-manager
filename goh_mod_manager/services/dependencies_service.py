from typing import List, Optional, Set

from goh_mod_manager.core.mod import Mod


class DependenciesService:
    @staticmethod
    def get_missing_dependencies(
        mod: Mod,
        active_mods: List[Mod],
        installed_mods: List[Mod],
        visited: Optional[Set[str]] = None,
    ) -> List[Mod]:
        if visited is None:
            visited = set()

        if mod.id in visited:
            return []

        visited.add(mod.id)

        if not mod.require:
            return []

        required_ids = str(mod.require).split()
        active_ids = {m.id for m in active_mods}
        installed_by_id = {m.id: m for m in installed_mods}

        missing: List[Mod] = []

        for req_id in required_ids:
            if req_id not in installed_by_id:
                continue
            if req_id in visited:
                continue

            req_mod = installed_by_id[req_id]
            sub_missing = DependenciesService.get_missing_dependencies(
                req_mod, active_mods, installed_mods, visited
            )

            for sub_mod in sub_missing:
                if sub_mod not in missing:
                    missing.append(sub_mod)

            if req_id not in active_ids and req_mod not in missing:
                missing.append(req_mod)

        return missing
