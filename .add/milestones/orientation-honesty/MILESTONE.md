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
- [ ] harness-workspace-isolation   depends-on: none   — the WM runner isolates the workspace from any ancestor `.add/` (root-walk boundary / tmpdir-style setup) so the agent's first `status`/`init` resolves the workspace, not AIDD-Book's parent project; kills the 7-13 startup-confusion cmds/rep at the source. FULL flow (benchmark-enforcement change).
- [ ] status-ancestor-warn         depends-on: none   — `status`/`init` prints a loud one-line warning when it resolved an ANCESTOR project ("no `.add/` here; using project at <path> — run `init` to scope here"); real-world value for nested/monorepo dirs + defense-in-depth behind the harness fix. Message-layer.
- [ ] next-command-hints           depends-on: none   — LEVER B: `status`/`advance` emit the fully-formed NEXT command WITH its flags (paste-ready), so the agent stops running `<cmd> --help` before first use (5.0 calls/rep, the biggest call lever). Stays a hint, never a gate. Message-layer.
- [ ] guide-fold                   depends-on: none   — LEVER E: `advance` output carries the current phase guide's key hint so the agent stops re-running `add.py guide` for orientation (1-2 calls/rep). Message-layer.
- [ ] scope-violation-explain      depends-on: none   — LEVER C: the `scope_violation`/return-to-build message explains the resolution rule (declared vs resolved paths) AND emits a paste-ready `re-cross --by "<you>"`, so the agent stops grepping `_in_scope`/`_declared_scope` internals to recover (5-11 spelunking cmds/rep). Message-layer, gate-preserving.

## Exit criteria (observable; map each to the task that delivers it)
- [ ] In a fresh workspace nested under an ancestor `.add/`, the WM runner's agent resolves the workspace's OWN (absent-then-init'd) project — no root-walk to the parent — verified by a benchmark isolation test        (← harness-workspace-isolation)
- [ ] `status` (full path) run in a dir with no local `.add/` but an ancestor `.add/` above prints an ancestor-resolved note naming the resolved path + the `init` remedy (stderr; `--json`/`--brief` stay silent). Scoped to the read command where the confusion fired — `init` creates at cwd, resolving no ancestor        (← status-ancestor-warn)
- [ ] `status` and `advance` output contains the exact next command with its required flags (e.g. `add.py freeze --by "<name>" --cross`), copy-pasteable — pinned by a test asserting the flagged form        (← next-command-hints)
- [ ] `advance` output carries the destination phase's key guide hint, so orientation needs no separate `guide` call — pinned by a test        (← guide-fold)
- [ ] a `scope_violation` return-to-build prints the declared-vs-resolved paths AND a paste-ready `re-cross` line — pinned by a test        (← scope-violation-explain)
- [ ] (paid, human-gated) WM1 re-measure IN THE ISOLATED HARNESS: calls <= 12 mean, fidelity >= 0.97 held, `--help` flag-probes <= 1/rep, zero startup root-walk confusion in transcripts

## Close — ship review   (AI fills when every task is done)
> Whole-milestone, cross-task review the AI fills in. Evidence behind the EXISTING engine gate.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py status/advance/scope_violation surfaces + benchmark/runner isolation — fill at close>
- skill   : <untouched unless a guide hint needs a doc mirror — fill at close>
- book    : <untouched — fill at close>

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS> · tests=<n green> · residue=<none>

### Goal met?
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: reach an honest WM1 <=12 — the isolated-harness re-measure line is the proof.

## Release steps   (AI-DEFINED — engine records, human gate)
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] (paid, human-gated) run the isolated-harness WM1 re-measure; record calls/fidelity vs the <=12 bar
- [ ] on MET: fold the call-residuals + orientation-honesty pair into the next release notes
