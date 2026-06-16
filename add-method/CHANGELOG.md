# Changelog

All notable changes to the ADD method (`@pilotspace/add` on npm,
`pilotspace-add` on PyPI) are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver.

## [1.7.0] — 2026-06-17

The AI-engineering release: ADD now has an **AI vertical** (EDD —
eval-driven development), the AI analog of the red suite. An AI feature freezes
an **eval contract** before build, verify gates on a **measured eval score**
instead of a green unit suite, and the frozen eval rides ADD's existing tamper
tripwire so it can never be quietly weakened. Additive and silent-when-absent: a
non-AI project sees none of it (SemVer MINOR).

### Added
- **The AI vertical (`ai.md`, `phases/ai.md`)** — the eval-definition loop
  (spec → ladder → eval-set → freeze-the-contract) and the `kind: ai` run
  overlay, loaded on demand like the UDD `design.md`.
- **`new-task <slug> --kind ai`** — records the task kind in `state.json`; the
  kind drives the eval-contract validators and the eval-gated verify.
- **AI eval validators in `add.py check`** — lint the `.add/ai/` named set
  (`eval-set.jsonl` · `rubric.json` · `eval-spec.json` · `io-contract.json` ·
  `fallback.md` · `monitor.json`): held-out-split leakage (HARD-STOP), the
  four rubric buckets thresholded, a pinned bias-mitigated judge, a declared
  baseline, per-failure-mode fallbacks. Silent when `.add/ai/` is absent.
- **`missing_eval_set`** — the freeze precondition: a populated `.add/ai/` set
  with no held-out `eval-set.jsonl` is a hard red (no held-out set, no build).
- **Eval-gated verify** — for a `kind: ai` task, `add.py gate PASS` requires a
  recorded eval run whose score clears the frozen threshold AND beats the
  baseline AND carries its lineage, scored against the frozen eval set
  (`below_threshold` · `no_baseline_gain` · `lineage_unrecorded` ·
  `eval_run_stale` · `safety_hard_stop`). The engine measures; it never runs the
  eval.
- **Eval-contract tamper freeze** — the `eval-set.jsonl` / `eval-spec.json` /
  `rubric.json` are snapshotted into ADD's build-integrity tripwire at
  tests→build; a post-freeze lowered threshold, mutated test row, or weakened
  rubric trips `build_tampered` (un-launderable), exactly like an edited red test.
- **AI templates** — `AI-SPEC.md` (the binding entry doc, the `DESIGN.md`
  analog), the `ai/*` named-set samples, and the `ai-eval.md` dialect.
- **Book chapters 17–19** — the AI vertical, the eval contract and validators,
  and AI verify and observe, plus glossary entries for the EDD terms.

## [1.6.0] — 2026-06-16

The releasing release: shipping a versioned cut is now a first-class **5th ADD
scope level**, not an ad-hoc ritual. The AI gathers the inventory and drafts
evidence-backed notes, the engine records the cut behind a security-hard-stop
readiness floor, and the human owns the tag and publish. All additive; no
breaking changes (SemVer MINOR).

### Added
- **The RELEASE scope level (`release.md`)** — the on-demand guide for the 7-step
  flow `cue → gather → draft notes → readiness floor → human confirms → cut → watch`,
  orthogonal to stage: bundle one or more closed milestones into a versioned,
  watched cut. Cross-referenced from `SKILL.md`.
- **`add.py release-report`** — a read-only gather of the five record-sets (closed
  milestones · their consolidated deltas · riding `RISK-ACCEPTED` waivers · open
  security `HARD-STOP` · scenarios → monitors), with `--json`, plus the
  `→ releasable: N milestone(s)` status cue.
- **`add.py release <version>`** — a guarded, record-only cut: it prepends the
  `CHANGELOG.md` block, appends an append-only `RELEASES.md` ledger row
  (newest-first), and attributes the bundled milestones — behind a four-code
  readiness floor (`release_security_open` · `release_tests_red` ·
  `release_no_closed_milestone` · `release_undisclosed_waiver`). The security stop
  is **un-forceable**: `--force` can override the other three, never that one.
- **`RELEASES.md`** — the append-only release ledger (date · version · milestones ·
  waivers · evidence); membership is the attribution source, so the cue never has
  to read a compacted milestone file.
- **Book chapter 16 (`16-releasing.md`)** + five glossary entries (Release · Release
  scope level · Readiness floor · RELEASES.md ledger · Hotfix release) + the
  `test_release_docs_accord` guard that keeps the book in accord with `release.md`.

