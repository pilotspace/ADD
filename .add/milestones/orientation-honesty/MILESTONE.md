# MILESTONE: Honest WM1 <=12: isolate the harness + make surfaces self-explaining

goal: Reach an HONEST WM1 <=12 calls by (a) removing the harness-induced startup confusion so the benchmark measures the method not the nesting, and (b) making engine surfaces self-explaining so the agent stops probing `--help` (5.0 calls/rep) and grepping engine internals — the real reducible levers the call-residuals pre-measure anatomy found, distinct from the four the six-phase report named
rationale: sub-milestone — human decision 2026-07-14 'keep investigating before the paid re-measure'. The pre-measure anatomy (benchmark/results/2026-07-callres-preflight-anatomy.md) of the actual sixphase-r{1,2,3} transcripts proved: TRUE double-init=0 and unknown-command-typo=0 (two of call-residuals' four tasks target failure modes that never fire), the dominant unaddressed lever is `--help` flag-discovery (5.0/rep), and ~7-13 cmds/rep of startup confusion are HARNESS-induced (workspace nested inside AIDD-Book's own `.add/`). ≤12 is reachable only with lever B, measured honestly only after harness isolation.
stage: mvp · status: active · created: 2026-07-14T14:33:51+00:00
release: pending
relates-to: call-residuals, add-bench-2

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  (1) benchmark harness: run each WM workspace isolated from any ancestor `.add/` so the agent's first `status`/`init` resolves the workspace, not the parent repo — an honest baseline. (2) engine message-layer: `status`/`init` warns when it resolved an ANCESTOR project; `status`/`advance` emit the paste-ready NEXT command WITH flags (kills the `--help` flag-discovery habit); `advance` carries the guide's key hint (kills `guide` re-reads); `scope_violation`/gate message explains the resolution rule + a paste-ready `re-cross` (kills `_in_scope` spelunking).
Out: no change to the FROZEN 5-metric benchmark set, the oracle/judge, or the scoring math; no phase-lifecycle change; the paid re-measure itself (human-gated, a separate spend); the init-idempotent-nudge / help-habit-kill tasks already merged (kept — defensively correct even though their levers measured 0).

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): engine `add-method/tooling/add.py` (×4 twins) — `cmd_status`, `_next_footer`, `cmd_advance`, the `scope_violation` return path, root-resolution (`find_root`/`_root` in `add_engine/io_state.py`); `add-method/tooling/engine_pin.py` (×3 twins, ENGINE_MD5); `.add/SEAMS.md` line pins. Benchmark `benchmark/runner/core.py` (`execute_wm`, `workspace_dir`), `benchmark/pilot.py` (setup), `benchmark/tests/` for the isolation guard.
Anchors: `_active_task`, `_next_footer`, `_declared_scope`, `_in_scope`, `scope_violation`, `execute_wm`, `workspace_dir`, `PINNED_MODEL`.
Honors (conventions): message-layer tasks change NO gate/enforcement path (except the harness task, which IS a benchmark-enforcement change and runs the full flow); engine edits sync ×4 twins byte-identically + re-pin ENGINE_MD5 + migrate SEAMS; NEVER sync test files across twins; red-before-green; frozen §3 contract; recorded §6 gate; security = HARD-STOP.
Issues/Risks (shared): the `--help`/next-command hint must stay a HINT, never a gate (propose-not-impose, per scope-first-draft precedent); the harness isolation must not break oracle-injection isolation (`check_isolation.py`) or the prior-WM workspace carry-forward (`runs_root/arm/wm{n-1}/workspace`); a status/advance wording change ripples into any test pinning that phrase (the full fence is authority, not grep).

## Shared decisions & glossary deltas   (living — every task must honor these)
- "self-explaining surface" — an engine output that hands the agent the exact next action (command + flags, or the resolution rule + paste-ready repair) so it never needs `--help` or to grep engine internals. The measure of success is a call/turn the agent DIDN'T have to make.
- honest baseline — a benchmark number that measures the method, not the measurement apparatus; the workspace-nesting artifact is removed at the source, not annotated away.

## Shared / risky contracts (freeze these first)
- harness workspace-isolation contract -> owning task `harness-workspace-isolation` (the runner boundary that stops root-walk at the workspace; freeze first — the other tasks assume the honest baseline)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] harness-workspace-isolation   depends-on: none   — the WM runner isolates the workspace from any ancestor `.add/` (root-walk boundary via opt-in `ADD_ROOT_CEILING`) so the agent's first `status`/`init` resolves the workspace, not AIDD-Book's parent project; kills the 7-13 startup-confusion cmds/rep at the source. FULL flow. **DONE `a87ed1e`** (ENGINE_PKG_MD5→955023db).
- [x] status-ancestor-warn         depends-on: none   — `status`/`init` prints a loud one-line warning when it resolved an ANCESTOR project; real-world value for nested/monorepo dirs + defense-in-depth behind the harness fix. Message-layer. **DONE `1d9a211`** (ENGINE_MD5→9476543399).
- [x] orient-map (was next-command-hints / LEVER B)  depends-on: none   — PIVOTED: lever B (next-command-with-flags) was found ~80% already shipped by prior tasks (first-call-ergonomics / skip-error-ergonomics / engine-hint-batch-ops — the sixphase agent already ran the flagged `freeze`/`new-task` forms). The true residual was the bare `add.py`/`--help` 50-choice dump → `_FLOW_MAP` leads the top-parser help + the no-subcommand error. **DONE `0798bd2`** (ENGINE_MD5→a88bc24c).
- [x] guide-fold                   depends-on: none   — LEVER E: a completing `advance` folds in the LANDED phase's guide chapter (`guide: .add/docs/<chapter>` + "no re-run `add.py guide`" cue) above the footer; non-duplicative (footer already carries command+why). **DONE `91b3371`** (ENGINE_MD5→c8e0a3e5; SEAMS 5711→5723).
- [~] scope-violation-explain      depends-on: none   — LEVER C: **NOT BUILT — found ALREADY SHIPPED** by the prior scope-gate-repair-path work. M1 (freeze-time prevention, `add.py:1487`) warns on the template-default §5 + names `re-cross --by`; M2 (gate-time repair, `add.py:5907`) explains the full resolution rule + emits the paste-ready `add.py re-cross --by <name>` + the revert alternative. The code comment at 5902-5905 records this exact fix already killed "the live-benchmark agent source-diving for ~10 turns to discover re-cross" — the precise pain this lever scoped. Human decision 2026-07-14: close at 4 tasks, no redundant 5th.

