# MILESTONE: Faceted §5 build strategy

goal: the build phase carries a structured, domain-anchored implementation strategy — algorithm approach, data strategy, dev pattern, and optimization stance are declared facets (not one overloaded line), each anchored upstream (§0/§1/§3), harvested per-facet into the §7 Decisions (ADR) block, and cross-cited by §7 Watch
rationale: intake bucket=one-task-gap → micro-milestone (2026-07-07): senior review of TASK.md.tmpl found §5's single `Strategy (ordered batches)` line conflates build order · architecture pattern · issue advice · persona stance, so builds skip the domain implementation decision (algorithm/data/pattern/optimization); no active milestone's goal covers method-template structure
stage: mvp · status: active · created: 2026-07-07T03:57:31+00:00
release: 1.18.0

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
- [x] strategy-facet-block   depends-on: none                 — split §5 Strategy into Approach/Data/Pattern/Optimization facets in both template twins + guide/doc ripples, lean-absorbed
- [x] facet-adr-harvest      depends-on: strategy-facet-block — engine harvests one [AI] ADR line per diverged facet; §7 Watch cross-cites Optimization stance

## Exit criteria (observable; map each to the task that delivers it)
- [x] A new task's §5 renders the four facet fields with upstream-anchor hints; a fast task renders the single collapsed `Approach:` line        (← strategy-facet-block; facet-adr-harvest's own scaffold rendered them live)
- [x] `add.py check` and the template guard suites stay green — one lean-budget rebaseline occurred, but it was CONTRACT-SIGNED (M6, phases pool 41190→41605, ledgered), not silent; the "NO rebaseline" wording here was drafted before the freeze made the signed exception explicit        (← strategy-facet-block)
- [x] At task done, a filled facet appears as its own `[AI]` line in §7 Decisions (ADR); zero filled facets collapse to the legacy block        (← facet-adr-harvest; self-dogfooded in its own §7)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : TASK.md.tmpl +4 facet lines / TASK.fast.md.tmpl +1 collapsed line (4-twin lockstep each) · add.py `_facets()` loop in _stamp_adr_record (+20 lines, ENGINE_MD5 78baf42b→35e7f701, trio synced, PKG unchanged) · §7 Watch line cites the Optimization stance · 2 new guard suites (test_strategy_facets 14 · test_facet_adr_harvest 9) · 3 ceiling pins migrated forward contract-signed (skill-lean 41605 · domain-test-mapping lockstep · taskmd-lean 11400) · fresh-checkout skip-tolerance in both new twin suites · SEAMS.md scope-token-grammar anchor re-pinned twice (4756→4766 pre-existing, →4786 this milestone's growth)
- skill   : phases/5-build.md gains the **Strategy facets** bullet (3 trees; ~100 B compressed in-file + M6-signed phases-pool rebaseline)
- book    : docs/07-step-5-build.md gains "## Choosing the implementation strategy" (3 git-tracked twins + .add/docs consistency copy)

### Cross-task evidence   (one row per task)
- strategy-facet-block : gate=PASS · tests=3132 run/3130 green + 2 pre-existing-on-main healed (14 new, red-first) · residue=none (💭 two hint-tests borrow coverage from a sibling, mutation-proven)
- facet-adr-harvest    : gate=PASS · tests=3141/3141 green (9 new, red-first) · residue=none (2 scope_violation self-heals: stray gitignored tmp/ commit-message files — removed, fresh re-snapshot, honest re-gate)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied: criterion 1 ← strategy-facet-block ship row (+ facet-adr-harvest's own scaffold rendering the facets live) · criterion 2 ← both tasks' green suites + the signed rebaseline ledger · criterion 3 ← facet-adr-harvest ship row (self-dogfooded §7)
- goal: the build phase carries a structured, domain-anchored implementation strategy — proven end-to-end by facet-adr-harvest's own §7 Decisions block, where the four facets it declared at build render as four harvested [AI] ADR lines

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from the Close ship-review above on a feature branch; the human reviews + merges
- [ ] verify ENGINE_MD5/PKG pins re-pinned honestly (facet-adr-harvest moves the engine)
- [ ] bundle into the next release cut (release.md); human runs tag/publish
