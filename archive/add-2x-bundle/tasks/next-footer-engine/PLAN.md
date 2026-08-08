# TASK: mutating verbs print an engine-sourced next: footer — one resolver, no double-printing

slug: next-footer-engine · created: 2026-06-12 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): VERIFIED 2026-06-12 via serena — `add-method/tooling/add.py` (engine change: ENGINE_MD5 re-pin 8a8967a151710f35dd9d3dea3ca86566 + ×3 sync (final value; the 45254aa ground-time guess was superseded as the engine was finalized)). The RESOLVER to reuse (the ONE source): `cmd_guide` (:997) resolves `phase -> PHASE_GUIDE[phase] = (action, chapter)` and prints `next : <action>` + a `then :` line whose logic is the next-command map — verify→"gate PASS|RISK-ACCEPTED|HARD-STOP", done→"new-task <slug>", else→"advance". That map + PHASE_GUIDE are the footer's single source; the task factors them into a shared `_next_footer(state, slug) -> str` that BOTH cmd_guide and the mutating verbs call (no duplicated next-step logic). The MUTATING verbs that gain the footer (they write state/files): advance (:535, tail `print("phase X -> Y")` — bare, no footer today) · gate (:653) · new-task · new-milestone · milestone-done · set-milestone · use · reopen · heal · phase · lock · stage · archive-milestone · compact · init. The CONVERGENCE points (ad-hoc next hints today that must fold onto the ONE footer, never double-print): new-task tail ("…then: add.py advance"), new-milestone tail ("Decompose it into tasks: add.py new-task…"), init tail (multi-line "next:" block). Read-only verbs are OUT (status/check/guide/report/deltas/audit/ready/project already orient).
Context (working folder): `.add/milestones/next-step-seams/MILESTONE.md` — risky contract owned here: the footer line grammar `next: <command> — <why>` (render-blind testable); the `[you drive|human gate]` driver marker is the SIBLING task gate-owner-marker (reserved trailing slot, not built here). Shared decisions: ONE resolver (reuse the guide path) · no double-printing (ad-hoc hints converge) · the marker derives from recorded state (autonomy×phase), never prose. Suites coupled: a NEW test_next_footer_engine.py; existing tests that assert a mutating verb's exact stdout (e.g. test asserting new-task / new-milestone / advance output) may need the footer line added — sweep at tests.
Honors (patterns / conventions): engine pin idiom (re-aim + ×3 sync); render-blind testable output (a plain `next: …` line, greppable, no color); additive-only (the footer never replaces the verb's result line, it follows it); the milestone's no-double-print rule (a verb prints exactly ONE next-step). NOT a trust/gate change — additive output — so autonomy stays auto (verify auto-gates on evidence + a refute-read).
Anchors the contract cites: `cmd_guide` + `PHASE_GUIDE` + the then-command map (verify/done/else) · `_next_footer` (NEW shared helper) · the mutating-verb tails · `_phase_owner` (exists; the marker's future input, named only) · `engine_pin.ENGINE_MD5` (RE-PINNED here).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an engine-sourced `next:` footer on every mutating verb — ONE resolver, no double-printing
Framings weighed: ONE shared `_next_footer(root, state)` reusing the guide path — two arms: active-task→PHASE_GUIDE+then-map, else→`_decide_next_base` (chosen) · per-verb bespoke next-step strings (rejected — duplicates logic, a second source of truth, the exact rot this milestone removes) · reconverge status+guide+report onto one renderer too (rejected — those are READ-ONLY, OUT of scope per the milestone; over-reaches blast radius)
Must:
<must>
  - `_next_footer(root, state) -> str` returns exactly ONE line beginning `next: ` and ending with a reserved trailing driver-marker slot (default empty this task; sibling gate-owner-marker fills ` [you drive]`|` [human gate]`)
  - Arm A — active task is IN-FLIGHT (`gate == "none"` AND `phase != "done"`): command = `add.py advance` (phase != verify) | `add.py gate PASS | RISK-ACCEPTED | HARD-STOP` (phase == verify); why = `PHASE_GUIDE[phase]` first clause (the same per-phase copy `guide` prints). The `gate == "none"` guard is precise: a HARD-STOPped task keeps `gate == "HARD-STOP"` (never done) so it falls to Arm B, and a PASS/RISK task is `phase == "done"` — so Arm A only ever sees a live, un-gated phase.
  - Arm B — otherwise: `next: ` + `_decide_next_base(state, report_data(root, state, active_milestone))` — the SAME state precedence the report dashboard renders (no parallel logic); a HARD-STOPped task resolves here to `resolve HARD-STOP on <slug>`
  - every COMPLETING (exit-0) mutating verb prints exactly one footer line as its LAST stdout, AFTER its result line — computed from the POST-mutation state (after save_state). The exit-3 HEAL paths (cmd_heal · gate→heal) are a redo SIGNAL, not a completion: they keep their `return_to_build` seam (human-confirmed at tests 2026-06-12), no footer.
  - convergence: verbs that already emit an ad-hoc next-step hint (new-task `then: add.py advance` · new-milestone `Decompose it into tasks…` · gate's `HARD-STOP recorded… return to BUILD`) DROP the ad-hoc hint and emit the footer instead — never both. init is NOT in this set: it KEEPS its bespoke setup-flow block — converging it would break test_brownfield_scan v1 (rule #3); see the §3 EXCEPTION
  - new-milestone's empty-milestone footer NAMES a command (`add.py new-task <slug>`), not the bare `none — no tasks yet`: the `_decide_next_base` empty-rows branch is reshaped command-first (improves the report's DECIDE NEXT identically — the string is unpinned)
  - gate routes EVERY outcome through the shared footer (no special arm): PASS/RISK → state-arm next, HARD-STOP → Arm B `resolve HARD-STOP on <slug>` — so the bespoke `HARD-STOP recorded…` line is dropped, never printed alongside the footer
  - fail-soft: if footer resolution raises (no active milestone, unreadable doc, corrupt rollup) the verb STILL exits 0 with its state saved, and the footer degrades to one generic `next: add.py status — re-orient` line — a successful mutation is never turned into a crash by its own footer
</must>
Reject:
<reject>
  - a mutating verb emits ZERO next: lines -> exit-criterion violation (caught per-verb by the sweep test)
  - a mutating verb emits TWO next-step hints (surviving ad-hoc tail + footer) -> "double_print" (the no-double-print decision; asserted by counting `next:`/hint lines == 1)
  - footer resolution raises and aborts a verb whose state already saved -> the fail-soft arm must swallow it and still print one line
  - next-footer-engine writes a prose-derived `[you drive]`/`[human gate]` marker -> reserved for gate-owner-marker; here only the empty slot is emitted, never an invented driver word
</reject>
After:
<after>
  - after ANY mutating verb, stdout's final non-empty line matches `^next: .+` and carries the trailing reserved marker slot
  - read-only verbs (status/guide/report) gain NO footer; the ONE shared change they inherit is `_decide_next_base`'s empty-rows text (the report's DECIDE NEXT for an empty milestone improves identically — intended, unpinned), nothing else
  - `_next_footer` writes nothing — it is a pure render over already-committed state — and the ×3 add.py mirrors stay byte-identical with `engine_pin.ENGINE_MD5` re-aimed
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the frozen grammar `next: <command> — <why>` assumes every next-step has ONE typeable command, but TWO reachable state-arm branches have none — `run in progress (<slug> at build)` and `resolve HARD-STOP on <slug>`. I widen the grammar to command-OPTIONAL for those (both only ever ADD to a previously-silent verb, never regress). Lowest confidence because the milestone froze a command-FIRST grammar and I am loosening it for ≥2 branches. If wrong: synthesize commands for them (`add.py use <slug>`, a recovery verb) — but that expands Arm B past the `_decide_next_base`-verbatim boundary, so it is deliberately deferred.
  - [x] RESOLVED (contract v2, change-request 2026-06-12): lifecycle/setup verbs lock · stage · archive-milestone · compact get the SAME generic state-arm footer (orientation, not a crisp workflow command). init is the EXCEPTION — converging it breaks test_brownfield_scan v1 (rule #3), so it KEEPS its bespoke setup-flow block; init's goal-placeholder UX stays with the sibling ux-stale-followups.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

Verb × representative-state → resolved footer → vs. today (the convergence ledger — a verb is IN
only if its footer is ≥ what it prints today):

| verb (state) | arm | footer line | vs today |
|---|---|---|---|
| advance (active at specify) | A | `next: add.py advance — state every rule; Must/Reject/After` | gain (bare result only) |
| advance (active → verify) | A | `next: add.py gate PASS | RISK-ACCEPTED | HARD-STOP — run the suite + checks, record the gate` | gain |
| gate PASS (next task at contract) | B | `next: approve the contract of <slug> — add.py report <ms> <slug> --decide` | gain (silent) |
| gate PASS (all tasks done) | B | `next: consolidate learnings + archive-milestone <ms>` | gain |
| gate HARD-STOP (task keeps gate=HARD-STOP) | B | `next: resolve HARD-STOP on <slug>` | converge (drop the bespoke "HARD-STOP recorded…" hint) |
| new-task <slug> | A | `next: add.py advance — gather the real codebase (§0 GROUND)` | converge (drop `then: advance`) |
| new-milestone <slug> (empty) | B* | `next: decompose into tasks — add.py new-task <slug>` | converge + FIX (would regress to `none — no tasks yet`) |
| use / reopen / phase | A | task-phase footer (advance, or gate at verify) | gain |
| set-milestone / lock / stage / milestone-done / compact | B | state-arm next (or generic on fail-soft) | gain |
| archive-milestone (no active ms left) | fail-soft | `next: add.py status — re-orient` | gain |
| heal · gate→heal (exit 3) | OUT | keeps `return_to_build: … advance back to verify` | unchanged (redo signal, not a completion) |

B* = the one shared-code change: `_decide_next_base` empty-rows branch reshaped command-first.

<scenarios>

```gherkin
Scenario: advance mid-front names the phase command
  Given an active task at phase specify (not done)
  When add.py advance runs (specify -> scenarios)
  Then the last stdout line is "next: add.py advance — <scenarios why>"
  And the verb's own "task '<slug>' phase specify -> scenarios" result line is unchanged

Scenario: advance into verify names the gate command
  Given an active task advancing tests -> verify
  When add.py advance runs
  Then the footer command is "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
  And exactly one line begins with "next: "

Scenario: gate PASS routes to the state arm
  Given task A is at verify and task B (same milestone) is at contract
  When add.py gate PASS runs on A (A -> done)
  Then the footer names B's contract approval ("approve the contract of B")
  And A's "gate -> PASS" result line is unchanged

Scenario: gate PASS on the last task points at consolidation
  Given the gated task is the milestone's only/last undone task
  When add.py gate PASS runs
  Then the footer names "archive-milestone <ms>"

Scenario: new-task converges its tail (no double-print)
  Given a project with a locked setup
  When add.py new-task foo runs
  Then exactly one next-step line is printed and it is "next: add.py advance — <ground why>"
  And the old "then: add.py advance" ad-hoc tail is absent

Scenario: new-milestone on an empty milestone names a command
  Given add.py new-milestone bar creates an empty active milestone
  When the footer resolves
  Then it is "next: decompose into tasks — add.py new-task <slug>"
  And it is NOT the bare "none — no tasks yet"

Scenario: gate HARD-STOP routes to Arm B (no special arm)
  Given a task at verify
  When add.py gate HARD-STOP runs (task keeps gate=HARD-STOP, phase=verify, not done)
  Then the footer is "next: resolve HARD-STOP on <slug>" (Arm B, not the verify gate command)
  And exactly one stdout line begins with "next: "
  And the bespoke "HARD-STOP recorded… return to BUILD" hint does NOT survive alongside it

Scenario: fail-soft when no active milestone
  Given a mutating verb runs with state.active_milestone = null (e.g. just after archive-milestone)
  When the footer resolves
  Then it degrades to "next: add.py status — re-orient"
  And the verb still exits 0 with its state saved (no no_active_milestone crash)

Scenario: every completing mutating verb ends with exactly one next: line (the exit-criterion sweep)
  Given each COMPLETING (exit-0) mutating verb is exercised in a representative state
  When it runs
  Then its stdout contains exactly one line matching ^next:
  And no completing mutating verb prints zero next: lines
  And the exit-3 heal paths are excluded by design (their return_to_build message is the seam)

Scenario: the driver-marker slot is reserved (render-blind)
  Given any footer line
  When it is parsed
  Then it carries a trailing marker slot (empty this task) that gate-owner-marker can fill
  And next-footer-engine never writes the words "you drive" or "human gate"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_next_footer(root: Path, state: dict) -> str
  returns: exactly one line, no trailing newline, shape:
    "next: <command-or-directive> — <why>{MARKER_SLOT}"
    MARKER_SLOT — reserved trailing region; "" this task (gate-owner-marker appends
                  " [you drive]" | " [human gate]"). command-OPTIONAL: a state with no
                  single next command (run in progress · resolve HARD-STOP) omits the command head.

  Arm A  (active task IN-FLIGHT: gate == "none" AND phase != "done"):
    phase   = task["phase"]            # gate=="none" + phase!="done" => a live, un-gated phase
    command = "add.py advance"                                   if phase != "verify"
            | "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"     if phase == "verify"
    why     = PHASE_GUIDE[phase][0]   (first clause; the copy `guide` already prints)
    -> "next: {command} — {why}{MARKER_SLOT}"
    # WHY gate=="none" (not `not _task_done`): a HARD-STOPped task is NOT done but keeps
    # gate=="HARD-STOP" -> it must fall to Arm B, not be told to re-gate itself.

  Arm B  (else — active task gated/done, or no live task):
    mslug = state.get("active_milestone")
    if not mslug: -> fail-soft generic line
    d     = report_data(root, state, mslug)        # pure, no writes
    -> "next: " + _decide_next_base(state, d) + MARKER_SLOT
    HARD-STOPped task -> _decide_next_base `stopped` branch -> "resolve HARD-STOP on <slug>"
    empty-rows branch reshaped: "none — no tasks yet"
        becomes "decompose into tasks — add.py new-task <slug>"  (command-first)

  Fail-soft: any exception resolving Arm B  ->  "next: add.py status — re-orient{MARKER_SLOT}"

Call sites (every COMPLETING exit-0 mutating verb; LAST stdout line, after the result line):
    print(_next_footer(root, state))
  converging (drop the ad-hoc tail, emit the footer): new-task · new-milestone · gate
  gate: completing outcomes -> shared footer (no special arm). PASS/RISK -> state-arm next;
        HARD-STOP -> Arm B "resolve HARD-STOP on <slug>". The bespoke
        "HARD-STOP recorded… return to BUILD" line is DROPPED (converges).
  CLARIFIED at tests (human-confirmed 2026-06-12): the exit-3 HEAL paths — cmd_heal and the
  gate->scope/tamper-heal that `raise SystemExit(3)` — are a redo SIGNAL, not a completion;
  they KEEP their existing `return_to_build: … advance back to verify` message as the seam
  (no footer, no double-print). The footer covers exit-0 completing verbs only.
  EXCEPTION — cmd_init (change-request 2026-06-12): init is NOT converged. It KEEPS its bespoke
  setup-flow next-step block (greenfield → run /add · brownfield → add.py lock). Converging it to
  the generic resolver would break test_brownfield_scan (frozen @ v1, pins that exact output) and
  regress onboarding — rule #3 forbids weakening that test. init still prints exactly ONE next:
  line (sweep-green) from its bespoke source; it sits with the heal paths as an EXCEPTION, not a
  generic-footer verb.

Schema: READS state.json (post-save) + MILESTONE.md/PROJECT.md (via report_data);
        WRITES nothing. engine_pin.ENGINE_MD5 re-aimed; add.py mirrored ×3 byte-identical.
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] command-OPTIONAL grammar — the milestone froze `next: <command> — <why>`; TWO
     reachable state-arm branches have no single command (`run in progress (<slug> at build)` and
     `resolve HARD-STOP on <slug>`), so the footer there is `next: <why>` (no command head). Both
     only ADD to a previously-silent verb (never regress). Cost if the human wants commands there:
     synthesizing them expands Arm B past the `_decide_next_base`-verbatim boundary — deferred.
  ⚠ [scenario] "every mutating verb" scope — lifecycle/setup verbs lock·stage·archive·compact get
     the generic state-arm footer, not bespoke per-verb lines. RESOLVED at contract v2: init is the
     EXCEPTION (keeps its bespoke setup-flow block — converging it breaks test_brownfield_scan v1,
     rule #3); init's goal-placeholder UX stays with the sibling ux-stale-followups. Widening the
     others to bespoke lines is a larger surface.

Status: FROZEN @ v2 — approved by Tin Dang 2026-06-12 (change-request: init → bespoke EXCEPTIONS, rule #3 vs test_brownfield_scan v1; supersedes v1, which listed init as converging — the build never converged init). v1 also approved 2026-06-12.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: hold the suite's current line; every scenario gets one render-blind test.
Plan (one test per scenario, asserting the printed line — never internals):
<test_plan>
  - test_advance_footer_is_phase_command: advance a front task / assert last line == "next: add.py advance — <why>" + result line intact
  - test_advance_into_verify_footer_is_gate: advance tests->verify / assert footer command is "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
  - test_gate_pass_routes_state_arm: gate PASS on A with B at contract / assert footer names B's contract approval + A "gate -> PASS" intact
  - test_gate_pass_all_done_consolidate: gate the last task / assert footer names "archive-milestone <ms>"
  - test_new_task_footer_replaces_tail_no_double: new-task / assert exactly one next-step line == "next: add.py advance — <ground why>" AND "then: add.py advance" absent
  - test_new_milestone_empty_names_command: new-milestone (empty) / assert footer == "next: decompose into tasks — add.py new-task <slug>" AND NOT "none — no tasks yet"  (the regression-fix pin)
  - test_gate_hardstop_routes_arm_b: gate HARD-STOP / assert footer == "next: resolve HARD-STOP on <slug>" (Arm B, NOT the verify gate command) + exactly one ^next: line + bespoke "HARD-STOP recorded…" line absent
  - test_failsoft_no_active_milestone: mutating verb with active_milestone=null / assert footer == "next: add.py status — re-orient" AND exit 0, state saved
  - test_every_mutating_verb_prints_one_next: drive each mutating verb in a representative state (compact↔archived ms · milestone-done↔all-done · etc.) / assert exactly one ^next: line each; the test enumerates the FULL mutating-verb list and fails loudly if any is left uncovered — never silently shrinks to the easy verbs (the exit-criterion sweep)
  - test_marker_slot_reserved: parse any footer / assert a trailing slot exists AND neither "you drive" nor "human gate" appears
  - test_mirrors_and_pin: the ×3 add.py copies are byte-identical AND md5 == engine_pin.ENGINE_MD5
  - test_pin_annotation_names_this_task: engine_pin.py annotation contains "re-aimed @ next-footer-engine"
</test_plan>

Tests live in: `add-method/tooling/test_next_footer_engine.py` · MUST run red (missing implementation) before Build.
Recorded red run (2026-06-12, `python3 -m unittest test_next_footer_engine`): 12 tests, 11 RED for the right reason
  — every mutating verb prints its result line with NO `next:` footer (use→bare result, new-task→old `then: add.py advance`,
  new-milestone→`Decompose…`), the sweep finds zero footers, and the pin annotation still names the prior task. 1 GREEN:
  test_mirrors_and_pin (the ×3 trio is in sync from scope-violation-heal — a discipline pin that must STAY green). No
  arrangement errored (each test reached its footer assertion), so the harness is sound.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_next_footer_engine.py` · `add-method/tooling/test_setup_lock.py`
Scope note (build-discovered, disclosed at the gate): `test_setup_lock.py` joined scope — `lock` gaining the footer (per §3) breaks its FROZEN single-line stdout assertion; the §0 GROUND anticipated "existing tests that assert a mutating verb's exact stdout may need the footer line added — sweep at tests". The co-update STRENGTHENS that test (it now pins the footer too), it does not weaken it (rule #3 holds). `lock` stays IN the footer — exempting it would instead break THIS task's own tamper-snapshotted sweep (lock ∈ COMPLETING_VERBS).
Strategy (ordered batches): 1. write `_next_footer(root, state)` (two arms + fail-soft) in canonical add.py 2. reshape the `_decide_next_base` empty-rows branch command-first 3. add `print(_next_footer(root, state))` to each mutating verb's tail, converging new-task/new-milestone/init's ad-hoc hints + gate's HARD-STOP terminal line 4. sync the ×3 add.py mirrors byte-identical 5. re-aim `engine_pin.ENGINE_MD5` + annotate `re-aimed @ next-footer-engine`
Safety rule (feature-specific): the footer is computed AFTER save_state and is fail-soft — a resolution error must be swallowed (verb exits 0, one generic line printed); the footer never writes state.
Code lives in: `add-method/tooling/add.py` (canonical) + its two mirrors.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only); the engine stays tool-agnostic (no git); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 909/909 on BOTH interpreters: py3.10 `Ran 909 in 871.119s → OK`, py3.14 `Ran 909 in 873.890s → OK` (post-fix full suites, 2026-06-12).
- [x] coverage did not decrease — held the suite line; ADDED test_next_footer_engine.py (12 tests) and STRENGTHENED test_setup_lock.py (now pins lock's two-line footer output).
- [x] no test or contract was altered during build — NUANCE (disclosed): the §3 contract WAS changed, but via a sanctioned CHANGE-REQUEST (reopened to contract, re-frozen @ v2 — init → bespoke EXCEPTIONS), NOT a build-time edit; test_setup_lock.py was STRENGTHENED (footer pinned), never weakened; the §4 red suite (test_next_footer_engine.py) is byte-unchanged (tamper-snapshot matches). Rule #3 holds — nothing was changed to force a failing build to pass.
- [x] the green was EARNED, not gamed — adversarial refute-read (2026-06-12) found no overfit / vacuous asserts / stubbed-away logic; every COMPLETING verb's footer is asserted on real printed stdout (render-blind), not internals. The one disclosed deviation (init bespoke vs §3 v1) was RESOLVED by the change-request, not papered over.
- [x] concurrency / timing of the risky operation is safe — N/A: `_next_footer` is a PURE render over already-committed state, computed AFTER save_state; the fail-soft arm swallows any resolution error so a saved mutation is never turned into a crash by its own footer.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; READS state.json + MILESTONE.md/PROJECT.md, WRITES nothing; the engine stays tool-agnostic (no git/network).
- [x] layering & dependencies follow CONVENTIONS.md — reuses the existing report precedence (`_decide_next_base`) as the SINGLE source; no parallel next-step logic introduced.
- [x] a person reviewed and approved the change — Tin Dang: approved the change-request direction, the §3 v2 freeze, and the PASS path (2026-06-12).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_next_footer(root, state)` is called by 13 mutating verbs (advance·gate·new-task·new-milestone·phase·use·reopen·set-milestone·milestone-done·lock·stage·archive-milestone·compact); the sweep `test_every_mutating_verb_prints_one_next` enumerates the FULL list and fails if any is uncovered. ×3 add.py mirrors byte-identical (md5 8a8967a151710f35dd9d3dea3ca86566 == engine_pin.ENGINE_MD5).
- [x] DEAD-CODE (code) — no orphaned symbol; the reshaped `_decide_next_base` empty-rows branch stays referenced by BOTH the report dashboard and Arm B (one precedence, no fork).
- [x] SEMANTIC (prose / non-code) — re-read §1/§2/§3 in full during the change-request; §3 v2 now matches the build (init bespoke) and §1/§2 are internally consistent (init absent from the convergence set; the [scenario] flag RESOLVED).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-12

Notes (dispositions disclosed at the gate):
  1. INIT deviation → RESOLVED by change-request. §3 v1 listed init among "converging" verbs, but converging init breaks test_brownfield_scan (frozen @ v1, pins init's greenfield/brownfield output) and regresses onboarding — rule #3 forbids weakening that test. Reopened to contract, re-froze §3 @ v2 (init → bespoke EXCEPTIONS, alongside the heal paths), human-approved 2026-06-12. The contract now MATCHES the build; no permanent carve-out, no §3 contradiction.
  2. LOCK footer co-update → STRENGTHENING. `lock` gained the footer per §3 convergence; since lock ∈ the tamper-snapshotted COMPLETING_VERBS sweep, exempting it would have broken THIS task's own sweep. test_setup_lock.py was co-updated to pin lock's two-line output (footer included) — a strengthening, disclosed in §5, never a weakening (rule #3 holds).
  3. SCOPE re-baseline → CLEAN. §5's declared scope froze (anchor in state.json) at the first tests→build with 5 files; the lock co-update (test_setup_lock.py) + self-inflicted .serena/cache drift (my own serena calls during build) fell outside the FROZEN anchor. Re-crossed tests→build (engine-sanctioned: "a legit change-request that re-crosses tests→build re-snapshots cleanly") to re-baseline the tripwire (new §3 v2 + the byte-unchanged red suite) and the scope (6 files + current tree). `add.py check` → 278 passed / 0 failed, zero scope warnings. §3 and the §4 red-suite bytes are unchanged across the re-cross.
  4. §0 ground-note reconciled — the ground-time pin guess 45254aa… was superseded by the final 8a8967a… (the actual ×3 md5); §0 corrected.
  5. NO security / concurrency / architecture residue → no HARD-STOP escalation; the auto-gate criteria were met and the human confirmed PASS.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the sweep `test_every_mutating_verb_prints_one_next` is the standing monitor — any NEW mutating verb that prints zero or two `next:` lines fails it loudly; the fail-soft test guards that a footer resolution error never crashes a saved mutation.
Spec delta for the next loop: the footer's trailing driver-marker slot is reserved for the SIBLING gate-owner-marker (next-step-seams 2/3 — fills ` [you drive]` | ` [human gate]`); init's goal-placeholder UX stays with ux-stale-followups (3/3).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a task's §3 verb-set can silently collide with a PRIOR task's frozen exact-stdout test, and the collision surfaces only at full-suite run — not at the contract freeze — forcing a change-request after build (evidence: converging init per §3 v1 would have failed test_brownfield_scan v1's pinned greenfield/brownfield output; caught only at the 909-test run, resolved by re-freezing §3 v2)
- [SDD · folded] "every mutating verb" over-reached as a contract phrase — it swept setup/lifecycle verbs (init) whose bespoke onboarding output must NOT converge; name the verb CLASS (workflow vs setup vs control), not "every" (evidence: §3 v2 carves init out as a setup-class EXCEPTION while keeping advance/gate/new-task/… in the workflow class)
- [TDD · folded] a sweep test that tamper-snapshots its own verb list (COMPLETING_VERBS) makes a late "exempt verb X" self-contradictory — X ∈ the frozen sweep still demands a next: line — so the exemption costs a contract change, not a quick carve-out (evidence: exempting lock would have broken test_next_footer_engine's own sweep; lock kept the footer and test_setup_lock was strengthened instead)
- [ADD · folded] the declared §5 scope is FROZEN into state.json's anchor at tests→build, so editing §5 prose alone cannot clear a scope violation — only a tests→build re-cross re-baselines it (evidence: add.py check held the scope_violation until reopen→contract→advance re-crossed; the gate reads anchor.declared, not live §5)
- [ADD · folded] an engine-pin re-aim must CARRY the immediately-prior task's "re-aimed @ <slug>" marker because that prior task's annotation test asserts it survives (evidence: test_scope_violation_heal::test_pin_annotation_names_this_task went red when the marker was overwritten; fixed by "supersedes re-aimed @ scope-violation-heal" in engine_pin.py)
