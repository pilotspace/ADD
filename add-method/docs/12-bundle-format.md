# 12 · The .add/ bundle — ABF-1 format

[← 11 Adoption](./11-adoption.md) · [Contents](./README.md) · Next: [13 The add command reference →](./13-command-reference.md)

---

## The one idea: files are the database

Everything ADD knows about a project lives in one directory, `.add/`, as plain markdown. Each entity is exactly one file with YAML frontmatter. There is no separate state store, no database process, no authoritative index the files must be kept in sync with. If you can edit a text file, you can drive the method by hand — the engine only makes it cheap and discoverable.

`graph.json` is the one exception that proves the rule. It is a **compiled cache** — the whole graph rebuilt from the nodes' frontmatter — so it is gitignored, regenerated on demand, and **never hand-edited**. If it ever disagrees with the files, the files win and the cache is thrown away and rebuilt. Nothing is ever *only* in `graph.json`.

This is the format's central bet: a truth stored twice rots. A hand-authored summary of the nodes drifts from the nodes within a day. So anything derivable from the nodes is *compiled*, never maintained — the graph, the `index.md` table of contents, the `log.md` journal. A compiled artifact cannot go stale, and it has no second writer to conflict with, which is exactly what lets many agents work many nodes in many worktrees at once.

## The directory shape

```
.add/
  index.md                 # bundle config in frontmatter + a COMPILED body (a TOC); never hand-edit the body
  log.md                   # the journal, newest first, compiled from node stamps
  <root Project node>      # type: Project — one per bundle, the direction of the whole
  specs/                   # the five living specs — .add/specs/
    domain.md              # lens: ddd — what the system IS
    system.md              # lens: sdd — how it is built
    experience.md          # lens: udd — how it feels to use
    quality.md             # lens: tdd — how we know it works
    method.md              # lens: add — how we work
  tasks/<slug>.md          # type: Task — one file = one atomic node
  tasks/<slug>.d/runs/     # OPTIONAL sidecar — run receipts, created only when a task accrues them
  milestones/<slug>.md     # type: Milestone — one file per user-request scope
  personas-teacher/        # the installed seed corpus of reasoning lenses (project Personas are typed nodes)
  tooling/                 # the vendored engine — the copy of the CLI that drives this bundle
  graph.json               # DERIVED cache — gitignored, rebuilt on demand
  .gitattributes           # declares the compiled files to git (merge=ours) so a merge never needs a hand-edit
```

`init` scaffolds the eight starter files — `index.md`, `log.md`, the root `Project` node, and the five specs under `.add/specs/` — and vendors `tooling/` and `personas-teacher/`. The smallest conforming bundle is three files: `index.md`, the root `Project` node, and one task.

Tasks live flat under `tasks/` and point at their milestone with a `milestone:` key rather than nesting under it, so a task's identity does not change when it is re-homed. A node's **concept ID** is its bundle-relative path with `.md` removed (`tasks/add-auth-token`); its **slug** is the filename stem (kebab-case, verb-first for tasks, noun-first for milestones), so a slug resolves before any frontmatter is parsed.

## The typed nodes

A closed vocabulary of `type:` values, each in its own place:

| type | one per | required keys |
|---|---|---|
| `Project` | bundle | `type, title, goal` |
| `Milestone` | file | `type, title, goal, status` |
| `Task` | file | `type, title, goal, status` |
| `Spec` | 5 fixed files | `type, title, lens` |
| `Persona` | file | `type, name, vibe` |
| `Prompt` | file | `type, title, fills` |
| `Run` | file | `type, runtime, receipt` |

The set is closed *for authoring*. Reading is more forgiving: an unknown `type:` is recorded as an `info` finding and still compiles into the graph. The engine is a **notary, not a guard** — unknown keys, unknown types, and broken links are recorded, never rejected. Only a link that escapes the bundle root (`edge_out_of_bundle`) is fatal.

### The Task node

