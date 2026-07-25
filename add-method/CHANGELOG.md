# Changelog

All notable changes to the ADD method (`@pilotspace/add` on npm,
`pilotspace-add` on PyPI) are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver.

## [2.5.0] — 2026-07-25

Minor: the **persona** system becomes a coherent artifact. The template guidance names
**four legs** with a quality bar each, gains an optional **Escalation** section, and — for the
first time — ADD **seeds** three planner personas into a new project instead of leaving every
roster empty. The twelve orphaned **preset** persona templates stop shipping. Engine change is
additive: `init` and `migrate` gain a seeding call; nothing else in the loop moves.

### Added

- **Three method-lens planners, seeded at `init` and `migrate`** — `task-planner` (inside one
  frozen contract), `milestone-planner` (ordering tasks into a DAG), `release-planner` (what
  makes a cut). A fresh project now reports a three-persona roster instead of
  `personas: unseeded`, so the persona ladder can *select* or *fold* rather than always *author*.
- **`## Escalation`** — an optional, routable persona section for stop-conditions: the point a
  lens hands the decision up, distinct from an always-do rule and from a guilty-until-proven
  smell. A retrospective can file `persona:<slug> · escalation` and the fold transcribes it.
- **The four legs** — Role (`## Identity`) · Rules (`## Critical Rules`) · Standards
  (`## Default Requirement` + `## Success Metrics`) · Process (`## Abilities` + `## Playbook`),
  each with the bar it must clear. `## Abilities` gains an explicit load contract.
- **A worked architect example** carrying `## Escalation`, alongside the I/O and design examples.

### Changed

- **`SKILL.md` seeds a persona when none fits** — the DIRECTION beat names where the roster comes
  from (`status --all`) and the **select → fold → author** ladder, and states the generic fallback
  that never blocks and never lowers a gate. Both rules previously lived only in an agent file the
  orchestrator does not read.
- **The persona chapter** now describes the load set the surfaces actually read, and states plainly
  that **the engine never edits a persona** — a fold is always a human's or the AI's transcription.
- **Seeding never clobbers.** `_seed_persona_file` mirrors the `_seed_spec_file` survivor idiom:
  an existing (possibly edited) persona is returned untouched; seeding fills gaps, never rewrites.

### Removed

- **The 12 preset persona templates.** They shipped in every npm tarball and pip wheel for months
  after the mechanism that read them was retired — authoritative-looking and dead. `software-architect`
  was promoted to a worked example; the rest are gone. The line that stops a repeat is written into
  the persona contract: ship a persona only if it is a **method lens** (one that reasons about ADD's
  own artifacts), never a **domain lens** (security, data, UX).

### Fixed

- **A pinned CI skip count that no local run could see.** A `@skipUnless` class skips per method, and
  the count was hand-maintained in two places — including the meta-test guarding the pin. Both now
  derive from source.

## [2.4.0] — 2026-07-24

Minor: the **strategy-intake** milestone closes — a fitting **persona** becomes ADD's
adaptive project-management brain — plus the follow-on cleanup that completes the 2.3.0
**scenarios fold** and adds a CI sweep of every shipped surface. The method changes are all
skill/agent-surface prose with **zero `add.py` engine change** (the engine records the
`## Strategy` slot and the gate, never drives the loop or gates on the strategy); this
release also carries one **concurrency fix** to the installer's lock (see *Fixed*).

### Persona-as-PM strategy loop — `strategy.md` (new guide)
- **DISCUSS → OPTIMIZE → CONVERGE** — a new `strategy.md` guide drives a persona-framed
  loop that fills a milestone's `## Strategy` slot with a sequenced, optimized task DAG,
  converging on the *existing* six-dimension confidence self-score (no new bar invented).
- **`add-advisor` refute at CONVERGE** — a high-uncertainty milestone spawns the advisor
  in refute mode to break the strategy before it's recorded; advisory (it cannot block),
  reusing the existing refute mode. The advisor's `direction` beat now names a milestone
  strategy as a refutable artifact alongside a task bundle.
- **risk-proportional depth ladder** — one legible rule: micro/`--tiny` skips the loop at
  zero added per-turn cost · multi-task low-uncertainty runs the loop · high-uncertainty
  adds the refute. It is the skill's judgment, never an engine gate; strategy stays SOFT
  and security stays HARD-STOP.
