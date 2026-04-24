import base64
import json
import zlib

import pytest
from src.core.exceptions import InvalidShareCodeError
from src.core.mod import ModInfo
from src.services.share_code_service import ShareCodeService


class TestShareCodeService:
    def setup_method(self):
        self.service = ShareCodeService()
        self.mods = [
            ModInfo(id="2867922286", name="GOH ARm", desc=""),
            ModInfo(id="2905667604", name="MACE", desc=""),
        ]

    def test_encode_and_decode(self):
        # Encode
        code = self.service.encode(self.mods)
        assert len(code) > 0
        assert isinstance(code, str)

        # Decode
        decoded_data = self.service.decode(code)
        assert len(decoded_data) == 2

        assert decoded_data[0]["id"] == "2867922286"
        assert decoded_data[0]["name"] == "GOH ARm"

        assert decoded_data[1]["id"] == "2905667604"
        assert decoded_data[1]["name"] == "MACE"

    def test_decode_invalid_code(self):
        with pytest.raises(InvalidShareCodeError):
            self.service.decode("This is definitely not a base64 zlib string!")

    def test_decode_rejects_malformed_legacy_entries(self):
        payload = ["2867922286"]
        code = base64.b64encode(
            zlib.compress(json.dumps(payload).encode("utf-8"))
        ).decode("utf-8")

        with pytest.raises(InvalidShareCodeError):
            self.service.decode(code)

    def test_decode_rejects_non_string_mod_fields(self):
        payload = {"mods": [{"id": 2867922286, "name": "GOH ARm"}]}
        code = base64.b64encode(
            zlib.compress(json.dumps(payload).encode("utf-8"))
        ).decode("utf-8")

        with pytest.raises(InvalidShareCodeError):
            self.service.decode(code)

    def test_resolve_mods_all_found(self):
        decoded_data = [
            {"id": "2867922286", "name": "GOH ARm"},
            {"id": "2905667604", "name": "MACE"},
        ]

        found, missing = self.service.resolve_mods(decoded_data, self.mods)

        assert len(found) == 2
        assert len(missing) == 0
        assert found[0].id == "2867922286"
        assert found[1].id == "2905667604"

    def test_resolve_mods_some_missing(self):
        decoded_data = [
            {"id": "2867922286", "name": "GOH ARm"},
            {"id": "9999999999", "name": "Unknown Ghost Mod"},
        ]

        found, missing = self.service.resolve_mods(decoded_data, self.mods)

        assert len(found) == 1
        assert found[0].id == "2867922286"

        assert len(missing) == 1
        assert missing[0]["id"] == "9999999999"
        assert missing[0]["name"] == "Unknown Ghost Mod"
