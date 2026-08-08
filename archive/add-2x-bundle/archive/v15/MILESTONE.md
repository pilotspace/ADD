# MILESTONE: Zero-command on-ramp

goal: After the single install command, a newcomer reaches their first verified feature purely by talking to the AI — no typed add.py commands
stage: mvp · status: active · created: 2026-06-05

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.
>
> Intake rationale (Tin confirmed 2026-06-05): "make Getting started fully
> automated with AI — no commands after install" is an onboarding-automation
> theme no active milestone's goal covers (v14 = enforcement/publish, at exit);
> spans docs + installer UX + skill behavior → new-major, 3 breadth-first tasks.

## Scope
In:  GETTING-STARTED.md restructured around the conversational spine (install →
     open the agent → /add → talk); installer ends with an explicit AI handoff
     and inferable defaults; the /add skill demonstrably drives a fresh install
     setup→first-feature with zero typed commands.
Out: new engine commands (add.py is feature-frozen this milestone); non-Claude
     agent INSTALLERS (the any-agent loop via `guide  :` already ships in 1.1.0);
     telemetry; the full observe loop; dogfood stage flip mvp→production.

## Shared decisions & glossary deltas   (living — every task must honor these)
- The commands never disappear — they move to the escape hatch. "Zero-command"
  means the newcomer NEVER NEEDS one, not that the CLI is hidden (the CLI stays
  the agent's hands + the human's override, per PROJECT.md).
- Shipped 1.1.0 anchors stay green: test_release_1_1_0 pins the orient section
  naming `guide  :` — the rewrite keeps that anchor (constraint, not change).
- One install command is allowed and unavoidable (`npx @pilotspace/add init` /
  `pip install` + `init`); "after install" is where zero-command begins.

## Shared / risky contracts (freeze these first)
- GETTING-STARTED.md section skeleton (the conversational spine + escape-hatch
  appendix) -> owning task getting-started-rewrite
- init handoff text + flag defaults (name inferred from cwd, stage default) ->
  owning task installer-handoff

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] getting-started-rewrite   depends-on: none                — the conversational path becomes the spine; 7-phases-by-hand moves to an escape-hatch appendix; shipped test anchors stay green
- [x] installer-handoff         depends-on: none                — `init` prints the AI handoff ("open Claude Code → /add — no further commands") and infers --name/--stage defaults so the install is one short command
- [x] skill-onramp              depends-on: installer-handoff   — verify /add on a fresh install drives setup→first-milestone end-to-end with zero typed commands; close any gaps found (protocol-walk test)

## Exit criteria (observable; map each to the task that delivers it)
- [x] A newcomer reading GETTING-STARTED top-to-bottom types exactly ONE command (the install) before their first verified feature        (← getting-started-rewrite; spine ban + 16-guard union green, 2026-06-05)
- [x] `npx @pilotspace/add init` with no flags succeeds and its final output names the next action as a conversation, not a command        (← installer-handoff; behavioral pins ×2 + flagless hint, 2026-06-05)
- [x] A protocol-walk test proves the /add flow from fresh install to a gated first task issues every add.py call ITSELF (the human typed none)        (← skill-onramp; test_protocol_walk_zero_typed_commands green against the installed tree + §4/companion guides reworded agent-run, CR v2, 2026-06-05)
