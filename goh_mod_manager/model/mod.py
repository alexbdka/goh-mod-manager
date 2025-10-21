from dataclasses import dataclass


@dataclass
class Mod:
    id: str
    name: str
    desc: str
    minGameVersion: str
    maxGameVersion: str
    folderPath: str
    manualInstall: bool
    require: str

    def __str__(self):
        return f"{self.name}"
