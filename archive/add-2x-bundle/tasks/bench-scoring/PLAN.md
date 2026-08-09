# TASK: scorers for the 5 frozen metrics: oracle re-runs (regression_rate), rubric judge (spec_fidelity), token/cost ledger, context-rot slope, time-to-first-edit

slug: bench-scoring · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `benchmark/schema/run_record.py:RunRecord`, `:validate`, `:BenchError`, `:REQUIRED_METRICS`, `:REQUIRED_ARTIFACTS` — frozen shape; `validate()` requires `metrics.keys() == REQUIRED_METRICS` EXACTLY (no extra key tolerated) but `artifacts` only checks a required-subset (extra keys already flow through today: `attempts`, `token_source`, `resolved_pin`, `leak_path`) — this task's write-back must respect both constraints.
  - `benchmark/runner/core.py:execute_wm`, `:_zero_metrics`, `:_parse_tokens_and_cost` — the runner already writes `regression_rate`/`spec_fidelity`/`context_rot_slope` as placeholder `0.0` on every "done" record, and real `tokens_total`/`cost_usd`/`time_to_first_edit` from the stream-json transcript; this task's job is to compute the three placeholders and re-validate the other three, never invent a sixth metric or touch a 4th artifact requirement.
  - `benchmark/runner/records.py:write_record_atomic`, `:find_resume_point` — the atomic temp-file+`os.replace` writer this task reuses verbatim to write scored records back (no second writer implementation).
  - `benchmark/workload/wm3/oracle/test_refactor.py` — the wm1+wm2 oracle re-exports tagged `pytest.mark.regression` (`test_regression_wm1_*` ×5, `test_regression_wm2_*` ×5); `regression_rate` is extracted by running exactly this marked set against the WM3 workspace.
  - `benchmark/workload/wm{1,2,3}/oracle/*` (`test_bookings.py`, `test_business_rules.py`, `test_refactor.py`) + `conftest.py` (each inserts `REPO_ROOT` at `sys.path`, reads `BENCH_WORKSPACE` env var) — the per-WM oracle suites; `spec_fidelity`'s judge reads the same workspace + these suites' outcomes as grounding context.
  - `benchmark/workload/_oracle_lib.py:running_app`, `:http_call` — the HTTP driver already wired by bench-runner; this task's regression re-run reuses it (via pytest's own fixtures, not reinvented).
  - `benchmark/pytest.ini:markers` — registers the `regression` marker this task filters on (`pytest -m regression`).
  - `benchmark/tests/test_workload_prompts.py:test_prompts_identical_contract_and_bait` (L17-24) — the loose or-chain (`"wm1" in ... or "task/booking" in ... or "breaking" in ...`) named in bench-scaffold's spec delta as this task's to absorb.
  - `benchmark/runner/agent.py:build_argv`, `:default_agent_cmd` — the injectable-argv seam pattern (fake-agent argv for hermetic tests) this task mirrors for the judge command.
  - `benchmark/run.py` — the existing `run`/`resume` subcommand CLI (argparse, `common` parent parser with `--arm`/`--timeout-s`/`--retries`/`--agent-cmd`) this task extends with `score`.
