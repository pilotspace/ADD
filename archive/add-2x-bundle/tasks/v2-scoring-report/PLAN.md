# TASK: Two-axis scoring report — trust vector + cost-per-trusted-feature (no agent spend)

slug: v2-scoring-report · created: 2026-07-10 · stage: mvp
milestone: add-bench-v2
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `benchmark/report.py` — v1 layer: `_load_record` hardwires `wm{n}`; `METRIC_COLUMNS` headlines judge spec_fidelity; `render_report` pure over records
- `benchmark/tamper.py` — `_test_functions` (name → assert-fingerprint multiset) is ALL the data a rename-tolerant weakened verdict needs; snapshots exist per arm/step for every rep0 record (wm + hv)
- `benchmark/score.py:compute_regression_rate_v2` — reads `workload/{family}{k}/oracle/survivors.py`
- `benchmark/workload/wm1|wm2/oracle/survivors.py` — fixed 2026-08 windows (the pollution source, twice proven); hv1/hv2 are byte-guard-locked copies (test_hv_base_pair_matches_wm_bytes) so any wm fix must be re-copied
- record artifacts hold NO own-suite-run result (only attempts/model/…); own-suite GREEN is not derivable from records alone
Context (working folder): MILESTONE.md trusted-flag floor + trust-vector decisions (2026-07-10) · both rep0 ledgers (results/2026-07-wv1-rep0.md · 2026-07-wv2-rep0.md) · §7 deltas from tasks 2–3 (rename tolerance · caveat printing · disjoint windows · cost-only separation)
Honors: deterministic-first · honest-outcome clause · trust axis = vector never one float · archived records immutable except additive provenance
Seams consulted: none applicable
Anchors the contract cites: `report.py:_load_record/render_report/METRIC_COLUMNS` · `tamper.py:_test_functions/compute_tests_weakened` · `workload/wm{1,2}/oracle/survivors.py` · new `trust.py` module
Issues/Risks (→ feed §1):
(1) own-suite-GREEN needs execution — archived workspaces are stdlib-only apps (entry contract) so `pytest` in-workspace is feasible at report time, but collection/env failures must render "unverified", never fake a green.
(2) hv1/hv2 byte-guard: fixing wm1/wm2 survivor windows REQUIRES re-copying to hv1/hv2 in the same change or the guard goes red.
(3) rep0 archives were scored on the OLD windows — window changes alter no archived score (regression already corrected via clean-clone provenance); only FUTURE campaigns benefit.
(4) rename tolerance must not create a gaming hole: moving asserts to a renamed fn is fine, but a rename that DROPS fingerprints still counts — match multisets, count only what vanished.
Related intent: milestone exit criterion 5 (one report prints BOTH axes with the honest-outcome clause applied) · shared decisions: trusted-flag floor · trust vector · control arm
Ground SHA: `aa19ea4`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: two-axis scoring report — trust vector + cost-per-trusted-feature (no agent spend)
Framings weighed: new trust.py module + report v2 section (chosen) · rewrite report.py wholesale (rejected: v1 tables are test-pinned and still honest for v1 records) · trusted flag stored INTO records (rejected: derived verdicts must stay recomputable; records stay raw + provenance-only)
Must:
<must>
  - `benchmark/trust.py`: `weakened_verdict(arm_runs_root, wm, family)` — rename-tolerant mechanical verdict over the existing snapshots: a removed fn whose fingerprint multiset reappears (subset-match) under another name is a RENAME not a removal; only VANISHED fingerprints count; returns {raw_count, adjusted_count, verdict: clean|evolution|weakened, detail}
  - `benchmark/trust.py`: `own_suite_status(workspace)` — report-time best-effort: run pytest on the arm's OWN tests in the archived workspace; returns green|red|unverified (collection/env failure -> unverified, NEVER a fake green) + test count from the snapshot
  - `benchmark/trust.py`: `trusted(record, arm_runs_root, family)` — the milestone floor: oracle_pass_rate == 1.0 AND regression_rate == 0.0 AND adjusted weakened verdict != weakened AND own suite exists AND own_suite_status == green; returns the full VECTOR {trusted: bool, pass, regression, weakened_raw, weakened_adjusted, weakened_verdict, own_tests, own_suite}; the vector prints EVERYWHERE the flag prints — never the bool alone
  - report v2: `render_trust_report(runs_root, family)` — per-arm × per-step trust-vector table + the two-axis headline: v1 raw cost-per-feature BESIDE cost-per-TRUSTED-feature (cost / trusted-step-count); every tests_weakened cell carries the caveat marker and verdict; honest-outcome line REQUIRED when all arms tie on trust (rep0 reality: cost-only separation)
  - `_load_record` grows the family arg (default "wm") so hv records render
  - wm1/wm2 survivors move to per-probe disjoint far-future windows (2028 days, one day per probe fn) AND hv1/hv2 copies are refreshed in the same change (byte-guard stays green); the survivors' probe SEMANTICS are unchanged
  - the report renders from records + snapshots alone — no judge call, no agent spend; archived records are never mutated by the report path
