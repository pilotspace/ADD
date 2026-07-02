# Changelog

All notable changes to the ADD method (`@pilotspace/add` on npm,
`pilotspace-add` on PyPI) are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver.

## [1.15.0] — 2026-07-02

Ten milestones — the largest bundle yet — round out ADD's self-knowledge
(**context-search**, **seams**, **artifact-graph**, **traceability-ids**,
**ground-trust**, **drift-guard**), extend it past static rules
(**persona-teacher-bundle**, **persona-learning-loop**, **advisor-gated-autonomy**),
and past Claude Code itself (**portable-roster**). All additive; nothing removed
or renamed on the CLI surface.

### Added (context-search — find prior work before you drift into it)
- **`add.py search <keyword...>`** — case-insensitive substring search over the
  milestone/task corpus (active + archived), title/goal/rationale lines only, never
  the full body. Surfaced at new-scope drafting and inside the specify/scenarios
  phase guides, so related prior work is found before drafting — not after a
  conflicting design ships.

### Added (seams — one home for a shared contract)
- **`SEAMS.md`.** Symbols that ≥2 tasks touch get promoted into a milestone-level
  doc that §0 references, so a shared contract has one home instead of being
  re-derived — and drifting — per task.

### Added (artifact-graph — a traversable cross-artifact graph)
- **Bidirectional backlinks.** Every ADD artifact now carries minimal backlink
  metadata (task↔milestone↔release↔deps↔delta) so the cross-artifact graph is
  traversable without re-deriving it by hand.

### Added (traceability-ids — every rule earns a stable ID)
- **`M#` / `R#` rule IDs.** Every §1 Must/Reject rule gets a stable ID that §2
  scenarios and §4 tests reference via a `covers:` line, plus lint coverage so no
  rule ships unscenarioed or untested.

### Added (persona-teacher-bundle — a vendored, pinned teacher corpus)
- **agency-agents, vendored.** The agency-agents teacher corpus ships as a pinned,
  MIT-attributed local library (`.add/personas-teacher/`), bundled into both the
  npm and PyPI distributions, de-branded from method prose, and refreshed on a
  schedule. The engine stays NO-EXEC; the release build is zero-network.

### Added (persona-learning-loop — personas that learn your project)
- **Project-fit personas.** The AI seeds requirements personas at setup (a living
  doc the project uses live), grows them through the observe→fold self-improve
  loop, applies them at UDD/advisor/build, and exposes a cross-runner
  (Claude Code · Codex · …) persona-aware subagent prompt.

### Added (advisor-gated-autonomy — earn autonomy through instrumentation, not by removing the gate)
- **A persisted, advisor-guarded `auto + parallel` run mode** so high-speed builds stay safe
  without a human on every step. The whole milestone was dogfooded — every task built
  `conservative` / human-gated, because you cannot auto-gate the feature that relaxes auto-gating.
- **`sensitivity:` taxonomy.** A human-declared TASK-header risk-CLASS (base
  `security · data · architecture · mechanical`, project-extensible via `GLOSSARY.md`) — ADD now
  reasons about *what kind* of risk, not just *how much* (`risk:`). Validated at freeze; the engine
  never classifies.
- **Persisted run mode + setup choice.** The `auto + parallel` posture is persisted and chosen at
  setup; `add.py status` shows `run mode: parallel + auto`. The non-interactive default stays
  byte-identical.
- **Persisted DAG-plan snapshot.** An auditable snapshot of the computed plan (waves · critical path ·
  tiers) with a freshness check vs the live `depends_on` edges (edges stay the source of truth).
- **Advisor 3-lens verdict.** The refute-read becomes a tier-aware single advisor running a sequential
  security → concurrency → architecture sweep recorded in §6 (Verdict · Residue · Binding) — the
  non-functional review is now structured and auditable; `advisor_verdict_unrecorded` measure-not-block lint.
- **Advisor coverage audits (measure, never block).** `add.py audit` flags a missing advisor verdict,
  a self-reviewed verdict (reviewer = author), and a mechanical task with advisor-found residue (mis-tier).
- **`advisor-gate-relax` — the narrowest safe relaxation.** A `risk: high` + `sensitivity: mechanical`
  task with a recorded `Verdict: PASS` + `Residue: none` auto-completes via `gate PASS` without a lowered
  autonomy level. **Security and every non-mechanical class are never relaxed** — the human-in-the-loop
  floor is untouched.
- **Per-phase spawn hint.** `status`/`guide` print an advisory subagent-spawn hint (idiom + tier) for the
  active phase; advisory only — the engine still never spawns.
- Documentation, glossary (4 new terms), and headers aligned with the feature.

