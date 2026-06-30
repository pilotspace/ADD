# MILESTONE: Artifact-graph

goal: Every ADD artifact carries minimal backlink metadata (task↔milestone↔release↔deps↔delta, bidirectional) so the cross-artifact graph is traversable without re-deriving it.
rationale: new-major roadmap "artifact-trust" milestone 2 of 5 (Tin-confirmed all 5). The PR40 audit showed TASK.md files are strong execution contracts but weak reference docs — knowledge is siloed per file ("one file = one task"), so a reader re-derives the task↔milestone relationship instead of reading it. MINIMAL backlinks (Tin chose this over a rich node+edge graph) make the graph traversable from the artifacts themselves.
stage: mvp · status: active · created: 2026-06-30T11:47:47+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Minimal, ENGINE-POPULATED backlinks in the artifact headers — the link is written/maintained by add.py, not hand-typed, so it can't silently drift:
     - TASK.md header gains `milestone: <slug>` (the parent), auto-filled by `add.py new-task`; the reverse link already exists (MILESTONE.md lists its tasks) → task↔milestone is bidirectional.
     - MILESTONE.md header gains `release: <pending|version>`, stamped by `add.py release` at the cut; the reverse already exists (RELEASES.md ledger names its milestones) → milestone↔release bidirectional.
     - `add.py check` surfaces a backlink that disagrees with state.json (audit/report, not a hard block).
Out: delta↔task links + rule IDs (→ M4 traceability-ids — that milestone owns delta lifecycle + IDs) · drift/ground SHAs (→ M3 drift-guard) · a rich node+edge graph or a graph-query command (rejected — Tin chose MINIMAL backlinks) · retro-filling backlinks into archived tasks (grandfathered, never retro-red).

## Shared decisions & glossary deltas   (living — every task must honor these)
- BACKLINK = a header field that NAMES a related artifact, written/maintained by the engine (not hand-typed). The engine already owns the parent relationship in state.json; the backlink mirrors it into the file so the file is self-describing.
- Engine touch is in-scope this milestone (unlike ground-trust) → every add.py copy re-pins engine_pin.ENGINE_MD5 in lockstep; method/trust-sensitive, so verify escalates to a human gate even under autonomy: auto.
- Pre-existing tasks without the field are grandfathered (never retro-red); the field is required only for tasks created after the feature ships.

## Shared / risky contracts (freeze these first)
- the TASK.md header `milestone:` field shape -> owning task `task-milestone-backlink` (frozen first; `milestone-release-backlink` extends the same header-backlink pattern).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] task-milestone-backlink     depends-on: none                    — TASK.md header gains `milestone: <slug>`, auto-populated by `add.py new-task`; `add.py check` flags a mismatch vs state.json; template ×3 + engine ×3 re-pinned + test
- [ ] milestone-release-backlink  depends-on: task-milestone-backlink — MILESTONE.md header gains `release: <pending|version>`, stamped by `add.py release`; template + engine re-pinned + test

## Exit criteria (observable; map each to the task that delivers it)
- [ ] A newly-created task's TASK.md header names its parent `milestone:`, written by the engine (not hand-typed), and `add.py check` flags it if it disagrees with state.json   (← task-milestone-backlink)
- [ ] A released milestone's MILESTONE.md header names its `release:` version, stamped at the cut   (← milestone-release-backlink)
- [ ] every add.py copy stays byte-identical and matches the re-pinned engine_pin.ENGINE_MD5; templates parity holds; full suite green   (← both)

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
