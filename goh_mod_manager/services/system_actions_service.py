import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple


class SystemActionsService:
    @staticmethod
    def open_path(path: str | Path) -> Tuple[bool, str]:
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

    @staticmethod
    def launch_executable(
        exe_path: str | Path, working_dir: str | Path | None = None
    ) -> Tuple[bool, str]:
        """
        Launch an executable with an optional working directory.

        Args:
            exe_path: Path to the executable to launch
            working_dir: Working directory for the process (optional)

        Returns:
            (success, error_message)
        """
        target = str(exe_path)
        cwd = str(working_dir) if working_dir else None
        try:
            subprocess.Popen([target], cwd=cwd)
            return True, ""
        except Exception as e:
            return False, str(e)