</must>
Reject:
<reject>
  - own-suite execution failure rendered as green -> "own_suite_unverified" must show instead
  - the trusted bool printed without its vector -> forbidden by test (grep the rendered output)
  - a rename that DROPS fingerprints scored as clean -> adjusted count must still count vanished fingerprints
  - survivors window change altering any probe's assert semantics -> the survivors pins (tokens, fn count, no-fallback-on-409) must stay green
  - report path writing to any record.json -> "report_is_read_only"
</reject>
After:
<after>
  - `python3 -m benchmark.report --trust --runs-root <rep0> --family hv` (and wm) renders the trust-vector table + two-axis headline for both rep0 archives
  - rep0 verdicts render honestly: all arms trusted at every step except add wm2 (pass 0.8 -> untrusted, the vector shows why); headline shows cost-per-trusted-feature ≈ cost/3 per arm with spec-kit/vanilla cheapest
  - wm1/wm2 + hv1/hv2 survivors book disjoint 2028 windows; full suite green
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ own-suite report-time execution works on archived workspaces (stdlib apps, pytest available) — lowest confidence because arms may import third-party test deps or need their .venv; if wrong: those cells render "unverified" and the trusted flag can NOT be earned for those records — the report stays honest but sparser. Mitigation: unverified is a designed outcome, not a failure.
  - [ ] snapshot fingerprint data suffices for rename-matching (no source re-read needed) — confirmed at ground: _test_functions returns name -> multiset
  - [ ] report CLI shape: extend benchmark.report main with --trust/--family flags rather than a new entrypoint — verify report.py has a main/CLI at tests time
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: rename is not weakening, dropped fingerprints still are   # M1, R3
  Given a prior snapshot with test_a (3 asserts) and a current one where test_a is renamed test_a_scoped with the same 3 fingerprints
  When weakened_verdict runs
  Then raw_count > 0 but adjusted_count == 0 and verdict == "evolution"
  And renaming while dropping 1 of the 3 fingerprints yields adjusted_count == 1 and verdict == "weakened"

Scenario: own-suite status never fakes a green   # M2, R1
  Given an archived workspace whose tests cannot even collect
  When own_suite_status runs
  Then it returns "unverified" (and green only when pytest exits 0 on real collected tests)

Scenario: the trusted flag is a vector, never a bare bool   # M3, R2
  Given a scored record with all floors held
  When trusted() evaluates and the report renders
  Then the output carries the full vector (pass · regression · weakened raw/adjusted/verdict · own_tests · own_suite)
  And no rendered line shows the flag without the vector

Scenario: the two-axis headline prints honestly   # M4
  Given the WV1 and WV2 rep0 archives
  When render_trust_report runs for each family
  Then v1 raw cost-per-feature and cost-per-TRUSTED-feature print side by side
  And when all arms tie on trust the honest-outcome line states cost-only separation

Scenario: survivors get disjoint windows without semantic change   # M5, R4
  Given wm1/wm2 survivors rewritten to per-probe 2028 days
  When the survivors pins and the hv byte-equality guard run
  Then all stay green (tokens carried, fn counts, no-fallback-on-409, hv copies refreshed)

Scenario: the report is read-only over records   # M6, R5
  Given any render call over an archive
  When it completes
  Then every record.json byte-hash is unchanged
