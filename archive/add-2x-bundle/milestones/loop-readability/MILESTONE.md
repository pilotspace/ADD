# MILESTONE: ADD loop readability — human-scannable output across every phase

goal: every report/ask the AI gives a human at a phase's decision point (the ARC +
  SUMMARY/DECISION/FLAGS/DECIDED/EVIDENCE/NEXT blocks per report-template.md) is easy to
  scan at a glance across all 8 phases, without growing report-template.md past its
  pinned reference-pool byte-budget
rationale: new-major (intake, unconfirmed) — no active milestone's goal covers the AI's
  OWN reporting/asking behavior; requested to dogfood the new MILESTONE.md.tmpl UI/UX
  hint (persona-teacher vocabulary + Claude Code's frontend-design distinctiveness
  principle) against a real target. CORRECTED mid-draft: "human readable ADD loop" means
  what the AI tells/asks the human (chat reports), NOT add.py's own printed CLI text —
  that first framing was wrong and is fully replaced below, not layered on top
stage: mvp · status: active · created: 2026-07-02T15:52:13+00:00
release: 1.15.0

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  applying the Scope hint's own vocabulary to chat text, term by term, honestly —
  not just citing it: INFORMATION ARCHITECTURE = the ARC + 6-block order itself;
  VISUAL HIERARCHY = SUMMARY-first, the ONE decision never buried under FLAGS/EVIDENCE,
  the ▶-marked recommendation; INTERACTION PATTERN = the guided-choice DECISION block
  and its AskUserQuestion mapping; COMPONENT STATES = each block's populated-vs-empty
  state (report-template.md's own "write none rather than dropping one"); a text-
  equivalent ACCESSIBILITY FLOOR = plain language, no unexplained jargon/shorthand
  (already required of me, named explicitly here); USER JOURNEY = the human meeting
  one of these reports at every one of the 8 phase gates, checked for a consistent
  shape; SIGNATURE ELEMENT = the one thing this reporting style is recognized by,
  named explicitly, not left implicit
Out: DESIGN TOKENS and RESPONSIVE BREAKPOINTS — screen/viewport-only terms with no
  honest chat-text equivalent; force-fitting them would be exactly the generic
  box-ticking the hint warns against · `add.py`'s own printed CLI text
  (`status`/`guide`/`advance`/`gate` — ENGINE output, not an AI report) · phase-guide
  teaching content aimed at the AI unless it directly shapes what gets told to the
  human · a screen/GUI (chat text — no DESIGN.md loop) · any reference-pool
  byte-budget rebaseline (test_skill_lean.py POOLS) without explicit human approval

> UI/UX in scope? Name it precisely, not "make it nice" — information architecture ·
> interaction pattern · visual hierarchy · design tokens · component states ·
> accessibility floor (WCAG AA) · responsive breakpoints · user journey
> (`.add/personas-teacher/design/`). Precise ≠ distinctive: skip generic AI-design
> defaults (cream+serif+terracotta · near-black+neon · broadsheet-hairline) and name ONE
> deliberate signature element instead (Claude Code's `frontend-design` skill). A UI
> feature also triggers DESIGN.md via the `add` skill's design.md.

## Shared decisions & glossary deltas   (living — every task must honor these)
- `report-template.md` is reference-pool budget-locked (test_skill_lean.py POOLS,
  ratio 0.68) — a scanability fix must hold or shrink bytes; any growth is a FLAG for
  the human, never an auto-rebaseline (see feedback_lean_over_budget_bump precedent)
- engine CLI text (add.py's own prints) is explicitly OUT — do not touch add.py in
  this milestone; a future milestone can cover engine output on its own merits

## Shared / risky contracts (freeze these first)
- none — one task, one artifact family (report-template.md's shape + its per-phase
  application), no cross-task schema to freeze

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] report-shape-scan-audit   depends-on: none   — report-template.md's ARC + 6-block
  shape audited for real scanability against report-template.md's OWN stated rules
  (summary-first, one decision, guided-choice), tightened within the pinned budget;
  any of the 8 phase guides whose gate-reporting cue drifts from the shape is named
- [x] skill-banner-cue   depends-on: none   — SKILL.md:108-110's compact pipeline map cites
  SHAPE already but omits report-template.md's decision banner ("rendered first, above
  everything"); not one of "the 8 phase guides" by this milestone's literal Scope, but the
  Out clause's own UNLESS carve-back applies (the sentence directly shapes what gets told
  to the human) — surfaced by report-shape-scan-audit's own disclosed flag, resolved via an
  add-advisor consult (fix now, recommended) rather than left as a silent gap

## Exit criteria (observable; map each to the task that delivers it)
- [x] report-template.md's shape is demonstrably easier to scan (cite the concrete
      friction found + the fix) while report-template.md's md5/byte count holds at or
      under its current reference-pool budget, or any growth sits as a named FLAG
      awaiting human approval                      (← report-shape-scan-audit)
- [x] all 8 phase guides' "what to tell the human at this gate" cues are checked
      against report-template.md's shape; any drift is named, not silently left
                                                     (← report-shape-scan-audit)
- [x] SKILL.md's compact pipeline sentence (core pool, always-loaded — higher leverage
      than any single phase guide) also names the banner, matching report-template.md's
      actual render order                            (← skill-banner-cue)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py / state.json / templates — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — what shipped, or "untouched">
- book    : <docs/* — what shipped, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
