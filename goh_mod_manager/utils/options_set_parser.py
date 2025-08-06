import re
from pathlib import Path
from typing import List

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.mod_manager_logger import logger


class OptionsSetParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.lines = []
        self.load()

    def load(self) -> bool:
        if not self.file_path.exists():
            return False
        else:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
            return True

    def save(self) -> bool:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(self.lines)
            return True
        except Exception as e:
            logger.error(f"Error while saving {self.file_path}: {e}")
            return False

    def is_mod_section_present(self) -> bool:
        if "\t{mods\n" in self.lines:
            return True
        else:
            logger.warning(f"No mods section found in {self.file_path}")
            if self.create_mods_section():
                return True
            else:
                return False

    def create_mods_section(self) -> bool:
        logger.info("Adding mods section...")
        self.lines.insert(len(self.lines) - 1, "\t{mods\n")
        self.lines.insert(len(self.lines) - 1, "\t}\n")
        return self.save()

    def get_mods(self) -> List[str]:
        if not self.is_mod_section_present():
            return []
        else:
            mods = []
            for elem in self.lines:
                match = re.match(r'^\t\t"mod_(\d+):0"\n$', elem)
                if match:
                    mods.append(match.group(1))
            return mods

    def clear_mods_section(self) -> bool:
        if not self.is_mod_section_present():
            return False
        else:
            self.lines = [
                line
                for line in self.lines
                if not re.match(r'^\t\t"(?:(mod_)?\d+):0"\n$', line)
            ]
            return self.save()

    def set_mods(self, mods: List[Mod]) -> bool:
        if not self.is_mod_section_present():
            return False
        else:
            self.clear_mods_section()
            mods_section_start = self.lines.index("\t{mods\n")
            index = mods_section_start + 1
            if len(mods) == 0:
                self.clear_mods_section()
            else:
                for mod in mods:
                    if mod.manualInstall:
                        self.lines.insert(index, f'\t\t"{mod.id}:0"\n')
                    else:
                        self.lines.insert(index, f'\t\t"mod_{mod.id}:0"\n')
                    index += 1
            return self.save()
