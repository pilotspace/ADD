# PLAN: amb1 checklist + oracle: score ONLY behavior the prompt states unambiguously

slug: amb1-checklist-oracle · created: 2026-07-26 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: amb1's `checklist.py` + `oracle/` suite, scoring ONLY behavior the prompt states unambiguously — so `--family amb` can write a record at all, without the meter secretly grading the planted ambiguities.
Framings weighed: SCORE-THE-CLEAN-SUBSET (chosen — a probe that touches a planted ambiguity declares one reading correct and silently converts the ambiguity track into a right-answer track, destroying the thing it measures) · score everything and "adjust" for the ambiguous rows (rejected — an adjustment is a second, unvalidated meter layered on the first, and it hides the bias instead of removing it).
Must:
<must>
  - M1 `workload/amb1/checklist.py` exposes a valid `REQUIREMENTS` list, so `compute_requirement_coverage` stops raising missing_checklist.
  - M2 `workload/amb1/oracle/` is a collectible pytest suite, so `compute_oracle_pass_rate` stops raising unknown_workload_family.
  - M3 NO checklist row and NO oracle test depends on the resolution of any planted ambiguity — proven mechanically against AMBIGUITIES, not by inspection.
  - M4 both meters are non-vacuous: an empty workspace scores 0.0, and a reference app implementing the clean subset scores 1.0.
  - M5 an arm is scored IDENTICALLY whichever reading it shipped — proven by scoring two reference apps that differ ONLY in their resolution of the three ambiguities.
  - M6 score_record on an amb1 run produces a complete, schema-valid metrics dict.
</must>
Reject:
<reject>
  - a checklist row whose probe requires an entry to reach a waitlist -> "contaminated_probe" (unreachable under the reject reading)
  - a probe asserting promotion ORDER or position semantics -> "contaminated_probe"
  - a meter that scores an empty workspace above 0.0 -> "vacuous_meter"
</reject>
After:
<after>
  - `--family amb` runs end-to-end and writes a schema-valid record with every REQUIRED metric plus ambiguity_surface_rate.
  - the live two-arm run becomes worth paying for: every number it produces is real.
</after>
Boundary: two reference apps — one resolving all three ambiguities one way, one the other — are the fixture; the meters must not be able to tell them apart.
<assumptions>
  ⚠ that the clean subset is genuinely clean — that no row I believe is unambiguous is in fact reachable only under one reading. If wrong, the coverage meter quietly penalises one arm and the whole track's fairness claim fails. Cost: the benchmark flatters whichever arm happens to share my reading, which is the exact failure the track exists to avoid.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/workload/amb1/checklist.py
  REQUIREMENTS = [ {id, description, probe(base, ws)}, ... ]
  the CLEAN subset only:
    R-post-create · R-get-list · R-get-one · R-unknown-404
    R-missing-field-400 · R-status-default-pending
    R-delete-cancels (booking >24h out)
    R-cancel-window-422 (booking inside the 24h window)
    R-auth-identifies-caller · R-priority-accepted
    R-entry-contract
  EXCLUDED, and why (contamination map, recorded in the module docstring):
    anything needing an entry ON a waitlist  -> A-conflict-response makes it
      unreachable under the `reject` reading
    promotion ORDER                          -> A-priority-vs-fifo
    position semantics                       -> A-position-ordering
    GET /rooms/{id}/waitlist on an empty room -> borderline; an arm reading §2
      as authoritative may build no waitlist feature at all

benchmark/workload/amb1/oracle/{__init__,conftest,test_amb1_clean}.py
  the same clean subset as a collectible pytest suite, red against an empty
  workspace (oracle_pass_rate's own red-for-the-right-reason rule)
```

Target (measurable): score_record on a synthetic amb1 run writes a schema-valid record with all REQUIRED metrics plus ambiguity_surface_rate; empty workspace -> requirement_coverage 0.0 and oracle_pass_rate 0.0; reference app -> 1.0 and 1.0; the two reference apps that differ ONLY in ambiguity resolution score IDENTICALLY on both meters; benchmark suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/workload/amb1/` `benchmark/tests/`
Regression floor: the full `benchmark/tests` suite — green before the gate.
Persona (optional): `.add/personas/tdd-verifier.md` — the risk is a meter that looks fair and is not.

Least-sure flag surfaced at freeze: [spec] the ⚠ above — that my clean subset is genuinely clean. This is a judgement about the PROMPT, and judgements about prompts are exactly what this track exists to distrust. Mitigation is mechanical rather than argumentative: M5 scores two reference apps that differ ONLY in how they resolve the three ambiguities and requires the meters to be blind to the difference. If a row I believed clean is in fact reading-dependent, those two apps score differently and the test fails. That converts my judgement into something a machine can refute.
### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_amb1_checklist_loads_and_validates: _load_checklist(1,"amb") returns validated rows · covers: M1
  - test_amb1_oracle_suite_collects: the oracle dir exists and pytest collects it · covers: M2
  - test_no_probe_mentions_a_planted_anchor: mechanical scan of checklist+oracle source against AMBIGUITIES anchors · covers: M3, R:contaminated_probe
  - test_no_probe_touches_waitlist_or_promotion_endpoints: no probe calls /waitlist or asserts promotion/position · covers: M3, R:contaminated_probe
  - test_empty_workspace_scores_zero_coverage: covers: M4, R:vacuous_meter
  - test_empty_workspace_scores_zero_oracle: covers: M4, R:vacuous_meter
  - test_reference_app_scores_full_coverage: the clean subset is actually satisfiable · covers: M4
  - test_reference_app_passes_the_oracle: covers: M4
  - test_both_ambiguity_resolutions_score_identical_coverage: THE FAIRNESS PROOF · covers: M5
  - test_both_ambiguity_resolutions_score_identical_oracle: covers: M5
  - test_score_record_amb_writes_a_complete_metrics_dict: covers: M6
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: <fill at VERIFY — what you ACTUALLY did (or "as planned"); harvested into §7 Decisions (ADR)>
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose SCORE-THE-CLEAN-SUBSET; rejected score everything and "adjust" for the ambiguous rows (rejected — an adjustment is a second, unvalidated meter layered on the first, and it hides the bias instead of removing it).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