- **persona-at-intake** — `intake.md` now loads the **fitting persona** before it sizes a
  request (match-else-seed, advisory), so the persona that owns the intake report also
  shapes the sizing.

### Fold completion + shipped-surface sweep
- the **scenarios fold** finishes — four remaining shipped residuals of the §2→§4 retirement
  are fixed, each defect class pinned by a new guard.
- a **shipped-surface** CI sweep derives the published file set from the packaging manifests
  and fails on any dead chapter/section reference across every shipped surface.
- CI/deps: `actions/setup-python` 6→7, `actions/setup-node` 6→7, `@clack/prompts` 1.6.0→1.7.0.

### Fixed
- **stale-lock reclaim could unlink a LIVE lock** (mutual-exclusion violation). The reclaim
  path gated its unlink on inode identity alone, assuming a fresh replacement lock always
  gets a new inode. Linux (ext4/tmpfs) **reuses freed inode numbers**, so a delayed racer
  could match the crashed generation's inode against a *live* holder's replacement lock and
  delete it — putting two processes inside the critical section at once. Reclaim now requires
  the file to be **both** the observed inode **and** still stale, so a live or
  heartbeat-refreshed lock is never mistaken for a dead one. Fixed at all four reclaim sites
  in `_installer.py` and mirrored into the `bin/cli.js` npm twin, which carried the identical
  guard. `O_EXCL`/`wx` remains the sole mutual-exclusion primitive and a genuinely crashed
  lock still self-heals. Surfaced as an intermittent `peak=2` on the Linux CI runner only.

## [2.3.0] — 2026-07-24

Minor: three waves — a **signal graph** view over the task DAG, the **§2
Scenarios fold** into §4, and a **call-lean pass** that kills the two measured
WM1 freeze/scope call sinks. Engine changes are additive; templates migrate
in place (no manual task-file edits).

### Signal graph — one addressable node for every note/todo/delta
- **unified signal model** — note, todo, and spec-delta collapse into ONE
  addressable `signal` node (status + edges), projected as a VIEW, not a new
  store; `_signals` reader.
- **`graph --signals`** — opt-in overlay renders signals on the task DAG;
  **exit-criteria** render as `ec_` *delivered-by* nodes (a milestone's own
  criteria appear as ✓/○ nodes wired to the tasks that meet them).
- **`graph --html`** — emits a self-rendering HTML page to tmp (Mermaid inline,
  no external host).
- **atomicity signal** — the freeze SEEDS a persistent atomicity signal into the
  task's todos instead of an ephemeral print, so the nudge survives the session.

### §2 Scenarios folded into §4 — one place for cases
- the standalone **§2 SCENARIOS** section is **retired in place**: pass/fail cases
  now live with the tests in **§4 · TESTS & SCENARIOS** (primary-case rigor). The
  §3–§7 numbers are unchanged so the freeze parser and every §-reference keep
  working — the §1→§3 jump is intentional.
- **PROJECT.md** gains a managed `ADD:SPECS` pointer block (init/migrate inject it
  from the 5-DD spec set); foundation references reconciled to the `.add/specs/`
  model; the generated **CLAUDE.md** block finalized in the generator.
- the Step-2 Scenarios book chapter folds into Step-4; `add-flow.png` retired.

### Call-lean pass — the WM1 freeze/scope sinks die at the source
- **freeze-flag slot** — `PLAN.md.tmpl` §3 carries a drafted-blank *Least-sure
  flag* slot; the first freeze no longer fails `unflagged_freeze` (0/6 reps in the
  re-measure, was 3/3). The unfilled part-menu placeholder still never satisfies
  the gate — the floor holds.
- **scope-first freeze** — a §3 Scope that resolves to zero cover is now refused
  `scope_unresolved` AT the freeze with a paste-ready fix, instead of surfacing
  later as `scope_violation` → re-cross → re-gate. UNDECLARED stays grandfathered;
  greenfield `[MISSING]` tokens still freeze; a `.add/tasks/` token gets a
  task-dir teach note.
