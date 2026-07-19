"""SWE-bench Lite smoke runner — does ADD improve a coding agent on
leaderboard-class tasks?

Two arms on the SAME pinned agent (`claude -p`, the meter model):
  - vanilla: the bare agent gets the issue text in the repo checkout.
  - add:     ADD (this checkout's 2.0 package) is installed into the repo
             first; the agent is told to drive the fix through the ADD loop.

Per instance x arm: clone repo @ base_commit -> agent run -> `git diff
<base_commit>` of TRACKED files, with ADD/agent artifacts filtered out ->
predictions_<arm>.jsonl in the official SWE-bench predictions shape.

Evaluate with the official harness (docker):
    uv run --with swebench python3 -m swebench.harness.run_evaluation \
        --dataset_name princeton-nlp/SWE-bench_Lite \
        --predictions_path benchmark/runs-swe/predictions_<arm>.jsonl \
        --max_workers 2 --run_id add-smoke-<arm> --namespace ''

Smoke defaults: three psf/requests instances (small repo, fast clones).
This is a SMOKE harness — n is tiny by design; it proves the pipeline and
gathers directional evidence, not a leaderboard submission.
"""
from __future__ import annotations

import argparse
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
PINNED_MODEL = "claude-sonnet-5"
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
    """ADD arm setup: this checkout's package + init, exactly like the wm bench."""
    steps = (
        ["uv", "venv", ".add-venv", "--clear"],
        ["uv", "pip", "install", "-e", str(REPO_ROOT / "add-method"),
         "--python", ".add-venv/bin/python"],
        [".add-venv/bin/pilotspace-add", "init", "--yes", "--non-interactive", "--force"],
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
        "Fix the following GitHub issue in this repository by driving the ADD loop "
        "(see CLAUDE.md): run `python3 .add/tooling/add.py status` first, create ONE task "
        "with `python3 .add/tooling/add.py new-task fix-issue`, declare `gate_mode: "
        "ai-plan-verify` in the PLAN.md header, draft the whole Direction bundle in one "
        "pass (rules, scenarios, change plan, red test capturing the issue). This is a "
        "FOREIGN host repo: its existing test suite is your §3 Regression floor — run the "
        "tests nearest the code you touch before the gate and keep them green (a fix that "
        "breaks a neighboring host test is a defect, not collateral). Freeze with `python3 "
        ".add/tooling/add.py freeze --by agent --cross`, build to green, record the gate. "
        "Never weaken existing tests. Modify only what the fix requires. When done, ensure "
        "the change is present in the working tree.\n\n"
        f"<issue>\n{problem_statement}\n</issue>"
    )


def agent_argv(prompt: str, model: str) -> list[str]:
    return [
        "claude", "-p", prompt,
        "--model", model, "--effort", "medium",
        "--output-format", "stream-json", "--verbose",
        "--disable-slash-commands", "--strict-mcp-config",
        "--dangerously-skip-permissions",
    ]


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


def run_instance(row: dict, arm: str, runs_root: pathlib.Path, model: str,
                 timeout_s: float) -> dict:
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
    proc = _run(agent_argv(wrap_prompt(row["problem_statement"], arm), model),
                cwd=workspace, timeout=timeout_s, log=log)
    elapsed = time.monotonic() - start

    diff = _run(["git", "diff", "--no-color", row["base_commit"]], cwd=workspace,
                timeout=120, log=log)
    patch = filter_patch(diff.stdout)
    (inst_dir / "model_patch.diff").write_text(patch)
    cost = _last_cost(proc.stdout)
    return {"instance_id": iid, "model_patch": patch,
            "model_name_or_path": f"{model}+{arm}",
            "elapsed_s": round(elapsed, 1), "cost_usd": cost}


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
    ap.add_argument("--arms", nargs="+", default=["vanilla", "add"],
                    choices=["vanilla", "add"])
    ap.add_argument("--instances", nargs="+", default=list(SMOKE_INSTANCES))
    ap.add_argument("--model", default=PINNED_MODEL)
    ap.add_argument("--runs-root", default=str(DEFAULT_RUNS))
    ap.add_argument("--timeout-s", type=float, default=1500.0)
    args = ap.parse_args()

    runs_root = pathlib.Path(args.runs_root)
    rows = fetch_instances(args.instances, cache=runs_root / "instances.json")
    print(f"[swe-smoke] {len(rows)} instances x {args.arms} on {args.model}", flush=True)

    for arm in args.arms:
        preds_path = runs_root / f"predictions_{arm}.jsonl"
        done = set()
        if preds_path.exists():
            done = {json.loads(l)["instance_id"] for l in preds_path.read_text().splitlines() if l.strip()}
        with preds_path.open("a") as fh:
            for row in rows:
                if row["instance_id"] in done:
                    print(f"[swe-smoke] skip {arm}/{row['instance_id']} (done)", flush=True)
                    continue
                print(f"[swe-smoke] run {arm}/{row['instance_id']} ...", flush=True)
                pred = run_instance(row, arm, runs_root, args.model, args.timeout_s)
                fh.write(json.dumps(pred) + "\n")
                fh.flush()
                print(f"[swe-smoke]   -> patch {len(pred['model_patch'])}B "
                      f"${pred.get('cost_usd', 0):.2f} {pred.get('elapsed_s', 0)}s", flush=True)
    print("[swe-smoke] predictions written; evaluate with the official harness "
          "(see module docstring)", flush=True)


if __name__ == "__main__":
    main()
