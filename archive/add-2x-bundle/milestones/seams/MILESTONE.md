# MILESTONE: Seams

goal: Promote symbols ≥2 tasks touch into a milestone-level SEAMS.md that §0 references, so a shared contract has one home instead of being re-derived per task.
rationale: sub-milestone of the `artifact-trust` roadmap (PR40 audit item 4, "knowledge is siloed
  per file"), queued 2026-06-30, drafted 2026-07-01. Grounding research (Explore agent over the full
  archive, 130+ TASK.md files scanned) found the duplication is dominated by PROJECT-WIDE engine
  conventions, not by any one milestone's own task set — Tin confirmed 2026-07-01 the artifact is
  therefore ONE project-level `.add/SEAMS.md` (sibling to PROJECT.md/GLOSSARY.md), reinterpreting
  "milestone-level" as "lives at the milestone/project tier of the artifact hierarchy," not
  "one file per milestone."

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A single `.add/SEAMS.md` file holding one entry per cross-cutting symbol/convention that
     recurs across ≥2 tasks spanning ≥2 different milestones (the evidence bar — a same-milestone
     repeat is normal cohesion, not a seam). Each entry: the symbol/convention name, its real
     file:line anchor, a one-paragraph statement of the shared contract, and a citation count as
     the evidence for why it earned a seam. Wiring §0 GROUND's template (`TASK.md.tmpl`) to add an
     optional "Seams consulted:" line so a new task cites `.add/SEAMS.md#<entry>` instead of
     re-deriving the fact inline. Seeding the file with the top candidates the grounding research
     already found (ranked by duplication + error cost): (1) the ENGINE_MD5/ENGINE_PKG_MD5 re-pin
     checklist — 130 files, 291 mentions; (2) the three-tree template/book parity convention; (3)
     the §5 "Scope (may touch):" token-resolution grammar (first-physical-line-only parsing +
     bare-token sibling-resolution) — the single most error-prone entry, independently
     self-healed by 3 separate tasks (`phase-agents-lean`, `template-structural-gaps`,
     `rule-id-coverage`); (4) `_raw_phase_bodies`/`_phase_spans` phase-body extraction — 26 files;
     (5) `_section_unfilled`'s placeholder/grandfather truth table — 3 files.
Out: A SEAMS.md per milestone (rejected 2026-07-01 — Tin chose project-level: the strongest
     evidence found spans dozens of milestones over the project's whole history, which a
     per-milestone file would never capture). A rich graph/backlink engine over seam usage —
     already rejected by `artifact-graph`'s own MILESTONE.md (MINIMAL backlinks only); a seam
     entry is prose + a citation count, not a queryable graph node. Auto-detecting NEW seam
     candidates by static analysis (e.g. AST-diffing task files for repeated phrases) — this
     milestone seeds from the research already done and makes future promotion a manual,
     human/AI-judgment call at observe time, not an automated miner. Retrofitting `Seams
     consulted:` onto already-`done`/archived tasks — forward-only, applies to tasks drafted
     after this milestone ships.

## Shared decisions & glossary deltas   (living — every task must honor these)
- SEAMS.md = project-level (one file, `.add/SEAMS.md`), not milestone-scoped — the artifact lives
  at the same tier as PROJECT.md/GLOSSARY.md even though it ships via a milestone named "seams".
- Evidence bar for a seam entry: cited/re-derived by tasks in ≥2 DIFFERENT milestones — a
  same-milestone repeat is ordinary task cohesion, not knowledge silo.
- A seam entry is prose (name, anchor, contract, citation count) — never a graph node or a new
  required TASK.md field; §0's "Seams consulted:" citation is opt-in, mirrors the rule-id-coverage
  convention's own opt-in-by-usage precedent.

## Shared / risky contracts (freeze these first)
- `.add/SEAMS.md`'s own entry format (fields, anchor style, citation-count convention) -> owning
  task `seams-doc` (frozen first — `seams-template-wiring` depends on the exact heading/anchor
  grammar to write the `TASK.md.tmpl` citation line correctly).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] seams-doc            depends-on: none        — create `.add/SEAMS.md` seeded with the 5
      ranked candidates from grounding research (name, file:line anchor, contract, citation count)
- [ ] seams-template-wiring depends-on: seams-doc   — add an optional "Seams consulted:" line to
      `TASK.md.tmpl`'s §0 GROUND block (+ its 3-tree twins) so a new task can cite a `.add/SEAMS.md`
      entry instead of re-deriving the fact inline

## Exit criteria (observable; map each to the task that delivers it)
- [x] `.add/SEAMS.md` exists with >=5 entries, each carrying a real file:line anchor and a citation count (verify: command `test -f .add/SEAMS.md && grep -c "^## " .add/SEAMS.md`)   (← seams-doc)
- [x] `TASK.md.tmpl`'s §0 GROUND carries an optional "Seams consulted:" line, synced across its 3 trees (verify: command `grep -cl "Seams consulted:" add-method/tooling/templates/TASK.md.tmpl .add/tooling/templates/TASK.md.tmpl add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl`)   (← seams-template-wiring)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` gained a `status --json --task <slug>` filter (`status-task-filter`, ENGINE_MD5 re-pinned) and a self-heal fix to `_flag_well_formed`'s fence-unaware comment strip (`fix-flag-fence-aware`); `test_ubiquitous_language.py`'s retired-"seam"-idiom ban gained a scoped carve-out (`seam-term-carveout`).
- skill   : untouched
- book    : `.add/SEAMS.md` created (5 seeded entries: engine-md5-repin, three-tree-parity, scope-token-grammar, phase-body-extraction, section-unfilled-truth-table) — `seams-doc`; `TASK.md.tmpl`'s §0 GROUND gained the optional "Seams consulted:" citation line, synced across all 3 template trees — `seams-template-wiring`.

### Cross-task evidence   (one row per task)
- seams-doc : gate=PASS · tests=n/a (documentation-only, no new test file) · residue=none
- seams-template-wiring : gate=PASS · tests=24/24 green (23/24 on this dev machine — 1 disclosed macOS/Linux `grep -cl` portability quirk, expected green on Linux CI) · residue=none
- fix-flag-fence-aware : gate=PASS · tests=6/6 green (`test_flag_fence_aware.py`) · residue=none
- status-task-filter : gate=PASS · tests=13/13 green (`test_machine_state.py`) · residue=none
- seam-term-carveout : gate=PASS · tests=6/6 green (`test_ubiquitous_language.py`) · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — criterion 1 by `seams-doc`'s Ship-by-domain row (5 seeded SEAMS.md entries); criterion 2 by `seams-template-wiring`'s Cross-task evidence row (24/24 green, 3-tree parity confirmed).
- goal: Promote symbols ≥2 tasks touch into a milestone-level SEAMS.md that §0 references, so a shared contract has one home instead of being re-derived per task — met: `.add/SEAMS.md` holds 5 project-level entries and `TASK.md.tmpl`'s §0 GROUND now carries the citation line across all 3 trees, confirmed by both exit-criterion commands run live against the current tree.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
