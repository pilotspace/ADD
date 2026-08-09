# TASK: report --decide seam digest + rollup DECIDE NEXT footer

slug: decide-digest · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `report --decide` — a decision-seam digest. Detect the task's seam FROM STATE,
extract decision markers VERBATIM from TASK.md §bodies, and render decisive-facts-first:
NEEDS YOUR JUDGMENT → ENGINE FACTS → UNLOCKS → the decide command. Plus a DECIDE NEXT
footer the milestone rollup always ends with.

Framings weighed: seam-switching single flag (chosen) · two flags --front/--gate
(rejected: the human asks "what do I decide?", not "which view do I want") ·
engine-ranked judgment items (rejected: ranking IS judgment; add.py stays
judgment-free — extraction in section order only).

Must:
  - `report [<milestone>] <task> --decide` renders the seam digest; positional
    resolution is IDENTICAL to existing `report` (smart milestone-first, then task).
    Bare `report --decide` resolves to the ACTIVE task.
  - Seam from state.json ONLY (never prose):
      · gate != none OR phase in {observe, done}        -> seam `recorded`
      · phase in {specify, scenarios, contract, tests}  -> seam `front`
      · phase in {build, verify}                        -> seam `gate`
  - Decision marker = a line whose first non-space chars are `⚠` or `- [~]` or
    `- [ ]`, PLUS its continuation lines (immediately following lines indented
    deeper than the marker). Extracted BYTE-VERBATIM — never re-wrapped, never
    clipped. Sources: gate seam -> §6 then §1; front seam -> §1 then §3.
  - NEEDS YOUR JUDGMENT always prints its count — including `(0)` (fail-visible:
    a surprising zero is readable; an omitted section is not).
  - ENGINE FACTS line: phase · gate · deps with each dep's gate · tests count —
    all from state.json + `_tests_count`, never parsed from prose.
  - gate seam: UNLOCKS line (gate PASS -> task done -> milestone n/m) and
    `DECIDE  add.py gate PASS | RISK-ACCEPTED | HARD-STOP`.
  - front seam, §3 `Status:` line not FROZEN: bundle flags first (⚠ from §1+§3),
    then the §3 contract block verbatim, then `STATUS DRAFT`, then
    `DECIDE approve -> freeze §3 -> auto run to build/verify (autonomy: <dial>)`.
  - front seam, §3 `Status:` line says FROZEN: render `no decision pending —
    frozen; the run owns it. next seam: verify gate` (missing Status -> DRAFT,
    fail-closed).
  - seam `recorded`: render `no decision pending` + the recorded gate from state.
  - `--decide --json` emits ONE dict: { seam, milestone, task, phase, gate,
    judgment: [{marker, section, text}], facts: {phase, gate, deps, tests},
    unlocks, decide } — additive; every existing report shape is unchanged.
  - `--decide` composes with `--plain` (ASCII tier, no ANSI) exactly as today.
  - The milestone ROLLUP (no --decide) always ends with one `DECIDE NEXT` line:
      · any task gate==HARD-STOP        -> name it (resolve the stop) [wins]
      · all tasks done                  -> `fold learnings + archive-milestone <ms>`
      · a task at a seam (active task first, then state order): front -> approve
        its contract; verify+gate==none -> gate it
      · otherwise                       -> `none — run in progress (<task> at <phase>)`
  - `report <ms> --decide` (positional resolves to a MILESTONE) renders just that
    DECIDE NEXT block.
  - PURE: every --decide path writes NOTHING (v9 read-only discipline carried).

Reject:
  - bare `report --decide` with no active task -> "no_active_task"
  - unknown positional names -> existing "unknown_milestone" / "unknown_task"
    (byte-identical to today; --decide adds no new resolution behavior)

After:
  - A reviewer at any seam runs ONE command and reads the decisive facts first.
  - Existing `report` outputs are unchanged EXCEPT the additive rollup footer.

