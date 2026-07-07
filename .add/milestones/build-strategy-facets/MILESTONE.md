# MILESTONE: Faceted §5 build strategy

goal: the build phase carries a structured, domain-anchored implementation strategy — algorithm approach, data strategy, dev pattern, and optimization stance are declared facets (not one overloaded line), each anchored upstream (§0/§1/§3), harvested per-facet into the §7 Decisions (ADR) block, and cross-cited by §7 Watch
rationale: intake bucket=one-task-gap → micro-milestone (2026-07-07): senior review of TASK.md.tmpl found §5's single `Strategy (ordered batches)` line conflates build order · architecture pattern · issue advice · persona stance, so builds skip the domain implementation decision (algorithm/data/pattern/optimization); no active milestone's goal covers method-template structure
stage: mvp · status: active · created: 2026-07-07T03:57:31+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  §5 faceted strategy block in BOTH template twins (TASK.md.tmpl; TASK.fast collapses to one `Approach:` line — collapse, never skip) · upstream anchoring guidance (§0 Honors / §1 Framings / §3 Schema) · ⚠ lowest-confidence-facet flag + advisor-consult hint on `risk: high` · fill-timing stated (facets draft at the tests→build crossing) · engine per-facet ADR harvest ("as planned" collapses to one line) · §7 Watch cites the declared Optimization stance · phase-guide/doc/streams prose ripples · all growth absorbed under existing lean budgets (compress, no rebaseline)
Out: no new engine gate (facets stay advisory, per strategy-soft-not-hard) · no persona-schema changes · no new subcommand · no book-chapter rewrite beyond the §5 ripple in docs/07 · no change to the §5 Scope token grammar or its parser

## Shared decisions & glossary deltas   (living — every task must honor these)
- Strategy stays PREFERRED, never enforced (strategy-soft-not-hard): facets guide the builder and feed audit; they never lower or add a gate.
- Facets are derivations, not a second design phase: each cites its upstream anchor (§0 Honors · §1 Framings weighed · §3 Schema), like `Seams consulted`.
- Glossary delta: `Strategy facet: one declared dimension of the §5 implementation strategy — Approach (algorithm/technique) · Data strategy · Pattern · Optimization stance`.
- Template hazards honored: no bare `<word>` placeholder collisions (test_scope_decl_template tag census) · no unmatched bare `<!--` · no stray backticks in §5 comments (parse as scope tokens) · nothing inserted between the §5 Scope line and its declaring position.

## Shared / risky contracts (freeze these first)
- §5 facet field names + fast-lane collapse rule -> owning task strategy-facet-block
- per-facet ADR harvest line grammar -> owning task facet-adr-harvest (consumes strategy-facet-block's field names)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] strategy-facet-block   depends-on: none                 — split §5 Strategy into Approach/Data/Pattern/Optimization facets in both template twins + guide/doc ripples, lean-absorbed
- [ ] facet-adr-harvest      depends-on: strategy-facet-block — engine harvests one [AI] ADR line per diverged facet; §7 Watch cross-cites Optimization stance

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A new task's §5 renders the four facet fields with upstream-anchor hints; a fast task renders the single collapsed `Approach:` line        (← strategy-facet-block)
- [ ] `add.py check` and the template guard suites stay green with NO lean-budget rebaseline        (← strategy-facet-block)
- [ ] At task done, a diverged facet appears as its own `[AI]` line in §7 Decisions (ADR); "as planned" collapses to one line        (← facet-adr-harvest)

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
- [ ] open a PR from the Close ship-review above on a feature branch; the human reviews + merges
- [ ] verify ENGINE_MD5/PKG pins re-pinned honestly (facet-adr-harvest moves the engine)
- [ ] bundle into the next release cut (release.md); human runs tag/publish
