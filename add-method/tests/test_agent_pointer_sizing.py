"""The installer pointer tells a non-skill reader the sizing rule — identically in both twins.

covers: task `direct-lane-size-gate` (S4 · S5). `_agent_pointer_block` / `agentPointerBlock` is the
only ADD text a Cursor/Codex/Copilot user reads before they act; without a sizing sentence it sends a
one-line fix into the full loop. The JS twin has no harness (see test_npm_pip_parity.py), so the JS
side is a text-invariant proof against the rendered Python block.
"""
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))
from add_method import _installer  # noqa: E402

SIZING_RE = re.compile(r"[^.\n]*3 adjacent files[^.\n]*\.")


def _py_block():
    return _installer._agent_pointer_block(_installer.AGENT_PROFILES[-1])


def _js():
    return (PKG / "bin" / "cli.js").read_text(encoding="utf-8")


def test_installer_pointer_twins_carry_identical_sizing_sentence():
    """covers: M6, A6, A12, E4, R:TWO_TREE."""
    block = _py_block()
    inner = block[len(_installer._GUIDE_BEGIN):block.find(_installer._GUIDE_END)]
    m = SIZING_RE.search(inner)
    assert m, "_installer.py pointer block: no sizing sentence naming '3 adjacent files' inside the markers"
    sentence = m.group(0).strip()
    assert re.search(r"security.{0,5}data.{0,5}architecture", inner, re.I), \
        "_installer.py pointer block: the closed floor is not named beside the sizing sentence"
    assert re.search(r"Task", inner), "_installer.py pointer block: no 'otherwise take a Task' fallback"
    js_src = _js()
    fn = js_src[js_src.find("function agentPointerBlock"):]
    fn = fn[:fn.find("\n}\n")]
    # the JS builds the block from string literals; the sentence must appear verbatim in one literal
    assert sentence in fn.replace('\\"', '"'), \
        f"cli.js agentPointerBlock: sizing sentence missing or differs from _installer.py: {sentence!r}"
    for verb in ("sync-guidelines", "add.py migrate", "add.py guide"):
        assert verb not in inner, f"_installer.py pointer block: names retired `{verb}`"
