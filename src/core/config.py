from dataclasses import dataclass, field


@dataclass
class AppConfig:
    """
    Represents the internal configuration of the Mod Manager.
    Stores the necessary paths to interact with the game and workshop.
    """

    game_path: str | None = None
    workshop_path: str | None = None
    profile_path: str | None = None
    presets: dict[str, list[str]] = field(default_factory=dict)
    language: str = "en_US"
    theme: str = "auto"
    font: str = "Inter"
    onboarding_seen: bool = False
