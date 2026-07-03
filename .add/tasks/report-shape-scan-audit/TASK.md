# TASK: Report Shape Scan Audit

slug: report-shape-scan-audit · created: 2026-07-02 · stage: mvp
milestone: loop-readability
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/skill/add/report-template.md` (9298 B; canonical of 3 mirrors — `.claude/skills/add/report-template.md`, `add-method/src/add_method/_bundled/skill/add/report-template.md`) — read in full: banner / ARC / PLAN·SHAPE / 6 core blocks / APPROVE-as-guided-choice / Hard rules
  - all 9 phase-guide files, each read in full and individually verdicted against report-template.md's shape (8 phases; ground+setup are phase 0's two entry variants): `phases/0-ground.md` (no gate — consistent), `phases/0-setup.md:79` (baseline-lock gate — cites ARC+APPROVE, **missing SHAPE**), `phases/1-specify.md` (no gate — feeds the freeze's FLAGS only, consistent), `phases/2-scenarios.md` (no gate — consistent), `phases/3-contract.md:17` (contract-freeze gate — cites ARC+APPROVE, **missing SHAPE**, the one gate SHAPE's own definition names as its use case), `phases/4-tests.md` (no gate — consistent), `phases/5-build.md` (no gate, explicitly deferred to verify under `auto` — consistent), `phases/6-verify.md:45` (verify gate — cites ARC+APPROVE+FLAGS explicitly, the most complete of the 3 gate guides), `phases/7-observe.md` (no gate — consistent)
  - `add-method/skill/add/SKILL.md:108-110` — the always-loaded "core" pool's own compact pipeline sentence ("open with the ARC..., then PLAN/SHAPE → SUMMARY → FLAGS → DECIDED → EVIDENCE → APPROVE → NEXT"); found while cross-checking the "no full order at a glance" candidate friction below — omits the banner (report-template.md's own "rendered first, above everything"). NOT one of "the 8 phase guides" this milestone scopes — a genuine boundary case, flagged not fixed (§1/§3).
  - `add-method/tooling/test_question_summary_layer.py::QuestionSummaryLayer.test_existing_constraints_verbatim` (lines 46-52, 82-86) — a byte-verbatim guard over 5 report-template.md `<constraints>` bullets, including "**Summary-first.** Never bury the decision under a task list or a diff." — built explicitly to prevent a reword of that text (docstring: "guards `guard_weakened`")
  - `add-method/tooling/test_skill_lean.py::POOLS` — "phases" (9 guides, ratio 0.80, baseline 40438) and "reference" (14 guides incl. report-template.md, ratio 0.68, baseline 75423) — the two byte-budget fences any proposed edit must clear; measured directly (not estimated): phases 32304/32350 B (46 B headroom), reference 51249/51287 B (38 B headroom)
Context (working folder):
  - `.add/tasks/report-plan-approve/TASK.md` (phase: done) — yesterday's task (2026-07-01) that rewrote report-template.md wholesale (banner+PLAN+SHAPE+APPROVE-rename) and renamed DECISION→APPROVE at exactly `0-setup.md:79` / `3-contract.md:17` / `6-verify.md:45`, but SHAPE-citation was never in *its* Must list at those 3 spots — the direct root cause of the gap this task found
  - `.add/tasks/docs-align/TASK.md` (phase: done) — the closest precedent for a multi-file prose-consistency §3 (a "touch-point inventory," not an HTTP shape); also shows the v1→v2 re-freeze convention for a disclosed frozen-contract delta
  - the working tree is DIRTY at ground time (`git status --short`: 10 modified + 9 untracked paths), including uncommitted edits to `phases/1-specify.md` / `scope.md` (×3 mirrors each) and `test_skill_lean.py` / `MILESTONE.md.tmpl` (×2 mirrors) from an apparent prior in-flight task ("uiux-hint-adoption," named in `test_skill_lean.py`'s own newest rebaseline comment) — the byte-headroom arithmetic above/below is measured against this CURRENT WORKING TREE (the real state a build edits on top of), not a clean commit; flagged as a stability risk in §1
Honors (patterns / conventions):
  - the 3-tree byte-identical mirror convention for every `skill/add/**` file (canonical `add-method/skill/add/` → `add-method/src/add_method/_bundled/skill/add/` + `.claude/skills/add/`), guarded by `test_skill_parity`/`test_bundle_parity` — dogfooded by both `report-plan-approve` and `docs-align`
  - the lean-fence rebaseline convention (CONVENTIONS.md, ~15 prior instances per `test_skill_lean.py`'s own comments): a human-approved content addition that busts a pool's target is absorbed by rebaselining (surface ÷ ratio, ratio kept exactly) — never by token-golfing unrelated prose thinner, and never self-approved by the AI
  - the "never weaken a test to make it pass" cardinal rule (5-build.md) extends, by the same spirit, to never silently reword a byte-verbatim guard's protected text without a disclosed, explicit decision
Anchors the contract cites: `add-method/skill/add/phases/3-contract.md:17` (+2 mirrors) · `add-method/skill/add/phases/0-setup.md:79` (+2 mirrors) · `add-method/skill/add/report-template.md`'s "## PLAN / SHAPE" section (cited as-is, unchanged) · `test_skill_lean.py::POOLS["phases"]` and `POOLS["reference"]`
Issues/Risks (→ feed §1):
  - report-template.md's own bullet "**Summary-first.** Never bury the decision under a task list or a diff." is momentarily ambiguous on a fresh read (SUMMARY-the-block, or APPROVE-the-ask?) — but it is byte-verbatim guarded (`test_question_summary_layer.py`) and `report-plan-approve`'s own build notes record a prior, deliberate reversion of an edit attempt to this exact region; reopening it for a marginal disambiguation gain is not justified this pass — named, not fixed.
  - `phases/3-contract.md` and `phases/0-setup.md` are the only two of the 9 phase files that fire an actual contract-freeze (SHAPE's sole "freeze-only" use case), yet neither names SHAPE — both cite ARC+APPROVE only. Root cause: `report-plan-approve` renamed DECISION→APPROVE at exactly these 2 spots (+6-verify.md) but SHAPE-citation was never its own Must item.
  - `SKILL.md:108-110`'s compact pipeline sentence (the always-loaded quick-reference) omits the banner — a real drift against report-template.md's own banner section, but SKILL.md is not literally one of "the 8 phase guides" this milestone scopes — genuine boundary ambiguity, escalated rather than resolved by guessing.
  - both budget pools (38 B / 46 B headroom) are near-zero AND measured against a dirty working tree with unrelated in-flight edits — any proposed byte-costing edit risks drifting stale between GROUND and BUILD.
Related intent:
  - `.add/PROJECT.md:50-59` ("decision-suggestions," SHIPPED 2026-06-16) — precedent that report-template.md is a "PRESENTATION layer (NO engine change)" whose shape "iterates freely WITHOUT a re-freeze," and that a full N-guide cue-consistency sweep (there: 8 gate-bearing guides — setup·contract·verify·intake·scope·close·graduate·release) is a normal, previously-executed exercise in this project.
  - Milestone `loop-readability` — corrected mid-draft from "add.py's own CLI text" to "the AI's chat reports to the human," scoped explicitly to report-template.md + "the 8 phase guides," excluding `add.py` CLI output, DESIGN TOKENS/RESPONSIVE BREAKPOINTS, and any silent lean-fence rebaseline.
  - GLOSSARY: none of SHAPE/ARC/PLAN/APPROVE are formal `.add/GLOSSARY.md` entries (grep-confirmed) — they are report-template.md's own internal block vocabulary; the actual glossary-level terms tied to this feature are **Guided decision** / **Recommended pick** (PROJECT.md:55), both unaffected by this task.
Ground SHA: `e1c5829` (working tree DIRTY at this SHA — see Context above; the byte-budget arithmetic in §1/§3 is measured against live working-tree file contents, not a clean commit — flagged as re-verify-at-BUILD in §1's ⚠ assumptions)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: audit report-template.md's ARC + 6-block shape for genuine scanability against its OWN stated rules, and check all 8 phase guides' human-gate reporting cues for drift against that shape
Framings weighed: a targeted 2-file phase-guide fix (SHAPE citation at both freeze gates) + explicit disclosure of what was found-but-deliberately-left + one escalated boundary flag (chosen) · a report-template.md restructure adding a compact "full render order" line (rejected — SKILL.md:108-110 already carries this exact map; the addition would be genuinely redundant, not gap-filling, and costs ~88 B against a 38 B reference-pool headroom) · reword the "Summary-first...the decision" bullet for disambiguation (rejected — byte-verbatim guarded by test_question_summary_layer.py, and report-plan-approve already deliberately reverted a similar edit to this exact region once) · silently merge the SKILL.md banner-omission fix into this task's frozen scope (rejected — SKILL.md is not literally one of "the 8 phase guides" the milestone names; merging it in without the human's explicit call would be an undisclosed scope stretch)
Must:
<must>
  - all 9 phase-guide files are read in full and each is individually verdicted against report-template.md's shape: gate-bearing-and-consistent, no-gate-so-correctly-silent, or drifted — no file sampled or skipped (§0 Touches records all 9)
  - report-template.md's own prose is audited against ITS OWN stated rules (summary-first, one decision never buried, guided-choice, "write none rather than dropping one") as the primary standard, not the auditor's taste
  - `phases/3-contract.md` (canonical + 2 mirrors) gains a minimal citation of the SHAPE block at the contract-freeze gate — the one gate SHAPE's own "freeze-only" definition names as its use case
  - `phases/0-setup.md` (canonical + 2 mirrors) gains the same minimal SHAPE citation at the baseline-lock gate, which also stamps a real `§3 FROZEN @ v1` per its own "5 · After the lock" section
  - every proposed edit is checked against the existing test suite (grep across `add-method/tooling/test_*.py`) for a verbatim-pinned collision BEFORE being written into this contract as frozen
  - the two affected `test_skill_lean.py` pools ("phases" and "reference") are measured precisely, not estimated, before and after every proposed edit, and any edit whose real cost exceeds the live headroom is named as an explicit FLAG — never silently applied and never silently dropped
</must>
Reject:
<reject>
  - a proposed report-template.md edit costing more bytes than the live reference-pool headroom, applied without a disclosed FLAG naming the exact overage and the human-approval-needed rebaseline path -> "lean_fence_silent_overrun"
  - a reword of any bullet inside report-template.md's `<constraints>` block that test_question_summary_layer.py::test_existing_constraints_verbatim pins byte-verbatim, applied without an explicit, disclosed test-update decision -> "guard_weakened"
  - a phase-guide edit that duplicates content report-template.md already renders by default (e.g. re-explaining EVIDENCE or SUMMARY at every gate) instead of citing only what's gate-specific -> "redundant_recue"
  - any of the 3 skill-tree mirrors (canonical / `_bundled` / `.claude/skills`) of an edited phase guide left un-mirrored after the edit -> "mirror_drift"
  - merging a finding outside "the 8 phase guides" (e.g. SKILL.md) into the frozen diff without naming it as a separate, human-decided scope question -> "scope_creep_undisclosed"
</reject>
After:
<after>
  - `phases/3-contract.md` and `phases/0-setup.md` (6 files across 3 mirrors) explicitly cite rendering SHAPE at their respective freeze gates; the "phases" pool measures 32326/32350 B (used 22 of 46 B headroom, 24 B spare)
  - `report-template.md` is unchanged (0 B delta) this pass; the "reference" pool measures 51249/51287 B, unchanged (38 B headroom preserved, untouched)
  - this TASK.md's §0/§1 name, for each of the 9 phase files, its verdict (consistent / no-gate-correctly-silent / drifted-and-fixed) — a future reader never re-derives which guides were checked
  - two flags are surfaced at the freeze (§3): the SKILL.md banner-omission boundary question, and the dirty-working-tree headroom-stability risk
  - the "Summary-first...the decision" ambiguity is named in §0 Issues/Risks as found-but-deliberately-untouched, with its guard-protection reasoning on record
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether `SKILL.md:108-110`'s pipeline sentence (which omits the banner) counts as in-scope under the milestone's own carve-back ("phase-guide teaching content... UNLESS it directly shapes what gets told to the human") — lowest confidence because this is a genuine textual ambiguity in the milestone's own Scope wording that re-reading cannot resolve, and SKILL.md is not literally one of "the 8 phase guides" the exit criteria name; if wrong (human wanted it in scope from the start): a ~20 B fix is cheap (core pool has 187 B headroom, comfortable margin) and addable as a one-line follow-up without reopening this freeze; if wrong the other way (correctly out of scope, as drafted): zero cost, since no edit was applied speculatively.
  - [ ] whether the ~38 B (reference) / ~46 B (phases) headroom measured against the CURRENT DIRTY working tree will still hold once this task reaches BUILD, given 10 modified + 9 untracked paths from other in-flight work already present at ground time — confirm by re-running the exact test_skill_lean.py POOLS arithmetic at BUILD start, not by trusting this GROUND-time number; if wrong (headroom shrinks further before build): the 22 B combined phases-pool fix has 24 B of real margin today, so it likely still clears, but a fresh measurement is the honest gate, not an assumption.
  - [ ] whether ruling OUT a report-template.md body edit entirely (guard-protected + SKILL.md already covers the one clean finding) still satisfies exit criterion 1's "cite the concrete friction found + the fix," versus a stricter reading that expects some nonzero literal diff to report-template.md itself — the milestone's own "...OR any growth sits as a named FLAG..." clause reads as permitting a zero-edit outcome when the honest conclusion is "materially sound, no safe value-add edit found"; confirm or correct at the freeze — low cost either way.
  - [ ] whether `0-setup.md`'s baseline-lock gate — a one-time event, not a recurring per-task freeze — genuinely warrants the identical SHAPE citation given to `3-contract.md`'s recurring per-task freeze — resolved by 0-setup.md's own "5 · After the lock" section explicitly naming a real `§3 FROZEN @ v1` stamp, so the freeze-relevance is genuine, not assumed; if wrong (the human judges setup's report is SETUP-REVIEW.md-centric enough that SHAPE there is unneeded noise): trivially revertible, an 11-byte single-line change.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: all 9 phase files are individually verdicted, none sampled   # M1
  Given the 9 files phases/0-ground.md, 0-setup.md, 1-specify.md, 2-scenarios.md, 3-contract.md,
    4-tests.md, 5-build.md, 6-verify.md, 7-observe.md
  When each is read in full and checked for its human-gate reporting cue against report-template.md's shape
  Then §0 GROUND names a verdict for every one of the 9 (6 "no gate, correctly silent," 1 "gate,
    consistent" [6-verify.md], 2 "gate, drifted" [3-contract.md, 0-setup.md]) — zero files unverdicted

Scenario: report-template.md is audited against its own stated rules, not the auditor's taste   # M2
  Given report-template.md's <constraints> block (summary-first · show-before-ask · guided-decision ·
    write-none-not-drop) read in full
  When the file's own prose (banner/ARC/PLAN·SHAPE/6-block order) is checked against those rules
  Then every cited friction traces to a specific rule or a specific block's own stated definition —
    never a bare stylistic preference

Scenario: 3-contract.md cites SHAPE at the contract-freeze gate   # M3
  Given phases/3-contract.md line 17's current freeze-report cue ("Open with the ARC per
    `report-template.md`, rendering the freeze APPROVE as a guided choice...")
  When the minimal SHAPE citation is applied ("...rendering SHAPE then the freeze APPROVE...")
  Then the edited line names SHAPE explicitly at the one gate report-template.md defines it for
    ("freeze-only"), and the same edit is mirrored byte-identically to both other skill trees

Scenario: 0-setup.md cites SHAPE at the baseline-lock gate   # M4
  Given phases/0-setup.md line 79's current gate-report cue ("Open the report with the ARC per
    `report-template.md`, render APPROVE as a guided choice, then present `SETUP-REVIEW.md`...")
  When the minimal SHAPE citation is applied ("...render SHAPE then APPROVE as a guided choice...")
  Then the edited line names SHAPE explicitly at the gate that stamps the first task's real
    `§3 FROZEN @ v1`, and the same edit is mirrored byte-identically to both other skill trees

Scenario: every proposed edit is checked against the test suite before being frozen   # M5
  Given the 2 proposed phase-guide edits (3-contract.md, 0-setup.md) and the report-template.md
    body (considered, then left unedited)
  When grep -rn is run across add-method/tooling/test_*.py for the exact old and new wording of
    each candidate edit
  Then no proposed edit collides with a verbatim-pinned assertion (confirmed: 3-contract.md's and
    0-setup.md's report lines are pinned by no test; report-template.md's "Summary-first" bullet
    IS pinned by test_question_summary_layer.py, so that candidate edit is dropped, not applied)

Scenario: both affected lean-fence pools are measured precisely before freezing   # M6
  Given test_skill_lean.py's POOLS entries "phases" (baseline 40438, ratio 0.80) and "reference"
    (baseline 75423, ratio 0.68)
  When the live byte totals are computed by reading the actual current working-tree files
  Then "phases" measures 32304/32350 B pre-edit (46 B headroom) and 32326/32350 B post-edit (24 B
    spare); "reference" measures 51249/51287 B, unchanged (38 B headroom, untouched) — both hold

Scenario: a report-template.md fix costing more than its live headroom is flagged, not silently applied   # R1
  Given the candidate "full render order at a glance" line (measured at 88 B) against a 38 B
    reference-pool headroom
  When the edit is evaluated
  Then it is rejected as a silent addition ("lean_fence_silent_overrun" avoided) — named instead as
    a found-but-not-applied friction, further noted as redundant with SKILL.md:108-110's existing
    compact pipeline sentence
  And report-template.md's byte count and every existing constraint bullet remain unchanged

Scenario: a guard-protected bullet reword is rejected, not silently applied   # R2
  Given report-template.md's byte-verbatim-pinned bullet "**Summary-first.** Never bury the
    decision under a task list or a diff." (test_question_summary_layer.py::
    test_existing_constraints_verbatim)
  When a disambiguating reword ("the decision" -> "SUMMARY") is evaluated
  Then it is rejected ("guard_weakened" avoided) without an explicit, disclosed test-update decision
    — named in §0 Issues/Risks as found-but-deliberately-untouched, citing both the guard test and
    report-plan-approve's own prior reversion of a similar edit
  And the bullet's exact current bytes remain in report-template.md, and
    test_question_summary_layer.py stays green, untouched

Scenario: a redundant per-gate re-explanation is rejected in favor of a terse citation   # R3
  Given the option to fully re-list all 6 core blocks' definitions inline at every one of the 3
    gate-bearing phase guides
  When the alternative (a terse, gate-specific citation naming only what's special to that gate) is
    compared
  Then the terse form is chosen — matching the EXISTING style already used for ARC/APPROVE/FLAGS
    citations in these same 3 files — and the fuller "redundant_recue" form is rejected

Scenario: an edited phase guide left un-mirrored is caught before the freeze   # R4
  Given the 2 proposed edits target the canonical add-method/skill/add/ tree
  When the byte-identical mirror requirement (add-method/src/add_method/_bundled/skill/add/ +
    .claude/skills/add/) is checked against the contract
  Then §3 CONTRACT explicitly lists all 3 mirror paths per edited file (6 files total for 2 edits),
    so a build that edits only the canonical copy is caught as incomplete against this contract

Scenario: a finding outside "the 8 phase guides" is named as a flag, never silently merged in nor silently dropped   # R5
  Given SKILL.md:108-110's compact pipeline sentence, found to omit the banner while cross-checking
    report-template.md's own shape
  When the milestone's literal scope ("all 8 phase guides") is checked against this finding
  Then SKILL.md is NOT added to §3's frozen diff (avoiding "scope_creep_undisclosed"), and is
    instead surfaced as the bundle's top ⚠ flag at the freeze, with its fix cost (~20 B against a
    187 B core-pool headroom) disclosed for the human's explicit call
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE-ONLY task — no engine logic change (no add.py / add_engine/ edit)

Touch-point inventory (2 edits, 6 files with mirrors; report-template.md UNCHANGED):

  1. add-method/skill/add/phases/3-contract.md  (+2 mirrors: add-method/src/add_method/_bundled/
     skill/add/phases/3-contract.md, .claude/skills/add/phases/3-contract.md)
     Line 17, AMEND (fragment before -> after):
       BEFORE: "Open with the ARC per `report-template.md`, rendering the freeze APPROVE as a
                guided choice (recommended pick + described alternatives)."
       AFTER:  "Open with the ARC per `report-template.md`, rendering SHAPE then the freeze
                APPROVE as a guided choice (recommended pick + described alternatives)."
       Delta: +11 B per file (33 B across all 3 mirrors) — verified against the live file, not estimated

  2. add-method/skill/add/phases/0-setup.md  (+2 mirrors: add-method/src/add_method/_bundled/
     skill/add/phases/0-setup.md, .claude/skills/add/phases/0-setup.md)
     Line 79, AMEND (fragment before -> after):
       BEFORE: "Open the report with the ARC per `report-template.md`, render APPROVE as a guided
                choice, then present `SETUP-REVIEW.md` lowest-confidence-first."
       AFTER:  "Open the report with the ARC per `report-template.md`, render SHAPE then APPROVE
                as a guided choice, then present `SETUP-REVIEW.md` lowest-confidence-first."
       Delta: +11 B per file (33 B across all 3 mirrors) — verified against the live file, not estimated

  3. add-method/skill/add/report-template.md  (+2 mirrors)
     NO EDIT this pass. Audited in full against its own stated rules; found materially sound
     post-report-plan-approve (2026-07-01). Two findings disclosed, neither applied:
       - "Summary-first...the decision" ambiguity: real but byte-verbatim guarded
         (test_question_summary_layer.py::test_existing_constraints_verbatim) — left untouched.
       - "full render order at a glance": real gap if report-template.md stood alone, but
         SKILL.md:108-110 already carries this exact compact map — redundant, not applied; would
         also cost ~88 B against a 38 B headroom if it were applied.
     Delta: 0 B.

Byte-budget arithmetic (test_skill_lean.py::POOLS, measured against the live working tree,
  NOT estimated):
  "phases" pool (9 guides, ratio 0.80, baseline 40438): 32304 B pre-edit -> 32326 B post-edit
    (target 32350 B; 46 B headroom pre-edit -> 24 B spare post-edit) — HOLDS.
  "reference" pool (14 guides incl. report-template.md, ratio 0.68, baseline 75423): 51249 B,
    UNCHANGED (target 51287 B; 38 B headroom, untouched) — HOLDS.

Reject (from §1, each traced to a mechanism):
  a proposed edit costing more than the live pool headroom, applied silently -> "lean_fence_silent_overrun"
    (test_skill_lean.py::test_pools_under_byte_budget goes red for the pool named)
  a reword of a byte-verbatim-pinned constraint bullet without a disclosed decision -> "guard_weakened"
    (test_question_summary_layer.py::test_existing_constraints_verbatim goes red)
  a phase-guide re-explaining a default-rendered block instead of a gate-specific citation -> "redundant_recue"
    (no dedicated test; caught at this contract's own review — the terse form is chosen, see R3)
  an edited phase guide left un-mirrored -> "mirror_drift"
    (test_skill_parity / test_bundle_parity goes red)
  a finding outside "the 8 phase guides" silently merged into the diff -> "scope_creep_undisclosed"
    (no dedicated test; caught at this contract's own review — SKILL.md is flagged, not merged in)
```

Glossary deltas: none — SHAPE/ARC/PLAN/APPROVE are report-template.md's own internal block
  vocabulary (established by report-plan-approve), not `.add/GLOSSARY.md` domain terms; this task
  cites existing vocabulary, it does not introduce a new concept.

Least-sure flag surfaced at freeze: [contract] whether SKILL.md:108-110's pipeline sentence (omits
  the banner) is in-scope under the milestone's own carve-back ("...UNLESS it directly shapes what
  gets told to the human") — lowest confidence because SKILL.md is not literally one of "the 8 phase
  guides" the exit criteria name, yet its prose does directly instruct report-rendering order; NOT
  included in this frozen diff. If the human wants it in: cheap, ~20 B against a 187 B core-pool
  headroom, addable as a small follow-up without reopening this freeze. If out, as drafted: zero
  cost. Second flag: [contract] the ~46 B "phases" / ~38 B "reference" headroom is measured against
  a DIRTY working tree (10 modified + 9 untracked paths from other in-flight work already present at
  ground time) — re-verify the exact POOLS arithmetic at BUILD start rather than trusting this
  GROUND-time number; today's 24 B spare margin on the applied fix makes drift-through unlikely but
  not certain.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/3-contract.md`, `add-method/skill/add/phases/0-setup.md`,
  `.claude/skills/add/phases/3-contract.md`, `.claude/skills/add/phases/0-setup.md`,
  `add-method/src/add_method/_bundled/skill/add/phases/3-contract.md`,
  `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` — exactly the §3 touch-point
  inventory; `report-template.md` explicitly OUT of scope (0 B delta, per §3).
Strategy (ordered batches): 1. write the RED test suite (`test_report_shape_scan_audit.py`) against
  the frozen §3 BEFORE/AFTER fragments and confirm RED. 2. apply the two AMEND edits verbatim across
  all 3 mirrors each (6 files, one batch). 3. confirm GREEN on the task suite. 4. run a targeted
  regression batch (34 pre-existing test files referencing the 3 touched files) to catch any
  wiring/parity fallout the task suite alone wouldn't.

Persona (optional): absent — generic; mechanical prose edit, no domain stance needed.
Known-problem fixes: mirror drift (editing one of 3 copies and forgetting the others) → planned fix:
  apply all 3 mirrors of each file in the same Edit batch, then assert byte-identity in the test suite.
Strategy actually used: as planned — no deviation.
Safety rule (feature-specific): none — no runtime/transactional surface; prose-only doc edit.
Code lives in: N/A — no `./src/`; this task edits skill-guide prose directly at its Scope paths above.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 7/7 task suite + 319/319 targeted regression batch (34 pre-existing files
      referencing the 3 touched paths), exit 0
- [x] coverage did not decrease — N/A (prose task, no code coverage metric)
- [x] no test or contract was altered during build — only the 2 frozen edits + 6 mirror files touched
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — N/A, no runtime/shared-state surface
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only markdown edit
- [x] layering & dependencies follow CONVENTIONS.md — no new dependency; mirror-parity convention followed
- [x] a person reviewed and approved the change — the §3 freeze itself (Tin Dang, "Approve"); this
      gate auto-resolves on evidence under `autonomy: auto` per the frozen run mode

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `3-contract.md`'s freeze-gate sentence names SHAPE ahead of the freeze APPROVE — confirmed by
      `sed -n '17p' add-method/skill/add/phases/3-contract.md` showing the AFTER fragment verbatim
- [x] `0-setup.md`'s baseline-lock sentence names SHAPE ahead of APPROVE — confirmed by
      `sed -n '79p' add-method/skill/add/phases/0-setup.md` showing the AFTER fragment verbatim
- [x] `report-template.md` carries 0 B delta — confirmed by byte count unchanged at 9298 B
      (`test_report_template_byte_count_unchanged`)
- [x] both edits mirrored byte-identically across canonical/dogfood/bundle — confirmed by md5
      equality (`test_contract_mirrors_byte_identical`, `test_setup_mirrors_byte_identical`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read all 6 touched files in full pre- and post-edit (not
      skimmed); confirmed each AMEND lands in the exact freeze-gate/baseline-lock sentence §3
      specified, with no adjacent prose disturbed, and the byte-verbatim-guarded "Summary-first"
      bullet in `report-template.md` survives unedited (`test_guarded_bullet_untouched`)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every anchor §3 CONTRACT cites still resolves in the current tree — confirmed by direct
      `sed -n` re-read of `3-contract.md` line 17 and `0-setup.md` line 79 post-edit: both still
      the exact lines (in-place text substitution, no line insertion/deletion, no drift from the
      dirty-tree state flagged at ground time)
- [x] no anchor moved/renamed since Ground SHA — the ⚠ ground-time flag (headroom measured against
      a dirty tree) is resolved: re-measured post-edit at BUILD, "phases" pool 32326 B / target
      32350 B (24 B spare, exact match to the §3 prediction), "reference" pool unchanged 51249 B /
      target 51287 B (38 B headroom) — no drift occurred

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) could the substring assertions pass on a decoy — e.g. "SHAPE"
  inserted somewhere irrelevant rather than at the freeze-gate sentence? No: each Edit's old_string
  matched the exact §3-specified BEFORE fragment at its one occurrence, so the AFTER text can only
  land at that specific sentence — verified by the direct `sed -n` line re-read above, not just the
  test. (2) could the mirror/byte-count tests be vacuously true (e.g. all 3 mirrors wrong in the
  same way)? No: the AFTER string is asserted present AND the BEFORE string is asserted absent, so
  a no-op or partial edit would fail; mirror identity is md5 over full file bytes, not a substring.
  (3) does the 319-test regression batch actually exercise these files, or just import them
  incidentally? Spot-checked `test_arc_gate_wiring.py` and `test_tree_parity.py` — both read the
  edited files' content directly, not just existence.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — markdown prose edit, no code path, no secrets/injection surface
2. Concurrency: CLEAR — no runtime code, no shared state, no locking touched
3. Architecture: CLEAR — two isolated one-line text amendments; mirror-parity convention preserved;
   no new coupling, no new abstraction, no cross-file structural change
Verdict: PASS
Residue: none
Binding: yes — mechanical (prose-only, no `risk: high` declared, disclosed+frozen touch-point inventory)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under autonomy: auto, per "yes, auto mode") · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): N/A — prose-only doc edit, no runtime signal; the real signal
  is qualitative: does a human reading a future contract-freeze or baseline-lock report actually
  notice SHAPE being rendered before APPROVE, closing the readability gap this task targeted.

### Decisions (ADR)
- [AI] specify — chose a targeted 2-file phase-guide fix (SHAPE citation at both freeze gates) + explicit disclosure of what was found-but-deliberately-left + one escalated boundary flag; rejected a report-template.md restructure adding a compact "full render order" line (rejected — SKILL.md:108-110 already carries this exact map; the addition would be genuinely redundant, not gap-filling, and costs ~88 B against a 38 B reference-pool headroom) · reword the "Summary-first...the decision" bullet for disambiguation (rejected — byte-verbatim guarded by test_question_summary_layer.py, and report-plan-approve already deliberately reverted a similar edit to this exact region once) · silently merge the SKILL.md banner-omission fix into this task's frozen scope (rejected — SKILL.md is not literally one of "the 8 phase guides" the milestone names; merging it in without the human's explicit call would be an undisclosed scope stretch)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — no deviation.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto, per "yes, auto mode"))

### Spec delta
- [SPEC · dropped] SKILL.md:108-110's compact pipeline sentence omits the banner citation (report-
  template.md's own "rendered first, above everything") — a genuine drift, deliberately left out of
  this task's frozen scope because SKILL.md is not literally one of "the 8 phase guides" the
  milestone names, only escalated as a flag (evidence: §3 flag 1; ~20 B cost against a 187 B
  core-pool headroom if picked up as its own small follow-up).
- [SPEC · carried] a §3 Status line hand-edited to `FROZEN @ vN` (bypassing `add.py freeze`) passes [carried: a real engine-hardening idea but a bigger design question (mirroring refute_unrecorded's pattern) than a quick fix; needs its own design pass]
  `_contract_frozen()` and reads as approved in TASK.md, but silently skips both the engine's
  `_flag_well_formed` pre-check and the structured `state.json` freeze audit record — consider an
  integrity check mirroring the existing `refute_unrecorded`/`advisor_verdict_unrecorded` pattern
  (evidence: this task's own freeze was hand-stamped; the resulting malformed flag-label wasn't
  caught until the tests→build crossing, one avoidable round-trip later).

### Competency deltas
- [ADD · folded] always run `add.py freeze --by "<name>"` for a contract approval, never hand-edit [folded foundation-version 62]
  `Status: DRAFT` → `FROZEN` — the command's own `_flag_well_formed` pre-check catches a malformed
  lowest-confidence-flag label BEFORE presenting to the human, and its write path records the
  structured `state.json` freeze entry a hand-edit silently skips (evidence: this task's freeze was
  hand-stamped, and the label mismatch it let through wasn't caught until `add.py advance` refused
  the tests→build crossing).
- [ADD · folded] the established "Least-sure flag surfaced at freeze:" convention (singular "flag", [folded foundation-version 62]
  colon immediately after, "Second flag:" for a 2nd point) is enforced by an exact-string engine
  regex, not just a style preference — a hand-drafted §3 that paraphrases this heading (e.g. plural
  "flags" + a parenthetical before the colon) reads fine to a human but fails `_flag_well_formed`
  silently until the build-crossing gate (evidence: this task's own §3, confirmed against 10+ other
  frozen tasks in `.add/tasks/*/TASK.md` all using the identical exact phrasing).

