# TASK: Earned-green rubric — judgment cheats (overfit · vacuous · stub) scored by an adversarial refute-read

slug: earned-green-rubric · created: 2026-06-11 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
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
  - `add-method/skill/add/phases/6-verify.md` (the verify GUIDE, ×3 skill trees: canonical · `.claude/skills/add/…` dogfood · `…/src/add_method/_bundled/skill/add/…` bundle) — sections `## Part one — confirm the evidence` / `## Part two — check what tests miss` / `## Part three — the deep check`. The earned-green rubric slots here (a new `## Part …` or an extension of Part one). Whole tree is parity-guarded → my edit auto-mirrors.
  - `add-method/docs/08-step-6-verify.md` (the BOOK chapter, ×4: root `./` · canonical · `.add/docs` dogfood · `_bundled/docs` bundle; 81 lines; `## Part one/two/three` + `## The verification checklist`) — carries the SAME rubric wording, `_norm`-identical to the guide (the deep-verify single-source pattern). ⚠ the ROOT `./08-step-6-verify.md` is NOT a woven chapter (`test_inline_citations.WOVEN_CHAPTERS = 02/03/09`) → its root↔canonical leg is UNGUARDED; this task syncs root by hand AND adds the guard.
  - `add-method/tooling/templates/TASK.md.tmpl` `## 6 · VERIFY` (the §6 TEMPLATE, ×3 tooling/templates trees) — 7 checkboxes + the `### Deep checks` block + `### GATE RECORD`. Add ONE additive earned-green line before GATE RECORD (mirrors how verify-deepen added the Deep-checks block). No `appendix-a-templates.md` §6 exists — the §6 template lives only in `TASK.md.tmpl`.
  - `.add/GLOSSARY.md` (the LIVE survivor, bare `term:` one-line format, concept-order) + `add-method/tooling/templates/GLOSSARY.md.tmpl` (×3 new-project template) — the two new terms land here (verify-deepen's precedent: `LIVING_GLOSSARY` + `GLOSSARY_TMPL`, NOT the book `appendix-c-glossary.md`).
  - `add-method/skill/add/run.md` `adversarial verify` — the EXISTING in-run skeptic term ("an independent skeptic tries to REFUTE a 'done' claim"). The new `adversarial refute-read` is the verify-gate, whole-suite specialization of the SAME discipline; relate-and-point (single-source), do NOT edit run.md in this task (its auto-gate ENFORCEMENT is task 3).
  - `add-method/tooling/test_earned_green_rubric.py` (NEW, the red guard) — mirrors `test_verify_deepen.py` exactly: per-surface ASCII anchors · `_norm` cross-surface identity (rubric_drift) · additive guard (existing §6 lines + deep-verify anchors survive) · template-triplet parity · glossary-term · `test_engine_unchanged` (pin holds) · PLUS the root-book root↔canonical guard.
Context (working folder):
  - docs — `.add/milestones/verify-integrity/MILESTONE.md` (shared decisions: the 3 named cheats `overfit · vacuous · stub` scored by an INDEPENDENT adversarial refute-read; "a confirmed cheat is a HARD-STOP — never auto-passed, never RISK-ACCEPTED"; task 2 exit criterion = guide+template NAME the cheats + the refute-read, ×3/×4 parity; the LOOP is task 3). `add-method/tooling/test_verify_deepen.py` (the precedent analog — the exact prose-only rubric task to mirror).
  - config/data — no engine state; this task writes NO `state.json` schema. `./tests/` holds the new guard test (run from `add-method/tooling/`).
  - no todos relevant.
Honors (patterns / conventions):
  - **mirror parity + a MIRRORS clause that enumerates EVERY copy** (CONVENTIONS fv18/fv22) — guide ×3, book ×4, template ×3, glossary survivor + `GLOSSARY.md.tmpl` ×3; a parity test backstops drift.
  - **prose-change TDD** (CONVENTIONS fv7) — assert content anchors + cross-tree byte-identity; write the assertion RED before the edit.
  - **single-source — POINT to, never restate** (CONVENTIONS fv22) — relate the refute-read to run.md's adversarial verify by pointer, don't duplicate the skeptic definition.
  - **v16 guide tag vocab** (frozen 5-tag; guides allow only `{prompt, output_format, exit_gate}`) — add NO new XML tags to `6-verify.md`; if a new `## Part` heading is added, register it in `test_xml_convention.PHASE_FILES["6-verify.md"]["narrative"]` (test-file only) so the over-tagging guard stays real.
  - **lean scope — the engine stays judgment-free** (verify-deepen precedent) — `add.py` byte-UNCHANGED, `engine_pin.ENGINE_MD5` does NOT bump; the resolver judges code-vs-prose, the engine never classifies.
  - **ASCII-safe anchors** (house rule) — test anchors are contiguous ASCII substrings of the canonical wording so cross-surface drift shows as a missing anchor.
Anchors the contract cites: `6-verify.md` Part-one/two/three (the rubric's home, ×3) · `08-step-6-verify.md` (book, ×4; root leg newly guarded) · `TASK.md.tmpl` `## 6 · VERIFY` (additive line before `### GATE RECORD`) · `.add/GLOSSARY.md` + `GLOSSARY.md.tmpl` (the 2 new terms) · `run.md` `adversarial verify` (the related-term pointer) · `test_verify_deepen.py` `_norm`/`DEEP_ANCHORS`/`SIX_EXISTING`/`test_engine_unchanged` (the pattern + the additive-survival guard) · `engine_pin.ENGINE_MD5` (must NOT bump — the lean-scope guard)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Earned-green rubric — the verify GUIDE + BOOK + the §6 TEMPLATE + the GLOSSARY name the three JUDGMENT cheats the mechanical tripwire can't see (src OVERFIT to the test fixtures · VACUOUS/tautological asserts · real logic STUBBED away) and require an INDEPENDENT adversarial refute-read to score them. The rubric is the judgment layer PAIRED with task 1's mechanical floor: the tripwire catches the tampering it can SEE (edited tests/contract), this rubric catches the cheats it CAN'T. Prose only — the engine stays judgment-free (pin holds).
Framings weighed: a named earned-green rubric as a new `## Part …` in the guide + book, mirrored to the §6 template as ONE additive check line, terms in the live glossary (chosen — mirrors verify-deepen's precedent exactly; the engine never classifies) · fold the rubric into the existing "no test or contract was altered" line (rejected — conflates the MECHANICAL tamper signal (task 1) with the JUDGMENT cheats; the milestone names them distinct) · add the rubric to run.md's auto-gate residue list now (rejected — that is ENFORCEMENT, task 3; task 2 describes the rubric, it does not wire the gate).
Must:
<must>
  - NAME the three judgment cheats in the verify GUIDE (`6-verify.md`), one tell each: src OVERFIT to the test fixtures (special-cased to the literal inputs) · VACUOUS / tautological asserts (green-trivial even at §4) · real logic STUBBED away (returns a constant).
  - REQUIRE the score from an INDEPENDENT adversarial refute-read — a reviewer (or subagent under `autonomy: auto`) prompted to argue "the green was NOT earned," separate from the build context. The guide RECOMMENDS a subagent; the engine never spawns one (tool-agnostic).
  - STATE the rubric IDENTICALLY in the BOOK chapter (`08-step-6-verify.md`), `_norm`-identical to the guide (the single-source deep-verify pattern — same wording, each surface wraps at its own column).
  - ADD one additive earned-green CHECK line to the §6 TEMPLATE (`TASK.md.tmpl`), before `### GATE RECORD`; ALL 7 existing checkboxes + the `### Deep checks` block stay intact.
  - DEFINE two new terms in the LIVE glossary (`.add/GLOSSARY.md`) + `GLOSSARY.md.tmpl`: "earned green / build integrity" and "adversarial refute-read"; relate the refute-read to run.md's "adversarial verify" by POINTER (single-source), never restating the skeptic definition.
  - STATE in prose that a confirmed earned-green failure is HARD-STOP-class — never auto-passed, never RISK-ACCEPTED — WITHOUT forward-referencing task 3's unbuilt ≤3-attempt loop machinery (the principle, not the mechanism).
  - KEEP the engine byte-UNCHANGED: `add.py` untouched, `engine_pin.ENGINE_MD5` does NOT bump.
  - SYNC every mirror: guide ×3 · book ×4 (incl. the hand-synced ROOT copy + a NEW root↔canonical guard, since `08` is not a woven chapter) · template ×3 · glossary survivor + `GLOSSARY.md.tmpl` ×3.
</must>
Reject:
<reject>
  - the rubric in the guide but missing from the book, or vice-versa -> "rubric_drift" (the `_norm` cross-surface anchor test)
  - an existing §6 template line OR a deep-verify anchor removed by the additive edit -> "seam_broken"
  - `add.py` edited / `engine_pin.ENGINE_MD5` bumped -> "engine_touched" (the lean-scope guard)
  - a new paired XML tag introduced in `6-verify.md` outside {prompt, output_format, exit_gate} -> "vocab_offmidiom"
  - the rubric describing the ≤3-attempt loop or auto-gate enforcement -> out of scope (task 3); task 2 states only the principle + the rubric
  - the ROOT book copy left stale (canon/bundle/dogfood edited only) -> "mirror_drift" (the NEW root↔canonical guard)
</reject>
After:
<after>
  - the 3 cheats + the adversarial refute-read are named in the guide AND the book, word-identical under `_norm`.
  - the §6 template carries the earned-green check line; every prior §6 line + the Deep-checks block survive.
  - the 2 terms are defined in the live glossary + the template; the refute-read points to run.md's adversarial verify.
  - `add.py` is byte-identical to the pin; the full suite is green; a guard test pins the anchors + ×3/×4 parity (incl. the root leg).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the relationship between the NEW "adversarial refute-read" and run.md's EXISTING "adversarial verify" — lowest confidence because they share the skeptic mechanism but apply at DIFFERENT points (in-run "done"-claim refutation vs verify-gate whole-suite earned-green refutation); chosen: coin "adversarial refute-read" as the verify-gate specialization, related-by-pointer to adversarial verify (milestone-blessed). If wrong (the human prefers REUSING "adversarial verify"): a term rename churns the frozen wording across guide + book + glossary.
  - [x] [spec] the §6 template line is INERT — confirmed by grep: the decide-digest only LISTS `- [ ]` markers (no pinned count); `_exit_criteria` tallies MILESTONE/PROJECT boxes, never TASK.md §6. One more box is just one more check.
  - [ ] [scenario] a new `## Part four` heading vs extending Part one — chosen: a new `## Part …` reads cleaner and pairs visibly with task 1's floor; register it in `test_xml_convention`'s narrative tuple (test-file only). Low risk (a prose call).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guide names the three judgment cheats
  Given the verify guide 6-verify.md
  When a reader reaches the earned-green rubric
  Then it names "overfit" to the fixtures, "vacuous"/tautological asserts, and logic "stubbed" away
  And each cheat carries a one-line tell

Scenario: the rubric requires an independent adversarial refute-read
  Given the earned-green rubric in the guide
  When it says HOW the cheats are scored
  Then it requires an independent adversarial refute-read prompted to argue "the green was NOT earned"
  And it RECOMMENDS a subagent under autonomy:auto while stating the engine never spawns one

Scenario: the book states the rubric identically to the guide
  Given the guide and the book chapter 08-step-6-verify.md
  When both are normalized (whitespace collapsed)
  Then every earned-green anchor present in the guide is present in the book verbatim
  And neither surface carries an anchor the other lacks            # rubric_drift

Scenario: the §6 template gains the earned-green check additively
  Given the §6 VERIFY section of TASK.md.tmpl
  When the earned-green check line is added
  Then it sits before "### GATE RECORD"
  And all 7 prior §6 checkboxes and the "### Deep checks" block remain   # seam_broken

Scenario: the glossary defines both new terms and points to run.md
  Given .add/GLOSSARY.md and GLOSSARY.md.tmpl
  When a reader looks up the new terms
  Then "earned green" / build integrity and "adversarial refute-read" are defined
  And the refute-read entry points to run.md's adversarial verify rather than restating it

Scenario: the principle is stated without forward-referencing task 3
  Given the earned-green rubric prose
  When it states the consequence of a confirmed cheat
  Then it says a confirmed earned-green failure is HARD-STOP-class — never auto-passed, never RISK-ACCEPTED
  And it does NOT describe the ≤3-attempt loop or auto-gate wiring   # task 3 scope

Scenario: the engine stays byte-unchanged (pin holds)
  Given add.py and engine_pin.ENGINE_MD5 before the task
  When the task completes
  Then add.py is byte-identical to the pinned engine            # engine_touched
  And no earned-green token (overfit/vacuous/stub) appears in add.py

Scenario: the guide adds no off-vocabulary XML tag
  Given 6-verify.md after the rubric is added
  When its paired XML tags are enumerated
  Then every tag is one of {prompt, output_format, exit_gate}    # vocab_offmidiom
  And any new "## Part" heading is registered in the narrative tuple

Scenario: every mirror copy carries the rubric (no stale root)
  Given guide ×3, book ×4, template ×3, glossary survivor + tmpl ×3
  When the guard test runs
  Then each tree's copy carries the earned-green anchors
  And the ROOT book copy matches canonical                       # mirror_drift
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOCS-CONTRACT  earned-green-rubric   (prose only; the engine is judgment-free)

RUBRIC ANCHORS — contiguous ASCII substrings frozen across the guide + book (the
  exact wording is drafted at build; these tokens are the drift sentinels):
    "earned"        the rubric is named (earned green / build integrity)
    "overfit"       cheat 1 — src special-cased to the test fixtures
    "vacuous"       cheat 2 — tautological / green-trivial asserts
    "stub"          cheat 3 — real logic stubbed away (returns a constant)
    "refute"        scored by an independent adversarial refute-read
    "the engine never spawns"   the refute-read is a recommendation; tool-agnostic
    "HARD-STOP"     a confirmed earned-green failure is HARD-STOP-class

SURFACES (what lands where):
  guide   add-method/skill/add/phases/6-verify.md      a new "## Part …" earned-green rubric
  book    add-method/docs/08-step-6-verify.md           the SAME rubric, _norm-identical to the guide
  tmpl    add-method/tooling/templates/TASK.md.tmpl      +1 additive "- [ ]" earned-green line before "### GATE RECORD"
  gloss   .add/GLOSSARY.md + …/templates/GLOSSARY.md.tmpl  2 new terms: "earned green", "adversarial refute-read"

MIRRORS (every copy — drift in any is a finding):
  guide ×3 : add-method/skill/add/… · .claude/skills/add/… · …/src/add_method/_bundled/skill/add/…
  book  ×4 : ./08-step-6-verify.md (ROOT) · add-method/docs/… · .add/docs/… · …/src/add_method/_bundled/docs/…
  tmpl  ×3 : add-method/tooling/templates/… · .add/tooling/templates/… · …/src/add_method/_bundled/tooling/templates/…
  gloss    : .add/GLOSSARY.md (survivor, ×1) + GLOSSARY.md.tmpl ×3
  guard    : add-method/tooling/test_earned_green_rubric.py (NEW) — anchors per surface · _norm identity (guide↔book) ·
             additive survival (SIX_EXISTING + DEEP_ANCHORS intact) · template triplet · glossary term · engine-unchanged ·
             ROOT book root↔canonical (the leg test_inline_citations does NOT cover for 08)

INVARIANTS:
  - additive: no existing §6 checkbox / Deep-checks line / deep-verify anchor is removed
  - _norm-identical: guide and book carry the same rubric WORDING (whitespace-collapsed)
  - engine untouched: add.py == engine_pin.ENGINE_MD5; pin does NOT bump
  - guide tag vocab ⊆ {prompt, output_format, exit_gate}; a new "## Part" heading is registered in the narrative tuple
  - single-source: the refute-read POINTS to run.md's adversarial verify, never restates it

KNOWN LIMIT (scope boundary, not a defect):
  - task 2 DESCRIBES the rubric + states the HARD-STOP principle; it does NOT enforce. The auto-gate
    wiring + the ≤3-attempt self-heal loop are task 3 (heal-then-escalate). A reader following only the
    rubric scores by JUDGMENT; the teeth arrive in task 3.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-11.
Least-sure flag surfaced at freeze: [contract] the term ontology — "adversarial refute-read" is the NEW verify-gate, whole-suite earned-green skeptic vs run.md's EXISTING in-run "adversarial verify" ("done"-claim skeptic). RATIFIED choice (Tin Dang, "Freeze — coin + point"): COIN "adversarial refute-read" as the verify-gate specialization, defined by a POINTER to run.md's adversarial verify (single-source — never restated). The alternative (reuse "adversarial verify" everywhere) was rejected to keep the two application points distinct.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior — every rubric anchor present per surface + cross-surface `_norm` identity + ×3/×4 parity + the engine-unchanged lean-scope guard. Not a % (prose task).
Plan (one test per scenario, asserting behavior not internals — mirrors `test_verify_deepen.py`):
<test_plan>
  - test_guide_names_three_cheats: assert 6-verify.md contains "overfit", "vacuous", "stub"      [scenario 1]
  - test_rubric_requires_refute_read: assert the guide contains "refute" + "the engine never spawns" (recommendation, tool-agnostic)   [scenario 2]
  - test_rubric_stated_identically: _norm(guide) and _norm(book) each contain every EARNED_ANCHOR; a miss in either -> rubric_drift   [scenario 3]
  - test_template_earned_green_additive: TASK.md.tmpl §6 gains the earned-green line BEFORE "### GATE RECORD"; assert all SIX_EXISTING lines + "Deep checks" survive -> seam_broken   [scenario 4]
  - test_glossary_defines_terms_and_points_runmd: .add/GLOSSARY.md + GLOSSARY.md.tmpl define "earned green" + "adversarial refute-read"; the refute-read line names run.md / adversarial verify (the pointer)   [scenario 5]
  - test_principle_no_loop_forward_ref: the rubric prose contains "HARD-STOP" AND does NOT contain the task-3 loop tokens ("3 attempts" / "self-heal" / "re-build loop")   [scenario 6]
  - test_engine_unchanged: md5(add.py) == engine_pin.ENGINE_MD5; assert no "overfit"/"vacuous"/"refute" token leaked into add.py   [scenario 7]
  - test_guide_vocab_subset: every paired XML tag in 6-verify.md ∈ {prompt, output_format, exit_gate}; (test_xml_convention backstops; a focused assert here too)   [scenario 8]
  - test_all_mirrors_carry_anchors: guide ×3 · book ×4 · template ×3 each carry the anchors; test_root_book_matches_canonical: md5(root 08) == md5(canonical 08) -> mirror_drift   [scenario 9]
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- ./tests/ is intentionally EMPTY for this prose/method task (consistent with verify-deepen
     and tamper-tripwire): the real red guard is `add-method/tooling/test_earned_green_rubric.py`,
     run via the tooling unittest suite (`cd add-method/tooling && python3 -m unittest discover`).
     It imports engine_pin and asserts the anchors + ×3/×4 parity + engine-unchanged. The ×3 skill /
     ×2 bundle / ×3 template parity is ALSO backstopped by the existing test_tree_parity /
     test_bundle_parity / test_verify_deepen suites; this task ADDS the root↔canonical book leg. -->
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 828 OK (was 815 + the new 13); the 13 ran RED before build (8 anchor-absent failures + the 5 over-block guards green) → GREEN after.
- [x] coverage did not decrease — +13 behavior tests; no existing test weakened (the only edit to an existing test was ADDITIVE: `## Part four …` appended to `test_xml_convention.PHASE_FILES["6-verify.md"]["narrative"]`, which TIGHTENS the over-tagging guard).
- [x] no test or contract was altered during build — the frozen §3 docs-contract honored; DOGFOOD: this task itself crossed tests→build under the new engine, so task 1's tamper tripwire snapshotted it (§3 + empty `./tests/`) and re-checked clean at this gate (no `tamper_detected`).
- [x] the green was EARNED, not gamed (self-applying THIS task's own rubric) — no OVERFIT (the tests assert real anchors in real files, not fixtures) · no VACUOUS asserts (the `_norm` hard-wrap bug was caught red — the test BITES) · no STUBBED logic. The rubric scored its own build and passed.
- [x] concurrency / timing — N/A: prose docs + a read-only guard test; no shared state, no IO race.
- [x] no exposed secrets, injection openings, or unexpected dependencies — the new test imports only stdlib (`re`, `hashlib`); no runtime dependency added; `add.py` byte-UNCHANGED (`test_engine_unchanged` green, pin holds).
- [x] layering & dependencies follow CONVENTIONS.md — mirror parity (guide ×3 · book ×4 · template ×3 · GLOSSARY.md.tmpl ×3, each one md5) · single-source (the refute-read POINTS to run.md's adversarial verify) · v16 vocab subset (no new XML tag in 6-verify.md) · prose-TDD (red first). The advisor-flagged ROOT book leg is now guarded (`test_root_book_matches_canonical`).
- [x] a person reviewed and approved the change — AUTO-RESOLVED under `autonomy: auto` with complete evidence and NO residue (no security · concurrency · architecture); the recorded run is the accountable owner. The one HUMAN gate for this task was the §3 contract freeze (Tin Dang, 2026-06-11, "Freeze — coin + point").

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new test symbol is referenced: helpers `_md5`/`_norm`/`_paired_tags` + constants `EARNED_ANCHORS`/`CHEAT_KEYWORDS`/`SIX_EXISTING`/`LOOP_TOKENS`/`GUIDE_TREES`/`BOOK_TREES`/`TMPL_TREES` are each used by the 13 test methods; the suite green confirms.
- [x] DEAD-CODE (code) — no orphan symbol added; every constant/helper has a caller.
- [x] SEMANTIC (prose / non-code) — read the rubric in full across guide + book + template + glossary: confirmed the `_norm` wording identity (guide↔book), the three named cheats + the adversarial refute-read, the HARD-STOP principle stated WITHOUT task-3 loop machinery, and the single-source pointer to run.md's adversarial verify.

### GATE RECORD
Outcome: PASS — auto-resolved under `autonomy: auto` (complete evidence; no security/concurrency/architecture residue; the run is the accountable owner). Prose+template only; `add.py` byte-identical to the pin (engine stays judgment-free); the §3 contract freeze was human-approved.
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved run (earned-green-rubric) · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the rubric is a static method surface, so the "monitors" are drift guards — `test_earned_green_rubric` (anchor-presence on every surface), the mirror-parity md5 checks (guide ×3, book ×4, template ×3 each one hash), and `test_engine_unchanged` (add.py == pin). Any surface that loses an anchor or diverges in md5 goes red; the engine pin going red means earned-green prose leaked into the engine.
Spec delta for the next loop: this task DESCRIBES earned-green; task 3 (heal-then-escalate) ENFORCES it — wire the rubric's HARD-STOP into the verify gate as the ≤3-attempt honest-rebuild loop. The §3 KNOWN LIMIT is the explicit handoff; the engine pin WILL bump there (this task's pin must not).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a build-integrity property needs BOTH a mechanical floor and a judgment ceiling — the tamper-tripwire (task 1) catches the cheats it can SEE (edited test / frozen contract), the earned-green rubric the cheats it cannot (src overfit to fixtures · vacuous asserts · stubbed-away logic) via an adversarial refute-read; neither layer alone closes the gamed-green gap (evidence: this task adds the judgment layer atop the now-shipped mechanical floor — the §3 two-layer contract).
- [ADD · folded] anchor-presence proves a phrase EXISTS on a surface, NOT that two surfaces AGREE on its qualifier — the template read "for high-risk" while the guide read "recommended under `autonomy: auto`", and no presence test could see the mismatch; cross-surface qualifier agreement needs a shared render or an adversarial/human read (evidence: advisor caught the template↔guide trigger disagreement after all 13 anchor tests were green; reconciled to the guide's framing pre-commit).
- [ADD · folded] the first NORMAL task run THROUGH a freshly-shipped engine guard is its cheapest end-to-end test — task 2 crossed tests→build under task 1's live tamper-tripwire and its §3 snapshot re-checked clean at the gate (evidence: `add.py gate PASS earned-green-rubric` exit 0, no HARD-STOP — the tripwire validated on a real task, not a fixture).
- [ADD · folded] one milestone can exercise BOTH verify-gate paths, proving the autonomy ladder discriminates by risk not ceremony — task 1 was human-gated (conservative · high-risk · md5 security-line ratified by a person), task 2 auto-resolved (auto · normal-risk · deterministic evidence) (evidence: tamper-tripwire gate = human PASS; earned-green-rubric gate = auto-resolved PASS, same milestone).
- [TDD · folded] a prose/method change is testable by anchor-presence + mirror-parity rather than coverage — one frozen wording carried across guide ×3 / book ×4 / template ×3 / glossary, each guarded by a `_norm`-normalized anchor (hard-wrap is incidental) and a one-hash md5 parity test, with the engine held byte-identical to the pin (evidence: 13 green tests in `test_earned_green_rubric.py`; full suite 815→828; add.py md5 == engine_pin).
- [SDD · folded] a method built in stages needs a scope guard that fails if a LATER stage's machinery leaks BACKWARD into an earlier stage's prose — the task-3 loop tokens (self-heal · re-build · 3 attempts) are asserted ABSENT from the task-2 guide so the rubric describes without pre-empting enforcement (evidence: `test_principle_no_loop_forward_ref` red-then-green; §3 KNOWN LIMIT names the task-2-describes / task-3-enforces boundary).
