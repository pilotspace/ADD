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
- [x] strategy-actual-writeback   depends-on: none                    — §5 gains a "Strategy actually used:" field; verify/observe records the AI's real build strategy (closes the report→§5 seeded delta)
- [x] adr-harvest                 depends-on: strategy-actual-writeback — engine renders the §7 "Decisions (ADR)" block from §1/§3/§5/§6 stamps, each tagged human/AI (write-back at done)
- [x] adr-audit-and-docs          depends-on: adr-harvest              — audit lint `adr_record_missing` at done + observe guide + book chapter + glossary + 3-tree skill parity

## Exit criteria (observable; map each to the task that delivers it)
- [x] a done task carries an engine-harvested §7 "Decisions (ADR)" block, each line tagged [human]/[AI], sourced from §1 framing / §3 freeze / §5 strategy-used / §6 gate        (← adr-harvest)
- [x] the AI's actual build strategy is recorded in §5 ("Strategy actually used:"), closing the report→§5 loop        (← strategy-actual-writeback)
- [x] `add.py audit` fires `adr_record_missing` when a done (non-grandfathered) task lacks the record        (← adr-audit-and-docs)
- [x] the observe guide + book + glossary document the ADR record; the 3-tree skill parity holds        (← adr-audit-and-docs)
- [x] the engine change is pinned (ENGINE_MD5 / ENGINE_PKG_MD5 bumped) and the full suite is green        (← adr-harvest + adr-audit-and-docs)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py — `_stamp_adr_record` (harvests the §7 "Decisions (ADR)" block at the gate, beside `_stamp_gate_record`) + `adr_record_missing` audit lint in `_audit_findings` (bare-line probe, block-absent grandfather, pure read → exit 1); §5 "Strategy actually used:" field in TASK.md.tmpl + TASK.fast.md.tmpl. ENGINE_MD5 → 03b422b2; ENGINE_PKG_MD5 e87f5652 UNCHANGED (add_engine/* untouched).
- skill   : phases/7-observe.md gains the "Decisions (ADR)" note (its own prose leaned ~180 B to hold the frozen lean budget rather than weaken it); fast-lane template carries the §5 field.
- book    : docs/09-the-loop.md "The decision record (ADR)" section + docs/appendix-c-glossary.md "Decisions (ADR)" term (canonical · dogfood · bundle · repo-root mirror all byte-identical).

### Cross-task evidence   (one row per task)
- strategy-actual-writeback : gate=PASS · the §5 "Strategy actually used:" field (the harvest's [AI] build input) · residue=none
- adr-harvest               : gate=PASS · §7 block + `_stamp_adr_record` · re-froze §3 @ v2 after dogfooding caught a §7-scoping bug (it had corrupted its own frozen §3) · residue=none
- adr-audit-and-docs        : gate=PASS · full suite 2132/0 (+6 test_adr_audit.py) · adversarial refute-read = EARNED · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 harvested §7 block → adr-harvest (`_stamp_adr_record`); proven on this very task's §7 (4 actor-tagged lines)
  - EC2 §5 strategy recorded → strategy-actual-writeback (tooling row)
  - EC3 `adr_record_missing` fires → adr-audit-and-docs (audit lint; `audit --json` count 0 on real tasks = correct grandfather)
  - EC4 observe guide + book + glossary + 3-tree parity → adr-audit-and-docs (book row; test_book_parity + test_v8_docs + test_adr_audit green)
  - EC5 pinned + suite green → ENGINE_MD5 03b422b2, ENGINE_PKG_MD5 unchanged, suite 2132/0
- goal: every task now ends with a durable engine-harvested, actor-tagged §7 Decisions (ADR) block, audited at done — proven by this milestone's own final task carrying [AI] specify / [human] freeze @ v1 / [AI] build / [AI] verify in its §7.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR from a feature branch (all 3 tasks in one commit, per Tin's "commit everything together"); the human reviews + merges
- [ ] the retrospective consolidation (fold open deltas) — separate step after merge, on demand
- [ ] bundle into the next release cut (release.md) — tag / publish is human-run
