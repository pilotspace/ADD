"""SWE-bench Lite smoke runner — does ADD improve a coding agent on
leaderboard-class tasks?

Two arms on the SAME model (`claude -p`, the wm bench's argv builder, operator settings isolated):
  - vanilla: the bare agent gets the issue text in the repo checkout, at medium effort.
  - add:     ADD 4.0 (this checkout's package) is installed into the repo first; the agent
             drives the fix through the skill, at LOW effort (ARM_EFFORT).

Per instance x arm: clone repo @ base_commit -> agent run -> `git diff
<base_commit>` of TRACKED files, with ADD/agent artifacts filtered out ->
predictions_<arm>.jsonl in the official SWE-bench predictions shape.

Evaluate with the official harness on Modal (x86, no local docker; `modal token new` once):
    uv run --with swebench --with modal python3 -m swebench.harness.run_evaluation \
        --dataset_name princeton-nlp/SWE-bench_Lite \
        --predictions_path benchmark/runs-swe/<run>/predictions_<arm>.jsonl \
        --modal true --run_id <run>-<arm>

Smoke defaults: three psf/requests instances (small repo, fast clones). A pilot slice:
`--sample 30 --seed 0` draws a fixed random slice of all 300 Lite instances.
This is a SMOKE harness — n is tiny by design; it proves the pipeline and
gathers directional evidence, not a leaderboard submission.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import random
import threading
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_RUNS = REPO_ROOT / "benchmark" / "runs-swe"
DATASET = "princeton-nlp/SWE-bench_Lite"
PINNED_MODEL = "claude-sonnet-5-5"
# ADD at low effort against raw Claude Code at medium — the round-7/8 question, on SWE-bench Lite
ARM_EFFORT = {"vanilla": "medium", "add": "low"}


def effort_for(arm: str, override: str | None) -> str:
    """The effort an arm runs at: `--effort` for this invocation, else its ARM_EFFORT default."""
    from benchmark.runner.agent import EFFORT_LEVELS
    effort = override or ARM_EFFORT[arm]
    if effort not in EFFORT_LEVELS:
        raise SystemExit(f"unknown effort {effort!r}; one of {list(EFFORT_LEVELS)}")
    return effort
SMOKE_INSTANCES = ("psf__requests-2317", "psf__requests-1963", "psf__requests-863")

# paths that are harness/method machinery, never part of the fix
_ARTIFACT_PREFIXES = (".add/", ".add-venv/", ".claude/", ".venv/", ".specify/")
_ARTIFACT_FILES = ("CLAUDE.md", "AGENTS.md", "CLAUDE.md.bak", ".clinerules")


def fetch_instances(instance_ids: list[str],
                    cache: pathlib.Path | None = None) -> list[dict]:
    """Rows from the HF datasets-server (no heavy deps): instance_id, repo,
    base_commit, problem_statement. The datasets-server flakes with 5xx, so:
    retry with backoff, and cache fetched rows so a transient outage can
    never kill a campaign that already has its slice. Loud on unknown ids."""
    cached: dict[str, dict] = {}
    if cache and cache.exists():
        cached = json.loads(cache.read_text())
    rows = []
    for iid in instance_ids:
        if iid in cached:
            rows.append(cached[iid])
            continue
        where = urllib.parse.quote(f"\"instance_id\"='{iid}'")
        url = (f"https://datasets-server.huggingface.co/filter?dataset={urllib.parse.quote(DATASET)}"
               f"&config=default&split=test&where={where}")
        last_err: Exception | None = None
        for delay in (0, 5, 15, 45):
            if delay:
                time.sleep(delay)
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    payload = json.load(resp)
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
                last_err = err
        else:
            raise SystemExit(f"datasets-server unreachable for {iid}: {last_err}")
        found = [r["row"] for r in payload.get("rows", [])]
        if not found:
            raise SystemExit(f"unknown instance_id for {DATASET}: {iid}")
        cached[iid] = found[0]
        rows.append(found[0])
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(cached, indent=1))
    return rows


def fetch_all_ids(cache: pathlib.Path | None = None,
                  rows_cache: pathlib.Path | None = None) -> list[str]:
    """Every instance_id in the Lite test split (300), paged from the datasets-server; cached.
    The pages carry the full rows, so they also seed `rows_cache` (fetch_instances' cache): the
    per-id /filter endpoint 500s under load and is then never needed."""
    if cache and cache.exists():
        return json.loads(cache.read_text())
    ids: list[str] = []
    rows: dict[str, dict] = json.loads(rows_cache.read_text()) if rows_cache and rows_cache.exists() else {}
    offset = 0
    while True:
        url = (f"https://datasets-server.huggingface.co/rows?dataset={urllib.parse.quote(DATASET)}"
               f"&config=default&split=test&offset={offset}&length=100")
        for delay in (0, 5, 15, 45):
            if delay:
                time.sleep(delay)
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    payload = json.load(resp)
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                continue
        else:
            raise SystemExit(f"datasets-server unreachable at offset {offset}")
        page = [r["row"]["instance_id"] for r in payload.get("rows", [])]
        rows.update({r["row"]["instance_id"]: r["row"] for r in payload.get("rows", [])})
        ids += page
        offset += len(page)
        if not page or offset >= payload.get("num_rows_total", 0):
            break
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(ids))
    if rows_cache:
        rows_cache.parent.mkdir(parents=True, exist_ok=True)
        rows_cache.write_text(json.dumps(rows, indent=1))
    return ids


def sample_ids(ids: list[str], n: int, seed: int) -> list[str]:
    """A fixed slice: independent of fetch order, reproducible from (n, seed)."""
    return sorted(random.Random(seed).sample(sorted(ids), n))


def _run(cmd: list[str], cwd: pathlib.Path | None = None, timeout: float = 600.0,
         log: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if log:
        with log.open("a") as fh:
            fh.write(f"$ {' '.join(cmd)} -> {proc.returncode}\n{proc.stdout[-4000:]}\n{proc.stderr[-4000:]}\n")
    return proc


def clone_at(repo: str, base_commit: str, dest: pathlib.Path, log: pathlib.Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", f"https://github.com/{repo}.git", str(dest)], timeout=900, log=log)
    _run(["git", "checkout", "-q", base_commit], cwd=dest, timeout=120, log=log)


def install_add(workspace: pathlib.Path, log: pathlib.Path) -> bool:
    """ADD arm setup: this checkout's ADD 4.0 package, then its installer — one skill, no engine.
    The clone is already a git repo, so the skill's freeze/verify commits land in it; collect_patch
    diffs against base_commit and filters the method's files out of the prediction."""
    steps = (
        ["uv", "venv", ".add-venv", "--clear"],
        ["uv", "pip", "install", "-e", str(REPO_ROOT / "add-method"),
         "--python", ".add-venv/bin/python"],
        [".add-venv/bin/pilotspace-add", "init"],
    )
    for step in steps:
        if _run(step, cwd=workspace, timeout=600, log=log).returncode != 0:
            return False
    return True


def wrap_prompt(problem_statement: str, arm: str) -> str:
    if arm == "vanilla":
        return (
            "Fix the following GitHub issue in this repository. Modify only what the fix "
            "requires; do not create new top-level files or docs. When done, ensure the "
            "change is present in the working tree (no need to commit).\n\n"
            f"<issue>\n{problem_statement}\n</issue>"
        )
    return (
        "Fix the following GitHub issue in this repository by driving this repo's ADD loop "
        "(see CLAUDE.md): read `.claude/skills/add/SKILL.md` first (skills are off in this "
        "session, so read the file) and size the work as the skill says — its Quick lane or a "
        "Task. This is a headless run with no human available: make the calls the skill leaves "
        "to the human yourself and never stop to ask. Start from a test that reproduces the issue "
        "and fails before the fix. This is a FOREIGN host repo: its existing tests nearest the "
        "code you touch are your regression floor — run them and keep them green. Never weaken "
        "existing tests. Modify only what the fix requires; do not create new top-level files or "
        "docs.\n\n"
        f"<issue>\n{problem_statement}\n</issue>"
    )


def agent_argv(prompt: str, model: str, effort: str) -> list[str]:
    """The wm bench's own argv builder: same flags, same operator isolation."""
    from benchmark.runner.agent import default_agent_cmd
    return default_agent_cmd(prompt, model, effort=effort)


def filter_patch(patch: str) -> str:
    """Drop diff hunks that touch harness/method artifacts — the prediction
    must contain the FIX only. Splits on 'diff --git' boundaries."""
    if not patch.strip():
        return patch
    kept = []
    for block in patch.split("diff --git ")[1:]:
        header = block.split("\n", 1)[0]
        path = header.split(" b/")[-1].strip()
        if path in _ARTIFACT_FILES or any(path.startswith(p) for p in _ARTIFACT_PREFIXES):
            continue
        kept.append("diff --git " + block)
    return "".join(kept)


def collect_patch(workspace: pathlib.Path, base_commit: str, log: pathlib.Path) -> str:
    """The fix as a diff against base_commit — committed, staged, unstaged AND new untracked files
    (`add -A` first: a plain `git diff <base>` drops a file the fix creates but never commits)."""
    _run(["git", "add", "-A"], cwd=workspace, timeout=120, log=log)
    diff = _run(["git", "diff", "--cached", "--no-color", base_commit], cwd=workspace, timeout=120, log=log)
    return filter_patch(diff.stdout)


def run_instance(row: dict, arm: str, runs_root: pathlib.Path, model: str,
                 timeout_s: float, effort: str | None = None) -> dict:
    effort = effort_for(arm, effort)
    iid = row["instance_id"]
    inst_dir = runs_root / arm / iid
    workspace = inst_dir / "workspace"
    log = inst_dir / "run.log"
    inst_dir.mkdir(parents=True, exist_ok=True)

    if not workspace.exists():
        clone_at(row["repo"], row["base_commit"], workspace, log)
    if arm == "add" and not install_add(workspace, log):
        return {"instance_id": iid, "model_patch": "", "model_name_or_path": f"{model}+{arm}",
                "error": "add setup failed"}

    start = time.monotonic()
    try:
        proc = _run(agent_argv(wrap_prompt(row["problem_statement"], arm), model, effort),
                    cwd=workspace, timeout=timeout_s, log=log)
        stdout = proc.stdout
    except subprocess.TimeoutExpired as exc:  # keep whatever the agent left in the tree
        stdout = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    elapsed = time.monotonic() - start
    (inst_dir / "transcript.jsonl").write_text(stdout)  # the trajectory a submission needs

    patch = collect_patch(workspace, row["base_commit"], log)
    (inst_dir / "model_patch.diff").write_text(patch)
    return {"instance_id": iid, "model_patch": patch,
            "model_name_or_path": f"{model}+{arm}", "effort": effort,
            "elapsed_s": round(elapsed, 1), "cost_usd": _last_cost(stdout)}


def _last_cost(stream_stdout: str) -> float:
    for line in reversed(stream_stdout.splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and "total_cost_usd" in event:
            return float(event["total_cost_usd"])
    return 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arms", nargs="+", default=["vanilla", "add"], choices=["vanilla", "add"])
    ap.add_argument("--instances", nargs="+", default=list(SMOKE_INSTANCES))
    ap.add_argument("--sample", type=int, default=0, help="draw N instances from all of Lite instead")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--model", default=PINNED_MODEL)
    ap.add_argument("--runs-root", default=str(DEFAULT_RUNS))
    ap.add_argument("--timeout-s", type=float, default=1500.0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--effort", default=None, help="override every arm's effort for this run (default: ARM_EFFORT)")
    args = ap.parse_args()

    runs_root = pathlib.Path(args.runs_root)
    ids = (sample_ids(fetch_all_ids(cache=runs_root / "lite_ids.json",
                                     rows_cache=runs_root / "instances.json"), args.sample, args.seed)
           if args.sample else args.instances)
    rows = fetch_instances(ids, cache=runs_root / "instances.json")
    print(f"[swe] {len(rows)} instances x {args.arms} on {args.model} "
          f"({ {a: effort_for(a, args.effort) for a in args.arms} })", flush=True)

    for arm in args.arms:
        preds_path = runs_root / f"predictions_{arm}.jsonl"
        done = set()
        if preds_path.exists():
            done = {json.loads(l)["instance_id"] for l in preds_path.read_text().splitlines() if l.strip()}
        todo = [r for r in rows if r["instance_id"] not in done]
        lock = threading.Lock()

        def one(row: dict) -> None:
            print(f"[swe] run {arm}/{row['instance_id']} ...", flush=True)
            try:
                pred = run_instance(row, arm, runs_root, args.model, args.timeout_s, args.effort)
            except Exception as exc:  # one broken clone must not sink the slice
                pred = {"instance_id": row["instance_id"], "model_patch": "",
                        "model_name_or_path": f"{args.model}+{arm}", "error": repr(exc)[:300]}
            with lock, preds_path.open("a") as fh:
                fh.write(json.dumps(pred) + "\n")
            print(f"[swe]   {arm}/{row['instance_id']} -> patch {len(pred['model_patch'])}B "
                  f"${pred.get('cost_usd', 0):.2f} {pred.get('elapsed_s', 0)}s", flush=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(one, todo))
    print("[swe] predictions written; evaluate with the official harness (see module docstring)",
          flush=True)


if __name__ == "__main__":
    main()
