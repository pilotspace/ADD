# Parallel streams — pipelining independent tasks

Load this **only** when a milestone has more than one task and you want to run them
concurrently. The default ADD path is one task at a time; this rubric is the opt-in
escape hatch for when independent tasks are queued and a human is ready to review.

It changes **no `add.py` code and no phase semantics**. It is a way *you, the
orchestrator*, drive several tasks at once by reading the dependency DAG that
`add.py status` already prints, and spawning one worker per ready task.

## The honest frame — this is pipelining, not N× speed

With **one human reviewer** you cannot beat `review_time × N_tasks` (the human-led
decision points are serial — `docs/10-setup-and-stages.md:91`). So the win is **not throughput**:
it is that the reviewer is **never blocked waiting on a build**. While the human reviews
task A's frozen bundle, the builds for B·C·D run behind *their* frozen contracts. You hide
build latency under human latency. Do not promise more than that.

## The two queues

Compute both from one `python3 .add/tooling/add.py status` — no new state:

- **READY-QUEUE** — tasks in the active milestone where `phase ≠ done` **and** every
  `deps=` task already shows `gate=PASS`. These are the only tasks a worker may pick up.
  A task with unmet deps stays queued; a task finishing PASS unblocks its dependents on
  the next `status`.
- **REVIEW-QUEUE** — the irreducibly serial part: the **bundle approval** (contract
  freeze) and any **Verify escalation**. One human, one queue. Present these one at a
  time, never in a batch the human will approve without reading.

```
  add.py status ─► READY-QUEUE ──spawn workers──► builds run ──► REVIEW-QUEUE ──► done
  (deps=PASS?)     (machine span)                 (concurrent)   (decision points,
       ▲                                                          strictly serial)
       └──────────────── a task gating PASS unblocks its dependents ──────────────┘
```

## The autonomy level is the throttle (not a new flag)

How much concurrency you actually get is set by each task's `autonomy:` header
(`run.md`), not by this rubric:

| `autonomy` (TASK.md) | What serializes on the human | Concurrency |
|----------------------|------------------------------|-------------|
| `conservative` / `manual` | bundle approval **+** every Verify | pure pipelining — builds overlap, both gates queue (`manual` is the strict floor; same streams behaviour) |
| `auto` (default) | bundle approval **only**; Verify auto-PASSes on evidence | real concurrency — only the decision point + residue escalations queue |
| `auto` but **high-risk** | refused → must lower to `conservative` / `manual` (`unguarded_high_risk_auto`) | back to pipelining, by design |

The irreducible floor is **one human approval per task at the contract decision point** — the decision point
never drops to zero (`run.md:22`). That floor is correct; do not engineer around it.

## Who writes what — the hard boundary

<constraints>
- **You (orchestrator)** own all shared writes: `MILESTONE.md`, and every
  `add.py advance <slug>` / `add.py gate <outcome> <slug>` call. **Always pass the explicit
  `<slug>`** — `advance`/`gate`/`phase` all take an optional task slug and act on it
  (`add.py` `_resolve_task`); omitting it falls back to the single `active_task`, which
  races once more than one stream is live. Name the task every time. Workers never run these.
- **A worker** owns only its own `.add/tasks/<slug>/` — it builds `src/`, drives the
  tests green, gathers evidence, and writes `SUMMARY.md` + OBSERVE deltas. It touches
  **no sibling stream and no shared file**.
- **Isolation**: spawn each worker with `isolation="worktree"` so concurrent builds
  cannot collide. The worktree is discarded on failure; the task resets to its last-good
  phase.
</constraints>

## Design for failure (required)

