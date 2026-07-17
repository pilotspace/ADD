# TASK: Decision-suggestion convention: recommended pick + described alternatives in report-template.md

slug: suggestion-block · risk: high · created: 2026-06-16 · stage: mvp
autonomy: conservative   <!-- LOWERED from the project `auto` default: method-defining scope (edits report-template.md, the decision-point trust layer) — the high-risk guard refuses an un-lowered `auto` gate (unguarded_high_risk_auto). The human owns the verify gate. -->
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
- `.claude/skills/add/report-template.md` — the AI's decision-point chat template (the file this task changes). Edit anchors: the **five blocks** list (`SUMMARY · DECISION · ⚠ FLAGS · EVIDENCE · NEXT`, lines ~53–59), block 2 **DECISION** body (lines ~64–66), **"The ask itself"** (lines ~77–79), and the `<constraints>` **Hard rules** block (lines ~83–106). Mirrored byte-identical in `add-method/skill/add/report-template.md` (canonical) + `add-method/src/add_method/_bundled/skill/add/report-template.md` (bundled).
- `.add/tasks/suggestion-block/tests/test_suggestion_block.py` — the new red guard (authored in §4): asserts the convention tokens present in `report-template.md` across the 3 homes + 3-home byte-identical parity. Shape mirrors `add-method/tooling/test_release_guide.py` (3-homes list + token asserts; no count bump — see below).

Context (working folder):
- `add-method/tooling/wording_lint.py` + `WORDING_RUBRIC.md` — fence-based prompt-clarity lint over the skill surface (`report-template.md` is in it). New prose must avoid `enforced_banned` phrases and keep `keep_list` terms present. NOT a count/density gate, so an in-place edit (no new file) needs no surface-count bump.
- `add-method/tooling/test_xml_convention.py` — the v16 closed 5-tag vocab (`prompt · exit_gate · constraints · reject_codes · output_format`). `report-template.md` carries `<constraints>` only; additions must introduce **no new tag** (the convention rides in prose + the existing `<constraints>` block + a fenced example).
- `add-method/tooling/test_bundle_parity.py` (`test_skill_tree_byte_identical`) + the tree-parity guard — keep all 3 homes byte-identical.
- `.claude/skills/add/confidence.md` — the advisory 0–1 six-dimension self-score that INFORMS the recommended pick (shared decision; referenced, not changed).
- engine `_driver_marker` → ` [human gate]` / ` [you drive]` (`.add/tooling/add.py`) — the convention scopes to `[human gate]` points; the marker is REFERENCED, never changed (engine stays byte-identical — convention-only milestone).

Honors (patterns / conventions):
- PROJECT.md §Domain — "a **presentation/layout** layer iterates freely WITHOUT a re-freeze (v9)": this task is presentation-layer; no frozen DATA contract changes.
- PROJECT.md §Users — "Leanness is a UX constraint on a dual-audience prose file (v16)": ≤1-line descriptions, no over-tagging.
- CONVENTIONS — "prose-feature red-greenable by token presence (fv26)"; "docs-guard-cross-checks-source"; "engine UNCHANGED for a convention-guided seam" (the release-guide pattern this task copies).
- `report-template.md`'s own rules — the ARC + 5 blocks, show-before-ask, never pre-stamp, "the question is a summary, never the artifact": the new convention REFINES block 2 only, honoring all of these.

