# MILESTONE: UDD design intake

goal: give the UDD design loop an explicit per-axis design intake (FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN) the agent runs WITH the human as a new front beat before render-capture-confirm — convention-only (no engine render), identity values stay human-owned
rationale: micro-milestone (one-task-gap rule) — enhances the existing UDD pillar (not a new theme, not a frozen-scope change); one focused convention-only task, housed in its own milestone for ledger attribution + exit criteria. Sizing confirmed via intake interview: new front beat · pure convention (engine never renders) · single task.
stage: mvp · status: active · created: 2026-06-26T07:00:39+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a new front beat `design-intake` in `design.md` (the UDD loop) — the agent interviews the human on four axes (FIDELITY: lo-fi wireframe / hi-fi mockup / production · CONCEPT: idea/mood/direction · LAYOUT: structure/grid/hierarchy · VISUAL DESIGN: color/type/spacing/imagery) and records the answers before review-domain; the recorded intake then informs the existing beats. The `DESIGN.md` template scaffold gains a place to capture the four axes. Propagated across the 3-tree skill mirror; the book UDD chapter + GLOSSARY gain the four axis terms.
Out: any engine change (the engine never renders — pure convention) · reshaping `tokens.json` / `catalog.json` / `prototypes/<name>.json` (read-only, unchanged) · auto-picking identity values (brand color/palette/typeface stay human-owned, surfaced to decide).

## Shared decisions & glossary deltas   (living — every task must honor these)
- Convention-only: no `add.py` / state.json / ENGINE_MD5 change — the four axes live in the guide + DESIGN.md template, recorded by the agent.
- Identity values (color/type) stay human-owned per `udd-tokens.md` — VISUAL DESIGN intake SURFACES them, never auto-picks.
- The four axes are: FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN (named consistently across guide, template, book, GLOSSARY).

## Shared / risky contracts (freeze these first)
- (none — convention/guide-level change; no machine contract reshaped)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] design-intake-beat   depends-on: none   — add beat 0 `design-intake` (4-axis interview) to design.md + DESIGN.md template + 3-tree mirror + book/GLOSSARY terms

## Exit criteria (observable; map each to the task that delivers it)
- [x] `design.md` opens the UDD loop with a `design-intake` beat that interviews the four axes before review-domain   (← design-intake-beat)
- [x] the `DESIGN.md` template has a section to capture the four axes' answers   (← design-intake-beat)
- [x] the four axis terms appear in the book UDD chapter + GLOSSARY, consistently named   (← design-intake-beat)
- [x] the 3-tree skill mirror is byte-consistent (parity tests green) and no engine/ENGINE_MD5 change   (← design-intake-beat)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `DESIGN.md.tmpl` gains a `## Design intake` section (×3 trees); `add.py` / state.json / ENGINE_MD5 / add_engine UNTOUCHED (convention-only invariant held)
- skill   : `design.md` UDD loop gains beat 0 `design-intake` (four axes + a hard rule), `SKILL.md` one-liner updated (×3 trees, byte-identical); lean fence rebaselined 50098→51732 (ratio 0.75 kept)
- book    : `14-foundation.md` narrates five beats; `appendix-c-glossary.md` defines the four axis terms (×4 book trees synced: canonical · repo-root · .add/docs · _bundled/docs)

### Cross-task evidence   (one row per task)
- design-intake-beat : gate=PASS · tests=1995 green (+15 new in test_design_intake_beat.py) · check 425/0 · residue=one disclosed test region-slice DEFECT fixed via re-cross tests→build (tamper-tripwire honored; not a weakening)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — EC1/EC2 ← skill+tooling rows; EC3 ← book row; EC4 ← skill row (byte-identical ×3 + engine untouched)
- goal: give the UDD loop an explicit per-axis design intake before render-capture-confirm — proven by the rendered `## Design intake` section + the five-beat `design.md` loop, all convention-only (ENGINE_MD5 unchanged).

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] commit the change on a feature branch (`feat/udd-design-intake`) — guide+template+book+test, all 3/4 trees
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] fold the observe-step competency deltas into the foundation (`add.py fold`), then archive the milestone
- [ ] bundle into the next release cut (orthogonal to stage; no version bump on its own) — `release.md`