Assumptions — least-sure first:
  ⚠ [extraction] The marker grammar is prose-convention (`⚠` / `- [~]` / `- [ ]`
    + indented continuations) — least sure because §bodies are free prose; a
    differently-worded deviation is silently MISSED (fail-open, the dangerous
    direction). In-scope mitigation: the always-printed count makes a surprising
    `(0)` visible; a `check` lint is explicitly OUT (milestone scope). If wrong:
    pin the grammar in the TASK template + add the lint — one new task.
  ⚠ [freeze-signal] The front seam trusts the §3 `Status:` prose line as the
    freeze signal (FROZEN vs DRAFT) — least sure because it is the ONE prose
    read in an otherwise state-only seam rule; v12 set the precedent (freeze is
    artifact-observable, no engine flag). If wrong (prose drifts): seam shows
    "approve" for an already-frozen contract — annoying, not unsafe; cost: add
    an engine freeze flag (contract change, new task).
  - [ ] DECIDE NEXT picks the active task first, then state order — confirm.
  - [ ] `report <ms> --decide` renders the footer block (vs erroring) — confirm.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: gate-seam digest leads with the judgment items
  Given a task at phase verify with gate none, a `- [~]` deviation in §6 and a `⚠` flag in §1
  When I run `report <ms> <task> --decide`
  Then NEEDS YOUR JUDGMENT (2) renders the §6 marker before the §1 marker, both byte-verbatim
  And ENGINE FACTS shows phase/gate/deps/tests from state, and the DECIDE line names the three gate outcomes

Scenario: front-seam digest renders the bundle for approval
  Given a task at phase contract whose §3 Status line says DRAFT, with two ⚠ flags in §1
  When I run `report <ms> <task> --decide`
  Then the ⚠ flags render first, then the §3 contract block verbatim, then STATUS DRAFT
  And the DECIDE line says approving freezes §3 and opens the auto run

Scenario: frozen front has no pending decision
  Given a task at phase tests whose §3 Status line says FROZEN @ v1
  When I run `report <ms> <task> --decide`
  Then it renders "no decision pending" naming verify as the next seam
  And no approval prompt is shown

Scenario: zero markers is visible, not omitted
  Given a task at phase verify whose §1 and §6 contain no marker lines
  When I run `report <ms> <task> --decide`
  Then NEEDS YOUR JUDGMENT (0) still renders, followed by ENGINE FACTS

Scenario: bare --decide uses the active task
  Given an active task at phase verify
  When I run `report --decide`
  Then the digest renders for the active task

Scenario: bare --decide with no active task is refused
  Given no active task
  When I run `report --decide`
  Then it fails with "no_active_task" and exit code 1
  And nothing is written

Scenario: recorded seam shows the gate, asks nothing
  Given a task at phase done with gate PASS
  When I run `report <ms> <task> --decide`
  Then it renders "no decision pending" plus the recorded gate PASS sourced from state

Scenario: --decide --json emits one frozen-shape dict
  Given a task at phase verify with one §6 marker
  When I run `report <ms> <task> --decide --json`
  Then stdout parses as ONE dict with keys seam/milestone/task/phase/gate/judgment/facts/unlocks/decide
  And judgment[0].text is byte-identical to the §6 marker lines

Scenario: --decide composes with --plain
  Given a task at phase verify
  When I run `report <ms> <task> --decide --plain`
  Then the output is ASCII-tier with no ANSI escapes

Scenario: rollup footer on a finished milestone
  Given a milestone whose tasks are all done
  When I run `report <ms>`
  Then the rollup ends with DECIDE NEXT naming fold learnings + archive-milestone

Scenario: rollup footer names the seam-blocked task
  Given a milestone with a task at verify and gate none
  When I run `report <ms>`
  Then DECIDE NEXT names that task and the gate command

Scenario: rollup footer HARD-STOP wins
  Given a milestone with one task gate==HARD-STOP and another awaiting a front approval
  When I run `report <ms>`
  Then DECIDE NEXT names the HARD-STOP task

Scenario: rollup footer during a run
  Given a milestone whose only undone task is at phase build
  When I run `report <ms>`
  Then DECIDE NEXT says none — run in progress, naming the task and phase

Scenario: --decide on a milestone renders only the footer block
  Given a milestone slug as the positional
  When I run `report <ms> --decide`
  Then only the DECIDE NEXT block renders (no rollup table)

Scenario: --decide writes nothing
  Given any task at any phase
  When I run `report <ms> <task> --decide`
  Then the set of files under .add/ is unchanged (no RETRO, no state write)

