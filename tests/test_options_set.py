import os
from typing import cast

from src.utils.gem_parser import GemNodeValue, parse_gem_file

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")


class TestOptionsSet:
    def test_parse_options_set(self):
        options_set_path = os.path.join(RESOURCES_DIR, "options.set")
        nodes = parse_gem_file(options_set_path)
        assert len(nodes) == 1

        options_node = nodes[0]
        assert options_node.name == "options"

        data = cast(dict[str, GemNodeValue], options_node.to_dict())
        assert "video" in data
        assert "sound" in data
        assert "game" in data
        assert "mods" in data

        video = cast(dict[str, GemNodeValue], data["video"])
        game = cast(dict[str, GemNodeValue], data["game"])
        mods = cast(list[str], data["mods"])
        resolution = cast(dict[str, GemNodeValue], video["resolution"])
        multiplayer = cast(dict[str, GemNodeValue], game["multiplayer"])

        assert video["adapter"] == "NVIDIA GeForce 256"
        assert resolution["custom_mode"] == "1280x720"
        assert resolution["mode"] == "desktop"

        assert game["difficulty"] == "easy"
        assert multiplayer["userName"] == "dummy"

        # Check if vertical_sync is treated as a boolean presence
        assert video["vertical_sync"] is True

        # Check mods list parsing
        assert "mod_2905667604:0" in mods
        assert "mod_2867922286:0" in mods
