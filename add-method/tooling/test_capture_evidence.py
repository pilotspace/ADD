"""Red suite for capture-evidence (udd-design-loop 3/4).

Frozen contract §3 @ v1:
  - NEW pure helper `add._missing_captures(root) -> list[str]` — prototype <name>s under
    `.add/design/prototypes/*.json` with NO capture file `.add/design/captures/<name>.<ext>`
    (ext ∈ png·svg·jpg·jpeg·webp). Pure · total (never raises) · read-only · document(sorted) order.
  - `add.py check` maps each returned name to a never-red WARN `missing_capture` on the EXISTING
    `warnings` array — never feeds `failed`, read-only, exit-1-iff-failed preserved; silent-when-absent.
  - the convention is DOCUMENTED in design.md (×3 skill trees) + udd-wireframe.md (×2 template trees):
    captures live at `.add/design/captures/<name>.<ext>`, attached/mentioned in the feature's TASK.md,
    `@json-render/image` (Satori → PNG/SVG) the recommended default, engine never renders.
  - DEMONSTRATED: a captured image is referenced from this task's TASK.md (exit-criterion 4).
  - ship discipline: 3 add.py copies byte-identical + the engine pin == md5(add.py).

RED before build: AttributeError (_missing_captures missing) · cmd_check emits no missing_capture ·
the doc lines + the TASK.md capture reference absent.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add
import engine_pin

_TOOLING = Path(__file__).resolve().parent
_REPO = _TOOLING.parent.parent                       # AIDD-Book/
_DESIGN_MD = _TOOLING.parent / "skill" / "add" / "design.md"
_WIREFRAME_MD = _TOOLING / "templates" / "udd-wireframe.md"
_TASK_MD = _REPO / ".add" / "tasks" / "capture-evidence" / "TASK.md"

# the 3 add.py copies that must stay byte-identical (mirrors test_argv_portability)
_ADDPY = (
    _TOOLING / "add.py",
    _TOOLING.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
)

_PROTO = {"root": "s", "elements": {"s": {"type": "Screen", "props": {}}}}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ---------------------------------------------------------------------------
# the pure helper
# ---------------------------------------------------------------------------
class MissingCapturesHelperTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-capture-"))
        self.add = self.tmp / ".add"
        self.proto = self.add / "design" / "prototypes"
        self.caps = self.add / "design" / "captures"
        self.proto.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _proto(self, name):
        (self.proto / f"{name}.json").write_text(json.dumps(_PROTO), encoding="utf-8")

    def _cap(self, name, ext="png"):
        self.caps.mkdir(parents=True, exist_ok=True)
        (self.caps / f"{name}.{ext}").write_bytes(b"\x89PNG\r\n")

    def test_uncaptured_prototype_is_listed(self):
        self._proto("welcome")
        self.assertEqual(add._missing_captures(self.add), ["welcome"])

    def test_capture_present_clears(self):
        self._proto("welcome")
        self._cap("welcome", "png")
        self.assertEqual(add._missing_captures(self.add), [])

    def test_any_allowed_ext_clears(self):
        for name, ext in (("a", "svg"), ("b", "jpg"), ("c", "jpeg"), ("d", "webp")):
            self._proto(name)
            self._cap(name, ext)
        self.assertEqual(add._missing_captures(self.add), [])

    def test_no_design_is_empty(self):
        shutil.rmtree(self.add / "design")
        self.assertEqual(add._missing_captures(self.add), [])

    def test_pure_total_and_sorted(self):
        for n in ("zeta", "alpha", "mu"):
            self._proto(n)
        (self.proto / "notes.txt").write_text("not json", encoding="utf-8")   # odd entry
        self.caps.mkdir(parents=True, exist_ok=True)
        (self.caps / "stray.png").write_bytes(b"x")                            # capture with no prototype
        before = sorted(p.name for p in (self.add / "design").rglob("*"))
        result = add._missing_captures(self.add)
        self.assertEqual(result, ["alpha", "mu", "zeta"], "document(sorted) order, .txt ignored")
        after = sorted(p.name for p in (self.add / "design").rglob("*"))
        self.assertEqual(before, after, "read-only — the helper writes nothing")

    def test_engine_renders_never(self):
        """The engine MEASURES presence; it must not render/produce a capture."""
        self._proto("welcome")
        self.assertEqual(add._missing_captures(self.add), ["welcome"])
        self.assertFalse(self.caps.exists(),
                         "engine_renders: the check must not create a captures dir / image")


# ---------------------------------------------------------------------------
# cmd_check integration over a temp .add/design/
# ---------------------------------------------------------------------------
class CheckMissingCaptureTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-capture-check-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo", "--stage", "mvp"])
        self.design = Path(self.tmp) / ".add" / "design"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _proto(self, name):
        d = self.design / "prototypes"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.json").write_text(json.dumps(_PROTO), encoding="utf-8")

    def _cap(self, name, ext="png"):
        d = self.design / "captures"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.{ext}").write_bytes(b"\x89PNG\r\n")

    def _check(self):
        buf = io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(["check"])
        except SystemExit as e:
            code = e.code or 0
        return code, buf.getvalue()

    def _check_json(self):
        buf = io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(["check", "--json"])
        except SystemExit as e:
            code = e.code or 0
        return code, json.loads(buf.getvalue())

    def test_missing_capture_warns_never_red(self):
        self._proto("welcome")
        code, out = self._check()
        self.assertIn("missing_capture", out)
        self.assertIn("welcome", out)
        self.assertEqual(code, 0, "missing_capture is a WARN — never red")

    def test_capture_present_no_warn(self):
        self._proto("welcome")
        self._cap("welcome", "png")
        code, out = self._check()
        self.assertNotIn("missing_capture", out)
        self.assertEqual(code, 0)

    def test_silent_when_no_design(self):
        code, out = self._check()
        self.assertNotIn("missing_capture", out)
        self.assertEqual(code, 0, out)

    def test_noisy_when_absent_guard(self):
        """A design/ with tokens but no prototypes/ → no missing_capture WARN."""
        self.design.mkdir(parents=True, exist_ok=True)
        (self.design / "tokens.json").write_text(json.dumps(
            {"primitive": {"color": {"$type": "color", "b": {"$value": "#3B82F6"}}}}), encoding="utf-8")
        code, out = self._check()
        self.assertNotIn("missing_capture", out)

    def test_capture_blocks_guard_json(self):
        """missing_capture rides `warnings`, never `failed` — exit stays 0."""
        self._proto("welcome")
        code, payload = self._check_json()
        self.assertEqual(code, 0)
        names = [w["name"] for w in payload.get("warnings", [])]
        self.assertIn("missing_capture", names)
        check_names = [c["name"] for c in payload.get("checks", [])]
        self.assertFalse(any("capture" in n for n in check_names),
                         "capture_blocks: capture must not be a `checks` entry that can fail")


# ---------------------------------------------------------------------------
# the documented + demonstrated convention
# ---------------------------------------------------------------------------
class CaptureConventionDocTest(unittest.TestCase):
    def test_convention_documented(self):
        for p in (_DESIGN_MD, _WIREFRAME_MD):
            t = _text(p)
            self.assertIn(".add/design/captures", t, f"{p.name} must name the capture location")
            self.assertIn("TASK.md", t, f"{p.name} must say the capture is attached to TASK.md")
            self.assertIn("@json-render/image", t, f"{p.name} must name the @json-render/image default")
        self.assertIn("never render", _text(_DESIGN_MD).lower(),
                      "design.md must keep the engine render-free")

    def test_demonstrated_in_task_md(self):
        # the committed demonstration capture(s) actually exist in the repo (the frozen decision)
        caps_dir = _REPO / ".add" / "design" / "captures"
        caps = [c for c in caps_dir.glob("*") if c.is_file()] if caps_dir.is_dir() else []
        self.assertTrue(
            any(c.suffix.lstrip(".").lower() in ("png", "svg", "jpg", "jpeg", "webp") for c in caps),
            "a real design-confirm capture must be committed under .add/design/captures/")
        # …and the §6 EVIDENCE of THIS task references one — scoped to §6 so an incidental
        # mention in the §4 test plan cannot vacuously satisfy it.
        t = _text(_TASK_MD)
        s6 = t.split("## 6 ")[-1].split("## 7 ")[0] if "## 6 " in t else ""
        self.assertRegex(s6, r"captures/[\w.-]+\.(png|svg|jpg|jpeg|webp)",
                         "§6 EVIDENCE must reference the committed capture image")


# ---------------------------------------------------------------------------
# ship discipline — 3 copies byte-identical + the pin re-aimed
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