Anchors the contract cites:
- `report-template.md` block 2 **DECISION** (the rule the convention extends)
- `report-template.md` **"The ask itself"** composition (the AskUserQuestion mapping)
- `report-template.md` `<constraints>` **Hard rules** (where the new rule is pinned)
- `test_suggestion_block.py` required-token set (the checkable lint seam — the convention's "data shape")

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The decision-suggestion convention — `report-template.md`'s DECISION block presents a highlighted recommended pick + 1–3 described alternatives at every human gate.
Framings weighed: refine block 2 DECISION (chosen) · add a 6th block "CHOICES" to the five-block list · a separate `decision-suggestions.md` guide file
  — chose refine-block-2: the convention is a refinement of an existing block, not a new one; a 6th block bloats the frozen five-block shape, and a new file splits decision guidance from where it lives + bumps the surface/parity inventory.
Must:
<must>
  - M1 — the DECISION spec states that, when a human must choose, the block leads with ONE highlighted recommended pick marked `▶ … (recommended)` — exactly one, never zero, never two.
  - M2 — the recommended pick is followed by 1–3 REAL, takeable alternatives; if there is genuinely one path, the block shows the single recommended step + its description (the degenerate case), never invented filler.
  - M3 — EVERY option (the pick and each alternative) carries a one-line description: what it means + what it unlocks or costs; ≤1 line; no bare labels.
  - M4 — the convention REFINES block 2 only: the ARC, ⚠ FLAGS, EVIDENCE, NEXT and the five-block list are unchanged; show-before-ask holds (the described choice is the ASK, rendered after EVIDENCE).
  - M5 — the spec names the AskUserQuestion composition: the recommended option is the FIRST option with a `(Recommended)` suffix and each option's `description` carries the one-line description; tool-agnostic — on a non-AskUserQuestion surface the SAME recommended-first + described shape renders as a numbered/▶ menu.
  - M6 — the convention fires at human decision points only (`[human gate]`), never at `[you drive]` autonomous steps.
  - M7 — the recommended pick is informed by the AI's confidence self-score (`confidence.md`); the human overrides freely (a recommendation, never a default that auto-proceeds).
  - M8 — the rule is pinned in the existing `<constraints>` Hard rules block (beside show-before-ask / never-pre-stamp) and introduces NO new XML tag (closed v16 vocab) and NO 6th block.
</must>
Reject:
<reject>
  - a required convention token (recommended-pick rule · per-option description rule · human-gate-only scope · AskUserQuestion composition) absent from report-template.md -> "convention_absent"   # the RED state the §4 guard asserts before build
  - the 3 report-template.md homes (canonical · _bundled · .claude) not byte-identical -> "home_drift"
  - a tag outside {prompt, exit_gate, constraints, reject_codes, output_format} or a 6th five-block entry introduced -> "tag_or_block_added"
</reject>
After:
<after>
  - report-template.md (all 3 homes, byte-identical) encodes M1–M8 in its DECISION spec + `<constraints>` Hard rules, citing confidence.md and the `[human gate]` marker.
  - the §4 red guard (`test_suggestion_block.py`) exists and asserts the convention tokens present in all 3 homes + parity — green only after this build.
  - the engine (`add.py`) is byte-identical (no behavior change); wording-lint + xml-convention + bundle-parity stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The ONE recommended-pick + described-alternatives shape maps cleanly onto BOTH AskUserQuestion (its own `(Recommended)` + per-option `description` UI) AND a plain-text `▶` menu for non-Claude agents — lowest confidence because the two surfaces render differently, so a single prescribed shape could feel forced on one of them; if wrong: the convention reads as Claude-Code-specific and other agents can't follow it cleanly → the tool-agnostic promise weakens. (This is the bundle-wide flag I'll lead the freeze with.)
  - [x] The convention belongs IN report-template.md (refine block 2), not a new file — confirmed; cohesion + no surface/parity bump (built as a block-2 refinement).
  - [x] "Human decision points only" correctly excludes auto-advance — confirmed; the human accepted scoping to `[human gate]` at milestone confirm.
  - [x] ≤1-line descriptions carry enough "what it unlocks/costs" without bloat — confirmed; matches the leanness-v16 constraint (built with ≤1-line descriptions).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# Observability note: report-template.md is prose, so "Then" is a grep/lint over the file's
# text (token presence), per the fv26 "prose-feature red-greenable by token presence" convention.

Scenario: Recommended pick is single + highlighted (M1)
  Given report-template.md after build
  When the §4 guard scans the DECISION spec
  Then it finds the rule that the block leads with ONE pick marked "▶ … (recommended)" — never zero, never two
  And the five-block list (SUMMARY · DECISION · ⚠ FLAGS · EVIDENCE · NEXT) is unchanged

