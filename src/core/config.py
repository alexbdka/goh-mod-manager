from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AppConfig:
    """
    Represents the internal configuration of the Mod Manager.
    Stores the necessary paths to interact with the game and workshop.
    """

    game_path: Optional[str] = None
    workshop_path: Optional[str] = None
    profile_path: Optional[str] = None
    presets: Dict[str, List[str]] = field(default_factory=dict)
    language: str = "en_US"
    theme: str = "auto"
    font: str = "Inter"
