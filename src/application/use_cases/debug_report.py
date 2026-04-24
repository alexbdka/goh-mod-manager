import datetime
import platform

from src.application.queries import ApplicationQueryService
from src.utils import app_paths


class ApplicationDebugReportUseCase:
    """
    Builds a text debug report independently from any UI framework.
    """

    def __init__(self, query_service: ApplicationQueryService):
        self._query_service = query_service

    def build(self) -> str:
        lines = [
            "--- GoH Mod Manager Debug Report ---",
            f"Generated at: {datetime.datetime.now()}",
            f"OS: {platform.system()} {platform.release()} ({platform.version()})",
            f"App Version: {app_paths.read_version()}",
            "",
            "--- Configuration ---",
        ]

        settings = self._query_service.get_settings_state()
        lines.extend(
            [
                f"Game Path: {settings.game_path}",
                f"Workshop Path: {settings.workshop_path}",
                f"Profile Path: {settings.profile_path}",
                "",
                "--- Catalogue Stats ---",
            ]
        )

        catalogue = self._query_service.get_catalogue_state()
        local_mods = [mod for mod in catalogue.items if mod.is_local]
        workshop_mods = [mod for mod in catalogue.items if not mod.is_local]
        lines.extend(
            [
                f"Total Installed Mods: {len(catalogue.items)}",
                f"Local Mods: {len(local_mods)}",
                f"Workshop Mods: {len(workshop_mods)}",
                "",
                "--- Active Mods Load Order ---",
            ]
        )

        active_mods = self._query_service.get_active_mods_state()
        if not active_mods.items:
            lines.append("No active mods.")
        else:
            for mod in active_mods.items:
                mod_type = "Local" if mod.is_local else "Workshop"
                load_order = mod.load_order if mod.load_order is not None else "?"
                lines.append(f"{load_order}. {mod.name} (ID: {mod.id}) - {mod_type}")

        lines.extend(["", "--- Recent Logs (Last 100 Lines) ---"])
        lines.extend(self._read_recent_log_lines())
        return "\n".join(lines) + "\n"

    @staticmethod
    def _read_recent_log_lines() -> list[str]:
        log_path = app_paths.get_log_file_path()
        if not log_path.exists():
            return ["No log file found."]

        with open(log_path, encoding="utf-8") as log_file:
            return [line.rstrip("\n") for line in log_file.readlines()[-100:]]