- **Fresh worktree base (verify base == HEAD)** — create each worker's worktree from current
  `HEAD` **after** you commit the task's frozen specification bundle (spec · scenarios · contract · tests). A
  worktree forked from a stale base forces the worker to recreate the frozen artifacts by hand
  (the v10 dogfood hit exactly this). Before the worker starts, confirm `git -C <worktree>
  rev-parse HEAD` equals the orchestrator's `HEAD`; if it drifted, `git merge` the base in first.
  On a runner that creates each worktree **at spawn** from a pool (e.g. Claude Code), that pool can hand
  out a STALE base, so the pre-spawn `rev-parse` evidence cell is unsatisfiable. The `unverified_fork_base`
  check then **shifts** — it never skips: the worker's **step-0** syncs to base (`git merge` the orchestrator's
  `HEAD`) and re-echoes `rev-parse HEAD`, which the orchestrator verifies at **merge-time**, before merge-back.
  The pre-spawn check stays the DEFAULT for fresh-`HEAD`-worktree runners; the merge-time path is the additive
  ALTERNATIVE for spawn-time runners — never a replacement of the pre-spawn rule.
- **Lease + timeout** — record which worker holds which task (in the wave ledger, below);
  if a worker dies, release the claim back to READY (re-spawn, do not assume partial work is sound).
- **Failure isolates** — a worker that hits a STOP-and-escalate (below) blocks only its
  own task. Siblings keep running; the escalation joins the REVIEW-QUEUE.
- **Circuit-breaker** — if N workers fail in a wave, stop fanning out and fall back to
  sequential. Repeated failure means the scope was wrong, not the parallelism.

## Wave ledger — the wave's resume point

A single task resumes from `state.json`; a wave used to resume from nothing — the
task ↔ lease ↔ fork-base ↔ autonomy ↔ merge-order mapping lived only in the orchestrator's
chat context, and the v12-1 recurrence proved that discipline without an artifact fails
(the base check existed in prose and never ran). The ledger fixes both: it is the file you
re-orient from, and its evidence cells cannot be filled without executing the checks.

**The file** — `.add/milestones/<m>/WAVE.md`, orchestrator-owned like `MILESTONE.md` and
`state.json`. ONE live wave per milestone at a time; opening a second while one is live is
refused (`wave_already_live`). **Workers never read WAVE.md** — the orchestrator copies the
relevant mid-wave decisions into each worker's PROMPT.md at spawn/respawn, so the worker
contract below stays unchanged and no worker widens into sibling state.

```markdown
# WAVE.md — transient wave ledger (orchestrator-owned · one live wave per milestone)
wave: <n> · opened: <date> · status: live|merging
base: <orchestrator HEAD at spawn — the sha every fork must equal>

### Roster (lease ledger)
| task   | lease (worker) | fork-base (pasted)                          | autonomy | spawned | timeout |
|--------|----------------|---------------------------------------------|----------|---------|---------|
| <slug> | wt-a           | <paste `git -C <wt> rev-parse HEAD` output> | auto     | <time>  | <dur>   |

### Mid-wave decisions
- <date> <decision a later or respawned worker must honor — copy it into that worker's PROMPT.md>

### Merge order (serial; integration Verify per merge)
1. <slug> → 2. <slug>
```

**Evidence cells, not ticks.** The fork-base cell holds the PASTED output of
`git -C <worktree> rev-parse HEAD`, and it must equal `base:`. A tick is not evidence; a row
you can only fill by running the command is the fresh-worktree-base check EXECUTING — the
v12-1 lesson (words-exist ≠ method-works) closed structurally. Spawning a worker whose roster
row lacks that evidence is refused (`unverified_fork_base`). On a spawn-time pool runner this
PRE-spawn paste is unsatisfiable (the pooled base is stale until the worker syncs), so the cell
instead holds the worker's **step-0** post-sync echo (still `== base:`) and the `unverified_fork_base`
refusal **shifts to merge-time**, before merge-back — it shifts, it never lifts.

**Lifecycle — open → consume → digest → delete.** Open the ledger when the first worker
spawns. The serial integration Verify consumes it (the merge order is read from it, one
worktree at a time). At wave close, absorb the evidence digest — wave base · roster→fork-base
evidence · merge order · integration-Verify outcome — into `MILESTONE.md` as an append-only
`## Wave log` block (this is the integration-Verify *record*, previously homeless), and only
then remove the file. Removing WAVE.md before the digest is absorbed is refused
(`digest_not_absorbed`) — the proof the checks ran must outlive the file.

