# TASK: Deepen verify: wiring + dead-code as code-evidence, semantic no-skim as prose-evidence

slug: verify-deepen · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — edits the VERIFY rubric itself (the trust layer): the skill guide, the book, run.md's
     auto-gate, and the §6 TASK.md template. "method/trust-layer edits are a residue category" (foundation).
     autonomy lowered to conservative: the verify gate stops for the human. The slug-line fields ARE the
     declaration; the engine refuses an unguarded high-risk completion (`unguarded_high_risk_auto`). -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: deepen the Verify rubric so a gate proves the work is real, not merely plausible — for a task that produced code, recorded evidence that every new symbol is referenced (wiring) and that no new dead/unused code was introduced; for a task that produced prose / non-code, a recorded semantic no-skim read (what was read in full · what it confirmed). The requirement is stated identically in the verify guide (`phases/6-verify.md`), the book (`docs/08-step-6-verify.md`), and run.md's automated-quality-gate evidence list, and carried as an additive "Deep checks" block in the §6 TASK.md template. Which path applies is the resolver's judgement (AI or human); the engine never classifies and `add.py` is not modified. This is the rubric the rest of v20 enforces — `reopen-transition` fires when a deepened check finds a done task's criterion unmet.
Framings weighed: rubric prose (guide + book + run.md, stated identically) + an additive §6 template Deep-checks block, resolver-judged code-vs-prose, engine byte-unchanged (chosen — matches the milestone's "stated identically in guide + book"; project-goal already proved the three checks work gate-side with no engine logic; keeps the engine judgment-free per run.md's "this is a rubric, not add.py"; the enforcement verb belongs to the dependent task `reopen-transition`) · ALSO add a mechanical structural audit backstop — a done coding-task §6 with the Deep-checks block unfilled becomes an `add.py audit` finding (rejected as the draft default, raised as the freeze ⚠: a presence-check is satisfied by any non-placeholder text including a plausible-but-false claim, so it buys appearance-of-enforcement not enforcement; the real failure mode — a fabricated wiring claim — is caught only by a reading resolver, which the conservative/human gate already is) · a new `add.py verify --deep` that runs the wiring/dead-code scan itself (rejected: the engine cannot judge wiring/dead-code/prose without a linter dependency — explicitly Scope Out of v20; the resolver runs the checks with its own tools and records the evidence)
Must:
<must>
  - the §6 VERIFY rubric in BOTH the skill guide (`phases/6-verify.md`) and the book (`docs/08-step-6-verify.md`) requires, for a task that produced code, recorded evidence that (a) every new symbol is referenced (wiring cross-check) and (b) no new dead/unused code was introduced
  - the same rubric requires, for a task that produced prose / non-code, a recorded semantic no-skim read (what was read in full · what it confirmed)
  - which path applies is RESOLVER-judged (the AI or human decides code vs prose); the engine never classifies, and `add.py` is byte-unchanged across all three engine copies (engine_pin ENGINE_MD5 unchanged)
  - the deepened requirement is stated IDENTICALLY across the guide, the book, and run.md's automated-quality-gate evidence list — one canonical wording, verbatim, no drift between surfaces
  - the §6 TASK.md template (`TASK.md.tmpl`, all three template copies byte-identical) gains an additive "Deep checks" block carrying the WIRING + DEAD-CODE (code) and SEMANTIC (prose) lines, fill-what-applies, inserted before the GATE RECORD; every pre-existing §6 checklist line is byte-unchanged (additive-evolution)
  - GLOSSARY defines the deepened-verify evidence as a single named term ("deep verify"), in both the living GLOSSARY and the template, so the rubric, the template, and the scenarios all use one name
  - every mirrored copy stays in parity: the dogfood skill (`.claude/skills/add/`) equals canonical (`add-method/skill/add/`); canonical equals the bundle (`_bundled/`); the four book copies (root `./`, `.add/docs/`, `add-method/docs/`, `_bundled/docs/`) stay byte-identical — `test_tree_parity` and `test_bundle_parity` stay green
</must>
Reject:
<reject>
  - the deep-check requirement appears in one surface but is missing from another (guide / book / run.md drift) -> "rubric_drift"
  - the §6 template change alters or removes any pre-existing checklist line (non-additive) -> "seam_broken"
  - a coding task records a gate PASS with the Deep-checks block left blank or as the `<…>` placeholder -> the rubric names this a shallow verify, not a pass -> "verify_shallow"  (a rubric-level situation the reading resolver / human gate catches; the engine is never asked to classify in this task)