- **scope-walk prunes** — `.venv` · `venv` · `.tox` · `.mypy_cache` · `.ruff_cache`
  · `.eggs` and any `*.egg-info` dir are pruned from the scope walk, so an
  in-workspace virtualenv or `pip install -e .` metadata is never read as an
  out-of-scope write. `dist`/`build` stay watched (can be a real write-set). The
  untouched-Scope-default warning now self-explains (a note, not a blocker; clears
  only by editing the Scope line — re-cross does not clear it).
- **honest fidelity meter** — the artifact-blind LLM `spec_fidelity` metric is
  replaced by a deterministic `requirement_coverage` (frozen per-WM checklists +
  probes, no LLM in the metric path); `oracle_pass_rate` promoted to the headline;
  the judge demoted to an advisory `code_quality_annotation`.
- **§3 Build-strategy relabel** — *Scope (may touch)* is the HARD scope-lock; the
  rest (Strategy · Regression floor · Persona) is SOFT/optional. `MILESTONE.md`
  gains a drafted-blank `## Strategy` slot.

Retired (no CLI/install surface change): the standalone **§2 SCENARIOS** section
(folded into §4) · the **ccsk / rule-file** mode · `add-flow.png`.

Pinned by `test_release_2_3_0.py`. `ENGINE_MD5` re-aimed to `60eef504…`
(scope refusal + walk prunes); the four tooling twins stay byte-identical;
full tooling suite green (2277 tests).

## [2.2.0] — 2026-07-22

Minor: the Direction beat gains a **fable reasoning discipline** — a prompt-only
pass that makes the agent derive from the task in front of it instead of a fluent
template, distilled from the fable-thinking protocol. No engine change.

- **fable reasoning discipline** — `phases/direction.md` opens with the lens for
  the whole bundle: **Fluent ≠ true** (a draft's polish tracks its token count,
  not its evidence), the **Five Moves** (FRAME · GROUND · REASON · ATTACK ·
  DELIVER) each mapped to the beat that already applies it, and two pre-answer
  checks the fluent draft skips — the **Floor** (restate the Goal in the human's
  world, then sweep the Leftovers: every supplied invariant and the BARE runtime)
  and the **constraint loop** (expand → verify mechanically → repair the §3 tag
  census · §5 scope tokens · §4 `covers:` keys · REDS refs before the freeze).
- **claim grammar** — `add-advisor`'s §6 Return tags every factual assertion by
  how it's known: `[OBSERVED]` (checked live this session) · `[DERIVED]` ·
  `[PRIOR]` (memory, may be stale) · `[ASSUMED]`; a bare claim reads as OBSERVED,
  so a guess never rides in unmarked. **GROUND** makes the same rule structural:
  a recalled file/flag/symbol is `[PRIOR]` until re-confirmed against the live tree.
- Prompt-only, propagated byte-identical across the three synced skill trees;
  `add.py` == ENGINE_MD5 unchanged. Pinned by `test_fable_floor.py`.

## [2.1.0] — 2026-07-22

Minor: the two-agent roster matures and the persona author learns from real
corpora; TDD flexes for non-coding tasks; every honest verify→build round
becomes engine-visible; the dogfood foundation completes its 2.0 migration.

- **two-agent roster** — `add` retires; **add-worker** runs every EXECUTION
  beat (direction · build · verify · persona) and **add-advisor** is the
  second mind serving EVERY beat (propose-plan · advise-midflight · refute)
  with a per-beat calibration map. The worker gains a mid-flight **support
  fan-out** for medium/large builds: non-overlapping §3-Scope slices,
  worktree isolation per support worker, the lead serializes git and re-runs
  the FULL suite on every return; the quality floor multiplies, never dilutes.
- **persona-author skill** — the static `.add/personas/_template.md` retires
  for a `persona-author` skill (contract · patterns · seeding references +
  two worked examples). Patterns grow 9 → 11 from a deep diagnosis of 13
  sample subagents and the 256-file teacher corpus: NEW *numbers-you'd-defend*
  (a named budget beats an adjective; fake precision is worse than none) and
  *per-flow stance* (what a lens LEADS with at build vs REFUSES at verify —
  the verify stance carries a default NEEDS-WORK verdict); seeding gains
  mine-the-gold / refuse-the-rot source guidance. All 6 live roster personas
  folded to patterns-v11.
