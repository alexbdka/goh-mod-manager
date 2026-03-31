import os
import pytest

from src.utils.gem_parser import parse_gem_file

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")


class TestOptionsSet:
    def test_parse_options_set(self):
        options_set_path = os.path.join(RESOURCES_DIR, "options.set")
        nodes = parse_gem_file(options_set_path)
        assert len(nodes) == 1

        options_node = nodes[0]
        assert options_node.name == "options"

        data = options_node.to_dict()
        assert "video" in data
        assert "sound" in data
        assert "game" in data
        assert "mods" in data

        assert data["video"]["adapter"] == "NVIDIA GeForce 256"
        assert data["video"]["resolution"]["custom_mode"] == "1280x720"
        assert data["video"]["resolution"]["mode"] == "desktop"

        assert data["game"]["difficulty"] == "easy"
        assert data["game"]["multiplayer"]["userName"] == "dummy"

        # Check if vertical_sync is treated as a boolean presence
        assert data["video"]["vertical_sync"]

        # Check mods list parsing
        assert "mod_2905667604:0" in data["mods"]
        assert "mod_2867922286:0" in data["mods"]


