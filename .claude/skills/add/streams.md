# Parallel streams — pipelining independent tasks

Load this when a milestone has more than one task and you want to run them concurrently.
**Default:** when a project confirms `parallel + auto` as its run mode at setup
(`phases/0-setup.md` "Run mode"), parallel streaming is the project default — an **opt-out**, not
the opt-in it once was; downgrade in one step (`add.py autonomy set conservative --project`, or
just run tasks one at a time). A project that kept the conservative run mode still treats this
rubric as the opt-in escape hatch.

It changes **no `add.py` code and no phase semantics**. It is a way *you, the orchestrator*,
drive several tasks at once by reading the dependency DAG `add.py status` already prints and
spawning one worker per ready task.

## The honest frame — this is pipelining, not N× speed

With **one human reviewer** you cannot beat `review_time × N_tasks` (decision points are serial).
The win: the reviewer is **never blocked waiting on a build** — builds for B·C·D run behind *their*
frozen contracts while the human reviews A. Build latency hides under human latency.

## The two queues

Both from one `add.py status` — no new state:

- **READY-QUEUE** — tasks where `phase ≠ done` **and** every `deps=` task shows `gate=PASS`.
  Unmet deps stay queued; a PASS unblocks dependents.
- **REVIEW-QUEUE** — the serial part: **bundle approval** (contract freeze) + any **Verify
  escalation**. One human, one queue; present one at a time, never batched.

```
  add.py status ─► READY-QUEUE ──spawn workers──► builds run ──► REVIEW-QUEUE ──► done
  (deps=PASS?)     (machine span)                 (concurrent)   (decision points, serial)
       ▲
       └──────── a task gating PASS unblocks its dependents ──────────────────────────┘
```

## The DAG strategy — let the engine schedule the waves (`add.py waves`)

Do **not** eyeball the READY-QUEUE by hand once a milestone has more than a couple of tasks.
`add.py waves` (read-only) groups not-done tasks into **topological waves**, names the **critical
path**, and emits an advisory **tier hint**:

```
$ add.py waves
milestone: v13-onboarding-polish
wave 1: dag-scheduler, setup-suggest-milestone, setup-domain-deepdive, soul-artifact
wave 2: setup-run-mode (deps: dag-scheduler), soul-self-improve (deps: soul-artifact)
critical path: dag-scheduler → setup-run-mode  (2 tasks)
tier hint: top → dag-scheduler, setup-run-mode; mid → the rest
```

- **Wave = a fan-out batch.** Every task in a wave has all in-milestone deps PASS, so the whole
  wave is spawnable at once (`isolation="worktree"`). Finish a wave, gate tasks PASS, then
  `add.py waves` again — the next wave is unblocked.
- **Run the widest wave first** to hide the most build latency under human review latency.
- **Spend your strongest model on the critical path.** Critical-path tasks gate the most
  downstream work; off-path tasks take **mid**. The tier hint is advisory — override when you
  know a task is harder than its position suggests.
- **`--json`** (`{ milestone, waves, critical_path, critical_path_len, tiers, blocked }`) feeds
  a runner that spawns programmatically. `blocked` lists tasks whose dep cannot be satisfied
  within this milestone; a `dependency_cycle` is refused with the offending members named.

The irreducible floor holds — `waves` decides *order and model*, never *whether the human gate fires*.

## The autonomy level is the throttle (not a new flag)

| `autonomy` (TASK.md) | What serializes on the human | Concurrency |
|----------------------|------------------------------|-------------|
| `conservative` / `manual` | bundle approval **+** every Verify | pure pipelining — builds overlap, both gates queue |
| `auto` (default) | bundle approval **only**; Verify auto-PASSes on evidence | real concurrency — only the decision point + residue escalations queue |
| `auto` but **high-risk** | refused → must lower (`unguarded_high_risk_auto`) | back to pipelining, by design |

The irreducible floor is **one human approval per task at the contract decision point** — that
floor never drops to zero (`run.md:22`). Do not engineer around it.

## Who writes what — the hard boundary

<constraints>
- **You (orchestrator)** own all shared writes: `MILESTONE.md`, and every `add.py advance <slug>` /
  `add.py gate <outcome> <slug>` call. Always pass the explicit `<slug>` — **name the task every time** —
  omitting it falls back to the single `active_task`, which races once more than one stream is live.
  Workers never run these.
