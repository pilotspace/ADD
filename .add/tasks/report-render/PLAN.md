# TASK: add.py report: render the nested what-happened digest

slug: report-render · created: 2026-06-02 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- touches add.py (the engine the human's escape hatch depends on) + freezes the render shape both v9 tasks share -> human reviews the diff at verify -->

> One-approval front (v7): the AI drafts Spec + Scenarios + Contract + Tests as ONE
> bundle; the human gives a single approval AT the frozen contract (§3, the seam).
> Below is that draft. Nothing builds until you approve §3.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

`add.py report [milestone]` renders ONE read-only digest of what happened in a milestone:
a header, one block per member task, and a roll-up footer — synthesizing data ADD already
records (state.json + each TASK.md + MILESTONE.md) so a person never reads the four files by hand.

Must:
  - `add.py report` with NO arg renders the **active milestone**; `add.py report <v>` renders
    the named milestone
  - the render is a DASHBOARD (frozen v2) with three rule-separated sections, in order:
    1. **header** — a `═`×64 banner; `<slug> · <title>` with a status badge `● <status>`; then
       `goal` (wrapped to the banner width); then a `tasks` progress bar (`▰▱`×10) + `D/T done`
       and a gate tally `g ✓  r ⚠  h ✗` (PASS / RISK-ACCEPTED / HARD-STOP counts)
    2. **TASKS** section — one block per member task (state order): `▸ <slug>` + right-side
       `gate: <badge> <gate>`; a self-labeled **phase track**
       `spec● scen● contract● tests◉ build○ verify○ observe○ done○` (● passed · ◉ current ·
       ○ not reached — from the task's phase index); then `tests <n>  ·  observe: <delta|(unknown)>`
    3. **ROLLUP** section — `exit criteria` bar (`▰▱`×10) + `x/y met`; `waivers` (each
       RISK-ACCEPTED owner·ticket·expiry, else `(none)`); `deltas` (every competency delta
       **with its status tag** `open|folded|rejected`, verbatim — NOT open-only, so learnings
       survive the fold-at-close, else `(none)`); a closing `═`×64 banner
  - **visual vocabulary (frozen v2)** — deterministic so RETRO.md is byte-reproducible:
    badges `●` status / `◉` current-phase / `●` passed / `○` not-reached;
    gate badges `✓ PASS · ⚠ RISK-ACCEPTED · ✗ HARD-STOP · · none`;
    bars are 10 cells, filled = `round(ratio×10)` `▰`, remainder `▱`; a `0/0` ratio → all-empty
    bar with `0/0` label (no divide-by-zero); banner/rule width = 64
  - the render is produced by a single pure function `render_report(root, state, mslug) -> str`
    (so v9's retro-artifact task can write the SAME text to RETRO.md) — `cmd_report` only prints it
  - **read-only**: `report` writes nothing to disk and never mutates state.json
  - **fail-closed on prose**: a missing/placeholder/unparseable prose field (observe delta, a
    task with no `tests/` dir) renders the literal `(unknown)` — never a silent omission or a crash
  - **milestone exists in state, MILESTONE.md missing**: still prints — title/goal render `(unknown)`,
    exit criteria render `0/0` (the milestone exists; only its doc is gone — do not reject)
  - **zero-task milestone**: `tasks 0/0 done`, no task blocks, `exit criteria 0/0 met`, no divide-by-zero
Reject:
  - milestone does not exist (no key in state.milestones) -> "unknown_milestone"  (exit 1, nothing on stdout)
  - no arg AND no active milestone is set -> "no_active_milestone"  (exit 1)
After:
  - stdout holds the nested digest; exit 0; state.json byte-identical to before the call
  - the same `render_report` output is reusable verbatim by retro-artifact (the frozen seam)
Assumptions (confirmed at freeze 2026-06-02):
  - [x] "tests-changed" is rendered as the **count of `def test_` functions** under the task's
        `tests/` dir (honest, countable) — not a git diff of tests (no VCS coupling in the engine)
  - [x] the observe one-liner is the §7 "Spec delta for the next loop:" line; if it is still the
        template placeholder (`<...>`) or absent, it renders `(unknown)`
  - [x] competency deltas are surfaced **verbatim WITH their status tag** (open|folded|rejected),
        NOT open-only — so learnings survive the fold-at-close (`open`→`folded`) and RETRO.md stays
        meaningful; `report` never grades/folds them (engine renders structure; human owns judgement — v2 boundary)
  - [x] exit-criteria coverage counts `- [x]` vs `- [ ]` lines inside MILESTONE.md's
        "Exit criteria" section only (not scope/other checkboxes)
  - [x] per-task block shows the task's CURRENT phase+gate (state.json keeps no per-phase log) — not a 7-row history

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: active milestone, mid-flight
  Given a milestone with 2 member tasks (one done/PASS with tests, one at 'specify' with none)
  When I run `add.py report` with no arg
  Then stdout shows the header (tasks 1/2 done · 1 PASS), a block per task with phase·gate·tests·observe
  And the footer shows exit-criteria coverage, waivers, and deltas with their status tags
  And state.json is byte-identical to before the call

Scenario: zero-task milestone (e.g. live v3 at 0/0)
  Given a milestone that exists in state with no member tasks
  When I run `add.py report <that milestone>`
  Then the header shows `tasks 0/0 done`, the footer `exit criteria 0/0 met`, no task blocks
  And it exits 0 with no divide-by-zero error

Scenario: milestone exists but MILESTONE.md is missing
  Given a milestone key in state.json whose MILESTONE.md file is absent
  When I run `add.py report <that milestone>`
  Then title and goal render `(unknown)` and exit criteria render `0/0`, the digest still prints (exit 0)
  And the command does NOT reject (the milestone exists; only its doc is gone)

Scenario: named milestone
  Given a milestone slug 'v9' exists
  When I run `add.py report v9`
  Then stdout renders v9's digest
  And no file on disk is created or modified

Scenario: a RISK-ACCEPTED task surfaces its waiver
  Given a member task gated RISK-ACCEPTED with owner+ticket+expiry in state.json
  When I run `add.py report` for its milestone
  Then the footer 'waivers:' line names that task's owner, ticket, and expiry
  And the task's block shows gate=RISK-ACCEPTED

Scenario: fail-closed on a missing prose field
  Given a member task whose §7 observe delta is still the template placeholder and has no tests/ dir
  When I run `add.py report` for its milestone
  Then that task's block shows `observe: (unknown)` and `tests=0`
  And the command still exits 0 (no crash, no silent skip)

Scenario: unknown milestone is rejected
  Given no milestone slug 'v99' exists
  When I run `add.py report v99`
  Then it exits non-zero with "unknown_milestone"
  And nothing is written to stdout's digest body and state.json is unchanged

Scenario: no active milestone and no arg
  Given state.json has no active_milestone set
  When I run `add.py report` with no arg
  Then it exits non-zero with "no_active_milestone"
  And state.json is unchanged
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:  add.py report [milestone] [--json] [--plain]
        milestone : optional positional; defaults to state.active_milestone
        --json    : emit raw structured data (report_data) for an agent to format
        --plain   : ASCII, no color, fixed width (pipe / CI / screen-reader safe)
      exit 0  -> dashboard / JSON on stdout; writes nothing
      exit 1  -> stderr "<code>: <msg>"; code ∈ { unknown_milestone, no_active_milestone }

Two seams both v9 tasks share:
  report_data(root, state, mslug) -> dict       # the FACTS; pure, NO writes (the raw capture)
  render_report(root, state, mslug, *, width=72, ascii=False) -> str   # PLAIN text (no ANSI); pure
  cmd_report: chooses tier (tty width / NO_COLOR / TERM / encoding), colorizes tty ONLY,
              prints. retro-artifact persists render_report(...) (canonical: width 72, ascii=False, plain).

Output shape — DASHBOARD v4 (human-review layout; label-grid header; wrapped learnings):
  ════════════════════════════════════════════════════════════════════════  (═×width)
   <slug> · <title>
  ════════════════════════════════════════════════════════════════════════
   VERDICT   <VERDICT>
   TASKS     <d>/<t> done        CRITERIA  <x>/<y> met
   GATES     <p PASS · r RISK · h STOP | none>   WAIVERS   <n | none>

   goal  <goal, wrapped; label once>

   TASK                        PHASE     GATE TESTS PROGRESS
   ───────────────────────────────────────────────────────────────────────
   <slug:<27>  <phase:<9>  <GATE:<4>  <tests:<5>  <8-cell phase track>
   legend  ● reached  ◉ current  ○ pending   spec→…→done

   EXIT CRITERIA  ●●●●●●●●●● <x>/<y> met
   [WAIVERS (<n>)            <- DETAILS block, only when waivers exist (count is in the grid)
     • <slug>: <owner> · <ticket> · expires <date>   (wrapped)]
   LEARNINGS (<n> carried)
     • <COMPETENCY · status · learning>   (word-wrapped to FULL text — never clipped)
  ════════════════════════════════════════════════════════════════════════

Rendering rules (v4 — terminal-correct + human-review; all stdlib, no wcwidth/rich):
  - VERDICT = BLOCKED if any HARD-STOP · DONE if all tasks done · else ACTIVE  (own line, leads)
  - HEADER = a 2-col aligned label grid (VERDICT / TASKS·CRITERIA / GATES·WAIVERS) — replaces the
    v3 crammed `·`-joined line; ASCII-only label+value cells so the grid can't break on width
  - LEARNINGS = the retro's payload: each delta word-wrapped to FULL text via `_wrap`, led by a
    `bullet` glyph, NEVER `_clip`-truncated (v4 human-review decision: readable > compact)
  - WAIVERS = count lives in the header grid; the footer shows the owner/ticket/expiry DETAILS
    block only when a waiver exists (no redundant "none" footer line)
  - alignment: ASCII-only in column-positioned cells (1 cell each); Unicode glyphs ONLY at
    line-END (the PROGRESS track) or a non-aligned row START (the learning/waiver bullet)
  - tiers: UNICODE (●◉○ ═ ─ •) | ASCII (#>. = - *) chosen by stdout encoding / TERM=dumb / --plain
  - color: ANSI on a tty ONLY (PASS green · RISK yellow · STOP/BLOCKED red), honoring NO_COLOR
    + TERM; render_report returns PLAIN so RETRO.md never carries escapes
  - width: adaptive (clamp 64–100) for an interactive tty; FIXED 72 for pipe/RETRO (reproducible)
  - GATE shortened: PASS · RISK · STOP · — (none); per-task observe moved to --json (not the table)
  - bar/track: 0/0 -> all-pending (no divide-by-zero); done task -> whole track reached

Data sources (per field) — unchanged from v2, captured at FULL fidelity:
  status / gate tally / phase / gate / waiver  <- state.json (authoritative; "exists" = key in state.milestones)
  title/goal                                   <- MILESTONE.md line 1 + goal:  (missing file -> (unknown))
  tests=<n>                                     <- count `def test_` under tasks/<slug>/tests/  (no dir -> 0)
  observe (json only)                           <- TASK.md §7 field, MULTI-LINE joined (placeholder -> (unknown))
  deltas                                        <- TASK.md §7 delta lines, ALL statuses, multi-line joined
  exit criteria x/y                             <- MILESTONE.md "Exit criteria" [x]/[ ] count  (no file -> 0/0)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · DATA SEAM   · PRESENTATION iterate-freely (currently v4)
  (2026-06-02 — applying THIS task's own [ADD] delta: the contract that binds is the FACTS /
  interface — `report_data` fields, the two seams, reject codes, purity, fail-closed — FROZEN @ v1
  and unmoved since. The pixel LAYOUT is a presentation layer that iterates without a re-freeze:
  v2 visual dashboard → v3 terminal-correct (senior-ui-ux-lead review) → v4 human-review layout
  (label-grid header + word-wrapped learnings, human-directed). A presentation change updates the
  shape sketch + its tests; it is NOT a change request back to SPECIFY. A change to the DATA SEAM
  still is.)
<!-- The DATA SEAM is the contract; the layout is presentation. See §7 [ADD] delta. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 90% (of the new report code path)
Plan (one test per scenario, asserting behavior not internals — drive `add.py report` as a subprocess / via `main()`):
  - test_active_mid_flight: build a fixture .add with 2 tasks (1 done+PASS+tests, 1 specify) / run `report` no-arg / assert header counts, both blocks present, state.json hash unchanged
  - test_named_milestone: run `report v9` / assert v9 digest on stdout / assert no file mtime changed under .add/
  - test_waiver_surfaced: task gated RISK-ACCEPTED with waiver / assert footer waivers line shows owner·ticket·expires
  - test_failclosed_unknown: task with placeholder observe + no tests/ dir / assert block shows `observe: (unknown)` and `tests 0` / assert exit 0
  - test_phase_track_and_badges: task at 'tests' phase, another done+PASS / assert track shows `contract●` and `tests◉` for the first, all `●` + `✓` badge for the done one (phase-position rendered, not a 7-row history)
  - test_progress_bars: milestone 1/2 done / assert tasks bar has exactly round(0.5×10)=5 `▰` cells; a 0/0 milestone renders an all-`▱` bar (no ZeroDivisionError)
  - test_deltas_with_status: tasks carrying open AND folded deltas / assert footer `deltas:` shows BOTH with their status tags (not open-only)
  - test_zero_task_milestone: milestone in state with 0 member tasks / assert `tasks 0/0 done`, `exit criteria 0/0 met`, no blocks, exit 0 (no ZeroDivisionError)
  - test_missing_milestone_doc: milestone key in state, MILESTONE.md deleted / assert title/goal `(unknown)`, exit criteria `0/0`, still prints, exit 0 (no reject)
  - test_unknown_milestone: `report v99` (no state key) / assert exit 1 and "unknown_milestone" on stderr / assert state.json unchanged
  - test_no_active_milestone: state with no active_milestone, no arg / assert exit 1 and "no_active_milestone"
  - test_render_is_pure: call `render_report(...)` twice / assert identical string AND zero writes (state.json + dir mtimes unchanged)

Tests live in: `./tests/` · MUST run red (missing `cmd_report`/`render_report`) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): render_report performs ZERO writes — read state + files only; cmd_report prints, never saves.
Code lives in: `./src/`  (and the wired command in `.add/tooling/add.py`)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — matches add.py); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 24 `test_report` + full suite **208 passed** (stdlib `unittest`)
- [x] coverage did not decrease — 24 tests; every scenario + the v3 tiers (ascii / no-color /
      --plain / verdict states / column alignment / multi-line fidelity / json↔text agreement) +
      2 v4 guards (test_header_is_label_grid, test_learnings_wrapped_not_clipped)
- [~] tests/contract changed during build — **DISCLOSE (4 presentation changes; the DATA SEAM never moved):**
      the LAYOUT went v1 (CLI) → v2 (visual dashboard) → v3 (terminal-correct, senior-ui-ux-lead review) →
      v4 (human-review layout: label-grid header + word-wrapped learnings, human-directed 2026-06-02).
      EVERY change was presentation — `report_data` facts, the two seams, reject codes, purity, fail-closed
      have been FROZEN @ v1 throughout. Per this task's own [ADD] delta, presentation is now an
      iterate-freely layer (not re-FROZEN each time), so a layout change updates the shape sketch + its
      test ASSERTIONS only (`X/Y tasks`→`X/Y done`; clipped→wrapped learnings). No passing test was
      weakened to hide a bug — the format changed by human direction and the tests followed it. Earlier
      build-bug fixes (goal-label, observe mis-scope, multi-line fidelity) each shipped with a regression test.
- [x] concurrency / timing of the risky operation is safe — `render_report`/`report_data` are PURE
      read-only (no writes, no shared state); `test_render_is_pure` + `test_no_ansi_when_not_tty` pin it
- [x] no exposed secrets, injection openings, or unexpected dependencies — **stdlib only** (`re`, `shutil`,
      `os`, `json`); no `rich`/`wcwidth` despite the TUI work; reads files read-only; no eval/shell/network
- [x] layering & dependencies follow CONVENTIONS.md — mirrors existing `cmd_*` + subparser + `_helpers`;
      dual tree (`.add` ⇄ `add-method`) re-synced byte-identical; ANSI kept OUT of the rendered string
- [x] a person reviewed and approved the change   ← YOUR gate (human-only step)

### GATE RECORD
Outcome: PASS   (recorded via `add.py gate PASS report-render`, 2026-06-02)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the fail-closed `(unknown)` rate (a rising rate = a prose
  field the parser can't read = a section header drifted); a non-zero exit from `report` (a reject
  code firing in normal use = a milestone-lookup assumption broke).
Spec delta for the next loop: §1 still describes the v2 dashboard glyphs (`▰▱` bars, labeled
  phase track) — superseded by §3 v3 (compact `●◉○` track, left-aligned columns, verdict-first
  header). The SPEC's *intent* ("one read-only digest of header + per-task block + roll-up") held
  across all three freezes; only its pixel description drifted. Lesson for the next spec: write §1
  presentation-agnostic — state WHAT facts appear and in what grouping, not the exact glyphs — so
  a presentation re-freeze doesn't strand the spec prose.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

- [ADD · folded] Presentation is not a freezable contract the way a behavioral/data seam is. The
  contract re-froze 3× (v1→v2→v3) and EVERY change was presentation; the data seam (`report_data`
  facts, reject codes, purity, fail-closed) never moved. Evidence: §3 history line + the v2→v3
  test churn touched only assertions about glyphs/columns, never about which facts. Fold: ADD's
  freeze-once discipline should bind the *facts/interface*, and explicitly mark a *presentation
  layer* as iterate-freely (don't stamp pixel layout "FROZEN @ vN"). This retroactively validates
  the tool-emits-data / agent-formats-report split (`--json` is the stable seam; the dashboard is
  a secondary, swappable surface).
- [SDD · folded] A milestone's frozen exit criteria can silently rot when a task's own contract
  changes shape. Evidence: v3 made `report` stdout multi-valued (tty color/width vs canonical
  plain), which falsified v9 MILESTONE.md's "RETRO.md byte-identical to stdout" — caught only by
  the advisor, not by any gate. Fold: add a verify-checklist line "do the milestone's frozen
  exit criteria still hold after what I built?" so a shared-contract drift turns a gate red
  instead of slipping to milestone close.
- [TDD · folded] When the test harness's capture stream (StringIO) lacks `.encoding`, the
  presentation tier auto-selects ASCII — so a test that drives the CLI and asserts Unicode glyphs
  is asserting against the wrong tier. Evidence: test_phase_track_compact / test_progress_bar_glyphs
  had to call `render_report(...)` directly (the canonical Unicode render) rather than capture
  `cmd_report` stdout. Fold: for tier-sensitive output, test the pure renderer at its canonical
  args; reserve CLI-capture tests for asserting the *tier-selection* logic itself.
- [UDD · folded] A no-`wcwidth` terminal UI stays aligned by construction if richness rides on
  width-neutral channels (color) and only ASCII-safe text sits in `len()`-aligned columns, with
  Unicode glyphs confined to line-end. Evidence: 200 green incl. test_columns_aligned_no_len_rightpad
  with zero width-measurement code. Fold: capture this as the house rule for any future ADD TUI.
- [ADD · folded] v9 reports the phase ROLLUP (which phase each task REACHED — the `●◉○` track +
  PHASE column), but NOT each phase's RESULT (what scenarios were set, what the contract froze,
  what verify actually found, the per-phase observe delta). The original ask was "report of each
  phase's result" — so v9 answers the milestone-level half and leaves the per-phase-detail half
  open. Evidence: a person reading `report v9` sees `report-render · done · PASS` but must still
  open TASK.md to learn WHAT each phase decided. Fold: a future loop adds a per-phase detail view
  (e.g. `report <milestone> <task>` or a `--phases` drill-down) that surfaces each phase's frozen
  artifact + outcome — turning the rollup into a true phase-by-phase narrative. Owner-directed
  (user, 2026-06-02): "improve ADD to report each phase."