A Task is one atomic graph node — the unit the loop runs on. Its frontmatter carries the fields the graph and the gate need at a glance:

```yaml
---
type: Task
title: Reject overlapping bookings per user
goal: a second booking overlapping an existing one returns 409 OVERLAP
status: todo | direction | build | verify | done | dropped
depth: quick | standard | deep          # the ceremony dial — never the authority dial
kind: feature | fix | refactor | test | docs | ui | security | data | infra | integration
sensitivity: mechanical | data | architecture | security     # pins the authority floor
milestone: /milestones/auth-layer.md    # optional — a quick task may be milestone-less
depends_on: [ /tasks/add-auth-token.md ]      # graph edges
needs: [ /tasks/add-auth-token.md#gives ]     # frozen fragments this task consumes
gives: [ "POST /bookings -> 409 OVERLAP on user-overlap" ]   # the interface it produces — FROZEN at freeze
scope: [ src/bookings/** ]              # paths this task may touch; also the freshness set
verified:                               # append-only stamps: freeze, gate, refreeze
  - { by: "human:tindang", at: 2026-07-29T09:00:00Z, act: freeze, authority: human }
---
```

Its body is six sections, each with one job:

- `## CARD` — the ≤10-line summary: goal restated, the contract shape, scope, the current beat and next action. This is the **only** section other nodes ever read.
- `## RULES` — Must (`M<n>`), Reject (`R:<code>`), After. What the request *said*, and only that.
- `## ASSUMPTIONS` — `A<n> [<dim>] covers: <S ids>`: what the request did **not** say, the reading
  you took, and the cost if it is wrong. Every `gives:` surface is swept on every dimension
  (`who · which · when · absent · order`) or the dimension is retired with `n/a · <why>`; `freeze`
  refuses and names the unswept pairs. Exempt at `depth: quick`. Not bindable by `covers:`, and not
  sealed by the direction digest (FORMAT.md §5).
- `## PLAN` — the contract detail that becomes the frozen `gives:`, the build strategy, and the `scope:`.
- `## EDGES` — optional enumerated boundary cases (`E<n>`) a check must cover.
- `## CHECKS` — one check per Must / Reject / Edge, red-first, each carrying a `covers:` referent.
- `## EVIDENCE` — the receipt link, the gate outcome, the scope check.
- `## LESSONS` — deltas emitted onward via `add learn <lens>`.

**Atomicity:** rebuilding a task may change anything in its body, but its frontmatter `gives:` is its external interface, frozen at the freeze stamp. Changing it is a *change request* that reopens direction and flags every dependent whose `needs:` cite it as **stale**, to re-verify before its next gate.

### The Milestone node

A Milestone is one user-request scope — the thing a wave of tasks delivers. Its frontmatter names its members (`tasks:`), its `status`, and its `ratified:`/`amended:` stamps. Its body is five sections:

- `## CARD` — goal restated, wave shape, current state.
- `## SCOPE` — In / Out, the anti-scope-creep list.
- `## GROUND` — gathered once: shared touches, anchors, honored decisions, shared risks. Tasks project from this and never re-ground the repo.
- `## EXIT` — observable criteria, each mapped to the task that delivers it. Append-only: a criterion that no longer applies is struck through with its date, never deleted.
- `## CLOSE` — at done: the per-task evidence rollup and the goal-met verdict.

(At `depth: deep` a `## STRATEGY` section is added for approach, freeze-first ordering, and waves.) The milestone owns membership, ground, and exit; each task owns its own edges — one source per fact.

### The Persona node

A Persona is a reasoning lens for a decision point, not a task — it has no lifecycle, never freezes, and never gates. Its frontmatter carries `type, name, vibe` and a `use-when:` line (the one field a tool reads to place the lens). Its body distills the stance into machine-readable parts: `## Identity`, `## Critical Rules`, `## Default Requirement`, `## Success Metrics`. The installed seed corpus lives in `personas-teacher/`; project-authored personas are typed nodes in the bundle. A persona advises; it can never lower a gate (see chapter 8).

