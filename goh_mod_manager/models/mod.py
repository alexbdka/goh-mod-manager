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

    def __str__(self):
        return f"{self.name}"
