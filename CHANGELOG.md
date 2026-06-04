# Changelog

All notable changes to the ADD method — the book, the skill, and the published
packages — are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). One version tag publishes
both distribution channels: `@pilotspace/add` (npm) and `pilotspace-add` (PyPI).

## [Unreleased]

_Nothing yet._

## [1.1.0] — 2026-06-04

The **trust-layer-truth** release. Milestones v6–v10 changed how the engine behaves
(auto-PASS by default, three approvals collapsed to one, deltas/fold/streams shipped)
but the book and skill still described the pre-v6 manual model. This release makes the
docs tell the truth, hardens the newest surfaces, and makes both installers
cross-platform.

### Added

- **`add.py use <slug>`** — switch the active task to an existing one without
  hand-editing `state.json` (rejects unknown slugs). Closes the gap that forced manual
  state edits when juggling parallel streams.
- **Fold-pressure nudge** — `add.py status` and `milestone-done` now surface the open
  competency-delta count and point at `add.py deltas`, so a fast run's learnings no
  longer pile up unfolded (rescues the v5 self-improving-foundation premise).
- **Book chapters for shipped subsystems** — competency deltas, the fold ritual, and
  foundation versioning (ch. 09/14) plus parallel streams (ch. 10) now have real
  coverage instead of a single footnote.
- **pip install path documented** — `GETTING-STARTED.md` teaches
  `pip install pilotspace-add` → `pilotspace-add init` alongside the npm path, with a
  Windows `py`-launcher note.

### Changed

- **The book and skill now match the engine.** Verify is the evidence **auto-gate**
  (auto-PASS by default per the `autonomy:` dial), not "human-only"; the human-led
  front is **one approval** at the frozen contract, not three; the flow is **seven
  steps** (Observe is step 7) consistently across ch. 02 and the requirements matrix.
- **`npx @pilotspace/add init --force`** now performs a **clean replace** of the skill
  tree rather than a merge, so a re-install can no longer leave orphaned files from a
  previous version behind — matching the pip installer's behavior.

### Fixed

- **Cross-platform install** — the npm installer now also tries the Windows `py`
  launcher and prints a platform-correct manual-recovery command when Python is absent.
- **State engine designs for failure** — a corrupt/unreadable `state.json` exits with a
  clean `state_invalid` message instead of a raw traceback; `status` survives schema
  drift and a stale active-task slug; `_write_retro` is atomic; `archive-milestone`
  writes a recoverable pre-archive snapshot before its destructive deletes.
- **Multi-line competency deltas** — `add.py check` and the deltas report now read a
  delta whose `(evidence: …)` wraps onto a continuation line in full, instead of
  truncating it to the first line.

### Tests

- New regression guards for every change above: trust-layer truth (`test_v11_docs`),
  the fold-nudge, state-engine hardening, streams safety clauses + slug-routing
  precedence, the pip quickstart path, the runtime `add_method.__version__` as a third
  synced version source, and `PyWheelTest` — which builds the real wheel and asserts the
  bundled skill/docs/tooling ship. The suite grows to **299 green**.

## [1.0.0] — 2026-06-02

First public release of ADD (AI-Driven Development) as an installable skill plus the
complete AIDD book as its trust layer.

### Added

- **The method, shippable.** `npx @pilotspace/add init` (npm) and `pilotspace-add init`
  (PyPI) drop the `add` skill into `.claude/skills/add/`, the state-tracked tooling
  into `.add/tooling/`, and the full book into `.add/docs/` — without ever clobbering
  existing project state.
- **Co-specification.** The Specify phase is now AI + human drafting the spec together
  and validating it by surfacing assumptions ranked **least-sure first** (⚠) — replacing
  the old flat pre-ticked assumption list. The frozen contract is the single approval gate.
- **The one-approval front.** Spec + Scenarios + Contract + Tests are drafted as one
  bundle; the human gives one approval at the frozen contract; build→verify then runs
  self-driving, with security findings always stopping back to the human.
- **State on disk, not in chat.** `add.py status` resumes any session at its exact
  phase — no context rot across sessions.
- **The AIDD book** (`docs/`): Foundations, the six steps in depth, operating it across
  a team, and copy-paste reference appendices (templates, prompts, glossary, a fully
  worked money-transfer example, checklists, and the requirements matrix).
- **Dual-ecosystem packaging.** npm package `@pilotspace/add` and PyPI package
  `pilotspace-add`, both at 1.0.0, built from one byte-identical bundled tree guarded by
  parity tests.
- **Autonomous release CI** (`.github/workflows/publish.yml`): a version tag runs the
  full test suite, asserts the tag matches both manifests, then publishes to npm
  (with provenance) and PyPI (via OIDC trusted publishing). A companion `ci.yml` runs
  the suite on every push and PR.

### Release channels

- **npm** — `@pilotspace/add@1.0.0` is published and installable.
- **PyPI** — `pilotspace-add` 1.0.0 publishes on the first version tag once the trusted
  publisher is configured (see `.github/workflows/publish.yml`).

[Unreleased]: https://github.com/pilotspace/ADD/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pilotspace/ADD/releases/tag/v1.0.0