- **flexible TDD** — §4 supports failing-first **acceptance checks** for
  non-coding kinds (docs · release · infra): verifiable pass/fail evidence,
  red before the artifact exists, green after — the red→green discipline
  holds; only the must-be-executable-code requirement is lifted. Guide,
  template, and book reframe; NO engine change (the kernel was already
  tolerant); 21 non-coding prose-guard tests retired dogfooding the policy.
- **round-visible runs** — every verify→build return trip is a recorded
  **round**: `add.py phase build [--note "finding"]` and every non-exhausted
  heal return increment an uncapped, observational `tasks[slug].rounds`
  (count + timestamped history, notes verbatim); `status` names `round N`;
  the route trace carries `"rounds"` beside `"heals"`. Heal stays the
  cheat-classed, capped subset; rounds are the honest whole. `--note` off
  the build target refuses (`phase_note_build_only`).
- **foundation-split** — the dogfood board completes the 1.x→2.0 foundation
  migration this package's own `migrate` verb leaves to judgment: PROJECT.md
  322 → 63 lines (engine-read lines byte-identical), the pre-2.0 standing
  picture folded into the five `.add/specs/` living specs with a per-bullet
  fold ledger — the worked example external 2.0 upgraders can follow.
- **SKILL.md command cookbook** — the skill router carries the common
  call recipes so agents skip the `-h` round-trip; README copy tightened
  (benefit-led highlights, honest tradeoffs, no dollar figures).

Retired (no CLI/install surface change): the `add` roster agent (superseded
by add-worker + add-advisor) and the static persona template (superseded by
the persona-author skill; `init` now creates an empty personas dir and the
hints point at the skill).

## [2.0.0] — 2026-07-18

Major: ADD 2.0 — a skill-led method on a thin state kernel. The skill drives
the loop; `add.py` records state and guards the seams; **personas carry the
playbooks** the platform pillars used to hard-code.

- **engine-kernel-trim** — the verb surface collapses 54 → 31: the platform
  pillars die as engine code (streams/waves/DAG orchestration · components/
  federation · release/graduation engines · gate-audit machinery · fold/compact
  consolidation · team verbs · the SPEC-delta trio · doctor/worktree-prep) and
  their workflows live on as seed-persona playbooks. `add.py` shrinks
  9,558 → 6,596 lines; the phase guides fold 17 → 12.
- **PLAN.md** — the task doc is `PLAN.md` everywhere (was TASK.md; the
  template is `PLAN.md.tmpl`), and the new one-shot **`add.py migrate`**
  converts a 1.x board: renames live + archived task docs, seeds any missing
  living spec, idempotent, refuses `migrate_conflict` before touching anything.
- **5-DD living specs** — `.add/specs/` (domain · system · experience ·
  quality · method) with **`add.py delta-append`** as the in-flight lesson
  channel; the fold ceremony is gone.
- **book-stops-shipping** — the AIDD book publishes at
  https://pilotspace.github.io/ADD/ and never installs; engine chapter
  pointers deep-link the site (`BOOK_URL`), installers drop the docs tree,
  and a legacy `.add/docs/` from 1.x is user-space (never swept).
- **phase-collapse-3** — the lifecycle is direction · build · verify: ONE
  freeze approval crosses the whole Direction bundle; the 3-call walk
  (`new-task` · `freeze --by --cross` · `gate PASS`) is the whole ceremony.
- **persona routes + route scoreboard (GEPA)** — the persona proposes the
  lane (`route:` header, ratified at freeze); every recorded gate appends a
  route-outcome trace, and `add.py deltas` rolls the traces up per lane —
  the evidence the PM persona reflects on GEPA-style, proposing route-rule
  deltas the human folds into the persona file.

Breaking (the 2.0 line): removed verbs refuse as unknown commands; task docs
must be `PLAN.md` (`add.py migrate` is the paved path); the book no longer
lands in `.add/docs/`; `TASK.fast.md.tmpl` is gone (one template, every lane).

## [1.18.0] — 2026-07-14

