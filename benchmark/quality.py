"""quality — six code-quality dimensions the oracle cannot see (.add/tasks/quality-dimensions.md).

The oracle only asks "does the spec'd behaviour work?". These meters ask what a reviewer asks next:
does it hold at the edges the spec implies (held-out edge suite), would its own tests catch a bug
(mutation score), is it maintainable (static), is it safe (security smells), are the tests real
(test quality), and — for ADD — is the recorded EVIDENCE true (evidence honesty)?

Stdlib + pytest only. A run's workspace is never written: anything that executes code runs in a
temp copy. `python -m benchmark.quality <run dir|runs root>…` writes quality.json beside each
record.json and prints a table.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import random
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = REPO_ROOT / "benchmark" / "workload"
SKIP_DIRS = {".venv", "venv", "env", ".git", ".add", "__pycache__", "node_modules", ".pytest_cache",
             ".mypy_cache", ".claude", ".specify", "site-packages", "build", "dist"}
TEST_DIRS = {"tests", "test"}
SUITE_TIMEOUT_S = 60
LONG_FUNCTION_LINES = 50

_PASSED = re.compile(r"(\d+) passed")
_RAN = re.compile(r"Ran (\d+) tests?")
_CLAIM = re.compile(r"(\d+)\s+(?:passed|tests?\b)")
_SECRET = re.compile(r"(token|secret|passw(or)?d|api_?key|credential)", re.I)
_LOG_METHODS = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
_DYNAMIC = {"ev" + "al", "ex" + "ec"}
_UNSAFE_LOADERS = {"pick" + "le", "mar" + "shal", "di" + "ll", "shel" + "ve"}


# ---- file discovery ---------------------------------------------------------------------------

def _walk_py(workspace: pathlib.Path):
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if f.endswith(".py"):
                yield pathlib.Path(root) / f


def _is_test(path: pathlib.Path, workspace: pathlib.Path) -> bool:
    rel = path.relative_to(workspace)
    return (any(p in TEST_DIRS for p in rel.parts[:-1]) or rel.name.startswith("test_")
            or rel.name.endswith("_test.py") or rel.name == "conftest.py")


def app_files(workspace: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in _walk_py(workspace) if not _is_test(p, workspace))


def test_files(workspace: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in _walk_py(workspace) if _is_test(p, workspace))


def _parse(path: pathlib.Path):
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


def _copy(workspace: pathlib.Path) -> pathlib.Path:
    dest = pathlib.Path(tempfile.mkdtemp(prefix="bench-quality-")) / "ws"
    shutil.copytree(workspace, dest, symlinks=True,
                    ignore=shutil.ignore_patterns(".venv", "venv", ".git", "__pycache__", ".pytest_cache",
                                                  "node_modules"))
    return dest


def _run_suite(cwd: pathlib.Path, argv: list[str] | None = None, timeout: float = SUITE_TIMEOUT_S):
    argv = argv or [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(cwd)}
    env.pop("BENCH_WORKSPACE", None)
    try:
        proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, ""
    return proc.returncode, proc.stdout + proc.stderr


# ---- M1/M2 edge robustness --------------------------------------------------------------------

def edge_robustness(workspace: pathlib.Path, workload: str) -> dict | None:
    suite = WORKLOADS / workload / "edge"
    if not suite.is_dir():
        return None
    report = pathlib.Path(tempfile.mkdtemp(prefix="bench-edge-")) / "report.xml"
    env = {**os.environ, "BENCH_WORKSPACE": str(pathlib.Path(workspace).resolve()),
           "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(suite),
                    f"--junitxml={report}"], cwd=REPO_ROOT, env=env, capture_output=True, text=True,
                   timeout=300)
    failed: list[str] = []
    total = 0
    if report.exists():
        import xml.etree.ElementTree as ET
        for case in ET.parse(report).getroot().iter("testcase"):
            total += 1
            if case.find("failure") is not None or case.find("error") is not None:
                failed.append(case.get("name", "?"))
    shutil.rmtree(report.parent, ignore_errors=True)
    return {"passed": total - len(failed), "total": total,
            "rate": round((total - len(failed)) / total, 3) if total else None, "failed": failed}


# ---- M3 test strength (mutation) --------------------------------------------------------------

_SWAP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq,
         ast.NotEq: ast.Eq, ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Is: ast.IsNot, ast.IsNot: ast.Is,
         ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv, ast.And: ast.Or, ast.Or: ast.And}


def _sites(tree: ast.AST) -> list[tuple[int, str]]:
    """Every mutable site as (node index in ast.walk order, operator label)."""
    out = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and type(node.ops[0]) in _SWAP:
            out.append((i, "compare"))
        elif isinstance(node, (ast.BinOp, ast.AugAssign)) and type(node.op) in _SWAP:
            out.append((i, "arith"))
        elif isinstance(node, ast.BoolOp) and type(node.op) in _SWAP:
            out.append((i, "bool"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            out.append((i, "const-bool"))
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            out.append((i, "const-int"))
        elif isinstance(node, ast.Return) and node.value is not None and not (
                isinstance(node.value, ast.Constant) and node.value.value is None):
            out.append((i, "return-none"))
    return out


def _mutate(source: str, index: int) -> str | None:
    tree = ast.parse(source)
    for i, node in enumerate(ast.walk(tree)):
        if i != index:
            continue
        if isinstance(node, ast.Compare):
            node.ops[0] = _SWAP[type(node.ops[0])]()
        elif isinstance(node, (ast.BinOp, ast.AugAssign, ast.BoolOp)):
            node.op = _SWAP[type(node.op)]()
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            node.value = not node.value
        elif isinstance(node, ast.Constant) and type(node.value) is int:
            node.value = node.value + 1
        elif isinstance(node, ast.Return):
            node.value = ast.Constant(value=None)
        else:
            return None
        return ast.unparse(ast.fix_missing_locations(tree))
    return None


def mutation_score(workspace: pathlib.Path, cap: int = 24, seed: int = 0) -> dict:
    workspace = pathlib.Path(workspace)
    if not test_files(workspace):
        return {"score": None, "reason": "no tests", "tried": 0, "killed": 0}
    copy = _copy(workspace)
    try:
        code, _ = _run_suite(copy)
        if code != 0:
            return {"score": None, "reason": "baseline not green", "tried": 0, "killed": 0}
        candidates = []
        for path in app_files(copy):
            if path.name == "__init__.py":
                continue
            tree = _parse(path)
            if tree is not None:
                candidates += [(path, i, label) for i, label in _sites(tree)]
        rng = random.Random(seed)
        picked = sorted(rng.sample(candidates, min(cap, len(candidates))), key=lambda c: (str(c[0]), c[1]))
        killed, survivors = 0, []
        for path, index, label in picked:
            original = path.read_text(encoding="utf-8")
            mutant = _mutate(original, index)
            if mutant is None:
                continue
            path.write_text(mutant, encoding="utf-8")
            try:
                code, _ = _run_suite(copy)
            finally:
                path.write_text(original, encoding="utf-8")
            if code != 0:  # a failing or hanging suite killed the mutant
                killed += 1
            else:
                survivors.append(f"{path.relative_to(copy)}:{label}")
        tried = len(picked)
        return {"score": round(killed / tried, 3) if tried else None,
                "reason": "" if tried else "no mutable code", "tried": tried, "killed": killed,
                "survivors": survivors[:10]}
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)


# ---- M4 static quality ------------------------------------------------------------------------

def _complexity(fn: ast.AST) -> int:
    score = 1
    for node in ast.walk(fn):
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler,
                             ast.comprehension)):
            score += 1 + (len(node.ifs) if isinstance(node, ast.comprehension) else 0) - (
                1 if isinstance(node, ast.comprehension) else 0)
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.match_case):
            score += 1
    return score


def _functions(tree: ast.AST):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def static_quality(workspace: pathlib.Path) -> dict:
    workspace = pathlib.Path(workspace)
    loc, fns, complexities, long_fns, bare, broad_pass = 0, 0, [], 0, 0, 0
    annotated = slots = 0
    bodies: dict[str, int] = {}
    for path in app_files(workspace):
        text = path.read_text(encoding="utf-8", errors="replace")
        loc += sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
        tree = _parse(path)
        if tree is None:
            continue
        for fn in _functions(tree):
            fns += 1
            complexities.append(_complexity(fn))
            if (fn.end_lineno or fn.lineno) - fn.lineno + 1 > LONG_FUNCTION_LINES:
                long_fns += 1
            args = [a for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs
                    if a.arg not in ("self", "cls")]
            slots += len(args) + 1
            annotated += sum(1 for a in args if a.annotation is not None) + (fn.returns is not None)
            if len(fn.body) >= 3:
                key = hashlib.sha1("".join(ast.dump(s) for s in fn.body).encode()).hexdigest()
                bodies[key] = bodies.get(key, 0) + 1
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                broad = node.type is None or (isinstance(node.type, ast.Name)
                                              and node.type.id in ("Exception", "BaseException"))
                bare += node.type is None
                broad_pass += broad and len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
    return {"app_loc": loc, "functions": fns,
            "max_complexity": max(complexities, default=0),
            "mean_complexity": round(sum(complexities) / len(complexities), 2) if complexities else 0.0,
            "long_functions": long_fns,
            "duplicate_functions": sum(n - 1 for n in bodies.values() if n > 1),
            "annotation_ratio": round(annotated / slots, 3) if slots else 0.0,
            "bare_excepts": bare, "broad_except_pass": broad_pass}


# ---- M6 test quality --------------------------------------------------------------------------

def _asserts(fn: ast.AST) -> int:
    n = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            n += 1
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
            if name.startswith("assert") or name in ("raises", "fail"):
                n += 1
    return n


def test_quality(workspace: pathlib.Path) -> dict:
    workspace = pathlib.Path(workspace)
    tests, zero, total_asserts, test_loc = 0, 0, 0, 0
    for path in test_files(workspace):
        text = path.read_text(encoding="utf-8", errors="replace")
        test_loc += sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
        tree = _parse(path)
        if tree is None:
            continue
        for fn in _functions(tree):
            if fn.name.startswith("test"):
                tests += 1
                a = _asserts(fn)
                total_asserts += a
                zero += a == 0
    app_loc = static_quality(workspace)["app_loc"]
    return {"tests": tests, "zero_assert_tests": zero,
            "asserts_per_test": round(total_asserts / tests, 2) if tests else 0.0,
            "test_to_app_loc": round(test_loc / app_loc, 2) if app_loc else 0.0}


# ---- M5 security smells -----------------------------------------------------------------------

def _names_in(node: ast.AST) -> list[str]:
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.append(n.id)
        elif isinstance(n, ast.Attribute):
            out.append(n.attr)
    return out


def security_smells(workspace: pathlib.Path) -> dict:
    workspace = pathlib.Path(workspace)
    findings = []

    def add(kind, path, node):
        findings.append({"kind": kind, "at": f"{path.relative_to(workspace)}:{node.lineno}"})

    for path in app_files(workspace):
        tree = _parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            fname = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
            owner = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else ""
            if isinstance(f, ast.Name) and fname in _DYNAMIC:
                add("dynamic-code", path, node)
            if any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                   for k in node.keywords):
                add("shell-true", path, node)
            if fname in ("load", "loads") and owner in _UNSAFE_LOADERS:
                add("unsafe-deserialize", path, node)
            if fname == "load" and owner == "yaml" and not any(
                    k.arg == "Loader" and "Safe" in ast.unparse(k.value) for k in node.keywords):
                add("unsafe-deserialize", path, node)
            if fname in ("execute", "executemany") and node.args and (
                    isinstance(node.args[0], ast.JoinedStr)
                    or (isinstance(node.args[0], ast.BinOp) and isinstance(node.args[0].op, (ast.Mod, ast.Add)))
                    or (isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Attribute)
                        and node.args[0].func.attr == "format")):
                add("sql-format", path, node)
            is_log = (fname in _LOG_METHODS and owner.lower() in ("logging", "log", "logger", "_log", "_logger")) \
                or fname == "print"
            if is_log and any(_SECRET.search(n) for a in node.args[1 if fname != "print" else 0:]
                              for n in _names_in(a)):
                add("secret-in-log", path, node)
    return {"count": len(findings), "findings": findings}


# ---- M7 evidence honesty ----------------------------------------------------------------------

def _claims(workspace: pathlib.Path) -> list[tuple[str, int]]:
    out = []
    for task in sorted((workspace / ".add" / "tasks").glob("*.md")):
        text = task.read_text(encoding="utf-8", errors="replace")
        evidence = text.split("## EVIDENCE", 1)[1] if "## EVIDENCE" in text else ""
        for line in evidence.splitlines():
            if line.strip().lower().startswith("regression:"):
                cmd = re.search(r"`([^`]+)`", line)
                count = _CLAIM.search(line)
                if cmd and count:
                    out.append((cmd.group(1), int(count.group(1))))
    return out


def evidence_honesty(workspace: pathlib.Path) -> dict | None:
    workspace = pathlib.Path(workspace)
    claims = _claims(workspace)
    if not claims:
        return None
    cmd, claimed = claims[-1]  # the latest task's regression claim is the one the tree must hold
    copy = _copy(workspace)
    try:
        try:
            argv = shlex.split(cmd)
        except ValueError:
            return {"claimed": claimed, "actual": None, "honest": None, "command": cmd}
        if argv and argv[0] in ("python", "python3"):
            argv[0] = sys.executable
        if any(tok in ("&&", "|", ";", "cd") for tok in argv):  # a shell pipeline: rerun the suite plainly
            argv = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
        code, out = _run_suite(copy, argv, timeout=180)
        m = _PASSED.search(out) or _RAN.search(out)
        actual = int(m.group(1)) if m else None
        return {"claimed": claimed, "actual": actual, "honest": actual == claimed if actual is not None else None,
                "command": cmd, "exit": code}
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)


# ---- aggregate + CLI --------------------------------------------------------------------------

def score_quality(workspace: pathlib.Path, wm: int, family: str) -> dict:
    workspace = pathlib.Path(workspace)
    return {"edge": edge_robustness(workspace, f"{family}{wm}"),
            "mutation": mutation_score(workspace),
            "static": static_quality(workspace),
            "security": security_smells(workspace),
            "tests": test_quality(workspace),
            "evidence": evidence_honesty(workspace)}


def _runs(paths: list[str]):
    for p in paths:
        for record in sorted(pathlib.Path(p).rglob("record.json")):
            ws = record.parent / "workspace"
            if ws.is_dir():
                yield record, ws


def _fmt(q: dict) -> str:
    e, m, s, sec, t, ev = q["edge"], q["mutation"], q["static"], q["security"], q["tests"], q["evidence"]
    edge = f"{e['passed']}/{e['total']}" if e else "n/a"
    mut = f"{m['score']:.2f} ({m['killed']}/{m['tried']})" if m.get("score") is not None else f"n/a ({m['reason']})"
    honest = "n/a" if not ev else f"{ev['claimed']}→{ev['actual']} {'✓' if ev['honest'] else '✗'}"
    return (f"edge {edge:6} | mutation {mut:16} | loc {s['app_loc']:4} cc max {s['max_complexity']:2} "
            f"mean {s['mean_complexity']:4} dup {s['duplicate_functions']} ann {s['annotation_ratio']:.2f} "
            f"| sec {sec['count']} | tests {t['tests']:3} zero-assert {t['zero_assert_tests']} "
            f"a/t {t['asserts_per_test']} | evidence {honest}")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: python -m benchmark.quality <run dir|runs root>…", file=sys.stderr)
        return 2
    for record, ws in _runs(args):
        rec = json.loads(record.read_text(encoding="utf-8"))
        family = next((f for f in ("amb", "hv", "wm") if f"/{f}{rec.get('wm')}" in str(record.parent) + "/"), "wm")
        q = score_quality(ws, rec.get("wm", 1), family)
        (record.parent / "quality.json").write_text(json.dumps(q, indent=2), encoding="utf-8")
        print(f"{str(record.parent)[-60:]:60} {_fmt(q)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
