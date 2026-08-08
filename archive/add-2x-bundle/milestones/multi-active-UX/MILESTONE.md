# MILESTONE: Multi Active Ux

goal: a team running several active milestones at once sees, in one place, what is theirs to work on and what is schedulable across all streams — ADD surfaces a per-actor 'my work' view, a per-stream owner, and a cross-active waves/ready frontier, instead of a single-milestone-at-a-time lens
rationale: sub-milestone of the **team-collaboration** major (confirmed intake 2026-06-22). Milestone 5 of 5 — the LAST sibling, the major's payoff. The prior four built the machinery: M1 reshaped state to multi-active (`active_milestones` SET + `active_tasks` per-ms map), M2 stamped a git-native actor identity (`_whoami`), M3 added owner/assignee per task+milestone, M4 made the shared state merge-safe. This milestone is the human-facing UX that makes all of it usable for a TEAM running several active milestones at once: a per-actor "my work" lens (what is mine across every stream), a per-stream owner in the existing `streams:` block (the carried delta from M1's parallel-status-view), and a cross-active `waves`/`ready` frontier (today the DAG scheduler scopes to the single active milestone — a team needs the schedulable picture across all of them). Relationship to the map: DEPENDS-ON M1 (the multi-active schema it reads) + M2 (`_whoami`/actor) + M3 (owner/assignee); ORTHOGONAL to M4. Scope confirmed with the human (2026-06-22): ALL THREE surfaces. risk: presentation-only — these are READ surfaces over existing state (no schema change, no new write seam, no decision semantics), so they DO NOT edit the byte-pinned engine's logic beyond adding read/render code; engine-edit discipline (3-copy + ENGINE_MD5) still applies because the code lives in add.py.
stage: mvp · status: active · created: 2026-06-22

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  A per-actor "MY WORK" lens — a read surface (command and/or `--mine`-style filter) that, across
     ALL active milestones, lists the tasks owned-by OR assigned-to the resolved actor (`_whoami`,
     honoring an `--actor "Name <email>"` override), so a teammate sees "what is mine to pick up"
     without scanning every stream. A PER-STREAM OWNER shown in the existing `streams:` status block
     + the report (each active stream names its owner/lead — the carried delta from M1). A CROSS-ACTIVE
     `waves`/`ready` frontier — the DAG scheduler reports the schedulable/ready tasks across EVERY
     active milestone, not only the single active one. All READ-ONLY + additive (legacy / N<=1 / no-owner
     output stays byte-identical). All 3 add.py copies in lockstep + ENGINE_MD5 re-pinned per task.
Out: WRITE/assignment UX (bulk assign, reassign flows) — M3 already shipped assign/unassign; this is
     SURFACE only. A web/TUI dashboard or any rendering beyond the CLI text/JSON surfaces — OUT (no
     server, tool-agnostic). CHANGING the wave DAG semantics / scheduling algorithm — OUT (only widen
     its SCOPE from one active milestone to all). NEW state keys, schema changes, or any decision that
     READS owner/assignee/actor (these stay descriptive, never enforced). Notifications / real-time.

## Shared decisions & glossary deltas   (living — every task must honor these)
- my work (NEW surface term) — the set of not-done tasks across all `active_milestones` whose `owner`
  OR `assignee` resolves to the current actor (`_whoami` or `--actor` override), matched by the actor's
  name/email. A read lens, never a filter that mutates. Add to GLOSSARY.
- actor match — "mine" matches on the resolved actor's identity (name+email), reusing `_whoami` +
  `_fmt_actor`; an `--actor "Name <email>"` override (parsed via `_parse_actor_arg`) lets one inspect
  another teammate's queue. Unowned tasks belong to no one's "my work".
- additive-cue convention (inherited) — every new surface is silent / byte-identical when it has nothing
  to add: no active milestones, no owners, N<=1 streams, or no tasks-mine → the prior output is unchanged.
- cross-active means SCOPE not SEMANTICS — `waves`/`ready` keep their DAG/ready rules; only the set of
  milestones they range over widens from {the one active} to {all active_milestones}.
- engine-edit discipline (inherited) — every task edits all THREE add.py copies byte-identically AND
  re-pins ENGINE_MD5 in the SAME commit; a new subcommand adds to `test_min_pillar` LIFECYCLE census.

