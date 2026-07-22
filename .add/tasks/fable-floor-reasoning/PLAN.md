# PLAN: fable Floor reasoning pass — claim grammar + Goal/Leftovers + GROUND + constraint-loop

slug: fable-floor-reasoning · created: 2026-07-22 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A "fable Floor" reasoning pass added to the ADD method PROSE — four reasoning disciplines distilled from the fable-thinking protocol, inserted into the advisor Return contract and the direction phase guide, propagated byte-identical across all three synced trees. Prompt-only; no engine change.
Framings weighed: extend-existing-guides (chosen — lands in the on-demand `direction.md` + `add-advisor.md`, ZERO `SKILL.md` byte growth, reuses the already-enforced tree-parity floor) · new-SKILL-section (rejected — SKILL.md is 9803B, already over the 9500B ceiling) · engine-enforced-gate (rejected — this is prompt discipline, not a kernel change; "no engine change" keeps the pin intact)
Must:
<must>
  - M1 — `add-advisor.md` §6 Return requires a claim-grammar tag `[OBSERVED|DERIVED|PRIOR|ASSUMED]` on factual assertions, with the four-term legend defined inline.
  - M2 — `direction.md` carries a pre-freeze **Floor** check naming BOTH Goal (the end-state the human wants, not the ticket's wording) AND Leftovers (every supplied constraint / PROJECT.md invariant / the BARE declared runtime either encoded in §1–§4 or explicitly waived).
  - M3 — `direction.md` GROUND step states observation-over-memory: a recalled fact (file · flag · symbol · prior lesson) is PRIOR until re-confirmed against the live tree THIS session; a live read outranks memory.
  - M4 — `direction.md` carries a constraint-loop micro-pass BEFORE the freeze for mechanically-checkable output-shape rules (frozen §3 tag census · §5 scope tokens · §4 `covers:` keys · REDS/dangling refs): expand the rule → self-verify the draft mechanically → repair → then freeze.
  - M5 — all three `add-advisor.md` copies byte-identical; all three `direction.md` copies byte-identical (the `test_tree_parity` floor stays green).
  - M6 — no engine change: `add.py` / `add_engine/**` / `ENGINE_MD5` pin untouched; `SKILL.md` not touched.
</must>
Reject:
<reject>
  - an edit that grows or touches `SKILL.md` -> "skill_ceiling"
  - a divergent copy across the three trees -> "tree_parity_broken"
  - an edit to `add.py`/`add_engine`/the pin -> "engine_touched"
</reject>
After:
<after>
  - the four disciplines are present and byte-consistent across all three trees; `test_tree_parity` + the new content guard are green; no engine repin needed.
</after>
Boundary: none — no external runtime input; the "inputs" are method markdown files, checked by grepping their text.
<assumptions>
  ⚠ the phrases I pin must not collide with an existing phrase-pin guard — if wrong: a pre-existing test reds. Mitigated: read `test_advisor_review_step.py` (pins PLAN.md.tmpl §6, NOT add-advisor.md prose) + `test_tree_parity.py` (byte-parity only); neither pins the prose I add.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
Scenario: advisor Return carries claim grammar
  Given a reader opens any of the three add-advisor.md copies
  When they read §6 Return
  Then the four-term legend OBSERVED/DERIVED/PRIOR/ASSUMED is defined and required on assertions
  And the three copies remain byte-identical

Scenario: the pre-freeze Floor is present
  Given a reader opens any of the three direction.md copies
  When they reach the freeze review
  Then a Floor check names both Goal (end-state ≠ wording) and Leftovers (unused invariants/BARE runtime)
  And SKILL.md is unchanged
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

Grounding — Anchors (the exact insertion sites, cited by symbol/heading, opened this session):
- `add-advisor.md` → `## 6 · Return` — the `{ mode, persona, … }` schema line (edit A appends the grammar rule + legend).
- `phases/direction.md` → `### Grounding — reason it in-context` — the "via code-navigation tools, not memory" clause (edit C strengthens it).
- `phases/direction.md` → `## The freeze review checklist` — the seven-bullet list (edit B prepends a Floor bullet; edit D adds a constraint-loop bullet).
Ground SHA: 3d1c8800 (the prompting-fidelity pass — this builds directly on it).

### Contract (freeze the shape — content guarantees for a docs/method task; no HTTP surface)

```
DOC-CONTRACT (method prose · acceptance-checked, not an API):
  add-advisor.md §6      -> defines legend OBSERVED|DERIVED|PRIOR|ASSUMED; requires the tag on assertions
  direction.md freeze    -> Floor bullet: Goal (end-state ≠ wording) + Leftovers (invariants/BARE runtime encoded or waived)
  direction.md Grounding -> recalled fact is PRIOR until re-confirmed live this session; live read outranks memory
  direction.md freeze    -> constraint-loop bullet: expand → self-verify mechanically → repair → freeze; targets {tag census, §5 scope tokens, §4 covers keys, REDS refs}
  Invariant: 3× add-advisor.md byte-identical · 3× direction.md byte-identical · SKILL.md & engine untouched
  Reject responses: skill_ceiling (SKILL.md touched) · tree_parity_broken (copies diverge) · engine_touched (add.py/pin changed)
```

Least-sure flag surfaced at freeze: [spec/test] the pinned prose could collide with an existing phrase-pin guard — mitigated by reading test_advisor_review_step.py (pins PLAN.md.tmpl §6, not this prose) + test_tree_parity.py (byte-parity only); residual risk low, caught by running the full guard suite at verify.

Target (measurable): the new content guard `test_fable_floor.py` goes 4/4 green (one check per Must M1–M4); `test_tree_parity.py` stays green (M5); `md5(add.py) == ENGINE_MD5` unchanged (M6); `SKILL.md` md5 unchanged. Confirmed by running both suites at verify.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `.claude/agents/add-advisor.md` `add-method/agents/add-advisor.md` `add-method/src/add_method/_bundled/agents/add-advisor.md` `.claude/skills/add/phases/direction.md` `add-method/skill/add/phases/direction.md` `add-method/src/add_method/_bundled/skill/add/phases/direction.md`
Strategy: edit the CANONICAL of each file first (`add-method/agents/add-advisor.md`, `add-method/skill/add/phases/direction.md`), then propagate byte-identical to the other two copies with `cp` (never hand-retype — divergence reds tree_parity). Two logical edits (A on advisor, B+C+D on direction), 6 files.
Regression floor: `add-method/tooling/test_tree_parity.py` (byte-parity of all trees + `md5(add.py)==ENGINE_MD5`) · `add-method/tooling/test_advisor_review_step.py` (PLAN.md.tmpl §6 pins) — both must stay green.
Persona (required): methodology-engine-dev (the method's own author voice; advisory).

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_claim_grammar_in_advisor_return: all 3 add-advisor.md define the OBSERVED/DERIVED/PRIOR/ASSUMED legend and require the tag in §6 Return · covers: M1
  - test_floor_goal_and_leftovers_prefreeze: all 3 direction.md carry a Floor check naming Goal AND Leftovers/invariant/BARE-runtime · covers: M2
  - test_ground_observation_over_memory: all 3 direction.md state a recalled fact is PRIOR until re-confirmed live this session · covers: M3
  - test_constraint_loop_before_freeze: all 3 direction.md carry the output-shape self-verify pass naming the census/scope/covers/REDS targets · covers: M4
  - (M5 byte-parity + M6 engine-pin are the REGRESSION FLOOR — already owned by test_tree_parity.py; not re-tested here)
</test_plan>

Tests live in: `add-method/tooling/test_fable_floor.py` · acceptance-check kind (docs/method): grep-based pass/fail over the 6 files. MUST run red (phrases absent) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — edited canonical `add-method/agents/add-advisor.md` (edit A) + `add-method/skill/add/phases/direction.md` (edits B/C/D), then `cp` byte-identical to both twins each; 6 files, zero engine/SKILL touch. Added the well-formed `Least-sure flag` line to §3 to clear `unflagged_freeze` before the freeze.
Code lives in: `./src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — test_fable_floor 4/4 · test_tree_parity · test_advisor_review_step green; add.py check 418/0; full tooling suite (regression floor) green
- [x] coverage did not decrease — N/A (prose task); a new content guard was ADDED (test_fable_floor.py, 4 checks)
- [x] no test or contract was altered during build — §3 frozen contract untouched; test_fable_floor was AUTHORED in tests-phase then HARDENED at verify (structural co-location — a tightening, never a weakening)
- [x] the green was EARNED — refute found the whole-file pins could pass vacuously (Goal/invariant pre-exist in direction.md); CLOSED by re-asserting Floor + constraint-loop tokens CO-LOCATED in one bullet before recording
- [x] concurrency / timing — N/A (method markdown, no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — text-only edits
- [x] layering & dependencies follow CONVENTIONS.md — canonical-then-cp propagation matches the enforced tree-parity convention
- [ ] a person reviewed and approved the change — PENDING (sensitivity: architecture → human verify gate; does not auto-PASS)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: each guard token against the PRE-EDIT file (PRIOR-until/REDS/census/the four tags were all absent → red was real). Weakness found + closed: test_floor & test_constraint keyed on Goal/invariant which pre-exist elsewhere in direction.md → hardened to require CO-LOCATION in the actual bullet. Residual: the pins are content-presence, not semantic — a future reword keeping the tokens could drift meaning; the human review + tree-parity backstop it.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-22

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose extend-existing-guides; rejected new-SKILL-section (rejected — SKILL.md is 9803B, already over the 9500B ceiling) · engine-enforced-gate (rejected — this is prompt discipline, not a kernel change; "no engine change" keeps the pin intact)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — edited canonical `add-method/agents/add-advisor.md` (edit A) + `add-method/skill/add/phases/direction.md` (edits B/C/D), then `cp` byte-identical to both twins each; 6 files, zero engine/SKILL touch. Added the well-formed `Least-sure flag` line to §3 to clear `unflagged_freeze` before the freeze.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
