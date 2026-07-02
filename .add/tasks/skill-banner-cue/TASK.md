# TASK: SKILL.md cites the banner in its compact pipeline map

slug: skill-banner-cue · created: 2026-07-03 · stage: mvp
milestone: loop-readability
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/skill/add/SKILL.md:108-110` (canonical of 3 byte-identical mirrors — `.claude/skills/add/SKILL.md`, `add-method/src/add_method/_bundled/skill/add/SKILL.md`; md5 `54eade6b583e1487d5c22c7505a92fe2` confirmed equal across all 3) — the always-loaded "core" pool's compact pipeline sentence: "At every human decision point (intake · bundle approval · gate · milestone close) follow report-template.md: open with the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE → SUMMARY → FLAGS → DECIDED → EVIDENCE → APPROVE → NEXT; show-before-ask; never pre-stamp; the question is a summary, never the artifact." Already cites SHAPE; omits the banner.
  - `add-method/skill/add/report-template.md:7-16` (read-only anchor, NOT edited) — "## The decision banner — rendered first, above everything": a boxed banner line rendered BEFORE the ARC, on every report at a human gate.
Context (working folder):
  - `.add/tasks/report-shape-scan-audit/TASK.md` (phase: done, gate: PASS) — the just-closed sibling task in this same milestone; its §3 flag 1 named this exact SKILL.md gap and deliberately left it out of its own frozen diff (SKILL.md is not one of "the 8 phase guides" its own scope named)
  - an `add-advisor` consult (spawned 2026-07-03 on that flag) recommended "fix now" as a new small task, citing the milestone Scope Out clause's own UNLESS carve-back ("phase-guide teaching content aimed at the AI UNLESS it directly shapes what gets told to the human") — SKILL.md's sentence is a literal, ordered recipe for report-render order, so the carve-back applies despite SKILL.md not being one of the 9 `phases/*.md` files
  - the working tree is DIRTY at ground time (`git status --short`: 26 paths, `git rev-parse --short HEAD` = e1c5829) — includes the sibling task's own now-closed edits plus still-uncommitted `uiux-hint-adoption` work; byte-headroom arithmetic below is measured against this CURRENT tree, not a clean commit
Honors (patterns / conventions):
  - the exact "X then Y" idiom `report-shape-scan-audit` established twice this same milestone (`"SHAPE then the freeze APPROVE"` in `3-contract.md`, `"render SHAPE then APPROVE"` in `0-setup.md`) — reused here as `"the banner then the ARC"` for a 3-for-3 consistent phrasing rather than inventing new wording
  - the 3-tree byte-identical mirror convention (`test_skill_parity`/`test_bundle_parity`) — same edit applied to all 3 `SKILL.md` copies in one batch
  - the lean-fence rebaseline convention is NOT needed here — the edit fits inside existing headroom (see arithmetic below), so no pool baseline changes
Anchors the contract cites: `add-method/skill/add/SKILL.md:109` (+2 mirrors) · `add-method/tooling/test_skill_lean.py::POOLS["core"]`
Issues/Risks (→ feed §1):
  - `intake.md:39` ("Present the proposal via `report-template.md` — open with the ARC (goal · done · plan): the goal this request serves...") superficially echoes "open with the ARC" but is NOT a duplicate of SKILL.md's compact pipeline sentence — it doesn't enumerate the full block chain (PLAN/SHAPE → SUMMARY → ... → NEXT) the way SKILL.md's sentence does, so it makes no completeness claim the fix would contradict. Verified by direct read, not assumed; left untouched — a parallel edit there would be a separate, undisclosed scope stretch.
  - no test pins SKILL.md's compact pipeline sentence verbatim (`grep -rln` across `test_*.py` for the BEFORE fragment returned zero files) — safe to reword, unlike report-template.md's byte-verbatim-guarded "Summary-first" bullet.
Related intent:
  - `.add/milestones/loop-readability/MILESTONE.md` Scope Out clause + its own UNLESS carve-back (lines 32-38) — the direct textual basis for why this task is in-scope despite SKILL.md not being one of "the 8 phase guides"
  - `.add/tasks/report-shape-scan-audit/TASK.md` §7 Spec delta 1 — the originating disclosed flag this task resolves
Ground SHA: e1c5829

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SKILL.md's compact pipeline sentence names the decision banner
Framings weighed: amend the existing sentence in-place with "the banner then" (chosen) ·
  add a whole new sentence about the banner (rejected — redundant, costs more bytes for the
  same fact) · restructure report-template.md instead (rejected — out of this task's scope,
  report-template.md is reference-pool budget-locked and untouched by the sibling task on
  purpose)
Must:
<must>
  - SKILL.md's phase-table-adjacent compact pipeline sentence names the banner, in render
    order, ahead of the ARC (matching report-template.md's own "rendered first, above
    everything")
  - the edit is mirrored byte-identically across all 3 SKILL.md copies
  - the "core" pool (test_skill_lean.py::POOLS) stays within its byte-budget target after
    the edit — no rebaseline
</must>
Reject:
<reject>
  - an edit that pushes the "core" pool over its target without a disclosed, human-approved
    rebaseline -> "lean_fence_silent_overrun"
  - a wording that reads as a NEW claim inconsistent with report-template.md's own banner
    section -> "guard_weakened" (by the same spirit as the byte-verbatim guard elsewhere,
    even though this specific sentence carries no literal test pin)
  - an edited SKILL.md left un-mirrored across the 3 copies -> "mirror_drift"
</reject>
After:
<after>
  - a human or AI reading SKILL.md's compact pipeline sentence sees the full, correctly
    ordered render sequence: banner -> ARC -> PLAN/SHAPE -> SUMMARY -> FLAGS -> DECIDED ->
    EVIDENCE -> APPROVE -> NEXT
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether "the banner then the ARC" (16 B) reads clearly inline, vs. a heavier restructure
    (e.g. a separate short clause) — lowest confidence because it's a style/taste judgment,
    not a mechanical fact; if wrong: a trivial reword, no re-freeze needed since the touch-
    point (this one sentence) doesn't change, only its exact phrasing
  - [x] does intake.md need the same treatment? — denied: confirmed by direct read (§0
    Issues/Risks) that intake.md:39 is a different, non-enumerating sentence; no parallel
    edit needed
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: compact pipeline sentence names the banner   # M1
  Given SKILL.md's current sentence "open with the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE → SUMMARY →"
  When the AMEND lands
  Then the sentence reads "open with the banner then the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE → SUMMARY →"
  And no other clause in the sentence changes

Scenario: mirrors stay byte-identical   # M2
  Given the same AMEND applied to all 3 SKILL.md copies (canonical, dogfood, bundle)
  When the edit is complete
  Then md5(canonical) == md5(dogfood) == md5(bundle)
  And the pre-edit shared md5 (54eade6b583e1487d5c22c7505a92fe2) no longer matches any of the 3

Scenario: core pool holds budget   # M3
  Given the "core" pool (SKILL.md + intake.md, ratio 0.88, baseline unchanged) measured at
    17999 B against an 18186 B target (187 B headroom) before this edit
  When the +16 B AMEND is applied
  Then the pool measures 18015 B, still <= 18186 B (171 B headroom remains)
  And no pool baseline in test_skill_lean.py is touched

Scenario: no test pin broken   # R1
  Given no existing test asserts the pre-edit BEFORE fragment verbatim
  When the AMEND lands
  Then the full regression batch (34 files referencing SKILL.md / report-template.md /
    lean pools, same batch as the sibling task) stays green
  And test_skill_parity / test_bundle_parity stay green (mirror check)

Scenario: intake.md left untouched   # R2
  Given intake.md:39's sentence is confirmed NOT a duplicate of SKILL.md's compact map
  When this task's build completes
  Then intake.md's byte count and content are unchanged
  And no parallel edit was made there
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE-ONLY task — no engine logic change (no add.py / add_engine/ edit)

Touch-point inventory (1 edit, 3 mirror files):

  1. add-method/skill/add/SKILL.md  (+2 mirrors: add-method/src/add_method/_bundled/
     skill/add/SKILL.md, .claude/skills/add/SKILL.md)
     Line 109, AMEND (fragment before -> after):
       BEFORE: "open with the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE →
                SUMMARY →"
       AFTER:  "open with the banner then the ARC (goal · done · plan, engine-sourced), then
                PLAN/SHAPE → SUMMARY →"
       Delta: +16 B per file (48 B across all 3 mirrors) — verified against the live file via
       len(after.encode())-len(before.encode()), not estimated

Byte-budget arithmetic (test_skill_lean.py::POOLS["core"], measured against the live working
  tree, NOT estimated):
  "core" pool (2 guides — SKILL.md + intake.md, ratio 0.88, baseline unchanged): 17999 B
    pre-edit -> 18015 B post-edit (target 18186 B; 187 B headroom pre-edit -> 171 B spare
    post-edit) — HOLDS, no rebaseline needed.

Reject (from §1, each traced to a mechanism):
  a proposed edit costing more than the live pool headroom, applied silently -> "lean_fence_silent_overrun"
    (test_skill_lean.py::test_pools_under_byte_budget goes red for the "core" pool)
  a reword that contradicts report-template.md's own banner section without disclosure -> "guard_weakened"
    (no dedicated test pin on this sentence; caught at this contract's own review — the AFTER
    text is reviewed against report-template.md's exact banner definition, quoted in §0)
  an edited SKILL.md left un-mirrored -> "mirror_drift"
    (test_skill_parity / test_bundle_parity goes red)
  a parallel edit to intake.md:39 silently bundled in -> "scope_creep_undisclosed"
    (no dedicated test; §0 Issues/Risks already confirms intake.md is NOT a duplicate and is
    explicitly left untouched)
```

Glossary deltas: none — "banner" is report-template.md's own existing internal block vocabulary
  (established by report-plan-approve, reused by report-shape-scan-audit), not a new
  `.add/GLOSSARY.md` domain term.

Least-sure flag surfaced at freeze: [contract] whether "the banner then the ARC" (16 B, reusing
  the exact "X then Y" idiom this milestone already established twice) reads clearly inline vs. a
  heavier restructure — lowest confidence because it's a style/taste judgment, not a mechanical
  fact; if wrong: a trivial reword of this same one sentence, no re-freeze of the touch-point
  itself needed, cost is a second small pass.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 5/5 scenarios (100% — the whole task is one sentence AMEND; no partial-coverage case exists)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_skill_names_banner: assert the AFTER fragment is in SKILL.md AND the BEFORE fragment is not · covers: M1
  - test_mirrors_byte_identical: md5 over all 3 SKILL.md copies, assert equal · covers: M2
  - test_core_pool_under_budget: recompute the "core" pool's live byte total against its target · covers: M3
  - (R1 covered by the existing targeted regression batch, not a new test — see §6)
  - test_intake_untouched: assert intake.md's byte count/content unchanged · covers: R2
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/SKILL.md`, `.claude/skills/add/SKILL.md`, `add-method/src/add_method/_bundled/skill/add/SKILL.md`
  Exactly the §3 touch-point inventory; `report-template.md` and `intake.md` explicitly OUT of
  scope (both read-only anchors, 0 B delta). (The declaring line above is deliberately kept to
  one physical line — `_declared_scope`'s regex only reads the first line after "Scope (may
  touch):"; a v1 draft of this line wrapped the 3rd token onto a continuation line and it was
  silently dropped from `declared`, caught at the verify gate's own scope_violation check.)
Strategy (ordered batches): 1. write the RED test suite against the frozen §3 BEFORE/AFTER
  fragment and confirm RED. 2. apply the one AMEND edit verbatim across all 3 mirrors in one
  batch. 3. confirm GREEN on the task suite. 4. run the same targeted regression batch the
  sibling task used (34 files referencing SKILL.md / report-template.md / lean pools) to
  catch any wiring fallout.

Persona (optional): absent — generic; mechanical prose edit, no domain stance needed.
Known-problem fixes: mirror drift → planned fix: apply all 3 mirrors in the same Edit batch,
  then assert byte-identity in the test suite (same pattern as the sibling task).
Strategy actually used: as planned through step 3 (RED → AMEND all 3 mirrors → GREEN). Step 4
  deviated: the naive full regression sweep (48 files referencing SKILL.md) stalled on I/O wait
  under real disk contention (94% full, active Spotlight indexing — confirmed via `ps` wall-clock
  vs CPU-time, not assumed), twice, including a backgrounded retry. Split instead: (a) a 232-test
  fast subset (content/parity/lean-budget — excluding subprocess-heavy installer tests) ran clean
  in 42s; (b) the remaining 16 subprocess-heavy installer/global tests were verified by direct code
  read rather than execution — confirmed every SKILL.md reference in those 16 files is either a
  synthetic fixture placeholder (`.write_text("skill\n")`, disconnected from the real file) or an
  `.exists()`/unrelated-substring check (e.g. "graduate.md", "Depth by stage") — none can observe a
  line-109 prose edit. Disclosed here rather than silently treated as equivalent to execution.
Safety rule (feature-specific): none — no runtime/transactional surface; prose-only doc edit.
Code lives in: N/A — no `./src/`; this task edits SKILL.md directly at its Scope paths above.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 5/5 task suite + 232/232 fast regression subset, exit 0; remaining 16
      subprocess-heavy installer tests verified by direct code-read (see Strategy actually used)
      rather than execution, disclosed as a deviation from the planned approach
- [x] coverage did not decrease — N/A (prose task, no code coverage metric)
- [x] no test or contract was altered during build — only the 1 frozen edit + 3 mirror files touched
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — N/A, no runtime/shared-state surface
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only markdown edit
- [x] layering & dependencies follow CONVENTIONS.md — no new dependency; mirror-parity convention followed
- [x] a person reviewed and approved the change — the §3 freeze itself (Tin Dang, "Freeze §3 as
      drafted", via `add.py freeze --by "Tin Dang"` — properly this time, not hand-stamped); this
      gate auto-resolves on evidence under `autonomy: auto` per the frozen run mode

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] SKILL.md's compact pipeline sentence names the banner ahead of the ARC — confirmed by
      `sed -n '109p' add-method/skill/add/SKILL.md` showing the AFTER fragment verbatim
- [x] all 3 SKILL.md mirrors stay byte-identical post-edit — confirmed by md5 equality across
      canonical/dogfood/bundle (`b88a806bcc076a9916b7905a3f8f1755`, all 3)
- [x] the "core" pool holds its byte budget with the new +16 B edit — confirmed by re-measuring
      test_skill_lean.py::POOLS["core"] against the live tree (target 18186 B)
- [x] intake.md is untouched — confirmed by its byte count staying exactly 5322 B (unchanged) and
      `test_intake_untouched` passing

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read SKILL.md's full phase table + compact pipeline sentence
      (lines ~90-115) and report-template.md's banner/ARC/PLAN-SHAPE sections (lines 1-70) in full,
      not skimmed, both pre- and post-edit; confirmed the AFTER text accurately reflects
      report-template.md's actual render order (banner -> ARC -> PLAN/SHAPE -> ...) and that no
      adjacent clause in the sentence was disturbed

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct
      `sed -n '109p'` re-read of all 3 SKILL.md copies post-edit: still the exact line (in-place
      text substitution, no line insertion/deletion)
- [x] no anchor moved/renamed since Ground SHA — line 109 unchanged in position across the edit;
      no drift

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) could "SHAPE"/"banner" have been inserted somewhere
  irrelevant rather than at the actual pipeline sentence? No — Edit's old_string matched the exact
  §3-specified BEFORE fragment at its one occurrence in each of the 3 files, verified by direct
  `sed -n '109p'` re-read post-edit, not just the test. (2) is the mirror/byte-count evidence
  vacuous? No — AFTER is asserted present AND BEFORE asserted absent (test_skill_names_banner), and
  a dedicated test independently confirms the post-edit digest no longer matches the known pre-edit
  digest (test_no_longer_matches_pre_edit_digest) — a no-op edit would fail both. (3) is skipping
  execution of the 16 installer tests actually safe, or just convenient? Verified by reading every
  SKILL.md reference in all 16 files directly (not sampled) — confirmed synthetic-fixture or
  existence-only in every case; this is a stronger check than a green CI run would have given,
  since it confirms WHY they can't be affected, not just that they didn't fail this run.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — markdown prose edit, no code path, no secrets/injection surface
2. Concurrency: CLEAR — no runtime code, no shared state, no locking touched
3. Architecture: CLEAR — one isolated one-line text amendment; mirror-parity convention preserved;
   no new coupling, no new abstraction, no cross-file structural change
Verdict: PASS
Residue: none — the I/O-contention detour was a verification-strategy deviation (disclosed above),
  not a code/architecture residue
Binding: yes — mechanical (prose-only, no `risk: high` declared, disclosed+frozen touch-point inventory)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under autonomy: auto, per "yes, auto mode") · date: 2026-07-03
Reviewed by: Tin Dang · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): N/A — prose-only doc edit, no runtime signal; same qualitative
  signal as the sibling task (does a human notice the improvement, this time in SKILL.md's own
  always-loaded quick-reference rather than a phase guide).

### Decisions (ADR)
- [AI] specify — chose amend the existing sentence in-place with "the banner then"
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned through step 3 (RED → AMEND all 3 mirrors → GREEN). Step 4
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto, per "yes, auto mode"))

### Spec delta
None material — this task closed the milestone's 3rd and final exit criterion with no new forward
  product-spec surface opened. The one live style judgment (§1's ⚠ flag on "the banner then the
  ARC" inline phrasing) resolved silently: no human pushback at freeze or after, so it stands as
  decided, not carried forward as an open delta.

### Competency deltas
- [ADD · folded] the §5 "Scope (may touch):" declaration parser (`_declared_scope` in add.py) reads [folded foundation-version 62]
  ONLY the first physical line after the label — `re.search(r"^\s*Scope \(may touch\):.*$", body,
  re.M)` has no `DOTALL`, so `.` never crosses a `\n`. A Scope line wrapped across multiple physical
  lines (readable to a human, matches how §0/§1/§3 prose wraps everywhere else in this same file)
  silently drops every token past line 1 from `declared` — no warning, no lint, just a quiet gap
  that only surfaces later as a `scope_violation` at the gate. Always keep the token list on ONE
  physical line; wrap explanatory prose onto a SEPARATE following line instead (evidence: this
  task's own v1 draft dropped its 3rd mirror path this way, caught at `gate PASS`).
- [ADD · folded] the §5 scope-lock's protection is only as real as its SEQUENCING: `declared` + [folded foundation-version 62]
  the touch-baseline snapshot are captured ONCE, at the tests→build phase crossing
  (`_build_entry`'s scope-snapshot block) — never re-derived at gate time. Editing files BEFORE
  crossing tests→build (e.g. applying the AMEND while still nominally in `tests`) means those edits
  are already baked into the snapshot, so the gate sees zero delta and the check silently no-ops —
  a clean `gate PASS` in that case proves nothing about scope discipline. Editing files AFTER the
  crossing (the documented/correct order) is what actually exercises the check. Evidence: the
  sibling task `report-shape-scan-audit` edited all 6 mirrored files before ever calling `advance`
  into build, so its own scope-lock never fired despite 4 of its 6 touched files also being
  undeclared past line 1 — an accidental pass, not a verified one. This task followed the correct
  order and the check caught a real gap. `add.py phase build <slug>` re-runs the identical guard
  stack on demand — the documented recovery path (matches the project's own prior
  `build_tampered` re-cross precedent), not a workaround.

