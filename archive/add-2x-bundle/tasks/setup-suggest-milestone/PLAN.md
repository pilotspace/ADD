# TASK: Setup: propose first milestone (goal+flow+scenarios)

slug: setup-suggest-milestone · created: 2026-06-15 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/skill/add/phases/0-setup.md` (≈59 "2. Size the first milestone" in §3 Draft to the lock) — today setup silently DRAFTS the first MILESTONE.md; this task makes setup first PROPOSE it as a concrete suggestion (goal + flow + scenarios) the human reacts to. 3 byte-identical trees.
- `add-method/skill/add/scope.md` — the milestone-drafting rubric the proposal draws on (diverge seeds: Outcome · First slice; the goal-sentence rule). The proposal is scope.md's brainstorm, surfaced at setup.
- prior art: `add-method/tooling/test_cospecify_lift.py` (content-test pattern); `report-template.md` (show-before-ask — propose, then the human reacts).
Context (working folder): brownfield path = `adopt.md` scan output; greenfield path = the 4-lens interview (0-setup.md §2b). Both feed the proposal. The "flow" = the breadth-first task order; "scenarios" = concrete Given/When/Then of what the user could do once the milestone ships.
Honors (patterns / conventions): show-before-ask (propose the milestone, human reacts — never auto-create); no engine change (guide only); 3-tree byte-identical sync; content tested by substrings.
Anchors the contract cites: the §3 "Size the first milestone" step gaining a PROPOSE-first instruction · the three proposal parts (goal · flow · scenarios) · the show-before-ask / human-reacts framing · the scope.md citation.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: after the brownfield scan / greenfield interview, setup PROPOSES the first milestone as a
concrete kickoff suggestion — goal + flow + scenarios — that the human reacts to, before any
MILESTONE.md is drafted.
Framings weighed: propose goal+flow+scenarios, human reacts, then draft (chosen) · silently draft the
MILESTONE.md and ask for sign-off (rejected — the human can't shape a draft they didn't see forming;
show-before-ask) · ask the human to write the first milestone unaided (rejected — the AI just read the
codebase; it should suggest).
Must:
<must>
  - phases/0-setup.md §3 "Size the first milestone" instructs setup to PROPOSE the first milestone as a
    suggestion BEFORE drafting MILESTONE.md — sourced from the scan/interview, presented in chat.
  - the proposal contains three parts: a one-sentence GOAL (outcome), a FLOW (the breadth-first task
    order that gets there), and SCENARIOS (concrete examples of what the user can do once it ships).
  - it is show-before-ask: the human REACTS to the proposal (confirm / adjust / redirect); setup does
    not auto-create the milestone from the suggestion.
  - it cites scope.md (the milestone-drafting rubric the proposal draws on) so the proposal is well-formed.
  - all 3 skill trees stay byte-identical.
</must>
Reject:
<reject>
  - (prose task) a freeze whose §3 lacks the propose-first instruction OR any of goal/flow/scenarios OR
    the human-reacts framing -> content tests stay red; never ship a half-section.
</reject>
After:
<after>
  - a reader of 0-setup.md knows setup proposes the first milestone (goal+flow+scenarios) and waits for
    the human to react before drafting it.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] "flow + scenarios" in the proposal risks DUPLICATING the per-task §2 scenarios / the
    MILESTONE.md task list — lowest confidence because the line between a kickoff SUGGESTION and the
    formal artifacts is fuzzy; if wrong: redundant work — mitigated by scoping the proposal as a
    lightweight REACT-TO sketch (a few bullets), explicitly NOT the frozen MILESTONE.md or §2 suites.
  - [ ] [contract] the proposal lives in §3 of 0-setup.md (not a new guide file) — assumes it's a
    refinement of the existing "size the first milestone" step; if wrong: it gets its own short guide.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: setup proposes the first milestone after the scan/interview
  Given phases/0-setup.md §3 "Size the first milestone"
  When I read it
  Then it instructs setup to PROPOSE the first milestone before drafting MILESTONE.md

Scenario: the proposal carries goal, flow, and scenarios
  Given the propose-first instruction
  When I read what the proposal must contain
  Then it names a goal, a flow, and scenarios

Scenario: the proposal is show-before-ask
  Given the propose-first instruction
  When I read how the human engages it
  Then the human REACTS to the proposal (confirm/adjust) and setup does not auto-create it

Scenario: the proposal draws on scope.md
  Given the propose-first instruction
  When I read it
  Then it cites scope.md (the milestone-drafting rubric)

Scenario: the three skill trees stay byte-identical
  Given canonical, dogfood, and bundled skill trees
  When the edit lands
  Then 0-setup.md is byte-identical across all three
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC CONTRACT — phases/0-setup.md §3 "Size the first milestone" MUST instruct setup to:
  ├─ PROPOSE the first milestone as a kickoff SUGGESTION before drafting MILESTONE.md
  ├─ include three parts: GOAL (one-sentence outcome) · FLOW (breadth-first task order)
  │   · SCENARIOS (concrete examples of what the user can do once it ships)
  ├─ be show-before-ask: the human REACTS (confirm/adjust); setup does NOT auto-create it
  └─ draw on `scope.md` (the milestone-drafting rubric)
Required substrings (render-blind): "propose" (or "suggest") · "first milestone" · "flow" ·
  "scenario" · "scope.md"
Parity: 0-setup.md byte-identical across canonical · dogfood · bundle. No engine change.
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15)
Least-sure flag surfaced at freeze: [spec] the proposal's "flow + scenarios" risks duplicating the per-task §2 scenarios / the MILESTONE.md task list; scoped as a lightweight react-to sketch (a few bullets), explicitly NOT the frozen artifacts — if it still reads as redundant in practice, a §7 delta tightens the wording.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every required substring + 3-tree parity (content-test pattern).
Plan (one test per scenario; read CANONICAL guide; scope the assertions to the §3 region):
<test_plan>
  - test_proposes_first_milestone: §3 instructs PROPOSE the first milestone before drafting MILESTONE.md
  - test_proposal_has_goal_flow_scenarios: the instruction names goal + flow + scenario(s)
  - test_show_before_ask: the human REACTS / setup does not auto-create
  - test_cites_scope_md: the instruction cites scope.md
  - test_three_trees_byte_identical: 0-setup.md identical across canonical/dogfood/bundle
</test_plan>

Tests live in: `add-method/tooling/test_setup_suggest_milestone.py` · MUST run red (missing instruction) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md`
Strategy (ordered batches): 1. extend §3 "Size the first milestone" in canonical 0-setup.md with the propose-first instruction (goal+flow+scenarios, show-before-ask, scope.md citation). 2. cp canonical→dogfood + prepare_bundle. 3. green content suite + parity + wording lint.
Safety rule (feature-specific): prose only; keep the proposal a lightweight react-to sketch (do NOT instruct duplicating the frozen MILESTONE.md or per-task §2 scenarios — the §1 lowest-confidence flag).
Code lives in: the 3 skill trees.
Constraints: do NOT change any test or the contract; keep 0-setup.md byte-identical across all 3 trees; no "dial"/banned slang; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1069 green; test_setup_suggest_milestone 5/5; parity green.
- [x] coverage did not decrease — 5 new content tests; no test removed.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged; the test region anchor (kickoff) was satisfied by rewording the PROSE, not the test (the genuine-red discipline held).
- [x] the green was EARNED — the test was deliberately scoped to a unique "kickoff" marker + a 900-char region so pre-existing "propose"/"flow" from the Run-mode section could NOT satisfy it (it was red until the real instruction landed). SEMANTIC read below.
- [x] concurrency / timing — N/A (documentation).
- [x] no secrets / injection / unexpected deps — prose only.
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree parity held; wording lint green; the new step sits inside §3 and reuses scope.md, no new guide file.
- [x] a person reviewed and approved — Tin Dang (autonomous authorization); auto-gate, no residue.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose) — read the rewritten §3 step 2 in full: it floats a kickoff suggestion (goal + flow + scenarios) for the first milestone, is show-before-ask (human reacts, no auto-create), keeps it a lightweight sketch (explicitly NOT the frozen MILESTONE.md / §2 suites — closing the §1 duplication flag), then draws on scope.md to draft. Consistent with the surrounding setup flow.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (autonomous authorization) · date: 2026-06-15
Evidence: full suite 1069 green; 5 content tests (genuine-red via the kickoff anchor); 3-tree parity held.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether the kickoff proposal reads as redundant with MILESTONE.md/§2 in real setups (the §1 flag) — tighten the wording if so.
Spec delta for the next loop: setup-domain-deepdive extends the same §2b interview; the proposal could later cite a worked example template.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a whole-file substring test is too weak when sibling sections share vocabulary — anchor the region on a UNIQUE new marker so the suite is genuinely red (evidence: "propose"/"flow" pre-existed from setup-run-mode; scoping to the "kickoff" marker made the test honest)
- [UDD · folded] setup should SUGGEST from what it just read, not interrogate — the AI proposes the first milestone (goal+flow+scenarios) and the human reacts; show-before-ask applies at the foundation altitude too (evidence: setup-suggest-milestone)
