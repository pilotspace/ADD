# MILESTONE: Autonomous Onboarding — zero-touch setup → human lock-down

goal: Point ADD at any repo and it autonomously drafts the foundation, first-milestone scope, and a candidate first contract — silent for an existing codebase, interview-then-autonomous for a new one — all frozen at a single human lock-down.
stage: mvp · status: active · created: 2026-06-04

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  AI-invokable + brownfield-aware `cmd_init` (infers name, picks a stage, detects a
     non-empty repo); an atomic `add.py lock` command that records the foundation/scope/
     contract lock layers in `state.json` and gates downstream commands until locked; a
     `SETUP-REVIEW.md` artifact listing every drafted decision least-sure-first, tagged
     evidence-grounded vs. guessed; a rewritten `phases/0-setup.md` + SKILL routing for
     the autonomous-draft → lock-down flow; aligned book chapters 10 / 13 / 14.
Out: no web/hosted lock-down UI (CLI + chat only); no auto-fold of competency deltas into
     PROJECT.md (fold stays a separate ritual); the greenfield 4-lens interview is KEPT,
     not removed; no change to the shipped v6–v7 build→verify autonomy; single-repo root
     only (no monorepo / multi-package scan).

## Shared decisions & glossary deltas   (living — every task must honor these)
- `lock-down` — the single human gate that freezes the autonomously-drafted foundation +
  first-milestone scope + candidate first contract. It is the setup-altitude analog of the
  contract freeze; the lock-down gate and the first task's v7 one-approval-front collapse
  into the SAME human action.
- `evidence-grounded vs. guessed` — every drafted decision in setup carries this tag so the
  human's single lock-down is informed, not a rubber stamp. Brownfield decisions are
  evidence-grounded (read from code); thin-greenfield decisions are flagged guessed.
- Brownfield = fully silent (zero questions; the code answers them). Greenfield = keep the
  4-lens interview, then draft autonomously to the lock.
- `add.py init` is non-clobber (already true at add.py:318) and stays so; autonomy never
  overwrites an existing survivor file or existing state.

## Shared / risky contracts (freeze these first)
- `state.json` lock-flag schema delta (foundation/scope/contract locked + drafting model +
  timestamp) -> owning task `setup-lock-state`   [everything depends on this]
- `add.py lock` CLI contract (name · args · JSON output · exit codes · one atomic action ·
  downstream gating) -> owning task `setup-lock-state`
- `SETUP-REVIEW.md` template shape -> owning task `setup-review-artifact`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] setup-lock-state       depends-on: none                                  — state.json lock flags + atomic `add.py lock` + downstream gating (freeze-first contract)
- [x] brownfield-scan        depends-on: setup-lock-state                      — skill guide + `cmd_init` brownfield detection: read existing code → fill survivors, never-clobber, evidence-vs-guess tags
- [x] setup-review-artifact  depends-on: setup-lock-state                      — `SETUP-REVIEW.md` template + least-sure-first presentation rules
- [x] autonomous-setup-guide depends-on: setup-lock-state,brownfield-scan,setup-review-artifact — rewrite `phases/0-setup.md` + SKILL routing; owns zero-touch entry (no `.add/` → AI runs `init` itself) + chains the v7 one-approval-front to candidate-freeze the first task's contract   <!-- verify gate HELD until installer-arm lands: the flow is unreachable while the installer pre-inits (see gap note below) -->
- [x] installer-arm          depends-on: setup-lock-state                      — installer (npm `bin/cli.js` + pip `_installer.py`) drops files only; STOP auto-running `add.py init` so `/add` finds an un-inited repo and the AI arms the gate with `init --await-lock`   <!-- 6th task, human-approved 2026-06-04 (Option A) -->
- [x] book-align             depends-on: autonomous-setup-guide                — update docs 10 / 13 / 14 to describe the autonomous-setup → lock flow consistently

<!-- MILESTONE GAP (found 2026-06-04 at the autonomous-setup-guide verify gate): both shipped installers
     (bin/cli.js:111, src/add_method/_installer.py:128) run PLAIN `add.py init` as their last step. Plain init
     writes no `setup` key → grandfathered-locked (add.py:202-208), so by the time `/add` runs the gate has
     never armed AND the `brownfield:` signal was already printed in the terminal (the AI never sees it) →
     `/add` routes to Intake, never to 0-setup.md. The autonomous-setup → lock-down flow was therefore
     UNREACHABLE through the dominant install path. None of the original 5 tasks touched the installer.
     Human chose Option A (2026-06-04): installer drops files only; the AI runs `init --await-lock` itself —
     which makes 0-setup.md §1's existing entry condition true with zero guide-prose change. -->

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py lock` atomically records the lock layers; pre-lock the engine ALLOWS the first task + its full front but refuses a SECOND task, advancing into build/verify/observe/done, and `gate` — each with a clear `setup_unlocked` error   (← setup-lock-state)   <!-- refined at the setup-lock-state freeze (2026-06-04): gate sits at the build boundary, not at task creation, so the autonomous flow can draft its own first contract -->
- [x] Plain `init` and legacy projects (no `setup` key) are grandfathered-locked — zero behavior change   (← setup-lock-state)
- [x] On an existing repo, the AI fills survivor files from the code with ZERO questions, never clobbers an existing file, and tags each decision evidence-vs-guess   (← brownfield-scan)
- [x] On an empty repo, the AI asks the 4-lens questions, then drafts autonomously through to the lock   (← autonomous-setup-guide)
- [x] The installer (npm + pip) drops files only and does NOT auto-run `add.py init`; so on a fresh install `/add` finds no `.add/state.json`, the AI runs `init --await-lock` itself (arming the gate + seeing the `brownfield:` signal), and the lock-down flow is reachable by default   (← installer-arm)
- [x] At lock, the first task's TASK.md §1–§3 (spec · scenarios · contract) exist and §3 is `FROZEN @ v1` (lock-authorized) — there is NO per-task engine flag; the freeze is artifact-observable + recorded by the setup `contract` lock layer   (← autonomous-setup-guide)   <!-- reworded at the autonomous-setup-guide freeze (2026-06-04): `contract_locked=true` implied an engine field; task 1 deliberately added none (grep confirms), so the criterion is the observable artifact -->
- [x] A `SETUP-REVIEW.md` lists every drafted decision least-sure-first for the human to sign   (← setup-review-artifact)
- [x] Book chapters 10 / 13 / 14 describe the autonomous-setup → lock flow consistently   (← book-align)