### Added (portable-roster — the phase-roster for every coding tool, not just Claude)
- **`AGENTS.md` / `.clinerules` carry the roster.** Non-Claude coding tools (Cursor,
  Copilot, Codex, Cline, …) now receive the ADD phase-roster's 5 roles and
  boundaries through the `AGENTS.md` the installer already drops, not just
  Claude Code's native subagents.
- **`add-advisor` — the 5th roster agent.** A consultative, frontier-model agent
  (`model: opus`) any phase can spawn on a medium-hard decision — an ambiguous
  read, a risky shape, a change of approach. It recommends and weighs tradeoffs;
  it never decides.

### Changed (ground-trust — GROUND surfaces problems, not just structure)
- **GROUND now surfaces the issues/risks** it finds in the real code (feeding
  SPECIFY) and links each task's related intent back to the foundation
  (`PROJECT.md` · `GLOSSARY.md` · conversation) — specs build on problems found,
  not assumed.

### Changed (drift-guard — kill §0 reference rot)
- **§0 cites symbols, not line numbers**, stamps `ground_sha`, refreshes at close,
  and strips dead live-phase scaffolding at done — a closed TASK.md stays true to
  the code instead of rotting the moment a line shifts.

### Added / Changed (loose tasks since 1.14.0)
- **Report template PLAN/SHAPE + APPROVE banner** (`report-plan-approve`) — the
  chat-report decision point renders a clearer guided-choice banner.
- **`status` pagination** (`status-pagination`) — milestones/tasks sort by
  updated-descending and cap to the top 10, with a `--all` escape hatch, so a
  long-lived project's `status` stays scannable.
- **Lean 3-agent phase roster + adaptive persona agent** (`phase-agents-lean`).
- **Skill-tree compaction** (`skill-tree-compaction-audit`) — audited and
  compacted the ADD skill tree for genuine prose redundancy under the pinned
  lean-fence budget.
- **Vendor-tree `.gitignore` fixes** — nested `.add/.gitignore` vendor-tree
  patterns now resolve relative to `.add/`, not repo root
  (`gitignore-vendor-path-fix`); the installer's own `.gitignore` seed covers all
  3 managed vendor trees (`installer-gitignore-mirrors`); `update --global`
  re-seeds `.gitignore` for every registered project, not just fresh installs
  (`update-global-gitignore-seed`).
- **CI tooling-mirror gap closed** (`ci-tooling-mirror-gap`) — the `.add/tooling`
  dogfood mirror is materialized in CI's test + publish-guard jobs, not just
  locally.
- **Fresh-checkout skip-count tolerance widened**
  (`nested-suite-skip-count-tolerance`) — the nested-suite OK-regex now tolerates
  every known environment-conditional skip, not just the recursion guard.
- **Scope-walk hygiene** — `.claude` pruned from the scope walk
  (`scope-exclude-claude`); stale mirror trees re-synced to canonical
  (`mirror-resync`); `.add/tooling` untracked as a regenerable dogfood mirror
  (`untrack-add-tooling`).

### Changed
- Five version sources bump in lockstep to **1.15.0** (`package.json`,
  `package-lock.json` ×2, `pyproject.toml`, `.claude-plugin/plugin.json`,
  `add_method.__version__`).

This release bundles **10 closed milestones** (`seams`, `context-search`,
`drift-guard`, `artifact-graph`, `ground-trust`, `traceability-ids`,
`persona-teacher-bundle`, `persona-learning-loop`, `advisor-gated-autonomy`,
`portable-roster`) and 13 loose tasks since 1.14.0. Every milestone was built
end-to-end through ADD's own spec→tests→build→verify flow. 7 open SPEC deltas
(non-security backlog — a grep-binary-agnostic test fix, an `advisor.md` naming
collision, an oversized pin-history comment, a hand-maintained skip-count
constant, a bundling gap in `prepare_bundle.py`, and an ADR-harvester multi-line
capture) ride forward unresolved into the next cycle.

## [1.14.0] — 2026-06-29

Two milestones round out lanes that shipped partially in earlier releases: the
**global-home / installer** lane gets its missing inverse + safety, and the
**component** pillar closes its remaining gaps and hardens its cross-repo edges.
Installer- and engine-pin-neutral — the ADD engine is byte-identical (ENGINE_MD5
unchanged); all changes live in the installer twins and the component validator.
Backward-compatible throughout.

### Added (installer-polish — complete the global lane)
- **Restore the global home.** `init --from-global-data` (and an `init` that detects a
  matching `<home>/data/<key>`) rehydrates a project's user-data from the global home on
  a fresh clone — the non-destructive inverse of the one-way backup. Fill-gaps by default;
  `--force` writes a `<name>.bak` sidecar before overwriting.
