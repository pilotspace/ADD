# TASK: minimal TASK.md template + fallback

slug: fast-lane-template · created: 2026-06-23 · stage: mvp
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

Touches (files · symbols · signatures): `.add/tooling/templates/TASK.fast.md.tmpl` (NEW — the minimal variant) · `add.py:_FALLBACK_TASK` (119, embedded circuit-breaker — needs a fast analog `_FALLBACK_TASK_FAST`) · `add.py:_render_template` (237, loads `templates/<name>.tmpl`, falls back for TASK.md only) · `add.py:_templates_dir` (233).
Context (working folder): the full `templates/TASK.md.tmpl` (170 lines, 9 numbered sections) is the baseline this shrinks; `tests/` is where the section-count + floor-retention guards land.
Honors (patterns / conventions): minimal-template floor (frozen contract + gate record always survive) · collapse-never-skip (the three non-negotiables preserved) · circuit-breaker parity (`_FALLBACK_*` mirrors the file template so a deleted `templates/` never hard-fails).
Anchors the contract cites: `_phase_spans` (4015, keys §N by NUMBER — a subset parses) · `task_phases` (4052, absent §→"(empty)", fail-closed) · `_flag_well_formed` (4362, FROZEN §3 needs the freeze-flag line) · `_stamp_gate_record` (584, §6 `### GATE RECORD`/`Outcome:`) · `_grounded_state`/`_section0_anchors` (4335/4325, §0 Anchors line).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the minimal "fast lane" TASK.md template — a file `TASK.fast.md.tmpl` + its embedded `_FALLBACK_TASK_FAST` analog — a strict SUBSET of the full template that still freezes a contract and records a gate.
Framings weighed: separate fast template file + fallback analog (chosen — additive, the full template is byte-untouched, render picks by name) · single template with conditional section-stripping at render (rejected — couples the two shapes, more code in _render_template) · same 9 headers terse-filled (rejected — that is approach (b); does not deliver "fewer sections")
Must:
<must>
  - keep a SUBSET of the full template's numbered sections — retain {0,1,3,4,5,6}, drop §2 SCENARIOS and §7 OBSERVE as standalone sections (the single acceptance scenario folds into §1 as an `Accept:` line; an OBSERVE delta is a one-line option the guide adds only when there is a lesson)
  - RETAIN the trust-floor seams: §3 carries the `Least-sure flag surfaced at freeze:` line (so a FROZEN fast task passes `_flag_well_formed`) · §6 carries `### GATE RECORD` + `Outcome:` (so `_stamp_gate_record` mirrors the verdict) · §0 carries the `Anchors the contract cites:` line (so `_grounded_state` still measures) · §4 keeps the red-before-build note · §5 keeps a one-line `Scope (may touch):` (so scope-gate still has a declaration)
  - parse cleanly under `_phase_spans`: every retained heading is `## N ·` numbered and sections ascend 0→6 (no gap breaks the scan)
  - the §6 "Build expectations" prose references §1 `Accept:` + §3 CONTRACT (NOT "§2 SCENARIOS", which the fast template drops)
  - carry the full template's substitution tokens ({{title}} {{slug}} {{date}} {{stage}} {{autonomy}}) + a `fast: true` header marker line
  - `_FALLBACK_TASK_FAST` mirrors the file template's section set (circuit-breaker parity — a deleted templates/ never hard-fails the fast lane)
  - be materially smaller: strictly fewer sections (6 < 9) AND substantially fewer lines than `TASK.md.tmpl`
</must>
Reject:
<reject>
  - a fast template missing §3 CONTRACT or §6 GATE RECORD -> "missing_floor" (violates retrieve+persist)
  - a retained section heading unnumbered or out of ascending order -> "malformed_sections" (breaks `_phase_spans`)
  - `_FALLBACK_TASK_FAST` section set diverging from the file template -> "fallback_drift"