```
</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
benchmark/trust.py (NEW — pure over snapshots/records/workspaces):
  weakened_verdict(arm_runs_root, wm, family="wm") -> {raw_count, adjusted_count, verdict: "clean"|"evolution"|"weakened", detail: [str]}
    rename-tolerance: a removed fn whose fingerprint multiset is a SUBSET of some added fn's multiset = rename; only fingerprints present in NO current fn count toward adjusted_count
  own_suite_status(workspace) -> {status: "green"|"red"|"unverified", tests: int}
    report-time `python -m pytest <workspace tests>` cwd=workspace; exit 0 + >0 collected = green · exit 1 = red · anything else = unverified
  trusted(record, arm_runs_root, family="wm") -> {trusted: bool, pass_rate, regression, weakened_raw, weakened_adjusted, weakened_verdict, own_tests, own_suite}
    floor: pass_rate == 1.0 AND regression == 0.0 AND verdict != "weakened" AND own_tests > 0 AND own_suite == "green"

benchmark/report.py (v2 additions, v1 tables untouched):
  _load_record(runs_root, arm, wm, family="wm")
  render_trust_report(runs_root, arms, steps, family="wm") -> str   # per-arm × per-step vector table + two-axis headline (v1 cost-per-feature BESIDE cost-per-trusted-feature = rep cost / trusted steps) + tests_weakened caveat marker on every weakened cell + honest-outcome line when trust ties
  CLI: python -m benchmark.report --trust --runs-root <dir> --family wm|hv [--arms ...]
  read-only: no record.json write path exists in the module

workload survivors (M5 — semantics frozen, windows moved):
  wm1/wm2 oracle/survivors.py: each probe fn books its OWN 2028 calendar day; tokens/probe-count/no-fallback-on-409 unchanged; hv1/hv2 copies refreshed in the same commit (byte-guard green)
Schema: records untouched (report derives; provenance stays additive-only)
```
Glossary deltas: `Trust vector: the per-step tuple (fidelity · regression · weakened raw/adjusted/verdict · own-suite evidence) — the only form the trusted flag may print in` · `Cost-per-trusted-feature: rep cost divided by trusted step count — the v2 headline printed beside v1 raw cost-per-feature`
Least-sure flag surfaced at freeze: [spec] own-suite report-time execution on archived workspaces may not collect (third-party test deps, stale envs) — those cells render "unverified" and CANNOT earn trusted; if widespread, the rep0 trust tables go sparse and the honest fix is recording own-suite results at execute time in FUTURE campaigns (a meter change, out of this task's scope)
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — banner/ARC/SHAPE + the ⚠ own-suite-execution flag rendered before the freeze question

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/` `tmp/`
Strategy (ordered batches): 1. red suite first (11 pins, test_trust_report.py) 2. trust.py (weakened_verdict → own_suite_status → trusted) 3. report.py v2 section (render_trust_report + argparse CLI) 4. wm2 survivors → disjoint 2028 windows + hv2 byte-refresh 5. prove against BOTH real rep0 archives before the gate
Approach (domain strategy): rename-tolerant weakening = pooled-fingerprint set difference (Counter over ALL fns per side) laid OVER the raw per-fn tamper diff — the raw count stays (mechanical truth), the adjusted count answers "did any assertion actually vanish"; trust is a floor vector, never a bare bool
Data strategy: 8-key trust vector dict per (arm, step); fingerprints reuse tamper.py's `_test_functions` census verbatim (no second census); records are READ-ONLY inputs — the report never writes into an archive
Pattern: extends the existing benchmark.report module + tamper fingerprint census (§0 Honors) — v2 is an appended section and CLI flag, not a new entrypoint
Optimization stance: correctness-first, no budget; ⚠ own-suite report-time execution (arm workspaces may not collect in the report host env → honest "unverified", never fake green)

Persona (required): methodology-engine-dev
Spawn isolation (default): inline, no spawns — sequential scoring-layer build (inline-over-heavy-spawns feedback); shared tree
Known-problem fixes: probe-state pollution (proven 2× in WV2 rep0) → per-probe disjoint 2028 days; fake green → green requires pytest exit 0 AND " passed" AND >0 collected; heredoc `\n` evaluation corrupting report.py → escaped-newline writes then normalize
Strategy actually used: as planned, plus one repair — the report.py heredoc write evaluated `\n` inside the payload and corrupted two join lines; repaired in place before the suite ran
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `benchmark/tests/` 190 passed in 49.96s (full suite, post-survivors-move)
- [x] coverage did not decrease — 11 new pins added (test_trust_report.py); zero tests removed; v1 report pins untouched
- [x] no test or contract was altered during build — the one red pin went green via survivors.py (in-scope build target, not a test); §3 @v1 untouched since freeze
- [x] the green was EARNED, not gamed — refute-read below; the strongest evidence is LIVE renders against both real rep0 archives producing numbers that reconcile with the record ledgers by hand
- [x] concurrency / timing of the risky operation is safe — report is single-threaded; own-suite subprocess has a 120s timeout and `-p no:cacheprovider` (no state left in workspaces)
- [x] no exposed secrets, injection openings, or unexpected dependencies — subprocess uses a fixed argv LIST (no shell), stdlib-only imports, archives read-only
- [x] layering & dependencies follow CONVENTIONS.md — trust.py derives from tamper.py's census (one fingerprint definition); report.py extends the existing module/CLI
- [x] a person reviewed and approved the change — human froze §3 @v1; gate auto-resolved under `autonomy: auto` on the evidence above

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `python3 -m benchmark.report --trust --runs-root <both rep0 archives>` renders trust tables + two-axis headline for wm AND hv families — confirmed by running it on the real archives at the gate: WV1 wm renders 12 vector rows + two-axis (spec-kit $1.14 · vanilla $1.53 · add $4.65 · add-main $13.94 per trusted feature); WV2 hv renders 12 rows + two-axis
- [x] full suite green (v1 report pins untouched); survivors window move keeps all survivors/byte-guard pins green — 190 passed (incl. test_report.py, test_wv1_survivors.py, test_wv2_family.py byte-guard)
- [x] rep0 render shows add wm2 untrusted with the vector explaining why (pass 0.80, `trusted NO`) — read in the output. DEVIATION, disclosed: the honest-outcome cost-only line did NOT render on the real archives — the rename-tolerant ADJUSTED verdict marks add-main wm2/wm3, vanilla wm2, vanilla hv2 as weakened (fingerprints genuinely vanished during rule rewrites), so trusted counts do not tie. The tie path was proven LIVE on an all-arms-tie fixture (scratchpad render: "**Honest-outcome:** … separation is cost-only." printed). The expectation predicted the archives' shape, not the code's; the code behaves as contracted.
- [x] record.json hashes unchanged after rendering — test_report_is_read_only_over_records green (sha256 before/after over rglob record.json)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — weakened_verdict/own_suite_status/trusted all imported and called by report.py:129 (render_trust_report) and test_trust_report.py; render_trust_report ← main ← `__main__` (report.py:184/202); CLI exercised live on both archives
- [x] DEAD-CODE (code) — no orphan: every new fn referenced (above); `detail` key of weakened_verdict is the hand-diff evidence surface consumed by the report's weakened cells
- [x] SEMANTIC (prose / non-code) — both rendered reports read in full: WV1/WV2 numbers cross-checked against the rep0 ledgers (`benchmark/results/2026-07-wv*.md`) — costs, pass rates, add wm2 0.80 all reconcile

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `_test_functions` (benchmark/tamper.py), `compute_tests_weakened`, `RunRecord.from_json`, `report.main` all import-resolve (190-test suite + live CLI runs would fail loudly otherwise)
- [x] any anchor that moved/renamed since Ground SHA (aa19ea4) is named here, not left silent — none moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) own-suite "green" cannot be faked — requires a REAL pytest subprocess exit 0 + " passed" + >0 collected fns; the uncollectable-import fixture correctly lands "unverified". (2) read-only pin actually re-hashes every record.json after a full render (which runs the pytest subprocesses) — not a mock. (3) honest-outcome tie line is NOT dead code — proven live on a tie fixture since the real archives don't tie. (4) known soft spot, disclosed: test_wm_survivors_use_disjoint_2028_windows is vacuous for wm1 (it books no windows by design — only wm2 binds); the wm2 half binds all four bookings. (5) the adjusted-verdict logic disagreeing with the earlier hand-diff on 4 cells was hand-re-checked: those cells DID lose fingerprints (assert lines rewritten under new rules) — the metric reports the mechanical truth and the caveat line carries the hand-diff context; not a false green, a stricter honest reading.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — fixed argv list subprocess (no shell interpolation), cwd pinned to the archive workspace, no network, no secrets read; report never writes outside stdout
2. Concurrency: CLEAR — sequential rendering; the only subprocess is timeout-bounded (120s) and cache-provider-disabled so parallel report runs cannot corrupt a workspace
3. Architecture: CLEAR — single fingerprint census reused from tamper.py; v2 report appended to the existing module + CLI (no parallel entrypoint); records stay read-only by contract and by pin
Verdict: PASS
Residue: none
Binding: advisory — no sensitivity declared (mechanical-adjacent scoring layer)

### GATE RECORD
Reported: yes — gate report (banner/ARC + evidence + the disclosed honest-outcome deviation) rendered in-session before this outcome recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto — complete evidence, no security finding, no residue) · date: 2026-07-10

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): unverified own-suite cell rate on future campaign renders (>0 sustained → move own-suite recording to execute time) · the honest-outcome line's tie condition on future reps (it fired on neither rep0 archive — the adjusted verdict separates arms) · report wall time (own-suite subprocess ×12 records ≈ tens of seconds; budget: tolerable for a report, never for scoring)

### Decisions (ADR)
- [AI] specify — chose new trust.py module + report v2 section; rejected rewrite report.py wholesale (rejected: v1 tables are test-pinned and still honest for v1 records) · trusted flag stored INTO records (rejected: derived verdicts must stay recomputable; records stay raw + provenance-only)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: rename-tolerant weakening = pooled-fingerprint set difference (Counter over ALL fns per side) laid OVER the raw per-fn tamper diff — the raw count stays (mechanical truth), the adjusted count answers "did any assertion actually vanish"; trust is a floor vector, never a bare bool
- [AI] build — data strategy: 8-key trust vector dict per (arm, step); fingerprints reuse tamper.py's `_test_functions` census verbatim (no second census); records are READ-ONLY inputs — the report never writes into an archive
- [AI] build — pattern: extends the existing benchmark.report module + tamper fingerprint census (§0 Honors) — v2 is an appended section and CLI flag, not a new entrypoint
- [AI] build — optimization stance: correctness-first, no budget; ⚠ own-suite report-time execution (arm workspaces may not collect in the report host env → honest "unverified", never fake green)
- [AI] build — strategy used: as planned, plus one repair — the report.py heredoc write evaluated `\n` inside the payload and corrupted two join lines; repaired in place before the suite ran
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto — complete evidence, no security finding, no residue))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] record own-suite status at EXECUTE time into record artifacts, so the trust report reads it instead of re-running archived workspaces — report-time execution is env-fragile by design and the ⚠ assumption stays live (evidence: §1 lowest-confidence flag + own_suite_status's unverified path existing at all)
- [SPEC · open] per-cell human-adjudication provenance for weakened verdicts — 4 rep0 cells render mechanically `weakened` (adjusted > 0) that the hand-diff adjudicated as spec-driven evolution; today the caveat line carries that context globally, a per-cell `adjudicated: evolution (by, date)` annotation would let the trusted flag honor it without weakening the mechanical default (evidence: WV1 render — add-main wm2/wm3, vanilla wm2; WV2 render — vanilla hv2)
- [SPEC · open] wm1 has no survivor bookings so the disjoint-2028-windows pin binds only wm2 — when wm4-6 survivors are authored (standing delta), the pin's fn-level day-uniqueness must extend to them in the same change (evidence: test_wm_survivors_use_disjoint_2028_windows vacuous-for-wm1 disclosure in the §6 refute-read)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a build expectation that predicts the DATA's shape (not the code's behavior) can be wrong while the code is right — record the deviation and prove the unexercised branch live instead of editing the expectation (evidence: honest-outcome tie line absent on both real archives, proven on a tie fixture at the gate)
- [ADD · open] a stricter mechanical metric layered over a prior human judgment must carry the judgment as context, not overwrite it — raw + adjusted + caveat rendered together kept both truths visible (evidence: 4 weakened cells vs the hand-diff, §6 refute-read item 5)

