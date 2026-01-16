from typing import Set

from PySide6.QtCore import QObject

from goh_mod_manager.core.mod import Mod


class ModDetailsViewModel(QObject):
    def get_required_ids(self, mod: Mod | None) -> Set[str]:
        if not mod or not mod.require:
            return set()

        return set(str(mod.require).split())
