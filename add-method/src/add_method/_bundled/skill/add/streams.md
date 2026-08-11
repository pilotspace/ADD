# Streams — delegate a beat to a persona subagent (the advisor pattern)

ADD's engine is the hands' *notary*; **you** are the hands. When a beat's work wants an expert the
main thread isn't the best-placed to do — a security refute-read, a backend contract, a UX pass —
delegate it to **one best-fit persona subagent** and fold its verdict back. This is opt-in and
additive: a task that delegates nothing behaves exactly as the 3-beat loop already does.

> **Two modes.** *Single-advisor* (this section): one persona subagent per beat, run to a returned
> verdict — when a beat wants one expert lens. *Parallel streams* (§ Parallel streams, below): N
> mutually-independent tasks built at once, each in its own git worktree, joined losslessly — when a
> milestone's frontier is several tasks that do not depend on each other. Both keep the four floors;
> neither lets a subagent own a gate.

The engine stays **NO-EXEC**: it never spawns, never reads a persona on the build path. `add brief
--for-subagent` *composes* the deterministic core; **the skill wraps and spawns**; the engine only
records that the returned verdict is present. Selection, spawn, and fold are your judgment.

## The four floors — a subagent never buys these back

A delegate is expertise and hands, never permission. Whatever persona it wears:

<constraints>
- **A subagent never owns a gate.** It returns findings + a confidence self-score; **you** (or the
  human at freeze) gate. A delegate may never run `add freeze` or `add gate` on its own authority.
- **security = HARD-STOP** — un-persona-negotiable. A stronger delegate never softens a security
  finding; it escalates it. Only the human may strike the carve-out.
- **High-risk scope still escalates** to the human — a persona is a lens, not a lowered floor.
- **The delegate stays inside `scope:`** and never edits a frozen `gives:`; a needed change is a
  change-request back to Direction, exactly as for the main thread.
</constraints>

## The pipeline — compose → wrap → spawn → fold

### 1 · Compose the deterministic core
```bash
add brief <slug> --for-subagent > /tmp/<slug>.core.xml
```
This is the budgeted, hashed `<task standalone="true">` — objective, the node's `<persona>` (if the
node names one), dependency cards, frozen `needs`, the specs' *decisions-that-bind*, the verbatim
`<subject>`, and a `<close>add run … then add gate …</close>`. Refs resolve **at brief time**, so it
already carries current scope. **Never hand-edit it** — it is content-addressed; edit the node and
re-brief instead.

### 2 · Wrap it in the Rule-5 envelope
The core is the *payload*; the envelope is the *orchestration*. Wrap — never replace — the core:

```xml
<objective>{the beat's outcome, one line from the node goal}</objective>
<persona>{the roster pick — see below — injected as its Identity + Critical Rules}</persona>
<execution_context>{paste the /tmp/<slug>.core.xml here — the frozen truth}</execution_context>
<files_to_read>{the anchors the node's scope names — actual paths, not a guess}</files_to_read>
${AGENT_SKILLS}          <!-- the skills the delegate should load; ADD itself if it will drive add -->
<mcp_tools>{prefer mcp__serena for code nav; name what this repo exposes}</mcp_tools>
<success_criteria>       <!-- lifted from the node's CHECKS / gives — the delegate's done-bar -->
  - [ ] every Must/Reject check green (the `covers:` set)
  - [ ] residue examined (security · concurrency · architecture)
  - [ ] returns a verdict + confidence self-score (below); does NOT gate
</success_criteria>
```

The `<success_criteria>` are **the node's own CHECKS**, not new invented ones — the delegate proves
the contract, it does not redefine it. Close the envelope by asking for the **confidence self-score**
(0–1 on completeness · clarity · practicality · edge-cases); a score < 0.9 means refine before
returning, not a softer gate.

### 3 · Spawn — pick model, effort, isolation
Spawn ONE `Agent()` with the wrapped prompt. Pick per the work (Rule-5 heuristics):

- **model** — `sonnet` simple · `opus` complex · `fable` very-complex or fast bulk.
- **effort** — `low` fast · `medium` balanced · `high` complex (only `low` with `fable`).
- **isolation** — sequential single-advisor needs **none**; one `worktree` per stream is how the
  parallel-streams mode keeps concurrent builders from racing (§ Parallel streams).
- **agentType** — prefer a tool-equipped specialist that fits the persona (roster column below).

### 4 · Fold the verdict — evidence, not a rubber stamp
The delegate returns findings; **you** record them against the beat with severity markers so a
scanning human sees weight at a glance. **🔴 severity is beat-aware** — the same finding means
different things before and after the build:

- **🔴 blocker** — at **direction/build**: a missing or unmet Must/Reject → **fold it into
  RULES/CHECKS** (backward-correction is always allowed) or fix the build before freeze; escalate to
  the human only if it cannot be discharged by a check. At **verify**: an unmet Must → **HARD-STOP**
  to the human. A **security** finding is a **HARD-STOP at every beat**, no exception — never folded away.
- **🟡 concern** — a real risk with a named cost; surface it in the gate's FLAGS (`gate.md`).
- **💭 note** — an observation worth an OBSERVE-beat delta (`deltas.md`), not a gate item.

Record **which persona did the work** in the beat's artifact (never in a state file). Then the beat
continues on the normal rails: `add run <slug> -- <cmd>` for the bound receipt, and the human/verify
`add gate`. The delegate informs the gate; it never is the gate.

