# TASK: host the persona-owned gate as a text-mode UDD artifact — fold report-template into the UDD family + a lightweight gate loop

slug: gate-experience-udd · created: 2026-07-16 · stage: mvp · risk: high
milestone: strategy-intake
autonomy: conservative
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: host the persona-owned gate as a text-mode UDD artifact — physically fold report-template.md into the UDD family (rename → gate-udd.md) + a lightweight text-mode gate loop in design.md
Framings weighed: PHYSICAL rename + migrate every reference (chosen, human-picked) · a conceptual fold keeping the path (rejected by human) · a new gate-loop guide (rejected — pool rebaseline)
Must:
<must>
  - M1 report-template.md is RENAMED to gate-udd.md across all 3 skill trees (canonical · .claude/skills/add · _bundled) — a real git-tracked rename, byte-parity preserved across the trees
  - M2 gate-udd.md opens by declaring it the TEXT-MODE UDD gate surface — a member of the UDD doc family — and cross-links design.md as its design home; its report PRINCIPLES + the four floors (show-before-ask · one-approval · never-pre-stamp · security-HARD-STOP) are preserved verbatim in substance (the fold relocates, never weakens)
  - M3 design.md's UDD loop gains a LIGHTWEIGHT text-mode gate variant: when the experience surface is a human GATE, run intake-the-INTERACTION-axis → design the report (per gate-udd.md) → confirm; NO wireframe / render-capture beat. Names gate-udd.md as the gate's design reference
  - M4 EVERY reference to report-template.md is repointed to gate-udd.md — the 9 skill guides (SKILL.md · loop.md · scope.md · graduate.md · release.md · intake.md · phases/{0-setup,3-plan,6-verify}.md) ×3 trees, the 2 book docs (02-the-flow.md · appendix-c-glossary.md), the 16 tests (path constants · content assertions · the test_skill_lean reference-pool list · the test_report_shape_scan_audit byte pin) — no dangling pointer survives
  - M5 no add.py edit, no ENGINE_MD5 repin; SKILL.md stays < 9500 B; the pool ceilings hold (the rename SHRINKS pools by −7 B/occurrence; design.md's added block offsets within orchestration-pool headroom, compress-not-rebaseline)
</must>
Reject:
<reject>
  - R1 any report-template.md reference left unmigrated — a dangling pointer to a file that no longer exists -> "dangling_gate_ref"
  - R2 a historical TASK-NAME string (report-template-recorded-loop · report-shape-scan-audit, in test ledger comments) corrupted by an over-eager blanket replace -> "taskname_corrupted"
  - R3 any of the four floors or the persona-owned report principles weakened or dropped during the move -> "floors_lost"
</reject>
After:
<after>
  - report-template.md no longer exists; gate-udd.md is its renamed home in the UDD family, opening as the text-mode UDD gate surface + cross-linking design.md; design.md carries the lightweight text-mode gate variant; every guide/doc/test points at gate-udd.md; the four floors intact; add.py untouched; the full engine suite green
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the NEW NAME gate-udd.md — CONFIRMED by tindang at the freeze (chosen over gate-experience.md / gate-design.md); the rename target + every migrated reference key off it, now settled
  - [ ] the token to migrate is the .md-suffixed filename `report-template.md` (+ the SKILL.md bare `report-template` pointer), NEVER the historical task-name substrings — confirm each replace is filename-scoped, not a blind global sed (R2 guards this)
  - [ ] the reference pool absorbs gate-udd.md's ~200 B reframe header after the rename's −7 B/occurrence savings — confirm at build against the 51885 ceiling; compress-not-rebaseline if tight
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: report-template.md is renamed to gate-udd.md in all 3 trees   # M1
  Given the skill after this task
  When I look for report-template.md and gate-udd.md
  Then report-template.md does not exist in any of the 3 skill trees
  And gate-udd.md exists in all 3, byte-identical across them

Scenario: gate-udd.md is framed as the text-mode UDD gate surface   # M2, R3
  Given gate-udd.md after the rename
  When I read its opening + its floors block
  Then it declares itself the text-mode UDD gate surface and cross-links design.md
  And the four floors (show-before-ask · one-approval · never-pre-stamp · security-HARD-STOP) are all still present
  And the persona-owned report principles are unchanged in substance

Scenario: design.md carries the lightweight text-mode gate variant   # M3
  Given design.md after this task
  When I read the UDD loop
  Then it defines a text-mode gate variant (intake INTERACTION axis → design report → confirm) with no wireframe/capture beat
  And it names gate-udd.md as the gate's design reference

Scenario: no reference to report-template.md dangles   # M4, R1
  Given the whole tree (guides · book docs · tests) after this task
  When I grep for the token report-template.md
  Then no skill guide, book doc, or test references report-template.md as a live file pointer
  And every former reference now names gate-udd.md

Scenario: historical task-name strings are preserved   # R2
  Given the test ledger comments after the migration
  When I grep for report-template-recorded-loop and report-shape-scan-audit
  Then those historical task-name substrings are intact (not corrupted to gate-udd-*)

Scenario: the engine is untouched   # M5
  Given add.py and the ENGINE_MD5 after this task
  When I diff add.py against main and check SKILL.md size
  Then add.py is unchanged (ENGINE_MD5 4e65596…) and SKILL.md is < 9500 B
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add-method/skill/add/report-template.md` (→ rename gate-udd.md; 9514 B; headings `# Chat reports…` · `## The four floors…` · `<constraints>`) · `add-method/skill/add/design.md` (the UDD loop `## The loop — five beats` + hard-rules `<constraints>` — gains the text-mode gate variant) · 9 guides carrying a `report-template.md` prose pointer: `SKILL.md` (L98,100) · `loop.md` (L52) · `scope.md` (L37) · `graduate.md` (L22) · `release.md` (L27) · `intake.md` (L45,47) · `phases/6-verify.md` (L48) · `phases/0-setup.md` (L80) · `phases/3-plan.md` (L48) — ALL ×3 skill trees. 2 book docs: `add-method/docs/02-the-flow.md` (L95) · `add-method/docs/appendix-c-glossary.md` (L59,61). 16 tooling tests keying the path/name (path constants `CANON/"report-template.md"`, `assertIn("report-template", skill)` pointer checks, the `test_skill_lean.py` reference-pool list L64, the `test_report_shape_scan_audit.py` byte pin `== 9514` L88). NO add.py symbol.
Context (working folder): the UDD doc family (design.md is the sibling design home; udd-tokens.md/udd-catalog.md book chapters are the data-contract members — not in the write-set); the persona-owns-gates reframing that made report-template.md persona-owned PRINCIPLES (this task relocates that content, unchanged, into the UDD family).
Honors (patterns / conventions): the 3-skill-tree byte-parity (a rename must move all 3 copies) · the SKILL.md 9500 B ceiling · engine-minimalism / compress-not-rebaseline (`feedback_lean_over_budget_bump`) · the four report floors stay (security = HARD-STOP the un-persona-negotiable one) · UDD's ethos (the gate is now a designed experience surface) · the historical-task-name convention in test ledger comments (never corrupt them).
Seams consulted: none (no scope-token grammar or add.py line anchor; the migration is filename-scoped).
Anchors the contract cites: report-template.md's headings + four-floors block + `<constraints>` · design.md's `## The loop — five beats` + hard-rules `<constraints>` · the 9 guide pointer lines · the 2 book-doc lines · test_skill_lean.py's reference-pool list + test_report_shape_scan_audit.py's `9514` byte pin (the migration targets).
Issues/Risks: the migration is LARGE (≈30 skill-file edits ×3 trees + 16 tests + 2 docs) but MECHANICAL — the risk is a MISSED reference (R1 dangling) or an OVER-eager replace corrupting a historical task-name (R2). Filename-scoped replace (`report-template.md`) + the two SKILL.md bare pointers, verified by a whole-tree grep, contains both. The `9514` byte pin migrates to gate-udd.md's new count (reframe header added). design.md's added block is bounded by orchestration-pool headroom (774 B; the rename's −7 B/occurrence savings help). Method-defining (risk: high).
Related intent: the strategy-intake UDD-redefine decisions (2026-07-16) — decision 2 (report-template FOLDS into the UDD family, human-picked PHYSICAL rename) + decision 3 (LIGHTWEIGHT text-mode gate loop, human-picked home = design.md) · the `[SPEC · seeded]` gate-experience-udd delta from persona-owns-gates + udd-experience-pillar · GLOSSARY "experience-driven development".
Ground SHA: 53f8b00 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
The physical fold of the gate report into the UDD doc family:

  RENAME (git-tracked, ×3 skill trees — canonical · .claude/skills/add · _bundled):
    report-template.md -> gate-udd.md   (byte-identical across the 3 trees)

  gate-udd.md CONTENT: report-template.md's body is preserved; its opening is reframed to
    declare it the TEXT-MODE UDD GATE SURFACE — a member of the UDD doc family — cross-linking
    design.md as the gate's design home. The four floors block (show-before-ask · one-approval ·
    never-pre-stamp · security = HARD-STOP the un-persona-negotiable floor) and the persona-owned
    report PRINCIPLES stay verbatim in substance.

  design.md UDD loop gains a LIGHTWEIGHT TEXT-MODE GATE VARIANT: when the experience surface is a
    human GATE, run — intake the INTERACTION axis (cadence · when/how to seek the human) -> design
    the report shape (per gate-udd.md) -> confirm. NO wireframe / render-capture beat. Names gate-udd.md.

  REPOINT every report-template.md reference -> gate-udd.md:
    9 guides ×3 trees (SKILL.md · loop.md · scope.md · graduate.md · release.md · intake.md ·
      phases/{0-setup,3-plan,6-verify}.md) · 2 book docs (02-the-flow.md · appendix-c-glossary.md)
    · 16 tooling tests (path constants · pointer assertions · test_skill_lean reference-pool list ·
      test_report_shape_scan_audit byte pin 9514 -> gate-udd.md's new count).

Invariants (HARD):
  - report-template.md does NOT exist after this task; gate-udd.md is its renamed home
  - the four floors + persona-owned principles are preserved in substance (never weakened) -> R3 floors_lost
  - NO report-template.md reference dangles -> R1 dangling_gate_ref
  - historical task-name substrings (report-template-recorded-loop · report-shape-scan-audit) intact -> R2 taskname_corrupted
  - no add.py edit, no ENGINE_MD5 repin; SKILL.md < 9500 B; 3 skill trees byte-identical
```

Glossary deltas: gate-udd (the gate as a UDD artifact): the persona-owned human-gate report, framed as the text-mode member of the UDD doc family — designed through the UDD lens (the INTERACTION axis + a confirm), the renamed home of report-template.md. text-mode gate variant: design.md's lightweight UDD loop for a human gate — intake INTERACTION → design report → confirm, no wireframe/capture beat.
Least-sure flag surfaced at freeze: the migration completeness — whether a filename-scoped `report-template.md`→`gate-udd.md` replace (+ the two bare SKILL.md pointers) catches EVERY live reference across ≈30 skill files + 16 tests + 2 docs without corrupting a historical task-name substring; a red test asserts zero dangling `report-template.md` + intact task-names, and a whole-tree grep at build proves it; if a reference hides in an un-grepped form, a test reddens (contained, not silent) [test/contract]
Status: FROZEN @ v1 — approved by tindang
Reported: yes — the freeze report (banner/ARC/SHAPE + the full blast-radius map) rendered before this froze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/skill/add/` `.claude/skills/add/` `add-method/src/add_method/_bundled/skill/add/` `add-method/docs/` `add-method/src/add_method/_bundled/docs/` `add-method/../02-the-flow.md` `add-method/../appendix-c-glossary.md` `add-method/tooling/`
Strategy (ordered batches): 1. git mv report-template.md → gate-udd.md in all 3 trees 2. reframe gate-udd.md's opening as the text-mode UDD gate surface + design.md cross-link (body preserved) 3. add design.md's lightweight text-mode gate variant block (×3 trees, byte-identical) 4. filename-scoped repoint `report-template.md`→`gate-udd.md` + the two SKILL.md bare `report-template` pointers across the 9 guides ×3 trees + 2 book docs 5. migrate the 16 tests (path constants · pointer assertions · reference-pool list · byte pin) — filename-scoped, preserving historical task-name substrings 6. write test_gate_experience_udd.py (rename-happened · gate-udd-is-UDD-surface · four-floors-intact · design.md-gate-variant · no-dangling-ref · task-names-intact · engine-untouched) RED first 7. run the FULL engine suite green + `add.py check`
Approach (domain strategy): a filename-scoped MECHANICAL migration (git mv + `report-template.md`→`gate-udd.md`), NOT a blind global sed — the `.md` suffix + the two known bare SKILL.md pointers are the only live-file references; historical task-name substrings lack the `.md` and are left untouched (R2). A whole-tree `grep report-template.md` at the end proves zero dangling (R1). Chosen over a conceptual fold because the human picked the physical rename.
Data strategy: three parallel skill trees kept byte-identical (md5 parity) for gate-udd.md + design.md — the same twin-parity shape as prior skill-doc tasks; the byte pin migrates forward with a ledger note (report-template convention).
Pattern: the 3-skill-tree parity + pool ceilings (engine-minimalism); the forward-migrated byte-ledger pin of test_report_shape_scan_audit.py; the historical-task-name-preservation convention of the test ledger comments.
Optimization stance: correctness-of-migration first (zero dangling, zero task-name corruption); token cost second — the rename SHRINKS pools (−7 B/occurrence), design.md's added block offsets within orchestration-pool headroom (⚠ the facet trusted least: design.md's 774 B headroom is tight — if the gate-variant block overflows, compress same-guide, never rebaseline).
Persona (required): terminal-ux-accessibility (the gate is a text-mode UX surface — its design stance owns "the gate as experience") — advisory, never lowers a gate.
Spawn isolation (default): inline (sequential mechanical edits across many files; user prefers inline over heavy spawns) — a review subagent MAY verify the large diff at verify (Rule 5).
Known-problem fixes: a missed reference → R1 dangling_gate_ref (whole-tree grep catches it) · a corrupted task-name → R2 taskname_corrupted (filename-scoped replace dodges it) · a weakened floor → R3 floors_lost (four-floors assertion) · design.md over pool budget → compress same-guide, never rebaseline · a stale byte pin → migrate 9514 forward to gate-udd.md's count

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: the migration batches 1–5 (git mv report-template.md→gate-udd.md ×3 trees · reframe opening as the text-mode UDD gate surface + design.md cross-link · design.md text-mode gate variant · filename-scoped repoint · test migration) landed in a PRIOR commit (`ed9a3e43` "thin-engine-loop W1 … fold gate-experience-udd rename"); this session completed the one unbuilt batch — batch 6, the acceptance suite `test_gate_experience_udd.py` (7 tests, canon tooling only; NOT twinned into `_bundled`, which must hold zero test sources). The suite pins the contract's DRIFT-STABLE invariants (rename ×3 byte-identical · UDD-surface + 4 floors · design.md variant · zero dangling `report-template.md` · engine untouched), deliberately NOT the frozen §3's since-superseded literal anchors — see the Live-verify block below.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] report-template.md no longer exists in any of the 3 skill trees; gate-udd.md exists in all 3, byte-identical — confirmed: `ls` shows rt=absent gu=present ×3; single md5 across trees; RenameHappened green
- [x] gate-udd.md opens as the text-mode UDD gate surface, cross-links design.md, and keeps all four floors (show-before-ask · one-approval · never-pre-stamp · security = HARD-STOP un-persona-negotiable) — confirmed: head line "# Gate reports — the text-mode UDD gate surface", links design.md, §"The four floors" block intact; GateUddIsUddSurface green
- [x] design.md's UDD loop carries the lightweight text-mode gate variant (intake INTERACTION → design → confirm, no wireframe/capture) naming gate-udd.md — confirmed: design.md §"Text-mode gate variant" (INTERACTION axis → report per gate-udd.md → confirm; "no capture beat") ×3 trees; DesignGateVariant green
- [x] a whole-tree grep for report-template.md returns ZERO live references (guides · docs · tests) — confirmed: 0 live pointers across 3 skill trees + 2 book docs ×3 book trees + tooling tests; NoDanglingReference green. R2 note: the historical task-name strings (report-template-recorded-loop · report-shape-scan-audit) are ABSENT from the current corpus — removed BY LATER refactors (test-corpus-slim et al.), NOT corrupted by this filename-scoped migration; R2 (no corruption by THIS task) holds.
- [x] add.py untouched by this task, SKILL.md — DRIFT DISCLOSED: EngineUntouched green (add.py holds no report-template/gate-udd string — migration is docs/tests only). STALE ANCHORS re-resolved: (a) `ENGINE_MD5 4e65596` is long superseded — add.py legitimately changed across dozens of later tasks (now `67519761…`); the invariant "no add.py edit BY THIS TASK" holds. (b) SKILL.md is 9876 B, OVER the frozen "< 9500 B" — this drift is from LATER unrelated work (adaptive-flow rewrote SKILL.md to the 3-beat loop + cookbook); the migration itself SHRANK it (−7 B/occurrence). The "< 9500" ceiling is unenforced now: `test_skill_lean.py` no longer exists and the full suite is green at 9876. (c) `test_report_shape_scan_audit` byte pin 9514 — that test/pin was removed with the corpus reorg. These are environmental drift since Ground SHA 53f8b00, not defects introduced here.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] DIALECT — tests speak the same value formats the spec's examples use (spec-dialect floor): <what confirmed>
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves in the current tree — RESOLVED with drift: gate-udd.md (×3 trees), design.md (×3), the 2 book docs all resolve; the migration is committed (`ed9a3e43`).
- [x] any anchor that moved/renamed since Ground SHA (53f8b00) is named here, not left silent — STALE ANCHORS: `report-template.md` (renamed → gate-udd.md, as intended) · `test_skill_lean.py` (REMOVED by later corpus reorg — no longer exists) · `test_report_shape_scan_audit.py` + its `9514` byte pin (REMOVED) · `SKILL.md < 9500 B` (now 9876 B via later work; ceiling unenforced) · `ENGINE_MD5 4e65596` (superseded → `67519761…`). None block the migration goal; all are post-freeze environmental drift.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed for the three ways this green could be fake — (1) vacuous no-dangling grep: confirmed the token is the real `.md` filename and the assertion scans live surfaces (3 skill trees + book docs + tooling tests), and it genuinely finds report-template.md ABSENT (not mis-scoped to zero files); (2) self-matching escape: the split-token `_OLD` construction means the test file's own text can't satisfy its own no-dangling assertion; (3) byte-parity illusion: the md5-set assertion would fail if any of the 3 trees drifted — verified 1 distinct digest. The floors/variant asserts read real content (opening line + §"four floors" + design.md §"Text-mode gate variant"), not test-internal stubs. NOTE (human backstop): this is a self refute-read under a CONSERVATIVE gate — the human owns the PASS.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — a docs/tests-only migration; no code path, secret, or input surface touched. add.py untouched.
2. Concurrency: CLEAR — no runtime, no shared state; pure static-file rename + test addition.
3. Architecture: RESIDUE (non-blocking) — the frozen §3 carries stale literal anchors (SKILL.md 9500 ceiling, ENGINE_MD5 4e65596, test_skill_lean/report_shape_scan_audit pins) that later work superseded; the acceptance test pins drift-stable invariants instead. Surfaced, not hidden — a human call on whether the drift is acceptable to PASS on.
Verdict: PASS (advisory)
Residue: stale frozen-contract anchors (documented above); no functional residue.
Binding: advisory — sensitivity: high (method-defining fold; human owns the gate)

