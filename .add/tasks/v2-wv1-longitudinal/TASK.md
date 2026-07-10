# TASK: WV1 longitudinal evolution — same-workspace WM1→WM2→WM3 workload + 3-arm campaign (spend gated)

slug: v2-wv1-longitudinal · created: 2026-07-10 · stage: mvp
milestone: add-bench-v2
autonomy: auto   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: build   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `benchmark/runner/core.py:_seed_from_prior` (longitudinal carry-forward ALREADY EXISTS — wm>1 fresh workspace seeded from the prior WM's completed workspace, .venv excluded, populated never overwritten) · `benchmark/pilot.py:_REP_METRICS` (`(tokens, cost, fidelity)` triple — the v2 trust metrics are NOT aggregated) · `benchmark/pilot.py:aggregate_reps` (pure, `r.metrics[metric]` would KeyError on an OPTIONAL v2 key) · `benchmark/pilot.py:run_reps` (n-rep campaign driver; per-rep runs_root/rep{i}, resume disabled) · `benchmark/arms/{add,spec-kit,vanilla}.toml` (fairness floor identical: same_model, 200k token / 60 turn ceilings; add = path-pin to this repo's add-method; spec-kit = v0.12.5; vanilla = no setup) · `benchmark/workload/wm{1,2,3}/PROMPT.md` (the longitudinal triple EXISTS and is a byte-frozen anchor — test_wm123_untouched) · `benchmark/results/2026-07-sonnet-campaign.md` (ledger format to extend)
Context (working folder): task1 (v2-meter-fixes `02d5cfd`) made per-WM snapshots + v2 regression + oracle_pass_rate automatic in run_pilot/score_record — this task is the CAMPAIGN + the aggregation gap, not new plumbing
Honors (patterns / conventions): pinned meter is law (milestone shared decision) · n≥3 for headline claims · spend human-gated per campaign · honest-outcome clause · BenchError fail-loud · pure aggregate (no IO)
Seams consulted: none apply (benchmark tree)
Anchors the contract cites: `aggregate_reps` · `_REP_METRICS` · `run_reps` · `_seed_from_prior` (behavioral dependency, untouched) · `benchmark/results/` ledger
Issues/Risks (→ feed §1): (1) aggregate_reps crashes (KeyError) on records missing an OPTIONAL v2 key — mixed v1/v2 record sets are the NORM (archived reps). (2) The wm1→wm2→wm3 carry-forward means a rep is one ARM-SEQUENCE: a wm1 timeout halts that arm's rep (existing halt semantics) — the campaign budget must expect partial reps. (3) WM2/WM3 runs carry a grown workspace → likely costlier than the wm1-only v1 campaigns; the $60–90 estimate assumes ~$2–4/ADD-run. (4) The report layer (report.py) is OUT of scope here — v2-scoring-report owns the two-axis print; this task's ledger table is hand-written from records. (5) wm1-3 PROMPT.md are byte-frozen — no workload edits.
Related intent: MILESTONE add-bench-v2 exit criterion 3 (WV1 campaign, n≥3, regression_rate per WM per arm) · DESIGN.md WV1 hypothesis: ADD's frozen contracts + accumulated suites keep regression ≈0 while per-WM cost amortizes
Ground SHA: `02d5cfd`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: WV1 longitudinal campaign — v2-metric rep aggregation + the 3-arm × wm1-3 × n=3 pinned-meter campaign + results ledger
Framings weighed: aggregate-extension + hand-run campaign (chosen — the plumbing shipped in task1; smallest diff, campaign is execution not code) · new WV1-specific runner module (rejected: run_reps already does per-rep roots + halt semantics) · defer aggregation to v2-scoring-report (rejected: an unreadable campaign result can't be sanity-checked at the spend it costs)
Must:
<must>
  - M1 `aggregate_reps` additionally aggregates the v2 metrics — regression_rate, oracle_pass_rate, tests_weakened — with OPTIONAL-key tolerance: a record missing a key is EXCLUDED from that metric's distribution and counted in `n_missing_<label>`; mixed v1/v2 record sets never crash
  - M2 `_REP_METRICS` grows the three v2 entries; the existing (tokens, cost, fidelity) triple is untouched so archived-campaign aggregation is byte-identical for v1 keys
  - M3 the WV1 campaign runs `run-all --arms add add-main spec-kit vanilla --wms 1,2,3 --reps 3` on the PINNED meter (claude-sonnet-5 / effort medium, pin `4d0c52e`) — ONLY after an explicit human spend go (milestone shared decision); partial reps (arm-halt on a failed WM) are recorded as-is, never re-rolled silently   <!-- @v2 change request 2026-07-10 (human directive): + add-main control arm -->
  - M5 (@v2) a new `add-main` CONTROL arm — ADD installed from the MAIN branch via a pinned git worktree — same fairness floor (same_model · 200k tokens · 60 turns), pin = the main SHA; controls this branch's engine changes against the released flow
  - M4 results land as a ledger section in `benchmark/results/` — per-arm × per-WM table: cost · turns · oracle_pass_rate · regression_rate · tests_weakened, with the honest-outcome clause applied (any floor spec-kit/vanilla holds is stated) and every partial/failed rep disclosed
</must>
Reject:
<reject>
  - aggregate_reps sees a metric present in ZERO records of a group -> that metric reported as {"n_missing": n, no distribution} — never a fabricated 0.0 mean
  - a campaign run on an unpinned/other-model meter -> VOID, excluded from the ledger (milestone shared decision — enforced editorially, disclosed in the ledger)
  - a rep re-rolled because its result "looked wrong" -> forbidden; every launched rep is reported (partial included)
</reject>
After:
<after>
  - The campaign's records carry per-WM oracle_pass_rate + regression_rate + tests_weakened for all three arms, n=3 (minus disclosed halts), aggregated readably by aggregate_reps
  - benchmark/results/ holds the WV1 ledger answering DESIGN.md's WV1 hypothesis with real numbers — whichever way they fall
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the $60–90 spend estimate holds for wm2/wm3 runs on grown workspaces — lowest confidence because v1 only ever priced wm1 (~$3-4.5/ADD-run); if wrong: the campaign overshoots budget mid-flight. Mitigation: launch rep0 across all arms first, extrapolate 3× before continuing (the go/continue split is part of the M3 spend gate).
  - [x] the carry-forward seed gives WV1 its same-codebase evolution — confirmed: _seed_from_prior copies the prior WM's completed workspace (task1 ground + this §0)
  - [x] wm1-3 prompts form the intended longitudinal triple — confirmed: CRUD → auth/business rules touching wm1 handlers → refactor+conflict rules (test_wm123_untouched pins them)
</assumptions>

<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: v2 metrics aggregate across reps   # M1+M2
  Given 3 records for (add, wm2) each carrying oracle_pass_rate 0.8/1.0/0.9 and regression_rate 0.0/0.1/0.0
  When aggregate_reps runs
  Then the (add, 2) entry holds pass-rate {mean 0.9, min 0.8, max 1.0} and regression {mean ~0.033}
  And the tokens/cost/fidelity output is byte-identical to today's for the same records

Scenario: mixed v1/v2 records never crash   # M1, R1
  Given 2 v2 records and 1 archived v1 record (no optional keys) in one group
  When aggregate_reps runs
  Then the v2 metrics aggregate over the 2 carriers with n_missing = 1
  And a group with ZERO carriers reports n_missing only — no fabricated 0.0 mean

Scenario: campaign spend is human-gated and staged   # M3
  Given the harness is ready and the human said go
  When the WV1 campaign launches
  Then rep0 runs first across all arms; the 3× extrapolation is shown before reps 1-2 continue
  And every launched rep lands in the ledger — partial arm-halts disclosed, none re-rolled

Scenario: add-main is a valid control arm   # M5 (@v2)
  Given benchmark/arms/add-main.toml pointing at a main-branch worktree, pin = the main SHA
  When load_arm validates all ARM_NAMES recipes
  Then add-main loads with the identical fairness floor as every other arm
  And the existing arms' tomls are byte-unchanged

Scenario: the ledger answers the hypothesis honestly   # M4, R2, R3
  Given all reps complete (or halt)
  When the WV1 section is written to benchmark/results/
  Then it tables cost/turns/oracle_pass_rate/regression_rate/tests_weakened per arm per WM
  And any trust floor spec-kit or vanilla ALSO holds is stated in the findings
  And no unpinned-meter number appears
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
benchmark/pilot.py:
  _REP_METRICS += (("pass_rate","oracle_pass_rate"), ("regression","regression_rate"),
                   ("weakened","tests_weakened"))                     # M2, v1 triple untouched
  aggregate_reps(records) -> dict                                     # M1, stays PURE / no IO
    per (arm, wm) group, per metric: distribution {mean,min,max} over the records
    CARRYING the key; records missing it excluded + surfaced as "n_missing": <int>
    inside that metric's entry (0 carriers -> entry is {"n_missing": n} ONLY)   # R1

campaign (M3 — execution, not code):
  python3 -m benchmark.pilot run-all --arms add add-main spec-kit vanilla --wms 1 2 3 --reps 3
    --runs-root <fresh dir> --repo-root <this repo> --timeout-s 1800
  meter: pinned claude-sonnet-5 / effort medium (pin 4d0c52e); launch AFTER human go;
  staged: rep0 all arms -> show 3x cost extrapolation -> human continue for reps 1-2
  halts recorded as-is; no silent re-rolls                            # R3

add-main control arm (M5 @v2 — human directive 2026-07-10):
  benchmark/arms/add-main.toml: setup_steps install add-method from a MAIN-branch
  git worktree (absolute campaign-local path), prompt_wrapper = "add-loop",
  pin = "<main SHA> (git worktree of main)"; fairness floor identical to all arms.
  loader.ARM_NAMES += "add-main"  (first-party arm: pin key present, not PIN_REQUIRED)

ledger (M4): a "WV1 longitudinal" section in benchmark/results/ (same file or sibling of
  2026-07-sonnet-campaign.md): per-arm x per-WM table of cost · turns · oracle_pass_rate ·
  regression_rate · tests_weakened + findings applying the honest-outcome clause

Schema: no record-schema change (task1's v2 keys reused); aggregate output dict gains the
        3 labels + n_missing; ledger is prose/markdown.
```

Glossary deltas: `n_missing: per-metric count of records in a rep group not carrying an optional v2 key — disclosure, never imputation`
Least-sure flag surfaced at freeze: [spec] the spend estimate (now 4 arms, ~$80–120) is extrapolated from wm1-only pricing — wm2/wm3 grown-workspace runs may cost materially more; mitigated by the staged rep0 → extrapolate → human-continue gate inside M3. (@v2 note: the add-main worktree pins main at ONE SHA — a moving main is never re-measured silently.)
Status: FROZEN @ v2 — approved by Tin Dang
<!-- @v2 change request 2026-07-10 — human directive: + add-main control arm; v1 was approved by Tin Dang -->
Reported: yes — @v1 freeze report + the @v2 change rendered in-chat before re-freeze
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the aggregate_reps change (the only code in this task)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_aggregate_v2_metrics: arrange 3 synthetic v2 records (add, wm2) / act aggregate_reps / assert pass_rate {mean 0.9, min 0.8, max 1.0} + regression mean ≈0.0333 · covers: M1, M2
  - test_aggregate_v1_output_unchanged: arrange v1-only records / act / assert the tokens/cost/fidelity sub-dicts equal today's output exactly · covers: M2
  - test_aggregate_mixed_records_n_missing: arrange 2 v2 + 1 v1 record in one group / act / assert v2 metric aggregates over 2 with n_missing 1; a zero-carrier group yields {"n_missing": 3} only, no mean key · covers: M1, R1
  - (@v2) test_arms.py amended: all ARM_NAMES recipes validate incl. add-main, fairness parity across the FULL set, add-main pin non-empty · covers: M5
</test_plan>

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build. (M3/M4 are campaign execution + prose — verified at the gate by the records + ledger themselves, not unit tests.)
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `benchmark/`
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
- [ ] `python3 -m pytest benchmark/tests/test_wv1_aggregate.py` 3/3 green + full benchmark suite green — confirmed by pytest summary lines
- [ ] rep0 campaign (3 arms × wm1-3, pinned meter) produces 9 record.json with oracle_pass_rate + regression_rate (+ tests_weakened where snapshots pair) — confirmed by reading the records
- [ ] the rep0 → 3× cost extrapolation is shown to the human BEFORE reps 1-2 launch — confirmed by the conversation record
- [ ] WV1 ledger section exists in benchmark/results/ with the per-arm × per-WM table + honest-outcome findings — confirmed by reading it

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
- [SPEC · open] tests_weakened has a TESTLESS-ARM LOOPHOLE: an arm writing zero tests can never weaken one (clean 0) while ADD carries the largest false-positive surface — the `trusted` flag must ALSO require the arm's OWN suite to exist and be green; add snapshot-derived own_tests_count/own_asserts_count (tamper.py snapshots already hold the data, zero re-runs) (evidence: human fairness challenge 2026-07-10; owned by v2-scoring-report)
- [SPEC · open] the trust axis prints as a VECTOR (pass rate · regression · weakened · own-test evidence · traceability when WV6 lands), never collapsed to one float; human-attention cost stays a disclosed unmeasurable with WV6 traceability as proxy (evidence: same challenge; owned by v2-scoring-report)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