### Notes
- **The engine records; the human ships.** `add.py release` writes the changelog +
  ledger + attribution; it never bumps a version source, tags, publishes, or
  deploys. The outward act stays human-owned and tool-agnostic — exactly the
  human-gated `git tag` that cut this very release.

## [1.5.0] — 2026-06-16

The UDD design-loop release: defining the design *before* the code is now a
guided, evidence-backed loop inside the method. A new `design.md` drives the UDD
beats to a confirmed screen, a wireframe + HTML-mock recipe renders a real screen
the human approves before build, and the engine measures that the confirmation
was actually captured. All additive; no breaking changes (SemVer MINOR).

### Added
- **UDD design-definition loop (`design.md`)** — turns the foundation's UDD
  concern into a runnable loop: a low-fi structural wireframe → a self-contained
  HTML mock (resolve semantic tokens → one kit class per component → compose the
  prototype tree → populate with mock data) → a captured screen the human
  confirms *before* any build. Wired into `0-setup` and `1-specify`.
- **Wireframe + HTML-mock recipe (`udd-wireframe.md`) + sample templates** — a
  zero-dependency, any-stack floor for rendering a prototype tree into a real
  screen, with a worked sample set (`tokens.sample.css`, `kit.sample.css`,
  `welcome.sample.html`, `settings.sample.html` reusing the kit,
  `wireframe.sample.txt`). One semantic-token flip re-themes every screen by
  construction. An optional `@json-render/image` (Satori → PNG/SVG, no browser)
  fast path is noted for JS-ecosystem projects.
- **Capture-evidence convention + `missing_capture` WARN** — design captures live
  at `.add/design/captures/<name>.<ext>`; `add.py check` emits a never-red
  `missing_capture` warning for any prototype lacking a capture (silent when
  absent, so non-UI projects stay clean). The engine *measures* capture presence;
  it never renders.

## [1.4.0] — 2026-06-15

The guided-onboarding release: starting and running an ADD project is now guided
and self-tuning. Setup interviews you into a run mode and a first milestone and
deepens each drive, the engine schedules parallel work into dependency waves,
stale installs nudge any agent to update, and the AI carries a human-owned voice
that improves itself. All additive; no breaking changes (SemVer MINOR).

### Added
- **Guided, self-tuning setup** — `0-setup` now interviews instead of assuming:
  it proposes a **run mode** (a parallel+auto vs. sequential comparison table,
  confirm-to-keep the recommended default), sketches a **first milestone** as a
  kickoff suggestion (goal + flow + scenarios, shown before it asks), and runs a
  per-drive **domain deep-dive** (DDD · SDD · UDD · TDD) that captures the
  decisions as ADRs. Onboarding stops being a blank page.
- **`add.py waves` DAG scheduler** — a new read-only command that groups the
  active milestone's open tasks into topological **waves** (a wave is the tasks
  whose in-milestone dependencies have all landed), names the **critical path**,
  emits an advisory **tier hint** (a scope-of-impact proxy for model selection,
  never a gate), and surfaces a transitively-**blocked** set with what each task
  is waiting on. It never mutates state and `streams.md` gains a "DAG strategy"
  section that points at it.
- **`SOUL.md` — a human-owned, self-improving voice** — `init` now scaffolds a
  `.add/SOUL.md` voice doc (schema: Name · Tone · Communication style · Trust ·
  Learns-from · Voice deltas) with a *proposed* "Trusting" starter voice that is
  explicitly yours to rewrite — the tests assert the schema, never the tone words.
  `status` points at it to read each session, and a new `soul.md` guide drives an
  observe→confirm→rewrite **voice-delta loop** (the human is the only writer),
  the voice-side sibling of the competency-delta→foundation loop.