</reject>
After:
<after>
  - `templates/TASK.fast.md.tmpl` exists, renders via `_render_template("TASK.fast.md", …)`, and a scaffolded fast TASK.md shows §3 + §6 with fewer total sections than the full one
  - the kept-section set + must-retain lines are pinned by a test so the floor cannot silently regress
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ dropping §2 SCENARIOS + §7 OBSERVE as standalone sections is safe — lowest confidence because a guard or a downstream phase guide may ASSUME §2 content for a path a fast task also traverses (the §6 Build-expectations prose literally cites "§2 SCENARIOS"); if wrong: a fast task trips a guard at freeze/verify and the kept-section set must be re-frozen. Mitigation: ground mapped every gate guard (`_flag_well_formed`/§3 · `_stamp_gate_record`/§6 · grounding/§0) — none read §2/§7; the only coupling found is the Build-expectations wording, fixed in the fast template itself.
  - [ ] §5 Scope is worth keeping (vs folding into §4) — keeping it preserves the scope-gate declaration for one cheap line; deny only if a fast task should be scope-gate-exempt
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: subset section set — drops §2 and §7, keeps the rest
  Given the fast template TASK.fast.md.tmpl
  When _phase_spans parses it
  Then the returned section numbers are exactly {0,1,3,4,5,6}
  And §2 and §7 are absent

Scenario: trust-floor seams retained
  Given the fast template text
  When scanned for the floor markers
  Then it contains the "Least-sure flag surfaced at freeze:" line (§3)
  And it contains "### GATE RECORD" and an "Outcome:" line (§6)
  And it contains the "Anchors the contract cites:" line (§0)
  And §4 keeps the red-before-build note and §5 keeps a "Scope (may touch):" line

Scenario: parses + renders cleanly
  Given the fast template
  When rendered via _render_template("TASK.fast.md", …) and parsed by task_phases
  Then no "{{…}}" substitution token remains
  And task_phases returns without error (absent sections render "(empty)")
  And a "fast: true" header marker line is present

Scenario: build-expectations cites the kept sections
  Given the fast template §6 "Build expectations" prose
  When read
  Then it references §1 Accept and §3 CONTRACT
  And it does NOT reference "§2 SCENARIOS"

Scenario: fallback mirrors the file template (circuit-breaker parity)
  Given _FALLBACK_TASK_FAST and TASK.fast.md.tmpl
  When their section-number sets are compared
  Then they are equal

Scenario: materially smaller than the full template
  Given TASK.fast.md.tmpl and TASK.md.tmpl
  When their sections and lines are counted
  Then the fast template has strictly fewer sections (6 < 9)
  And substantially fewer lines

Scenario: REJECT missing_floor — no §3 or no §6
  Given a candidate fast template missing §3 CONTRACT or §6 GATE RECORD
  When the floor guard checks it
  Then it reports "missing_floor"
  And the shipped template is unchanged (still has §3 and §6)

Scenario: REJECT malformed_sections — heading unnumbered/out of order
  Given a retained heading that is not "## N ·" or breaks ascending order
  When _phase_spans scans it
  Then the expected {0,1,3,4,5,6} set is NOT produced
  And the guard flags "malformed_sections"

Scenario: REJECT fallback_drift — fallback section set diverges
  Given _FALLBACK_TASK_FAST with a section set != the file template's
  When the parity guard compares them
  Then it reports "fallback_drift"
  And neither artifact is silently accepted
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  templates/TASK.fast.md.tmpl   (NEW file)  +  add.py:_FALLBACK_TASK_FAST   (NEW constant)
RENDER    _render_template("TASK.fast.md", title=…, slug=…, date=…, stage=…, autonomy=…)
          -> file template if present, else _FALLBACK_TASK_FAST  (mirrors the TASK.md fallback branch)

