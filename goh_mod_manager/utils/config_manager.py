from PySide6.QtCore import QSettings


class ConfigManager:
    def __init__(self):
        self.settings = QSettings("alex6", "GoH Mod Manager")

    def get_mods_directory(self):
        return self.settings.value("mods_directory", "")

    def get_options_file(self):
        return self.settings.value("options_file", "")

    def get_presets(self):
        return self.settings.value("presets", {})

    def get_font(self):
        return self.settings.value("font", "")

    def set_mods_directory(self, path):
        self.settings.setValue("mods_directory", path)

    def set_options_file(self, path):
        self.settings.setValue("options_file", path)

    def set_presets(self, presets):
        self.settings.setValue("presets", presets)

    def set_font(self, font):
        self.settings.setValue("font", font)