**Resume rule.** On session start, a live WAVE.md is the wave's resume point: re-orient from
the file — roster, bases, decisions, merge order — never from conversational memory.

## Merge is serial — integration Verify

Parallel build, **serial integration**. After workers return, you merge the worktrees
one at a time and run the **integration** Verify — the concurrency / architecture / layering
checks that `run.md:102` says automation cannot judge. Two green tasks in isolation can
still conflict when merged; this step is where that surfaces. Never auto-pass it.

Each worktree carries a full copy of `.add/`. Merge back **only** `src/`, `tests/`, and the
worker's own `.add/tasks/<slug>/` (TASK.md · SUMMARY.md) — `.add/state.json`, `MILESTONE.md`,
and the live `WAVE.md` stay orchestrator-owned, or a parallel merge will drag stale state back.

## The worker contract — portable across coding agents

A worker **is** the dynamic run (`run.md`) for one task. Keep two things separate:

- **The contract** (below) — the prompt. It is **agent-agnostic**: it names no vendor tool,
  no model, no spawn API. It is a durable ADD artifact, like the spec and the tests.
- **The adapter** (next sections) — the thin, swappable mapping that tells *one* runner
  (Claude Code · Codex · opencode · pi-mono · any CLI agent) how to launch the contract.

This split is the whole point: the same frozen contract runs on any agent; only the adapter
changes. Fill every `{{...}}` per stream. The ADD-specific value is `<touch_boundary>` + the
"return a verdict, never write shared state" rule — they are identical on every runner.

```xml
<!-- PROMPT.md — dropped into the worker's worktree, or passed inline. No runner-specific tokens. -->
<objective>
Execute the LOCKED dynamic run for task '{{TASK_SLUG}}' in milestone {{MILESTONE}}:
drive §4 TESTS red→green against the FROZEN contract {{CONTRACT_VERSION}}, converge, and
resolve verify per autonomy={{AUTONOMY}}. You own ONLY the machine-led span — the two human
decision points (bundle approval · escalated Verify) are NOT yours.
</objective>

<persona>
You are a {{DOMAIN}} engineer with 15 years building {{DOMAIN_DETAIL}}.
A wrong-but-plausible result here is expensive; correctness over speed.
Work step by step:
1. Load the context files. Confirm the start gate: §3 CONTRACT FROZEN @ {{CONTRACT_VERSION}}
   AND §4 TESTS RED for the right reason. If not → STOP and escalate (forward-skip forbidden).
2. Build in small batches in src/ until the red tests pass — never weaken or skip a test.
3. Converge: loop-until-dry · adversarial-verify every 'done' claim · completeness-critic.
4. Resolve verify per the boundary. Write SUMMARY.md + OBSERVE deltas (deltas.md grammar).
Score confidence (0-1) on Completeness · Clarity · Practicality · Optimization · EdgeCases ·
Self-Eval; if any < 0.9, refine before returning.
</persona>

<touch_boundary>   <!-- from run.md:56-73; the worker's contract, identical on every runner -->
MAY:  rewrite code in src/ · drive tests green WITHOUT weakening them · gather verify evidence.
MUST NOT: edit the frozen CONTRACT or locked scope · weaken/delete/skip any test ·
          touch §1–§3 bundle artifacts · write MILESTONE.md / state.json / any sibling stream.
STOP-and-escalate (return your findings; do not decide):
  • a discovered scope/contract gap  → backward-correction, reopen Specify (principle 4)
  • any SECURITY finding              → HARD-STOP, always
  • a concurrency/timing OR architecture/layering risk the tests cannot exercise
  • [include this bullet when autonomy is conservative OR manual — any lowered rung] the verify gate itself — STOP for the human
Auto-PASS only if autonomy=auto AND: all tests green · coverage not decreased · no test weakened ·
  no contract edited · loops dry · completeness-critic clean · no residue above. Log it as
  auto-resolved, naming this run as owner — never forge a human signature.
</touch_boundary>

<context_files>   <!-- paths relative to the worktree root -->
.add/PROJECT.md · .add/milestones/{{MILESTONE}}/MILESTONE.md (READ-ONLY) ·
.add/tasks/{{TASK_SLUG}}/TASK.md · .claude/skills/add/run.md · .claude/skills/add/deltas.md
</context_files>

<expertise>
Adopt the persona above. If your runner supports specialist injection — a Claude Code skill,
a Codex/opencode system-prompt preamble, an agent profile — load the one matching {{DOMAIN}}.
If it does not, the persona IS your expertise.
</expertise>

<tools>
Navigate with your runner's code-intelligence: mcp__serena under Claude Code; LSP / ctags /
ripgrep otherwise. Design every IO path for failure — timeouts, retries, rollback.
</tools>

<return>   <!-- the worker PROPOSES; the orchestrator RECORDS. A worker never runs add.py. -->
End with a structured verdict AND write the same into SUMMARY.md in the task dir, then
**commit SUMMARY.md + deltas.md** in the worktree (uncommitted worktree files survive only by
harness courtesy — commit them so the serial-integration merge-back carries your report):
{ task, outcome: PASS|RISK-ACCEPTED|HARD-STOP|ESCALATE, evidence: <tests+coverage>,
  residue: [security|concurrency|architecture findings], deltas: [open lessons learned] }.
Do NOT touch add.py or any shared file — the orchestrator gates on your verdict.
</return>
```

