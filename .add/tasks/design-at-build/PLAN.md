# PLAN: A node that publishes invariants cannot gate without its DESIGN.md

slug: design-at-build · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a node that PUBLISHES invariants cannot record a completing gate without a non-empty DESIGN.md beside its PLAN.md.
Framings weighed: tie the obligation to PUBLISHING and enforce it at the gate (chosen — PLAN.md deliberately persists the interface and not essays, which is right for most tasks and wrong for exactly one kind: a node that binds its neighbours. If you tell a dependent "you must not break this", you owe them the reasoning that produced it, and the gate is the last moment that reasoning still exists) · require a DESIGN.md from every task (rejected — that is precisely the ceremony this method spent whole milestones removing, and a document nobody needed is a document nobody reads) · require it at DIRECTION rather than build (rejected — the design that survives is the one the implementation actually took; demanding it before the build produces a document describing a plan nobody followed)
Must:
<must>
  - a task whose §3 publishes at least one invariant is refused a completing gate (PASS or RISK-ACCEPTED) unless `DESIGN.md` exists beside its PLAN.md, and the refusal names the path to create
  - once a non-empty DESIGN.md exists, the gate proceeds exactly as before
  - a DESIGN.md that is empty or whitespace-only does NOT satisfy the floor — a touched file is not reasoning
  - a task that publishes NOTHING gates exactly as it does today, and nothing creates a DESIGN.md for it
</must>
<reject>
  - a publisher recording a completing gate with no DESIGN.md -> "design_missing"
  - a publisher whose DESIGN.md is empty or whitespace-only -> "design_empty"
</reject>
After:
<after>
  - an inherited invariant can be traced to the reasoning that produced it, by the node that owns it
  - the obligation is proportional: it lands only on nodes that bind other nodes
  - `invariant-inherit`'s view points at a node that can actually answer "why"
</after>
Boundary: the input is the task directory `.add/tasks/<slug>/` — `PLAN.md` §3 for the published-invariant test, and the sibling `DESIGN.md` whose CONTENT is checked only for being non-whitespace. No format is imposed on the design itself; a schema here would be the ceremony this task exists to avoid.
<assumptions>
  ⚠ non-empty is a strong enough bar — if wrong (someone writes "TODO" to clear the gate): the floor has already done its real work by making the omission visible at a human seam, and any deeper check (headings, length, links) would be a shape requirement on prose, which this method has repeatedly found to produce filled-in templates rather than thought; cost = accept the weaker bar, or add a reviewer prompt at the gate report.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract

```
.add/tasks/<slug>/DESIGN.md        (NEW, conditional artifact)

cmd_gate, inside the `completing` branch, AFTER _tamper_guard
  publishes := _published_invariants(§3 of PLAN.md) is non-empty
  publishes and DESIGN.md absent            -> _die design_missing  (names the path)
  publishes and DESIGN.md .strip() == ""    -> _die design_empty
  otherwise                                  -> unchanged

  applies to BOTH completing outcomes: PASS and RISK-ACCEPTED
  (a waiver must not launder a missing design; security stays HARD-STOP)
```
Ground: `add-method/tooling/add.py::cmd_gate` — `completing = args.outcome in ("PASS", "RISK-ACCEPTED")` is the existing gate-verdict predicate, and `_tamper_guard(root, state, slug)` is the first mechanical cheat block inside that branch, with the comment "a tamper finding is never launderable through RISK-ACCEPTED" — the new floor sits immediately after it and inherits the same both-outcomes posture. `_published_invariants(raw3)` is the PURE reader from `invariants-publish`; `_phase_spans(text).get(3, "")` reads §3. The task directory `root / "tasks" / slug` already holds PLAN.md and is where `strip-scaffold-at-done` tidies, so a sibling file is the natural home. The `waiver_incomplete` refusal is the precedent for a gate-time refusal that fires before `save_state`. PLAN.md's own header states the design intent this task deliberately narrows: "persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays".

