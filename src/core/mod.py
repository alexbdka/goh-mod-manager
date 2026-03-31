from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ModInfo:
    id: str
    name: str
    desc: str
    tags: List[str] = field(default_factory=list)
    minGameVersion: Optional[str] = None
    maxGameVersion: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    isLocal: bool = False
    hasShaders: bool = False
    path: str = ""