## Choosing the model — vendor-neutral tiers

ADD picks a **tier** from the scope's nature; the adapter maps the tier to the runner's model id.
The contract is identical whichever model runs it (the model is disposable, like the code):

| Tier | When | Claude Code | Any other runner |
|------|------|-------------|------------------|
| **mid** | ordinary, well-tested scope; clear contract | `sonnet` | the runner's balanced model |
| **top** | complex / ambiguous / cross-cutting / broad scope of impact | `opus` | the runner's strongest reasoning model |

Two rules sit **above** model choice and never bend:
- **High-risk ⇒ a lowered rung (`conservative` or `manual`), regardless of model** (`run.md` high-risk guard). A
  stronger model does not buy back the human gate.
- **Security residue always escalates** — no tier and no model auto-passes it.

## The spawn adapter — one thin mapping per runner

ADD needs six capabilities from any runner. **Isolation is the one ADD owns itself** (a git
worktree), so streams stay portable even on a runner with no native sandbox — ADD makes the
worktree, then points the agent at that directory.

| ADD needs | Abstract | Claude Code (verified reference) | Any CLI agent — Codex · opencode · pi-mono · … |
|-----------|----------|----------------------------------|-----------------------------------------------|
| spawn a worker | prompt + label | `Task(description=…, prompt=…)` | `cd $WT && <agent> run --prompt-file PROMPT.md` |
| pick the model | tier → id | `model="opus"\|"sonnet"` | a `--model <id>` flag |
| isolate | worktree | `isolation="worktree"` | `git worktree add $WT HEAD` (after committing the bundle; verify base == HEAD), then run inside it |
| load context | files / cwd | `<context_files>` + repo cwd | run inside `$WT`; paths are relative |
| domain expertise | skill / preamble | a Claude skill in `<expertise>` | a system-prompt / profile preamble |
| return a verdict | structured | final message (optionally a schema) | stdout JSON the orchestrator parses |

The **hint of `Task` spawn** is the Claude Code column — the worked reference. For any other
agent the recipe is the same shape: `git worktree add` → point the agent CLI at that dir with
the chosen model → it reads `PROMPT.md` → you parse its verdict.

> **Honesty:** only the Claude Code column is verified. The CLI forms for Codex/opencode/pi-mono
> are *illustrative shapes*, not confirmed flags — exact syntax differs per runner and version;
> confirm with the `find-docs` skill. The portable, durable parts are the **contract** and the
> **six-capability mapping**, never any one runner's flags.

When workers return, **you** record each outcome with the explicit slug — `add.py advance <slug>`
as evidence lands, `add.py gate PASS|RISK-ACCEPTED|HARD-STOP <slug>` at verify — then re-read
`status` to refill the READY-QUEUE. The worker proposes a verdict; the orchestrator records it.
That split is exactly what lets a non-Claude worker take part without ever touching shared state.
