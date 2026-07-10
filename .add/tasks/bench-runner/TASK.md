# TASK: headless claude -p runner: sandboxed arm workspaces, WM sequencing with resume, timeout/retry, transcript+token capture

slug: bench-runner · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done

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
  - [x] token-count sourcing from `claude -p` JSON output — CONFIRMED by live spike 2026-07-07 (orchestrator ran `claude -p "Reply with exactly: ok" --output-format json`): the result event carries top-level `total_cost_usd`, `num_turns`, and `usage.{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}`; `--output-format stream-json` yields the per-event transcript (source for `time_to_first_edit` = first Edit/Write tool_use event). Contract pins these exact field names; fallback when unparseable: `tokens_total=0` + a loud mark in artifacts.
  - [ ] the startup-detection heuristic in `_oracle_lib.running_app` (10s deadline, 0.2s poll) is assumed "good enough to harden with a retry wrapper" rather than needing a full rewrite — confirm or deny once a real arm-built app is driven through it; if wrong, the fix is bigger than this task's Strategy assumes.
  - [ ] `claude -p`'s exit code reliably distinguishes "agent finished (successfully or not)" from "process crashed" for the retry-vs-timeout-vs-failed classification — assumed true from general CLI convention, not confirmed against this specific tool's behavior.
  - [ ] resuming from run-records alone (no separate ledger) is sufficient even if a WM is retried multiple times before succeeding — assumed the LAST written record per WM is authoritative and prior failed-attempt records for the same WM are either overwritten or clearly superseded, not accumulated as ambiguous siblings.
</assumptions>

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

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI run.py run --arm <name> --wm <1|2|3> [--timeout-s <float>=1800] [--retries <int>=1] [--agent-cmd <argv...>]
  token/cost sourcing (pinned by live spike 2026-07-07): the final `claude -p --output-format stream-json` result event's
  usage fields — tokens_total = usage.input_tokens + usage.cache_creation_input_tokens + usage.cache_read_input_tokens
  + usage.output_tokens; cost_usd = total_cost_usd; time_to_first_edit = elapsed seconds to the first Edit|Write
  tool_use event in the stream (fallback when unparseable: tokens_total=0 + artifacts["token_source"]="unparseable", loud)
  exit 0 -> writes benchmark/runs/<arm>/wm<n>/record.json { arm, wm, rep, status: "done"|"timeout"|"failed", metrics: {5 frozen keys}, artifacts: {workspace, transcript, oracle_report, resolved_pin?} }
  exit 2 -> "unknown_arm" | "invalid_arm_recipe" | "invalid_wm"   (no workspace/record created)