Minor: eleven milestones, expanded from the original July-7 two-milestone cut
(unpublished — the 1.17.0-amend precedent) to attribute everything merged
since. Headline: **six-phase-loop** — the lifecycle merges 8 phases into 6
(specify absorbs scenarios; verify absorbs observe), phase guides disclose
into the roster's bundle subagents, and the tick into build re-renders the
frozen spec. Also: **expectations-first** (plan phase; ONE freeze),
**plan-legibility**, **quality-floors**, **risk-proportional-ceremony**,
**three-phase-flow**, **add-bench** + **add-bench-v2** (the trust benchmark
that measured it all), **add-lean-loop**, plus the original
**build-strategy-facets** and **delta-drain**. The ceremony-to-effort and
call-floor features (compound ticks · scope echo · kickoff truth · skill
orient split) ship here too; their milestones remain open on measurement
criteria. Folded in after the July-14 cut: the **engine-minimalism /
context-cost thread** — a progressive foundation read, a lean default `status`,
and one fewer ceremony turn per crossing — measured by **token-anatomy** and
**honest-fidelity-meter**. No gate weakened; a security finding still HARD-STOPs.

### Changed (the headline)
- **The loop is six phases**: `specify → plan → tests → build → verify → done`.
  Scenarios live inside SPECIFY (§2 unchanged as a section); the observe duties
  live inside VERIFY (§7 unchanged). Legacy phase tokens (`ground`, `contract`,
  `scenarios`, `observe`) normalize on read — in-flight boards migrate loud and
  safe; the skip grammar is retired (nothing is skippable; vestigial `skips:`
  headers are noted at gate, never fatal) (six-phase-loop).
- **Guides re-cut to 6 files**; delegating spawns a bundle agent that loads its
  own phase guides — the orchestrator reads only SKILL.md; the inline lane stays
  first-class (six-phase-loop).
- The specification bundle approves at ONE freeze on the plan phase
  (expectations-first); the freeze report renders the BUILD PLAN block and the
  resolved scope echo (plan-legibility, ceremony-to-effort).

### Added
- **Build-entry spec echo** — the tests→build tick prints the §1 Must/Reject
  rules + the frozen §3 contract head, so the builder starts from the spec on
  the screen, not from memory; fail-open, both entry paths (six-phase-loop).
- **Per-phase persona presets** — teacher-grade expert stances per owned phase
  in the roster agents; project-persona routing stays first; a preset never
  lowers a gate (six-phase-loop).
- **Compound ticks** — `freeze --cross` lands in tests; `gate` records from
  build (one call fewer per crossing); init prints the resume pointer
  (call-floor).
- **Quality floors** — spec-dialect warn at build entry · fast-lane
  `Boundary:` freeze-refusal · §6 DIALECT check line (quality-floors).
- **The trust benchmark** — arms × workload-milestones harness with
  deterministic oracles, tamper/regression meters, and the
  cost-per-trusted-feature verdict (add-bench, add-bench-v2).
- **AI-plan-verify gate + phase bundles** (three-phase-flow) · message-layer
  error ergonomics, −24% turns at equal rigor (risk-proportional-ceremony).

### Added (from the original July-7 cut)
- **Faceted §5 build strategy** — four domain-generic facet lines drafted at
  the tests→build cross: `Approach` (domain strategy) · `Data strategy` ·
  `Pattern` · `Optimization stance`; the fast lane collapses them to one line
  (build-strategy-facets).
- **per-facet ADR harvest** — each §5 facet lands in §7 Decisions (ADR) as its
  own actor-tagged line at done (build-strategy-facets).
- **compact-foundation `--propose`** — a read-only preview of the compaction a
  run would take; inspect before any byte moves (delta-drain).
- **`verify` flow value for personas** — personas route to the verify surface
  directly; the streams.md worker-contract `<persona>` block names the flow
  preference (delta-drain).
- **persona roster line** — `status`/`check` render an engine-built roster with
  flows, never hand-maintained (delta-drain).

### Changed
- §5 build strategy guidance, phase guides, and the TASK.md/TASK.fast.md
  templates teach and carry the facet block (build-strategy-facets).

