# TASK: headless claude -p runner: sandboxed arm workspaces, WM sequencing with resume, timeout/retry, transcript+token capture

slug: bench-runner · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: contract   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `benchmark/schema/run_record.py:RunRecord`, `:validate`, `:BenchError`, `:REQUIRED_METRICS`, `:REQUIRED_ARTIFACTS`, `:VALID_STATUSES` — frozen per-run shape (arm, wm, rep, status, metrics, artifacts); runner is the FIRST real writer/reader of this shape.
  - `benchmark/arms/loader.py:load_arm`, `:Arm`, `:ARM_NAMES`, `:PIN_REQUIRED_ARMS` — arm recipe loader; runner drives `setup_steps`/`prompt_wrapper` per arm.
  - `benchmark/arms/add.toml:pin` — a repo-path pin string, not a resolvable ref (see Issues below).
  - `benchmark/workload/_oracle_lib.py:running_app`, `:http_call`, `:STARTUP_TIMEOUT_S`, `:POLL_INTERVAL_S` — HTTP driver + startup-poll heuristic; shipped uncalled by bench-scaffold, this task is its first real caller.
  - `benchmark/workload/wm{1,2,3}/PROMPT.md` — the 3 fixed prompts the runner feeds an arm verbatim per WM, each carrying the `python -m app` / `$PORT` entry-contract line (wm1 L20, wm2 L23, wm3 L24).
  - `benchmark/check_isolation.py:find_leaks`, `:main` — invoked today only via `subprocess.run` from tests; runner is the first NON-test caller (must run it at every workspace teardown per bench-scaffold's Observe note).
  - `.gitignore:49` `benchmark/runs/` — the run-record output root the runner writes into; already gitignored, runner must create nothing outside it.
Context (working folder): `benchmark/tests/conftest.py` (fixture shapes reused for hermetic runner tests) · `benchmark/pytest.ini` (registers `regression` marker) · no CLI entrypoint exists yet under `benchmark/` — `run.py` is net-new, no file to extend.
Honors (patterns / conventions): stdlib-first, fail-loud `BenchError` on any malformed shape (never silently coerce) — the pattern `run_record.py`/`loader.py` already establish; subprocess calls use list-form argv only (no shell string) per bench-scaffold's Advisor security lens; CLAUDE.md's "design for failure: timeouts, retries, circuit breakers, rollback strategy in IO request" applies directly — this task IS that IO request.
Seams consulted: none — no SEAMS.md entry covers subprocess orchestration or resume-ledger shape yet; this task originates the seam.
Anchors the contract cites: `RunRecord`/`validate`/`BenchError` (benchmark/schema/run_record.py) · `load_arm`/`Arm` (benchmark/arms/loader.py) · `running_app`/`http_call` (benchmark/workload/_oracle_lib.py) · `check_isolation.main` (benchmark/check_isolation.py) · `benchmark/workload/wm{1,2,3}/PROMPT.md`.
Issues/Risks (→ feed §1):
  - the `add` arm's `pin` field is a repo-path comment string ("add-method (this repo, path pin...)"), not a reproducible ref — carried spec delta from bench-scaffold; this task must resolve it to something recorded in the run record at execution time (e.g. `git rev-parse HEAD` of the pinned path), not just pass the string through.
  - `_oracle_lib.running_app`/`http_call` are dead code today (bench-scaffold's own DEAD-CODE finding) — this task is on the hook to wire them into a real caller or the dead-code finding recurs.
  - the ⚠ startup-detection heuristic (poll-until-`/bookings`-answers, 10s deadline) is flagged by bench-scaffold as untested against a slow-starting real arm-built app — named risk to harden here, at minimum bound retry/timeout behavior around it, not silently trust it.
  - no live `claude` CLI in tests (task constraint) — the runner's own subprocess-invocation point must be swappable (injectable argv/command) so tests can substitute a fake agent script; there is no existing seam for this, it must be designed fresh.
  - resume semantics: nothing in the frozen run-record schema currently marks "in-progress" vs "done" mid-WM — a crash mid-write must not leave a record `validate()` would accept as complete (atomic-write requirement).
Related intent: MILESTONE.md exit criteria "a killed run resumes from the last completed WM without redoing finished work" and "`run.py run --arm add --wm 1` completes headlessly and writes a schema-valid run record" — both owned by this task. GLOSSARY: `arm`, `workload milestone`, `oracle suite`, fairness floor (all MILESTONE.md "Shared decisions").
Ground SHA: a0d7183

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: headless per-arm×WM runner (`benchmark/run.py run|resume`) — sandboxed workspace, WM sequencing with resume, timeout/retry, transcript+token capture, schema-valid run records.
Framings weighed:
  sequential single-process loop, one arm×WM at a time, driving the agent through an injectable command factory (chosen) — matches the pilot's stated scale (5×3×1), keeps failure isolation trivial (one subprocess, one workspace, one record), and gives tests a clean seam (swap the real `claude -p` argv for a fake-agent script) without inventing a process-pool abstraction the milestone doesn't need yet.
  · per-arm process pool / async concurrency — rejected: MILESTONE.md scope explicitly caps this milestone at "statistical scale-up (3+ reps)" OUT; concurrency buys nothing at 1 rep and multiplies the retry/timeout/resume state-machine surface for no pilot benefit.
  · a separate JSON state-file ledger tracking WM progress — rejected: run-records are already the frozen, validated, arm×WM-keyed shape; a second ledger risks drifting out of sync with the records it's supposed to describe (two sources of truth for "what's done").
Must:
<must>
  - `run --arm <name> --wm <n>` loads the arm recipe via `load_arm`, creates one sandboxed workspace directory under `benchmark/runs/<arm>/wm<n>/`, runs `setup_steps` then invokes the agent command (real `claude -p` in production, an injectable argv in tests) with the WM's `PROMPT.md` wrapped per `prompt_wrapper`, and on completion writes exactly one `RunRecord` (via `validate`) to `benchmark/runs/<arm>/wm<n>/record.json`.
  - the agent invocation is bounded by a per-run timeout (configurable, sane default); on timeout the process is killed and a `RunRecord` with `status="timeout"` is written — never left half-written.
  - a run that fails transiently (nonzero exit, agent-invocation error) is retried up to a bounded retry count before the record is written as `status="failed"`; the retry count and each attempt's outcome are visible in the record's `artifacts`/transcript, not silently swallowed.
  - `resume --arm <name>` inspects existing `record.json` files under `benchmark/runs/<arm>/` to find the highest WM with `status="done"`, and continues sequencing from the next WM (1→2→3) without re-invoking the agent for an already-done WM.
  - every run captures a transcript (raw agent stdout/JSON stream) and a token count into the record's `artifacts`/`metrics` (`tokens_total`) — sourced from `claude -p`'s JSON output when available, or a documented fallback when not.
  - before invoking the agent, the runner's sandboxed workspace is confirmed to carry no oracle file at teardown via `check_isolation.main` — a detected leak is recorded (never silently ignored) and fails that run.
  - the `add` arm's path-pin is resolved to a reproducible reference (e.g. the pinned path's current `git rev-parse HEAD`) and that resolved ref is recorded in the run record's `artifacts`, not the raw comment string from `add.toml`.
  - `_oracle_lib.running_app`/`http_call` are called by this runner (post-agent, pre-record) to confirm the workspace's app answers its entry contract before scoring metadata is finalized — closing bench-scaffold's dead-code finding.
</must>
Reject:
<reject>
  - unknown `--arm` name (not in `ARM_NAMES`) -> "unknown_arm"
  - arm recipe fails `load_arm` validation (missing key, unpinned competitor arm) -> "invalid_arm_recipe" (re-raised from loader, not re-wrapped)
  - `--wm` outside {1,2,3} -> "invalid_wm"
  - `resume` called with no prior run records for the arm (nothing to resume from) -> "nothing_to_resume"
  - agent invocation exceeds the per-run timeout after exhausting retries -> record written with status="timeout" (not an exception — a recorded outcome)
  - a malformed/partial record would result from a crash mid-write -> "invalid_run_record" never reaches disk; the runner uses a write-to-temp-then-rename so a crash leaves either the OLD complete record or NO record, never a partial one
  - oracle-leak detected in the workspace at teardown -> "oracle_leak" (record status="failed", leak path logged), the run is not silently scored as done
</reject>
After:
<after>
  - `benchmark/runs/<arm>/wm<n>/record.json` exists, is `validate()`-clean, and its `status` accurately reflects what happened (done/timeout/failed) — no run ever leaves zero records after starting.
  - a killed/interrupted run, when `resume`d, does not re-invoke the agent for any WM already recorded `status="done"`.
  - the workspace directory used for a run contains no oracle file at the moment the record is written (`check_isolation` clean).
  - the `add` arm's resolved ref is a concrete, re-derivable value (a SHA), never the raw path-comment string.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ token-count sourcing from `claude -p`'s JSON stream output is assumed available and parseable per-turn — lowest confidence because this task has never actually invoked the real CLI (tests are hermetic-only, fake-agent seam) and the JSON schema of `claude -p` output is asserted from documentation/memory, not verified against this task's own evidence; if wrong: `tokens_total` silently under/over-counts, corrupting the `bench-scoring` task downstream and the pilot's cost metric.
  - [ ] the startup-detection heuristic in `_oracle_lib.running_app` (10s deadline, 0.2s poll) is assumed "good enough to harden with a retry wrapper" rather than needing a full rewrite — confirm or deny once a real arm-built app is driven through it; if wrong, the fix is bigger than this task's Strategy assumes.
  - [ ] `claude -p`'s exit code reliably distinguishes "agent finished (successfully or not)" from "process crashed" for the retry-vs-timeout-vs-failed classification — assumed true from general CLI convention, not confirmed against this specific tool's behavior.
  - [ ] resuming from run-records alone (no separate ledger) is sufficient even if a WM is retried multiple times before succeeding — assumed the LAST written record per WM is authoritative and prior failed-attempt records for the same WM are either overwritten or clearly superseded, not accumulated as ambiguous siblings.
</assumptions>

<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: run writes a done record on a fake agent's success   # M1
  Given a valid arm recipe and PROMPT.md for wm=1, with the agent command injected as a fake script that exits 0
  When `run --arm <name> --wm 1` executes
  Then `benchmark/runs/<name>/wm1/record.json` exists and `validate()` accepts it with status="done"

Scenario: timeout kills the process and records status=timeout   # M2
  Given a fake agent script that sleeps past the configured per-run timeout
  When `run` executes
  Then the process is killed, no zombie remains, and the record is written with status="timeout" — never half-written

Scenario: transient failure retries then records failed   # M3
  Given a fake agent script that exits nonzero every invocation
  When `run` executes with retry count N
  Then the agent is invoked exactly N+1 times, each attempt's outcome appears in artifacts/transcript, and the final record has status="failed"

Scenario: resume skips a WM already done   # M4
  Given `benchmark/runs/<name>/wm1/record.json` exists with status="done" and no wm2 record exists
  When `resume --arm <name>` executes
  Then the agent is invoked only for wm2 (never re-invoked for wm1), sequencing continues 2->3

Scenario: transcript and token count captured on success   # M5
  Given a fake agent script that emits a JSON stream containing a token count
  When `run` executes and succeeds
  Then the record's artifacts contain a transcript path and metrics["tokens_total"] reflects the parsed count (or the documented fallback value if the stream carries none)

Scenario: oracle leak detected before scoring is recorded   # M6
  Given a workspace where an oracle test file (or a renamed/copied duplicate) is present at teardown
  When `run` reaches the isolation check via `check_isolation.main`
  Then the run's record is written with status="failed" and the leak path is logged, not silently scored as done

Scenario: add arm's path pin resolves to a concrete SHA   # M7
  Given the `add` arm recipe's raw pin field is the repo-path comment string
  When `run --arm add --wm 1` executes
  Then the record's artifacts contain a resolved git SHA (not the raw pin string) for the pinned path

Scenario: unknown arm name is rejected   # R1
  Given `--arm ghost` is not in ARM_NAMES
  When `run` is invoked
  Then it fails with "unknown_arm" and no record.json or workspace directory is created
  And no agent process is ever spawned

Scenario: invalid arm recipe is rejected   # R2
  Given an arm TOML missing a required key (or gsd/spec-kit missing `pin`)
  When `run` is invoked for that arm
  Then it fails with "invalid_arm_recipe" (re-raised from `load_arm`, not re-wrapped)
  And no workspace or record is created

Scenario: out-of-range WM is rejected   # R3
  Given `--wm 4`
  When `run` is invoked
  Then it fails with "invalid_wm"
  And no workspace or record is created

Scenario: resume with nothing to resume is rejected   # R4
  Given no `record.json` files exist yet under `benchmark/runs/<name>/`
  When `resume --arm <name>` is invoked
  Then it fails with "nothing_to_resume"
  And no agent process is spawned, no record is created

Scenario: a crash mid-write never leaves a partial record   # R5
  Given the process is killed mid-write of record.json (simulated by injecting a fault after temp-file write, before rename)
  When the run directory is inspected afterward
  Then `benchmark/runs/<name>/wm<n>/record.json` is either the prior complete record or absent entirely — never a partial/corrupt file
  And a subsequent `resume` treats that WM as not-done, re-running it
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI run.py run --arm <name> --wm <1|2|3> [--timeout-s <float>] [--retries <int>] [--agent-cmd <argv...>]
  exit 0 -> writes benchmark/runs/<arm>/wm<n>/record.json { arm, wm, rep, status: "done"|"timeout"|"failed", metrics: {5 frozen keys}, artifacts: {workspace, transcript, oracle_report, resolved_pin?} }
  exit 2 -> "unknown_arm" | "invalid_arm_recipe" | "invalid_wm"   (no workspace/record created)

CLI run.py resume --arm <name> [--timeout-s <float>] [--retries <int>] [--agent-cmd <argv...>]
  exit 0 -> sequences remaining WM(s) from last status="done", writes one record.json per WM run, same shape as `run`
  exit 2 -> "nothing_to_resume"   (no prior record.json under benchmark/runs/<arm>/)

Internal (importable) surface — the seam `run|resume` are built from:
  runner.execute_wm(arm: Arm, wm: int, *, agent_cmd: Sequence[str] | None, timeout_s: float, retries: int) -> RunRecord
    — agent_cmd defaults to the real `claude -p` invocation; tests inject a fake-agent argv (hermetic, no live CLI)
  runner.find_resume_point(arm_name: str) -> int | None   — highest done WM + 1, or None if nothing_to_resume
  runner.write_record_atomic(path: pathlib.Path, record: RunRecord) -> None   — temp-file + os.replace, never a partial file on disk
  runner.resolve_pin(raw_pin: str, arm_name: str) -> str   — "add" arm: `git rev-parse HEAD` of the pinned path; other arms: raw pin passed through unchanged

Schema: no new persistent schema — reuses the frozen `benchmark/schema/run_record.py:RunRecord`/`validate` shape verbatim (this task is its first writer); one record.json file per arm×wm under benchmark/runs/ (gitignored); no second ledger file.
```

Glossary deltas: **resolved pin** — the concrete, re-derivable reference (a git SHA) the runner records in `artifacts.resolved_pin` when an arm's TOML `pin` field is not itself reproducible (currently only the `add` arm); **fake-agent seam** — the `--agent-cmd`/`agent_cmd` injection point tests use to substitute a stdlib script for the real `claude -p` process, keeping the suite hermetic.
Status: DRAFT
Least-sure flag surfaced at freeze: [spec] — the token-count sourcing assumption (§1 ⚠, ranked #1: `claude -p` JSON-stream parseability, never verified against this task's own evidence) is the flag most likely to force a re-open of this contract's `metrics.tokens_total` sourcing once a real agent is driven through it.
Reported: no — pending the human freeze decision (this bundle is the freeze-report raw material, rendered in this task's Return, not yet approved)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90%
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_run_writes_done_record: arrange arm recipe + wm1 PROMPT.md + fake-agent argv that exits 0 / act `run --arm <name> --wm 1 --agent-cmd <fake>` / assert record.json exists and `validate()` accepts status="done" · covers: M1
  - test_run_timeout_kills_and_records: arrange fake-agent argv that sleeps past `--timeout-s` / act `run` / assert process no longer alive (no zombie), record status="timeout", written file is `validate()`-clean · covers: M2
  - test_run_retries_then_fails: arrange fake-agent argv that always exits 1, `--retries N` / act `run` / assert fake-agent invoked exactly N+1 times (via a counter file the fake script writes), each attempt logged in artifacts, final record status="failed" · covers: M3
  - test_resume_skips_done_wm: arrange a pre-existing wm1 record.json status="done", no wm2 record / act `resume --arm <name> --agent-cmd <fake>` / assert fake-agent invoked only once (for wm2), never for wm1 (fake script fails the test if invoked twice) · covers: M4
  - test_transcript_and_tokens_captured: arrange fake-agent argv that prints a JSON line with a token count / act `run` / assert record.artifacts contains a transcript path with that content, metrics["tokens_total"] equals the parsed count · covers: M5
  - test_tokens_fallback_when_absent: arrange fake-agent argv that prints plain (non-JSON) stdout / act `run` / assert metrics["tokens_total"] is the documented fallback (0) not a crash · covers: M5 (edge)
  - test_oracle_leak_fails_run: arrange a workspace where a copy of a real `wm1/oracle/test_*.py` file is planted before teardown / act `run` / assert `check_isolation` is invoked, record status="failed", leak path present in artifacts, run not scored done · covers: M6
  - test_add_arm_pin_resolved_to_sha: arrange the real `add.toml` recipe / act `run --arm add --wm 1 --agent-cmd <fake>` / assert `resolve_pin` returns a 40-or-abbreviated hex SHA (matches `git rev-parse HEAD` of the pinned path) recorded in artifacts.resolved_pin, not the raw comment string · covers: M7
  - test_unknown_arm_rejected: arrange `--arm ghost` / act `run` / assert exit 2 "unknown_arm" · assert no `benchmark/runs/ghost/` directory created, no fake-agent invoked · covers: R1
  - test_invalid_arm_recipe_rejected: arrange a tmp arm TOML missing `setup_steps` / act `run --arm <that file>` / assert "invalid_arm_recipe" propagates from `load_arm` unchanged · assert no workspace/record created · covers: R2
  - test_invalid_wm_rejected: arrange `--wm 4` / act `run` / assert exit 2 "invalid_wm" · assert no workspace/record created · covers: R3
  - test_resume_nothing_to_resume: arrange an empty `benchmark/runs/<name>/` (or missing dir) / act `resume` / assert exit 2 "nothing_to_resume" · assert fake-agent never invoked · covers: R4
  - test_crash_mid_write_leaves_no_partial_record: arrange `write_record_atomic` with an injected fault raised after the temp-file write but before `os.replace` / act call `write_record_atomic` directly / assert target path is unchanged (absent, or the prior complete record) — never a partial/corrupt file · assert a subsequent `find_resume_point` treats that WM as not-done · covers: R5
</test_plan>

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/`
Strategy (ordered batches): 1. `benchmark/runner/agent.py` — the fake-agent-injectable command seam (`default_agent_cmd`, argv builder for real `claude -p`) with no execution logic yet, so tests can import the seam before the loop exists. 2. `benchmark/runner/records.py` — `write_record_atomic` (temp-file + `os.replace`), `find_resume_point` (scan `benchmark/runs/<arm>/wm*/record.json`, return highest done+1 or None) — pure functions over the existing frozen `RunRecord`/`validate`, no new shape. 3. `benchmark/runner/pin.py` — `resolve_pin` (git rev-parse HEAD of a path pin for the `add` arm; passthrough otherwise). 4. `benchmark/runner/core.py` — `execute_wm` (workspace creation, `setup_steps`, subprocess invoke with timeout+bounded retry, transcript capture, token parse-or-fallback, `check_isolation` teardown check, record assembly) — the one place all the failure-design constraints (timeout/retry/rollback) live. 5. `benchmark/run.py` — thin argparse CLI wrapping `run`/`resume` over the `runner/` package; maps `BenchError`/internal exceptions to the frozen exit-2 codes. 6. wire `_oracle_lib.running_app`/`http_call` into `execute_wm`'s post-agent check (closes the bench-scaffold dead-code finding) — call after the agent exits, before the isolation check, to confirm the workspace's app answers its entry contract.
Approach (domain strategy): sequential single-process orchestration per §1's chosen framing — one `execute_wm` call does one arm×WM end-to-end (workspace → setup → invoke → capture → check → record), no concurrency; the injectable `agent_cmd` seam is the core technique that makes this hermetically testable, mirroring bench-scaffold's own fail-loud validation discipline (raise `BenchError`-flavored, frozen-code failures rather than silently degrading) extended here to subprocess/IO failure modes (timeout, retry, atomic write) per CLAUDE.md's "design for failure" rule.
Data strategy: run-records-as-ledger (no second state file) — `find_resume_point` derives all resume state by re-reading the existing frozen `RunRecord` shape from disk; matches the §3 Schema line ("no new persistent schema... this task is its first writer").
Pattern: fixture-and-oracle pattern (bench-scaffold's own, extended) — the runner is the harness that drives the fixed `PROMPT.md` fixture through an arm and checks isolation before trusting the result, same discipline as the oracle suites, now operationalized as a live loop instead of a static check.
Optimization stance: correctness-first, no perf budget — pilot scale (5×3×1), matches bench-scaffold's own stance; ⚠ least-trusted facet: the token-count sourcing from `claude -p` JSON output (§1's #1 ⚠) — budget is "get a number, document the fallback," not "get it exactly right this task."
Persona (required): methodology-engine-dev — same adaptation bench-scaffold used (fail-loud validation, pinned/resolved versions, stdlib-first), extended here from static validators to a live subprocess-orchestration loop; no benchmark-runner-specific persona exists yet.
Spawn isolation (default): worktree — no shared-tree reason applies (single-agent build, no parallel spawn needed).
Known-problem fixes: crash mid-record-write → `write_record_atomic`'s temp-file+`os.replace` (R5) · slow-starting real app defeating the startup-poll heuristic → wrap `running_app`'s poll in the runner's own bounded retry/timeout rather than trusting a single 10s window (named risk from §0, hardened not rewritten this task) · oracle contamination surviving into a scored run → `check_isolation.main` called at teardown, a leak forces status="failed" (M6) · unresolvable `add` arm pin drifting the fairness record → `resolve_pin` records a concrete SHA every run (M7).
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned")>
Safety rule (feature-specific): the agent subprocess and its timeout/kill/retry sequence plus the final record write are the one atomic-outcome unit — a kill, a retry exhaustion, or a mid-write crash must each resolve to exactly one of {no record yet, prior complete record, one newly-complete record}, never a torn/partial record on disk.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree (diverges from §4's non-recursive counting) · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered, never retro-red) · enforcement live: a completing verify gate refuses an out-of-scope build (scope_violation → self-heal); check surfaces it. EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] `run --arm add --wm 1 --agent-cmd <fake-agent-script>` (hermetic, no live `claude` call) completes and writes a `validate()`-clean `benchmark/runs/add/wm1/record.json` with status="done" — confirmed by direct file read + `RunRecord.from_json`
- [ ] killing/interrupting a run after wm1 completes, then calling `resume --arm <name>`, invokes the fake-agent exactly once more (for wm2), never re-invoking it for wm1 — confirmed by a fake-agent invocation counter file
- [ ] a fake-agent that sleeps past `--timeout-s` results in the process no longer running (`psutil`/`os.kill(pid,0)`-style liveness check or exit-status inspection) and a status="timeout" record — confirmed live
- [ ] a planted oracle-file copy inside the run's workspace at teardown forces status="failed" with the leak path recorded — confirmed by reading the record's artifacts after a deliberate plant
- [ ] the `add` arm's recorded `artifacts.resolved_pin` is a real git SHA matching `git rev-parse HEAD` of the pinned path, not the raw TOML string — confirmed by string comparison against a live `git rev-parse` call
- [ ] `benchmark/runs/` remains untracked by git after a full run (`git status --porcelain benchmark/runs` empty) — confirmed live, same check bench-scaffold used

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by <how / where>
- [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Advisor 3-lens and Refute-read verdicts are audit-measured (`advisor_verdict_unrecorded` · `refute_unrecorded`), never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