CLI run.py resume --arm <name> [--timeout-s <float>=1800] [--retries <int>=1] [--agent-cmd <argv...>]
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
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07)
Least-sure flag surfaced at freeze: [spec] — with token sourcing spiked and pinned (live `claude -p` probe), the least-sure remaining assumption is exit-code classification: that `claude -p`'s exit code reliably separates "agent finished" from "process crashed" for the retry-vs-failed decision — asserted from CLI convention, not probed; if wrong: retries fire on completed-but-unhappy runs, inflating attempt counts in the record (cost: a targeted re-open of the retry-classification line, not the shape). Human approved at freeze after the ⚠1 spike (defaults 1800s/1 retry and add-arm-only resolve_pin decided by the human 2026-07-07).
Reported: yes — freeze report rendered (SHAPE/FLAGS/decisions); ⚠1 resolved by live spike before approval

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
Strategy actually used: as planned (agent.py -> records.py -> pin.py -> core.py -> run.py -> oracle wiring), with one deliberate scope-narrowing: `execute_wm` does NOT shell out each arm's `setup_steps` strings — they're free-text install/init lines with inline comments (e.g. "pip install -e add-method  # or: npm install..."), which cannot be run as list-form argv (the §0 "no shell string" security constraint) without a shell, and shelling them would call live network/CLI tools inside a "hermetic, no live claude call" test suite. Environment setup for a real pilot run stays a pre-runner manual/CI step for this task; `setup_steps` content is preserved on the loaded `Arm` for a future task to wire (recorded as a Spec delta in §7). `_invoke_once` also switched from a streaming readline-based watcher to `subprocess.communicate(timeout=...)` mid-build: readline() blocks past the deadline on a silent/sleeping fake agent, which produced a real RED (test_run_timeout_kills_and_records got status="done" instead of "timeout") — communicate()'s TimeoutExpired is the correct primitive for this seam.
Safety rule (feature-specific): the agent subprocess and its timeout/kill/retry sequence plus the final record write are the one atomic-outcome unit — a kill, a retry exhaustion, or a mid-write crash must each resolve to exactly one of {no record yet, prior complete record, one newly-complete record}, never a torn/partial record on disk.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `uv run --with pytest pytest benchmark/tests -q` → 35 passed; `add.py check` → 607 passed, 0 failed (78 warnings, none new-blocking — see below)
- [x] coverage did not decrease (new files; measured 89% on `benchmark/runner`+`benchmark/run` vs §4's 90% target — 🟡 under target, see findings)
- [x] no test or contract was altered during build — `git diff --stat` shows only new files under `benchmark/runner/` + `benchmark/run.py`; TASK.md §3 unchanged since freeze
- [ ] the green was EARNED, not gamed — see Refute-read verdict below: EARNED for what's tested, but a Must-rule (setup_steps) has ZERO test coverage because it's ZERO-implemented — 🔴 see findings, this is a real gap not a cheat but the checklist item cannot be ticked clean
- [x] concurrency / timing of the risky operation is safe — see Advisor lens
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor lens
- [x] layering & dependencies follow CONVENTIONS.md — see Advisor lens
- [ ] a person reviewed and approved the change — pending human gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `run --arm add --wm 1 --agent-cmd <fake-agent-script>` (hermetic, no live `claude` call) completes and writes a `validate()`-clean `benchmark/runs/add/wm1/record.json` with status="done" — confirmed by `test_run_writes_done_record` + `test_add_arm_pin_resolved_to_sha` (execute_wm-level, uses a fake-arm/`add` recipe) reading the on-disk record via `RunRecord.from_json`. NOTE: the CLI entrypoint form (`python run.py run --arm add --wm 1 --agent-cmd ...`) itself is NOT exercised end-to-end by any test — `run.py`'s success path (lines 61-69) is 0%-covered; only its exit-2 rejection branches are CLI-tested (`test_run_cli.py`). The underlying `execute_wm` is well-tested, but the CLI glue that wires argparse → `execute_wm` is unverified.
- [x] killing/interrupting a run after wm1 completes, then calling `resume --arm <name>`, invokes the fake-agent exactly once more (for wm2), never re-invoking it for wm1 — confirmed by `test_resume_skips_done_wm` via an invocation-counter file, BUT this test calls `execute_wm` directly after computing `find_resume_point` itself in the test body — it does NOT call `run.py resume` as a CLI command. `run.py`'s actual `resume` sequencing loop (lines 79-97, the real WM 1→3 for-loop over `execute_wm`) is 0%-covered by any test. This is the §3-contracted CLI surface for M4 and it has no integration test.
- [x] a fake-agent that sleeps past `--timeout-s` results in the process no longer running and a status="timeout" record — confirmed live by `test_run_timeout_kills_and_records`: verified in code that `_invoke_once`'s `finally` calls `_kill_process_group` (`os.killpg(..., SIGKILL)`) and `proc.wait(timeout=5)` on every exit path, not just the timeout branch, so no zombie survives even on the done/failed paths.
- [x] a planted oracle-file copy inside the run's workspace at teardown forces status="failed" with the leak path recorded — confirmed by `test_oracle_leak_fails_run`; code path in `core.py:_isolation_check`→`execute_wm` sets `status = "done" if isolation_clean else "failed"` and records `artifacts["leak_path"]`.
- [x] the `add` arm's recorded `artifacts.resolved_pin` is a real git SHA matching `git rev-parse HEAD` of the pinned path — confirmed by `test_add_arm_pin_resolved_to_sha`; `pin.py:resolve_pin` shells `["git","rev-parse","HEAD"]` list-argv (no shell string) against `REPO_ROOT`, genuine not stubbed.
- [x] `benchmark/runs/` remains untracked by git after a full run — `.gitignore:49` already covers it (bench-scaffold-era); no new write path escapes `benchmark/runs/<arm>/wm<n>/` per code read of `core.py`.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `build_argv`/`default_agent_cmd` used by `core.py`; `write_record_atomic`/`find_resume_point`/`DEFAULT_RUNS_ROOT` used by `core.py`+`run.py`; `resolve_pin` used by `core.py` (add-arm branch); `execute_wm` used by `run.py` both commands. No orphaned import.
- [x] DEAD-CODE (code) — `_oracle_lib.running_app`/`http_call` are now called from `core.py:_post_agent_app_check` (closes bench-scaffold's dead-code finding, confirmed by direct read of core.py:140-142). No new unused symbol found.
- [ ] SEMANTIC — 🔴 the one symbol §3 explicitly documents (`execute_wm`) does NOT implement the full behavior §1 M1 requires: `arm.setup_steps` is loaded (`Arm.setup_steps` populated by `loader.py`) but never read/executed anywhere in `core.py` (`grep -n setup_steps benchmark/runner/` → zero hits outside test fixtures). This is a genuine Must-rule gap, not a skim miss — see findings below.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree: `runner.execute_wm` (core.py:160), `runner.find_resume_point` (records.py:43), `runner.write_record_atomic` (records.py:20), `runner.resolve_pin` (pin.py:16) — all present with the exact frozen signatures (verified by direct read, not grep-only).
- [x] no anchor moved/renamed since Ground SHA (a0d7183) — `RunRecord`/`validate`/`BenchError`, `load_arm`/`Arm`/`ARM_NAMES`, `running_app`/`http_call`, `check_isolation.find_leaks`/`main`, `PROMPT.md` paths all resolve at their §0-cited locations, confirmed by the import lines in core.py/run.py/records.py/pin.py.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (for what is tested) — with a disclosed material gap outside the tested surface (see findings)
By: self (add-verify) · adversarially checked:
  - `write_record_atomic`: crash-injection test monkeypatches `os.replace` to raise — genuine fault injection, not a stub; confirmed target path absent + no leaked temp file + `find_resume_point` correctly treats it as not-done. Partial-file-impossible claim holds: write goes to a `tempfile.mkstemp` sibling, only `os.replace` publishes it.
  - `find_resume_point`: only single-retry-per-WM scenario tested (no test for done-wm1 + done-wm3 with wm2 missing/failed — a real gap the WM 1→2→3 sequential design makes moot in practice, but the function itself would return 2 correctly by construction, not defensively verified).
  - timeout path: confirmed genuine — `_invoke_once`'s `finally` unconditionally calls `_kill_process_group` (SIGKILL via `os.killpg` on `start_new_session=True`'s own process group) + `proc.wait(timeout=5)` on EVERY exit path (done/failed/timeout), not just timeout. Verified by code read, not just test pass.
  - token parsing: matches the §3-pinned live-spike field names exactly (`usage.{input,output,cache_creation_input,cache_read_input}_tokens`, `total_cost_usd`) — genuine JSON parse of the fake agent's real stdout, not a hardcoded return.
  - `resolve_pin`: genuine `subprocess.run(["git","rev-parse","HEAD"], cwd=repo_path)` list-argv call, not stubbed; test asserts against a live independent `git rev-parse HEAD` call for comparison.
  - CONCERN (not a cheat, a coverage gap): `run.py`'s CLI success paths (`run` lines 61-69, `resume` lines 71-97 including the actual WM-sequencing for-loop) are 0%-covered — `test_run_cli.py` only exercises the 4 rejection codes; `test_runner_resume.py`/`test_runner_core.py` test `execute_wm`/`find_resume_point` directly, never through `run_mod.main([...])`. The contracted CLI surface (`run.py run|resume`) itself has no green test proving it, only its parts.
  - CONFIRMED GAP (not a cheat, a Must-rule violation): setup_steps — see findings below; no test exists for it because it isn't implemented, so the suite cannot have "gamed" it, but M1's green is incomplete for this clause.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (add-verify, tdd-verifier persona lens)
1. Security: CLEAR — every subprocess call across `agent.py`/`pin.py`/`core.py` uses list-form argv (`subprocess.Popen(argv, ...)`, `subprocess.run(["git","rev-parse","HEAD"], ...)`), no `shell=True`, no string interpolation into a shell; no secrets/env handling introduced; `resolve_pin`'s `cwd` defaults to a fixed `REPO_ROOT`, not user input.
2. Concurrency: CLEAR — single-process sequential design per §1's chosen framing; timeout kill uses `start_new_session=True` + `os.killpg(SIGKILL)` in a `finally` covering every exit path, confirmed no zombie risk; `write_record_atomic` is a single-writer temp-file+`os.replace` (atomic rename), no concurrent-writer race in this design (no concurrency was ever introduced).
3. Architecture: CLEAR structurally (clean `agent → pin/records → core → run.py` layering, stdlib-first, no circular imports) — but flagging as RESIDUE at the completeness level: `execute_wm` (the one symbol carrying the whole Must-set) silently omits the `setup_steps` clause of M1 with no runtime signal (no exception, no artifact note, no log) that it was skipped — a future caller reading only the record.json would not know setup never ran.
Verdict: PASS (lens-wise) — Residue carried forward as a non-security completeness gap, not a lens HARD-STOP
Residue: `execute_wm` never executes `arm.setup_steps` (M1 Must-clause), and no artifact/record field discloses that omission at runtime — see findings
Binding: advisory — this task is `autonomy: auto`, non-mechanical change; the setup_steps gap is a content/completeness finding, not itself security/concurrency/architecture in the classic sense, so it is NOT auto-binding to HARD-STOP by the 3-lens rule, but it is binding on the GATE RECORD outcome below because it is an unresolved Must-rule.

### GATE RECORD — gaps closed post-recommendation (human-approved re-cross, recorded by the engine)
> Verify's CLOSE-GAP-BEFORE-GATE recommendation was executed before gating, not waived: (1) M1 setup_steps now
> implemented in execute_wm (shlex list-argv, no shell; "setup: <argv> -> exit N" recorded in attempts + transcript;
> a failing step fails the attempt loudly, pre-agent) with 3 new tests; (2) timeout now consumes a retry per the
> frozen §1 wording, with a timeout-then-success test; (3) CLI happy paths (run success end-to-end, resume
> sequencing wm2/wm3) tested through run_mod.main. Fixture correction human-approved: the M7 pin test keeps its
> SHA assertions on the real add.toml pin but with empty setup_steps (real provisioning cannot run in an empty
> sandbox; intent = pin resolution). Suite 41/41 green · coverage 93% (target 90) · check 607/0 ·
> re-cross recorded by engine (approved by Tin Dang, 2026-07-07).
Reported: yes — verify findings + close-gap plan rendered to the human; both decisions (fix-all-3, fixture adaptation) human-answered before this record
Outcome: PASS
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a
Reviewed by: Tin Dang (close-gap + fixture decisions) with add-verify findings · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): timeout/failed record rate per arm during the pilot (a high setup-failure rate for one arm = fairness problem, not an arm defect) · zombie/orphan processes after killed runs (should be zero) · `token_source: unparseable` occurrences (each one degrades `tokens_total`) · real `add`-arm setup_steps success in a fresh sandbox (first live pilot run is the real test of the provisioning lines).

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (2026-07-07))
- [AI] build — approach: sequential single-process orchestration per §1's chosen framing — one `execute_wm` call does one arm×WM end-to-end (workspace → setup → invoke → capture → check → record), no concurrency; the injectable `agent_cmd` seam is the core technique that makes this hermetically testable, mirroring bench-scaffold's own fail-loud validation discipline (raise `BenchError`-flavored, frozen-code failures rather than silently degrading) extended here to subprocess/IO failure modes (timeout, retry, atomic write) per CLAUDE.md's "design for failure" rule.
- [AI] build — data strategy: run-records-as-ledger (no second state file) — `find_resume_point` derives all resume state by re-reading the existing frozen `RunRecord` shape from disk; matches the §3 Schema line ("no new persistent schema... this task is its first writer").
- [AI] build — pattern: fixture-and-oracle pattern (bench-scaffold's own, extended) — the runner is the harness that drives the fixed `PROMPT.md` fixture through an arm and checks isolation before trusting the result, same discipline as the oracle suites, now operationalized as a live loop instead of a static check.
- [AI] build — optimization stance: correctness-first, no perf budget — pilot scale (5×3×1), matches bench-scaffold's own stance; ⚠ least-trusted facet: the token-count sourcing from `claude -p` JSON output (§1's #1 ⚠) — budget is "get a number, document the fallback," not "get it exactly right this task."
- [AI] build — strategy used: as planned (agent.py -> records.py -> pin.py -> core.py -> run.py -> oracle wiring), with one deliberate scope-narrowing: `execute_wm` does NOT shell out each arm's `setup_steps` strings — they're free-text install/init lines with inline comments (e.g. "pip install -e add-method  # or: npm install..."), which cannot be run as list-form argv (the §0 "no shell string" security constraint) without a shell, and shelling them would call live network/CLI tools inside a "hermetic, no live claude call" test suite. Environment setup for a real pilot run stays a pre-runner manual/CI step for this task; `setup_steps` content is preserved on the loaded `Arm` for a future task to wire (recorded as a Spec delta in §7). `_invoke_once` also switched from a streaming readline-based watcher to `subprocess.communicate(timeout=...)` mid-build: readline() blocks past the deadline on a silent/sleeping fake agent, which produced a real RED (test_run_timeout_kills_and_records got status="done" instead of "timeout") — communicate()'s TimeoutExpired is the correct primitive for this seam.
- [AI] verify — gate PASS (reviewed by Tin Dang (close-gap + fixture decisions) with add-verify findings)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] the real `add.toml` setup_steps (`pip install -e` …) cannot succeed in a bare sandbox — bench-pilot-report must provision arm environments (venv/uv per workspace) before the live pilot, or amend the arm recipes' setup lines (evidence: fixture correction at re-cross; direct repro `externally-managed-environment`)
- [SPEC · open] `find_resume_point` is not defensively tested for non-contiguous done-WMs (done-wm1 + done-wm3, wm2 missing) — moot under sequential 1→2→3 but worth one guard test at bench-pilot-report (evidence: §6 refute-read note)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a disclosed deviation from a frozen Must is still a Must violation — verify escalated CLOSE-GAP-BEFORE-GATE instead of accepting the builder's honest §7 delta, and the gap closed in one re-cross (evidence: setup_steps finding → shlex list-argv fix, 41/41 green)
- [ADD · open] a pre-existing test whose fixture can never run for real (real pip in an empty sandbox) is a fixture bug, not a contract conflict — adapt the fixture to the test's stated intent (M7) with human approval, never weaken the assertion (evidence: test_add_arm_pin_resolved_to_sha correction)
- [TDD · open] red-first caught a real orchestration bug pre-implementation: a blocking readline() loop can never observe a deadline against a silent child — subprocess.communicate(timeout=) is the correct shape (evidence: build report RED excerpt)
  - [SPEC · open] `execute_wm` does not execute an arm's `setup_steps` (install/init shell lines) — a future task must decide how/where arm environment provisioning runs (sandboxed shell? container?) without violating the list-form-argv-only security constraint (evidence: TASK.md §5 "Strategy actually used").

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

