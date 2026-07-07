# TASK: scorers for the 5 frozen metrics: oracle re-runs (regression_rate), rubric judge (spec_fidelity), token/cost ledger, context-rot slope, time-to-first-edit

slug: bench-scoring · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: tests   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

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

<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

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

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

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
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

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
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

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
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned")>
Safety rule (feature-specific): a scored write is all-or-nothing — `score_record` computes everything into an in-memory dict, calls `validate()` once on the COMPLETE dict, and only then calls `write_record_atomic`; any exception before that point leaves the on-disk record.json untouched (no interleaved partial metric writes).
Code lives in: `benchmark/`
Constraints: do NOT change any test's assertions except the one named M10 tightening (`test_prompts_identical_contract_and_bait`, explicitly in-scope per the absorbed spec delta) or the frozen contract; allow-list packages only (stdlib + pytest, already a project dependency); ask if unclear.

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
- [ ] `python benchmark/run.py score --arm add --wm 1` against a fixture "done" record rewrites metrics.spec_fidelity/regression_rate(=0.0)/context_rot_slope(=0.0) while leaving tokens_total/cost_usd/time_to_first_edit byte-identical — confirmed by diffing record.json before/after
- [ ] `score --arm add --wm 3` against fixture wm1/wm2/wm3 records with known spec_fidelity values produces the exact least-squares slope by hand-calculation — confirmed by a direct numeric assertion in test output
- [ ] `score --arm add --wm 3` against a fixture with N of the 10 regression-marked tests failing produces regression_rate == N/10 exactly — confirmed by the printed record.json's metrics field
- [ ] every one of the 7 Reject codes is reachable and, when triggered, leaves the on-disk record.json (if any) byte-unchanged — confirmed by a before/after hash comparison per rejection test
- [ ] no test in the suite spawns the literal `claude` binary — confirmed by grepping test output/process list during the run, or by a monkeypatched subprocess assertion
- [ ] `test_prompts_identical_contract_and_bait` fails if wm3/PROMPT.md's duration_minutes->end_time bait language is stripped from a copy — confirmed by a mutation check in the test itself
- [ ] a scored record.json still passes `benchmark/schema/run_record.py:validate()` unmodified — confirmed by re-importing and calling validate() on the written file in a test

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