### GATE RECORD
Reported: yes — the verify gate report (banner/ARC/SHAPE/FLAGS/EVIDENCE) rendered in chat before this record, drift disclosed
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose PHYSICAL rename + migrate every reference; rejected a conceptual fold keeping the path (rejected by human) · a new gate-loop guide (rejected — pool rebaseline)
- [human] freeze — froze §3 @ v1 (approved by tindang)
- [AI] build — approach: a filename-scoped MECHANICAL migration (git mv + `report-template.md`→`gate-udd.md`), NOT a blind global sed — the `.md` suffix + the two known bare SKILL.md pointers are the only live-file references; historical task-name substrings lack the `.md` and are left untouched (R2). A whole-tree `grep report-template.md` at the end proves zero dangling (R1). Chosen over a conceptual fold because the human picked the physical rename.
- [AI] build — data strategy: three parallel skill trees kept byte-identical (md5 parity) for gate-udd.md + design.md — the same twin-parity shape as prior skill-doc tasks; the byte pin migrates forward with a ledger note (report-template convention).
- [AI] build — pattern: the 3-skill-tree parity + pool ceilings (engine-minimalism); the forward-migrated byte-ledger pin of test_report_shape_scan_audit.py; the historical-task-name-preservation convention of the test ledger comments.
- [AI] build — optimization stance: correctness-of-migration first (zero dangling, zero task-name corruption); token cost second — the rename SHRINKS pools (−7 B/occurrence), design.md's added block offsets within orchestration-pool headroom (⚠ the facet trusted least: design.md's 774 B headroom is tight — if the gate-variant block overflows, compress same-guide, never rebaseline).
- [AI] build — strategy used: the migration batches 1–5 (git mv report-template.md→gate-udd.md ×3 trees · reframe opening as the text-mode UDD gate surface + design.md cross-link · design.md text-mode gate variant · filename-scoped repoint · test migration) landed in a PRIOR commit (`ed9a3e43` "thin-engine-loop W1 … fold gate-experience-udd rename"); this session completed the one unbuilt batch — batch 6, the acceptance suite `test_gate_experience_udd.py` (7 tests, canon tooling only; NOT twinned into `_bundled`, which must hold zero test sources). The suite pins the contract's DRIFT-STABLE invariants (rename ×3 byte-identical · UDD-surface + 4 floors · design.md variant · zero dangling `report-template.md` · engine untouched), deliberately NOT the frozen §3's since-superseded literal anchors — see the Live-verify block below.
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

