from dataclasses import dataclass, field


@dataclass
class ModInfo:
    id: str
    name: str
    desc: str
    tags: list[str] = field(default_factory=list)
    minGameVersion: str | None = None
    maxGameVersion: str | None = None
    dependencies: list[str] = field(default_factory=list)
    isLocal: bool = False
    hasShaders: bool = False
    path: str = ""
    image_path: str | None = None
