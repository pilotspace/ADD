"""The measured section reads as ADD's values beside vanilla's (owner, 2026-10-07)."""
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
READMES = (PKG.parent / "README.md", PKG / "README.md")


def test_measured_table_is_values_side_by_side():
    for path in READMES:
        text = path.read_text(encoding="utf-8")
        section = text.split("## Measured on 4.0", 1)[1].split("## When vanilla Claude", 1)[0]
        assert "| what you get | vanilla Claude Code | Claude Code + ADD |" in section, path
        for value in ("Fixes that land", "Verified before it ships", "Ships with a test",
                      "Guesses you can review", "Claims you can trust", "you pay"):
            assert f"**{value}" in section, f"{path}: no {value!r} row"
