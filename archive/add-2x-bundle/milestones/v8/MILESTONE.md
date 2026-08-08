# MILESTONE: AI-first install & milestone on-ramp

goal: After install, a user develops with ADD by talking to the agent — request to milestone to one-approval run — with no add.py typing in the happy path; install output and onboarding teach that flow
stage: mvp · status: active · created: 2026-06-02

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> **Why now.** The skill is already AI-first (intake → milestone → one-approval
> run), but the *install output* and *onboarding* are not: the `sync-guidelines`
> CLAUDE.md block teaches the old manual `phase`/`advance`/`gate` flow, `init`'s
> next-hint jumps to `new-task` (skipping the milestone/intake layer), and the
> onboarding docs walk `add.py` phase-by-phase with no milestone story. v8 makes
> a freshly-installed project teach what the method actually does.

## Scope
In:  (1) **Agent-orientation block** — the `sync-guidelines` CLAUDE.md/AGENTS.md
     template teaches the AI-first flow (orient → intake → milestone → one-approval
     front → self-driving run), replacing today's manual `phase`/`advance`/`gate`
     framing. (2) **Install output** — `init`'s `next:` hint points at the agent
     entry (not `new-task`); verify + fix that `init` actually installs the skill
     (`.claude/skills/add/`) and book (`.add/docs/`) so the AI-first brain is present
     after install. (3) **Onboarding docs** — `GETTING-STARTED.md` + `README.md`
     lead with the conversational `/add` entry and the milestone on-ramp (request →
     intake → milestone → tasks); raw `add.py` demoted to the agent's hands / manual
     escape hatch.
Out: any change to the 7-phase sequence or phase semantics (untouched); any redesign
     of v7's one-approval / auto-default behavior (v8 *documents* it, does not change
     it); any engine judgment in `add.py` (it stays a scaffolder + state tracker, not
     a decider); removing the `add.py` CLI (it stays — it is the agent's hands and the
     human's escape hatch); auto-running anything without the human's spoken request
     (the human still initiates).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **The canonical AI-first entry is the 8-step flow** — install → `/add` → orient
  (`add.py status`) → INTAKE classifies → milestone draft + human confirm → per-task
  one-approval front (Spec+Scenarios+Contract+Tests bundle, ONE approval at the frozen
  contract) → self-driving run (auto, evidence-gated; security = HARD-STOP) → fold
  deltas at close. All four artifacts (block, next-hint, two docs) render THIS SAME
  flow. Frozen here as the shared reference; this milestone doc IS the contract.
- **The human types no `add.py` in the happy path.** The CLI is the agent's hands and
  the human's escape hatch — never the prescribed human interface.
- **Honesty rule (designed vs shipped).** v8 documents the v7-*designed* one-approval /
  auto flow. v7 is at `verify`, not shipped — so the **prose artifacts** (`GETTING-STARTED.md`,
  `README.md`) label v7-designed behavior "as designed in v7" against today's shipped v6
  (conservative, three-gate). **EXEMPT: the terse orientation block** (`_guideline_block()`) —
  a stable minimal pointer (add.py:198–201) cannot carry the caveat without bloating past a
  pointer; it names the *target* flow, and the docs it points to carry the nuance.
  *(amended 2026-06-02 — agent-orientation-block surfaced the pointer-vs-caveat conflict; resolved
  by human at its verify gate.)*
- **Release-ordering constraint.** v8 ships **with or after v7** (v7 already at `verify`), so the
  block's AI-first flow is accurate at release. v8 must not ship ahead of v7.
- New glossary term: **On-ramp** — the install→first-milestone path a new user walks.

## Shared / risky contracts (freeze these first)
- the **canonical AI-first entry flow** (the 8 steps + exactly what the human touches:
  request · milestone confirm · one approval per seam · any HARD-STOP) — riskiest
  because all three tasks must render it identically; frozen in this doc's Shared
  decisions above, every task honors it.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] agent-orientation-block    depends-on: none   — rewrite the `sync-guidelines` CLAUDE.md/AGENTS.md block → the AI-first 8-step flow; mirror both `add.py` trees  · gate PASS
- [x] install-onramp             depends-on: none   — `init` next-hint → agent entry; verify+fix that `init` bundles the skill (`.claude/skills/add/`) + book (`.add/docs/`)  · gate PASS
- [x] milestone-onboarding-docs  depends-on: none   — rewrite `GETTING-STARTED.md` + `README.md` → lead with `/add` + the milestone on-ramp; demote raw `add.py`  · gate PASS

## Exit criteria (observable; map each to the task that delivers it)
- [x] the CLAUDE.md/AGENTS.md block from `sync-guidelines` describes orient→intake→milestone→one-approval→run, with no manual-only framing   (← agent-orientation-block)
- [x] `init` in a clean repo prints an agent-entry next-hint AND leaves `.claude/skills/add/` + `.add/docs/` present                          (← install-onramp)
- [x] `GETTING-STARTED.md` opens with the `/add` conversational entry and walks request→milestone→task (not `add.py`-first)                   (← milestone-onboarding-docs)
- [x] `README.md` "Use it" leads with talking to the agent; `add.py` shown as the agent's hands / escape hatch                                (← milestone-onboarding-docs)
- [x] all four artifacts render the SAME canonical 8-step flow (designed-vs-shipped labelled per the honesty rule)                            (← shared decision, checked across all three tasks)

## Close note (2026-06-02)
All three tasks gated PASS; all five exit criteria met. Milestone marked **done**.
**Release-ordering hold (honors the constraint above):** the npm release of v8 waits until **v7
reaches `done`** — v7 is still at `verify`, and v8 documents the v7-*designed* one-approval/auto flow.
Marking v8 done records that the *work* is complete; it does **not** authorize shipping ahead of v7.