## The roster — role → persona → executor → when

One persona drives a beat; `use-when` / `not-when` route it over a sibling. Personas are distilled
from the teacher corpus (`personas.md` §Seed); the `agentType` is the tool-equipped subagent that
best carries the lens in this environment.

| Role | Persona (teacher) | Suggested `agentType` | Beats | use-when |
|------|-------------------|-----------------------|-------|----------|
| Systems / API | `personas-teacher/engineering/engineering-backend-architect` | `backend-expert` · `python-expert` | direction · build | a contract, IO, persistence, or failure design |
| Security | `personas-teacher/security/security-architect` | `security-expert` | verify · advisor | **any** security/data/auth scope — the HARD-STOP lens |
| Experience / UX | `personas-teacher/design/design-ux-architect` | `frontend-expert` | direction · verify | a user-facing surface, accessibility, or a perf budget |

Selection is per-beat and cheapest-fit: **no persona named and no floor raised → don't delegate**,
drive it yourself. A security/data/architecture scope **always** pulls the Security lens into verify,
whatever else drives the build. When two fit, `use-when`/`not-when` in the persona frontmatter
decides; when still tied, ask the human — never run two in v1.

## When delegation is the wrong tool

Delegating has a real cost (a full subagent drive ≈ 1.5–2× the inline cost — the census measured it).
Delegate when the beat genuinely wants expertise or a fresh adversarial read; **do not** delegate a
one-liner the main thread can do, and never delegate the human decision itself. The advisor sharpens
the work; the gate, the freeze, and the floor stay exactly where the 3-beat loop put them.

## Read fan-out — facts merge, decisions serialize

Read-only work fans out FREELY: grounding a milestone, the residue lenses, explore-lane research
(`phases/explore.md`) — spawn N parallel readers with **no wave, no worktree, no disjoint-scope
proof**. The wave machinery below exists to serialize DECISIONS; reads return facts, and facts merge
— contradictory findings surface to the human at the fold, the same divergence rule join uses.

Read-only is pinned to the **spawn instruction**, not to good intentions: a delegate whose prompt
asks for any edit is a writer, and one write instruction anywhere taints the whole delegate — that
spawn is wave-gated (builds carry implicit decisions; parallel writers need the disjoint-scope
proof below). Findings fold with their read time — a reader that ran beside a build observed a
moving tree.

The floors hold at any fan-out width: no reader owns a gate; findings fold back through the main
thread, which records them against the beat; and a security finding from ANY reader is a
HARD-STOP, exactly as from the main thread.

## Parallel streams — build the whole frontier at once

When a milestone's frontier is **several tasks that do not depend on each other**, build them
concurrently instead of one at a time. The engine stays NO-EXEC: it **plans** the wave and **joins**
the results; **you** create the worktrees and spawn the builders. Four steps — plan → isolate →
build → join.

### 1 · Plan the wave (the engine proves it is safe to parallelise)
```bash
add wave <milestone>                      # derive the DAG schedule: topological LEVELS, each a
                                          #   maximal antichain (mutually-independent tasks)
add wave <milestone> --streams a,b,c      # record ONE level as the active wave
```
A level is a set the engine has **proven** safe to run at once. It refuses an unsafe wave, so you
never fan out into a race:
- **R:INTRADEP** — two streams with a dependency path between them (they must sequence across waves).
- **R:OVERLAP** — two streams whose `scope:` shares a file (disjoint scope is the write-safety invariant).
- **R:CYCLE** — a dependency cycle (no parallel plan exists).

### 2 · Isolate — one git worktree per stream
Give each stream its own `git worktree` on its own branch, forked from the join point, each with its
own `.add/`. Because the wave guaranteed **disjoint scope**, the streams only ever touch different
files — so the build phase **cannot race**; the only reconciliation is the join.

### 3 · Build each stream to its gate
Spawn one `Agent()` per stream (the single-advisor envelope above, or drive it directly). Each runs
its **own full 3-beat loop** inside its worktree — direction is already frozen, so it builds to green
and runs `add gate <slug>` **in its worktree**. A stream that hits a security or unmet-Must finding
gates **HARD-STOP** there; it does not merge.

### 4 · Join — fold the worktrees back losslessly
```bash
add join <stream-1>/.add <stream-2>/.add …    # one bundle path per worktree
```
`join` reconciles by ABF's own invariants: **PASS-only** (a HARD-STOP stream is never merged), task
nodes copied **byte-for-byte** (disjoint, lossless), spec deltas **union-merged**, a same-lesson /
different-disposition divergence **FLAGGED** for you (never silently double-kept), and `graph.json`
**regenerated** (never copied). **Rollback** is just dropping a worktree: join leaves every other
stream byte-intact.

### The four floors hold for N builders exactly as for one
<constraints>
- **No stream owns a gate.** Each stream gates its own task in its worktree; join only **records** the
  outcome — it never manufactures a PASS. You (or the human) still own the milestone-level decision.
- **security = HARD-STOP** — per stream and at the join. A HARD-STOP stream is structurally un-mergeable;
  no join flag or union softens it.
- **High-risk still escalates** to the human — a wave is a scheduling tool, not a lowered floor.
- **Each stream stays inside its `scope:`** and never edits a frozen `gives:`; the wave's disjoint-scope
  refusal is what makes that mechanical rather than merely asked-for.
</constraints>

→ persona lifecycle (seed · grow · fold): `personas.md`. The gate render: `gate.md`.
