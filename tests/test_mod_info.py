import os
from typing import cast

from src.utils.gem_parser import GemNodeValue, parse_gem_file

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")


class TestModInfo:
    def test_parse_mod_info(self):
        mod_info_path = os.path.join(RESOURCES_DIR, "mod.info")
        nodes = parse_gem_file(mod_info_path)
        assert len(nodes) == 1

        mod_node = nodes[0]
        assert mod_node.name == "mod"

        data = cast(dict[str, GemNodeValue], mod_node.to_dict())
        assert "name" in data
        name = cast(str, data["name"])
        assert "GOH ARm" in name
        assert data["minGameVersion"] == "1.061"
        assert data["maxGameVersion"] == "1.061"
        assert data["require"] == "mod_2905667604"