## Exit criteria (observable; map each to the task that delivers it)
- [x] In a fresh workspace nested under an ancestor `.add/`, the WM runner's agent resolves the workspace's OWN (absent-then-init'd) project — no root-walk to the parent — verified by a benchmark isolation test        (← harness-workspace-isolation: `benchmark/tests/test_workspace_isolation.py`)
- [x] `status` (full path) run in a dir with no local `.add/` but an ancestor `.add/` above prints an ancestor-resolved note naming the resolved path + the `init` remedy (stderr; `--json`/`--brief` stay silent)        (← status-ancestor-warn: `test_status_ancestor_warn.py`)
- [x] bare `add.py`/`--help` LEAD with the concise flow map (status/init/new-task/advance/freeze/gate) then the full list, instead of the 50-choice dump — pinned by a test (REPLACES the lever-B criterion; lever B's flagged next-command form was already shipped pre-milestone)        (← orient-map: `test_orient_map.py`)
- [x] a completing `advance` carries the LANDED phase's guide chapter above the footer, so orientation needs no separate `guide` call — pinned by a test        (← guide-fold: `test_guide_fold.py`)
- [x] a `scope_violation` return-to-build explains the resolution rule AND emits a paste-ready `re-cross --by` line — ALREADY SHIPPED by scope-gate-repair-path M1+M2 (`add.py:1487`, `add.py:5907`); pinned by the existing scope-gate tests        (← scope-violation-explain: pre-shipped, not re-built)
- [x] (paid, human-gated) WM1 re-measure IN THE ISOLATED HARNESS: fidelity 1.00 >= 0.97 MET · zero startup root-walk confusion MET in 9/9 measured reps (isolation held) · --help <= 1/rep PARTIAL (run-3: 1/3/0) · calls <= 12 mean **WAIVED 2026-07-23 — signed: Tin Dang** (decision: 'Fix + close on trend'). 5-run trend 27 → 18.7 → 15.0 → 14.3 → 13.3 mean calls (−51%), fidelity 1.00 on EVERY measured rep, rep-floor 10 (run-3 rep2); unflagged_freeze dead (flag slot), scope-grammar garbage dead (scope_unresolved), .venv/venv/.tox/.mypy_cache/.ruff_cache/.eggs + *.egg-info pruned from the scope walk. Evidence: .add/benchmark-remeasure-2026-07-23.md

## Close — ship review   (AI fills when every task is done)
> Whole-milestone, cross-task review the AI fills in. Evidence behind the EXISTING engine gate.

### Ship by domain   (what changed, per bounded context)
- tooling : `add_engine/io_state.py` `find_root` gained opt-in `ADD_ROOT_CEILING` (bounded upward walk); `add.py` gained `_ancestor_note` (status ancestor warn), `_FLOW_MAP` + `_AddArgParser.format_help`/`error` (orient-map), the guide-fold print in `cmd_advance`. ×4 twins synced; ENGINE_PKG_MD5→955023db, ENGINE_MD5→c8e0a3e5; SEAMS `_declared_scope` 5688→5711→5723. Lever C (scope_violation explain) untouched — already shipped.
- benchmark : `runner/core.py` `_invoke_once` sets `ADD_ROOT_CEILING=<cwd>` so each WM workspace resolves its own project, not AIDD-Book's parent — the honest baseline.
- skill   : untouched (no guide hint needed a doc mirror; guide-fold points at existing chapters).
- book    : untouched.

### Cross-task evidence   (one row per task)
- harness-workspace-isolation : gate=PASS · tests=green (test_findroot_ceiling + benchmark/tests/test_workspace_isolation) · residue=none
- status-ancestor-warn        : gate=PASS · tests=green (test_status_ancestor_warn) · residue=none
- orient-map                  : gate=PASS · tests=green (test_orient_map, 4 asserts) · residue=none
- guide-fold                  : gate=PASS · tests=green (test_guide_fold, 4 asserts; full fence 3611 pass, the lone bundle-parity fail was a gitignored .pyc from the run) · residue=none
- scope-violation-explain     : PRE-SHIPPED (scope-gate-repair-path M1+M2) · no new code · human-accepted 2026-07-14

### Goal met?
- [x] each built Exit criterion is satisfied by a Cross-task evidence row (cited above); lever C's criterion is met by pre-shipped code (scope-gate-repair-path M1+M2)
- [x] goal: reach an honest WM1 <=12 — resolved by the signed waiver above (13.3 measured, trend −51%, fidelity 1.00; the strict <=12 mean waived by the human 2026-07-23).
- Human decision 2026-07-14: close the BUILD at 4 tasks (lever C redundant); the milestone GOAL stays open on the deferred paid re-measure.

## Release steps   (AI-DEFINED — engine records, human gate)
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] (paid, human-gated) run the isolated-harness WM1 re-measure; record calls/fidelity vs the <=12 bar
- [ ] on MET: fold the call-residuals + orientation-honesty pair into the next release notes