</reject>
After:
<after>
  - the verify guide, the book, and run.md all carry the same deepened evidence requirement (code -> wiring + dead-code; prose -> semantic no-skim read), word-for-word on the canonical line; the §6 TASK.md template carries an additive Deep-checks block serving both paths with every prior line intact; GLOSSARY names the concept "deep verify"; `add.py` is byte-unchanged; all parity guards are green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the deepened verify is rubric + template ONLY, with NO mechanical engine backstop — lowest confidence because the v20 theme is "actually catch unwired / dead / skimmed code" and a bare checklist line risks the words-exist≠method-works gap prior deltas flagged; chosen lean because the milestone framing names prose surfaces ("stated identically in guide + book"), project-goal already gated successfully on these checks with no engine logic, a structural presence-check cannot catch a plausible-but-false claim anyway, and the enforcement verb belongs to the dependent task `reopen-transition`; if wrong: add the backstop later as a clean ADDITION — this is the freeze question (adding is a cleaner human decision than subtracting)
  ⚠ [spec] code-vs-prose is resolver-judged, not engine-classified — low confidence on whether you want the engine to KNOW a task's type; chosen resolver-judged to keep the engine judgment-free (run.md); if wrong: the type becomes a declared header field (like `risk:`), a larger change touching add.py
  - [ ] run.md's auto-gate evidence list is the right third surface to keep in sync (vs updating only guide + book) — high confidence: run.md's "Auto-PASS requires ALL of …" IS the evidence rubric; leaving it unchanged would create exactly the drift this task forbids
  - [ ] one umbrella GLOSSARY term ("deep verify") covers the evidence triad (wiring + dead-code + semantic) vs three separate terms — leaning one term; if wrong, split — cheap, the template lines already name each check
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a coding task's verify requires wiring + dead-code evidence
  Given the shipped verify guide and book
  When I read the §6 deep-check rubric
  Then it requires, for a task that produced code, recorded evidence that every new symbol is referenced and no new dead code was introduced
  And the pre-existing §6 checks (tests pass / coverage / security / architecture) are all still present

Scenario: a prose task's verify requires a semantic no-skim read
  Given the shipped verify guide and book
  When I read the §6 deep-check rubric
  Then it requires, for a prose / non-code task, a recorded semantic no-skim read (what was read in full · what it confirmed)
  And it states the resolver — not the engine — judges that the prose path applies

Scenario: the deepened rubric is stated identically across surfaces   # rubric_drift
  Given the shipped guide, book, and run.md
  When I extract the canonical deep-check line from each
  Then the same wording appears verbatim in all three
  And no surface omits it

Scenario: the §6 template carries an additive Deep-checks block   # seam_broken
  Given the shipped TASK.md template
  When I read its §6
  Then it has a "Deep checks" block with WIRING, DEAD-CODE, and SEMANTIC lines (fill-what-applies), inserted before the GATE RECORD
  And every pre-existing §6 checklist line is byte-unchanged

Scenario: an unfilled deep-check block is not a pass   # verify_shallow
  Given a coding task whose §6 Deep-checks block is left blank / placeholder
  When the resolver or human reviews the gate
  Then the rubric names it a shallow verify and the gate does not PASS on it
  And the catch is the reading resolver / human (the engine is never asked to classify)

Scenario: the evidence triad is a defined GLOSSARY term
  Given the shipped GLOSSARY (living and template)
  When I read it
  Then it defines "deep verify" as the deepened evidence (wiring + dead-code + semantic no-skim read)
  And the rubric and template use that name

Scenario: the engine is byte-unchanged
  Given the verify-deepen change set
  When I compare add.py across the three engine copies and the engine_pin md5
  Then add.py is unmodified and the pin is unchanged
  And the deepened verify is delivered as rubric + template, not engine logic