- **Agent-agnostic update nudge** — because every agent is told to run
  `add.py status`/`guide` first each session, the engine uses that one universal
  chokepoint to flag a stale install: on those orientation reads only, when a
  launcher `.add-version` stamp is present and the registry's latest is newer, it
  writes one `ACTION REQUIRED` line to **stderr** naming the channel-correct
  command (`npx @pilotspace/add@latest update` / `pipx run pilotspace-add
  update`). It is the engine's one deliberate, tightly-bounded network touch:
  fail-open (offline/timeout → silent no-op), throttled once per 24 h via a
  git-ignored `.update-cache.json`, inert without a launcher stamp, and silenced
  by `ADD_NO_UPDATE_CHECK=1`. stdout and exit codes are never touched, so `--json`
  stays clean. (Originated as community PR #17.)
- **First-class `add.py autonomy show|set`** — autonomy was the only mutable
  first-class state with no CLI verb, so an agent driving under `autonomy: auto`
  could hallucinate the missing `add.py autonomy` command, hit `invalid choice`,
  and derail an autonomous run. `autonomy show` prints declared · effective
  (fallback-resolved) · project default · the verify-gate owner; `autonomy set
  <level> [slug] [--project] [--yes]` is the first writer of the `autonomy:`
  header token — an idempotent, atomic single-line rewrite (trailing comment
  preserved, never appended) with three fail-closed guards run before any write:
  an invalid level, raising the rung without `--yes` (raising is a human-owned
  trust escalation), and raising a `risk: high` task to `auto`. The command-shaped
  header-edit wording is de-shaped to cite the verb, and an `[enforced]`
  `WORDING_RUBRIC` fence keeps the phantom phrasing from regressing.
- **Foundation compaction across all four specs** — the living foundation now
  stays relevant-first and short as a project grows. Every append-only sequence
  (`PROJECT.md` §Spec · §Key-Decisions · `CONVENTIONS.md` learnings) reads
  **newest-first**, and at milestone close the AI proposes collapsing each spec's
  shipped, zero-open-residue tail into one per-spec **rolled-up settled line** —
  the human confirms one line at a time; it summarizes and points to git, never
  deletes, and every open residue stays expanded. A new `compact-foundation.md`
  skill guide drives the ritual — convention-guided, with no new engine command,
  and distinct from `add.py compact` (which archives finished-milestone files).
  The loop chapter and glossary document it.
- **Per-step Advisor + Confidence context** — every ADD step now carries a thin
  pointer to two new shared skill guides: `advisor.md` (when and how to delegate
  one plan-following subagent — vendor-neutral; the engine never spawns) and
  `confidence.md` (an advisory 0–1 self-score across six dimensions, refine if any
  dimension scores below 0.9). Both are advisory by construction — the self-score
  is never a gate — making delegate-and-self-assess first-class guidance for any
  agent driving the loop.
- **`.add/.gitignore` scaffolded at init** — `init` now writes a co-located
  `.add/.gitignore` so the engine's transient local artifacts (scope snapshots,
  pre-archive backups, the update-nudge cache) never reach git. It is additive and
  never clobbers an existing copy; edit it freely.

### Changed
- **Conversational-only install hand-off** — after `init`, the closing hint points
  only at the conversational entry point: open your AI agent CLI, run `/add`, and
  say what you want to build. The hand-off is tool-agnostic (Claude Code, Codex,
  …) and no longer advertises a manual `add.py new-task` / `--await-lock` escape
  as the primary path (the flag still exists; `/add` runs it internally).

## [1.3.0] — 2026-06-13

The render-ready-foundation release: a UI project now gets a lintable design
foundation the AI drafts from, a build's declared scope is enforced as a gate,
every command names who drives the next step, and the new update command
refreshes an installed project in place. All additive; no breaking changes
(SemVer MINOR).

### Added
- **Render-ready UDD foundation** — a `DESIGN.md` prose front-door plus a JSON
  foundation (3-layer design tokens · a component catalog · flat prototype
  content trees) the AI drafts UI from, wired into 0-setup. `add.py check` now
  lints the named set under `.add/design/`, going red with a named code on any
  layer, catalog, tree, or cross-file token-resolution violation — and staying
  silent when a project has no design set, so non-UI projects are unaffected.
  A `udd-tokens.md` + `udd-catalog.md` pair documents the compact-DTCG dialect
  and the json-render render recipe.
- **The scope gate** — a task's `§5 Scope (may touch)` declaration is frozen
  into a snapshot at tests→build and enforced at the gate: an out-of-scope touch
  heals the task back to BUILD for an honest redo (counting against a per-task
  cap), while erased gate evidence fails closed. Scope creep can no longer ride a
  green suite into a merge.
- **Engine next-step footer + the driver marker** — every completing command now
  prints exactly one engine-sourced `next:` line, and names who owns it:
  `[you drive]` when the AI proceeds, `[human gate]` at a decision point. The
  driver marker resolves from one place (autonomy × phase), so the next step and
  its owner are never ambiguous across a session.
- **The `update` command** — `npx @pilotspace/add update` (and the
  `pilotspace-add update` command on PyPI) re-materializes the managed layer
  (skill · tooling · docs) to the installed package version without a re-install.
  It never touches your work — `state.json`, `PROJECT.md`, milestones, tasks, and
  archive are preserved (state is backed up first regardless) — is idempotent via
  a `.add-version` stamp, and offers `--check` to report version drift without
  writing.

### Changed
- The foundation self-improved across these milestones: closing
  `udd-design-foundation` folded its OBSERVE backlog into the versioned
  CONVENTIONS/PROJECT foundation (foundation-version 29), sharpening the
  contract-completeness, adversarial-refute, and engine-pin conventions.

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