Scenario: existing outputs stay stable
  Given the same project before and after this feature
  When I run `report <ms>` and `report <ms> <task>` without --decide
  Then the drill output is byte-identical and the rollup differs ONLY by the appended DECIDE NEXT footer
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# CLI (additive — every existing report form is byte-stable except the rollup footer)
add.py report [--decide] [--json] [--plain] [milestone] [task]

  resolution: UNCHANGED from today (explicit <m> <task>; smart single positional
              milestone-first-then-task; none -> active milestone). NEW: with
              --decide and NO positional -> the ACTIVE TASK (not milestone);
              none active -> stderr "add: error: no_active_task — name one:
              add.py report <milestone> <task> --decide" exit 1.

  --decide, resolves to a TASK -> seam digest, exit 0:
      seam := "recorded"  if gate != "none" or phase in {observe, done}
              "front"     if phase in {specify, scenarios, contract, tests}
              "gate"      if phase in {build, verify}
      marker := line whose first non-space chars are "⚠" | "- [~]" | "- [ ]",
                plus following lines indented deeper than the marker line;
                text kept byte-verbatim (no wrap, no clip)
      gate seam  -> header (DECIDE · <task> · seam: VERIFY GATE)
                    NEEDS YOUR JUDGMENT (n)   markers: §6 then §1, section-tagged
                    ENGINE FACTS              phase · gate · deps(+gates) · tests
                    UNLOCKS                   gate PASS -> task done -> milestone n/m
                    DECIDE                    add.py gate PASS | RISK-ACCEPTED | HARD-STOP
      front seam -> §3 "Status:" line FROZEN? (missing -> DRAFT, fail-closed)
                    DRAFT:  flags (⚠ from §1+§3) -> §3 block verbatim -> STATUS DRAFT
                            -> DECIDE approve -> freeze §3 -> auto run (autonomy dial)
                    FROZEN: "no decision pending — frozen; next seam: verify gate"
      recorded   -> "no decision pending" + gate from state.json

  --decide, resolves to a MILESTONE -> ONLY the DECIDE NEXT block, exit 0
  --decide --json -> ONE dict, exit 0:
      { "seam": str, "milestone": str, "task": str|null, "phase": str,
        "gate": str, "judgment": [ {"marker": "⚠"|"[~]"|"[ ]",
        "section": 1|3|6, "text": str} ], "facts": {"phase": str, "gate": str,
        "deps": [{"slug": str, "gate": str}], "tests": int},
        "unlocks": str, "decide": str }
  --decide --plain -> ASCII tier, no ANSI (same tiering as today)

  ROLLUP footer (no --decide; always appended, additive-only):
      "DECIDE NEXT  <line>" where precedence is
        1. any gate==HARD-STOP            -> "resolve HARD-STOP on <task>"
        2. all tasks done                 -> "fold learnings + archive-milestone <ms>"
        3. first seam-blocked task (active first, then state order):
             front -> "approve the contract of <task> — report <ms> <task> --decide"
             verify & gate==none -> "gate <task> — report <ms> <task> --decide"
        4. else                           -> "none — run in progress (<task> at <phase>)"

# Errors (existing codes unchanged; one new)
  no_active_task     -> bare `report --decide`, no active task        exit 1
  unknown_milestone / unknown_task -> byte-identical to today          exit 1

# Purity
  every report path (incl. --decide) is PURE: no writes, no state mutation
