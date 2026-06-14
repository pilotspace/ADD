# Changelog

All notable changes to the ADD method (`@pilotspace/add` on npm,
`pilotspace-add` on PyPI) are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver.

## [Unreleased]

### Added
- **`update` — refresh a project without re-installing.** The launchers
  (`@pilotspace/add` on npm, `pilotspace-add` on PyPI) gained an `update` verb
  that re-materializes the managed layer (the `add` skill, `.add/tooling`,
  `.add/docs`) to the installed package version. It **clean-replaces** each tree,
  so a file removed upstream no longer lingers as an orphan (the prior
  `init --force` merge behaviour), and it never touches your work — `state.json`,
  `PROJECT.md`, milestones, tasks, and archive are preserved (state is backed up
  to `pre-update-state.bak.json` first regardless). It is idempotent (the same
  version twice is a no-op), records a `.add/.add-version` stamp, and
  `update --check` reports version drift read-only. One-shot per ecosystem:
  `npx @pilotspace/add@latest update` · `pipx run pilotspace-add update`.
- **State-migration framework** — `update` carries a forward-only, idempotent
  migration registry (empty today) so the next state-schema change ships as an
  in-place update, never a re-install.

## [1.2.0] — 2026-06-10

The decision-arc release: the method now narrates the build as one continuous
arc of decisions, and the loop reaches past a single milestone — graduating a
prototype to production, gating milestones on their own goal, and running tasks
in parallel waves. All additive; no breaking changes (SemVer MINOR).

### Added
- **The decision arc** — every human-gate report opens by naming where you are
  on the arc (intent → cases → contract → tests → build → verify → observe), and
  the book + GLOSSARY describe it as the spine of the method. The one human
  approval is always placed on the arc, never floating.
- **Graduation to production** — `add.py graduate` plus a graduate-guide and a
  `→production` stage guard turn the mvp→production transition into an
  analytics-driven, criteria-gated step instead of a label flip: a
  graduation-report surfaces the evidence and a stage-goal-criteria cue tells you
  when the prototype has earned the next stage.
- **Goal-gated milestones & the dynamic task loop** — an explicit project GOAL
  now rides on `status`/`guide`, a milestone completes only when every success
  criterion is met, and a recorded `done → phase` reopen-transition lets a closed
  task legitimately re-open without losing its history.
- **verify-deepen** — the verify phase gained a deep-check rubric
  (wiring · dead-code · semantic) so verification probes intent, not just a green
  suite.
- **Parallel waves** — `WAVE.md`, the wave ledger that is the resume point for
  parallel task execution; `status` surfaces a live wave so a multi-task wave can
  pause and resume cleanly.
- **The flag-first freeze guard** — declaring a contract freeze is now
  fail-closed: an `unflagged_freeze` is refused at `advance` time and flagged by
  `add.py audit`, so a freeze can never be recorded without its explicit marker.
- **Foundations & Lineage chapter** — the book gained an annotated Foundations
  chapter with author-year citations and a references appendix, tracing the
  method's lineage.

### Changed
- Engine prose now speaks one ubiquitous language — `add.py` output uses
  consistent domain terms (scope level, decision point, retrospective, …).
- `add.py compact` keeps the active state lean by compacting heavy archive
  history, with the bundled engine frozen in lockstep.

## [1.1.0] — 2026-06-05

Production-ready enforcement: the gates are now verified by machinery distinct
from the agent, and any AI agent can follow the method through the CLI alone.

### Added
- **`add.py audit [--json]`** — judgment-free, read-only verification that
  human seams left well-formed records: a named human at every contract freeze,
  exactly one gate outcome per done task, a human reviewer wherever the
  security line carries a `NOTE`/`⚠` marker, no waivers on security. Exit 0
  clean / exit 1 with `{task, code, detail}` findings.
- **Seam audit in CI** — a `seam-audit` job (this repo) plus a copy-paste
  workflow for consumer projects (GETTING-STARTED "Enforce the seams in CI"):
  a malformed seam record fails CI on a machine the agent does not control
  (*never self-gate*, enforced).
- **The mechanized high-risk guard** — declare `risk: high` in a TASK.md
  header and the engine refuses to complete the task (`PASS`/`RISK-ACCEPTED`)
  until the dial is lowered to `autonomy: conservative`; error and audit
  finding `unguarded_high_risk_auto`. Judging *what* is high-risk stays human;
  the declared combination is enforced. `HARD-STOP` is never blocked.
- **Agent portability** — `add.py guide` now names the exact phase-guide file
  to read (`guide  : .claude/skills/add/phases/<n>-<phase>.md`, never a dead
  pointer; additive `"guide"` key in `--json`), and the AGENTS.md/CLAUDE.md
  block routes any agent — Claude, Cursor, Copilot, Codex — through the CLI
  alone.
- **The freeze review checklist** — six ⚠-first lines inside the contract
  phase guide that aim the human's one approval (intent · cases · shape ·
  risk declaration · tests), never a second gate.

### Changed
- GitHub Actions bumped off the deprecated Node-20 runtimes
  (checkout v5, setup-python v6, setup-node v5).
- GETTING-STARTED: CI enforcement section + `guide  :` orientation.

## [1.0.0] — 2026-06-04

First public release: the seven-phase flow (specify → scenarios → contract →
tests → build → verify → observe) driven by one `TASK.md` per task, the
`add.py` state tracker (init · status · guide · report · check · gates ·
milestones · competency deltas · fold), the `add` skill for Claude Code, and
the full method book (`.add/docs/`). Installable via
`npx @pilotspace/add init` or `pip install pilotspace-add`.