- **A worker** owns only its own `.add/tasks/<slug>/` — it builds `src/`, drives tests green,
  gathers evidence, and writes `SUMMARY.md` + OBSERVE deltas. It touches **no sibling stream and
  no shared file** — never write shared state (state.json, MILESTONE.md, a sibling's files).
- **Isolation**: spawn each worker with `isolation="worktree"` so concurrent builds cannot
  collide. The worktree is discarded on failure; the task resets to its last-good phase.
</constraints>

## Design for failure (required)

- **Fresh worktree base (verify base == HEAD)** — cut each worktree from current `HEAD` **after**
  committing the frozen bundle; confirm `git -C <worktree> rev-parse HEAD` equals the orchestrator's
  `HEAD` (drifted → `git merge` first). On a pool runner (e.g. Claude Code) the check **shifts** to
  the worker's **step-0** (sync + re-echo `rev-parse HEAD`), verified at **merge-time**. The engine
  gates this (`engine-merge-base-enforcement`): `add.py wave-verify` before the first merge-back
  refuses a mismatched/pending echo (`unverified_fork_base`) or off-template ledger
  (`wave_ledger_malformed`); `add.py check` is the standing monitor.
- **Lease + timeout** — record which worker holds which task (wave ledger); a dead worker releases
  its claim back to READY.
- **Failure isolates** — a worker's STOP-and-escalate blocks only its own task; siblings run on, the
  escalation joins the REVIEW-QUEUE.
- **Circuit-breaker** — if N workers fail in a wave, stop fanning out and fall back to sequential.
  Repeated failure means the scope was wrong, not the parallelism.

## Wave ledger — the wave's resume point

**The file** — `.add/milestones/<m>/WAVE.md`, orchestrator-owned. ONE live wave per milestone;
opening a second while one is live is refused (`wave_already_live`). **Workers never read
WAVE.md** — the orchestrator copies relevant decisions into each worker's PROMPT.md at spawn.

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
`git -C <worktree> rev-parse HEAD` and must equal `base:`. Filling the row requires running the
command — words-exist ≠ method-works. Spawning a worker whose roster row lacks that evidence is
refused (`unverified_fork_base`). On a pool runner the cell holds the worker's **step-0**
post-sync echo (still `== base:`) and the refusal **shifts to merge-time**.

**Lifecycle — open → consume → digest → delete.** Open when the first worker spawns. At wave
close, absorb the evidence digest — base · roster fork-base · merge order · integration-Verify
outcome — into `MILESTONE.md` as an append-only `## Wave log` block, then remove the file.
Removing WAVE.md before the digest is absorbed is refused (`digest_not_absorbed`).

**Resume rule.** On session start, a live WAVE.md is the wave's resume point: re-orient from the
file — roster, bases, decisions, merge order — never from conversational memory.

## Merge is serial — integration Verify

Parallel build, **serial integration**. After workers return, merge worktrees one at a time and
run the **integration** Verify — the concurrency / architecture / layering checks automation
cannot judge. Two green tasks in isolation can still conflict when merged. Never auto-pass it.

Each worktree carries a full copy of `.add/`. Merge back **only** `src/`, `tests/`, and the
worker's own `.add/tasks/<slug>/` (TASK.md · SUMMARY.md) — `.add/state.json`, `MILESTONE.md`,
and the live `WAVE.md` stay orchestrator-owned.

## The worker contract — portable across coding agents

A worker **is** the dynamic run (`run.md`) for one task. The contract below is **agent-agnostic**:
no vendor tool, no model, no spawn API — a durable ADD artifact. The adapter (next sections) is
the thin, swappable mapping for one runner. Fill every `{{...}}` per stream.

```xml
<!-- PROMPT.md — dropped into the worker's worktree, or passed inline. No runner-specific tokens. -->
<objective>
Execute the LOCKED dynamic run for task '{{TASK_SLUG}}' in milestone {{MILESTONE}}:
drive §4 TESTS red→green against the FROZEN contract {{CONTRACT_VERSION}}, converge, and
resolve verify per autonomy={{AUTONOMY}}. You own ONLY the machine-led span — the two human
decision points (bundle approval · escalated Verify) are NOT yours.
</objective>

<persona>
Load `.add/personas/{{PERSONA_SLUG}}.md` (Identity→you · Critical Rules→constraints · Success
Metrics→done-bar); no match → the generic default below. Portable body + per-runner spawn stubs:
`templates/PROMPT.persona.md.tmpl` (one canonical body; Claude Code verified, the rest illustrative).
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

<strategy>
The task's §5 plan — the Strategy (ordered batches) order and the Known-problem fixes — is
your PREFERRED starting path, not a hard rule. Improve on it when a better strategy emerges
as you build; on done, report the strategy you ACTUALLY used so the orchestrator can update
§5 for the audit trail.
</strategy>

<touch_boundary>   <!-- from run.md; the worker's contract, identical on every runner -->
MAY:  rewrite code in src/ · drive tests green WITHOUT weakening them · gather verify evidence.
MUST NOT: edit the frozen CONTRACT or locked scope · weaken/delete/skip any test ·
          touch §1–§3 bundle artifacts · write MILESTONE.md / state.json / any sibling stream.
STOP-and-escalate (return your findings; do not decide):
  • a discovered scope/contract gap  → backward-correction, reopen Specify (principle 4)
  • any SECURITY finding              → HARD-STOP, always
  • a concurrency/timing OR architecture/layering risk the tests cannot exercise
  • [include this bullet when autonomy is conservative OR manual] the verify gate itself — STOP for the human
Auto-PASS only if autonomy=auto AND: all tests green · coverage not decreased · no test weakened ·
  no contract edited · loops dry · completeness-critic clean · no residue above. Log it as
  auto-resolved, naming this run as owner — never forge a human signature.
</touch_boundary>

<context_files>   <!-- paths relative to the worktree root -->
.add/PROJECT.md · .add/milestones/{{MILESTONE}}/MILESTONE.md (READ-ONLY) ·
.add/tasks/{{TASK_SLUG}}/TASK.md · .claude/skills/add/run.md · .claude/skills/add/deltas.md
</context_files>

<expertise>
If your runner supports specialist injection (a Claude Code skill, a system-prompt preamble, an
agent profile), load the one matching {{DOMAIN}}. Otherwise the persona above IS your expertise.
</expertise>

<tools>
Navigate with your runner's code-intelligence: mcp__serena under Claude Code; LSP / ctags /
ripgrep otherwise. Design every IO path for failure — timeouts, retries, rollback.
</tools>

<return>   <!-- the worker PROPOSES; the orchestrator RECORDS. A worker never runs add.py. -->
End with a structured verdict AND write the same into SUMMARY.md in the task dir, then
**commit SUMMARY.md + deltas.md** in the worktree (uncommitted files survive only by harness
courtesy — commit them so the serial-integration merge-back carries your report):
{ task, outcome: PASS|RISK-ACCEPTED|HARD-STOP|ESCALATE, evidence: <tests+coverage>,
  residue: [security|concurrency|architecture findings], deltas: [open lessons learned] }.
Do NOT touch add.py or any shared file — the orchestrator gates on your verdict.
</return>
```

## Choosing the model — vendor-neutral tiers

ADD picks a **tier** from the scope's nature; the adapter maps the tier to the runner's model id.

| Tier | When | Claude Code | Any other runner |
|------|------|-------------|------------------|
| **mid** | ordinary, well-tested scope; clear contract | `sonnet` | the runner's balanced model |
| **top** | complex / ambiguous / cross-cutting / broad scope of impact | `opus` | the runner's strongest reasoning model |

Two rules sit **above** model choice: **high-risk ⇒ a lowered rung (`conservative` or `manual`),
regardless of model** — a stronger model does not buy back the human gate. And **security residue
always escalates** — no tier auto-passes it.

## The spawn adapter — one thin mapping per runner

ADD needs six capabilities from any runner. **Isolation ADD owns itself** (a git worktree), so
streams stay portable even without a native sandbox.

| ADD needs | Abstract | Claude Code (verified reference) | Any CLI agent — Codex · opencode · pi-mono · … |
|-----------|----------|----------------------------------|-----------------------------------------------|
| spawn a worker | prompt + label | `Task(description=…, prompt=…)` | `cd $WT && <agent> run --prompt-file PROMPT.md` |
| pick the model | tier → id | `model="opus"\|"sonnet"` | a `--model <id>` flag |
| isolate | worktree | `isolation="worktree"` | `git worktree add $WT HEAD` (after committing the bundle; verify base == HEAD), then run inside it |
| load context | files / cwd | `<context_files>` + repo cwd | run inside `$WT`; paths are relative |
| domain expertise | skill / preamble | a Claude skill in `<expertise>` | a system-prompt / profile preamble |
| return a verdict | structured | final message (optionally a schema) | stdout JSON the orchestrator parses |

> **Honesty:** only the Claude Code column is verified. The CLI forms for Codex/opencode/pi-mono
> are *illustrative shapes* — confirm exact syntax with the `find-docs` skill.

When workers return, **you** record each outcome with the explicit slug — `add.py advance <slug>`
as evidence lands, `add.py gate PASS|RISK-ACCEPTED|HARD-STOP <slug>` at verify — then re-read
`status` to refill the READY-QUEUE. The worker proposes; the orchestrator records.
