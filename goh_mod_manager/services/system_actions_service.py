import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple


class SystemActionsService:
    def open_path(self, path: str | Path) -> Tuple[bool, str]:
        target = str(path)
        try:
            if sys.platform.startswith("win"):
                os.startfile(target)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
            return True, ""
        except Exception as e:
            return False, str(e)

    def open_url(self, url: str) -> Tuple[bool, str]:
        return self.open_path(url)
