# PLAN: An enumerated edge case must be covered or reasoned before the gate

slug: edge-rigor · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an edge case ENUMERATED in §4 must resolve to a real test in the declared suite, or carry a stated reason, before a completing gate.
Framings weighed: check `[edge]`-tagged rows against the §4-declared test files at the gate, with an explicit `[edge — waived: <reason>]` escape (chosen — §4's Rigor rule already distinguishes GATED rows from prose build-guidance, so the tag exists; the hole is that ENUMERATING a case buys credit for work that may never have been done, and the gate is the only seam that sees both the plan and the suite) · require an actual green run of each edge test at the gate (rejected — the engine would have to run and attribute individual tests, and `--run-red` already showed how much new responsibility shelling out carries; the §6 evidence floor already owns green-ness) · leave it to review (rejected — an enumerated-but-unwritten row reads as coverage to every later reader, and nothing ever disagrees with it)
Must:
<must>
  - at a completing gate (PASS or RISK-ACCEPTED), every §4 row tagged `[edge]` must name a test function present in the §4-declared test files
  - the refusal names WHICH enumerated edge case is unaccounted for
  - an edge row whose test exists gates exactly as before
  - an edge row may be waived with `[edge — waived: <reason>]`, and a blank reason is refused: the escape hatch costs a sentence
  - a §4 with no `[edge]` rows is untouched, `[GATED]` rows are not subject to this floor, and an unreadable declared suite never crashes the gate
</must>
<reject>
  - an `[edge]` row whose named test is absent from the declared suite and which states no reason -> "edge_unaccounted"
  - an `[edge — waived: ]` row with an empty reason -> "edge_waiver_unreasoned"
</reject>
After:
<after>
  - enumerating an edge case commits you to covering it or to saying why not, on the record
  - a reader of §4 can trust that an `[edge]` row means something happened
  - the happy-path bias the milestone set out to fix is closed at the one seam the engine can see
</after>
Boundary: input is §4's `<test_plan>` rows and the files named by §4's `Tests live in:` line; a row is an edge row only if it carries the literal `[edge]` or `[edge — waived: …]` tag. A missing or unreadable declared file contributes no test names and never raises.
<assumptions>
  ⚠ presence of the test FUNCTION NAME in a declared file is a sound proxy for "covered" — if wrong (someone writes `def test_empty_list(): pass` to clear the floor): this guard was never the green-ness check, the §6 evidence floor and the earned-green refute-read are, and a stub that passes is the cheat class those two exist for; cost = nothing here changes, because this floor's job is to close the enumerate-and-forget hole, which it still does.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract

```
§4 test_plan row grammar (already in use across this milestone):
  - <test_name>: <description> · covers: <M#|R:code>  [GATED]
  - <test_name>: <description> · covers: <M#|R:code>  [edge]
  - <test_name>: <description> · covers: <M#|R:code>  [edge — waived: <reason>]

add.py :: _edge_rows(raw4: str) -> list[tuple[str, str | None]]
  PURE. -> [(test_name, waiver_reason | None)] for [edge]-tagged rows ONLY
  a row with no [edge] tag is not returned at all

cmd_gate, in the `completing` branch, AFTER the design-at-build floor
  names := every `def <name>` found across _declared_test_files(root, slug)
  for (test_name, waiver) in _edge_rows(§4):
      waiver is not None and waiver.strip() == ""  -> _die edge_waiver_unreasoned
      waiver is not None                            -> accounted (a stated reason)
      test_name not in names                        -> _die edge_unaccounted (names the row)
  applies to BOTH completing outcomes; no [edge] rows -> no behaviour change
```
Ground: `add-method/tooling/add.py::cmd_gate` — the `completing` branch, immediately after the `design_missing`/`design_empty` floor shipped by `design-at-build`, which is itself after `_tamper_guard`; that ordering keeps a cheat outranking a bookkeeping gap. `_declared_test_files(root, slug)` (add_engine/taskdoc.py:51) already resolves §4's `Tests live in:` tokens to real paths and is what `_declared_tests_count` builds on; `_count_test_defs` is the existing `def test_*` counter, so the name set comes from machinery this engine already trusts. `_phase_spans(text).get(4, "")` reads §4. §4's own Rigor paragraph is the rule this enforces: "one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below … no `covers:` tag, no red test, not gated." Every task in THIS milestone already tags its rows `[GATED]`/`[edge]`, so the grammar is in use before it is enforced.

Target (measurable): the new suite is RED before and GREEN after; an enumerated-but-absent edge row refuses PASS *and* RISK-ACCEPTED naming the row; a present one gates; a waived one gates and a blank waiver refuses; a §4 with no `[edge]` rows and a §4 whose absent row is `[GATED]` both gate unchanged; deleting the declared suite produces a refusal or a pass but never a traceback; `add-method/tooling/` (2908 green) stays green with every existing gate test passing UNCHANGED.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/tooling/` `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Regression floor: `add-method/tooling/` — the whole method suite; every existing gate test must pass UNCHANGED, and `test_ci_tooling_mirror_gap.py`'s nested fresh-checkout run must stay green.
Persona (optional): `.add/personas/tdd-verifier.md`.

Least-sure flag surfaced at freeze: [test] that this floor bites the RIGHT author. It fires at the gate, which is the end of the run — so the person who pays is whoever is closing the task, and the enumerate-and-forget happened back at direction. That is unavoidable at this seam (the tests do not exist at freeze time, which is the whole point of a red suite), but it means the refusal will sometimes land as a late surprise. I am accepting that because the alternative — checking at freeze — would demand the tests exist before they are written, inverting the method. If it proves annoying in practice, the fix is to surface unaccounted edge rows as a WARNING at `status`/`check` during build, long before the gate.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_an_uncovered_edge_row_refuses_the_gate: an enumerated-but-unwritten edge case refuses · covers: M1, R:edge_unaccounted  [GATED]
  - test_the_refusal_names_the_offending_row: the message names the test · covers: M2  [GATED]
  - test_a_covered_edge_row_gates: a present edge test lets the gate through · covers: M3  [GATED]
  - test_a_waived_edge_row_gates: a stated reason accounts for the row · covers: M4  [GATED]
  - test_an_empty_waiver_reason_is_refused: a blank waiver refuses · covers: M4, R:edge_waiver_unreasoned  [GATED]
  - test_a_plan_with_no_edge_rows_gates_as_before: grandfathered · covers: M5  [GATED]
  - test_risk_accepted_is_refused_too: the waiver route cannot launder it · covers: M1  [edge]
  - test_a_gated_row_is_not_subject_to_the_edge_floor: [GATED] rows belong to the §6 evidence floor · covers: M5  [edge]
  - test_an_unreadable_declared_suite_does_not_crash_the_gate: fail-soft · covers: M5  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. NOTE: this task's own three `[edge]` rows are all written, so it is subject to — and cleared by — the floor it ships.

Build-guidance (prose, not gated): keep `_edge_rows` PURE so it can be unit-tested without a project on disk. Match the tag case-sensitively and accept both an em-dash and a plain hyphen in the waiver form, since the template and hand-typed rows will differ.

Tests live in: `add-method/tooling/test_edge_rigor.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus one refactor the plan did not call for. The first draft re-read PLAN.md a second time for §4 (with a walrus and a stray `or True` guarding it) — both floors now share ONE read whose spans are indexed by section, which is what the design-at-build floor should have done in the first place. `_edge_rows` accepts an em-dash or a plain hyphen in the waiver form because the template and hand-typed rows differ.
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
Verdict: EARNED
By: self · adversarially checked: (1) THIS task gated through its own floor — its three `[edge]` rows are all written and resolved against its declared suite, so the guard is dogfooded against itself at the moment it ships, the same discipline the signal-graph milestone used; (2) `test_a_plan_with_no_edge_rows_gates_as_before` and `test_a_gated_row_is_not_subject_to_the_edge_floor` are the two positive controls — without them a guard that refused every row, or one that also policed `[GATED]` rows, would satisfy every negative test; (3) `test_an_empty_waiver_reason_is_refused` closes the blank-escape-hatch bypass and `test_risk_accepted_is_refused_too` closes the waiver-outcome bypass; (4) `test_an_unreadable_declared_suite_does_not_crash_the_gate` asserts on stderr for a traceback, so fail-soft is observed rather than assumed. NOT claimed: that the enumerated test PASSES, or is more than a stub — §1's assumption states plainly that presence is the mechanical proxy, that green-ness belongs to the §6 evidence floor, and that a passing stub is the cheat class the earned-green refute-read exists for. This guard closes enumerate-and-forget, nothing wider.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose check `[edge]`-tagged rows against the §4-declared test files at the gate, with an explicit `[edge — waived: <reason>]` escape; rejected require an actual green run of each edge test at the gate (rejected — the engine would have to run and attribute individual tests, and `--run-red` already showed how much new responsibility shelling out carries; the §6 evidence floor already owns green-ness) · leave it to review (rejected — an enumerated-but-unwritten row reads as coverage to every later reader, and nothing ever disagrees with it)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus one refactor the plan did not call for. The first draft re-read PLAN.md a second time for §4 (with a walrus and a stray `or True` guarding it) — both floors now share ONE read whose spans are indexed by section, which is what the design-at-build floor should have done in the first place. `_edge_rows` accepts an em-dash or a plain hyphen in the waiver form because the template and hand-typed rows differ.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
