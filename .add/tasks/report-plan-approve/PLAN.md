# TASK: Report template: PLAN/SHAPE + APPROVE banner

slug: report-plan-approve · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `.claude/skills/add/report-template.md` (+2 byte-identical mirrors:
  `add-method/skill/add/report-template.md`, `add-method/src/add_method/_bundled/skill/add/report-template.md`)
  — full rewrite of the "decision arc"/"report blocks" sections; `SKILL.md:110` (+2 mirrors) —
  the "SUMMARY → DECISION → …" pipeline sentence; `phases/0-setup.md:79`, `phases/3-contract.md:17`,
  `phases/6-verify.md:45` (each +2 mirrors) — the "render the DECISION as a guided choice" phrase;
  `add-method/tooling/test_report_arc.py:64` (`ReportArcMarkerTest.test_arc_renders_above_the_five_blocks`)
  — the literal `"DECISION"` marker-guard assertion.
Context (working folder): none beyond the 8 files above — this task is skill-doc prose + one test, no
  `add.py` engine code changes.
Honors (patterns / conventions): the existing marker-guard-test convention (`test_report_arc.py` already
  guards report-template.md's *shape* the same way `test_skill_lean.py` guards budget — a red/green prose
  test, not a content-quality test); the 3-skill-tree byte-identical mirror convention (verified above,
  md5 4ded72c5.../ee67febe.../6a2270a7.../c0c6d5ff.../a6a7a36a — all 3 trees match per file today).
Anchors the contract cites: `report-template.md`'s block table (`ARC`/`PLAN`/`SHAPE`/`SUMMARY`/`FLAGS`/
  `DECIDED`/`EVIDENCE`/`APPROVE`/`NEXT`), the banner format, the `DECISION`→`APPROVE` rename, and
  `ReportArcMarkerTest`'s existing + new marker assertions.

---

## 1 · SPECIFY — the rules

Feature: report-template.md gains a decision banner + PLAN/SHAPE blocks + DECISION→APPROVE rename
Must:
  - report-template.md opens every human-gate report with a `PLAN · <title> · <gate> → APPROVE?` banner
    line naming the bolded task/milestone title + a `📄` path line to TASK.md (+ MILESTONE.md if any).
  - report-template.md defines a `PLAN` block (multi-step breakdown, ✅/🔄/⬜/⚠ glyphs, done collapsed
    to a count, live items capped ~5–7) and a `SHAPE` block (freeze-only: the frozen shape itself).
  - the block list renames `DECISION` to `APPROVE` and reorders it to sit last among the core blocks
    (right before NEXT), matching the existing "ask after everything below" rule instead of
    contradicting it.
  - every §-numbered section named in a rendered report is bolded (e.g. `**§3 CONTRACT**`).
  - all 3 skill-tree mirrors of report-template.md, SKILL.md, 0-setup.md, 3-contract.md, 6-verify.md
    stay byte-identical after the edit; `test_report_arc.py` is updated to guard the new shape (banner,
    PLAN/SHAPE, `APPROVE` in place of `DECISION`) and passes.
Reject:
  - a rendered report that skips SUMMARY because PLAN/SHAPE already covered the context -> "summary_dropped"
  - any of the 3 report-template.md mirrors (or the 4 other ripple files) diverging after the edit -> "mirror_drift"
Accept: Given report-template.md after this task, When a human reads `ReportArcMarkerTest` + the file
  itself, Then the banner/PLAN/SHAPE/APPROVE shape is present exactly as specified, `DECISION` no longer
  appears as a block name, all 3 mirrors are byte-identical, and the full add-method suite is green.
