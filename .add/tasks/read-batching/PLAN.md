# PLAN: Direction grounds in batched turns, not a serial read chain

slug: read-batching · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the direction guide instructs GROUND to issue its independent reads and greps in ONE turn, and the benchmark's `add-loop` wrapper carries the same instruction so the measured arm actually exercises it.
Framings weighed: guide prose + wrapper clause + a mechanical parity guard across the three skill trees (chosen — the defect is measured and purely instructional: across 209 direction turns in the pay1–4 campaign ZERO emitted more than one tool call, costing 7.3 of 31 direction minutes to strictly serial Reads; no engine change is needed and none should be spent) · an engine verb that batches reads (rejected — `add.py` cannot see a model's tool calls, so it could only advise, and the milestone's own decision is that the engine never enforces what it cannot observe) · leave the guide alone and change only the benchmark wrapper (rejected — that improves the benchmark number without improving the method, which is the exact dishonesty `arm-honesty` just closed)
Must:
<must>
  - the direction guide's Grounding section instructs that independent reads/greps be issued together in ONE turn, and says why (a serial chain pays a full turn's context per file)
  - the instruction is byte-identical across all THREE skill trees, so a plugin/npm/PyPI install carries what the repo carries
  - the benchmark `add-loop` wrapper carries the same batching instruction, so the arm under measurement exercises the method's own guidance
  - the wrapper tells the agent to skip harness bookkeeping (task-tracker calls, sleep-polling) — turns that buy the benchmark nothing and inflate the phase being measured
</must>
<reject>
  - a skill tree whose direction guide lacks the batching clause the others carry -> "batch_clause_drift"
  - an `add-loop` wrapper with no batching instruction -> "unbatched_arm"
</reject>
After:
<after>
  - a direction phase can issue its grounding sweep in one turn without the operator asking for it
  - the parallel-turn count in a fresh pay1–4 record is greater than zero, where the 2026-07-26 baseline was exactly zero
  - the guidance a user installs is the guidance the benchmark measures
</after>
Boundary: this is instructional surface only — three markdown guides and one Python string constant. No engine verb, no template, no state schema, and therefore no engine-pin repin.
<assumptions>
  ⚠ the model follows a stated batching instruction when the reads are genuinely independent — if wrong: the clause is inert and the parallel-turn count stays zero, which the Gate A re-run measures directly; cost = the measurement, not a rollback, and the finding itself is publishable (instruction alone does not move tool-call shape).
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
skill/add/phases/direction.md :: "### Grounding" section        (3 TREES, byte-identical)
  + a BATCH clause: independent reads/greps go out in ONE turn, with the reason

benchmark/runner/core.py :: BATCH_CLAUSE : str                   (NEW module constant)
benchmark/runner/core.py :: _wrap_prompt(text, "add-loop"|"add-loop-enumerate")
  -> the returned prompt contains BATCH_CLAUSE

guard: add-method/tooling/test_read_batching.py
  the three direction.md trees carry the clause, identically  -> else "batch_clause_drift"
guard: benchmark/tests/test_read_batching_wrapper.py
  _wrap_prompt(t, "add-loop") and (t, "add-loop-enumerate") carry it -> else "unbatched_arm"
  "raw" and "spec-kit" are UNTOUCHED (a clause leaked into a control biases the comparison)
```
Ground: `.claude/skills/add/phases/direction.md` — the `### Grounding` section already says "Sweep BROAD cheaply … then DEEPEN", which is about *breadth*, and says nothing about *turn shape*; its GROUND move (`- **GROUND** — verify by observation, not memory`) is where the discipline is named. The file's opening already mandates "ONE silent draft" for the WRITE side, so the batching idea is established for writes and simply absent for reads. The three trees: `.claude/skills/add/phases/direction.md` · `add-method/skill/add/phases/direction.md` · `add-method/src/add_method/_bundled/skill/add/phases/direction.md` (all 24k, currently identical). `benchmark/runner/core.py::_wrap_prompt` — the `add-loop`/`add-loop-enumerate` branch already concatenates `ENUMERATE_CLAUSE` as an optional string, so a second constant follows an established shape; the `raw` fall-through and the `spec-kit` branch must not receive it. The parity precedent for three-tree guards is `add-method/tooling/test_adr_audit.py::OBSERVE_GUIDE`. Evidence the defect is real: the pay1–4 flamegraph fold (2026-07-26) — 209 direction turns, 0 with more than one tool call, 7.3 min of serial Reads.

