import re
from pathlib import Path

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.mod_manager_logger import logger


class ModInfoParser:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.lines = []
        self.load()

    def load(self) -> bool:
        if not self.file_path.exists():
            logger.warning(f"{self.file_path} does not exist")
            return False
        else:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
            return True

    def parse(self) -> Mod:
        result = {
            "name": "",
            "desc": "",
            "minGameVersion": 0.0,
            "maxGameVersion": 0.0,
        }

        pattern = re.compile(
            r'\{\s*(name|desc|minGameVersion|maxGameVersion)\s+"?([^"}]+)"?\s*}'
        )

        for elem in self.lines:
            match = pattern.search(elem)
            if match:
                key, value = match.groups()
                result[key] = value

        mod_dir = self.file_path.parent
        imported_flag = mod_dir / ".imported_by_mod_manager"
        manual = imported_flag.exists()

        return Mod(
            id=self.file_path.parent.name,
            name=result["name"],
            desc=result["desc"],
            minGameVersion=result["minGameVersion"],
            maxGameVersion=result["maxGameVersion"],
            manualInstall=manual,
        )