FROZEN STRUCTURE (the checkable seam):
  kept-section set      : exactly { 0, 1, 3, 4, 5, 6 }   (DROPPED: 2 SCENARIOS, 7 OBSERVE)
  section ordering      : ascending; every heading is "## N · NAME" (parses under _phase_spans)
  header                : line1 "# TASK: {{title}}" · "slug: {{slug}} · created: {{date}} · stage: {{stage}}"
                          · "autonomy: {{autonomy}}" · "phase: ground" · "fast: true"   (the lane marker)
  §0 GROUND floor       : an "Anchors the contract cites:" line   (feeds _grounded_state)
  §1 SPECIFY floor      : "Feature:" · "Must:" · "Reject:" · one "Accept:" line (the folded scenario)
                          · a "⚠" lowest-confidence assumption line
  §3 CONTRACT floor     : a shape block · "Status: DRAFT" · the
                          "Least-sure flag surfaced at freeze:" line   (feeds _flag_well_formed)
  §4 TESTS floor        : a "MUST run red … before Build" note  (red-before-build preserved)
  §5 BUILD floor        : a "Scope (may touch):" line           (scope-gate declaration preserved)
  §6 VERIFY floor       : "### GATE RECORD" + "Outcome:" + "Reviewed by:" lines
                          (feeds _stamp_gate_record) · a "Build expectations" note citing §1 Accept + §3
  parity               : set(section numbers in _FALLBACK_TASK_FAST) == set(file template's)
  size                 : sections 6 < 9  AND  line-count substantially < TASK.md.tmpl

REJECTS (guard codes, pinned by tests):
  missing_floor        -> §3 CONTRACT or §6 GATE RECORD absent
  malformed_sections   -> a heading not "## N ·" or sections not ascending (breaks _phase_spans)
  fallback_drift       -> _FALLBACK_TASK_FAST section set != file template section set

OUT OF SCOPE (this task): the `--fast` flag + cmd_new_task wiring + check/audit tolerance
  (owned by fast-new-task-flag); this task ships only the template artifact + fallback + its guards.
```

Least-sure flag surfaced at freeze: [spec/contract] the frozen kept-section set {0,1,3,4,5,6} — dropping §2 + §7 is the bet most likely to be wrong; if a downstream guide/guard assumes §2 content for a path a fast task traverses, the set must be re-frozen. Ground refuted the gate-guard half (none read §2/§7); the residual risk is a phase GUIDE assumption, accepted (the fast-lane-guide task owns folding scenarios into §1 Accept).

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every frozen-structure invariant (kept-set · floor markers · render · fallback parity · size · reject guards) pinned — not a % (a static artifact).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - FastTemplateExists: file in all 3 trees, byte-identical
  - SubsetSectionSet: _phase_spans -> {0,1,3,4,5,6}; §2/§7 absent; headings ascend
  - TrustFloorRetained: freeze-flag · GATE RECORD/Outcome/Reviewed · §0 Anchors · §4 red-before-build · §5 Scope
  - HeaderAndRender: `fast: true` marker · no {{token}} left · task_phases fail-closed "(empty)" for §2/§7
  - BuildExpectationsWording: cites §1 Accept + §3, not "§2 SCENARIOS"
  - FallbackParity: _FALLBACK_TASK_FAST exists · section set == file · used when file absent
  - MateriallySmaller: 6 sections < 8 · lines < 60% of full
  - RejectGuards: missing_floor · malformed_sections · fallback_drift detected
</test_plan>

Tests live in: `add-method/tooling/test_fast_lane_template.py` · MUST run red (missing implementation) before Build.
RED confirmed: 25 tests, failures=5 errors=18 — all because TASK.fast.md.tmpl + add._FALLBACK_TASK_FAST do not exist yet (the right reason).
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/TASK.fast.md.tmpl` `.add/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. author TASK.fast.md.tmpl (canonical) 2. add `_FALLBACK_TASK_FAST` + extend `_render_template` fallback branch for "TASK.fast.md" in add.py 3. mirror both into the dogfood + bundle trees (byte-identical) 4. re-pin engine_pin md5 5. green the suite.
Safety rule (feature-specific): the 3 add.py trees + the 3 template trees stay byte-identical (parity); the full TASK.md.tmpl is byte-untouched.
Code lives in: `add-method/tooling/` (+ the 2 mirror trees).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1614 (was 1589 + 25 new)
- [x] coverage did not decrease — the new constant + render branch + template are fully exercised by the 25 tests
- [x] no test or contract was altered during build — only §5-declared files changed (git status confirms); §3 FROZEN @ v1 + the red suite untouched post-freeze
- [x] the green was EARNED, not gamed — tests assert real structure via the engine's OWN `_phase_spans` (not string fixtures), render produces zero `{{}}`, reject-guards construct synthetic malformed inputs and assert detection; no overfit/vacuous/stubbed asserts
- [x] concurrency / timing — n/a (a static template + a pure dict-lookup render branch; no shared state, no IO ordering)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (a dict literal + str.replace); add.py diff +45/-3, no new import
- [x] layering & dependencies follow CONVENTIONS.md — circuit-breaker parity preserved (`_FALLBACK_*` mirrors the file template); 3-tree byte-identity held
- [x] a person reviewed and approved the change — the freeze was human-approved (Tin Dang); this gate presented before recording

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §1 Accept
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green.
- [x] `add._render_template("TASK.fast.md", …)` returns a rendered minimal TASK.md with §3 + §6 and no `{{}}` left — confirmed by HeaderAndRender (test_no_substitution_token_remains)
- [x] the fast template parses to exactly sections {0,1,3,4,5,6} under `_phase_spans`, materially fewer than the full 8, lines < 60% — confirmed by SubsetSectionSet + MateriallySmaller
- [x] the trust floor survives (freeze-flag · GATE RECORD/Outcome/Reviewed · §0 Anchors · §4 red-before-build · §5 Scope) — confirmed by TrustFloorRetained
- [x] a deleted `templates/` still yields a floor-complete fast template via `_FALLBACK_TASK_FAST` — confirmed by test_fallback_used_when_file_absent

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_FALLBACK_TASK_FAST` referenced in `_render_template` (add.py:284, the `_fallbacks` map); the template loads via `_render_template("TASK.fast.md")`
- [x] DEAD-CODE (code) — no orphan: the constant's only reach is the file-absent circuit-breaker (covered) and the file is the normal path
- [x] SEMANTIC (prose) — read the rendered minimal template in full: 53 lines, §0/§1/§3/§4/§5/§6 present, floor markers intact, no `§2 SCENARIOS` reference

### Disclosure (honest, non-blocking)
- The §3 parenthetical "6 < 9" is a stale descriptive integer — the full template has 8 numbered sections (§0–§7); "9" counted the `done` phase. The BINDING seam (kept set {0,1,3,4,5,6}) is correct and unambiguous; tests assert the true 6 < 8. Per the foundation convention (a frozen DESCRIPTIVE annotation may be wrong while the seam holds — disclose at verify, don't silently retrofit), surfaced here rather than edited into the frozen contract.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · folded] a minimal TASK.md can drop sections SAFELY because `_phase_spans` keys §N by NUMBER and `task_phases` fails closed to "(empty)" — so the engine tolerates a subset with no parser change; the trust floor reduces to two seams the gate guards actually read (§3 freeze-flag for `_flag_well_formed`, §6 GATE RECORD for `_stamp_gate_record`) plus the grounding/scope/red-test lines (evidence: ground refuted the drop-risk; 25 tests + full 1614 green with §2/§7 absent). [folded foundation-version 48]
  - [ADD · folded] the "minimal-template floor" = frozen-contract + gate-record: those are the two sections that make a task RETRIEVABLE (intent/contract) and TRUSTED (the proof) in a later session; everything else is collapsible ceremony (evidence: fast-lane-template kept exactly these as non-droppable). [folded foundation-version 48]
  - [SDD · folded] a frozen DESCRIPTIVE parenthetical can mis-count while the binding SEAM holds — "6 < 9" vs the true "6 < 8" (the §3 set {0,1,3,4,5,6} is unambiguous); disclose at verify, don't retro-edit the frozen contract (evidence: tests assert 6 < 8; disclosed in §6). [folded foundation-version 48]