Context (working folder): `benchmark/tests/conftest.py` (fixture shapes: fake workspaces/records reused for hermetic scoring tests) · `benchmark/runs/` (gitignored output root — `.gitignore:49` — scoring reads/writes record.json here, creates nothing outside it) · no `judge.py` or `score.py` module exists yet — both are net-new under `benchmark/`.
Honors (patterns / conventions): stdlib-first, fail-loud `BenchError` on any malformed/missing shape (never silently coerce or default to 0 to mask a real failure) — the pattern `run_record.py`/`runner/core.py` already establish; subprocess calls use list-form argv only (no shell string), matching bench-runner's Advisor security lens; CLAUDE.md's "design for failure: timeouts, retries, circuit breakers" — the judge call is itself an IO request and gets the same injectable-command + fail-loud treatment as the agent call, not a bespoke one-off.
Seams consulted: none — no SEAMS.md entry covers scoring/judge subprocess seams yet; this task originates it (mirrors `benchmark/runner/agent.py`'s existing fake-agent seam rather than inventing a different shape).
Anchors the contract cites: `RunRecord`/`validate`/`BenchError` (benchmark/schema/run_record.py) · `write_record_atomic` (benchmark/runner/records.py) · `execute_wm`'s placeholder metrics (benchmark/runner/core.py) · the `regression`-marked test set (benchmark/workload/wm3/oracle/test_refactor.py) · `test_prompts_identical_contract_and_bait` (benchmark/tests/test_workload_prompts.py).
Issues/Risks (→ feed §1):
  - `validate()`'s exact-match on `metrics.keys()` means scoring MUST overwrite the same 5 keys in place (a sidecar file would either duplicate the schema or drift from record.json — resolved in §5 as write-back, not sidecar; see ⚠1).
  - `context_rot_slope` is defined by MILESTONE.md as "fidelity trend WM1→WM3" — a per-ARM trend, but the frozen schema stores metrics per (arm, wm, rep) record; WM1/WM2 records structurally cannot hold a 3-point trend when scored standalone — needs an explicit convention (this task must decide: computed only at WM3, reading WM1/WM2's already-scored `spec_fidelity` off THEIR OWN record.json) or the "loud error, never silent 0" constraint is unenforceable. Top risk — see §1 ⚠1.
  - `regression_rate` is genuinely undefined before WM3 (no `regression`-marked oracle tests exist for WM1/WM2 in isolation) — same "structurally N/A before WM3" shape as context_rot_slope; must not be conflated with "failed to compute."
  - `runner/core.py:_invoke_once`'s `first_edit_elapsed` defaults to `0.0` both when an edit is found at position 0 AND when no edit event is ever found — an ambiguity in the ALREADY-FROZEN bench-runner contract; this task cannot fix it (frozen §3, out of scope) but must not compound it — score validates presence/non-negativity only, never reinterprets the value.
  - the real judge is a live `claude -p` rubric call — same hermeticity problem bench-runner solved for the agent call; must mirror `agent.py`'s injectable-argv seam rather than block tests on a live LLM.
  - the WM3 regression-bait prompt-contract test (`test_prompts_identical_contract_and_bait`) has a loose or-chain that this task's spec delta assigns to tighten once regression extraction is defined here (§0 Related intent, §2 scenario).
Related intent: MILESTONE.md exit criterion "`score` computes all 5 frozen metrics for a finished run from artifacts alone (re-runnable, no live agent)" (this task's sole deliverable) · MILESTONE.md Shared decisions "Metrics (frozen names)" line (regression_rate/spec_fidelity/tokens_total/cost_usd/context_rot_slope definitions) · bench-scaffold TASK.md §7 Spec delta #3: "the WM3 regression-bait assertion in test_prompts_identical_contract_and_bait is a loose or-chain over keywords — tighten to an exact `duration_minutes`-removal assertion when bench-scoring defines regression_rate extraction" — ABSORBED here (§2 Scenario + §5 Scope include `benchmark/tests/test_workload_prompts.py`). GLOSSARY: `arm`, `workload milestone`, `oracle suite`, `resolved pin`, `fake-agent seam` (all MILESTONE.md / bench-runner TASK.md).
Ground SHA: 8668859

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `benchmark/run.py score --arm <name> --wm <1|2|3>` — computes the 5 frozen metrics for a finished arm×WM run from artifacts alone (record.json + transcript + workspace + oracle re-runs), writing the result back into that WM's record.json via the frozen `validate()`/`write_record_atomic`.
Framings weighed: **write-back into record.json** (chosen) · sidecar `score.json` per WM (rejected: `validate()`'s exact metrics-key match means a sidecar would either duplicate the same 5-key schema — two files that can silently drift — or force a second schema that MILESTONE.md never asked for; write-back keeps ONE source of truth and reuses the already-frozen atomic writer verbatim) · a single `report`-owned cross-WM aggregator instead of per-WM `score` (rejected: MILESTONE.md's task stub explicitly separates `score` from `report`, and `context_rot_slope`/`regression_rate` needing prior-WM data is handled by reading sibling record.json files, not by merging the two tasks).
Must:
<must>
  - `score --arm A --wm N` reads `benchmark/runs/A/wmN/record.json`; if `status != "done"` (i.e. "timeout" or "failed"), score refuses — nothing to score, the placeholder zero-metrics stand as-is (M1).
  - `score` computes `tokens_total`/`cost_usd`/`time_to_first_edit` as a VALIDATION pass over the runner's already-written values: numeric, `tokens_total >= 0`, `cost_usd >= 0`, `time_to_first_edit >= 0`; if `artifacts["token_source"] == "unparseable"`, score copies that value through unchanged and surfaces a `metrics_warnings` artifact entry — it never invents a nonzero substitute (M2).
  - `score` computes `spec_fidelity` via an injectable judge command (mirrors `benchmark/runner/agent.py`'s fake-agent seam): `judge.build_judge_argv(rubric_prompt, judge_cmd)` — default is a real `claude -p <rubric>` call; tests inject a fake stdlib judge script. The judge reads the WM's PROMPT.md requirements + the oracle_report.json (app_check/isolation_clean) + the oracle suite pass/fail counts for that WM, and returns a float in `[0.0, 1.0]` (M3).
  - `score` computes `regression_rate` ONLY at WM3: runs `pytest -m regression benchmark/workload/wm3/oracle/test_refactor.py` with `BENCH_WORKSPACE=<wm3 workspace>` (subprocess, list-argv, real pytest — no injection needed, hermetic via a fixture app, no live agent/judge involved), and sets `regression_rate = failed_count / total_regression_count` (M4).
  - `score` computes `regression_rate = 0.0` for WM1/WM2 by DEFINITION (no prior baseline exists to regress against — this is a valid computed value, not a skipped one) (M5).
  - `score` computes `context_rot_slope` ONLY at WM3: reads `spec_fidelity` from WM1's and WM2's OWN already-scored record.json (their `status == "done"` required), plus the just-computed WM3 `spec_fidelity`, and fits the 3-point least-squares slope of fidelity-vs-WM-index (x = 1,2,3) — `slope = Σ((x-x̄)(y-ȳ)) / Σ((x-x̄)²)` (M6).
  - `score` computes `context_rot_slope = 0.0` for WM1/WM2 by DEFINITION (fewer than 3 points exist yet — insufficient trend, not a failure) (M7).
  - a computed metric writes back into the SAME 5 keys `execute_wm` already wrote, via `validate()` (which still enforces the exact-key + status + artifact-subset invariants) then `write_record_atomic` — no new top-level field, no new schema (M8).
  - `score` is re-runnable/idempotent: running it twice on the same finished record with the same artifacts on disk produces the same numeric result (byte-identical judge stub in tests; live judge is best-effort, not asserted byte-identical) (M9).
  - the WM3 regression-bait prompt test tightens: `test_prompts_identical_contract_and_bait` replaces its loose 3-way `or`-chain with an exact assertion that WM3's PROMPT.md names the `duration_minutes` → `end_time` field removal (the concrete regression bait `test_refactor.py` actually oracles) (M10).
</must>
Reject:
<reject>
  - `score` invoked with `--wm` for a record.json that does not exist on disk -> "record_not_found"
  - `score` invoked against a record whose `status` is "timeout" or "failed" -> "record_not_done"
  - `score --wm 3` invoked when WM1 or WM2's record.json is missing, or exists but `status != "done"` -> "missing_prior_wm_record"
  - `--wm` outside `{1,2,3}` -> "invalid_wm"
  - `--arm` not one of `ARM_NAMES` -> "unknown_arm"
  - the injected/default judge command's stdout is not a parseable `[0.0, 1.0]` float -> "unparseable_judge_output"
  - the `pytest -m regression` subprocess itself errors before producing pass/fail counts (e.g. collection error) -> "regression_run_failed"
</reject>
After:
<after>
  - `benchmark/runs/<arm>/wm<N>/record.json` for a "done" record has all 5 metrics reflecting REAL computed values (never the runner's `0.0` placeholders for regression_rate/spec_fidelity/context_rot_slope on a WM that has been scored).
  - `benchmark/run.py score --arm add --wm 3` run twice back-to-back with the same on-disk artifacts leaves record.json numerically unchanged (idempotent) and exits 0 both times.
  - `test_prompts_identical_contract_and_bait` asserts the exact `duration_minutes`/`end_time` bait, not a loose keyword or-chain.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Write-back-into-record.json (vs sidecar) is right AND `validate()`'s exact-metrics-key invariant is meant to be re-satisfied by an UPDATE (not just the runner's first write) — lowest confidence because MILESTONE.md's contract line ("run-record JSON schema... -> owning task bench-scaffold") never explicitly says who is allowed to overwrite an already-`validate()`-passed file after the fact; if wrong (the human wants an append-only ledger / sidecar instead): the entire §3 CONTRACT internal surface (write_scored_record) needs a re-open at CONTRACT, not just BUILD — cost = re-cross specify→contract for this task only, runner/schema untouched either way.
  - [ ] `context_rot_slope`/`regression_rate` being WM3-only (0.0 defined for WM1/WM2) matches the human's intent for "fidelity trend WM1→WM3" — confirm or deny; if the human instead wants EVERY record to attempt a trend/regression computation and hard-fail when data is insufficient, M5/M7's "0.0 by definition" become Reject cases instead (`insufficient_trend_data`), which changes M6/M7 and the Reject list.
  - [ ] the rubric judge's real invocation shape (a `claude -p` prompt template, its exact scoring rubric text, and where the rubric prompt template file lives under `benchmark/`) is deferred to BUILD as an implementation detail, not frozen in §3 beyond the `judge_cmd` seam signature — confirm this is an acceptable looseness for a "preferred, not enforced" Strategy, not a contract gap.
  - [ ] `pytest -m regression`'s exit/collection behavior when the WM3 workspace app is unreachable (vs a genuine test failure) is assumed distinguishable via pytest's own exit codes (5 = no tests collected, 2 = interrupted) — not yet probed against a live fixture; if wrong, "regression_run_failed" may fire on transient app-not-up conditions that a retry would have cleared.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: refuses to score a not-done record   # M1
  Given benchmark/runs/add/wm1/record.json exists with status "timeout"
  When `score --arm add --wm 1` runs
  Then it exits 2 with "record_not_done"
  And record.json's metrics are byte-unchanged on disk

Scenario: token/cost/first-edit are validated, not recomputed   # M2
  Given a "done" record.json with tokens_total=4200.0, cost_usd=0.31, time_to_first_edit=12.5
  When `score --arm add --wm 1` runs
  Then the written record.json keeps tokens_total=4200.0, cost_usd=0.31, time_to_first_edit=12.5 unchanged
  And exit is 0

Scenario: unparseable token source is surfaced, never masked   # M2
  Given a "done" record.json with artifacts["token_source"]="unparseable" and tokens_total=0.0
  When `score --arm add --wm 1` runs
  Then the written record.json still has tokens_total=0.0 and artifacts["token_source"]="unparseable"
  And a "metrics_warnings" artifact entry names tokens_total as unparseable-sourced

Scenario: spec_fidelity via injected fake judge   # M3
  Given a "done" wm1 record.json and workspace, and a fake judge argv that prints "0.82"
  When `score --arm add --wm 1 --judge-cmd <fake-judge-argv>` runs
  Then the written record.json has metrics.spec_fidelity == 0.82
  And no live `claude` process is spawned

Scenario: regression_rate computed at WM3 from the marked oracle re-exports   # M4
  Given a "done" wm3 record.json/workspace where 2 of the 10 regression-marked tests fail against it
  When `score --arm add --wm 3` runs
  Then the written record.json has metrics.regression_rate == 0.2

Scenario: regression_rate is 0.0 by definition before WM3   # M5
  Given a "done" wm1 record.json
  When `score --arm add --wm 1` runs
  Then the written record.json has metrics.regression_rate == 0.0
  And no regression-marked pytest subprocess is invoked for wm1

Scenario: context_rot_slope computed at WM3 from the 3-point fidelity trend   # M6
  Given wm1 record.json scored with spec_fidelity=0.9, wm2 scored with spec_fidelity=0.75, and wm3 about to be scored with spec_fidelity=0.6
  When `score --arm add --wm 3` runs
  Then the written record.json has metrics.context_rot_slope == -0.15   # least-squares slope of (1,0.9)(2,0.75)(3,0.6)

Scenario: context_rot_slope is 0.0 by definition before WM3   # M7
  Given a "done" wm2 record.json
  When `score --arm add --wm 2` runs
  Then the written record.json has metrics.context_rot_slope == 0.0

Scenario: scored write-back preserves the frozen shape   # M8
  Given a "done" wm1 record.json
  When `score --arm add --wm 1` runs and the resulting file is re-read
  Then benchmark.schema.run_record.validate() accepts it without raising
  And its metrics dict has exactly the 5 REQUIRED_METRICS keys, no more, no fewer

Scenario: score is idempotent on unchanged artifacts   # M9
  Given a "done" wm1 record.json, workspace, and transcript untouched since the last score
  When `score --arm add --wm 1` runs twice in a row (same fake-judge stub both times)
  Then both runs write numerically identical metrics
  And both runs exit 0

Scenario: WM3 prompt bait assertion is exact, not a loose or-chain   # M10
  Given benchmark/workload/wm3/PROMPT.md as committed
  When `test_prompts_identical_contract_and_bait` runs
  Then it asserts wm3's PROMPT.md names the duration_minutes -> end_time field removal specifically
  And it no longer passes merely because "wm1" or "task/booking" or "breaking" appears anywhere in the text

Scenario: unknown record.json path   # R1 record_not_found
  Given benchmark/runs/add/wm2/record.json does not exist
  When `score --arm add --wm 2` runs
  Then it exits 2 with "record_not_found"
  And no file is created under benchmark/runs/

Scenario: not-done record rejected   # R2 record_not_done
  Given a wm1 record.json with status "failed"
  When `score --arm add --wm 1` runs
  Then it exits 2 with "record_not_done"
  And the on-disk record.json is unchanged

Scenario: WM3 scored before WM1/WM2 are done   # R3 missing_prior_wm_record
  Given wm3's record.json is "done" but wm1's record.json does not exist yet
  When `score --arm add --wm 3` runs
  Then it exits 2 with "missing_prior_wm_record"
  And wm3's record.json is left unchanged (no partial metrics write)

Scenario: invalid WM index   # R4 invalid_wm
  Given no record.json is required to exist
  When `score --arm add --wm 4` runs
  Then it exits 2 with "invalid_wm"
  And no file is created or modified under benchmark/runs/

Scenario: unknown arm   # R5 unknown_arm
  Given "ghost" is not in benchmark.arms.loader.ARM_NAMES
  When `score --arm ghost --wm 1` runs
  Then it exits 2 with "unknown_arm"
  And no file is created or modified under benchmark/runs/

Scenario: judge output is not a parseable float   # R6 unparseable_judge_output
  Given a fake judge argv that prints "not-a-number"
  When `score --arm add --wm 1 --judge-cmd <fake-judge-argv>` runs
  Then it exits 2 with "unparseable_judge_output"
  And the on-disk record.json is left unchanged (no partial metrics write)

Scenario: regression subprocess itself errors   # R7 regression_run_failed
  Given the wm3 workspace app cannot even be collected against (e.g. oracle module import error)
  When `score --arm add --wm 3` runs
  Then it exits 2 with "regression_run_failed"
  And the on-disk wm3 record.json is left unchanged (no partial metrics write)
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI run.py score --arm <name> --wm <1|2|3> [--judge-cmd <argv...>]
  exit 0 -> re-validates/overwrites benchmark/runs/<arm>/wm<n>/record.json in place:
              metrics.tokens_total/cost_usd/time_to_first_edit -> unchanged (validated only)
              metrics.spec_fidelity -> judge score in [0.0, 1.0]
              metrics.regression_rate -> 0.0 (wm 1|2, by definition) | failed/total over the
                pytest -m regression re-run against test_refactor.py (wm3 only)
              metrics.context_rot_slope -> 0.0 (wm 1|2, by definition) | least-squares slope of
                (1, spec_fidelity@wm1), (2, spec_fidelity@wm2), (3, spec_fidelity@wm3)  (wm3 only)
              artifacts unchanged except an added "metrics_warnings" key when token_source was
                "unparseable" (never overwrites an existing artifact key)
  exit 2 -> "record_not_found" | "record_not_done" | "missing_prior_wm_record" | "invalid_wm"
            | "unknown_arm" | "unparseable_judge_output" | "regression_run_failed"
            (record.json on disk is left byte-unchanged for every exit-2 path)

Internal (importable) surface — the seam `score` is built from:
  score.score_record(arm_name: str, wm: int, *, judge_cmd: Sequence[str] | None = None,
                      runs_root: pathlib.Path | None = None) -> RunRecord
    — orchestrates read -> validate-eligibility -> compute -> write_record_atomic; raises
      BenchError("<code>: ...") for every Reject case above, never partially writes.
  judge.build_judge_argv(rubric_prompt: str, judge_cmd: Sequence[str] | None) -> list[str]
    — mirrors benchmark/runner/agent.py:build_argv; default is the real `claude -p <rubric>`
      invocation, tests inject a fake stdlib judge script (hermetic, no live claude).
  judge.judge_fidelity(workspace: pathlib.Path, wm: int, oracle_report: dict, *,
                        judge_cmd: Sequence[str] | None = None) -> float
    — runs build_judge_argv's argv, parses stdout as a float in [0.0, 1.0]; raises
      BenchError("unparseable_judge_output: ...") on anything else.
  score.compute_regression_rate(workspace: pathlib.Path) -> float
    — subprocess `pytest -m regression benchmark/workload/wm3/oracle/test_refactor.py`
      with BENCH_WORKSPACE=<workspace>, list-argv, parses the pass/fail counts; raises
      BenchError("regression_run_failed: ...") on a collection/execution error (not a normal
      test failure, which is signal, not error).
  score.compute_context_rot_slope(fidelities: list[float]) -> float
    — pure least-squares slope over (index, fidelity) pairs; 1-indexed by WM.
  score.read_prior_wm_record(arm_name: str, wm: int, *, runs_root=None) -> RunRecord
    — reads a sibling WM's already-scored record.json; raises
      BenchError("missing_prior_wm_record: ...") if absent or not status=="done".

Schema: no new persistent schema — reuses the frozen `benchmark/schema/run_record.py:RunRecord`/
  `validate` shape verbatim (this task is its second writer, after bench-runner); no sidecar file,
  no second ledger; one record.json per arm×wm remains the single source of truth.
```

Glossary deltas: **scored record** — a record.json whose 5 metrics have been overwritten by `score` with real computed values (vs a runner-fresh record, which still carries the `0.0` placeholders for regression_rate/spec_fidelity/context_rot_slope); **judge command** — the injectable argv seam (`judge_cmd`) tests substitute a fake stdlib script into, in place of a live `claude -p` rubric call, mirroring bench-runner's fake-agent seam.
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07; all 3 freeze questions answered: write-back approved · 0.0-by-definition pre-WM3 approved · judge prompt text deferred to build)
Least-sure flag surfaced at freeze: [contract] — the write-back-into-record.json vs sidecar decision (§1 ⚠1) is the single biggest unresolved shape question: nothing in MILESTONE.md or bench-runner's frozen §3 explicitly authorizes a SECOND writer to mutate a record.json that has already passed `validate()` once. If the human instead wants an append-only/immutable run-record (sidecar `score.json`, or a `scored: true` flag file), this whole §3 internal surface (`score_record`/`write_record_atomic` reuse) re-opens — cost: a re-cross to CONTRACT for this task only; the runner/schema task themselves stay untouched either way since `write_record_atomic` is reused as-is, not modified.
Reported: yes — freeze report (SHAPE/FLAGS/lead recommendation) rendered to the human; approved with both ⚠ flags explicitly accepted (write-back, 0.0-by-definition).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90%
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_refuses_not_done_record: arrange a wm1 record.json with status="timeout" / act `score --arm add --wm 1` / assert exit 2 "record_not_done" + assert record.json bytes unchanged · covers: M1, R2
  - test_validates_tokens_cost_first_edit_unchanged: arrange a "done" wm1 record with real tokens_total/cost_usd/time_to_first_edit / act score / assert those 3 fields identical post-write · covers: M2
  - test_unparseable_token_source_surfaced_not_masked: arrange artifacts["token_source"]="unparseable", tokens_total=0.0 / act score / assert tokens_total stays 0.0 + a metrics_warnings artifact names it · covers: M2
  - test_spec_fidelity_via_fake_judge: arrange a fake judge argv printing "0.82" / act score --judge-cmd <fake> / assert metrics.spec_fidelity == 0.82 + assert no subprocess spawns the literal "claude" binary · covers: M3
  - test_regression_rate_computed_at_wm3: arrange a fixture wm3 workspace where 2/10 regression-marked tests fail / act score --wm 3 / assert metrics.regression_rate == 0.2 · covers: M4
  - test_regression_rate_zero_before_wm3: arrange a "done" wm1 record / act score --wm 1 / assert metrics.regression_rate == 0.0 + assert no pytest subprocess invoked · covers: M5
  - test_context_rot_slope_computed_at_wm3: arrange wm1(0.9)/wm2(0.75) already-scored + wm3 about to score at 0.6 / act score --wm 3 / assert metrics.context_rot_slope == pytest.approx(-0.15) · covers: M6
  - test_context_rot_slope_zero_before_wm3: arrange a "done" wm2 record / act score --wm 2 / assert metrics.context_rot_slope == 0.0 · covers: M7
  - test_scored_record_still_validates: arrange a "done" wm1 record / act score / assert run_record.validate() accepts the re-read file + assert metrics.keys() == REQUIRED_METRICS exactly · covers: M8
  - test_score_is_idempotent: arrange a "done" wm1 record + fixed fake-judge stub / act score twice / assert both writes numerically identical + both exit 0 · covers: M9
  - test_wm3_bait_assertion_is_exact: arrange the committed wm3/PROMPT.md / act run test_prompts_identical_contract_and_bait / assert it checks the duration_minutes->end_time removal specifically (and fails if that phrase is stripped from a copy of the prompt) · covers: M10
  - test_record_not_found: arrange no wm2/record.json on disk / act score --wm 2 / assert exit 2 "record_not_found" + assert nothing created under benchmark/runs/ · covers: R1
  - test_missing_prior_wm_record: arrange wm3 record "done" but wm1's record.json absent / act score --wm 3 / assert exit 2 "missing_prior_wm_record" + assert wm3 record.json unchanged · covers: R3
  - test_invalid_wm: arrange no record required / act score --wm 4 / assert exit 2 "invalid_wm" + assert no file created/modified · covers: R4
  - test_unknown_arm: arrange "ghost" not in ARM_NAMES / act score --arm ghost --wm 1 / assert exit 2 "unknown_arm" + assert no file created/modified · covers: R5
  - test_unparseable_judge_output: arrange a fake judge argv printing "not-a-number" / act score --judge-cmd <fake> / assert exit 2 "unparseable_judge_output" + assert record.json unchanged · covers: R6
  - test_regression_run_failed: arrange a wm3 oracle fixture with a broken import (collection error) / act score --wm 3 / assert exit 2 "regression_run_failed" + assert wm3 record.json unchanged · covers: R7
</test_plan>

Tests live in: `./tests/` `benchmark/tests/` `benchmark/tests/test_workload_prompts.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/score.py` `benchmark/judge.py` `benchmark/run.py` `benchmark/tests/` `benchmark/tests/test_workload_prompts.py`
Strategy (ordered batches):
  1. `benchmark/judge.py` — `build_judge_argv`/`judge_fidelity`, mirroring `runner/agent.py`'s injectable-argv seam exactly (same shape, new module) — lowest-risk, no dependency on the others.
  2. `benchmark/score.py` — pure helpers first (`compute_context_rot_slope`, `compute_regression_rate`, `read_prior_wm_record`), each independently testable without the CLI.
  3. `benchmark/score.py:score_record` — the orchestrator wiring read -> eligibility checks (Reject cases) -> compute -> `write_record_atomic`; every Reject case as an early `BenchError` raise, no partial write path.
  4. `benchmark/run.py` — add the `score` subparser (parent `common`-style: `--arm`, `--wm`, `--judge-cmd`), wire to `score_record`, translate `BenchError` codes to the frozen exit-2 messages (same pattern as existing `run`/`resume` handlers).
  5. `benchmark/tests/test_workload_prompts.py` — tighten `test_prompts_identical_contract_and_bait`'s or-chain to the exact duration_minutes/end_time bait assertion (M10) — smallest, most isolated change, done last so it doesn't block the scorer's own red/green cycle.
Approach (domain strategy): stdlib-first fail-loud validation pipeline, matching the methodology-engine-dev discipline already established in `run_record.py`/`runner/core.py` — every eligibility check is a guard clause raising a named `BenchError` before any computation runs, so a Reject case never touches disk. The two genuinely-novel algorithms (least-squares slope, regression pass/fail ratio) are kept as pure functions with no I/O, tested in isolation before the orchestrator wires them to disk reads.
Data strategy: no new schema — read-modify-write over the frozen `RunRecord`/`validate()` shape via `write_record_atomic` (reused, not reimplemented); WM3's cross-record reads (`read_prior_wm_record`) are plain file reads of sibling `record.json`s, no new index/ledger.
Pattern: fixture-and-oracle pattern (bench-scaffold's own Observe-block pattern) extended one step further — score is the oracle-suite's CONSUMER, turning oracle pass/fail + judge output into the frozen metric numbers; the injectable-command seam explicitly extends `runner/agent.py`'s fake-agent pattern to a second subprocess boundary (the judge).
Optimization stance: correctness-first, no perf budget — pilot scale (5 arms × 3 WMs × 1 rep), same stance bench-scaffold/bench-runner already declared. ⚠ least-trusted facet: the rubric judge's real prompt/scoring text is an implementation detail deferred past this freeze (§1 assumption 2) — trusted least because a badly-worded rubric could produce spec_fidelity numbers that don't actually track prompt-requirement coverage, silently undermining the whole pilot's headline metric.
Persona (required): methodology-engine-dev — deterministic, fail-loud engine-adjacent code; this task is squarely "the engine that scores the engine's own benchmark," same domain stance as bench-runner/bench-scaffold.
Spawn isolation (default): worktree — prefer `isolation: "worktree"` for the TESTS/BUILD spawn (no stated reason to share the tree).
Known-problem fixes:
  - trap: sidecar-vs-write-back ambiguity (⚠1) → planned fix: write-back reusing `write_record_atomic` verbatim, decided in §3 (re-open at CONTRACT if the human disagrees at freeze).
  - trap: `metrics.keys()` exact-match rejecting a naive partial-update → planned fix: `score_record` always reads the full existing dict, mutates only the 3 computed keys in memory, re-validates the FULL 5-key dict before writing (never constructs a partial dict).
  - trap: conflating "structurally N/A" (WM1/WM2 regression_rate/context_rot_slope) with "failed to compute" → planned fix: M5/M7 are unconditional early-return branches in `score_record`, never routed through the same code path as a Reject-case raise.
  - trap: live-`claude`/live-LLM calls leaking into the hermetic suite → planned fix: every test exercises `judge_cmd`/agent-adjacent seams with a fake stdlib script; `compute_regression_rate`'s pytest subprocess runs against a stdlib-http-server fixture app, never a live agent.
Strategy actually used: as planned, batches 1-4 in order (judge.py -> score.py pure helpers -> score_record orchestrator -> run.py CLI wiring), with batch 5 (the M10 prompt-test tightening) done alongside batch 1 rather than last, since it was independent and smallest — no blocking dependency either way. RED was confirmed for the right reason (ImportError on `benchmark.score`, not a broken harness) by temporarily moving score.py/judge.py aside and reverting run.py's CLI wiring before the first pytest run, then restoring both. compute_regression_rate's "collection error" Reject path (R7) is exercised via a monkeypatched subprocess.run (returncode=2) rather than a genuinely broken oracle collection, since the frozen oracle files can't be perturbed to produce one hermetically; M4's "2 of 10 regression tests fail" is instead a real, unmocked `pytest -m regression` subprocess run against a from-scratch minimal stdlib HTTP fixture app (benchmark/tests/test_score.py's `_APP_PY`) whose only two natural failures are a genuine, inherent conflict already latent in the frozen wm1 vs wm2 oracle re-exports (WM1's `test_list_bookings`/`test_update_and_delete_booking` assume anonymous access; WM2's auth rules require it) — not an artificially injected defect.
Safety rule (feature-specific): a scored write is all-or-nothing — `score_record` computes everything into an in-memory dict, calls `validate()` once on the COMPLETE dict, and only then calls `write_record_atomic`; any exception before that point leaves the on-disk record.json untouched (no interleaved partial metric writes).
Code lives in: `benchmark/`
Constraints: do NOT change any test's assertions except the one named M10 tightening (`test_prompts_identical_contract_and_bait`, explicitly in-scope per the absorbed spec delta) or the frozen contract; allow-list packages only (stdlib + pytest, already a project dependency); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 59/59 green (`uv run --with pytest pytest benchmark/tests -q` → "59 passed in 15.74s"); `python3 .add/tooling/add.py check` → "611 passed, 0 failed (85 warnings)"
- [x] coverage did not decrease — score.py 96% / judge.py 84% (93% combined vs 90% target), per build report; no coverage regression in touched files observed during this review
- [x] no test or contract was altered during build — `git diff HEAD~1 -- benchmark/tests/test_workload_prompts.py` shows exactly the M10-authorized change (loose 3-way or-chain → exact `duration_minutes`/`end_time` assertions); §3 CONTRACT block unchanged since freeze (Status: FROZEN @ v1, no diff)
- [x] the green was EARNED, not gamed — see Refute-read verdict below: EARNED
- [x] concurrency / timing of the risky operation is safe (with one noted RESIDUE — see Advisor lens 2 below)
- [x] no exposed secrets, injection openings, or unexpected dependencies — `grep -rn "shell=True"` over `benchmark/` = 0 hits; all subprocess calls are list-argv (`judge.py:71`, `score.py:81`); no new third-party deps (stdlib + pytest only)
- [x] layering & dependencies follow CONVENTIONS.md — score/judge sit above runner/schema, never modify them; judge.py mirrors runner/agent.py's injectable-argv seam shape exactly
- [ ] a person reviewed and approved the change — pending human gate (this is a proposed recommendation, not the recorded gate)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `python benchmark/run.py score --arm add --wm 1` against a fixture "done" record rewrites metrics.spec_fidelity/regression_rate(=0.0)/context_rot_slope(=0.0) while leaving tokens_total/cost_usd/time_to_first_edit byte-identical — confirmed via `test_validates_tokens_cost_first_edit_unchanged` (score.py:162-165 validates-only, never recomputes those 3 keys) — re-ran green
- [x] `score --arm add --wm 3` against fixture wm1/wm2/wm3 records with known spec_fidelity values produces the exact least-squares slope by hand-calculation — hand-computed (1,0.9)(2,0.75)(3,0.6): x̄=2, ȳ=0.75, numerator=(-1)(0.15)+(0)(0)+(1)(-0.15)=-0.3, denominator=1+0+1=2, slope=-0.15 — matches `test_context_rot_slope_computed_at_wm3`'s asserted `pytest.approx(-0.15)` exactly; `compute_context_rot_slope` (score.py:56-69) is a pure function, verified by direct read
- [x] `score --arm add --wm 3` against a fixture with N of the 10 regression-marked tests failing produces regression_rate == N/10 exactly — re-ran `test_regression_rate_computed_at_wm3` standalone (`pytest -k regression_rate_computed_at_wm3 -v` → 1 passed); this is a REAL unmocked `pytest -m regression` subprocess against a real fixture HTTP app (score.py:_APP_PY), not stubbed — asserts `regression_rate == pytest.approx(0.2)` from a genuine wm1/wm2 auth-rule conflict (not an injected defect), matching the build report's claim
- [x] every one of the 7 Reject codes is reachable and, when triggered, leaves the on-disk record.json (if any) byte-unchanged — confirmed by reading `test_score.py`'s `before = record_path.read_bytes()` / `assert record_path.read_bytes() == before` pattern present at lines 242/247 and 472/477, and equivalently for each Reject-path test (R1/R3/R4/R5/R6/R7 + M1/R2)
- [x] no test in the suite spawns the literal `claude` binary — `test_spec_fidelity_via_fake_judge` monkeypatches `judge.subprocess.run` as a spy and asserts `"claude" not in argv` for every captured call; `grep -rn '"claude"' benchmark/tests/` shows only this assertion, never an actual invocation
- [x] `test_prompts_identical_contract_and_bait` fails if wm3/PROMPT.md's duration_minutes->end_time bait language is stripped from a copy — confirmed: `test_wm3_bait_assertion_is_exact` (test_score.py:437+) builds a stripped copy (`.replace("duration_minutes", "").replace("end_time", "")`) and the surrounding test asserts a failure on that copy — mutation-style self-check present
- [x] a scored record.json still passes `benchmark/schema/run_record.py:validate()` unmodified — `score_record` (score.py:197-206) calls the frozen `validate()` on the complete 5-key dict before every write; `test_scored_record_still_validates` covers this directly

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `score.score_record` is called from `run.py`'s new `score` subparser (confirmed via `git diff --stat` showing `benchmark/run.py | 120 ++++`); `judge.judge_fidelity` is called from `score_record` (score.py:181); `compute_regression_rate`/`compute_context_rot_slope`/`read_prior_wm_record` are all called from `score_record`'s wm==3 branch (score.py:152-155, 185-186) — no orphaned new symbol found
- [x] DEAD-CODE (code) — every new public function in score.py/judge.py (`build_judge_argv`, `default_judge_cmd`, `build_rubric_prompt`, `judge_fidelity`, `compute_context_rot_slope`, `compute_regression_rate`, `read_prior_wm_record`, `score_record`) is exercised by at least one test in test_score.py per the §4 test_plan mapping; none unused
- [ ] SEMANTIC (prose / non-code) — N/A, this task is code not prose (test_workload_prompts.py's tightened prose assertion covered under Build expectations above)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct Read of `benchmark/score.py` (score_record, compute_context_rot_slope, compute_regression_rate, read_prior_wm_record all present at the cited signatures) and `benchmark/judge.py` (build_judge_argv, judge_fidelity present); `RunRecord`/`validate`/`BenchError`/`write_record_atomic` imports resolve cleanly (score.py:20-23)
- [x] no anchor moved/renamed since Ground SHA (8668859) — this is the FIRST commit introducing score.py/judge.py, so no drift window existed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-verify, tdd-verifier persona) · adversarially checked:
  - judge_fidelity: probed for silent-default behavior — confirmed BenchError raised (not a masked 0.0) on empty stdout, non-float stdout, and out-of-range/NaN values (judge.py:83-92); no fallback path found
  - compute_context_rot_slope: hand-computed the M6 fixture's slope independently (-0.15) and it matches the test's asserted value exactly — not a vacuous `assert result == result` pattern; WM1/WM2's 0.0-by-definition path (score.py:187-191) is a structurally separate unconditional branch, never sharing code with the Reject-raise path, so a real failure could not be silently coerced to the same 0.0
  - compute_regression_rate: re-ran `test_regression_rate_computed_at_wm3` in isolation — confirmed it is a genuine subprocess run against a real fixture app producing a real 2/10 failure ratio (not asserted against a monkeypatched/stubbed subprocess as M4's real path), while R7 correctly uses a monkeypatch only for the unreproducible collection-error path — the two are not conflated
  - write-back byte-identity: read the exact `before/after` byte-comparison assertions in test_score.py rather than trusting the build report's prose claim
  - M10: diffed the actual test file change against the frozen bundle's exact M10 wording — confirms ONLY that one assertion changed, no other test weakened
- No stubbed-away logic, no overfit-to-fixture-only assertion, no vacuous pass found. Full suite reruns green from a fresh invocation (not just relying on the build's earlier claim).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (add-verify)
1. Security: CLEAR — no `shell=True` anywhere in benchmark/; both new subprocess call sites (judge.py:71, score.py:81) use list-form argv exclusively; the judge's rubric prompt is passed as a single argv element (never interpolated into a shell string), so no argv/shell injection surface from PROMPT.md content or arbitrary rubric text; no secrets touched; no new third-party dependency (stdlib + pytest only, matching the allow-list constraint)
2. Concurrency: RESIDUE — `write_record_atomic`'s temp-file+`os.replace` is atomic PER WRITE (no corrupt/partial file possible), but there is no lock guarding two concurrent `score` invocations against the SAME record.json: a second writer racing the first would read-modify-write on a stale in-memory copy and the last `os.replace` wins, silently dropping the first writer's computed metrics (no error, no BenchError, no detection). This is not a new class of bug (bench-runner's `execute_wm` has the same single-writer assumption), and the CLI's a-single-operator/pilot-scale usage (5 arms × 3 WMs × 1 rep, no stated concurrent invocation) makes actual contention unlikely — but it is real, unmitigated, and undocumented as a constraint anywhere in §3. Recommend: note this as a known limitation in Observe/§7, not a blocking gap for this pilot-scale task.
3. Architecture: CLEAR — score/judge sit strictly above runner/schema (import direction: score.py imports from runner.records and schema.run_record, never the reverse); no new schema/ledger; judge.py mirrors runner/agent.py's seam shape exactly per the Honors pattern; stdlib-first honored throughout
Verdict: PASS (with concurrency RESIDUE noted, non-blocking at pilot scale)
Residue: concurrency — no second-writer lock on record.json across concurrent `score` invocations (see lens 2); recommend documenting as an operational constraint (single-operator CLI use) rather than a code fix, since bench-runner's own writer has the identical assumption and no scenario in §2 covers concurrent scoring
Binding: advisory — this is not a security/mechanical-sensitivity finding, and no domain sensitivity classes are yet declared (per `add.py check`'s `sensitivity_classes_unset` warning, a pre-existing project-wide gap, not specific to this task)

### GATE RECORD
Reported: yes — this Verify report is the gate report, rendered before recording
Outcome: PASS
Reviewed by: add-verify (tdd-verifier persona) · date: 2026-07-07 — recommendation only; the human is the final approver of this recorded outcome (per boundary: MUST NOT auto-run `add.py gate`)

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `unparseable_judge_output` rate during the live pilot (each one = a judge-prompt robustness problem) · `regression_run_failed` occurrences (an oracle infrastructure failure, distinct from a real regression) · **operational constraint: `score` assumes a single operator — two concurrent score invocations on the same record.json are last-write-wins with no lock/detection (Advisor concurrency residue, acceptable at pilot scale; revisit before any parallel scale-up)** · WM3 regression-rate spread across arms (if every arm scores ~0 or ~1, the bait is mis-tuned).

### Decisions (ADR)
- [AI] specify — chose **write-back into record.json**; rejected sidecar `score.json` per WM (rejected: `validate()`'s exact metrics-key match means a sidecar would either duplicate the same 5-key schema — two files that can silently drift — or force a second schema that MILESTONE.md never asked for; write-back keeps ONE source of truth and reuses the already-frozen atomic writer verbatim) · a single `report`-owned cross-WM aggregator instead of per-WM `score` (rejected: MILESTONE.md's task stub explicitly separates `score` from `report`, and `context_rot_slope`/`regression_rate` needing prior-WM data is handled by reading sibling record.json files, not by merging the two tasks).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (2026-07-07; all 3 freeze questions answered: write-back approved · 0.0-by-definition pre-WM3 approved · judge prompt text deferred to build))
- [AI] build — approach: stdlib-first fail-loud validation pipeline, matching the methodology-engine-dev discipline already established in `run_record.py`/`runner/core.py` — every eligibility check is a guard clause raising a named `BenchError` before any computation runs, so a Reject case never touches disk. The two genuinely-novel algorithms (least-squares slope, regression pass/fail ratio) are kept as pure functions with no I/O, tested in isolation before the orchestrator wires them to disk reads.
- [AI] build — data strategy: no new schema — read-modify-write over the frozen `RunRecord`/`validate()` shape via `write_record_atomic` (reused, not reimplemented); WM3's cross-record reads (`read_prior_wm_record`) are plain file reads of sibling `record.json`s, no new index/ledger.
- [AI] build — pattern: fixture-and-oracle pattern (bench-scaffold's own Observe-block pattern) extended one step further — score is the oracle-suite's CONSUMER, turning oracle pass/fail + judge output into the frozen metric numbers; the injectable-command seam explicitly extends `runner/agent.py`'s fake-agent pattern to a second subprocess boundary (the judge).
- [AI] build — optimization stance: correctness-first, no perf budget — pilot scale (5 arms × 3 WMs × 1 rep), same stance bench-scaffold/bench-runner already declared. ⚠ least-trusted facet: the rubric judge's real prompt/scoring text is an implementation detail deferred past this freeze (§1 assumption 2) — trusted least because a badly-worded rubric could produce spec_fidelity numbers that don't actually track prompt-requirement coverage, silently undermining the whole pilot's headline metric.
- [AI] build — strategy used: as planned, batches 1-4 in order (judge.py -> score.py pure helpers -> score_record orchestrator -> run.py CLI wiring), with batch 5 (the M10 prompt-test tightening) done alongside batch 1 rather than last, since it was independent and smallest — no blocking dependency either way. RED was confirmed for the right reason (ImportError on `benchmark.score`, not a broken harness) by temporarily moving score.py/judge.py aside and reverting run.py's CLI wiring before the first pytest run, then restoring both. compute_regression_rate's "collection error" Reject path (R7) is exercised via a monkeypatched subprocess.run (returncode=2) rather than a genuinely broken oracle collection, since the frozen oracle files can't be perturbed to produce one hermetically; M4's "2 of 10 regression tests fail" is instead a real, unmocked `pytest -m regression` subprocess run against a from-scratch minimal stdlib HTTP fixture app (benchmark/tests/test_score.py's `_APP_PY`) whose only two natural failures are a genuine, inherent conflict already latent in the frozen wm1 vs wm2 oracle re-exports (WM1's `test_list_bookings`/`test_update_and_delete_booking` assume anonymous access; WM2's auth rules require it) — not an artificially injected defect.
- [AI] verify — gate PASS (reviewed by add-verify (tdd-verifier persona))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · seeded] single-operator/no-concurrent-score constraint documented in Watch above; formalize (a lock or a scored-by stamp) before any multi-rep parallel scale-up (evidence: verify Advisor lens 2 — last-write-wins on record.json)
- [SPEC · open] the real rubric-judge prompt text (deferred to build, shipped as a first cut) has never met a real arm output — bench-pilot-report should human-spot-check 2-3 judge verdicts against the workspaces before trusting spec_fidelity (evidence: judge seam is hermetic-tested only)
- [SPEC · open] `add.py check` emits rule_coverage_gap for this task's 7 Reject codes despite §4 listing covers: R1..R7 — likely a covers:-tag format mismatch in the audit parser, needs an engine-side look (evidence: verify 💭 note; warnings, not failures)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] the strongest scorer test was the un-mocked one: a real `pytest -m regression` subprocess against a real fixture app surfaced a genuine WM1-vs-WM2 auth conflict no mock would have shown (evidence: M4 scenario, 2/10 real failures)
- [SDD · open] absorbing a carried delta INTO a frozen bundle (M10's exact-assertion tightening named in §1/§2/§5) is the clean way to authorize a pre-existing-test edit — no re-cross needed because the freeze itself covered it (evidence: verify's git-diff scope check passed)

