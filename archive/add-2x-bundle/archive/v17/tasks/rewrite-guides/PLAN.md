# TASK: Rewrite the 8 phase guides + appendix-b to the frozen rubric

slug: rewrite-guides · created: 2026-06-07 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high declared — the boundary holds 6-verify.md's security prose + 5-build.md's
     never-weaken line (the method/trust-layer itself); the verify gate stays human-led. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: rewrite the 8 phase guides + appendix-b (the remaining 9-file surface) to the FROZEN
  WORDING_RUBRIC; clear every remaining idiom in BOTH written forms (hyphen + space) surface-wide and
  promote the full idiom_map to [enforced]; behind both gates (wording-lint + semantic-inventory) plus
  a new both-forms red suite. NO guard change-request this time — every edit is word-level inside an
  existing structure (no section moves into/out of tags).
Framings weighed: ONE task staged by file-risk (chosen — milestone froze rewrite-guides as one task; the
  boundary is small: 7 idiom occurrences + ~3 positivizations) · split guides/appendix into two tasks
  (rejected — rubber-stamp + wall-of each live in BOTH 1-specify.md and appendix-b, so a split couples the
  promotion flips across tasks) · fold into clarity-greenstate (rejected — greenstate is verification-only
  by the milestone decomposition).
Must:
  - CLEAR the 7 remaining idiom occurrences, BOTH FORMS: phases/1-specify.md L14 (collapses to) ·
    L28 (wall of + rubber-stamped + negative framing, one reword) · L34 (FIRST FEEDER, caps dialed) ·
    phases/7-observe.md L9 (`blast-radius` — the ALREADY-[enforced] hyphen escape F1 cannot see;
    proven live: the lint is GREEN today with this hit on the surface) · appendix-b L27 (rubber-stamped)
    · L30 (wall of, INSIDE a protected `Never:` field — the FIELD and its prohibition stay; only the
    idiom phrase changes).
  - PROMOTE all 4 remaining idioms [mapped]→[enforced], each in the SAME commit that removes its LAST
    surface occurrence: collapses-to + first-feeder flip with the 1-specify.md commit; rubber-stamp +
    wall-of flip with the appendix-b commit (their last occurrences live there).
  - POSITIVIZE ordinary instruction-negatives where a clean positive exists: 0-setup.md L31 (never
    clobber) · 2-scenarios.md L19 (Never omit it on a rejection) · 3-contract.md L37 (never a second
    gate). Light-touch candidates (build judgment, kept-deliberately if not taken): 0-setup L30 ·
    1-specify L24 · 1-specify L58 · appendix-b L145.
  - LEAVE BYTE-UNCHANGED the gate-blind protected safety lines: 5-build.md L15 (never weaken/never edit
    frozen) · 6-verify.md L11 + L28 (security always HARD-STOP / never auto-passed / never a waiver) ·
    4-tests.md L34 (symlink escapes never read) · every `Never:` prompt-field (sole exception: the
    idiom inside appendix-b L30, field intact). An EMPTY DIFF is the proof of safety for a gate-blind line.
  - SCOPE QUALIFIERS: add one only where a rule reads phase-wide without stating its scope (guides are
    phase-scoped by construction — expected near-no-op; a no-op is recorded as a finding, never silent).
  - KEEP BOTH GATES GREEN after every commit; the §4 red suite green at close (both-forms zero + full
    promotion); xml-convention guards on 1-specify.md + appendix-b stay green UNTOUCHED.
  - MIRROR PARITY per commit: phases/ → _bundled + .claude byte-identical; appendix-b → its 3 TRACKED
    copies (canonical · _bundled · repo-root) + the gitignored .add/docs dogfood copy — NO existing test
    guards the root/.add copies (the §4 parity guard + manual discipline close that hole).
Reject:
  - a reword that changes a RULE's meaning -> "semantics_changed"  (change-request to SPECIFY, never a wording edit)
  - positivizing a protected safety negative or dropping a `Never:` field -> "protected_negative_removed"
  - renaming a keep_list term instead of rewording around it -> "keep_term_renamed"  (F3 break)
  - removing an idiom's last surface occurrence WITHOUT flipping [mapped]→[enforced] in the same commit,
    or flipping one still present anywhere -> "idiom_unretired"
  - clearing only ONE written form of an idiom while the other survives anywhere on the surface
    -> "form_escape"  (NEW — the blast-radius lesson; the §4 both-forms test is its fence)
  - a canonical edit not mirrored to ALL its copies in the same commit -> "parity_drift"
  - adding or splitting an XML tag, or moving prose across a tag boundary -> "tag_vocab_violated"