- **`prune-data` orphan cleanup.** A new `prune-data` command removes home snapshots with
  no live registry owner — dry-run by default, `--force` to delete. Both installer twins
  (pip + npm) carry the behavior, byte-for-byte.
- **`update --global` made safe.** An O_EXCL home lock (`<home>/.update.lock`) serializes
  concurrent runs **cross-twin** (a pip-held lock blocks an npm run and vice-versa), and
  every registered path is validated before any write — a relative/traversal entry aborts
  the whole run loud (`unsafe_registry_path`), a directory without `.add/` is dropped.
- **Reconcile roll-up.** Every reconcile now reports a file-level `N restored · M refreshed`
  summary, so a partially-gutted-but-present managed tree's heal is finally visible (it
  healed silently before). Pure observation — copy semantics are unchanged.

### Added (component-polish — close the pillar gaps + harden the edges)
- **`add.py components` reader + validator.** A `components.toml` schema-lint surfaces
  `component_unknown_key` / `component_type_mismatch` / `component_unknown_table` — all
  measure-not-block warnings at `check`.
- **Federation hardening.** `federate pull` path-confines the manifest `source` to a
  sibling-repo allowlist with a fail-closed HARD-STOP (`federation_source_escapes`) before
  any read; a stale leftover contract snapshot that no longer admits a consumer is surfaced
  (`producer_contract_stale`, never red).
- **Registry fill + a worked example.** The component registry round-trips completely, and
  a full worked example threads the component flow end-to-end in the book.

### Changed
- Five version sources bump in lockstep to **1.14.0** (`package.json`, `package-lock.json`
  ×2, `pyproject.toml`, `.claude-plugin/plugin.json`, `add_method.__version__`).

## [1.13.0] — 2026-06-28

Two method milestones make ADD's loop more **self-auditing** and more **honest**:
the observe step now harvests a decision record automatically, and every flow gate
is either mechanically enforced or plainly disclosed where it is not. Plus the npm
release pipeline moves to tokenless **Trusted Publishing**. Backward-compatible
throughout; nothing retro-changes an existing task or milestone record.

### Added (adr-at-observe — a decision record, harvested not hand-written)
- **`### Decisions (ADR)` harvested at the gate.** On `add.py gate PASS`, the engine
  harvests a §7 Architecture-Decision-Record block from §1/§3/§5/§6 — one
  actor-tagged line per decision (`[AI] specify · [human] freeze · [AI] build ·
  [human] verify`), refilled only while the placeholder stands (never hand-edited).
- **`add.py audit` checks the ADR at done.** A done task whose §7 ADR block is unfilled
  is surfaced — presence-only, never a semantic judgment of the decisions themselves.
- **Strategy write-back.** The §6 GATE RECORD is stamped with the git actor + date, and
  the §5 "Strategy actually used" line is harvested into the ADR as the `[AI] build` row.

### Added (flow-honesty — every gate engine-true or honestly disclosed)
- **Two structural holes became real, forceable gates.** A **universal freeze gate**
  (`contract_not_frozen` fires for every task at tests→build, with a recorded
  `--skip-freeze` escape) and a **delta-drain release floor**
  (`release_build_in_flight`, `--force`-able but loud) — the two places the method
  promised enforcement and now delivers it.
- **Four honor-system edges became plain disclosures + measure-not-block lints.**
  `add.py audit` now surfaces `shallow_deep_check`, `risk_unset`, and
  `refute_unrecorded` (presence-only, never blocking); the guides + book state plainly
  that a *missed* security finding is invisible to the engine (a human spot-audit is
  the only backstop under `auto`); reject-code names read honestly
  (`release_tests_red`→`release_build_in_flight`).
- **The earned-green refute-read is now a recorded verdict.** Under `auto`, the §6
  `### Refute-read verdict` block records `EARNED | NOT-EARNED`; the engine measures it
  is filled but never spawns the read — the resolver still does the judging.
- **Stale guidance synced to the shipped engine.** The 5-build "scope gate deferred"
  note is gone (the scope gate enforces today); the auto-PASS precondition list is now
  identical across `run.md`, `6-verify.md`, and the book.

### Added (loose tasks)
- **`/add --todo` flag** (`skill-todo-flag`) — capture/list/close backlog todos.
- **§5 Strategy fed into spawns** (`build-strategy-solutions` · `streams-strategy-pull`)
  — the planned build order + known-problem fixes flow into subagent prompts.
- **`<strategy>` softened** (`strategy-soft-not-hard`) — §5 is the *preferred* plan; the
  builder may self-improve during build and reports the strategy actually used for audit.

