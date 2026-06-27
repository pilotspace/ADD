# MILESTONE: Decision/ADR record harvested at OBSERVE

goal: every task ends with a durable engine-harvested Decisions (ADR) block in §7 — the key decisions by both human and AI (who · what · why · alternatives), gathered from the actor-stamps already in the file, with an audit lint that it is present at done
rationale: sub-milestone from todo #22 — decisions are captured today but scattered (§1 framing=AI · §3 freeze=human · §6 gate=human) and the AI's actual build strategy is not recorded at all; ADD has no consolidated, actor-tagged decision record. Harvest (not author) the stamps already in the file into a durable §7 ADR block. Shape confirmed by Tin: engine-harvested §7 block (not a separate file, not a `decision` command).
stage: mvp · status: active · created: 2026-06-27T17:43:42+00:00

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a durable, engine-HARVESTED "Decisions (ADR)" block in §7 of every task — each line tagged [human]/[AI], sourced from the actor-stamps already present: §1 Framings weighed (AI), §3 FROZEN-by (human), §5 Strategy actually used (AI · NEW field), §6 GATE RECORD (human). A §5 write-back so the AI's REAL build strategy is recorded. An audit lint (`adr_record_missing`) requiring the block at done. Observe guide + book + glossary + 3-tree skill parity.
Out: a separate DECISIONS.md / ADR file · an `add.py decision` authoring command · capturing EVERY micro-decision (only the four stamped decision points) · back-filling ADR blocks onto already-archived tasks (grandfathered).

## Shared decisions & glossary deltas   (living — every task must honor these)
- HARVEST, never AUTHOR — the ADR block is rendered from stamps already in the file; the engine writes no new decision content of its own (NO-EXEC honored).
- every harvested line is ACTOR-TAGGED [human] or [AI] — the whole point is to separate who decided what.
- the four decision sources are fixed: §1 framing (AI) · §3 freeze (human) · §5 strategy-actually-used (AI) · §6 gate (human).
- engine-written, like the existing GATE RECORD write-back (gate-record-writeback) — same grandfather rule for pre-existing tasks.

## Shared / risky contracts (freeze these first)
- the §5 "Strategy actually used:" field shape -> owning task `strategy-actual-writeback` (the harvest depends on it)
- the §7 "Decisions (ADR)" block shape + the four source→actor mappings -> owning task `adr-harvest`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] strategy-actual-writeback   depends-on: none                    — §5 gains a "Strategy actually used:" field; verify/observe records the AI's real build strategy (closes the report→§5 seeded delta)
- [ ] adr-harvest                 depends-on: strategy-actual-writeback — engine renders the §7 "Decisions (ADR)" block from §1/§3/§5/§6 stamps, each tagged human/AI (write-back at done)
- [ ] adr-audit-and-docs          depends-on: adr-harvest              — audit lint `adr_record_missing` at done + observe guide + book chapter + glossary + 3-tree skill parity

## Exit criteria (observable; map each to the task that delivers it)
- [ ] a done task carries an engine-harvested §7 "Decisions (ADR)" block, each line tagged [human]/[AI], sourced from §1 framing / §3 freeze / §5 strategy-used / §6 gate        (← adr-harvest)
- [ ] the AI's actual build strategy is recorded in §5 ("Strategy actually used:"), closing the report→§5 loop        (← strategy-actual-writeback)
- [ ] `add.py audit` fires `adr_record_missing` when a done (non-grandfathered) task lacks the record        (← adr-audit-and-docs)
- [ ] the observe guide + book + glossary document the ADR record; the 3-tree skill parity holds        (← adr-audit-and-docs)
- [ ] the engine change is pinned (ENGINE_MD5 / ENGINE_PKG_MD5 bumped) and the full suite is green        (← adr-harvest + adr-audit-and-docs)

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