Target (measurable): the new suite is RED before and GREEN after; a publisher is refused PASS *and* RISK-ACCEPTED without a design; a whitespace-only design still refuses; a non-publisher gates with byte-identical behaviour to today and gets no DESIGN.md created; `add-method/tooling/` (2900 green) stays green with every existing gate test passing UNCHANGED.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.add/tooling/` `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Regression floor: `add-method/tooling/` — the whole method suite; every existing gate test (`test_advance_fold_build_gate.py`, `test_advisor_gate_relax.py`, `test_min_pillar.py`) must pass UNCHANGED, and `test_ci_tooling_mirror_gap.py`'s nested fresh-checkout run must stay green.
Persona (optional): `.add/personas/tdd-verifier.md`.

Least-sure flag surfaced at freeze: [spec] the non-empty bar. This floor is satisfiable by writing the word "TODO", and I am shipping it anyway because the alternative — imposing a shape on the prose — is the move this method has repeatedly found to produce filled-in templates instead of thought. The honest position is that this floor makes an omission VISIBLE at a human seam rather than guaranteeing the reasoning is good; if audits later show DESIGN.md files that say nothing, the fix is a reviewer prompt in the gate report, not a stricter parser.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_publisher_cannot_pass_without_a_design: a publishing node is refused PASS · covers: M1, R:design_missing  [GATED]
  - test_the_refusal_names_the_path_to_create: the message names DESIGN.md · covers: M1  [GATED]
  - test_publisher_passes_once_the_design_exists: a non-empty design lets the gate through · covers: M2  [GATED]
  - test_an_empty_design_does_not_satisfy_it: whitespace-only is refused · covers: M3, R:design_empty  [GATED]
  - test_a_task_publishing_nothing_gates_as_before: a non-publisher is untouched · covers: M4  [GATED]
  - test_risk_accepted_is_refused_too: the waiver route cannot launder it · covers: M1  [edge]
  - test_a_non_publisher_needs_no_design_file_on_disk: nothing is auto-created · covers: M4  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated.

Build-guidance (prose, not gated): the check must fire AFTER `_tamper_guard`, so a cheat is still reported before a missing document. Read DESIGN.md fail-soft — an unreadable file is treated as empty, never a traceback at a gate.

Tests live in: `add-method/tooling/test_design_at_build.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned. The floor sits immediately after `_tamper_guard` inside the `completing` branch, so it inherits that block's both-outcomes posture for free — a cheat still outranks a missing document, and RISK-ACCEPTED cannot launder either. Both reads (PLAN.md §3 and DESIGN.md) are fail-soft: an unreadable file is treated as publishing-nothing / empty rather than raising a traceback at a gate. §4 declares `Tests live in:` as the FILE rather than the directory, applying the lesson the previous task paid a re-cross for.
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
By: self · adversarially checked: (1) `test_a_task_publishing_nothing_gates_as_before` is the positive control that stops the floor passing by refusing every gate — without it, a check that always fired would satisfy all four negative tests; (2) `test_a_non_publisher_needs_no_design_file_on_disk` proves nothing auto-creates the artifact to satisfy itself, which is how this kind of floor usually goes vacuous; (3) `test_an_empty_design_does_not_satisfy_it` closes the touch-a-file bypass, and `test_risk_accepted_is_refused_too` closes the waiver bypass — the two ways a completing gate normally gets around a new refusal; (4) the fixture drives a REAL task through freeze --cross to verify rather than hand-editing a phase marker, so the refusal is observed at the actual seam. NOT claimed: that a DESIGN.md containing "TODO" is refused — §1's assumption and the §3 flag both state that the bar is non-empty and why a prose-shape check would be worse.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose tie the obligation to PUBLISHING and enforce it at the gate; rejected require a DESIGN.md from every task (rejected — that is precisely the ceremony this method spent whole milestones removing, and a document nobody needed is a document nobody reads) · require it at DIRECTION rather than build (rejected — the design that survives is the one the implementation actually took; demanding it before the build produces a document describing a plan nobody followed)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. The floor sits immediately after `_tamper_guard` inside the `completing` branch, so it inherits that block's both-outcomes posture for free — a cheat still outranks a missing document, and RISK-ACCEPTED cannot launder either. Both reads (PLAN.md §3 and DESIGN.md) are fail-soft: an unreadable file is treated as publishing-nothing / empty rather than raising a traceback at a gate. §4 declares `Tests live in:` as the FILE rather than the directory, applying the lesson the previous task paid a re-cross for.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
