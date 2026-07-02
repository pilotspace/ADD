# MILESTONE: Context search

goal: Give the AI a fast, keyword-searchable index over the project's milestone/task corpus, surfaced at new-scope drafting and inside the specify/scenarios phase guides, so related prior work is found before drafting -- not after a conflicting design ships.
rationale: new-major (intake 2026-07-01) — no active milestone's goal covers cross-artifact
  keyword search; `add.py deltas`' 14 open SPEC deltas had no matching backlog item either.
  Relationship to the milestone map: kindred spirit to the `artifact-trust` roadmap (ground-trust /
  artifact-graph / traceability-ids all reduce re-derivation-per-file) but a DISTINCT new theme, not
  a slice of any of them — explicitly NOT the "graph-query command" `artifact-graph`'s own
  MILESTONE.md scoped OUT ("rejected — Tin chose MINIMAL backlinks"); Tin confirmed 2026-07-01 this
  is a flat keyword/full-text index over document prose, a different mechanism from graph
  traversal over the backlink edges.
stage: mvp · status: active · created: 2026-07-01T16:07:33+00:00
release: pending

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A new `add.py search <keywords>` command that scans active `.add/milestones/*/MILESTONE.md` +
     `.add/tasks/*/TASK.md` AND their `.add/archive/*/` counterparts for keyword/substring matches
     over title/goal/rationale lines (not full body), ranked by simple match count, printing
     `{slug, kind (milestone|task), status, one matching-line snippet}`. Wiring that command into
     the skill's OWN existing manual instruction — scope.md's "Relate to the milestone map" step
     (`Read every existing goal — .add/milestones/*/MILESTONE.md and .add/archive/*`) and intake.md's
     Diverge step — so it names the search command as the first action, mechanizing a step the
     method already requires but today means a full manual re-read.
Out: A graph-traversal/query engine over the artifact backlink graph — already explicitly rejected
     in `artifact-graph`'s own MILESTONE.md ("Out: ... a graph-query command (rejected — Tin chose
     MINIMAL backlinks)"); this is a flat keyword index over document prose, never edge traversal.
     Semantic/embedding search (vector DB, ML ranking, new runtime dependency) — plain keyword/
     substring match only for v1. An interactive TUI/fuzzy-finder — a plain CLI text/JSON list is
     enough. A new REQUIRED field on every MILESTONE.md/TASK.md — the index is DERIVED from
     existing prose (or a regenerable cache), never hand-maintained, never retrofitted into
     archived docs. Real-time file-watching/incremental indexing — rebuild-on-demand is enough at
     this corpus size (~230 milestones+tasks total, active+archived).

## Shared decisions & glossary deltas   (living — every task must honor these)
- INDEX = a derived, regenerable view over existing MILESTONE.md/TASK.md files — never a new
  required field, never hand-maintained (mirrors `artifact-graph`'s own BACKLINK definition style).
- Keyword/substring match only for v1 — no semantic/embedding search, no new runtime dependency
  (matches the project's lean-dependency / NO-EXEC ethos elsewhere in the engine).
- Distinguished explicitly from a "graph-query command" (the `artifact-graph`-rejected
  alternative): flat full-text/keyword retrieval over document prose, not graph traversal over
  backlink edges — every task in this milestone must preserve that distinction, not blur it.

## Shared / risky contracts (freeze these first)
- the `add.py search` command's I/O shape (query args, output format, ranked fields) -> owning
  task `search-index` (frozen first — `phase-search-wiring` depends on its exact invocation
  grammar to write correct guide prose).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] search-index          depends-on: none           — new `add.py search <query>` command +
      a pure predicate in `add_engine` scanning active+archived MILESTONE.md/TASK.md title/goal/
      rationale lines for keyword matches, ranked, printed as `{slug, kind, status, snippet}`
- [ ] phase-search-wiring   depends-on: search-index    — wires the command into scope.md's
      "Relate to the milestone map" step and intake.md's Diverge step so drafting new scope runs
      a keyword search first, before a manual re-read of every MILESTONE.md

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py search <keyword>` returns ranked matches with a snippet (verify: command `add.py search <keyword>`)                                                             (← search-index)
- [x] scope.md + intake.md name the search command first, before a manual re-read (verify: command `grep -cl "add.py search" .claude/skills/add/scope.md .claude/skills/add/intake.md`) (← phase-search-wiring)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `add.py` gained a new `search <keywords>` command + an `add_engine` predicate scanning active+archived MILESTONE.md/TASK.md title/goal/rationale lines, ranked, printed as `{slug, kind, status, snippet}` — `search-index`.
- skill   : `scope.md`'s "Relate to the milestone map" step and `intake.md`'s Diverge step now name `add.py search` as the first action before a manual re-read — `phase-search-wiring`.
- book    : untouched

### Cross-task evidence   (one row per task)
- search-index : gate=PASS · tests=green (frozen §3 contract, `add.py search` command + predicate) · residue=none
- phase-search-wiring : gate=PASS · tests=green · residue=none (one transient `scope_violation` false-positive self-healed via `phase tests→build→verify` re-cross, confirmed EARNED refute-read, CLEAR/CLEAR/CLEAR 3-lens)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — criterion 1 by `search-index`'s Ship-by-domain row (`add.py search` command shipped); criterion 2 by `phase-search-wiring`'s Ship-by-domain row (scope.md + intake.md both name the command first).
- goal: Give the AI a fast, keyword-searchable index over the project's milestone/task corpus, surfaced at new-scope drafting and inside the specify/scenarios phase guides, so related prior work is found before drafting — met: `add.py search <keyword>` returns ranked `{slug, kind, status, snippet}` matches over the live+archived corpus, and both `scope.md` + `intake.md` now invoke it as the first drafting action, confirmed by both exit-criterion commands run live against the current tree.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] <step — e.g. open a PR from the Close ship-review above; the human reviews + merges>
- [ ] <step — e.g. export the ship-review to a hand-off doc, e.g. `pandoc CLOSE.md -o close.docx`>
- [ ] <step — e.g. tag / publish / deploy  (human-run, per release.md)>
