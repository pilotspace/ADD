# TASK: dedicated verify persona flow value

slug: verify-flow-value · created: 2026-07-07 · stage: mvp
milestone: delta-drain
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add_engine/constants.py:PERSONA_FLOW_VALUES (trio: add-method/tooling · .add/tooling · _bundled/tooling; PKG pin moves) · templates/personas/_template.md.tmpl flow hint (4 template trees) · docs/18-personas.md "Apply — three surfaces" (root + add-method/docs + _bundled/docs git-tracked, .add/docs consistency copy) · skill/add/phases/6-verify.md persona bullet (3 trees; phases pool headroom 9 B -> in-file compensation) · agents/add-verify.md flow-selection line (3 agent trees) · .add/personas/tdd-verifier.md flow flip · engine_pin.py:ENGINE_PKG_MD5 (add.py itself untouched)
Context (working folder): .add/personas/ roster (6 real personas; tdd-verifier is the verify archetype currently routed under advisor)
Honors (patterns / conventions): personas are advisory, never a gate · flow is RECOMMENDED frontmatter, absent = conformant · constants.PERSONA_* is the single source of truth (schema and validator never drift) · book parity = 3 git-tracked trees (.add/docs never required)
Anchors the contract cites: PERSONA_FLOW_VALUES · _persona_quality_warnings · "Apply — four surfaces"
Ground SHA: a1cfd6a

---

## 1 · SPECIFY — the rules

Feature: weigh a dedicated `verify` flow value vs folding verify under advisor — the §1 ⚠ flag, revisit after the roster runs with flow: routing (from persona-flow-routing spec-delta)
Must:
  - PERSONA_FLOW_VALUES = ("design", "build", "advisor", "verify") in every add_engine twin — `flow: verify` earns NO persona_quality warning
  - the persona template's flow hint names verify (the evidence-judging surface: the earned-green refute-read + gate-record lens) and counts FOUR apply-surfaces; 4 template trees lockstep
  - docs/18-personas.md: section retitled "Apply — four surfaces" + a verify bullet; 3 git-tracked twins lockstep
  - agents/add-verify.md selects a `flow: verify` persona FIRST, falls back to advisor (the old route), then archetype -> generic; 3 agent trees lockstep
  - phases/6-verify.md persona bullet names `flow: verify`; phases pool fence (33284) held by in-file compression
  - .add/personas/tdd-verifier.md declares `flow: verify, advisor` (the writer+reader land in the SAME task — no dead wiring)
Reject:
  - a flow value outside the 4-value set -> existing "flow value '<v>' not one of design|build|advisor|verify" persona_quality warning (WARN-only, never a gate)
Accept: Given tdd-verifier declares `flow: verify, advisor`, When `add.py check` runs, Then no persona_quality flow warning renders for it.
Assumptions: ⚠ verify belongs BESIDE advisor in tdd-verifier (both surfaces still load it), not replacing it — if wrong: one frontmatter-line edit, cheap

---

## 3 · CONTRACT — freeze the shape

```
PERSONA_FLOW_VALUES = ("design", "build", "advisor", "verify")     # order + spelling frozen
verify := the evidence-judging surface — the earned-green refute-read and the gate-record lens
           (6-verify / add-verify); added BESIDE advisor, which keeps its delegation meaning
routing (add-verify): flow: verify first -> flow: advisor fallback -> archetype -> generic
docs surface count: "Apply — four surfaces" (design · advisor/streams · build · verify)
unknown flow value -> persona_quality WARN naming the 4-value set (unchanged mechanism)
```

`Least-sure flag surfaced at freeze:` [spec] whether design.md/advisor.md prose must ALSO enumerate verify — scoped to the surfaces that LOAD it; if wrong: a prose ripple in a later task, cheap
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: test_verify_flow_value.py — 4-value constant across twins · `flow: verify` warning-free (Accept) · unknown value still warns naming verify · template hint + four-surfaces docs + add-verify routing + 6-verify bullet · tree lockstep md5s · phases pool fence held · ENGINE_MD5 unchanged / PKG re-pinned honestly.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/` `add-method/skill/` `.claude/skills/` `add-method/agents/` `.claude/agents/` `add-method/docs/` `.add/docs/` `.add/personas/` `add-method/../18-personas.md`
Strategy & known-problem fixes: (1) red suite first (2) constants tuple + twins (3) prose surfaces smallest-first, compressing 6-verify.md in-file for the 9 B pool headroom (4) tdd-verifier flip last (reader exists by then) (5) re-pin ENGINE_PKG_MD5 only — add.py untouched, ENGINE_MD5 must NOT move
Approach (domain strategy): single-source-of-truth constant extension · additive vocabulary (no meaning change to advisor) · lockstep-twin discipline · token-cost-first on pooled guides (9 B headroom)
Strategy actually used: as planned + 2 sibling pins migrated forward (test_persona_schema_hardening flow-values pin, test_persona_flow_routing KNOWN_FLOWS) and a pre-existing drifted dogfood template twin (add-method/.add) healed by mirroring canon
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [ ] all tests pass · coverage held · no test or contract altered during build
- [ ] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [ ] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `flow: verify, advisor` on tdd-verifier renders zero persona_quality flow warnings in `add.py check`; all enumerating surfaces render the 4-value set — confirmed by test_verify_flow_value (11 green) + migrated sibling suites

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07