### Fixed
- **Installer data loss** — `.claude/agents` is a shared namespace: init/update
  now land only ADD's own roster files per-file (atomic), removal is
  explicit-tombstone-only — the user's own subagents survive every install and
  update (loose task installer-shared-namespace-guard, PR #151).

### Added (engine-minimalism — the context-cost thread)
- **Progressive foundation read** — `status --foundation` prints a MAP (the preamble +
  `invariants:` + Domain + Spec in full; every other section collapsed to its heading +
  an on-demand `add.py status --foundation "<section>"` pull), so the cross-milestone
  foundation that is re-read every turn is a slice, not the whole file; a named section
  fleshes out on demand and `--all` restores the whole foundation (foundation-slice, −59%
  on a 55KB foundation). Invariants never collapse — the contracts that bind every task
  always survive the map.
- **Lean default `status`** — bare `status` prints the resume essentials; five heavy
  blocks gate behind `--all`; `status --brief` is the mid-task resume; `status --section
  <n>` reads one TASK.md §body instead of the whole growing file (engine-minimalism).
- **`--help` diet** — the top-level help drops from 121 lines to 19 (engine-minimalism).

### Changed (engine-minimalism)
- **One fewer ceremony turn per crossing** — a green build steers straight to `gate PASS`;
  the redundant pre-gate `advance` is folded away (ceremony-turn-cut / advance-fold).
- **Leaner per-turn engine output** — bare `status` stops restating the 'now' card in its
  resume block; `new-task` teaches the full annotated recipe once per project, compact
  thereafter; the skill re-orients from each verb's `next:` footer instead of re-running
  `status` (engine-output-trim, status-brief-adoption, trust-the-footer).

### Added (measurement — not shipped in the package)
- **Token anatomy** attributes a benchmark run's cache-read cost by category; a
  deterministic **`requirement_coverage`** meter replaces the artifact-blind spec-fidelity
  judge (now a source-aware, non-gating annotation); scoring is hermetic per boot
  (token-anatomy, honest-fidelity-meter). Dev harness under `benchmark/` — not in the
  npm/PyPI tarball.

### Disclosed waivers (non-security, signed)
- `reclaim-ticket-race` — lock-reclaim TOCTOU flake; owner Tin Dang, expires 2026-08-04.
- `js-reclaim-lock-heartbeat` — JS lock-heartbeat race; owner Tin Dang, expires 2026-08-04.

## [1.17.0] — 2026-07-06

Minor: four milestones — **method-ergonomics** (every recurring gate rule becomes
a form the engine presents at that moment, cutting per-task ceremony without
moving the safety floor), **persona-domain-fit** (a new milestone or task
whose domain no existing persona covers gets a concrete draft-one nudge),
**dynamic-personas** (a drafted persona carries `flow:` routing to its agent
surface, at teacher-grade depth and load cost), and **self-improving-loop**
(the observe→deltas→fold→compact loop surfaces its own accumulation instead of
rotting silently) — plus twelve loose tasks. New engine verbs are additive; no
gate weakened, nothing removed or renamed.

### Added
- **`add.py gate --explain [slug]`** — a read-only dry-run of the verify gate:
  prints phase · autonomy · risk · sensitivity · advisor lines and one
  `path: AUTO | HUMAN | RELAX | REFUSED (reason)` verdict, always ending with
  the security floor (a security finding is always HARD-STOP). Writes nothing.
- **`add.py advance --to <phase>`** — fast-forwards a drafted bundle's
  bookkeeping crossings in one call, stopping hard at `tests` (the freeze gate,
  tamper tripwire and scope snapshot are never skipped).
- **`add.py re-cross`** — records a human-approved post-freeze re-cross
  (`--by` required): re-runs the full tests→build gate stack to legally
  re-snapshot after an approved test addition, never bypassing the freeze.
- **`add.py worktree-prep <slug>`** — mechanizes the spawn-isolation recipe:
  cuts a git worktree at HEAD, materializes the gitignored `.add/tooling` +
  `.add/docs` a tracked-only checkout lacks, and echoes the fork base for the
  WAVE.md ledger. Workspace-only; state.json is never written.
- **Verify-record rollup** — `add.py audit` folds its four §6 shape lints into
  one `verify_record_incomplete` line per task.
- **Delta verbs reach archived tasks** — `drop-delta` / `carry-delta` /
  `reopen-delta` now operate on a light-archived task's on-disk TASK.md
  (explicit slug only, `(archived — on-disk record)` marker, state untouched).
- **Batched intake + batched gates** — intake.md and report-template.md
  document one report + one confirm for N same-gate items (per-item
  lowest-confidence flags; any item holdable by name). Presentation only.
- **Domain test forms** — 4-tests.md states that a test is any
  machine-checkable assertion (metric threshold · reconciliation query ·
  plan-diff · rendered-screen diff), red-first holding for each.
- **Persona domain-fit nudge** — a milestone/task whose domain no existing
  persona covers is nudged toward drafting a fitting one; TASK templates now
  require a named persona and carry a domain-strategy hint.
- **Fast-lane ground anchor** — the `--fast` template's §0 gains the
  `Ground SHA:` drift anchor, so a fast task can clear the stale-line-ref WARN.
- **Persona `flow:` routing** — a persona's `flow:` frontmatter (design | build
  | advisor) is now read, not just written: the 4 flow-routed roster agents,
  `design.md`'s evidence checklist, and `advisor.md`'s spawn block all select
  a persona flow-first; add-persona drafts the current schema (`flow:` /
  `source:` / `## Abilities`) and returns `flow` in its verdict.