After:
  - All 5 idiom_map entries are [enforced]; a both-forms scan of all 5 idioms over the whole surface
    returns ZERO; `enforced_banned == full idiom_map` is assertable (clarity-greenstate's exit).
  - The protected safety lines are byte-identical to pre-task; every `Never:` field survives.
  - The 3 tracked appendix-b copies + dogfood copy are byte-identical; phases/ mirrors in parity.
  - Both gates + the red suite + xml guards + whole tooling suite + add.py check/audit green.
Assumptions — least-sure first:
  ⚠ THE GATE PROVES LESS IN THIS BOUNDARY than it did in rewrite-core — 5-build.md has ZERO semantic-
    inventory entries (its never-weaken line is fully gate-blind), 6-verify.md is TOKEN-ONLY (an inversion
    around a surviving HARD-STOP passes S1), and appendix-b has zero inventory entries AND no parity test.
    Least sure because the ceded class here is not one trim but the WHOLE safety prose of two guides + the
    full appendix. If wrong: the method's core integrity prose weakens with every gate green. Mitigated:
    byte-unchanged discipline (empty diff shown at the gate as the proof), the §4 green-guards pinning the
    exact strings, and the human diff-read at the conservative verify gate (the primary protection).
  ⚠ THE POSITIVITY JUDGMENT IS ITSELF THE CEDE (cede_list: "whether a negative was rightly positivized") —
    least sure because a wrong positivization weakens an instruction with all gates green. If wrong: an
    agent treats a formerly-prohibited action as merely unlisted. Mitigated: only 3 clear positivizations
    are in-contract; doubtful candidates stay negative by default; every positivization diff is shown
    line-by-line at the verify gate.
  - [ ] the both-forms scan is complete: 7 occurrences across 3 canonical files (grep-verified over the
        whole lint surface; mirrors byte-identical by parity) — backstopped by the §4 regex test, which
        catches any inflection/form variant the manual scan missed.
  - [ ] no guard change-request is needed: every edit is word-level inside existing structures, so
        test_xml_convention (incl. the appendix-b render-safety + pilot guards) stays green untouched —
        verified per-commit; if a structural need surfaces, that is a change-request back to SPECIFY,
        never an inline edit.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: both-forms idiom retirement (the red target)
  Given the frozen idiom_map (4 [mapped] + blast-radius's live hyphen escape in 7-observe.md)
  When the 9-file boundary is rewritten
  Then a case-insensitive BOTH-FORMS scan of all 5 idioms over the whole lint surface returns zero
  And every keep_list term still appears (F3) and wording_lint exits 0

Scenario: promotion lands with the last occurrence
  Given an idiom whose final surface occurrence is removed by a commit
  When that commit lands
  Then the SAME commit flips its idiom_map line [mapped]→[enforced]
  And wording_lint exits 0 on that commit (never trivially-green: the flip arms F1 for it)

Scenario: protected safety lines untouched (gate-blind class)
  Given the pinned safety lines in 5-build.md · 6-verify.md · 4-tests.md and every `Never:` field
  When the rewrite lands
  Then each pinned line is byte-identical to pre-task (empty diff shown at the verify gate)
  And semantic_inventory reports 0 findings and the §4 green-guards still pass

Scenario: a positivization preserves the rule
  Given an ordinary instruction-negative with a clean positive form (the 3 in-contract lines)
  When it is positivized
  Then the obligation and its scope are unchanged (same actor, same action, same condition)
  And the line's diff is reviewed at the conservative verify gate

Scenario: appendix-b stays in sync everywhere
  Given the 3 tracked copies + the gitignored .add/docs dogfood copy
  When the canonical add-method/docs/appendix-b-prompts.md is edited
  Then all four copies are byte-identical in the same commit
  And the §4 parity guard passes (the previously-unguarded hole is fenced)

Scenario: form escape is rejected (reject form_escape)
  Given an idiom cleared in one written form while the other survives anywhere on the surface
  When the §4 suite runs
  Then test_no_idiom_any_form_on_surface FAILS naming file:line and the surviving form
  And the commit is blocked (the fence catches what F1 is form-blind to)

Scenario: a semantics change is routed, not reworded (reject semantics_changed)
  Given a reword that would drop/rename/relocate a unit, break an invariant, or add an exception
  When it is detected (gate, guard, or review)
  Then the edit is withdrawn and routed as a change-request back to SPECIFY
  And the frozen contract and all guards remain untouched
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TOUCH-BOUNDARY (9 surface files + rubric flips + new test; mirrors propagate per commit):

EDIT  skill/add/phases/1-specify.md
      L14  "this collapses to one sentence"  ->  "this shortens to one sentence"
      L28  "Never a flat wall of equal `[x]` ticks — that is what gets rubber-stamped."
           ->  "Keep the ranking visible — a flat list of equal `[x]` ticks gets approved without reading."
      L34  "your §1 ranking is the FIRST FEEDER into"  ->  "your §1 ranking is the first input into"
EDIT  skill/add/phases/7-observe.md
      L9   "**Release behind a blast-radius limit**"  ->  "**Release behind a scope-of-impact limit**"
EDIT  docs/appendix-b-prompts.md            (+ 2 tracked copies + dogfood, byte-identical)
      L27  "# why: a flat all-equal list gets rubber-stamped; a ranked one aims my attention at the risk."
           ->  "# why: a flat all-equal list gets approved without reading; a ranked one aims my attention at the risk."
      L30  "Never a blank \"none\" or a flat wall of equal ticks."
           ->  "Never a blank \"none\" or a flat list of equal ticks."     (the `Never:` field + prohibition STAY)
EDIT  skill/add/phases/0-setup.md
      L31  "fill each survivor file from the code, never clobber an existing one, and tag"
           ->  "fill each missing survivor file from the code, keep an existing one unchanged, and tag"
EDIT  skill/add/phases/2-scenarios.md
      L19  "Never omit it on a rejection."  ->  "Include it on every rejection."
EDIT  skill/add/phases/3-contract.md
      L37  "— never a second gate, no sign-off forms, no"  ->  "— the freeze stays the only gate: no sign-off forms, no"
FLIP  tooling/WORDING_RUBRIC.md  idiom_map   (promotion protocol — flip IN the clearing commit)
      collapses to + first feeder  -> [enforced]   (with the 1-specify.md commit)
      rubber-stamp + wall of       -> [enforced]   (with the appendix-b commit)
ADD   tooling/test_rewrite_guides.py         (§4 suite: 2 RED targets + 3 GREEN guards — already written)

UNTOUCHED — byte-identical, the gate-blind protected class:
      5-build.md L15 · 6-verify.md L11 + L28 · 4-tests.md L34 · every `Never:` prompt-field
      (sole exception: the idiom phrase inside appendix-b L30; field + prohibition intact)

LIGHT-TOUCH candidates (build judgment; each taken OR recorded kept-deliberately; diffs shown at the gate):
      0-setup L30 ("read it, don't ask" -> "read it instead of asking") · 1-specify L24 (contrast example)
      · 1-specify L58 (reinforcing parenthetical) · appendix-b L145 ("never chat memory" contrast)

STAGING (gates green after EVERY commit; binding properties govern over this illustrative order):
      C1 7-observe.md blast-radius (no flip — already [enforced]; closes the live escape)
      C2 1-specify.md rewrite + FLIP collapses-to & first-feeder
      C3 appendix-b rewrite + FLIP rubber-stamp & wall-of + 4-copy sync
      C4 positivize pass (0-setup · 2-scenarios · 3-contract + any light-touch taken)

HEADER: risk: high · autonomy: conservative   (6-verify security prose + 5-build never-weaken =
      the method/trust-layer; the verify gate stays human-led, no auto-PASS)
NO GUARD CHANGE-REQUEST: word-level edits inside existing structures only; test_xml_convention,
      the lint, and the inventory gate are NOT edited by this task.
```

> **RE-RAISED AT THIS FREEZE — the held surface-wide promotion rule** (PENDING in v17/MILESTONE.md
> since the rewrite-core freeze): *an idiom flips [mapped]→[enforced] in the same commit that removes
> its LAST occurrence from the whole lint surface, clearing BOTH written forms (hyphen + space) — and
> a both-forms escape on an ALREADY-enforced idiom is cleared by whichever rewrite task owns the file.*
> Live proof of the rule's operative content: `blast-radius` sits in 7-observe.md TODAY with the lint
> green, because F1 is form-strict. **RATIFIED at this freeze (2026-06-07, Tin Dang)** — recorded as a
> v17/MILESTONE.md shared decision (binds clarity-greenstate + any future wording task); the PENDING
> entry there is resolved.

Status: FROZEN @ v1 — approved by Tin Dang · date: 2026-06-07   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: n/a (docs task — the suite + both gates + parity are the net)
Plan (one test per scenario; RED targets drive the build, GREEN guards pin the gate-blind class):
  - test_no_idiom_any_form_on_surface  [RED — 7 hits named]: both-forms regex scan of all 5 idioms over
    surface_files(); the form_escape fence (catches what F1 is form-blind to, incl. blast-radius today)
  - test_idiom_map_fully_enforced      [RED — 4 still mapped]: load_rubric() → mapped_idioms == [] and
    len(enforced_banned) == 5 (the promotion-protocol scenario; greenstate's exit pre-asserted)
  - test_protected_safety_lines_pinned [GREEN guard — disclosed]: exact safety strings byte-present in
    5-build.md · 6-verify.md · 4-tests.md (the files the inventory does NOT cover)
  - test_appendix_b_copies_identical   [GREEN guard — disclosed]: 3 tracked copies byte-identical
    (closes the unguarded-sync hole — no existing parity test covers appendix-b)
  - test_never_fields_survive          [GREEN guard — disclosed]: every `Never:` prompt-field survives;
    appendix-b keeps ≥7 (the protected-negative scenario's fence)
  (the positivization-preserves-rule + semantics-routed scenarios are HUMAN-judged at the conservative
   verify gate — they are the cede, deliberately not encoded as tests: a meaning test would be the
   model_judged_gate the milestone refuses)

Tests live in: `add-method/tooling/` (test_rewrite_guides.py) · run RED now for the RIGHT reason:
  2 failures naming exactly the 7 occurrences + the 4 unpromoted idioms; 3 guards green.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): a gate-blind protected line ships with an EMPTY diff — when in doubt
  whether a line is protected, leave it unchanged and record it; promotion flips land IN the clearing
  commit, never before or after.
Code lives in: the 9 boundary surface files + their mirrors (phases/ → _bundled + .claude;
  appendix-b → 3 tracked copies + .add/docs dogfood) + WORDING_RUBRIC.md flips (no `src/`).
Constraints: do NOT change any test or the contract; gates green after every commit; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

Build commits: fa8c51d C1 blast-radius escape · 5257a0d C2 1-specify + flip collapses-to/first-feeder ·
fb09be0 C3 appendix-b + flip rubber-stamp/wall-of (FULL map enforced) · c5dc04c C4 positivize ·
e139e3c CR-2 ratified needle update (isolated) · 3b63421 CR-3 revert 0-setup L31 (human-directed AT
the gate, isolated). Gates green after every commit.

Part one — confirm the evidence:
- [x] all tests pass — whole tooling suite 517 OK · test_rewrite_guides 5/5 (both RED targets green:
      zero both-forms occurrences surface-wide + idiom_map fully [enforced]) · wording_lint 0 (F1 armed
      for all 5 idioms) · semantic_inventory 0 · add.py check 200 passed/0 failed (4 pre-existing legacy
      warnings, not this task) · add.py audit clean (46 tasks)
- [x] coverage did not decrease — ADDED test_rewrite_guides.py (2 targets + 3 standing guards, incl.
      the previously-missing appendix-b copy-parity fence); nothing weakened or deleted
- [~] no test or contract was altered during build — the FROZEN §3 is untouched; the ONLY guard edit is
      CR-2 (test_review_checklist.py needle "never a second gate" -> "the freeze stays the only gate",
      isolated commit e139e3c, RATIFIED BY THE HUMAN BEFORE THE EDIT — the guard's stated intent, "the
      anti-ceremony clause must be stated", is unchanged and still enforced). DISCLOSED: §1's "no guard
      change-request needed" assumption proved WRONG for this one line — the task-close whole-suite run
      caught it; surfaced immediately (close-gap-before-gate), never edited inline. The WORDING_RUBRIC
      flips are the contract-mandated promotions, not guard edits.

Part two — blind-spots:
- concurrency / timing — N/A: a prose/docs rewrite, no runtime path. The architectural invariant is
  mirror parity: phases/ 3-tree (canonical ↔ _bundled ↔ .claude) + appendix-b 4-copy — ALL GREEN,
  including the NEW §4 parity guard that previously did not exist for appendix-b.
- ⚠ SECURITY (escalates to human, by design): this boundary is the LEAST gate-covered slice of v17
  (5-build.md: ZERO inventory entries; 6-verify.md: token-only; appendix-b: zero inventory). The build's
  countermeasure: the protected class shipped with an EMPTY DIFF — verified `git diff e10150b..HEAD` on
  5-build.md · 6-verify.md · 4-tests.md is EMPTY, and all 7 appendix-b `Never:` fields are intact (the §4
  green-guards pin both facts going forward). What REMAINS for the human read (the ceded class): the 4
  positivizations + the two idiom-line rewords — whether each preserves the obligation and its scope. No
  weakened guard or removed invariant DETECTED; this is an escalation-for-review, not a HARD-STOP finding.
  RESOLVED at the gate (2026-06-07): the human read the full canonical diff (e10150b..HEAD rendered in
  chat). Ratified as obligation-preserving: 3 of the 4 positivizations + both idiom-line rewords. The 4th
  (0-setup L31 — the single edit where the obligation itself moved: fill-each→fill-each-missing,
  never-clobber→keep-unchanged) was REVERTED by ruling — CR-3, isolated 3b63421 — and joins the
  kept-deliberately class; the engine's own comment (add.py:353 "never clobber an existing one")
  confirmed the original prose mirrors engine semantics. Gates re-run green after CR-3.
- architecture / layering — N/A (no code layers); v16 5-tag XML vocabulary untouched (word-level edits
  only, inside existing structures); CONVENTIONS.md mirror rule honored.

### GATE RECORD
Outcome: PASS — contingent on CR-3 (the L31 revert), which was executed, mirrored, and re-verified
green (517 OK · lint 0 · inventory 0 · 5/5) BEFORE this stamp. The PASS also ratifies CR-2's
execution, the 3 kept-deliberately light-touch candidates, and the scope-qualifier no-op finding.
Push HELD until v17 milestone close (human ruling at this gate).
Reviewed by: Tin Dang · date: 2026-06-07

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): no production runtime — the scenarios ARE the standing monitors:
wording_lint F1 (all 5 idioms enforced, inflection-tolerant) + test_rewrite_guides both-forms regexes
(the form_escape fence) + protected-line pins + appendix-b 4-copy parity, all in every suite run.
Spec delta for the next loop (clarity-greenstate): its exit `enforced_banned == full idiom_map` is now
ASSERTABLE (all 5 [enforced], both-forms scan zero). Carry the kept-deliberately register so future
rewrites don't retry them: 1-specify L24 (contrast example) · L58 (run.md consistency) · appendix-b
L145 (load-bearing field warning) · 0-setup L31 (CR-3: the negative IS the obligation).

### Competency deltas
- [TDD · folded] on a guard-dense surface the per-commit battery must grep the tooling tests for pinned
  needles of EVERY edited line (or run the whole suite per commit) — boundary-scoped guard lists miss
  out-of-boundary pins (evidence: test_no_ceremony collision surfaced only at task-close → CR-2).
- [ADD · folded] empty-diff-as-evidence: a gate-blind protected class is verified by byte-identity, not
  by gates — show the empty diff at the gate as the proof (evidence: `git diff e10150b..HEAD` empty on
  5-build/6-verify/4-tests carried the ⚠ SECURITY escalation to resolution).
- [ADD · folded] the conservative gate's human read catches what no gate can: of 4 positivizations all
  gates-green, the human reverted exactly the one whose obligation moved (evidence: CR-3 on 0-setup
  L31, directed at the gate with lint/inventory/suite green throughout).
- [SDD · folded] positivization has a boundary: when the negative IS the obligation ("never clobber"),
  rewording shifts semantics — guide prose should mirror engine semantics verbatim (evidence:
  add.py:353 "never clobber an existing one" matched the original L31; the reword silently diverged).
