# TASK: Wire the guided-decision cue into every human-gate guide

slug: gate-wiring · created: 2026-06-16 · stage: mvp
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

Touches (files · symbols · signatures): the 8 human-gate guides, each of which ALREADY carries a `report-template.md` ARC cue line I extend with the guided-decision cue (3 skill homes each, byte-identical):
- `phases/0-setup.md:121` (baseline-lock) · `phases/3-contract.md:23` (freeze) · `phases/6-verify.md:69` (verify gate)
- `intake.md:36` (intake) · `scope.md:40` (scope) · `loop.md:42` (milestone-close) · `graduate.md:41` (graduation) · `release.md:48` (release)
- the frozen convention vocabulary lives in `report-template.md` ("The DECISION block as a guided choice" — tokens T1–T6, FROZEN by suggestion-block); this task only POINTS guides at it, adds no new rule.
- new red guard `.add/tasks/gate-wiring/tests/test_gate_wiring.py` — asserts each of the 8 guides names the guided-decision cue + 3-home parity (mirrors test_xml_convention's per-guide dict).

Context (working folder):
- `add-method/tooling/wording_lint.py` + `test_xml_convention.py` + `test_bundle_parity.py` — same guards as suggestion-block: no banned phrase, closed tag vocab (these guides carry {prompt, output_format, exit_gate} — I add NO tag), 3-home byte-identical.
- the arc-gate-wiring precedent (v23): the SAME 8 guides were each given a one-line ARC cue; this task mirrors that wiring shape exactly.

Honors (patterns / conventions):
- PROJECT.md §Domain — presentation/layout iterates WITHOUT a re-freeze; additive one-line cue per guide.
- CONVENTIONS — "prose-feature red-greenable by token presence"; "single-source-point-not-restate" (the guides POINT at report-template.md's convention, never restate the rules); "no double-cue" (one slot per guide, beside the existing ARC cue).
- MILESTONE.md EC2 listed 9 gates incl. "human-gated-advance" — RECONCILE in §1: phase-advance is engine-mechanical with no own guide; the real human-gate guides are these 8 (advance folds into the freeze + verify gates, both covered).

Anchors the contract cites:
- the 8 guide files + their existing `report-template.md` ARC cue lines (the insertion points)
- `report-template.md` "guided choice" section (the frozen target the cue points to)
- `test_gate_wiring.py` per-guide cue token (the checkable seam)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Wire the guided-decision cue into every human-gate guide — each of the 8 gate guides points at report-template.md's guided-choice convention beside its existing ARC cue.
Framings weighed: extend the existing ARC-cue line (chosen) · a separate new paragraph per guide · a single SKILL.md note
  — chose extend-the-ARC-cue-line: the guided-choice convention is a sibling of the ARC (both presentation rules for the same report), so one combined cue per guide keeps it lean (no double-cue) and mirrors the v23 arc-gate-wiring shape exactly.
Must:
<must>
  - M1 — each of the 8 human-gate guides (0-setup · 3-contract · 6-verify · intake · scope · loop · graduate · release) carries a one-line cue to render the DECISION as a "guided choice" (a recommended pick + described alternatives), pointing at `report-template.md`.
  - M2 — the cue POINTS, never RESTATES: it references `report-template.md`'s guided choice; it does not re-list the convention's rules (single-source-point-not-restate).
  - M3 — one cue per guide, beside the existing ARC cue — no double-cue, no new paragraph block.
  - M4 — additive prose only: NO new XML tag (the guides carry {prompt, output_format, exit_gate}); no guide's prompt/exit_gate structure changed; the 3 homes of each guide stay byte-identical.
  - M5 — RECONCILE the gate count: MILESTONE.md EC2's 9th "human-gated-advance" is not a distinct guide (advance is engine-mechanical, no own guide); the covered set is these 8 guides (advance's human moments ARE the freeze + verify gates, both wired). Correct EC2 to the 8-guide list.
</must>
Reject:
<reject>
  - a human-gate guide missing the guided-choice cue -> "guide_uncued"   # the RED state the §4 guard asserts before build
  - the 3 homes of any wired guide not byte-identical -> "home_drift"
  - report-template.md's frozen convention edited by this task (it should POINT, not change the convention) -> "convention_touched"
</reject>
After:
<after>
  - all 8 guides reference the guided-choice convention beside their ARC cue; `report-template.md` is UNCHANGED (the convention is frozen by suggestion-block); MILESTONE.md EC2 reconciled to the 8-guide set.
  - the §4 red guard (`test_gate_wiring.py`) asserts the cue in all 8 guides + 3-home parity — green only after build; engine byte-identical; wording-lint + xml-convention + bundle-parity green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the 8-guide set is the COMPLETE set of human decision points — lowest confidence because a human gate could live somewhere without a `report-template.md` ARC ref (e.g. a SKILL.md note); if wrong: a gate renders a bare choice and the gap the milestone closes stays open at that gate. Mitigation: I grepped every guide for `report-template` refs; the 8 with an ARC cue == the gate set v23 wired (same set).
  - [x] extend-the-ARC-cue-line is the right shape (vs a separate paragraph) — confirmed; mirrors arc-gate-wiring, keeps it lean.
  - [x] "human-gated-advance" correctly folds into the freeze + verify gates — confirmed; advance is engine-mechanical with no own guide.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# Observability: each guide is prose; "Then" is a grep over the file text (token presence).

Scenario: Every human-gate guide carries the cue (M1)
  Given the 8 gate guides after build
  When the §4 guard scans each
  Then each of 0-setup · 3-contract · 6-verify · intake · scope · loop · graduate · release names a "guided choice" cue pointing at report-template.md

Scenario: The cue points, never restates (M2)
  Given a wired guide
  When the guard reads its cue line
  Then it references report-template.md AND does not re-list the convention's rules (a single pointer line)

Scenario: One cue per guide, no double-cue (M3)
  Given a wired guide
  When the guard counts guided-choice cues in it
  Then there is exactly one, sitting beside the existing ARC cue

Scenario: Additive — no new tag, parity holds (M4)
  Given the wired guides
  When xml-convention + the parity guard run
  Then no guide gained a tag outside {prompt, output_format, exit_gate} AND each guide's 3 homes are byte-identical

Scenario: Gate count reconciled (M5)
  Given MILESTONE.md after build
  When the guard reads EC2
  Then EC2 names the 8 guides and no longer claims a separate "human-gated-advance" guide

Scenario: REJECT guide_uncued — a guide missing the cue (Reject 1)
  Given report-template.md wired but one gate guide left uncued
  When the §4 guard runs
  Then it FAILS naming the uncued guide
  And the other guides are unaffected

Scenario: REJECT home_drift — a guide's homes diverge (Reject 2)
  Given the cue added to only one home of a guide
  When the parity guard runs
  Then it FAILS (canonical · _bundled · .claude not byte-identical)

Scenario: REJECT convention_touched — this task edits the frozen convention (Reject 3)
  Given an edit that changes report-template.md's guided-choice section
  When the guard compares report-template.md to its frozen state
  Then it FAILS (this task POINTS at the convention, never changes it)
  And the convention's tokens remain exactly as suggestion-block froze them
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONVENTION  gate-guide wiring (a prose/presentation seam — no engine, no HTTP)

  THE 8 HUMAN-GATE GUIDES (the frozen coverage set; each in 3 byte-identical homes):
    phases/0-setup.md (baseline-lock) · phases/3-contract.md (freeze) · phases/6-verify.md (verify)
    intake.md · scope.md · loop.md (milestone-close) · graduate.md · release.md

  REQUIRED PER GUIDE (the checkable seam §4 asserts):
    C1 the literal cue token "guided choice" present, on/beside the existing report-template.md ARC line
    C2 the cue references `report-template.md` (it POINTS — single source, not a restatement)

  INVARIANTS (held, not added):
    I1 report-template.md is UNCHANGED by this task (the convention is frozen by suggestion-block)
    I2 no XML tag outside { prompt, output_format, exit_gate } in any guide; no guide's structure changed
    I3 each guide's 3 homes byte-identical; engine add.py byte-identical
    I4 MILESTONE.md EC2 reconciled to the 8-guide set (no "human-gated-advance" guide)

  REJECT (named; §4 asserts each):
    guide_uncued        -> a gate guide missing the "guided choice" cue (the RED pre-build state)
    home_drift          -> a wired guide's 3 homes not byte-identical
    convention_touched  -> report-template.md's frozen guided-choice section changed by this task
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16 (bundle approval; autonomy: auto — freeze is the one gate)
Least-sure flag surfaced at freeze: [spec] is 8 the COMPLETE set of human-gate guides? — a gate could live without a `report-template.md` ARC ref (e.g. a SKILL.md note); if wrong: one gate still renders a bare choice and the milestone's gap stays open there. Mitigation: grepped every guide for `report-template` refs — the 8 with an ARC cue == the exact set v23 arc-gate-wiring covered. Human approved the 8-guide set at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every guide (8) + each invariant + each reject condition asserted; prose lint (no line %).
Plan (reads the canonical home of each guide + 3-home parity):
<test_plan>
  - test_each_guide_cued (M1/C1+C2): for each of the 8 guides, assert "guided choice" present AND "report-template" present
  - test_no_new_tag (M4/I2): for each guide, assert its XML tag set ⊆ {prompt, output_format, exit_gate}
  - test_each_guide_homes_identical (Reject home_drift/I3): for each guide, assert md5(canonical)==md5(_bundled)==md5(.claude)
  - test_convention_untouched (Reject convention_touched/I1): assert report-template.md still contains the frozen guided-choice tokens ("▶", "recommended pick", "guided choice") — unchanged by this task
  - test_milestone_ec2_reconciled (M5/I4): assert MILESTONE.md EC2 names the 8 guides and not "human-gated-advance"
  # Reject guide_uncued is the RED meta-property: test_each_guide_cued FAILS for the 8 uncued guides before build.
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/` `.add/milestones/decision-suggestions/MILESTONE.md` `./tests/`
Strategy (ordered batches): 1. write the red guard in `./tests/`. 2. edit the 8 gate guides in the CANONICAL skill tree — one "guided choice" cue per guide, beside its existing ARC line. 3. mirror byte-identical to `_bundled` + `.claude`. 4. reconcile MILESTONE.md EC2 to the 8-guide set. 5. run the guard + wording-lint + xml-convention + bundle-parity green.
Safety rule (feature-specific): `report-template.md` stays UNTOUCHED (the frozen convention); each guide's 3 homes end byte-identical; no new XML tag.
Code lives in: the 8 gate guides across the 3 skill homes (prose — no `src/`).
Constraints: do NOT change report-template.md's convention, any test, or the contract; engine `add.py` byte-identical; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — gate-wiring guard 5/5; full engine suite 1158/1158 OK
- [x] coverage did not decrease — prose task; all 8 guides + invariants + reject conditions asserted
- [x] no test or contract was altered during build — report-template.md (the frozen convention) UNTOUCHED; only the 8 guides + MILESTONE.md EC2 changed
- [x] the green was EARNED, not gamed — the cue is a real one-line guided-choice pointer added to each guide's existing ARC sentence (read below), not a token dropped to satisfy the grep; report-template.md unchanged proves the convention wasn't restated
- [x] concurrency / timing — N/A: prose
- [x] no exposed secrets, injection openings, or unexpected dependencies — no code; wording-lint 0 findings
- [x] layering & dependencies follow CONVENTIONS.md — additive prose; engine byte-identical; no new XML tag (xml-convention 17/17); per-guide 3-home parity OK
- [x] auto-resolved (autonomy: auto, no residue, no security) — recorded as an explicit auto-PASS, accountable run: Claude (the orchestrating agent)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read each of the 8 wired guides' ARC sentences in full: each now renders its DECISION as a "guided choice (the recommended pick + described alternatives)" pointing at report-template.md, woven into the existing ARC instruction (one cue, no double-cue, no new paragraph). report-template.md's frozen guided-choice section is byte-unchanged (test_convention_untouched green). MILESTONE.md EC2 reconciled to the 8-guide set. No WIRING/DEAD-CODE path (no code produced).

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto) · accountable run: Claude · date: 2026-06-16   (evidence: gate-wiring guard 5/5 + suite 1158/1158 + wording-lint/xml/parity green + per-guide 3-home parity; NO residue — presentation prose, engine byte-identical, security N/A)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): all 8 guides keep the cue + 3-home parity as the skill evolves; report-template.md stays the single source (cues point, never restate).
Spec delta for the next loop: suggest-book-align (task 3) documents the convention in the book + GLOSSARY headwords `guided decision` · `recommended pick`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a guide-tag lint that greps `</?tag>` false-positives on prose PLACEHOLDERS (`<name>`, `<slug>`) — match CLOSING tags only (`</tag>`), since real block tags are paired but placeholders never close (evidence: test_no_new_tag first failed on `<assumption>`/`<slug>`; fixed to closing-only)
- [SDD · folded] the on-demand guides (intake.md · scope.md · release.md) carry the engine-doc tags `constraints`/`reject_codes`, not just the phase-guide trio — a per-guide tag-vocab check must use the FULL closed-5 vocab, not the phase-guide subset (evidence: test_no_new_tag failed on intake.md's `</reject_codes>` until the set was widened)
- [ADD · folded] a MILESTONE.md exit criterion can over-enumerate the work (a phantom "human-gated-advance" 9th gate) — the wiring task reconciled EC2 to the real 8 guides, the recorded change-as-method move (evidence: M5 reconcile; test_milestone_ec2_reconciled went red→green)
- [ADD · folded] task 2 ran `auto` (method-APPLYING) where task 1 ran conservative (method-DEFINING) — the same milestone discriminates autonomy by which kind of change a task makes, not by milestone theme (evidence: gate-wiring auto-resolved verify; suggestion-block human-gated)
