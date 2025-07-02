from dataclasses import dataclass


@dataclass
class Mod:
    id: str
    name: str
    desc: str
    minGameVersion: float
    maxGameVersion: float
    manualInstall: bool

    def __str__(self):
        return f"{self.name} [{self.id}]"