- **Persona load performance** — every seeded persona gains `## Abilities`
  (orient-command-led) and `## Anti-patterns`; selection is frontmatter-first
  (name · vibe · flow, then one body — not the whole roster); add-persona
  routes the teacher library by division directory, never its catalog README.
- **Fold grows the current persona schema** — `add.py fold` routes a
  `persona:<slug> · anti-pattern|ability` lesson into those sections too (was
  limited to `critical-rule`/`success-metric`), so the persona learning loop
  can grow the sections that shape agent behavior.
- **Loop-surfacing status cues** — `add.py status` names the carried
  spec-delta backlog and the un-compacted foundation tail (last-rolled vs.
  current `foundation-version`) once either passes a noticeable size;
  `release-report` lists the carried total. Additive; a clean project's
  output is unchanged.
- **`skill/add/self-improve.md`** — one map of how ADD improves itself: the
  four self-improving artifacts (foundation · personas · `SOUL.md` · next
  scope), routed across the 5 domains, fed by all 8 steps.

### Changed
- **Sequential+auto is the default run mode** — parallel streams stay a
  deliberate, persisted opt-in.
- **Leaner TASK.md template** — instructional comment bloat trimmed 16%
  (comments −27%); every machine-parsed marker untouched.
- **Leaner guides** — run.md's specification-bundle section is a pointer at
  its one home (`phases/3-contract.md`); the ⚠ flag grammar now lives in
  exactly one guide.
- **Waiver field census is case-insensitive** — `audit` recognizes
  `Owner:/Ticket:/Expires:` as written by the signed records; the
  missing-field refusal is unchanged.

### Fixed
- The CI-observed reclaim-ticket race in `_update_lock` (+ its JS/npm
  heartbeat twin), orphaned reclaim-ticket sweep, the prune-data/update-global
  lock race, the ADR harvester's multi-line field capture, and the
  strip-scaffold backtick-comment over-strip.

## [1.16.1] — 2026-07-04

Patch: two loose, additive persona-loop improvements found while dogfooding
ADD in a real consumer project. No engine validation changed; no CLI
behavior changed; nothing removed or renamed.

### Changed
- **Persona seed nudge is project-scoped.** The setup/status/check/new-milestone
  hint to draft a project's missing personas now names the project by scope
  instead of a generic reminder, so it fires once per genuinely-uncovered
  project rather than repeating a one-size-fits-all message.
- **Persona schema template recommends `flow:` + `## Abilities`.** A seeded
  persona can now state which ADD apply-surface (design/build/advisor) loads
  it and what it can concretely do, distinct from `## Critical Rules`
  (always-enforced constraints) and the optional `## Playbook`. Recommended,
  not engine-checked — existing personas anywhere stay schema-conformant
  with no forced re-seed.

## [1.16.0] — 2026-07-03