Scenario: every mirrored copy stays in parity
  Given the change applied to the canonical trees and synced
  When test_tree_parity and test_bundle_parity run
  Then the dogfood skill equals canonical, canonical equals the bundle, and the four book copies are byte-identical
  And the suite is green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DEEP-VERIFY RUBRIC — the frozen canonical line (must appear VERBATIM in 3 surfaces):

  surfaces (each on its §6 / auto-gate evidence list, all mirrored copies kept in parity):
    guide   .claude/skills/add/phases/6-verify.md     (+ add-method/skill + _bundled)
    book    .add/docs/08-step-6-verify.md             (+ root ./ + add-method/docs + _bundled)
    rubric  .claude/skills/add/run.md                 (+ add-method/skill + _bundled)

  canonical wording (frozen — this exact sentence is the drift sentinel):
    "Deep check — do not skim. If the task produced code, record that every new symbol is
     referenced (wiring) and that no new dead/unused code was introduced. If it produced prose
     or non-code, record a semantic read — what you read in full and what it confirmed. Which
     path applies is the resolver's judgement; the engine never classifies."

§6 TASK.md TEMPLATE — additive block (3 template copies byte-identical), inserted immediately
  BEFORE "### GATE RECORD"; every existing §6 line byte-unchanged:

    ### Deep checks — do not skim (fill the path that applies; the resolver judges which)
    - [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
    - [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
    - [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

GLOSSARY term (living .add/GLOSSARY.md + GLOSSARY.md.tmpl triplet):
    deep verify: the deepened Verify evidence (v20) beyond passing tests — for code, that every new
    symbol is wired and no new dead code exists; for prose/non-code, a recorded no-skim semantic
    read; resolver-judged which path applies, engine-uninvolved.

ENGINE: add.py byte-unchanged across all three copies; engine_pin ENGINE_MD5 unchanged.
PARITY: test_tree_parity (skill live↔canonical) and test_bundle_parity (canonical↔bundle) green.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08 (lean scope chosen: rubric + §6 template, add.py byte-unchanged; the mechanical backstop is deferred — enforcement belongs to reopen-transition. Both ⚠ flags accepted.)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag.
     ⚠ [contract] — the #1 flag: this bundle draws verify-deepen LEAN — rubric + §6 template only,
        NO mechanical engine backstop. project-goal already gated successfully on exactly these
        checks (wiring via serena, dead-code scan, semantic re-read) with zero engine logic, and the
        milestone framing says "stated identically in guide + book" (prose, not add.py). The open
        question put in front of you: should verify-deepen ALSO carry a structural audit backstop, or
        does enforcement belong to the dependent task reopen-transition? Cost if wrong: a clean later
        ADDITION (not a subtraction). Approve lean, or say "add the backstop" and I fold it in pre-freeze.
     ⚠ [spec] — secondary: code-vs-prose is resolver-judged, not engine-classified (keeps the engine
        judgment-free); if you want the engine to know task type it becomes a declared header field.
     Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen contract = change
     request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: structural — every surface, the template block, the GLOSSARY term, and the engine-unchanged + parity invariants. (Honest limit: for a prose+template task the strongest mechanizable test is string-presence + verbatim-drift detection; the real proof is the human read at the freeze + this task's own §6 deep-check run on itself — recorded, not skimmed.)
Plan (one test per scenario, asserting the shipped artifact not internals):
<test_plan>
  - test_guide_has_deepcheck_rubric: read phases/6-verify.md / assert the canonical deep-check wording (code -> wiring + dead-code; prose -> semantic) is present
  - test_book_has_deepcheck_rubric: read docs/08-step-6-verify.md / assert the same canonical wording is present
  - test_runmd_autogate_has_deepcheck: read run.md / assert the auto-gate evidence list carries the deep-check requirement
  - test_rubric_stated_identically: extract the canonical drift-sentinel sentence / assert it appears VERBATIM in guide AND book AND run.md (rubric_drift)
  - test_template_has_deepchecks_block: read TASK.md.tmpl §6 / assert a "Deep checks" block with WIRING, DEAD-CODE, SEMANTIC lines, positioned before "### GATE RECORD"
  - test_template_deepchecks_additive: assert every pre-existing §6 line (the 7 known checklist lines + GATE RECORD) still present byte-for-byte in TASK.md.tmpl (seam_broken)
  - test_template_triplet_identical: assert the 3 TASK.md.tmpl copies are md5-identical
  - test_glossary_defines_deep_verify: assert living .add/GLOSSARY.md AND GLOSSARY.md.tmpl define "deep verify"
  - test_engine_unchanged: assert md5(add.py) == engine_pin.ENGINE_MD5 AND no "Deep check"/"WIRING" token leaked into add.py (verify-deepen added no engine code)
  - test_verify_shallow_named: assert the guide states an unfilled deep-check block is not a pass (the verify_shallow rubric situation is written)
</test_plan>

Tests live in: `add-method/tooling/test_verify_deepen.py` · MUST run red (the wording / block / term do not exist yet) before Build.
<!-- real path, not `./tests/`: this dogfood task ships its suite beside the engine it guards (matches project-goal's §4); the `_declared_tests_count` audit resolves a `/`-token from project root and counts the real file. -->

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

- [x] all tests pass — 595 → 605 green (10 new verify-deepen tests, 0 regressions)
- [x] coverage did not decrease — every new surface / term / invariant is exercised by a test
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the one test edit (`_norm` whitespace-normalize) fixed a markdown-hard-wrap matching bug, NOT a weakening — it makes the drift sentinel test word-sequence identity, which is exactly the contract's "stated identically"
- [x] concurrency / timing — N/A: prose + template edits and read-only file-presence tests; no shared mutable state
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (ast/hashlib/unittest/pathlib); no new import in add.py (engine byte-unchanged)
- [x] layering & dependencies follow CONVENTIONS.md — additive-evolution (every prior §6 line byte-unchanged), engine judgment-free (no add.py logic), all parity guards green
- [x] a person reviewed and approved the change — Tin Dang, conservative gate, 2026-06-08 (the 2 test edits affirmed as corrections)

### Deep checks — do not skim (the first task to run the rubric it built, on itself)
- [x] SEMANTIC (prose / non-code — the primary deliverable) — read in full, not skimmed: the canonical deep-check wording is present and normalized-identical across guide `phases/6-verify.md` (Part three), book `docs/08-step-6-verify.md` (Part three + checklist), and `run.md` (auto-gate bullet) — all 4 anchors verbatim (test_rubric_stated_identically); the §6 template block is additive (7 prior lines intact, block before GATE RECORD); "deep verify" defined in template + living GLOSSARY. Confirmed by reading each edit, not just the test pass.
- [x] WIRING (code — the test file) — `_md5` and `_norm` are both referenced; all 10 test methods are collected + run by unittest discovery (605 total); no unused import (AST scan). CAUGHT a real defect: §4 declared `./tests/` (empty) so `_declared_tests_count` reported **0** while the real suite lives in `tooling/`; fixed §4 to the real path (matches project-goal's pattern), audit now counts **10** — the wiring check working on this task's own test declaration.
- [x] DEAD-CODE — the scan CAUGHT one: `import add` was imported-but-unused; removed before this gate (the deep check working on its own deliverable). Remaining: clean.
- [x] SECURITY — no finding (else mandatory HARD-STOP). Read-only file reads; no secrets / injection / network; no new dependency; add.py md5 == engine_pin (54f54e3…).

### GATE RECORD
Outcome: PASS (conservative, human-gated — Tin Dang owned the gate; the 2 test edits affirmed as corrections, not weakenings)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `test_rubric_stated_identically` is the live drift monitor — any future edit to one prose surface (guide/book/run.md) that doesn't update the others trips `rubric_drift`. `test_engine_unchanged` watches for deep-verify logic leaking into add.py. A future task gating with an unfilled Deep checks block = a shallow verify the resolver must reject.
Spec delta for the next loop: the rubric is judgement-only (the engine never classifies code-vs-prose). reopen-transition may add a *mechanical backstop* — refuse a gate whose §6 Deep checks block is empty — now that the block exists in the template; that enforcement was deliberately deferred out of this lean task.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the deep-check has teeth: its WIRING path caught a real defect on its OWN task — §4 declared `./tests/` (empty) so `_declared_tests_count` reported 0 while the real 10-test suite lived in `tooling/`; fixed pre-gate (evidence: count 0 → 10). A plausible-looking §4 can silently count zero tests.
- [ADD · folded] reopen-transition AND dynamic-task-loop TASK.md were scaffolded from the pre-v20 template — they carry NO §6 Deep checks block; each must gain it when it reaches verify, else it gates without the rubric it is downstream of (evidence: both files predate this task's template edit).
- [TDD · folded] a drift sentinel across hard-wrapped prose surfaces needs whitespace-normalized matching, not byte-equality — "stated identically" means same wording, and each surface wraps at its own column (evidence: `_norm` added so the long anchor matches across guide/book/run.md line-wraps while different words still fail).