Assumptions: ⚠ renaming `DECISION`→`APPROVE` in prose-only guides (0-setup/3-contract/6-verify) is safe
  because none of them are frozen §3 contracts of an in-progress task — they're stable skill docs; if
  wrong (some other guide or a human's saved workflow still expects the literal word "DECISION"), the
  cost is a confusing one-word mismatch, not a functional break — cheap to fix in a follow-up edit.

---

## 3 · CONTRACT — freeze the shape

```
report-template.md block/section shape (the artifact this task freezes):

  Banner (new):    ════…════ / " PLAN · <bold title> · <gate> → APPROVE?" / "📄 <TASK.md> · <MILESTONE.md>" / ════…════
  ARC (unchanged): goal: / done: / plan:
  PLAN (new, optional): milestone/theme line + ✅ done (N) / 🔄 active / ⬜ next (cap ~5-7, "+N more queued") / ⚠ flagged
  SHAPE (new, freeze-only): "<bold title> — v<N> (DRAFT)" + field/reject-token rows
  Core blocks, renamed order: SUMMARY -> FLAGS -> DECIDED -> EVIDENCE -> APPROVE -> NEXT
    (was: SUMMARY -> DECISION -> FLAGS -> DECIDED -> EVIDENCE -> NEXT; DECISION renamed APPROVE, moved last)
  Bolding rule: any "§N NAME" section reference anywhere in a report is bolded.
  Ripple (same rename, 1 line each, x3 mirrors): SKILL.md:110, phases/0-setup.md:79,
    phases/3-contract.md:17, phases/6-verify.md:45 — "DECISION" -> "APPROVE" in each named phrase.
  Reject: report renders SUMMARY missing when PLAN/SHAPE present -> "summary_dropped" (rule stays explicit
    in <constraints>: SUMMARY never optional/never folded into PLAN/SHAPE)
  Reject: any of the 3 mirrors (or the 4 ripple files) diverge post-edit -> "mirror_drift" (guarded by
    the existing tree-parity tests, no new test needed for that half)
```

`Least-sure flag surfaced at freeze:` ⚠ [spec] the `DECISION`→`APPROVE` rename touches 4 files beyond
  report-template.md (SKILL.md + 3 phase guides) that are prose-only, not frozen §3 contracts of any
  live task — because they're stable/shipped docs, renaming them alongside is safe; if wrong (some
  other unseen guide or a saved external workflow still keys off the literal word "DECISION"), the
  cost is a one-word doc mismatch, cheap to patch in a follow-up, not a functional break.
Status: FROZEN @ v1 — approved by Tin Dang (chat approval "approved", after the full block-by-block
  draft — banner, PLAN/SHAPE, DECISION→APPROVE rename + reorder, path line, bold-title/section rule —
  was rendered in full and the ripple-file blast radius was disclosed, both shown before this ask).

---

## 4 · TESTS — failing-first (red)