Closes the **install-update-hardening** milestone: `add.py init`/`update` (both
`--global` and project-scope, pip + npm twins) now survive a crash or a
concurrent run without leaving a half-written `.add/` tree or a wedged lock.
Backward-compatible; nothing removed or renamed on the CLI surface.

### Added (a lock where none existed)
- **Project-scope install/update lock.** Two concurrent `install`/`update` runs
  against the same project-scope destination can no longer interleave writes —
  one waits or fails cleanly (`install_in_progress`). Independent of the
  existing global lock — separate file, separate default threshold, no shared
  code — but the same identity-verified reclaim discipline (below).
- **`--lock-timeout <seconds>`, opt-in** (`init` and `update`, both twins).
  Unset keeps today's behavior — fail immediately if the lock is held; set it
  to poll instead, so CI can wait out a held lock. The staleness threshold
  itself (when a held lock counts as abandoned, not merely held) stays an
  env-var (`ADD_LOCK_STALE_SECONDS`), not a routine flag.

### Fixed (crash-safety, both twins)
- **Managed-tree reconcile** (`_clean_replace` / `cleanReplaceTree`) and the
  **user-data persist/restore path** (`_persist_data` / `_restore_data`) both
  move to a stage-then-commit idiom — self-heal a leftover scratch sibling,
  stage into a fresh uniquely-named one, commit via same-parent rename, sweep
  the old backup. A killed process mid-copy or mid-write no longer leaves a
  half-written tree; the next run heals it automatically.
- **Global and project-scope lock reclaim, made identity-verified.** A stale
  lock used to be reclaimed by unlinking it by *path* — an independent verify
  pass found this let two racers both believe they held it at once. Reclaim
  now re-stats the lock immediately before unlinking and proceeds only on an
  inode match; a per-generation ticket file gates entry to the reclaim itself,
  so a losing racer never touches the real lock file at all. Confirmed
  against 1167+ combined adversarial concurrent attempts, 0 anomalies, across
  both locks.

### Known limitation
- The reclaim fix's identity check compares inode numbers — sound only if the
  filesystem never reuses one inside the brief re-stat-to-unlink window.
  Confirmed on macOS/APFS this cycle; Linux/Windows were not independently
  re-verified. Disclosed, not blocking — flagged for the next verify pass.

### Changed
- Five version sources bump in lockstep to **1.16.0** (`package.json`,
  `package-lock.json` ×2, `pyproject.toml`, `.claude-plugin/plugin.json`,
  `add_method.__version__`).

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

### Changed (loop-readability — human-scannable output across every phase)
- **Report shape, audited and tightened.** `report-template.md`'s ARC + 6-block
  shape was checked against its own stated rules (summary-first, one decision,
  guided-choice) across all 8 phase guides' gate-reporting cues; 2 guides
  (`0-setup.md`'s baseline-lock sentence, `3-contract.md`'s freeze-gate
  sentence) had drifted and were tightened to name SHAPE ahead of the APPROVE
  guided choice.
- **SKILL.md's compact pipeline sentence now names the decision banner**
  ("rendered first, above everything") ahead of the ARC, matching
  `report-template.md`'s actual render order — closing a gap the shape audit
  surfaced.
- **`MILESTONE.md.tmpl` gains a UI/UX Scope hint** — the axes to name
  precisely for a UI feature (information architecture, interaction pattern,
  visual hierarchy, design tokens, component states, accessibility floor,
  responsive breakpoints, user journey), pointing at `design.md` — with
  adoption pointers wired into `1-specify.md` and `scope.md` so drafters
  actually reach it. The seed this milestone was created to dogfood.

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

This release bundles **11 closed milestones** (`seams`, `context-search`,
`drift-guard`, `artifact-graph`, `ground-trust`, `traceability-ids`,
`persona-teacher-bundle`, `persona-learning-loop`, `advisor-gated-autonomy`,
`portable-roster`, `loop-readability`) and 13 loose tasks since 1.14.0. Every
milestone was built end-to-end through ADD's own spec→tests→build→verify flow.
25 open SPEC deltas (non-security backlog spanning the newly-grounded
install-update-hardening tasks, report-shape-scan-audit/skill-banner-cue
follow-ups, and pre-existing items — full list: `add.py deltas`) ride forward
unresolved into the next cycle.

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
