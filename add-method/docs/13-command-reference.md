# 13 · The add command reference

[← 12 The .add/ bundle — ABF-1 format](./12-bundle-format.md) · [Contents](./README.md) · Next: [14 The foundation and the five living specs →](./14-foundation.md)

---

Every command is `add <verb>`. The engine records; it never runs the method or spawns an agent — it stamps what happened and points at the next step. A global `--root` (default `.add`) selects the bundle. Every verb's output ends with a `next:` line naming the exact next command, so the loop is discoverable from the tool itself.

This is the complete, shipped verb set — nothing here is aspirational, and there is nothing beyond it.

## Orient

Where you start, and where you return every session — never re-read the whole repo.

| verb | what it does | example |
|---|---|---|
| `status` | resume: the standing picture — active nodes, the current beat, what is next. `--all` for the full report, `--check` for conformance findings | `add status --check` |
| `init` | create a `.add/` bundle: the eight starter files plus the vendored engine and seed corpus. `--profile code \| doc` | `add init my-service --profile code` |
| `upgrade` | move a 2.x project to 3.0: the whole 2.x bundle is renamed into `.add-2x-archive/` (byte-identical, nothing deleted), a fresh 3.0 bundle is initialised beside it, and the archive gains a `MIGRATION.md` walking the re-authoring. 2.x state is deliberately not translated | `add upgrade` |

## Author

Create a node and take it through Direction to the one approval.

| verb | what it does | example |
|---|---|---|
| `new` | scaffold a typed node — `Task \| Milestone \| Persona \| …`. Flags: `--title --depth --sensitivity --kind --milestone --scope` | `add new Task reject-overlap --depth standard --sensitivity data --scope src/bookings/**` |
| `freeze` | the one human approval — closes Direction, opens Build. `--by`, `--authority` | `add freeze reject-overlap --by "tindang" --authority human` |
| `brief` | compile the sealed direction into the working XML prompt — and, on a frozen task, record an `act: brief` stamp: the entry into Build. The gate refuses a `PASS` whose receipts predate that entry. `--phase`, `--for-subagent`, `--by` | `add brief reject-overlap` |
| `replan` | record a steering amendment on a frozen task — one additive `act: replan` stamp carrying the note; the seal, the checks and the gate are untouched. A frozen `gives:`/check change stays a change-request (refreeze), never a replan. `--note`, `--by` | `add replan reject-overlap --note "pivoting to sorted-merge"` |

## The loop

Build to green, verify on evidence, record one outcome. `gate PASS` auto-closes the task.

| verb | what it does | example |
|---|---|---|
| `run` | execute the checks and write a fresh, scope-bound Run receipt. `--junitxml` parses test IDs; `--timeout <s>` raises the 900 s ceiling for a build-heavy command; the command follows `--` — keep it the narrowest run that reports every bound check | `add run reject-overlap --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- pytest tests/test_overlap.py` |
| `gate` | record the verdict: `PASS \| RISK-ACCEPTED \| HARD-STOP`. `--by`, `--authority`, `--reason` | `add gate reject-overlap PASS --by "tindang"` |
| `done` | close a gated task (the normal path closes automatically at `gate PASS`) | `add done reject-overlap` |
| `reopen` | return a done task to a beat with a reset gate. `--to direction\|build\|verify` and `--reason` both required | `add reopen reject-overlap --to build --reason "missed a race"` |
| `learn` | file a lesson into a living spec — `ddd\|sdd\|udd\|tdd\|add`. `--evidence` is the receipt or decision that caused it | `add learn ddd "overlap is half-open [start,end)" --evidence runs/2.md` |

A `RISK-ACCEPTED` needs its reason: `add gate <slug> RISK-ACCEPTED --by "tindang" --reason "owner · ticket · expiry"`. Security is never batched — a security finding is always `HARD-STOP`.

## Milestone

Group tasks into one user-request scope; close it on met exit criteria.

| verb | what it does | example |
|---|---|---|
| `milestone-done` | close a milestone — refuses while any `## EXIT` box is unchecked | `add milestone-done auth-layer` |
| `check` | mark (or `--off` unmark) a checklist box by 1-based index, and record who did it. `--section` narrows to one `## SECTION`; `--all` takes every box | `add check auth-layer 2 --by "Ada"` |
| `milestone-archive` | retire a done milestone — refuses one that is not done | `add milestone-archive auth-layer` |
| `deltas` | list open deltas across the specs — the carried inventory. `--status open\|folded\|rejected` | `add deltas --status open` |
| `fold` | retag a named open delta folded (human consolidation) into a spec `domain\|system\|experience\|quality\|method` | `add fold domain "half-open"` |

## Parallel

Fan a milestone's DAG out across git worktrees, then fold the streams back.

| verb | what it does | example |
|---|---|---|
| `wave` | plan a parallel wave from the task DAG (independent levels). `--streams` records one wave as active | `add wave auth-layer --streams add-auth-token,reject-overlap` |
| `join` | fold worktree stream bundles back — PASS-only, union the deltas, regenerate the graph | `add join ../wt-a/.add ../wt-b/.add` |

## Personas

Apply a reasoning lens to a beat. A persona advises; it never lowers a gate.

| verb | what it does | example |
|---|---|---|
| `advise` | record a persona lens on a sequential beat (NO-EXEC; feeds the coverage floor). `--persona` required | `add advise reject-overlap --persona concurrency-hawk` |

Personas also drive the parallel verbs above — `wave`/`join` assign personas to the streams they fan out.

## Query

Read-only lookups over the bundle.

| verb | what it does | example |
|---|---|---|
| `doctor` | conformance findings; `--sync` recomputes compiled artifacts and re-vendors a stale engine | `add doctor --sync` |
| `locate` | reverse lookup — which node's `scope:` owns a path | `add locate src/bookings/service.py` |
| `todo` | the open worklist — active tasks grouped by beat. `--milestone` restricts to one | `add todo --milestone auth-layer` |