```

Status: FROZEN @ v1   <!-- approved by Tin, 2026-06-04 — the v7 one-approval; both ⚠ flags + the two [ ] defaults presented at the seam. Changing this = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every new branch — the seam map (3 seams × gate/phase combos), the
marker extractor (3 prefixes + continuations + zero-markers), front DRAFT vs FROZEN,
`--json` shape, `--plain` tier, the 4-precedence rollup footer, both error paths,
purity, and the byte-stability regression guards.

Plan (one test per §2 scenario, asserting behavior via stdout/exit/state — never internals):
  - test_gate_seam_digest_leads_with_judgment: §6 marker before §1, byte-verbatim
  - test_front_seam_renders_bundle_for_approval: flags → §3 verbatim → STATUS DRAFT
  - test_frozen_front_no_pending_decision
  - test_zero_markers_prints_count_zero
  - test_bare_decide_uses_active_task
  - test_bare_decide_no_active_task_refused: stderr "no_active_task", exit 1, no writes
  - test_recorded_seam_shows_gate_from_state
  - test_decide_json_one_dict_frozen_keys: judgment[0].text byte-identical to §6
  - test_decide_plain_ascii_no_ansi
  - test_footer_done_milestone_fold_archive
  - test_footer_names_seam_blocked_task
  - test_footer_hard_stop_wins
  - test_footer_run_in_progress
  - test_decide_on_milestone_renders_footer_block_only
  - test_decide_writes_nothing: .add/ file set + state.json bytes unchanged
  - test_existing_outputs_stable: drill byte-identical; rollup differs only by footer

Tests live in: `add-method/tooling/test_decide_digest.py` (suite root, like every prior
task) · `import add`, the shared `_run(argv)` capture helper, temp project via
`add.main(["init", ...])` · MUST run red (no `--decide` flag, no footer) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): every `--decide` path stays PURE (no writes, no state
mutation) — reuse the existing read-only report plumbing; marker text passes through
byte-verbatim (no _wrap/_clip on judgment items). Footer is APPEND-ONLY to the rollup.
Code lives in: `add-method/tooling/add.py` (canonical), then sync to `.add/tooling/add.py`
+ `src/add_method/_bundled/` so `test_bundle_parity` / tree-parity stay green.
Constraints: do NOT change any test or the contract; stdlib only (no new imports
expected); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 347 tests … OK`; the 18 `test_decide_digest`
      scenarios all green; dogfood smoke on this very task rendered the gate-seam
      digest + the v13 footer correctly.
- [x] coverage did not decrease — every new branch exercised AND asserted: the three
      seams (gate / front-DRAFT / front-FROZEN / recorded), all 3 marker prefixes +
      continuations + `- [x]` non-match + zero-markers, bare `--decide` (active task /
      none), `--json` (task + milestone key-set), `--plain`, all 4 footer precedence
      branches, purity (no writes), and the v9 byte-stability landmarks.
- [~] no test or contract was altered during build — **DISCLOSED (not silent).** §3
      (frozen contract) untouched. After the red run, TWO ADDITIVE tests were added to
      `test_decide_digest.py` (this task's own new suite): `- [ ]` prefix extraction +
      milestone `--decide --json` key-set — both REQUIRED by §4's own coverage target
      ("3 prefixes", "--json shape"), closing the gap pre-gate. No existing assertion
      was changed or weakened; no pre-existing test file touched.
- [x] concurrency / timing safe — every `--decide` path is PURE (zero writes, proven
      by `test_decide_writes_nothing` over text/footer/json paths); nothing to race.
- [x] no exposed secrets, injection openings, or unexpected dependencies — zero new
      imports (stdlib already in place); marker text is printed verbatim to stdout,
      never eval'd; same prose-render exposure class as the existing drill-down.
- [x] layering & dependencies follow CONVENTIONS.md — one canonical heading scan
      (`_phase_spans`) now shared by task_phases + the digest (dedup, v12-1 style);
      3-tree md5 parity verified (`49ec37ca…` × 3); `test_bundle_parity` green.
- [x] a person reviewed and approved the change — Tin, 2026-06-04 (gate PASS)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-04
Note: disclosed deviation accepted — two ADDITIVE tests added post-red to this task's
own new suite, mandated by §4's coverage target (3 prefixes · --json shape); nothing
weakened, §3 + all pre-existing tests untouched. 347/347 green; 3-tree md5 parity.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does NEEDS YOUR JUDGMENT (0) ever render at a real
gate seam (would signal the fail-open extraction missing a worded deviation)? do humans
actually run the DECIDE NEXT command lines?
Spec delta for the next loop: the footer's "fold + archive" fired while MILESTONE.md
still listed 2 planned-but-uncreated tasks — state-only is blind to planned scope.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] DECIDE NEXT is state-only, so planned-but-unscaffolded MILESTONE.md tasks are invisible — it said "fold + archive v13" with 2 of 3 planned tasks not yet created; consider a "n planned tasks not yet scaffolded" hint sourced from MILESTONE.md (evidence: report v13 right after decide-digest PASS)
- [TDD · folded] a red suite can under-cover its own §4 coverage target — two §4-mandated branches (3rd marker prefix, milestone --json key-set) were only caught at verify; at the tests phase, diff the §4 target nouns against the test list before declaring the suite red-complete (evidence: decide-digest §6 [~] disclosure)