Scenario: 1–3 real alternatives, degenerate single-path allowed (M2)
  Given the DECISION spec
  When the guard reads the alternatives rule
  Then it finds "1–3" real/takeable alternatives AND the single-recommended-step degenerate case (no invented filler)

Scenario: Every option is described in one line (M3)
  Given the DECISION spec
  When the guard reads the per-option rule
  Then it finds that the pick and EACH alternative carry a one-line description (what it means + unlocks/costs), no bare labels

Scenario: Convention refines block 2 only (M4)
  Given report-template.md after build
  When the guard compares the ARC, ⚠ FLAGS, EVIDENCE, NEXT sections to baseline
  Then those sections and the five-block list are byte-unchanged except the DECISION/ask refinement
  And show-before-ask still reads "the described choice is the ASK, after EVIDENCE"

Scenario: AskUserQuestion composition is named + tool-agnostic (M5)
  Given the DECISION/ask spec
  When the guard reads the composition rule
  Then it finds the AskUserQuestion mapping (recommended option FIRST + "(Recommended)" + per-option description)
  And a tool-agnostic fallback (the same shape as a numbered/▶ menu for non-AskUserQuestion agents)

Scenario: Fires at human gates only (M6)
  Given the DECISION spec
  When the guard reads the scope rule
  Then it finds the convention is scoped to "[human gate]" points and explicitly NOT "[you drive]" steps

Scenario: Pick informed by confidence, human overrides (M7)
  Given the DECISION spec
  When the guard reads the recommendation-source rule
  Then it finds the pick is informed by confidence.md AND the human overrides freely (not an auto-proceed default)

Scenario: Pinned in Hard rules, no new tag/block (M8)
  Given report-template.md after build
  When the guard reads the <constraints> Hard rules block
  Then the recommended-pick rule is pinned there
  And no XML tag outside {prompt, exit_gate, constraints, reject_codes, output_format} and no 6th block were introduced

Scenario: REJECT convention_absent — red before build (Reject 1)
  Given report-template.md BEFORE this build (no convention tokens)
  When the §4 guard runs
  Then it FAILS with the convention-absent condition (a required token missing)
  And report-template.md is otherwise unchanged

Scenario: REJECT home_drift — homes diverge (Reject 2)
  Given the convention added to only one of the 3 report-template.md homes
  When the parity guard runs
  Then it FAILS (canonical · _bundled · .claude not byte-identical)
  And no home is silently left behind

