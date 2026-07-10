# TASK: Two-axis scoring report — trust vector + cost-per-trusted-feature (no agent spend)

slug: v2-scoring-report · created: 2026-07-10 · stage: mvp
milestone: add-bench-v2
autonomy: auto   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: build   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

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
<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

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

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

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
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/` `tmp/`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>
Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain — an algorithm, a data model, a migration path, a prose structure, a UX flow — in the named Persona's domain vocabulary; derive from §1 Framings weighed, not invented here>
Data strategy: <the shapes and access patterns the work realizes — data structures, schema use, information architecture for prose/docs — must agree with the §3 Schema line>
Pattern: <the domain pattern this build follows and the §0 Honors / CONVENTIONS.md anchor it extends>
Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, readability — or "correctness-first, no budget"; never blank; ⚠-mark the facet you trust least; risk: high -> consult add-advisor; facets draft at tests->build; advisory, never a gate>

Persona (required): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; name "generic" if no project persona fits yet>
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
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
- [ ] `python3 -m benchmark.report --trust --runs-root <both rep0 archives>` renders trust tables + two-axis headline for wm AND hv families — confirmed by running it on the real archives at the gate
- [ ] full suite green (v1 report pins untouched); survivors window move keeps all survivors/byte-guard pins green — pytest summary
- [ ] rep0 render shows add wm2 untrusted with the vector explaining why (pass 0.8) and the honest-outcome cost-only line — read the output
- [ ] record.json hashes unchanged after rendering — the read-only test

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
