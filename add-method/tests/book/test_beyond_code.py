"""BEYOND-CODE.md's checker, ledger and red transcript are real: run them.

The walkthrough says a twenty-line script is the whole test runner a month-end close needs, and
shows what it prints before the close is done. That is only honest if the script on the page runs
and prints exactly that. This extracts the marked blocks, runs the checker against the page's
ledger (it must pass), against the pre-close ledger (it must print the page's red transcript), and
against a variance past the materiality line the rule sealed (it must fail).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]
PAGE = PKG / "BEYOND-CODE.md"


def _block(marker: str) -> str:
    text = PAGE.read_text(encoding="utf-8")
    m = re.search(rf"<!-- {marker} -->\s*```\w*\n(.*?)```", text, re.S)
    assert m, f"BEYOND-CODE.md has no `<!-- {marker} -->` code block"
    return m.group(1)


def _run(tmp_path: Path, ledger: dict) -> subprocess.CompletedProcess:
    (tmp_path / "checks").mkdir(exist_ok=True)
    (tmp_path / "checks" / "close.py").write_text(_block("recon-checker"), encoding="utf-8")
    (tmp_path / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    return subprocess.run([sys.executable, "checks/close.py"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=30)


def test_the_page_ledger_passes_its_own_checker(tmp_path):
    proc = _run(tmp_path, json.loads(_block("recon-data")))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.count("PASS ") == 2, proc.stdout


def test_the_red_transcript_is_what_the_checker_prints(tmp_path):
    """Before the close, line v2 has no source document — the page shows that run's output."""
    ledger = json.loads(_block("recon-data"))
    ledger["lines"][1]["source_doc"] = ""
    proc = _run(tmp_path, ledger)
    assert proc.returncode == 1
    shown = [line for line in _block("recon-red").splitlines() if not line.startswith("$ ")]
    assert proc.stdout.splitlines() == shown, proc.stdout


def test_a_variance_past_materiality_fails(tmp_path):
    ledger = json.loads(_block("recon-data"))
    ledger["variance"] = int(ledger["gross"] * 0.005) + 1
    assert _run(tmp_path, ledger).returncode == 1


def test_the_check_names_on_the_page_match_the_checker():
    checks, checker = _block("recon-checks"), _block("recon-checker")
    names = re.findall(r"test_\w+", checks)
    assert len(names) == 2, f"expected two sealed checks on the page, found {names}"
    for name in names:
        assert f'"{name}"' in checker, f"CHECKS names {name}, which the checker never reports"