Scenario: REJECT tag_or_block_added — vocab/structure regression (Reject 3)
  Given an edit that adds a new XML tag or a 6th five-block entry
  When xml-convention + the structure guard run
  Then they FAIL (out-of-vocab tag / changed block list)
  And the closed 5-tag vocab and five-block shape remain the invariant
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONVENTION  report-template.md "decision-suggestion" (a prose/presentation seam — no engine, no HTTP)
  surface : report-template.md, byte-identical across 3 homes
            [ add-method/skill/add · add-method/src/add_method/_bundled/skill/add · .claude/skills/add ]

  REQUIRED TOKENS (the checkable seam §4 asserts present; the stable vocabulary gate-wiring
  + suggest-book-align depend on — change = change-request back to SPECIFY):
    T1 "recommended pick"      — the one highlighted option; marker glyph "▶" + literal "(recommended)"   (M1)
    T2 "described alternatives"— 1–3 real alternatives; the degenerate single-step case named            (M2)
    T3 one-line "description"  — every option (pick + each alt) carries a ≤1-line what-it-means/costs      (M3)
    T4 "AskUserQuestion"       — recommended option FIRST + "(Recommended)" + per-option `description`;
                                 + a tool-agnostic numbered/▶-menu fallback for non-AskUserQuestion agents (M5)
    T5 "[human gate]"          — scope: human decision points only; explicitly NOT "[you drive]"           (M6)
    T6 "confidence"            — the pick is informed by confidence.md; the human overrides freely         (M7)
  LOCATION: T1–T6 appear in the DECISION/ask spec; the binding rule (T1 single-pick + T5 scope) is
            ALSO pinned in the existing <constraints> Hard rules block.                                    (M8)

  INVARIANTS (held, not added — §4 + the existing guards assert):
    I1 refines block 2 (DECISION/ask) ONLY — the five-block list + ARC/⚠ FLAGS/EVIDENCE/NEXT unchanged    (M4)
    I2 no XML tag outside { prompt, exit_gate, constraints, reject_codes, output_format }; no 6th block    (M8)
    I3 engine add.py byte-identical (3 trees) — convention-only, no behavior change
    I4 wording-lint + xml-convention + bundle/tree-parity stay green

  REJECT (named; §4 asserts each fires):
    convention_absent   -> a required token T1–T6 missing from report-template.md (the RED pre-build state)
    home_drift          -> the 3 homes not byte-identical
    tag_or_block_added  -> I2 violated (out-of-vocab tag or a 6th five-block entry)

  GLOSSARY names (for suggest-book-align; introduced there, reserved here):
    "guided decision" · "recommended pick"
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16 (bundle approval)
Least-sure flag surfaced at freeze: [contract] one shape for two surfaces — the recommended-pick + described-alternatives shape must map cleanly onto BOTH `AskUserQuestion` (its own `(Recommended)` + per-option `description`) AND a plain `▶`/numbered menu for non-Claude agents; because the two render differently, a single prescribed shape could feel forced on one. If wrong: the convention reads Claude-Code-specific and the tool-agnostic promise weakens. Mitigation in scope: contract token T4 requires the menu fallback + the build adds a concrete non-Claude example. Human approved the single-shape model at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every M1–M8 + each of the 3 reject conditions has ≥1 assertion (11 checks); prose lint, so "coverage" = Must/Reject completeness, not line %.
Plan (one test per scenario, asserting behavior not internals — reads the canonical home + the 3-home parity):
<test_plan>
  - test_recommended_pick_single_highlighted (M1): assert "▶" AND "(recommended)" AND the "never zero, never two" rule present in the DECISION spec
  - test_alternatives_one_to_three (M2): assert "1–3" alternatives AND the single-recommended-step degenerate case named
  - test_every_option_described (M3): assert the per-option one-line-description rule (no bare labels) present
  - test_refines_block_two_only (M4): assert the five-block list (SUMMARY·DECISION·⚠ FLAGS·EVIDENCE·NEXT) still present AND the show-before-ask "the described choice is the ASK, after EVIDENCE" line present
  - test_askuserquestion_composition (M5): assert "AskUserQuestion" + recommended-FIRST + "(Recommended)" + per-option "description" + the tool-agnostic numbered/▶-menu fallback
  - test_human_gate_scope (M6): assert "[human gate]" scope present AND "[you drive]" named as the explicit exclusion
  - test_confidence_informs_pick (M7): assert "confidence" cited AND the human-overrides-freely clause present
  - test_pinned_in_hard_rules (M8): assert the recommended-pick rule appears INSIDE the <constraints> Hard rules block
  - test_no_new_tag (Reject tag_or_block_added, part 1): assert the set of XML tags in report-template.md ⊆ {prompt, exit_gate, constraints, reject_codes, output_format}
  - test_five_blocks_unchanged (Reject tag_or_block_added, part 2): assert exactly the 5 named blocks in the list — no 6th
  - test_homes_byte_identical (Reject home_drift): assert md5(canonical) == md5(_bundled) == md5(.claude)
  # Reject convention_absent is the RED meta-property: every token test above FAILS before the build adds the convention.
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/report-template.md` `add-method/src/add_method/_bundled/skill/add/report-template.md` `.claude/skills/add/report-template.md` `./tests/`
Strategy (ordered batches): 1. write the red guard in `./tests/` (assert tokens absent → red). 2. edit the CANONICAL home (`add-method/skill/add/report-template.md`) — refine block 2 DECISION + "The ask itself" + add the Hard rule. 3. copy byte-identical into `_bundled` + `.claude`. 4. run the task guard + wording-lint + xml-convention + bundle-parity green.
Safety rule (feature-specific): the 3 homes MUST end byte-identical (md5-equal); introduce NO XML tag outside the closed vocab and NO 6th block — presentation-layer only, engine untouched.
Code lives in: the 3 `report-template.md` homes (this is a prose convention — no `src/`).
Constraints: do NOT change any test or the contract; no new dependency; engine `add.py` stays byte-identical; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — task guard 7/7; full engine suite 1158/1158 OK
- [x] coverage did not decrease — prose task; M1–M8 + 3 reject conditions all have an assertion (no line-coverage surface)
- [x] no test or contract was altered during build — only the 3 report-template.md homes changed; §3/§4 untouched after freeze
- [x] the green was EARNED, not gamed — manual adversarial refute-read: the tokens sit in coherent, substantive prose (a guided-choice structure + worked example + 4 rules + the ask composition + a Hard rule), NOT token-stuffed; no vacuous/overfit/stub path (it is prose). The human gate is the real backstop (conservative).
- [x] concurrency / timing — N/A: prose convention, no runtime/IO/concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — no code, no dependency; wording-lint 0 findings
- [x] layering & dependencies follow CONVENTIONS.md — presentation-layer only; engine add.py byte-identical (bundle-parity `test_add_py_byte_identical` green); no new XML tag (xml-convention 17/17); 3 homes md5-identical
- [ ] a person reviewed and approved the change — PENDING (this gate; conservative + risk:high → human-owned)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full (canonical report-template.md lines 60–117): confirmed M1 single highlighted `▶ … (recommended)` pick (never zero/two) · M2 1–3 real alternatives + the single-step degenerate case · M3 one-line description per option · M4 the five-block list + ARC/FLAGS/EVIDENCE/NEXT unchanged, show-before-ask preserved ("rendered after EVIDENCE") · M5 AskUserQuestion composition (recommended-first + `(Recommended)` + per-option `description`) + tool-agnostic numbered/▶ menu fallback · M6 `[human gate]`-only, not `[you drive]` · M7 confidence.md informs, human overrides · M8 the rule pinned in `<constraints>`, no new tag/block. The convention reads as one coherent refinement of block 2, not bolt-on tokens.
  (No WIRING/DEAD-CODE path — no code was produced.)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-16   (conservative + risk:high — human-owned gate; evidence: task guard 7/7 + suite 1158/1158 + wording-lint/xml/parity green + 3 homes md5-identical + engine byte-identical; earned-green confirmed by manual refute-read)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the guided-choice convention is followed at later gates (gate-wiring + suggest-book-align freezes/verifies render as recommended-pick + described-alternatives); report-template.md stays md5-identical across the 3 homes.
Spec delta for the next loop: gate-wiring inherits this frozen token vocabulary (T1–T6); suggest-book-align introduces the glossary headwords `guided decision` · `recommended pick`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the decision-suggestion convention dogfooded its own gates — the milestone-confirm, the §3 freeze, and the verify gate all rendered as guided choices (▶ recommended-first + per-option descriptions) in the very convention being built (evidence: the three AskUserQuestion asks in this run used the recommended-pick + described-alternatives shape)
- [SDD · folded] a prose-convention contract freezes a TOKEN SET + structural invariants, not an HTTP shape — §3's checkable seam (tokens T1–T6 + invariants I1–I4 + 3 reject codes) is the dependable gate the two downstream tasks build against (evidence: test_suggestion_block asserts the token set; engine byte-identical, bundle-parity green)
- [TDD · folded] for a prose feature the red suite splits into RED feature-token tests + STAY-GREEN invariant guards (five-block · no-new-tag · home-parity) — "red for the right reason" comes from the feature tokens while the invariants guard regression during the 3-home edit (evidence: 3 fail / 4 pass at the red run → 7/7 after build)
- [ADD · folded] `after EVIDENCE` and `Least-sure flag surfaced at freeze:` are PARSED prose tokens an automated guard reads — the freeze guard refused `advance` until the literal label was present (evidence: unflagged_freeze on the first tests→build advance attempt)
