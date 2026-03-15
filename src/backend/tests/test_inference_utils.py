import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ml"))

from app.scripts.inference import _strip_hex


class TestStripHex:
    def test_short_label_unchanged(self):
        assert _strip_hex("cat") == "cat"

    def test_exactly_32_unchanged(self):
        label = "a" * 32
        assert _strip_hex(label) == label

    def test_strips_32_char_prefix(self):
        prefix = "0123456789abcdef" * 2  # 32 chars
        assert _strip_hex(prefix + "real_label") == "real_label"

    def test_empty_string(self):
        assert _strip_hex("") == ""

    def test_long_hex_prefix(self):
        hex_prefix = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"  # 32 chars
        assert _strip_hex(hex_prefix + "Signal_5") == "Signal_5"
