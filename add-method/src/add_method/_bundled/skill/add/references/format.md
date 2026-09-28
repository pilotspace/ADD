# The `.add/` bundle — ABF-1, maintained by hand

Plain markdown with YAML frontmatter. The files are the state; git is the history and the seal.
You write every file — keep each one short and true. Nothing here is compiled or generated.

```
.add/
  PROJECT.md             goal · invariants · test_cmd — read first, every session
  specs/<lens>.md        domain · system · experience · quality · method
  milestones/<slug>.md
  tasks/<slug>.md
  personas/<name>.md     optional expert lenses
```

Slugs are kebab-case and stable: commits refer to them (`freeze(<slug>)`, `verify(<slug>)`).

## PROJECT.md

```markdown
---
type: Project
title: <name>
goal: <one line — what this project is for>
invariants:                  # bind every change, Quick included; [] when none yet
  - <a property no change may break>
test_cmd: <the full suite command>
stage: prototype | mvp | production
---
## CARD
goal: <the goal, in plain words>
state: <where things stand — one line, updated at the end of each session>
next: <the next piece of work>
```

## Task

```markdown
---
type: Task
title: <title>
status: direction | build | done | dropped
milestone: <slug>            # omit when standalone
kind: feature | fix | refactor | explore | docs | test | data | infra | ui | security | release | integration
sensitivity: none | security | data | architecture
scope: [src/auth/session.py, tests/auth/test_session_expiry.py]
gives:
  - S1 POST /sessions -> 201 {id, expires_at}
needs: [tasks/session-store.md#gives]   # surfaces from other tasks this one builds on
---
## CARD
goal: expired sessions are refused
why: support saw week-old sessions still acting after password resets

## RULES
- M1 a session within its lifetime is accepted (from: request)
- R:EXPIRED a session past `expires_at` is refused with 401 "session expired" (from: docs/auth.md)

## ASSUMPTIONS
- A1 [when] the boundary second is not specified → `expires_at` itself is already expired → one second of access
- A2 [who] n/a · sessions are per-user; no cross-user surface

## PLAN
strategy: compare against a clock port, not the wall clock
check: pytest tests/auth/test_session_expiry.py
regression: pytest

## CHECKS
- C1 covers: M1 · acceptance · tests/auth/test_session_expiry.py::test_live_session_accepted
- C2 covers: R:EXPIRED, A1 · acceptance · tests/auth/test_session_expiry.py::test_expired_at_boundary_refused

## LOG
- refreeze: C2 aimed at the wrong clock; now uses the injected clock

## EVIDENCE
freeze: 3f2a91c · head: 8be0d44
seal: git diff 3f2a91c 8be0d44 -- .add/tasks/session-expiry.md tests/auth/test_session_expiry.py → empty
check: `pytest tests/auth/test_session_expiry.py` → exit 0 · 2 passed
regression: `pytest` → exit 0 · 318 passed
residue: security — refusal leaks no session id; concurrency — n/a; architecture — clock port only
refute: expires_at = now + 1ms → accepted; now - 1ms → refused · held
verdict: PASS
```

- `status:` moves `direction → build` in the freeze commit and `build → done` in the verify commit;
  a HARD-STOP leaves it at `build`. `dropped` carries `dropped: <reason>` in the CARD.
- `## EDGES` is optional: `E<n> Given <state> · When <action> · Then <result>` — readable examples.
  A written edge needs a check that covers it.
- `## LOG` changes only in a `refreeze(<slug>)` commit. `## EVIDENCE` is written once, at verify.
- An explore task (`kind: explore`) carries `## QUESTIONS`, `## BUDGET` and `## FINDINGS` instead of
  RULES/CHECKS — see `explore.md`.

## Milestone

```markdown
---
type: Milestone
title: <title>
status: active | done
---
## CARD
goal: <the outcome that makes this worth doing>
why: <one line>

## SCOPE
In:  <what this milestone covers>
Out: <what it deliberately does not>

## EXIT
- [ ] <a criterion that proves the goal> — evidence: <task slug | sha>

## TASKS
- session-store — sessions persist across restarts
- session-expiry — expired sessions are refused (after: session-store)
```

Tick an EXIT box only with its evidence on the line. `status: done` when every box is ticked.

## Spec — one per lens

```markdown
---
type: Spec
lens: domain | system | experience | quality | method
---
## Now
<what is true today, a few lines>

## Decisions that bind
- D1 <a decision future tasks must follow> (evidence: <sha | task>)

## Deltas
- 2026-09-28 open · <lesson> (evidence: <sha | task>)
```

Lenses: **domain** — the business language and rules · **system** — architecture and interfaces ·
**experience** — users and their journeys · **quality** — tests, reliability, performance ·
**method** — how this team works. A delta is `open`, then `folded` into a decision or `rejected`.
An escaped defect's delta names why the checks missed it and the check that now prevents it.

## Persona

```markdown
---
type: Persona
title: <the lens, in a phrase>
flow: design, verify, advisor      # the beats it serves
task-kinds: feature, security
use-when: <when to load it>
not-when: <when not to>
---
<what this expert checks, prefers and refuses — distilled, not copied>
```

## Non-code work

The loop is the same. A check is anything that can fail and be run or read: a lint, link or
spelling script, a schema validator, a rendered-output diff, or a pass/fail rubric scored against
the artifact. Name the mode on the CHECKS line (`script` · `validator` · `rubric`) so a reviewer
knows how it was judged.

## Coming from ADD 3.x

A 3.x bundle reads as-is. Its extra frontmatter (`verified:`, `generated:`, digests), `graph.json`,
`index.md`, `log.md`, `runs/` and `tasks/<slug>.d/` are history: leave them, do not maintain them.
New work uses the shapes above.
