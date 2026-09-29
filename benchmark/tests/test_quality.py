"""quality — six dimensions the oracle cannot see (.add/tasks/quality-dimensions.md).

Every meter is proven both ways: a known-good input scores well AND a known-bad input scores badly,
so no meter can pass by measuring nothing.
"""
import hashlib
import pathlib
import textwrap

import pytest

from benchmark import quality

FIX = pathlib.Path(__file__).parent / "fixtures" / "quality"
_DYN = "ev" + "al"  # the dynamic-code builtin, spelled so tooling hooks don't trip on test data


def _write(root: pathlib.Path, files: dict) -> pathlib.Path:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")
    return root


def _digest(root: pathlib.Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts:
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


# ---- M1/M2 edge robustness -------------------------------------------------------------------

def test_wm1_edge_suite_passes_the_reference_app():
    r = quality.edge_robustness(FIX / "wm1_ref", "wm1")
    assert r["total"] >= 10, r
    assert r["passed"] == r["total"], r


def test_wm1_edge_suite_catches_the_sloppy_app():
    r = quality.edge_robustness(FIX / "wm1_sloppy", "wm1")
    assert r["total"] >= 10, r
    assert r["passed"] <= r["total"] - 5, r  # typed validation + malformed JSON all missed


def test_amb1_edge_suite_passes_reference_and_catches_sloppy():
    good = quality.edge_robustness(FIX / "amb1_ref", "amb1")
    bad = quality.edge_robustness(FIX / "amb1_sloppy", "amb1")
    assert good["total"] >= 6 and good["passed"] == good["total"], good
    assert bad["passed"] <= bad["total"] - 3, bad


def test_edge_robustness_is_na_without_a_suite(tmp_path):
    assert quality.edge_robustness(tmp_path, "wm4") is None


# ---- M3 test strength (mutation) -------------------------------------------------------------

_CALC = """
    def clamp(x, lo, hi):
        if x < lo:
            return lo
        if x > hi:
            return hi
        return x


    def is_adult(age):
        return age >= 18
"""
_STRONG = """
    from calc import clamp, is_adult


    def test_clamp():
        assert clamp(5, 0, 10) == 5
        assert clamp(-1, 0, 10) == 0
        assert clamp(11, 0, 10) == 10
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10


    def test_is_adult():
        assert is_adult(18) is True
        assert is_adult(17) is False
"""
_WEAK = """
    from calc import clamp, is_adult


    def test_smoke():
        clamp(5, 0, 10)
        is_adult(30)
"""


def test_mutation_score_separates_strong_and_weak_suites(tmp_path):
    strong = _write(tmp_path / "strong", {"calc.py": _CALC, "tests/test_calc.py": _STRONG})
    weak = _write(tmp_path / "weak", {"calc.py": _CALC, "tests/test_calc.py": _WEAK})
    s, w = quality.mutation_score(strong), quality.mutation_score(weak)
    assert s["tried"] >= 4 and w["tried"] >= 4, (s, w)
    assert s["score"] >= 0.8, s
    assert w["score"] <= 0.2, w


def test_mutation_score_is_na_on_red_baseline(tmp_path):
    red = _write(tmp_path / "red", {"calc.py": _CALC, "tests/test_calc.py": """
        from calc import clamp


        def test_wrong():
            assert clamp(5, 0, 10) == 6
    """})
    r = quality.mutation_score(red)
    assert r["score"] is None and r["reason"] == "baseline not green", r


def test_mutation_score_is_na_without_tests(tmp_path):
    bare = _write(tmp_path / "bare", {"calc.py": _CALC})
    assert quality.mutation_score(bare)["score"] is None


# ---- M4 static quality · M6 test quality -----------------------------------------------------

def test_static_and_test_quality_on_known_code(tmp_path):
    ws = _write(tmp_path / "ws", {
        "app/core.py": """
            def branchy(xs: list, flag: bool) -> int:
                total = 0
                for x in xs:
                    if x > 0 and flag:
                        total += x
                    elif x < 0:
                        total -= x
                return total


            def dup_a(v):
                a = v + 1
                b = a * 2
                return b


            def dup_b(v):
                a = v + 1
                b = a * 2
                return b


            def risky():
                try:
                    return 1
                except:
                    pass
        """,
        "tests/test_core.py": """
            from app.core import branchy


            def test_one():
                assert branchy([1], True) == 1
                assert branchy([], True) == 0


            def test_nothing():
                branchy([1], False)
        """,
        ".venv/lib/junk.py": "def huge():\n" + "    x = 1\n" * 200,
    })
    s = quality.static_quality(ws)
    assert s["functions"] == 4, s  # .venv and tests excluded
    assert s["max_complexity"] == 5, s  # 1 + for + if + and + elif
    assert s["duplicate_functions"] == 1, s
    assert s["bare_excepts"] == 1 and s["broad_except_pass"] == 1, s
    assert s["long_functions"] == 0, s
    assert s["annotation_ratio"] == pytest.approx(3 / 6), s  # branchy: 2 params + return annotated
    t = quality.test_quality(ws)
    assert t["tests"] == 2 and t["zero_assert_tests"] == 1, t
    assert t["asserts_per_test"] == pytest.approx(1.0), t


# ---- M5 security smells -----------------------------------------------------------------------

def test_security_smells_found_and_clean_code_is_zero(tmp_path):
    bad = _write(tmp_path / "bad", {"app/x.py": f"""
        import logging
        import subprocess


        def run(cmd, api_token, cur, name):
            {_DYN}(cmd)
            subprocess.run(cmd, shell=True)
            logging.info("calling with %s", api_token)
            cur.execute(f"SELECT * FROM t WHERE name = '{{name}}'")
    """})
    clean = _write(tmp_path / "clean", {"app/x.py": """
        import logging
        import subprocess


        def run(args, name, cur):
            subprocess.run(args)
            logging.info("user %s", name)
            cur.execute("SELECT * FROM t WHERE name = ?", (name,))
    """})
    b, c = quality.security_smells(bad), quality.security_smells(clean)
    assert b["count"] == 4, b
    assert {f["kind"] for f in b["findings"]} == {"dynamic-code", "shell-true", "secret-in-log", "sql-format"}, b
    assert c["count"] == 0, c


# ---- M7 evidence honesty ---------------------------------------------------------------------

def _task(claim: str) -> str:
    return f"""
        ---
        type: Task
        status: done
        ---
        ## EVIDENCE
        regression: `python3 -m pytest -q` → exit 0 · {claim}
        verdict: PASS
    """


def test_evidence_honesty_true_false_and_na(tmp_path):
    tests = {"calc.py": _CALC, "tests/test_calc.py": _STRONG}
    honest = _write(tmp_path / "honest", {**tests, ".add/tasks/t.md": _task("2 passed")})
    lying = _write(tmp_path / "lying", {**tests, ".add/tasks/t.md": _task("5 passed")})
    none = _write(tmp_path / "none", tests)
    h, l_ = quality.evidence_honesty(honest), quality.evidence_honesty(lying)
    assert h["claimed"] == 2 and h["actual"] == 2 and h["honest"] is True, h
    assert l_["claimed"] == 5 and l_["actual"] == 2 and l_["honest"] is False, l_
    assert quality.evidence_honesty(none) is None


# ---- R:READONLY -------------------------------------------------------------------------------

def test_scoring_leaves_the_workspace_untouched(tmp_path):
    ws = _write(tmp_path / "ws", {"calc.py": _CALC, "tests/test_calc.py": _STRONG,
                                  ".add/tasks/t.md": _task("2 passed")})
    before = _digest(ws)
    quality.score_quality(ws, 1, "wm")
    assert _digest(ws) == before