## Shared / risky contracts (freeze these first)
- the "MY WORK" actor-match + surface contract — how a task counts as "mine" (owner OR assignee, by
  resolved name+email), the `--actor` override grammar, and the command/flag shape + its text & `--json`
  output (the other two surfaces reuse existing render seams; this one is the new surface) -> owning task `my-work-lens`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] my-work-lens       depends-on: none            — a read-only "my work" surface: across ALL active milestones, list the not-done tasks owned-by/assigned-to the resolved actor (`_whoami`, `--actor` override); text + `--json`. The new surface — freeze its actor-match + shape first.
- [x] per-stream-owner   depends-on: none            — show each active stream's owner/lead in the existing `streams:` status block + report (the carried M1 delta); additive, byte-identical when a stream has no owner. Reuses `_fmt_ownership`/`_fmt_actor`.
- [x] cross-active-waves depends-on: my-work-lens    — widen `waves`/`ready` to report the schedulable/ready frontier across EVERY active milestone, not just the single active one; DAG semantics unchanged, only the milestone scope widens. Additive/byte-identical at N<=1 active.

## Exit criteria (observable; map each to the task that delivers it)
- [x] a teammate can see, in one command across all active milestones, the not-done tasks that are theirs (owner or assignee) — and inspect another actor's queue via `--actor` — in text and JSON   (← my-work-lens) (verify: `python3 -m unittest test_my_work_lens` — 8 green incl. owned+assigned, exclusions, --actor, --json, email-first/name-fallback)
- [x] the `streams:` status block + report name each active stream's owner/lead, and stay byte-identical when a stream has no owner   (← per-stream-owner) (verify: `python3 -m unittest test_per_stream_owner` — 6 green incl. owned stream, no-owner/blank-name byte-identity, json parity, N<=1)
- [x] `waves`/`ready` report the ready frontier across every active milestone (not just the single active one), with N<=1-active output unchanged   (← cross-active-waves) (verify: `python3 -m unittest test_cross_active_waves` — 7 green incl. spans-active, single-byte-identical, --milestone, streams-json, scalar-gate rejection, ready annotation)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : add.py gained THREE read-only surfaces over the multi-active state — `mine` (`_actor_matches` + `_my_work`, a per-actor "my work" lens across all `active_milestones`, text + `--json`, `--actor` override), per-stream owner in the human `streams:` status block (reuses `_fmt_actor`, name-guarded so a blank-name/no-owner stream stays byte-identical) + `owner`/`assignee` on each status-`--json` milestone entry, and cross-active `waves`/`ready` (extracted `_wave_block_lines`; `waves` with no `--milestone` spans every active milestone — `active streams:` header + per-block fences — `ready` annotates each task `[milestone]`). All 3 add.py copies in lockstep, ENGINE_MD5 re-pinned per task (b102fb61→1c7a8f58→…→69c46d6c). `mine` added to `test_min_pillar` LIFECYCLE census. No state-schema change, no new write seam, no decision reads owner/assignee.
- skill   : untouched (presentation-only surfaces; the streams/loop/run guides already describe the multi-active model).
- book    : untouched.

### Cross-task evidence   (one row per task)
- my-work-lens       : gate=PASS · tests=8 green (test_my_work_lens) · residue=none
- per-stream-owner   : gate=PASS · tests=6 green (test_per_stream_owner) · residue=none
- cross-active-waves : gate=PASS · tests=7 green (test_cross_active_waves) · residue=none

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
  - EC1 (per-actor "my work" across all active milestones, `--actor`, text+JSON) ← my-work-lens row (8 green) + tooling `mine` surface
  - EC2 (`streams:` block names each active stream's owner, byte-identical with no owner) ← per-stream-owner row (6 green) + tooling streams-owner fragment
  - EC3 (`waves`/`ready` span every active milestone, N<=1 unchanged) ← cross-active-waves row (7 green) + tooling `_wave_block_lines`/`ready` annotation
- goal: a team running several active milestones at once sees, in one place, what is theirs and what is schedulable across all streams — proved live on a 2-active-milestone scratch project: `waves` emitted `active streams: 2` with both stream blocks, `ready` annotated `[m1]`/`[m2]`, and `mine` listed only the resolved actor's open tasks across both streams.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] this milestone is the LAST of the **team-collaboration** major (5/5) — it ships on the shared PR #47 (`feat/fold-suggestion-seams`) alongside its four siblings; the human reviews + merges that PR.
- [ ] the whole team-collaboration major is then releasable — bundle all 5 closed milestones into one cut via release.md (`add.py status` will show `→ releasable: N closed since last release`); draft notes from the consolidated foundation deltas, meet the readiness floor (security HARD-STOP un-forceable), human confirms → `add.py release <version>`.
- [ ] tag / publish (npm + PyPI) + cut the GH release — human-run, per release.md.
