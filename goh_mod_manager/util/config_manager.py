from pathlib import Path

from PySide6.QtCore import QSettings, QObject
from loguru import logger

from goh_mod_manager.util.steam_utils import get_goh_game_path


class ConfigManager(QObject):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("alex6", "GoH Mod Manager")
        self.first_run()

    # Getters
    def get_mods_directory(self):
        return self.settings.value("mods_directory", "")

    def get_game_directory(self):
        return self.settings.value("game_directory", "")

    def get_options_file(self):
        return self.settings.value("options_file", "")

    def get_presets(self):
        return self.settings.value("presets", {})

    def get_font(self):
        return self.settings.value("font", "")

    # Setters
    def set_mods_directory(self, path):
        self.settings.setValue("mods_directory", path)

    def set_game_directory(self, path):
        self.settings.setValue("game_directory", path)

    def set_options_file(self, path):
        self.settings.setValue("options_file", path)

    def set_presets(self, presets):
        self.settings.setValue("presets", presets)

    def set_font(self, font):
        self.settings.setValue("font", font)

    # Automatic search
    def first_run(self):
        if self.get_game_directory() == '':
            self.settings.setValue("game_directory", str(self.find_game_directory()))
            logger.info(f"Found game directory: {self.get_game_directory()}")

        if self.get_mods_directory() == '':
            self.settings.setValue("mods_directory", str(self.find_mods_directory()))
            logger.info(f"Found mods directory: {self.get_mods_directory()}")

        if self.get_options_file() == '':
            self.settings.setValue("options_file", str(self.find_options_file()))
            logger.info(f"Found options file: {self.get_options_file()}")

    @staticmethod
    def find_game_directory():
        return str(get_goh_game_path())

    def find_mods_directory(self):
        game_path = Path(self.get_game_directory())
        if not game_path.exists():
            return ""

        workshop_path = game_path.parent.parent / "workshop" / "content" / "400750"

        return str(workshop_path) if workshop_path.exists() else ""

    @staticmethod
    def find_options_file():
        possible_base_paths = [
            Path.home() / "Documents/My Games/gates of hell/profiles",
            Path.home() / "AppData/Local/digitalmindsoft/gates of hell/profiles",
        ]

        for base in possible_base_paths:
            if base.exists():
                # looking for a sub folder with a steam user id
                for sub in base.iterdir():
                    if sub.is_dir():
                        # just taking the first one
                        options_file = sub / "options.set"
                        if options_file.exists():
                            return str(options_file)
        return ""