### Changed (release infrastructure)
- **npm Trusted Publishing (OIDC).** `publish.yml` drops the stored npm token (no more
  ~90-day rotation), publishes via OIDC (`id-token: write`, Node 24 + npm ≥ 11.5.1),
  and generates provenance automatically (`--provenance` no longer needed). A guard test
  locks the tokenless shape. PyPI already used OIDC.

## [1.12.0] — 2026-06-26

Multi-milestone polish release — the intake/roadmap front grows a real **queue**,
the parallel-front residuals close, and the UDD loop gains a design-intake beat.
Backward-compatible throughout; a single-active project sees no behavior change.

### Added (multi-milestone-intake — a request that is several milestones)
- **`queued` milestone status.** The milestone status enum becomes
  **active · queued · done** (was active · done). A milestone can now exist
  non-active, awaiting promotion — created with `new-milestone --queued` and made
  active with an explicit `activate`. Migration-safe: an old state with no `queued`
  milestones reads byte-identically.
- **Roadmap intake.** `intake.md` now guides decomposing a request that is *several*
  milestones into a roadmap that creates **all N — 1 active + N−1 queued** — instead
  of only the first. Promotion stays human-gated; the whole set is never auto-activated.
- **Queued-backlog resume cue.** `status` surfaces the queued backlog (active
  milestone + what's queued next), so a multi-milestone session resumes cleanly. The
  cue is present-only — byte-identical output when nothing is queued.

### Added (multi-active-polish — close the parallel-front residuals)
- **`waves --merge`** folds the active SET into one cross-milestone DAG and critical
  path (today's `waves` is per-milestone only).
- **`mine --all`** widens the ownership lens past the active milestones — every
  not-done task you own or are assigned, across all milestones plus loose, with an
  email-OR-name match. Plain `mine` (active-only) stays byte-identical.
- **`doctor` value-domain checks.** `doctor` now flags a bad `gate` enum
  (∉ {PASS, RISK-ACCEPTED, HARD-STOP}), a bad `phase`, archived inconsistency, or a
  malformed owner/assignee — beyond the existing referential pointers. It **adds
  findings only**; it never auto-fails or retro-reds grandfathered history.
- **`new-milestone` add-and-focus.** Creating a milestone while one is active now
  **preserves the active SET** (adds the new one and focuses it) instead of replacing
  the set and evicting the others. `--queued` and single-active stay byte-identical.

### Added (udd-design-intake)
- **`design-intake` beat.** The UDD design loop opens with a new front beat that
  interviews the human on four axes — **FIDELITY · CONCEPT · LAYOUT · VISUAL DESIGN**
  — recorded in `DESIGN.md` before review-capture-confirm. Convention-only (the engine
  never renders); identity values (brand color/type) stay human-owned — surfaced to
  decide, never auto-picked.

### Added / Changed (loose tasks since 1.11.0)
- **Descriptive-slug nudge (`new-milestone`).** A milestone slug that is a bare
  version number (`v2`, `v1-1`, `1.2` — matched by `^v?\d+([._-]\d+)*$`) prints an
  advisory `note:` suggesting a short **descriptive** name (e.g. `payment-retries`) and
  **still creates the milestone** — never blocks.
- **Full-ISO `created:` stamp.** MILESTONE.md's `created:` line is the full UTC ISO
  timestamp (`2026-06-26T03:47:28+00:00`); a single `_now()` instant feeds both the
  rendered file and the `state.json` record.
- **`add.py freeze`** — an engine-stamped human-approval write at the §3 contract
  freeze (DRAFT → FROZEN @ vN with a structured actor line). A security finding remains
  an un-forceable HARD-STOP.
- **Queued + await-confirm reminder.** A milestone that is both `queued` and
  `--await-confirm` now surfaces its `milestone-confirm` reminder at resume.
- **Flow docs.** Book ch.02 gains a subsection explaining the milestone-scale
  composition rule — tasks are **listed breadth-first up front** (the DAG), then each
  **specified just-in-time**.

This release bundles **3 closed milestones** (`udd-design-intake`,
`multi-milestone-intake`, `multi-active-polish`) and the loose tasks above since
1.11.0. Every milestone was built end-to-end through ADD's own
spec→tests→build→verify flow.

## [1.11.0] — 2026-06-26

Engine-modularization + audit-hardening release — the 7k-line monolith becomes a
navigable package, the verify/atomicity/coverage gates get five fixes, and the
standalone (milestone-free) lane becomes first-class. **No behavior change** to the
CLI, the flow, or any output: this is an internal architecture + hardening release.

### Changed
- **The engine is now a focused package.** `add-method/tooling/add.py` (7049 → 5640
  lines, −20%) split into **13 `add_engine/*.py` modules** — `constants`, `io_state`,
  `accessors`, `predicates`, `identity`, `guidelines`, `render`, `milestones`,
  `components`, `version`, `release`, `taskdoc`, `autonomy` — behind a stable
  re-export surface (`import add; add.<name>` still resolves, public AND `_`-prefixed,
  so every existing test is untouched). `add.py` stays the runnable **orchestrator
  entry** (the `load_state`/`save_state`/`report_data`/`cmd_*`/`main` spine). Each of
  the 16 extractions was its own CI-green PR, proven verbatim by an AST source-segment
  diff and gated by the full suite (1815 → 1959 green throughout, no test weakened).
- **Two-pin integrity model.** Alongside `ENGINE_MD5` (md5 of `add.py`),
  `ENGINE_PKG_MD5` is a manifest digest over every `add_engine/*.py`; both are literal
  pins (never self-hashed) and are checked byte-identical across the 3-tree mirror
  (canonical · `.add` · `_bundled`). `prepare_bundle` + both installers + the `.add`
  mirror now ship the whole `add_engine/` package.

### Fixed (audit-hardening)
- Five gate/atomicity/coverage fixes: a phase-build guard, hardened save-state
  atomicity, force-preserve self-healing, setup-tests-before-build ordering, and a
  consumer-stale gate. A security finding remains an un-forceable HARD-STOP.

### Added (the standalone / lightweight lane)
- **`add.py todo`** — capture a milestone-free backlog item without scaffolding a task.
- **`loose tasks:` release attribution** — a release now attributes *any* done,
  milestone-free task on its `RELEASES.md` row (not only milestone membership), with a
  separate status cue for releasable loose work.
- **`fast` (task) + `auto` (mode) flag modes** — the standalone lane is first-class:
  a minimal `TASK.fast.md`, freeze-gated under any milestone, with a flag-mode quick
  reference.

This release bundles **2 closed milestones** (`audit-hardening`,
`engine-modularization`) and **27 loose tasks** since 1.10.0.

## [1.10.0] — 2026-06-25

Component-aware major — ADD now models every codebase as a **graph of components**,
each owning a source root, its own green bar, and the contracts it produces or
consumes, so **one milestone can ship a vertical slice across components** in a
monorepo or across repos. Bundles the closed `component-aware-add` major plus the
`docs-site` (the book as a live MkDocs site) and `loop-steering` milestones, and the
ccsk `--rule-file` mode. Every new gate is **opt-in or grandfathered** — a project
that declares no components is byte-identical to 1.9.0.

### Added
- **Component registry (`component-aware-add`)** — declare parts of a multi-part
  codebase in `.add/components.toml` under `[component.<name>]` (a `root` + a
  `green-bar`). A task binds to one with a `component:` header line, which anchors its
  §5 Scope to that component's root. Declared, never inferred; zero components ⇒
  byte-identical to today.
- **Per-component verify** — a bound task is held to ITS component's green-bar at the
  verify gate (the cite-gate refuses `component_green_bar_uncited`), so two tasks in
  one milestone can pass on two different toolchains (e.g. `pytest` and `vitest`). The
  engine still never runs a suite — the AI runs it, the gate checks the right bar was
  cited.
- **Cross-component contracts (`produces:` / `consumes:`)** — declare `[contract.<id>]`
  (producer + consumers). A producer's §3 freeze writes an immutable snapshot at
  `.add/contracts/<id>.json`; a consumer pins its hash; a changed re-freeze flags every
  consumer stale. A missing/malformed snapshot HARD-STOPS — never build against a
  guessed shape.
- **One milestone, full-stack slice** — a `consumes:` task is HELD from entering §3
  (`producer_contract_unfrozen`) until its producer's contract is frozen, so a BE→FE
  vertical slice ships in one milestone, ordered by the frozen contract.
- **Multi-repo federation (`add.py federate pull <id>`)** — a consumer repo declares
  `[federation.<id>]` (a `source` path + optional `pin`) and pulls a byte-for-byte copy
  of a producer repo's published snapshot into its local `.add/contracts/`, where the
  rest of ADD treats mono- and multi-repo identically. Fail-loud: unknown id /
  unreadable source / invalid snapshot / version mismatch each HARD-STOPS and lands
  nothing.
- **Component pillar docs** — a new book chapter `17 · Components`, a skill guide
  (`components.md`), and glossary terms (Component · Cross-component contract ·
  Federation) teach the whole loop.
- **The book as a live site (`docs-site`)** — the AIDD book ships to GitHub Pages as a
  MkDocs-Material site (`mkdocs.yml` + `requirements-docs.txt`, build-time only — the
  published packages stay zero-dependency); `mkdocs build --strict` fails the deploy on
  a broken intra-book link.
- **Rule-file mode for ccsk projects (`--rule-file`)** — when a project keeps its
  workflow rules under `.claude/rules/` (the ccsk convention, detected by a `.ccsk/`
  dir), ADD relocates CLAUDE.md's block to `.claude/rules/add-workflows.md` and leaves a
  single reference bullet, instead of inlining. Triggers three ways (the explicit
  `--rule-file` flag, a `.ccsk/` directory, or a rule file already present),
  **CLAUDE-only**, migrates a prior inline block out (`.bak` on change), idempotent and
  fail-soft. Mirrored across all three installers (engine `add.py`, pip `_installer.py`,
  npm `cli.js`).

### Changed
- **Guided dynamic loop (`loop-steering`)** — `status` and `guide` now STEER into the
  build→verify loop at the loop juncture rather than only reporting it, so an agent is
  pointed at the next loop step instead of having to infer it.

### Compatibility
- Python 3.11+ is required to USE the component pillar (it parses `components.toml` with
  the stdlib `tomllib`); on 3.10 the engine runs unchanged but a declared
  `components.toml` fails loud (`components_malformed`). The published packages remain
  zero-dependency.

## [1.9.0] — 2026-06-24

Lean-pass major — make ADD's own surface (skill · flow · engine) the most-effective
prompt at optimized token cost, *not* token-golf. Bundles four closed milestones:
`skill-effectiveness` (M1), `flow-simplification` (M3), `flow-enforcement` (M4), and
the `fast-lane` sub-milestone. The skill tree routes identically but loads lighter;
the method's three fill-seams are now engine-enforced rather than convention; and a
new opt-in **fast lane** collapses ceremony for small tasks without lowering the trust
floor. Every new gate is opt-in or grandfathered — existing flows are byte-unchanged.

### Added
- **Fast lane (`fast-lane`)** — `add.py new-task <slug> --fast` runs a small task
  through a minimal `TASK.fast.md` (sections {0,1,3,4,5,6}) that still freezes a
  contract, proves a red→green, and reads back cold in a later session. The lane is
  *collapse-never-skip*: a `--fast` task is freeze-gated under ANY milestone (the floor
  fires on `_optin OR fast`). Human-triggered only — the engine never auto-classifies a
  task as "small". New `phases/fast-lane.md` guide + a SKILL.md quick-ref document it.
- **Freeze-before-build gate (`fast-lane`)** — crossing tests→build now refuses
  `contract_not_frozen` when §3 is still DRAFT and the task is opted-in or fast, closing
  the gap where a task could reach `gate=PASS` without an approved, frozen contract.
- **Contract-fill + build-expectations gates (opt-in, `flow-enforcement`)** — under
  `new-milestone --await-confirm`, the engine HOLDS a task whose §3 CONTRACT or §6
  Build-expectations block is still a placeholder, so the method's fill-seams are
  enforced rather than trusted. `await_confirm` is the master switch; without it no key
  is written → grandfathered → byte-unchanged.
- **Gate-record write-back (`flow-enforcement`)** — recording a verify gate now stamps
  the verdict into the §6 GATE RECORD of the TASK.md for ALL tasks (grandfathered
  backfill), so the file itself carries the outcome the Seam audit reads.
- **Confirm-parent gate (opt-in, `flow-simplification`)** — `new-milestone <slug>
  --await-confirm` seeds the milestone *unconfirmed*, so `new-task` is HELD (reject
  `milestone_unconfirmed`) until you show the filled `MILESTONE.md`, get the human's go,
  and run the new `add.py milestone-confirm <slug>`. Closes the gap where the AI would
  detail a task's §0–§5 before the human had agreed the parent milestone. Mirrors
  `init --await-lock` one level down.

### Changed
- **Skill tree 25% lighter (`skill-effectiveness`)** — the on-demand skill guides were
  compacted tree-wide (164,333 → ~123,000 bytes) with zero routing, gate, reject-code,
  threshold, or rule lost; an independent adversarial review confirmed every operative
  element preserved (it flagged 6 dropped nuances → all restored). Same flow an agent
  reads, fewer tokens to load.
- **One home for the worker-spawn model tiers (`spawn-fold`)** — the tier→model mapping
  (mid→sonnet / top→opus) now lives only in `streams.md`; `advisor.md` points at it
  instead of copying. Advisor keeps its own advisory template.

## [1.8.0] — 2026-06-23

Team collaboration: ADD becomes git-native and multi-user, with N
parallel-active milestones, plus a polish pass on the delta-resolution
machinery. Additive and backward-compatible — `add.py` ships a one-way state
migration (single-active → multi-active), and the non-interactive byte stream
for existing single-user flows is preserved. Bundles six closed milestones.

### Added
- **Multi-active milestones (`team-collaboration`)** — work N milestones in
  parallel: `add.py activate` / `deactivate` manage an active working SET,
  `add.py mine` is a my-work lens over owned tasks, the `streams:` block shows a
  per-stream owner, and waves can span all active milestones.
- **Git-native user identity** — `add.py whoami` resolves the actor from git
  config; tasks carry an owner.
- **Ownership & assignment** — `add.py assign` / `unassign` attach a task to an
  owner; ownership renders across status and reports.
- **Git-merge safety** — merge-base enforcement guards a stale worker base; the
  drift vectors a parallel-wave merge can introduce are pinned suite fixtures.
- **Multi-file commit primitive** — `_atomic_write_many` is now true
  all-or-nothing: stage every temp → fsync → rename-aside → rename-all, with
  rollback-on-any-failure restoring prior bytes. `fold`, `release`, and the
  delta seed all route through it, closing the prior mid-rename residual window.
- **`--match <substr>` selector** — `add.py new-task --from-delta` and
  `add.py drop-delta` accept `--match` to target ONE open SPEC delta among
  several; a 0-match or ambiguous match is a named reject. First-open behavior
  is byte-identical when `--match` is absent.
- **`compact --force`** — `add.py compact --force` overrides the project-wide
  `open_spec_deltas_unresolved` block ONLY (never a structural guard) so an
  urgent compaction is not blocked by an UNRELATED open SPEC delta; the bypass
  is warned and recorded as `force_bypassed_spec_deltas`.

### Notes
- One version tag publishes both channels: `@pilotspace/add` (npm) and
  `pilotspace-add` (PyPI). The engine (`add.py`) is mirrored byte-identical
  across all three trees with `ENGINE_MD5` re-pinned.

## [1.7.3] — 2026-06-18

Multi-agent installer reach (`multi-agent-installer`). Additive; no breaking
changes — the non-interactive byte stream is unchanged for existing agents and
the engine (`add.py`) is byte-identical.

### Added
- **Seven new agent profiles in the installer** — `add init` now detects and
  onboards **Cursor, Windsurf, Trae, GitHub Copilot, Cline, Aider, and Gemini
  CLI** (best-effort env detection, overridable in the interactive picker), in
  addition to Claude Code, Codex, and OpenCode. Each gets the context file it
  actually auto-loads: `AGENTS.md` for most, `.clinerules` for Cline. Unknown
  agents still degrade to the generic `AGENTS.md`. Mirrored byte-for-decision
  across both installer twins (`bin/cli.js` + `src/add_method/_installer.py`).
- **Gemini CLI settings wiring (`.gemini/settings.json`)** — because Gemini CLI
  auto-loads `GEMINI.md` (not `AGENTS.md`), the installer now performs a
  fail-soft, idempotent, key-preserving merge of `.gemini/settings.json` so its
  `context.fileName` includes `AGENTS.md` — the installer's first JSON-config
  write. Re-running is a no-op; a malformed or unwritable settings file warns and
  is skipped without aborting the install.

### Changed
- **Onboarding docs name the full agent set** — the README ("Works with your
  agent") and `GETTING-STARTED.md` now list all ten supported agents and how
  each loads ADD; only Claude Code runs the `/add` skill natively, every other
  agent follows the same loop through the phase guides via the CLI.

## [1.7.2] — 2026-06-18

Test-coverage and project-hygiene patch. Additive; no breaking changes.

### Added
- **PTY harness for clack interactive coverage (`installer-smarts-polish`)** — a
  reusable PTY test helper (`tooling/pty_clack.py`) drives the clack
  select/confirm prompts, so the agent-select step and the interactive
  happy-path are exercised under a real pseudo-terminal in CI (previously
  node-syntax-checked and logic-unit-tested only).
- **`SECURITY.md` security policy** — supported-version table, private
  vulnerability reporting via GitHub Security Advisories, and response SLAs;
  shipped in both the npm tarball and the PyPI sdist/wheel.

### Changed
- **Brand tagline** — refreshed to *"One skill. Eight steps. Five disciplines.
  Every feature ships through the loop."* across the README, the npm/PyPI
  package descriptions, and the Claude Code plugin manifest.

## [1.7.1] — 2026-06-18

Installer depth and method quality release: the onboarding installer gains
brand-aware prompts, readiness detection, and intent handoff; SOUL.md is now
seeded on first install and update; scope drafting and build verification gain
new depth guards. All additive; no breaking changes.

### Added
- **Brand-aware guided installer (`installer-smarts`)** — `add init` now prompts
  for the user's brand/project name and detects whether ADD is already present
  (readiness check); defaults to global scope and captures the user's first
  intent, handing it off to the first `/add` session via `.add/.intent`.
- **SOUL.md seeded on install and update (`installer-soul-seed`)** — `add init`
  and `add update` now seed `.add/SOUL.md` from the bundled voice template if it
  does not yet exist, so the voice file is present from the first session without
  waiting for `add.py init`.
- **Build expectations in VERIFY (`verify-expectations`)** — the §6 VERIFY step
  gains a Build-expectations block: the AI pre-declares observable outcomes derived
  from §2 scenarios + §3 contract, and verify confirms them — so a build is checked
  correct, not merely test-green.

### Changed
- **Scope drafting quality guard (`scope-drafting-quality`)** — the scope guide now
  requires the goal to be grounded in current project assets and the milestone map
  before the goal sentence is drafted; a draft well-formedness gate catches
  incomplete MILESTONE.md shapes early.

## [1.7.0] — 2026-06-18

The installer & onboarding release: standing up — or repairing — ADD is now one
guided installer that adapts to the terminal and the agent, and the method's own
build loop gained recorded delta resolution, guided choices at every human gate,
and a milestone-close ship review. All additive; no breaking changes (SemVer MINOR).

### Added
- **Guided, agent-aware, self-healing installer (`installer-experience`)** — `npx
  @pilotspace/add` (and `pilotspace-add`) now runs an interactive `@clack/prompts`
  onramp in a real terminal and degrades to a byte-identical plain-text flow in
  CI / non-TTY (the pip twin matches, on the stdlib). It **detects the active agent**
  (Claude Code · Claude app/cowork · Codex · OpenCode · generic) and writes that
  agent's integration file (`CLAUDE.md` / `AGENTS.md`) as a marker-delimited pointer,
  then prints that agent's exact next step. `init` **and** `update` now **heal/reconcile**
  a partial `.add/` — restoring missing managed assets and refreshing stale ones
  **without touching** `state.json` / `PROJECT.md` / milestones / tasks.
- **Global install (`--global`)** — install the engine + book + skill once into a
  shared ADD home (`ADD_HOME` → `XDG_DATA_HOME/add` → `~/.add`) and reuse it across
  projects; `update --global` refreshes the home and propagates to every registered
  project. The home mirrors the bundled layer; the registry is a flat, atomically
  written `registry.json`, and a corrupt registry fails loud (read-before-write,
  zero-mutation abort).
- **Global data (`--global-data`)** — opt-in (implies `--global`): a one-way snapshot
  of a project's **user-data** under `<home>/data/<key>` keyed by project path, so the
  shared home remembers each opting project. The per-project, git-tracked default is
  byte-unchanged; without the flag, data stays local.
- **Claude Code plugin distribution** — ADD is now installable straight from a
  marketplace, with no npm or pip step: `/plugin marketplace add pilotspace/ADD`
  then `/plugin install add@add-method`. A repo-root `.claude-plugin/marketplace.json`
  lists the `add` plugin, which bundles the skill, the engine, and the AIDD book; on
  first run the skill materializes the engine and book INTO the project
  (`cli.js init --no-skill`) so every agent and a human at the shell get a
  self-contained result identical to an npm/pip install. The skill stays in the plugin
  (no duplicate); boundaries are disclosed in the README and guarded by
  `tooling/test_plugin_manifest.py`.
- **Recorded delta resolution (`delta-resolution`)** — both delta types now resolve
  explicitly: SPEC deltas get a `seed` / `drop` lifecycle and competency deltas
  consolidate into the foundation via **`add.py fold`** (transcription-only, human-
  authorized). `add.py check` stays green only when deltas are well-formed.
- **Guided-choice prompts (`decision-suggestions`)** — every human gate (intake ·
  bundle approval · verify · milestone close · release) renders a recommended pick
  plus 1–3 described alternatives. Presentation-only — the engine is untouched.
- **Milestone-close ship review (`ship-review`)** — closing a milestone now records a
  cross-task ship review (ship-by-domain · per-task evidence · goal-met map) that the
  existing engine gate reads, plus AI-defined release-step hints that feed `release.md`.

### Notes
- The `udd-design-loop` work (the `design.md` UDD loop + the wireframe/HTML-mock
  recipe, described narratively under [1.5.0]) is attributed to this cut in the
  `RELEASES.md` ledger — its first explicit ledger accounting.
- **The engine records; the human ships.** `add.py release` recorded the `RELEASES.md`
  row and this changelog lineage; it never bumps a version source, tags, or publishes.
  The human-gated `git tag v1.7.0` triggers the npm / PyPI publish.

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
