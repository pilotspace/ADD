# TASK: run the 5-arm x 3-WM x 1-rep pilot and render the arm-vs-arm report with evidence links

slug: bench-pilot-report · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `benchmark/run.py:main`, `:_build_parser` — existing `run|resume|score` CLI; this task ADDS a `report` subcommand here (MILESTONE.md names `run.py run|resume|score|report` as one CLI surface).
  - `benchmark/runner/core.py:execute_wm` — the frozen per-arm×WM atomic-outcome unit (bench-runner §3); this task's pilot orchestration calls it directly (import, not subprocess-of-CLI) with a RESOLVED `Arm` (setup_steps rewritten, see below), never reimplementing its workspace/timeout/retry/record logic.
  - `benchmark/runner/core.py:_run_setup_steps` (L97-132) — runs each `arm.setup_steps` line as `shlex.split()` list-argv with `cwd=workspace_dir`; already wired (bench-runner's post-freeze gap-close), but the real `add` arm's literal steps (`pip install -e add-method`, `python3 .add/tooling/add.py init --auto`) resolve relative to `workspace_dir` — `add-method` and `.add/` do not exist there. This is the exact provisioning gap this task must close (§0 Issues below).
  - `benchmark/arms/add.toml:setup_steps` — data (TOML string list), NOT part of any frozen §3 CONTRACT shape (only `loader.py:REQUIRED_KEYS`/`REQUIRED_FAIRNESS_KEYS` are frozen); editing the setup_steps *content* is in-scope for this task, editing the TOML *shape* is not.
  - `benchmark/arms/loader.py:load_arm`, `:Arm`, `:ARM_NAMES` (`("add","vanilla","plan-mode","gsd","spec-kit")`), `:PIN_REQUIRED_ARMS` — `Arm` is `@dataclasses.dataclass(frozen=True)`; this task derives a RESOLVED copy via `dataclasses.replace`, never mutates or re-shapes it.
  - `benchmark/runner/records.py:find_resume_point` (L43-63), `:write_record_atomic`, `:DEFAULT_RUNS_ROOT` — `find_resume_point` returns `highest_done_wm + 1` by scanning ALL `wm*/record.json` under an arm, not a strict 1→2→3 walk; a non-contiguous done-set (e.g. wm1+wm3 done, wm2 missing) returns 4 ("nothing left"), silently treating wm2 as already covered. Frozen by bench-runner §3 — this task does NOT change the function (out of scope, another task's frozen contract), but MUST add the one guard test bench-runner's own §7 Spec delta named, pinning this real (moot-under-sequential-use, but real) behavior so it is never rediscovered as a surprise.
  - `benchmark/score.py:score_record`, `judge.py:judge_fidelity`, `:build_judge_argv` — the frozen `score` CLI/internal surface (bench-scoring §3); this task's pilot orchestration calls `score_record` directly after each successful `execute_wm`, passing through an injectable `judge_cmd` exactly like `score`'s own CLI does — never reimplementing the judge/scoring logic.
  - `benchmark/schema/run_record.py:RunRecord`, `:validate`, `:REQUIRED_METRICS`, `:REQUIRED_ARTIFACTS` — `artifacts` only enforces a required SUBSET (`workspace`, `transcript`, `oracle_report`) — extra keys already flow through (`attempts`, `token_source`, `resolved_pin`, `leak_path`, `metrics_warnings`); this task adds one more extra key, `spec_fidelity_audit`, following that exact precedent — no schema change.
  - `.gitignore:49` `benchmark/runs/` — the report reads from here; nothing new is written outside `benchmark/runs/<arm>/wm<n>/` except the report's own output file (path is a CLI arg, defaults to stdout).
Context (working folder): `benchmark/tests/conftest.py` (`REPO_ROOT` sys.path fixture, reused) · no `benchmark/pilot.py` or `benchmark/report.py` exists yet — both net-new · `benchmark/arms/*.toml` (5 files, read above) is the only pre-existing file this task edits in place (setup_steps content for the `add` arm only; the other 4 arms' setup_steps need no venv — `npm install -g`, `uvx --from git+...`, and bare `claude --print` calls are already self-contained, global-tool invocations with no relative-path/pip dependency).
Honors (patterns / conventions): stdlib-first, fail-loud `BenchError` on any malformed shape (never silently coerce) — same discipline `run_record.py`/`runner/core.py`/`score.py` already establish; subprocess calls use list-form argv only (no `shell=True`) — the new `uv venv`/`uv pip install` provisioning steps in the arm TOML are themselves shlex-split list-argv through the ALREADY-EXISTING `_run_setup_steps`, no new subprocess surface introduced by this task; report/pilot orchestration reuse existing internal functions (`execute_wm`, `score_record`, `find_resume_point`) by import, never by re-deriving their logic or shelling out to `run.py` as a black box (constraint: "must reuse the existing run/resume/score CLI, not reimplement it").
Seams consulted: none new — mirrors bench-scoring's own precedent of extending `artifacts` with an extra tolerated key (`metrics_warnings`) for `spec_fidelity_audit`; no SEAMS.md entry existed for pilot-sequencing or report-rendering before this task.
Anchors the contract cites: `execute_wm` (benchmark/runner/core.py) · `score_record` (benchmark/score.py) · `find_resume_point`/`write_record_atomic`/`DEFAULT_RUNS_ROOT` (benchmark/runner/records.py) · `load_arm`/`Arm`/`ARM_NAMES` (benchmark/arms/loader.py) · `RunRecord`/`validate`/`BenchError` (benchmark/schema/run_record.py) · `benchmark/arms/add.toml` (edited content).
Issues/Risks (→ feed §1):
  - **Provisioning gap (MUST absorb, per milestone brief):** the real `add` arm's `setup_steps` cannot succeed in a bare sandbox workspace (`externally-managed-environment` pip error, reproduced at bench-runner's own re-cross fixture correction) — this task must design and ship a concrete per-workspace venv mechanism, not defer it again.
  - **Spot-check gap (MUST absorb, per bench-scoring §7 delta):** `spec_fidelity` has never been checked by a human against a real arm output; the pilot flow must mark it "unaudited" until an explicit attestation exists, never silently presented as ground truth.
  - **find_resume_point non-contiguous gap (MUST absorb, ONE test only, per bench-runner §7 delta):** pin the current (real, moot-under-sequential-use) behavior with a guard test — NOT a fix to the frozen function.
  - **rule_coverage_gap audit-format question (ROUTE, not absorb, per bench-scoring §7 delta):** `add.py check`'s `covers:` tag parser mismatch is an engine-side concern outside this task's `benchmark/` scope — noted here so it is not silently dropped, but deliberately NOT fixed by this task (would touch `.add/tooling/`, outside §5 Scope).
  - the live pilot itself (5 arms × 3 WMs × 1 rep, ~15 `claude -p` runs + ~15 judge calls) is expensive and slow — it is a §6 VERIFY/OBSERVE activity, never a unit test; the hermetic test suite must prove the orchestration logic (sequencing, provisioning-step resolution, report rendering, resume behavior) entirely against fixtures + a fake agent/judge, with zero live network/CLI calls.
  - `_run_setup_steps` fails a WM's whole run if any setup line exits nonzero (records `status="failed"`, per bench-runner's frozen Must) — a broken venv/install step is therefore already visible as a `failed` record, not a silent no-op; this task's design must not weaken that.
  - workload milestones are causally sequential (WM2's prompt assumes WM1's code exists in the SAME workspace) — a non-"done" WM must halt that arm's remaining sequence, never attempt the next WM against a broken/incomplete workspace.
Related intent: MILESTONE.md exit criterion "the full pilot (5 arms × 3 WMs × 1 rep) runs unattended and `report` renders the arm-vs-arm comparison with evidence links" (this task's sole deliverable) · MILESTONE.md "Shared / risky contracts" line naming `run.py run|resume|score|report` as one CLI surface · bench-runner TASK.md §7 Spec deltas (provisioning + non-contiguous resume guard) · bench-scoring TASK.md §7 Spec deltas (spot-check + rule_coverage_gap routing) — all four ABSORBED-or-ROUTED per the objective. GLOSSARY: `arm`, `workload milestone`, `oracle suite`, `resolved pin`, `scored record`, `judge command` (all prior tasks' deltas).
Ground SHA: 4f75b73

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: (a) `benchmark/run.py report` — renders the 5-arm × 3-WM arm-vs-arm markdown comparison from scored `record.json` files alone (re-runnable, no live agent); (b) `benchmark/pilot.py` — a new orchestration entrypoint that sequences the full 5×3×1 live pilot (per-arm venv provisioning → `execute_wm` → `score_record`, per WM, honoring resume), reusing `run.py`'s internal functions, never reimplementing them.
Framings weighed:
  **separate `benchmark/pilot.py` entrypoint, importing `execute_wm`/`score_record`/`find_resume_point` directly** (chosen) — MILESTONE.md's named CLI surface is explicitly `run.py run|resume|score|report`; `report` belongs on `run.py` (a read-only query over `benchmark/runs/`), but "sequence 5 arms × 3 WMs, provisioning + run + score, with resume" is a distinct orchestration concern with its own failure modes (which arm/WM to run next, halt-on-non-done) that would bloat `run.py`'s existing well-tested subparsers; a separate module keeps `run.py`'s frozen-shaped CLI untouched while giving the pilot loop its own hermetic test surface.
  · a `run.py pilot` subcommand instead — rejected: would require `run.py` to import `score.py` AND orchestrate multi-arm/multi-WM looping inside the same argparse module that bench-runner/bench-scoring already froze tightly around `run|resume|score`; a new top-level module is a smaller, more isolated diff and matches "the pilot itself is a §6 activity" (a distinct concern from the already-frozen per-WM CLI).
  · shelling out to `python -m benchmark.run run --arm ... --wm ...` as subprocesses from the pilot orchestrator instead of importing `execute_wm`/`score_record` directly — rejected: adds a second process-boundary and JSON-parsing seam purely to "reuse the CLI," when the CLI itself is a thin wrapper over exactly those two functions; importing them directly IS reusing the existing implementation (not reinventing it) while keeping tests fast/hermetic (no nested subprocess-of-subprocess).
  Provisioning mechanism — **rewrite the `add` arm's `setup_steps` TOML content to a `uv venv` + `uv pip install -e {REPO_ROOT}/add-method --python .venv/bin/python` + `.venv/bin/pilotspace-add init --yes --non-interactive` sequence, with `{REPO_ROOT}` resolved by a new pure function `pilot.resolve_setup_steps(arm, repo_root) -> Arm` before `execute_wm` is called** (chosen) — the token-substitution step is a pure, hermetically-testable data transform (no I/O), keeps `_run_setup_steps`'s existing "shlex-split list-argv, cwd=workspace_dir" contract completely untouched (bench-runner's frozen §3 code is not touched), and the other 4 arms have no `{REPO_ROOT}` token so `resolve_setup_steps` is a no-op passthrough for them (verified by a scenario).
  · a container/docker sandbox per arm instead — rejected: MILESTONE.md's stage is `mvp` / pilot scale (5×3×1); a container runtime is new infra this milestone's Scope never asked for and the workload's `_oracle_lib.running_app` already assumes a bare `python -m app` process on `$PORT`, not a container network — would ripple into bench-scaffold's frozen workload contract.
  · installing `add-method` into a single SHARED venv reused across all 3 WMs/arms instead of per-workspace — rejected: MILESTONE.md's fairness floor requires arms "never share workspace state"; a shared venv across the `add` arm's own 3 WMs is fine (same arm), but the loader/`_run_setup_steps` already runs setup fresh per WM's own `workspace_dir` (bench-runner's frozen per-WM sandboxing) — creating the venv INSIDE `workspace_dir` (not a repo-level shared path) is the only option that doesn't touch that frozen isolation boundary.
Must:
<must>
  - `report` reads every `benchmark/runs/<arm>/wm<n>/record.json` that exists for `arm in ARM_NAMES` × `wm in (1,2,3)` and renders ONE markdown table per workload milestone (5 arms × 5 metrics), plus a per-cell evidence link to that WM's `record.json` and `transcript` artifact paths; a missing record.json renders as "not run", never an error (a partial pilot is still reportable) (M1).
  - for `wm in (1,2)`, `report` renders `regression_rate` and `context_rot_slope` as an explicit `N/A (by definition)` annotation, NEVER as a bare `0.0` — those two metrics are structurally undefined before WM3 per bench-scoring's frozen M5/M7, and presenting them as a measured `0.00` would misrepresent a placeholder as data (M2).
  - `report` renders `spec_fidelity` with an `(unaudited)` suffix for any arm×WM cell whose `record.json.artifacts` lacks a `spec_fidelity_audit` key; the suffix is dropped only for a cell that carries one (M3).
  - a new `pilot.py attest --arm <name> --wm <n> --note <text>` command writes `artifacts["spec_fidelity_audit"] = "spot-checked: <text>"` back into that WM's `record.json` via the existing frozen `write_record_atomic`/`validate` — the human-in-the-loop spot-check mechanism the spec delta calls for; refuses (does not write) if the record isn't `status="done"` and scored (no `spec_fidelity` computed yet) (M4).
  - `pilot.py resolve_setup_steps(arm: Arm, repo_root: Path) -> Arm` replaces every literal `{REPO_ROOT}` token in `arm.setup_steps` with `str(repo_root)`, returning a NEW `Arm` (`dataclasses.replace`) — the original loaded `Arm` object is never mutated; an arm with no `{REPO_ROOT}` token in any step is returned unchanged (identity passthrough) (M5).
  - `benchmark/arms/add.toml`'s `setup_steps` is rewritten to: `uv venv .venv`, `uv pip install -e {REPO_ROOT}/add-method --python .venv/bin/python`, `.venv/bin/pilotspace-add init --yes --non-interactive` — each a valid single-line shlex-splittable list-argv command (no `&&`, no shell string), matching `_run_setup_steps`'s existing (frozen, unmodified) execution contract (M6).
  - `pilot.py run_pilot(arms=ARM_NAMES, wms=(1,2,3), *, resume=True, agent_cmd=None, judge_cmd=None, timeout_s=1800.0, retries=1, runs_root=None, repo_root=None) -> list[RunRecord]` sequences, PER ARM independently: resolve the arm (`load_arm` + `resolve_setup_steps`), determine the starting WM (`find_resume_point` when `resume=True` and prior records exist, else `wms[0]`), then for each WM in order call `execute_wm` (reusing it verbatim) and, only if that WM's resulting `status == "done"`, call `score_record` (reusing it verbatim, passing `judge_cmd` through) before continuing to the next WM (M7).
  - if a WM's `execute_wm` result is NOT `"done"` (`"timeout"` or `"failed"`), `run_pilot` records that outcome and HALTS that arm's remaining WM sequence (never invokes the next WM against a workspace whose predecessor never finished) — but continues on to the NEXT arm, since arms never share state (M8).
  - `run_pilot` is resumable: interrupting it after arm N's WM M completes and re-invoking with `resume=True` continues from arm N's next unresumed WM (via `find_resume_point`) without re-invoking the agent for any already-`"done"` WM, and does not re-run arms whose WM3 is already `"done"`+scored (M9).
  - `benchmark/tests/` gains exactly one new guard test pinning `find_resume_point`'s real behavior on a non-contiguous done-set (wm1 done, wm3 done, wm2 missing) — asserting its CURRENT documented semantics (returns `4`, i.e. "nothing left"), not a fix; a comment cites bench-runner TASK.md §7 as the origin of this absorbed delta (M10).
</must>
Reject:
<reject>
  - `report --arm <name>` / `report --wm <n>` given an out-of-range filter -> "unknown_arm" / "invalid_wm" (same frozen codes `run`/`score` already use — no new vocabulary for an already-named rejection)
  - `pilot.py attest` targeting a `record.json` that does not exist -> "record_not_found" (reuses `score.py`'s existing code)
  - `pilot.py attest` targeting a record whose `status != "done"` -> "record_not_done" (reuses `score.py`'s existing code)
  - `pilot.py attest` targeting a "done" record whose `metrics["spec_fidelity"]` is still the runner's `0.0` placeholder (never scored) -> "record_not_scored" (new code — attesting an unscored judge verdict is meaningless; distinct from "not done" because a "done"-but-unscored record is a real, valid, in-between state per bench-scoring's own design)
  - `pilot.py run_pilot` given an `arm` not in `ARM_NAMES` -> "unknown_arm" (propagated from `load_arm`/frozen `ARM_NAMES` check, not re-wrapped)
  - `pilot.py resolve_setup_steps` given a `repo_root` that does not exist on disk -> "invalid_repo_root" (new code — a silently-wrong path would produce a confusing downstream `setup_steps` failure instead of a clear one)
</reject>
After:
<after>
  - `benchmark/run.py report` run against a partially-complete `benchmark/runs/` tree renders a complete 3-table (one per WM) markdown document with every arm×metric cell populated, either with a real number, an evidence-linked N/A annotation, an (unaudited) suffix, or "not run" — never a blank cell, never a crash.
  - the `add` arm's `execute_wm` (driven through `pilot.run_pilot`, with `resolve_setup_steps` applied) succeeds its `setup_steps` phase in a completely bare, from-scratch sandbox workspace — the `externally-managed-environment` failure mode is closed, not deferred again.
  - after `pilot.py attest --arm X --wm N`, that cell's `record.json.artifacts["spec_fidelity_audit"]` is present and `report`'s rendering of that one cell drops the `(unaudited)` suffix; all other cells are untouched.
  - a killed `run_pilot` invocation, re-run with `resume=True`, never re-invokes the agent or judge for any arm×WM already `"done"`+scored.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] the `uv venv` + `uv pip install -e {REPO_ROOT}/add-method --python .venv/bin/python` sequence provisions a bare sandbox — CONFIRMED by live spike 2026-07-07 (orchestrator): venv created, pilotspace-add==1.17.0 editable-installed, `add_method` importable, and `.venv/bin/pilotspace-add init --yes --non-interactive` scaffolded `.add/` + `.claude/` + CLAUDE.md in an empty dir. CORRECTION folded in: the third setup line is the installed CLI `pilotspace-add init --yes --non-interactive` — the previously-drafted `add.py init --auto` flag does not exist on the real CLI.
  - [ ] `report`'s markdown-table-per-WM shape (5 arms × 5 metrics, one table per WM) is the right rendering for "arm-vs-arm comparison" — confirm or deny against MILESTONE.md's phrase "markdown table + per-arm evidence links"; if the human instead wants ONE table with arm×WM as compound rows (15 rows × 5 metric columns) rather than 3 separate 5×5 tables, `report.render_report`'s internal grouping changes but the CONTRACT's public surface (`report --out <path>`) does not.
  - [x] DECIDED at freeze (human, 2026-07-07): attest writes a STRUCTURED audit record `{reviewer, date, note}` (serialized into artifacts["spec_fidelity_audit"]), not a free-text string — was: free-text `--note` assumed sufficient
  - [ ] halting an arm's sequence on the first non-"done" WM (M8) — rather than attempting WM2/WM3 anyway against a stale/incomplete workspace to at least gather partial metrics — is assumed the right pilot-report tradeoff (a clean halt vs. attempting a probably-meaningless run); if wrong, the report would need a way to distinguish "never attempted" from "attempted against a broken predecessor," which M8/M1's "not run" rendering does not currently separate.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: report renders a full grid from fixture records   # M1
  Given fixture record.json files exist for all 5 arms × 3 WMs, all status="done" and scored
  When `run.py report` executes (no live agent)
  Then it prints 3 markdown tables (one per WM), each with 5 arm rows and 5 metric columns
  And every cell links to that arm×WM's record.json and transcript path

Scenario: a missing record renders as "not run", not a crash   # M1
  Given no benchmark/runs/gsd/wm2/record.json exists
  When `run.py report` executes
  Then the gsd/wm2 row for every metric renders "not run"
  And the report still completes for all other arm×WM cells

Scenario: WM1/WM2 regression_rate and context_rot_slope render N/A   # M2
  Given a "done" scored wm1 record.json with regression_rate=0.0, context_rot_slope=0.0 (by definition)
  When `run.py report` executes
  Then those two cells render "N/A (by definition)"
  And no cell in the wm1 table shows a bare "0.00" for either metric

Scenario: unaudited spec_fidelity is flagged   # M3
  Given a "done" scored wm1 record.json with no artifacts["spec_fidelity_audit"] key
  When `run.py report` executes
  Then the spec_fidelity cell renders "0.82 (unaudited)" (or the actual scored value + the suffix)

Scenario: attesting a cell drops its unaudited flag   # M3, M4
  Given the same wm1 record.json as above
  When `pilot.py attest --arm add --wm 1 --note "matches PROMPT.md requirements"` runs, then `run.py report` runs again
  Then the record.json now has artifacts["spec_fidelity_audit"] == "spot-checked: matches PROMPT.md requirements"
  And the report's spec_fidelity cell for add/wm1 no longer carries the "(unaudited)" suffix

Scenario: resolve_setup_steps substitutes the REPO_ROOT token   # M5
  Given the add arm's loaded setup_steps containing "uv pip install -e {REPO_ROOT}/add-method --python .venv/bin/python"
  When `pilot.resolve_setup_steps(arm, repo_root=/tmp/repo)` runs
  Then the returned Arm's matching setup_steps line reads "uv pip install -e /tmp/repo/add-method --python .venv/bin/python"
  And the original `arm` object's setup_steps is unchanged (no mutation)

Scenario: resolve_setup_steps is a no-op for arms without the token   # M5
  Given the vanilla arm's setup_steps (no "{REPO_ROOT}" token anywhere)
  When `pilot.resolve_setup_steps(arm, repo_root=/tmp/repo)` runs
  Then the returned Arm's setup_steps is identical (by value) to the input

Scenario: add arm's rewritten setup_steps succeed in a bare sandbox   # M6
  Given a from-scratch empty workspace directory and the real (rewritten) add.toml, with `{REPO_ROOT}` resolved to this repo's real path
  When `execute_wm` runs the resolved arm's setup_steps (fake-agent argv injected for the agent step itself)
  Then all 3 setup lines exit 0 (uv venv creates .venv, uv pip install succeeds, add.py init --auto succeeds)
  And the resulting record's status is not "failed" due to a setup-step nonzero exit

Scenario: run_pilot sequences arm-by-arm, halting on a non-done WM   # M7, M8
  Given a fake agent that succeeds for add/wm1 and add/wm2, then fails (nonzero exit) for add/wm3, and succeeds for every WM of vanilla
  When `pilot.run_pilot(arms=["add","vanilla"], wms=(1,2,3), agent_cmd=<fake>, judge_cmd=<fake>)` runs
  Then add has record.json for wm1 (done, scored), wm2 (done, scored), wm3 (failed, unscored)
  And add's wm3 failure does not prevent vanilla's wm1-3 from all running and scoring
  And score_record is never invoked for a WM whose execute_wm status was not "done"

Scenario: run_pilot resumes without re-invoking a done arm   # M9
  Given add/wm1, add/wm2, add/wm3 are all already "done" and scored from a prior run_pilot invocation
  When `pilot.run_pilot(arms=["add"], resume=True, agent_cmd=<fake-that-fails-the-test-if-invoked>)` runs
  Then the fake agent is never invoked for the add arm
  And add's 3 existing record.json files are byte-unchanged

Scenario: find_resume_point's non-contiguous behavior is pinned   # M10
  Given benchmark/runs/<arm>/wm1/record.json status="done" and wm3/record.json status="done", with no wm2/record.json
  When `find_resume_point(<arm>)` is called
  Then it returns 4 (documents the real "highest-done+1 across all records" behavior — not a fix, a guard)

Scenario: report rejects an out-of-range filter   # R1 unknown_arm / R2 invalid_wm
  Given `report --arm ghost` is invoked
  When report parses arguments
  Then it exits 2 with "unknown_arm"
  And no output is printed

Scenario: attest targets a nonexistent record   # R3 record_not_found
  Given benchmark/runs/add/wm2/record.json does not exist
  When `pilot.py attest --arm add --wm 2 --note "x"` runs
  Then it exits 2 with "record_not_found"
  And no file is created

Scenario: attest targets a not-done record   # R4 record_not_done
  Given a wm1 record.json with status="failed"
  When `pilot.py attest --arm add --wm 1 --note "x"` runs
  Then it exits 2 with "record_not_done"
  And the on-disk record.json is unchanged

Scenario: attest targets a done-but-unscored record   # R5 record_not_scored
  Given a "done" wm1 record.json whose metrics["spec_fidelity"] is still the runner's 0.0 placeholder (never scored)
  When `pilot.py attest --arm add --wm 1 --note "x"` runs
  Then it exits 2 with "record_not_scored"
  And the on-disk record.json is unchanged

Scenario: run_pilot rejects an unknown arm   # R6 unknown_arm
  Given "ghost" is not in ARM_NAMES
  When `pilot.run_pilot(arms=["ghost"])` runs
  Then it raises/exits with "unknown_arm"
  And no workspace or record is created for "ghost"

Scenario: resolve_setup_steps rejects a nonexistent repo_root   # R7 invalid_repo_root
  Given repo_root="/does/not/exist"
  When `pilot.resolve_setup_steps(arm, repo_root="/does/not/exist")` runs
  Then it raises BenchError("invalid_repo_root: ...")
  And no setup_steps execution is attempted
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI run.py report [--arm <name>] [--wm <1|2|3>] [--runs-root <path>] [--out <path>]
  exit 0 -> prints (or writes to --out) markdown: one table per WM in {1,2,3} (or the single
    filtered WM), rows = ARM_NAMES (or the single filtered arm), columns = the 5 REQUIRED_METRICS;
    each numeric cell links its arm×WM's record.json + transcript artifact paths; a missing
    record.json cell renders "not run"; wm in {1,2} renders regression_rate/context_rot_slope as
    "N/A (by definition)"; any spec_fidelity cell lacking artifacts["spec_fidelity_audit"] renders
    with an "(unaudited)" suffix
  exit 2 -> "unknown_arm" | "invalid_wm"   (no output printed, no file written)

CLI pilot.py run-all [--arms <name...>=ARM_NAMES] [--wms <n...>=(1,2,3)] [--resume=true]
                     [--agent-cmd <argv...>] [--judge-cmd <argv...>] [--timeout-s <float>=1800]
                     [--retries <int>=1] [--runs-root <path>] [--repo-root <path>=REPO_ROOT]
  exit 0 -> sequences each arm independently (resolve -> per-WM execute_wm -> score_record on
    "done", halting that arm's remaining WMs on a non-"done" status), writes/overwrites the
    normal run/score record.json files (no new schema), returns/prints the list of RunRecords
  exit 2 -> "unknown_arm"   (propagated from load_arm/ARM_NAMES, unwrapped)

CLI pilot.py attest --arm <name> --wm <1|2|3> --note <text>
  exit 0 -> benchmark/runs/<arm>/wm<n>/record.json rewritten in place (write_record_atomic) with
    artifacts["spec_fidelity_audit"] = "spot-checked: <text>"; all other fields byte-identical
  exit 2 -> "record_not_found" | "record_not_done" | "record_not_scored"
    (record.json on disk left byte-unchanged for every exit-2 path)

Internal (importable) surface:
  report.render_report(runs_root: pathlib.Path, arms: Sequence[str] = ARM_NAMES,
                        wms: Sequence[int] = (1, 2, 3)) -> str
    — pure function over on-disk record.json files; never raises for a missing record (renders
      "not run"); the CLI's exit-2 filter validation happens BEFORE calling this, not inside it.
  pilot.resolve_setup_steps(arm: Arm, repo_root: pathlib.Path) -> Arm
    — pure token-substitution ("{REPO_ROOT}" -> str(repo_root)) over arm.setup_steps; returns a
      NEW Arm via dataclasses.replace; raises BenchError("invalid_repo_root: ...") if repo_root
      does not exist on disk; identity passthrough for an arm with no token.
  pilot.run_pilot(arms: Sequence[str] = ARM_NAMES, wms: Sequence[int] = (1, 2, 3), *,
                  resume: bool = True, agent_cmd: Sequence[str] | None = None,
                  judge_cmd: Sequence[str] | None = None, timeout_s: float = 1800.0,
                  retries: int = 1, runs_root: pathlib.Path | None = None,
                  repo_root: pathlib.Path | None = None) -> list[RunRecord]
    — orchestrates, per arm: load_arm -> resolve_setup_steps -> (find_resume_point if resume else
      wms[0]) -> for wm in sequence: execute_wm(...) -> if status=="done": score_record(...) ->
      else: break (halt this arm's remaining WMs, continue to next arm). Reuses execute_wm/
      score_record/find_resume_point verbatim (imported, not reimplemented). Raises
      BenchError("unknown_arm: ...") per-arm before any workspace is touched for that arm.
  pilot.attest_record(arm_name: str, wm: int, note: str, *, runs_root: pathlib.Path | None = None)
      -> RunRecord
    — reads record.json, raises BenchError("record_not_found"/"record_not_done"/
      "record_not_scored") per the Reject list, else writes artifacts["spec_fidelity_audit"] via
      write_record_atomic (reused verbatim) and returns the updated RunRecord.

Schema: no new persistent schema — report reads the frozen RunRecord/validate shape verbatim
  (third reader, after runner+score); attest is a third WRITER of the same shape (after runner+
  score), adding only the already-tolerated-extra-key precedent (artifacts["spec_fidelity_audit"],
  same pattern as score.py's artifacts["metrics_warnings"]) — REQUIRED_METRICS/REQUIRED_ARTIFACTS
  unchanged, no sidecar file.
```

Glossary deltas: **spot-checked cell** — an arm×WM record.json whose `artifacts["spec_fidelity_audit"]` key is present, meaning a human has manually compared the judge's `spec_fidelity` verdict against the real workspace/transcript at least once; **provisioned arm** — an `Arm` returned by `resolve_setup_steps`, whose `setup_steps` have every `{REPO_ROOT}` token resolved to a concrete filesystem path, ready for `execute_wm`.
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07; provisioning spiked live pre-freeze; decisions: 3 per-WM tables + a headline WM3 summary table on top · attest writes a structured {reviewer, date, note} audit record · the LIVE pilot needs a final human go/no-go after build-verify, never auto-fires)
Reported: yes — freeze report + live-pilot cost envelope (~15 claude -p runs + 15 judge calls, ~$50–300) rendered; ⚠1 resolved by spike before approval

Least-sure flag surfaced at freeze: [spec] with provisioning spiked and confirmed (uv venv + editable install + `pilotspace-add init --yes --non-interactive`, live 2026-07-07), the least-sure remaining assumption is judge-verdict quality: the rubric judge's `spec_fidelity` scores have never met a real arm output, so the pilot's headline metric could be systematically miscalibrated across arms — mitigated by the frozen attest flow (report renders `(unaudited)` until a structured human spot-check exists) and by the human go/no-go before any live spend; if wrong: the rubric prompt iterates at observe, the contract shape (judge seam, attest, report) survives.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90%
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_report_renders_full_grid: arrange fixture "done"+scored record.json for all 5 arms × 3 WMs / act `report --runs-root <fixture>` / assert 3 tables, 5 rows each, 5 metric columns, evidence-link text present for every cell · covers: M1
  - test_report_missing_record_renders_not_run: arrange a runs tree missing gsd/wm2/record.json / act `report` / assert that row/metric cell == "not run", other cells unaffected · covers: M1
  - test_report_wm1_wm2_na_annotation: arrange a "done" wm1 record with regression_rate=0.0/context_rot_slope=0.0 / act `report` / assert both cells render "N/A (by definition)", never "0.00" · covers: M2
  - test_report_unaudited_suffix: arrange a "done" wm1 record with no spec_fidelity_audit key / act `report` / assert the spec_fidelity cell string ends with "(unaudited)" · covers: M3
  - test_attest_then_report_drops_unaudited: arrange the same fixture / act `pilot.attest_record("add", 1, "note")` then `report` / assert record.json's artifacts["spec_fidelity_audit"] set + report's cell no longer has the suffix · covers: M3, M4
  - test_resolve_setup_steps_substitutes_token: arrange add arm's real loaded Arm / act `resolve_setup_steps(arm, repo_root=tmp_path)` / assert the returned setup_steps line contains str(tmp_path), original arm object's setup_steps list unchanged (identity/equality check) · covers: M5
  - test_resolve_setup_steps_noop_without_token: arrange vanilla arm's loaded Arm / act `resolve_setup_steps(arm, repo_root=tmp_path)` / assert returned setup_steps == original setup_steps · covers: M5
  - test_add_arm_setup_succeeds_in_bare_sandbox: arrange a from-scratch tmp_path workspace + the real add.toml resolved against the REAL repo root / act `execute_wm` with a fake-agent argv (agent step itself injected/hermetic) / assert all 3 setup lines exit 0 and the record's status is not "failed" from a setup step · covers: M6 (⚠ this is the one test that touches the real filesystem/uv — marked slow, allowed to require `uv` on PATH; skip-with-reason if absent, never silently pass)
  - test_run_pilot_halts_arm_on_non_done_wm: arrange a fake-agent argv that succeeds for add/wm1+wm2 and fails for add/wm3, succeeds for all vanilla WMs / act `run_pilot(arms=["add","vanilla"], ...)` / assert add has wm1/wm2 done+scored, wm3 failed+unscored, vanilla all 3 done+scored, and score_record was never called for add/wm3 (spy/monkeypatch count) · covers: M7, M8
  - test_run_pilot_resumes_without_reinvoking: arrange add's 3 WMs already done+scored on disk / act `run_pilot(arms=["add"], resume=True, agent_cmd=<fake that asserts never called>)` / assert fake agent invocation count == 0, record.json files byte-unchanged · covers: M9
  - test_find_resume_point_noncontiguous_guard: arrange wm1+wm3 record.json status="done", no wm2 / act `find_resume_point(<arm>)` / assert result == 4 (pins the documented real behavior; comment cites bench-runner §7) · covers: M10
  - test_report_rejects_unknown_arm: arrange `report --arm ghost` / act CLI / assert exit 2 "unknown_arm", no output printed · covers: R1
  - test_report_rejects_invalid_wm: arrange `report --wm 9` / act CLI / assert exit 2 "invalid_wm" · covers: R2
  - test_attest_record_not_found: arrange no wm2/record.json / act `attest_record("add", 2, "x")` / assert BenchError "record_not_found", no file created · covers: R3
  - test_attest_record_not_done: arrange wm1 record status="failed" / act `attest_record("add", 1, "x")` / assert BenchError "record_not_done", record.json unchanged · covers: R4
  - test_attest_record_not_scored: arrange "done" wm1 record with metrics["spec_fidelity"]==0.0 (placeholder, unscored) / act `attest_record("add", 1, "x")` / assert BenchError "record_not_scored", record.json unchanged · covers: R5
  - test_run_pilot_rejects_unknown_arm: arrange arms=["ghost"] / act `run_pilot(arms=["ghost"])` / assert BenchError "unknown_arm", no benchmark/runs/ghost/ directory created · covers: R6
  - test_resolve_setup_steps_rejects_bad_repo_root: arrange repo_root="/does/not/exist" / act `resolve_setup_steps(arm, repo_root="/does/not/exist")` / assert BenchError "invalid_repo_root", no subprocess attempted · covers: R7
</test_plan>

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/report.py` `benchmark/pilot.py` `benchmark/run.py` `benchmark/arms/add.toml` `benchmark/tests/`
Strategy (ordered batches):
  1. `benchmark/arms/add.toml` — rewrite `setup_steps` to the 3-line `uv venv` / `uv pip install -e {REPO_ROOT}/add-method --python .venv/bin/python` / `.venv/bin/pilotspace-add init --yes --non-interactive` sequence — smallest, most isolated, no code dependency.
  2. `benchmark/pilot.py:resolve_setup_steps` — pure token-substitution function, testable standalone before anything else in this module exists.
  3. `benchmark/pilot.py:attest_record` — read -> eligibility guard clauses (record_not_found/not_done/not_scored) -> write_record_atomic; mirrors `score.py:score_record`'s exact guard-clause shape.
  4. `benchmark/pilot.py:run_pilot` — the per-arm sequencing loop (resolve -> resume-point -> execute_wm -> conditional score_record -> halt-on-non-done); the one orchestrator wiring the pieces above plus the already-frozen `execute_wm`/`score_record`.
  5. `benchmark/report.py:render_report` — pure function reading `benchmark/runs/` into markdown; N/A and (unaudited) annotation logic lives here, isolated from the CLI.
  6. `benchmark/run.py` — add the `report` subparser wiring `render_report`, mapping the two filter-validation Rejects to exit 2 (same pattern as existing `run`/`resume`/`score` handlers); add `pilot.py`'s own thin argparse CLI (`run-all`, `attest`) in its own `if __name__ == "__main__"` block, separate from `run.py`.
  7. `benchmark/runner/records.py` — NO code change; add the one `test_find_resume_point_noncontiguous_guard` test only, importing the existing frozen function unmodified (M10 is a guard test, not a fix).
Approach (domain strategy): same stdlib-first, fail-loud, guard-clause-before-any-I/O discipline `run_record.py`/`runner/core.py`/`score.py` already established — every new Reject case is an early `BenchError` raise before any disk write, matching `score_record`'s "compute everything into an in-memory dict, validate once, write once" all-or-nothing shape, now applied to `attest_record` (single-field update) and `run_pilot` (multi-WM sequencing halted on the first non-"done" result rather than continuing into an inconsistent state).
Data strategy: no new schema — `report` is a third READER of the frozen `RunRecord`/`validate` shape (after runner, score); `attest` is a third WRITER adding one more tolerated-extra `artifacts` key (`spec_fidelity_audit`), following score.py's own `metrics_warnings` precedent exactly; `run_pilot` writes nothing itself — it is pure orchestration delegating every actual write to `execute_wm`/`score_record`'s own `write_record_atomic` calls.
Pattern: orchestrator-over-frozen-primitives pattern — `run_pilot` is a thin sequencing loop composed entirely of already-frozen, already-tested building blocks (`load_arm`, `execute_wm`, `score_record`, `find_resume_point`), the same "don't reimplement, import and sequence" discipline the objective's constraint demands; `report` extends the fixture-and-oracle pattern one more step (bench-scoring's own Observe-block phrase) as the harness's final CONSUMER, turning scored records into a human-readable comparison.
Optimization stance: correctness-first, no perf budget for the hermetic suite (pilot scale, matches every prior bench-* task's stance); ⚠ least-trusted facet: the concrete `uv venv`/`uv pip install` provisioning lines (§1/§3 ⚠) — budget is "prove it works against one real bare sandbox" (test_add_arm_setup_succeeds_in_bare_sandbox), not "assume the reasoning is correct without ever running it."
Persona (required): methodology-engine-dev — same fail-loud, deterministic, stdlib-first adaptation every prior bench-* task used; no report/orchestration-specific persona exists yet, and none is warranted (same domain).
Spawn isolation (default): worktree — no shared-tree reason applies (single-agent build, no parallel spawn needed).
Known-problem fixes:
  - trap: `uv`/`uv venv` unavailable on the build/CI machine → planned fix: `test_add_arm_setup_succeeds_in_bare_sandbox` skips (with a loud, named reason) rather than silently passing or hard-failing the whole suite, if `uv` is not found on PATH.
  - trap: `run_pilot` continuing to WM2/WM3 after a non-"done" WM1, producing metrics against a broken workspace → planned fix: M8's explicit halt-on-non-done branch, tested directly (test_run_pilot_halts_arm_on_non_done_wm).
  - trap: `attest_record` overwriting a field other than `spec_fidelity_audit` → planned fix: read the full record, mutate only `artifacts["spec_fidelity_audit"]` in the in-memory copy, re-`validate()` the complete dict before `write_record_atomic` (mirrors score.py's own read-modify-write discipline).
  - trap: `report` crashing on a partially-run pilot (some arm×WM cells missing) → planned fix: M1's "not run" cell rendering is the FIRST thing implemented and tested, before any "happy path all-done" test.
Strategy actually used: as planned, batches 1-7 in the declared order, with one addition — after batch 6 (CLI wiring), a coverage pass added two CLI-level tests (`test_cli_attest_success_and_rejection`, `test_cli_run_all_rejects_unknown_arm`) exercising `pilot.py main()`'s `attest`/`run-all` argparse paths directly, since the internal-function tests alone left `pilot.py`'s CLI branch under the 90% coverage target (60% pilot.py-only); this raised combined pilot.py+report.py coverage to 96%. No other deviation from the strategy or scope.
Safety rule (feature-specific): a `run_pilot` sequence is per-arm all-or-nothing-forward: once a WM's `execute_wm` result is not `"done"`, no further WM in that arm's sequence is ever attempted (no partial/inconsistent workspace is ever built upon) — but a halt on one arm never blocks or corrupts any other arm's independent sequence.
Code lives in: `benchmark/`
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib + pytest + `uv` as an external CLI tool, not a Python dependency); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 80/80 green (`uv run --with pytest pytest benchmark/tests -q`, re-run independently at gate)
- [x] coverage did not decrease — pilot.py 95% (106 stmts, 5 miss: lines 212-214 `run-all` json-print loop tail, 226/231 `unknown command`/`__main__` guards), report.py 97% (61 stmts, 2 miss: 34-35 a `BenchError` parse-failure branch in `_load_record`) — matches build's claimed 95%/97% exactly, combined 96%
- [x] no test or contract was altered during build — `git diff 876254a..0c716f0` (tests-commit → build-commit) touches only `benchmark/arms/add.toml`, `benchmark/pilot.py`, `benchmark/report.py`, `benchmark/run.py`, and a 1-line TASK.md phase bump; zero bytes changed under `benchmark/tests/`
- [x] the green was EARNED, not gamed — see Refute-read verdict below
- [x] concurrency / timing of the risky operation is safe — `run_pilot` is a single-threaded `for arm in arms: for wm in sequence:` loop; no threads/async/multiprocessing; `write_record_atomic` (reused verbatim) does temp-file+`os.fsync`+`os.replace`, so a crash mid-write leaves the prior complete record or nothing, never a partial file
- [x] no exposed secrets — 🟡 one concern found (see Security lens below), no HARD-STOP
- [x] layering & dependencies follow CONVENTIONS.md — orchestrator-over-frozen-primitives; pilot.py/report.py import execute_wm/score_record/find_resume_point/write_record_atomic verbatim, never reimplement; stdlib-first (argparse, dataclasses, pathlib, json only)
- [ ] a person reviewed and approved the change — pending human gate (this is the verify recommendation feeding that gate)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] `python benchmark/run.py report` against the hermetic fixture tree renders 3 markdown tables (one per WM), every cell populated (real value / N/A-by-definition / (unaudited) / not-run), each numeric cell carrying an evidence link — confirmed by `test_report_renders_full_grid` + `test_report_missing_record_renders_not_run`.
- [x] the real `add` arm's rewritten `setup_steps`, resolved via `resolve_setup_steps` against this repo's real path, complete with exit 0 in a from-scratch bare sandbox directory (no pre-existing venv/site-packages) — confirmed live at the gate: re-ran `test_add_arm_setup_succeeds_in_bare_sandbox` in isolation (`pytest -k bare_sandbox`), PASSED against the real repo root (`uv` present on PATH — not a skip); asserts all 3 transcript `setup:` lines contain "exit 0".
- [x] `pilot.py run-all` against a fully-fixtured fake-agent+fake-judge pair sequences all 5 arms × 3 WMs (or halts an arm early on an injected failure) with zero live `claude`/live-LLM subprocess calls — confirmed by `test_run_pilot_halts_arm_on_non_done_wm` + the AST-based `test_no_live_claude_call_in_this_module` (walks every function body except itself, asserts no string constant contains "claude").
- [x] `pilot.py attest` followed by `report` visibly flips one cell's unaudited annotation off while leaving every other cell (and every other artifacts field on that same record) untouched — confirmed by `test_attest_then_report_drops_unaudited` (asserts "(unaudited)" present before, absent after, "0.82" value preserved).
- [ ] LIVE-PILOT expectation (not a unit test — a §6/§7 VERIFY/OBSERVE activity once BUILD is green): running the real `pilot.py run-all` end-to-end for at least the `add` arm against the live `claude -p` CLI produces 3 real `record.json` files with non-placeholder `spec_fidelity`/`tokens_total`/`cost_usd` values, and `report` renders a real (not fixture) arm-vs-arm table from them — this is what a human running the actual pilot should SEE; it cannot be asserted by a hermetic test and is not claimed as "tested" by any test in §4.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `resolve_setup_steps`/`attest_record`/`run_pilot` used by `pilot.py main()`'s CLI + by `benchmark/tests/test_pilot.py`; `render_report` wired into `run.py`'s new `report` subparser (`benchmark/run.py:133`) and used directly by `test_report.py`/`test_attest_then_report_drops_unaudited`; the guard test in `test_runner_records.py` imports `find_resume_point` (unmodified) — confirmed by grep + read of `benchmark/run.py` L20-24, L120-138 and `benchmark/pilot.py` L20-24.
- [x] DEAD-CODE (code) — no orphaned symbol: every function in `pilot.py`/`report.py` is either CLI-reachable (`main`/`_build_parser`) or test-covered per the coverage report (95%/97%, misses are only argparse-error/`__main__` boilerplate lines 212-214/226/231 in pilot.py and one `BenchError`-catch branch in report.py's `_load_record`, not unreachable code).
- [ ] SEMANTIC (prose / non-code) — n/a, this task's deliverable is code (pilot.py/report.py/add.toml), not prose; §0-§5 of this TASK.md itself were read in full during this verify pass.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by grepping the current tree for each: `execute_wm` (benchmark/runner/core.py), `score_record` (benchmark/score.py), `find_resume_point`/`write_record_atomic`/`DEFAULT_RUNS_ROOT` (benchmark/runner/records.py), `load_arm`/`Arm`/`ARM_NAMES` (benchmark/arms/loader.py), `RunRecord`/`validate`/`BenchError` (benchmark/schema/run_record.py) — all 11 anchors present at their §0/§3-named paths, no move/rename since Ground SHA `4f75b73`.
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — none moved; no discrepancy found.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (add-verify) · adversarially checked:
  - `resolve_setup_steps`: confirmed a real `{REPO_ROOT}` substitution (not a stub) — `test_resolve_setup_steps_substitutes_token` asserts the tmp_path string literally appears in the resolved line AND the original arm's `setup_steps` list is unchanged (identity-safety, `dataclasses.replace` not in-place mutation); the no-token passthrough test asserts full list equality, not just "no crash".
  - `attest_record`: read the full guard-clause chain (record_not_found → record_not_done → record_not_scored) and confirmed each Reject test byte-diffs the on-disk record.json before/after (`before_bytes == record_path.read_bytes()`) — a real no-write assertion, not a vacuous "raises" check.
  - `run_pilot`: confirmed resumability is real, not simulated — `test_run_pilot_resumes_without_reinvoking` monkeypatches `execute_wm`/`score_record` to `raise AssertionError` if called at all, so the test fails loudly if resume silently re-invokes anything; the halt test uses a real fake-agent subprocess (nonzero exit) wired through the actual `execute_wm`, confirms `score_record` is never called for the failed WM via a call-log spy, and confirms the OTHER arm (vanilla) is unaffected (arms-are-independent, per M8/M9).
  - `render_report`: read `_render_cell`'s exact branch order — N/A-by-definition checked before the unaudited-suffix logic, so a WM1/WM2 cell never falls through to a bare numeric value; evidence links are real relative record.json/transcript paths built from `record.artifacts["transcript"]`, not hardcoded fixture strings.
  - the one real (non-hermetic) test, `test_add_arm_setup_succeeds_in_bare_sandbox`, was independently re-run in isolation at this gate (`pytest -k bare_sandbox`) — PASSED live against the real repo root with `uv` present (not a skip), confirming the provisioning claim is real, not asserted-and-never-exercised.
  - confirmed via `git diff 876254a..0c716f0` that build touched ZERO bytes under `benchmark/tests/` — the green suite was never adjusted to fit the implementation.
  No overfit, no vacuous asserts, no stubbed-away logic found.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (add-verify)
1. Security: CLEAR — no shell=True anywhere (`_run_setup_steps` uses `shlex.split()` + list-argv, frozen/unmodified); `{REPO_ROOT}` substitution is a plain `str.replace`, no eval/exec/shell-interpolation, so no command-injection vector even with an adversarial repo_root string. 🟡 one non-security ROBUSTNESS concern found and folded into Observe below: a `repo_root` path containing a space is NOT quoted before substitution, so `shlex.split()` on the resulting line silently mis-tokenizes the argv (verified live: `/tmp/my repo` → `['uv','pip','install','-e','/tmp/my','repo/add-method',...]`) — a corrupted-but-not-injected argv, would surface as a confusing setup-step failure exactly as §1 Reject R7's rationale already anticipates for a bad path, just not for THIS specific bad-path shape. Attest `note` and `spec_fidelity_audit` flow through `json.dumps` (stdlib escaping) into the record — no injection surface there.
2. Concurrency: CLEAR — `run_pilot` is single-threaded, strictly sequential per-arm/per-WM; `write_record_atomic` (reused verbatim, unmodified) does temp-file+fsync+`os.replace`, so no torn-write hazard even if the live pilot process were killed mid-WM.
3. Architecture: CLEAR — orchestrator-over-frozen-primitives layering held throughout; `pilot.py`/`report.py` import and reuse `execute_wm`/`score_record`/`find_resume_point`/`write_record_atomic` verbatim, zero reimplementation; stdlib-first (argparse/dataclasses/pathlib/json only, no new third-party dependency).
Verdict: PASS
Residue: none blocking — one 🟡 concern (repo_root-with-spaces argv mis-tokenization) recorded in §7 Observe as a forward spec delta, not a build defect (no test scenario named this shape; real REPO_ROOT in this repo has no space).
Binding: advisory — non-security concern; does not gate this PASS.

### GATE RECORD
Reported: yes — this §6 evidence block rendered before recording the outcome below.
Outcome: PASS
Reviewed by: add-verify (self) · date: 2026-07-07
Note: the human gate (checkbox "a person reviewed and approved the change") and the LIVE PILOT go/no-go remain open — this PASS covers the BUILD (hermetic suite + provisioning-in-isolation), not the live 5×3×1 spend, which is its own separate §6/§7 VERIFY/OBSERVE activity per the frozen contract's own note.

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-arm setup-step failure rate during the live pilot (a high `add`-arm setup failure rate = the ⚠ provisioning assumption was wrong, not an arm defect) · `(unaudited)` cell count in the rendered report after the pilot (should shrink toward 2-3 spot-checked cells per the absorbed delta, never stay at 15/15) · arms halted mid-sequence (a non-"done" WM1/WM2 for a competitor arm may be a fairness/setup problem, not a real arm defect) · `rule_coverage_gap` warning on this task's own Reject `covers:` tags (routed, not absorbed — watch whether it recurs; if so, escalate to the engine-side task named in §0).

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (2026-07-07; provisioning spiked live pre-freeze; decisions: 3 per-WM tables + a headline WM3 summary table on top · attest writes a structured {reviewer, date, note} audit record · the LIVE pilot needs a final human go/no-go after build-verify, never auto-fires))
- [AI] build — approach: same stdlib-first, fail-loud, guard-clause-before-any-I/O discipline `run_record.py`/`runner/core.py`/`score.py` already established — every new Reject case is an early `BenchError` raise before any disk write, matching `score_record`'s "compute everything into an in-memory dict, validate once, write once" all-or-nothing shape, now applied to `attest_record` (single-field update) and `run_pilot` (multi-WM sequencing halted on the first non-"done" result rather than continuing into an inconsistent state).
- [AI] build — data strategy: no new schema — `report` is a third READER of the frozen `RunRecord`/`validate` shape (after runner, score); `attest` is a third WRITER adding one more tolerated-extra `artifacts` key (`spec_fidelity_audit`), following score.py's own `metrics_warnings` precedent exactly; `run_pilot` writes nothing itself — it is pure orchestration delegating every actual write to `execute_wm`/`score_record`'s own `write_record_atomic` calls.
- [AI] build — pattern: orchestrator-over-frozen-primitives pattern — `run_pilot` is a thin sequencing loop composed entirely of already-frozen, already-tested building blocks (`load_arm`, `execute_wm`, `score_record`, `find_resume_point`), the same "don't reimplement, import and sequence" discipline the objective's constraint demands; `report` extends the fixture-and-oracle pattern one more step (bench-scoring's own Observe-block phrase) as the harness's final CONSUMER, turning scored records into a human-readable comparison.
- [AI] build — optimization stance: correctness-first, no perf budget for the hermetic suite (pilot scale, matches every prior bench-* task's stance); ⚠ least-trusted facet: the concrete `uv venv`/`uv pip install` provisioning lines (§1/§3 ⚠) — budget is "prove it works against one real bare sandbox" (test_add_arm_setup_succeeds_in_bare_sandbox), not "assume the reasoning is correct without ever running it."
- [AI] build — strategy used: as planned, batches 1-7 in the declared order, with one addition — after batch 6 (CLI wiring), a coverage pass added two CLI-level tests (`test_cli_attest_success_and_rejection`, `test_cli_run_all_rejects_unknown_arm`) exercising `pilot.py main()`'s `attest`/`run-all` argparse paths directly, since the internal-function tests alone left `pilot.py`'s CLI branch under the 90% coverage target (60% pilot.py-only); this raised combined pilot.py+report.py coverage to 96%. No other deviation from the strategy or scope.
- [AI] verify — gate PASS (reviewed by add-verify (self))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] `rule_coverage_gap` audit-format question ROUTED (not absorbed) — the `covers:` tag parser mismatch bench-scoring surfaced is an engine-side (`.add/tooling/`) concern outside this task's `benchmark/` Scope; needs its own future task (evidence: bench-scoring TASK.md §7).
- [SPEC · open] `resolve_setup_steps`'s `{REPO_ROOT}` token substitution is a plain unquoted `str.replace`; a `repo_root` path containing a space silently mis-tokenizes the resulting `shlex.split()` argv instead of failing loudly (evidence: verify-gate repro, `/tmp/my repo` → argv split at the space) — not exploitable (no shell=True, no injection), but a real robustness gap distinct from R7's already-handled "path doesn't exist" case; fix (quote the substituted token, e.g. `shlex.quote(str(repo_root))`) is small and low-risk but out of THIS task's frozen §3 shape — route to a future fast task.

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