Target (measurable): both guards RED before the change (naming the missing clause in 3 trees and 2 wrappers) and GREEN after; the three direction.md files remain byte-identical to each other; `_wrap_prompt(t, "raw") == t` still holds and the `spec-kit` wrapper is unchanged; `benchmark/tests/` stays green (520 -> 520+new) and `add-method/tooling/` stays green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `.claude/skills/add/phases/direction.md` `add-method/skill/add/phases/direction.md` `add-method/src/add_method/_bundled/skill/add/phases/direction.md` `add-method/tooling/` `benchmark/runner/core.py` `benchmark/tests/`
Regression floor: `benchmark/tests/` — 520 green · `add-method/tooling/` — the method suite, in particular `test_ci_tooling_mirror_gap.py` (its skip count is pinned) and any SKILL.md byte-ledger guard.
Persona (optional): `.add/personas/tdd-verifier.md` — the two guards are the deliverable; the prose edit merely satisfies them.

Least-sure flag surfaced at freeze: [contract] whether a prose clause changes tool-call shape at all. This task can only prove the clause is PRESENT and consistent; whether it is OBEYED is the Gate A measurement, one re-run away. I am deliberately shipping a change whose value is unproven, because it is free, reversible, and the milestone's sequencing decision requires it to be measured before `direction-one-shot` lands — but if Gate A shows the parallel-turn count still zero, the honest read is that instruction alone does not move behavior and `direction-one-shot` (an engine call that removes the turns rather than asking for fewer) carries the whole milestone.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_every_skill_tree_direction_guide_carries_the_batch_clause: enumerate the 3 trees; each Grounding section contains the clause · covers: M1, M2, R:batch_clause_drift  [GATED]
  - test_the_three_direction_guides_are_byte_identical: parity, so an install cannot ship a stale variant · covers: M2, R:batch_clause_drift  [GATED]
  - test_batch_clause_states_the_reason: the clause names WHY (a serial chain pays a turn's context per file), not just the instruction · covers: M1  [GATED]
  - test_add_loop_wrapper_carries_the_batch_clause: both add-loop and add-loop-enumerate · covers: M3, R:unbatched_arm  [GATED]
  - test_wrapper_tells_the_agent_to_skip_harness_bookkeeping: the wrapper names task-tracker/sleep-poll turns as out of scope · covers: M4  [GATED]
  - test_raw_wrapper_is_untouched: _wrap_prompt(t, "raw") == t — a clause leaked into the control biases every comparison · covers: M3  [edge]
  - test_spec_kit_wrapper_does_not_receive_it: the SDD arm keeps its own instructions only · covers: M3  [edge]
  - test_guard_enumerates_trees_from_disk: the tree list is derived from the repo layout, not a literal that rots when a fourth tree lands · covers: M2  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Build-guidance (prose, not gated): keep the clause to two sentences — the direction guide is at its useful density and the milestone's own lesson is that adds must be funded by compression, not by growth. Word it as method, not as benchmark tuning.

Tests live in: `add-method/tooling/` `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned. The clause anchors on the existing sentence "DEEPEN on what THIS task needs." so it lands inside `### Grounding` in all three trees from one scripted pass, keeping them byte-identical by construction rather than by three hand-edits — the failure class this task's own parity guard exists to catch. `BATCH_CLAUSE` follows `ENUMERATE_CLAUSE`'s established concatenation shape in the add-loop branch.
Code lives in: `add-method/` `benchmark/`
Spawn (multi-agent): solo — the change is two prose insertions and one string constant; a worktree spawn would cost more than the edit.
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
By: self · adversarially checked: (1) the guard enumerates the trees by globbing the repo layout and `test_enumeration_is_not_vacuous` proves an empty root yields ZERO guides, so the parametrized checks cannot pass by finding nothing — the vacuous-probe class that has bitten this benchmark repeatedly; (2) `test_batch_clause_sits_in_the_grounding_section` partitions on the heading rather than searching the whole file, so a clause pasted anywhere else still fails; (3) `test_batch_clause_is_substantive` rejects a one-word constant that would satisfy every containment check vacuously; (4) the negative controls are real — `_wrap_prompt(t, "raw") == t` and the spec-kit branch is asserted clause-free, so the treatment cannot silently lift the controls; (5) the guards were confirmed RED (9 failures naming all 3 trees) before the change. NOT claimed: that the clause changes behavior — see the §3 least-sure flag; that is Gate A's measurement, not this gate's.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose guide prose + wrapper clause + a mechanical parity guard across the three skill trees; rejected an engine verb that batches reads (rejected — `add.py` cannot see a model's tool calls, so it could only advise, and the milestone's own decision is that the engine never enforces what it cannot observe) · leave the guide alone and change only the benchmark wrapper (rejected — that improves the benchmark number without improving the method, which is the exact dishonesty `arm-honesty` just closed)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. The clause anchors on the existing sentence "DEEPEN on what THIS task needs." so it lands inside `### Grounding` in all three trees from one scripted pass, keeping them byte-identical by construction rather than by three hand-edits — the failure class this task's own parity guard exists to catch. `BATCH_CLAUSE` follows `ENUMERATE_CLAUSE`'s established concatenation shape in the add-loop branch.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
