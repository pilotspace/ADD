---
name: add
description: >-
  ADD (AI-Driven Development) — a lean, state-tracked workflow where the AI writes the code and
  the human owns direction and verification. Drives every change through one atomic task node:
  Direction (specify · plan · red tests) → Build → Verify, red/green TDD built in, trusted on a
  recorded receipt not a plausible diff. Research rides the same rails: "investigate this bug",
  "evaluate this library", "research X" route to the Explore lane. Use whenever a repo has a
  `.add/` bundle, or the user says "add", "/add", "start a task", "next phase", "specify this",
  "ADD method", "AI-driven development", or wants spec/tests-first discipline over vague-prompt
  coding. Resumes across sessions from the bundle alone — run `add status`, never re-read the repo.
user-invocable: true
category: workflows
keywords: [add, aidd, ai-driven-development, spec-first, tdd, contract, receipt, gate, task, resume, explore, research]
argument-hint: "status | <describe the change or goal>"
license: MIT
metadata: { author: add, version: "3.1.0", format: ABF-1 }
---

# ADD — direction · evidence · a durable bundle (the agent is the hands)

You turn intent into the right-sized task, then drive it. ADD keeps the AI fast *and* safe by
**fixing direction before the build** (rules, contract, red tests) and **trusting the result on
passing evidence**, not on a diff that reads plausible. The bundle survives; the code is disposable.

**Engine.** `add` below = `python3 .add/tooling/cli.py` (the ABF-1 CLI) — the vendored copy the
installer drops into your project, which stamps `tooling_engine:`; `status --check` warns if it drifts.
**First run in a fresh project** (no `.add/tooling/` yet): materialize it once with the package
installer — `pilotspace-add init "<name>"` (pip) or `add init "<name>"` / `npx @pilotspace/add init
"<name>"` (npm), or `node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init "<name>"` when installed as the
Claude Code plugin — then drive from `.add/tooling/cli.py`. State
lives in the `.add/` bundle — files are the database, `graph.json` is a rebuildable cache. The engine
records; it never runs the method or spawns an agent. The full loop surface — including `fold ·
reopen · deltas · milestone-archive` — is wired.

## Always start here (orient — do not skip)

Run **`add status`** first, every session — it is your resume point, read from the bundle, not the
repo. Then branch:

- **No `.add/` yet** → `add init --profile <code|doc> "<name>"` — those two ship, and `init`
  refuses any other name rather than guess. Non-code domain? Take `doc`, then re-author its
  lenses (`domains.md`). Offer to seed starter personas (`seed.md`,
  opt-in), then size the request (Intake).
- **A task is active** (`status` not `done`) → open `.add/tasks/<slug>.md`, read its `## CARD`, and
  work the beat `add status` names next. The beat is **derived from the node's stamps**, not the
  `status` field — which stays `direction` until close: unfrozen → author + freeze; frozen with no
  green receipt → build; a fresh green receipt → verify (loop below).
- **No active task** → size the request first (Intake), then create scope.

## Intake — size before you create scope (`intake.md`)

Read the request into a task shape, then pick the **lane** (you route; the human vetoes):

- **Quick** — one file / adjacent few, behavior the specs already cover, no new contract, mechanical.
  Make the edit, then leave a receipt: the git diff + `add … learn <dd> "<lesson>"`. No task node.
- **Task** — one atomic node in the active milestone's scope. The 3-beat loop below.
- **Explore** — the answer IS the deliverable (research · investigate · high unknowns) — explore-first:
  questions + a hard budget freeze, and the gate reads the cited `## FINDINGS` brief directly —
  **no run receipt** for a findings-only explore (`phases/explore.md`). One contract-shaping
  unknown already argues this lane; freezing a contract on a guess ships the wrong thing with
  perfect receipts.
- **Project / milestone** — a new theme or a slice too big for one task. Load the best-fit persona
  whose `flow:` includes **advisor** BEFORE drafting (skip silently if none is seeded), draft the
  milestone (goal · scope · exit criteria · breadth-first task list), confirm it, create it and its
  tasks, and record the lens: `add advise <milestone> --persona <p>`.

**The floor is closed:** anything touching **security · data · architecture** always becomes a real
task — never Quick, whatever its size. **Security is always a HARD-STOP.** When in doubt, size up.

## The 3-beat loop (this file IS the loop; refs load on demand)

One task = one atomic node. Three beats, one human decision:

1. **DIRECTION** (`phases/direction.md`) — compose the whole bundle in ONE draft, then take the ONE
   approval. The draft, section by section:
   - `## RULES` — Must · Reject: what you were told. EDGES are the boundaries of those rules —
     without them, a thing nobody said becomes a Must phrased like one that was said.
   - `## ASSUMPTIONS` — sweep EVERY `gives:` surface on EVERY dimension
     (`who · which · when · absent · order · experience`): `A<n> [<dim>] covers: <S ids> · <what the spec does
     NOT say — and the reading you took> -> <cost if wrong>`, or retire a pair with
     `[<dim>] n/a · <why>`. A cheaply-checkable guess is better discharged than priced: run the
     two-minute probe and record `found: <what>` + its evidence on the line.
   - `## PLAN` — contract shape (you author it into the node's `gives:`/`needs:` frontmatter) ·
     strategy · `scope:` tokens.
   - `## CHECKS` — one check per Must and per Reject, each with a `covers:` key. The binding is
     enforced at **gate**, and it binds EVERY referent you name — Musts, Rejects, probed
     assumptions, edges. Run the checks **red for the right reason**.
   - `freeze` REFUSES on a template slot, an unauthored `gives:`, or an unswept `(dim, surface)`
     pair — and names them; `add todo` counts them down while you author.
   - The ONE approval stamps direction closed: **`add freeze <slug> --by "<name>" --authority
     human`**. Get the composed prompt with `add brief <slug>` — its refs resolve from the graph,
     so a spec edit re-scopes it with no edit here.
2. **BUILD** (`phases/build.md`) — code until every red check is green. Change **no** check and **no**
   frozen `gives:`; stay inside `scope:`. A discovered constraint or a strategy turn is *steering* —
   record it, seal untouched: `add replan <slug> --note "<what changed>"`. Anything that would move
   a frozen surface is a change-request back to Direction, never a silent edit.
3. **VERIFY** (`phases/verify.md`) — gather evidence, check the 3 residue lenses (security · concurrency
   · architecture — **security HARD-STOP**), then `add run <slug> --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- <test cmd>` for a
   fresh, bound receipt — wrap the **narrowest command that reports every bound check**; the full
   suite rides CI. **No runner for your domain? Write one** — `run` parses JUnit XML and does not
   care what produced it, so a script comparing a measured value against a threshold your frozen
   RULES already state earns the same bound receipt (`domains.md`). And **`add gate <slug> PASS --by "<name>"`** — a **PASS auto-closes** the task
   (and repairs its CARD). `add done` is only for closing after a signed `RISK-ACCEPTED`.

Emit **lessons** as you learn them, tagged by which of the five specs they sharpen
(`ddd · sdd · udd · tdd · add`) — they fold into `.add/specs/` at close (`loop.md`, `deltas.md`).
Present every human decision — intake · freeze · gate · close — as a guided choice with the goal→done→plan
arc (`gate.md`). Adopting a project-fit persona is opt-in (`personas.md`); a persona never lowers a gate.
Delegate a beat to a best-fit persona subagent when it wants an expert (`streams.md`) — the delegate
advises and returns a verdict; it never freezes, never gates, and security stays HARD-STOP. Read-only
research fans out freely — facts merge; one write taints the stream back onto the serialized path.

## Non-negotiable rules (from the method)

<constraints>
1. **Direction before speed.** Never start Build until RULES · PLAN · CHECKS exist and checks are red.
2. **Trust evidence, not inspection.** A change is trusted because its checks pass and the residue
   (security · concurrency · architecture) was examined — not because the code reads fine.
   **A green gate proves the checks you declared ran, passed and are bound — never that they were
   enough.** A check that asserts nothing still binds and still passes. Writing the check that would
   have caught the bug is your job; the engine can only prove you ran the ones you wrote
   (`FORMAT.md` §10).
3. **Never weaken a check or edit a frozen `gives:` to make the build pass.** That inverts the method;
   a real change is a change-request back to Direction.
4. **No silent skips.** Every Verify ends in exactly one recorded outcome — `PASS`, `RISK-ACCEPTED`
   (signed, non-security), or `HARD-STOP`. A security finding is always `HARD-STOP`.
5. **A refusal is the method working.** Every engine refusal names its fix in the same breath
   (`next: <verb>`) — do that fix. Never route around the engine, never hand-edit state files or
   stamps to get past a refusal it just gave you.
</constraints>

## Command cookbook — copy a line

```bash
add status                                   # resume · --all full · --check conformance
add init --profile code "<name>"             # create a .add/ bundle — code | doc ONLY (see domains.md)
add upgrade                                  # 2.x bundle? archive it whole, init 3.0, MIGRATION.md guides re-authoring
add new Task <slug> --title "..." --depth quick|standard|deep [--kind explore] [--milestone m] [--scope a,b]
                                             # --sensitivity security|data|architecture sets the floor
add brief <slug>                             # the composed XML prompt for the active beat
add todo [--milestone m]                     # the open worklist by beat, each with its next verb
add locate <path>                            # which node's scope owns this file
add advise <slug> --persona <p>              # record the lens that reviewed a sequential beat
add doctor                                   # report-only findings — never writes, never gates
add freeze <slug> --by "<name>" --authority human    # the ONE approval → Build
add replan <slug> --note "<what changed>"    # record a steering turn on a frozen task — seal untouched
add run <slug> [--timeout <s>] --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- <test cmd>   # execute → a fresh, bound receipt
add gate <slug> PASS --by "<name>"           # verdict — a PASS auto-closes · RISK-ACCEPTED (signed) · HARD-STOP
add done <slug>                              # close after a RISK-ACCEPTED (a PASS gate already closed it)
add learn <ddd|sdd|udd|tdd|add> "<lesson>" --evidence <ref>   # file a lesson into a living spec
add milestone-done <slug>                    # close a milestone — refuses while a goal box is unchecked
```

## Depth dial — steps never change, ceremony does

Depth tunes **ceremony**, not the authority floor. The floor is computed by the engine from
`sensitivity:` (and `index.md`'s `sensitive_paths:`) — `security → human`, `data|architecture → plan`,
else `process` — never from depth.

- **quick** — CARD · CHECKS · EVIDENCE; at a green, `covers`-bound receipt the AI may record the PASS
  itself at `process` authority (an explicit pass you run, not an engine auto-verdict), unless the
  sensitivity floor is higher.
- **standard** — the full node; evidence-gated, at whatever authority the floor computes.
- **deep** — full node + milestone strategy, lowest-confidence-first; a human owns freeze whenever the
  floor (or your judgment) calls for it.

A coined term you cannot decode is in `terms.md` — load it once, not every session.
The method's **why** lives in `FORMAT.md` (the ABF-1 bundle format, in the ADD source repo) —
**referenced, never inlined** (load the State; reference the Story). Read it only when a decision is
genuinely unclear. The AIDD book is deeper background and is **external** (not shipped with the skill)
— treat it as optional; never block waiting to open a file the skill does not ship.
