# TASK: report <milestone> <task>: render each phase's result from TASK.md

slug: phase-detail-render · created: 2026-06-02 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- extends the `report` command in add.py (the engine) + freezes the v9-1 extraction shape -> human reviews the diff at verify -->

> One-approval front (v7): the AI drafts Spec + Scenarios + Contract + Tests as ONE
> bundle; the human gives a single approval AT the frozen contract (§3, the seam).
> Below is that draft. Nothing builds until you approve §3.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

`add.py report <milestone> <task>` renders ONE read-only phase-by-phase narrative for a single
task: its seven phases (specify→observe) each shown with the CONTENT that phase captured in the
TASK.md (the rules, scenarios, frozen contract, test plan, build note, verify gate+evidence,
observe delta) plus the phase's reached/current state from state.json. It surfaces "what each
phase DECIDED" — the half v9's milestone rollup leaves to the file.

Must:
  - `add.py report <task>` (smart single arg) AND `add.py report <m> <task>` (explicit) render the
    task's 7 phase blocks in order specify→…→observe; each block shows the phase name, its
    reached/current/pending marker (from state.json's `phase`), and the captured content of that
    phase's `## N · PHASE` section in TASK.md
  - smart resolution: a single positional is tried as a MILESTONE first (-> rollup); if it is not a
    milestone but IS a known task, it drills into that task (milestone resolved from state) — so a
    person can drill by the task's own name without naming its milestone
  - the verify block additionally surfaces the recorded GATE outcome (PASS / RISK-ACCEPTED /
    HARD-STOP / none) read from state.json (authoritative), not parsed from prose
  - a section that is missing, or whose body is only template placeholders (`<...>`), renders
    `(empty)` for that phase — never a silent gap (carry v9 fail-closed)
  - the render is READ-ONLY: it writes nothing and leaves state.json byte-unchanged
  - the existing `add.py report` / `report <m>` (milestone rollup) renders exactly as before —
    the drill path is purely additive
Reject:
  - `report <m> <task>` where <task> is not a member of <m> -> "unknown_task"
  - `report <name>` (single arg) where <name> is neither a known milestone nor a known task ->
    "unknown_milestone" (milestone-first semantics; carry v9)
After:
  - the 7-phase narrative is on stdout; state.json is unchanged; the milestone rollup is unaffected
Assumptions (confirm before building):
  - [x] CLI surface = SMART single positional on the existing `report` command: `report <name>`
        resolves <name> as a milestone (-> rollup) else as a task (-> drill, milestone resolved
        from state), and the explicit `report <m> <task>` still drills — confirmed: removes the
        type-the-milestone friction (drill into a task by its own name); milestone/task slugs
        never collide (`v9` vs `report-render`), so the milestone-first fallback is unambiguous
  - [x] the view renders the FULL captured content per phase (trimmed of HTML comments + the
        `EXIT:` marker lines), not a one-line summary — confirmed: it is a drill-down, reading is
        the point (carry v9's "full text > clipped" decision)
  - [x] "done" is a terminal STATE, not an 8th section — the 7 blocks are specify→observe; a
        done task shows every block reached + the verify gate = PASS — confirmed

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: drill into a mid-flight task
  Given milestone 'vX' has task 'alpha' at phase 'contract' with §1–§3 filled
  When I run `add.py report vX alpha`
  Then stdout shows 7 phase blocks specify→observe in order
  And the specify/scenarios/contract blocks show their captured content
  And contract is marked current, specify/scenarios reached, tests→observe pending
  And state.json is byte-unchanged

Scenario: verify block surfaces the recorded gate
  Given task 'alpha' is done with gate PASS
  When I run `add.py report vX alpha`
  Then the verify block shows gate "PASS" (from state.json, not parsed prose)
  And every phase block is marked reached

Scenario: an unfilled phase renders (empty), never a silent gap
  Given task 'alpha' whose §5 BUILD body is only template placeholders
  When I run `add.py report vX alpha`
  Then the build block renders "(empty)"
  And the command still exits 0

Scenario: unknown task for the milestone is rejected
  Given milestone 'vX' has no task 'ghost'
  When I run `add.py report vX ghost`
  Then it exits non-zero with "unknown_task"
  And nothing is written and state.json is unchanged

Scenario: the milestone rollup is unaffected (additive)
  Given milestone 'vX'
  When I run `add.py report vX` (name resolves to a milestone)
  Then it renders the v9 milestone rollup exactly as before (not the phase detail)

Scenario: smart single arg drills by task name without naming the milestone
  Given milestone 'vX' has task 'alpha' and no milestone is named 'alpha'
  When I run `add.py report alpha` (single arg, not a milestone but a known task)
  Then it renders alpha's 7-phase detail (milestone resolved from state)
  And `add.py report vX alpha` renders the identical detail
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:  add.py report [name] [task] [--json] [--plain]   (EXTENDS the v9 report command)
        name : optional 1st positional. SMART: tried as a milestone (-> rollup) FIRST; if not a
               milestone but a known task, it drills into that task. Omitted -> active milestone.
        task : optional 2nd positional — explicit drill `report <m> <task>`; render PHASE-DETAIL.
      exit 0  -> phase-detail narrative (drill) or the v9 rollup (milestone/none) on stdout; writes nothing
      exit 1  -> stderr "add: error: <code>"; code ∈ { unknown_milestone, no_active_milestone,
                 unknown_task }   (rollup codes carried from v9; unknown_task is new)
      --json shape is POLYMORPHIC, keyed on path: rollup -> report_data dict; drill -> task_phases
             list (7 dicts). One line of doc so a downstream consumer knows which it gets.

Data seam (the v9-1 frozen shape — what each phase block is sourced from):
  task_phases(root, slug) -> list[dict]        # PURE; parse TASK.md §1–§7, NO writes
    each dict = { "phase": <name>, "n": <1..7>, "body": <cleaned section text | "(empty)"> }
    - reads TASK.md with encoding="utf-8" (dense with Unicode ·●◉○═─; never the locale default —
      carry the retro utf-8 lesson on the READ side; matches _task_prose / _milestone_doc)
    - section match keyed on the NUMBER, not the phase word: heading `^##\s*<n>\s*·` for n in 1..7
      (number is case/locale-proof; the phase name maps n->PHASES[n-1] for the block label)
    - body = lines from the heading until the next `^##\s` / `^---\s*$` / EOF.  KNOWN LIMIT
      (documented, not silent): a section body containing a line-start `## ` or a bare `---`
      would truncate early; today's TASK.md bodies don't (contracts use box-chars ─═, sub-heads
      use `### `). If that ever changes, this is the seam to revisit.
    - cleaned = body minus HTML comments (`<!-- … -->`) and the `EXIT:`/`<!-- EXIT -->` marker;
      a body that is empty or only `<...>` angle-placeholders after cleaning -> "(empty)"
    - missing file or missing section -> that phase's body = "(empty)" (fail-closed)
  render_task_detail(root, state, mslug, slug, *, width=72, ascii=False) -> str   # PURE, PLAIN

Render shape — PHASE DETAIL (one block per phase; presentation iterates per v9 [ADD] delta):
  ════════════════════════════════════════════════════════════════════════
   <mslug> › <slug>  ·  <task title>
   PHASE <current>   ·   GATE <outcome>
  ════════════════════════════════════════════════════════════════════════
   <glyph> 1 SPECIFY        (glyph = reached ● | current ◉ | pending ○, from state phase index)
   ──────────────────────────────────────────────────────────────────────
     <cleaned §1 body, wrapped to width | (empty)>

   <glyph> 2 SCENARIOS
   ──────────────────────────────────────────────────────────────────────
     <cleaned §2 body | (empty)>
   … (3 CONTRACT · 4 TESTS · 5 BUILD · 6 VERIFY · 7 OBSERVE, same block form) …
   6 VERIFY block also prints `GATE  <PASS|RISK-ACCEPTED|HARD-STOP|none>` from state.json
  ════════════════════════════════════════════════════════════════════════

Routing in cmd_report (additive — the rollup path is untouched):
  - args.task present (explicit `report <m> <task>`) -> DRILL: milestone=args.name; if name ∉
      milestones -> _die("unknown_milestone"); if task ∉ members -> _die("unknown_task")
  - args.name present, args.task None  -> if name ∈ milestones -> v9 ROLLUP (unchanged);
      elif name ∈ state.tasks -> DRILL (milestone = state.tasks[name].milestone);
      else -> _die("unknown_milestone")   (milestone-first semantics)
  - no positionals                     -> v9 ROLLUP on the active milestone (unchanged)
  - DRILL renders render_task_detail (or, with --json, dumps task_phases); tiers (width / ascii /
    color / --plain) reuse v9's cmd_report helpers unchanged

Data sources (per field):
  phase / current / gate     <- state.json (authoritative; gate is NEVER parsed from prose)
  per-phase body             <- TASK.md §1–§7 sections (cleaned; fail-closed to "(empty)")
  task title                 <- TASK.md line 1 `# TASK: <title>` (missing -> slug)
  membership (task ∈ m)      <- state.tasks[slug].milestone == mslug
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (approved 2026-06-02 · smart single-arg CLI chosen at the one-approval gate)
<!-- The DATA SEAM (task_phases fields, reject codes, fail-closed rule, smart-resolution routing)
is the contract; the per-block LAYOUT is presentation that iterates without a re-freeze (carry the
v9 [ADD] delta). -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: 90% (of the new phase-detail path)
Plan (one test per scenario; drive `add.py report` via `main()` on a tempdir .add):
  - test_drill_renders_seven_phases: fixture task at 'contract' / run `report vX alpha` / assert
    all 7 phase names present in order, §1–§3 bodies shown, contract marked current, state hash unchanged
  - test_verify_block_shows_gate_from_state: done+PASS task / assert verify block prints "PASS"
    sourced from state (corrupt the §6 prose gate text -> still shows state's PASS, not the prose)
  - test_unfilled_phase_is_empty: task whose §5 BUILD body is only `<placeholders>` / assert the
    build block renders "(empty)" / assert exit 0
  - test_unknown_task_rejected: `report vX ghost` (no such member) / assert exit !=0 + "unknown_task"
    on stderr / assert state.json unchanged
  - test_unknown_milestone_rejected: `report v99 alpha` / assert exit !=0 + "unknown_milestone"
  - test_smart_single_arg_drills_by_task: `report alpha` (alpha is a task, not a milestone) / assert
    it drills (per-phase "1 SPECIFY" block present) AND equals `report vX alpha` output; and
    `report ghost` (neither milestone nor task) -> exit !=0 + "unknown_milestone"
  - test_rollup_unaffected: `report vX` (name is a milestone) / assert it renders the v9 rollup
    (VERDICT/TASKS grid), NOT the phase detail (no per-phase "1 SPECIFY" block)
  - test_detail_is_read_only: call `render_task_detail(...)` twice / assert identical string AND
    state.json byte-unchanged (zero writes)
  - test_json_dumps_task_phases: `report vX alpha --json` / assert valid JSON list of 7 phase
    dicts with keys phase/n/body / assert read-only
  - test_task_phases_pure_extraction: unit-test `task_phases(root, slug)` directly — 7 entries,
    HTML comments + EXIT markers stripped, placeholder-only body -> "(empty)"

Tests live in: `add-method/tooling/test_phase_detail.py` (mirrors test_report.py; dual tree keeps
suites in the tooling dir) · MUST run red (missing `task_phases`/`render_task_detail` + the task
arg) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the drill path is READ-ONLY — no `write_text`/`save_state` on
any branch; the TASK.md read is wrapped try/except OSError so a bad file fails closed, never
crashes mid-render (CLAUDE.md design-for-failure).
Code lives in: `add-method/tooling/add.py` (the engine), synced byte-identical to `.add/tooling/add.py`.
Built: `_clean_phase_body`, `task_phases`, `_task_title`, `_detail_body`, `render_task_detail`
(new pure helpers/seams) + smart routing in `cmd_report` + the `task` positional in build_parser.
Constraints: stdlib only (re/argparse/json); did NOT change any test or the frozen §3 contract.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 219 in the add-method suite (10 new in test_phase_detail.py + the 208
      pre-existing + 1 fail-closed hardening test); `python3 -m unittest discover` -> OK. The
      suite ran RED first for the right reason (no task_phases / render_task_detail / 2nd
      positional) before any code was written.
- [x] coverage did not decrease — net +11 tests; a test per scenario + per reject + both seams
      unit-tested directly (task_phases extraction, render_task_detail purity).
- [x] no test or contract was altered to pass — §3 was FROZEN at the one-approval gate before
      Build; the build only ADDED helpers/seams + cmd_report routing + the `task` positional.
      The one post-build test (unreadable -> fail-closed) STRENGTHENS coverage; weakens nothing.
- [x] IO failure designed-for (CLAUDE.md) — task_phases / _task_title wrap the TASK.md read in
      try/except OSError -> fail closed (every phase "(empty)" / title->slug), proven by
      test_unreadable_file_failclosed. utf-8 pinned on the read (the v9 retro lesson, carried).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new
      package; READ-ONLY on every branch (zero writes — proven by state-hash asserts).
- [x] additive / no regression — test_rollup_unaffected proves `report <m>` renders the v9
      rollup byte-for-byte (it passed even while the rest of the suite was red); dual tree
      (.add ⇄ add-method) re-synced byte-identical (diff -q clean).
- [ ] a person reviewed and approved the change   <!-- the one-approval gate, below -->

Disclosed for review:
  - PRESENTATION (iterate-freely, NOT a re-freeze): at the 72-wide pipe/canonical tier a long
    pre-wrapped §body soft-wraps once more, so a few continuation lines read slightly ragged; on
    a real tty (wider width) it doesn't. The DATA SEAM (task_phases fields, fail-closed, smart
    routing) is unchanged — this is the v9 "presentation is a skin" boundary in action.
  - `--json` is shape-polymorphic by path (drill -> task_phases list; rollup -> report_data
    dict) — documented in the CLI help so a downstream consumer knows which it gets.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-02   (saw the full add.py diff + test file + live render before deciding)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): unknown_task / unknown_milestone reject-rate on `report`;
ragged-wrap complaints at the 72-wide pipe tier (the disclosed presentation debt).
Spec delta for the next loop: the awareness surface is now two-level — rollup (`report <m>`) +
drill (`report <task>`); a natural next slice is cross-task phase diff, explicitly OUT of v9-1.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] "smart single positional" (milestone-first, else task) beat the drafted two-arg
  CLI at the one-approval gate — the advisor caught that the draft made drill-down UNREACHABLE
  (argparse binds a lone positional to the 1st name). Lesson: trace argparse binding when a
  contract adds an optional positional; the obvious shape can silently strand a code path.
  (evidence: §3 routing line was internally inconsistent until reconciled before freeze)
- [ADD · folded] the v9 "freeze the DATA seam, not presentation" delta PAID OFF here: the ragged
  72-wide wrap shipped as disclosed presentation debt, NOT a gate-blocker, because the frozen
  contract is task_phases' fields + fail-closed rule, not the block layout. (evidence: PASS with
  a known cosmetic gap, no re-freeze needed to fix it later)
- [TDD · folded] the v9 retro utf-8 lesson generalized to the READ side: pinning encoding + an
  OSError fail-closed guard on the TASK.md read was added BEFORE the gate (not after a locale
  bug), and locked by test_unreadable_file_failclosed. (evidence: design-for-failure check
  passed with a test, not a promise)
- [UDD · folded] a drill-down is a READ surface where line-structure (scenarios, contract code)
  matters more than column alignment — so it preserves physical lines + soft-wraps, unlike the
  rollup which collapses prose. Two render idioms now coexist by purpose. (evidence: _detail_body
  vs _wrap diverged deliberately)