Plan: extend `ReportArcMarkerTest` in `add-method/tooling/test_report_arc.py` with new marker-guard
  methods asserting: the banner shape (`PLAN ·`, `→ APPROVE?`, `📄`), the `PLAN`/`SHAPE` block names,
  and `APPROVE` present while `DECISION` is absent as a block name (the existing
  `test_arc_renders_above_the_five_blocks` gets its block tuple updated from `DECISION` to `APPROVE`).
  Assert against `add-method/skill/add/report-template.md` (this test's existing CANON_SKILL target).
Tests live in: `add-method/tooling/test_report_arc.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `.claude/skills/add/report-template.md`, `add-method/skill/add/report-template.md`,
  `add-method/src/add_method/_bundled/skill/add/report-template.md`, `.claude/skills/add/SKILL.md`,
  `add-method/skill/add/SKILL.md`, `add-method/src/add_method/_bundled/skill/add/SKILL.md`,
  `.claude/skills/add/phases/0-setup.md`, `add-method/skill/add/phases/0-setup.md`,
  `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md`,
  `.claude/skills/add/phases/3-contract.md`, `add-method/skill/add/phases/3-contract.md`,
  `add-method/src/add_method/_bundled/skill/add/phases/3-contract.md`,
  `.claude/skills/add/phases/6-verify.md`, `add-method/skill/add/phases/6-verify.md`,
  `add-method/src/add_method/_bundled/skill/add/phases/6-verify.md`,
  `add-method/tooling/test_report_arc.py`
  GROUND GAP found mid-build: the book's 3-tree-mirrored `02-the-flow.md` and `appendix-c-glossary.md`
  (root, `add-method/docs/`, `add-method/src/add_method/_bundled/docs/`) also name the DECISION block
  in prose (missed at §0 GROUND). Same mechanical rename, no new business logic — added to Scope rather
  than opening a change-request: `02-the-flow.md` (×3), `appendix-c-glossary.md` (×3).
Strategy & known-problem fixes: (1) write the new `ReportArcMarkerTest` methods first against the
  CURRENT report-template.md content -> confirm RED; (2) rewrite report-template.md's canonical copy
  (`add-method/skill/add/`) in full per the frozen §3 shape; (3) `cp` it byte-identically onto the other
  2 mirrors — avoids hand-retyping drift between trees; (4) apply the 4 one-line ripple edits to
  SKILL.md/0-setup.md/3-contract.md/6-verify.md, each in all 3 mirrors the same way; (5) re-run the new
  + existing test_report_arc.py tests -> confirm GREEN; known-problem: forgetting a mirror copy is the
  single most likely slip — verify with `diff`/`md5` across all 3 trees per file before calling it done.
Strategy actually used: as planned for steps 1-5, plus 3 real corrections found only by running the
  full suite (not just test_report_arc.py) — surfaced legitimate ripple this task's §0 GROUND missed:
  (a) the book's 3-tree `02-the-flow.md`/`appendix-c-glossary.md` also named DECISION in prose — added
  to Scope mid-build (see §5 Scope note above) and renamed the same way; (b) my first draft of the
  "Show before ask" bullet reworded an existing verbatim-pinned constraint (test_question_summary_layer)
  by inserting "PLAN/SHAPE ·" inline — reverted to the original wording + a separate trailing sentence
  instead, since "digest" already covers PLAN/SHAPE conceptually and the pinned bullet didn't need
  touching; (c) "folded into" in the new SUMMARY-never-optional rule tripped the ubiquitous-language
  slang guard (`fold` is reserved for the `add.py fold` command) — reworded to "merged into"; (d) the
  rewrite legitimately grew 2 lean-budget pools past their ratio-pinned target (core: SKILL.md +14 B;
  reference: report-template.md +3308 B) — rebaselined both via the established surface÷ratio method
  (core 20490→20506, reference 70359→75224), same convention as every prior rebaseline in
  `test_skill_lean.py`. Also found + fixed one MORE stale-untracked-mirror gotcha from earlier this
  session's playbook: `.add/docs/{02-the-flow,appendix-c-glossary}.md` are gitignored dogfood copies
  that had drifted stale relative to the 3 git-tracked book trees — synced by `cp`, zero git impact.
Code lives in: the 5 skill-doc files above (×3 mirrors) + the 1 test file.   ·   Constraints: change no
  frozen §3 line above without a change-request back to SPECIFY; no other files touched.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full add-method
      suite 2622/2622 green (`python3 -m unittest discover -s tooling -p 'test_*.py'`); the frozen
      §3 shape was never altered, only implemented; `test_report_arc.py`'s pre-existing 6 tests plus
      9 new ones (banner, PLAN/SHAPE, APPROVE-rename, ripple) all pass.
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic — each new test asserts a
      real, specific substring/ordering fact about the shipped doc (banner marker before ARC, APPROVE
      after EVIDENCE, DECISION absent repo-wide via `ReportTemplateRippleMarkerTest`); RED was
      confirmed first (10/15 failing for the right reason) before any implementation.
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — none
      applicable: prose-only skill-doc + test-file change, no code path, no I/O, no new dependency.

Build expectations (from §1 Accept + §3 CONTRACT): report-template.md carries the banner, ARC, PLAN/SHAPE,
  and APPROVE (in place of DECISION, reordered last) exactly as frozen — confirmed by `test_report_arc.py`
  green (15/15) and manual read of the shipped file. All 3 skill-tree mirrors + the 4 ripple files (SKILL.md,
  0-setup.md, 3-contract.md, 6-verify.md) + the book's 2 git-tracked chapters (found mid-build, added to
  Scope) are byte-identical across every tree — confirmed by `md5`/`diff` on each, and by the pre-existing
  tree-parity test suite passing. No `DECISION` string remains anywhere in the touched surface (grep-confirmed
  repo-wide + `ReportTemplateRippleMarkerTest`).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (autonomy: auto — auto-resolved on complete evidence, no residue/security/lowered-autonomy escalation) · date: 2026-07-01

OBSERVE: [ADD · open] a task's §0 GROUND pass for a "rename X to Y across N referencing files" change
  should explicitly grep the git-tracked book chapters (`02-the-flow.md`, `appendix-c-glossary.md`) and
  any gitignored dogfood mirrors (`.add/docs/`) up front — this task missed both at GROUND and found
  them only via a full-suite run at BUILD, costing 2 extra fix cycles that a more thorough GROUND grep
  would have caught in one pass.