## The covers grammar — binding a rule to its check

A `## CHECKS` line names, with `covers:`, the exact rule it exists to prove. The referent depends on depth, and the grammar is closed. Quoted verbatim from FORMAT.md §6.1:

```covers-grammar
quick           = \A(goal|G\d+)\Z
standard | deep = \A(M\d+|R:[A-Z0-9_]+|E\d+)\Z
```

So at `standard`/`deep` depth a check covers `M<n>` (a Must), `R:<CODE>` (a Reject), or `E<n>` (an enumerated edge). At `quick` depth there is no RULES section, so a check covers `goal` or `G<n>` (the nth entry of `gives:`).

The binding is checked at two distinct moments:

| moment | the check | failure |
|---|---|---|
| **freeze** | every `M<n>` and `R:<CODE>` in RULES appears in at least one check's `covers:` | refuse to freeze — a rule in no check means the rules are not understood |
| **gate** | every check listed in CHECKS appears in the receipt with `outcome: pass` | refuse the gate — `covers:` names a check that did not demonstrably pass |

`covers:` is a *binding*, not a label: the gate refuses a PASS whose rules are not all covered by a passing check, and refuses a receipt that is stale (its observed code no longer matches) or unbound.

## The engine is a NO-EXEC notary

One law governs the whole format: **the engine records; it never executes.** It runs only the command its caller passes on the command line (via `add run … -- <cmd>`) and captures the result. A `computation:` string stored in a node is *never* executed — a notary that ran arbitrary strings from files would be an execution surface, and a gate could pass without anyone having run anything. The engine does not run the method, does not write your RULES or CHECKS for you, and does not spawn an agent. It stamps what happened.

## A worked node

```yaml
---
type: Task
title: Reject overlapping bookings per user
goal: a second booking overlapping an existing one returns 409 OVERLAP
status: verify
depth: standard
kind: feature
sensitivity: data
scope: [ src/bookings/** ]
gives: [ "POST /bookings -> 409 OVERLAP on user-overlap" ]
verified:
  - { by: "human:tindang", at: 2026-07-29T09:00:00Z, act: freeze, authority: human }
---
## CARD
goal: a second overlapping booking for the same user returns 409 OVERLAP.
contract: POST /bookings -> 409 { error: OVERLAP }   scope: src/bookings/**
beat: verify · next: add gate reject-overlap PASS --by "tindang"

## RULES
<must>
- M1 a booking overlapping one the user already holds is refused
</must>
<reject>
- R:OVERLAP the overlapping request is rejected -> "OVERLAP"
</reject>

## PLAN
contract: POST /bookings -> 201 on free slot · 409 { error: OVERLAP } on overlap
scope: src/bookings/**

## CHECKS
- test_overlap_rejects   · covers: R:OVERLAP · a second overlapping booking gets 409
- test_adjacent_allows   · covers: M1       · a back-to-back non-overlapping slot gets 201
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/2.md
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- overlap is half-open [start, end) — folded to specs/domain -> add learn ddd
```

The receipt at `runs/2.md` is a `type: Run` node recording the command's exit code, the passing check IDs, and the git blob hash of every in-`scope:` file at run time. The gate reads that receipt, re-hashes the scope, confirms `R:OVERLAP` and `M1` each map to a passing check, and only then records a `PASS`.

## Conformance

A bundle **conforms** iff it has zero `error` findings. There are only two severities. The `error` set is small and structural — `missing_frontmatter`, `type_empty`, `edge_out_of_bundle`. Everything else is `info`: unknown keys and types, unresolved edges (a wave may be sketched before its tasks exist), a gate that passed on coarse evidence. Within a major `abf_version`, changes are additive only — new keys, new sections, new finding codes — so an old engine reading a newer bundle sees unknown keys and records `info` rather than breaking.
