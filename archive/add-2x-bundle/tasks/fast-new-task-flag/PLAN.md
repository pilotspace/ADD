# TASK: new-task --fast + engine tolerance

slug: fast-new-task-flag · created: 2026-06-23 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add.py:cmd_new_task` (822 — render-call at ~879 picks the template name; record `fast` in state) · the `new-task` argparse parser (~5867 `pn` — add `--fast` flag) · `add.py:cmd_status` (optional `fast` lane marker on the active-task line). ×3 add.py trees byte-identical + engine_pin re-pin.
Context (working folder): builds directly on `fast-lane-template` (TASK.fast.md.tmpl + `_FALLBACK_TASK_FAST` already shipped); `test_fast_new_task_flag.py` lands in `add-method/tooling/`.
Honors (patterns / conventions): human opts in (`--fast` explicit, engine never guesses ceremony) · collapse-never-skip (the floor stays ENFORCED, not added — see Anchors) · additive flag (no existing new-task test enumerates the flag set, mirrors `--await-confirm`) · 3-tree parity.
Anchors the contract cites: `_render_template` (278 — already falls back for "TASK.fast.md") · `cmd_advance` freeze-before-build gate (the `_optin`/`raw3`/`contract_not_frozen` block at the `nxt == "build"` crossing, shipped by freeze-before-build-gate — its firing condition is what `--fast` extends with the fast arm) · `_contract_frozen`/`unflagged_freeze` (the existing flag check that fires only on an ALREADY-frozen §3 — which is WHY a DRAFT §3 needed the new freeze gate) · `_stamp_gate_record` (584 — stamps §6, present in the fast template) · `cmd_audit` `malformed_gate_record`/`gate_record_mismatch` (~5189 — stays clean on a fast task, no §2/§7 requirement).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py new-task <slug> --fast` — opt into the fast lane: scaffold the minimal TASK.fast.md template + record the task as fast, with the trust floor still ENFORCED by the existing freeze/gate chain.
Framings weighed: a `--fast` boolean flag on new-task that ALSO wires the task into the freeze-before-build gate (chosen — mirrors `--await-confirm`; renders the fast template + records a state marker + makes the freeze floor real for the fast lane via a one-arm extension `_optin OR fast`) · a `--fast` flag with NO new guard, floor left to the milestone opt-in (rejected at the v1→v2 re-freeze — leaves a hole: a fast task under a plain milestone reaches gate=PASS unfrozen) · a separate `fast-task` subcommand (rejected — duplicates new-task, inflates the census) · auto-detect "small" tasks (rejected — the engine never guesses ceremony; the human opts in)
Must:
<must>
  - `new-task <slug> --fast` renders via `_render_template("TASK.fast.md", …)` (not "TASK.md"), so the scaffolded TASK.md has sections {0,1,3,4,5,6} and a `fast: true` header
  - record `state["tasks"][slug]["fast"] = True` (the durable lane marker; ABSENT on a normal task — grandfathered, never retro-flagged)
  - WITHOUT `--fast`: new-task output + state + scaffold are BYTE-IDENTICAL to today (renders TASK.md, no `fast` key) — zero ripple to the existing new-task suites
  - the trust floor is made REAL for the fast lane: `--fast` extends the freeze-before-build gate's firing condition with a fast arm (`_gated := _optin OR state["tasks"][slug].get("fast") is True`), so a fast task cannot cross tests→build with a DRAFT §3 under ANY milestone (opted-in or not) and cannot reach verify/gate=PASS unfrozen; the §6 gate record is stamped by `_stamp_gate_record` (the fast template carries the block)
  - `check`/`audit` stay clean across a full fast-task lifecycle (no §2/§7 requirement — the minimal shape is tolerated)
  - `cmd_status` marks an ACTIVE fast task (a `fast` tag on the active-task line — presentation-only, existence-gated)
  - `--fast` composes with `--from-delta` (both pre-fill §1 `Feature:`, which the fast template has); 3 add.py trees byte-identical + engine_pin re-pinned
</must>
Reject:
<reject>
  - none NEW — `--fast` is additive; the existing guards apply unchanged: `task '<slug>' already exists` (no --force) · `setup_unlocked` (pre-lock 2nd task) · `milestone_unconfirmed` (opted-in parent). A bad flag value is impossible (boolean store_true).
</reject>
After:
<after>
  - a fast task exists with the minimal template + `fast: true` in state; advance→freeze→tests→build→gate runs the SAME guards as a normal task; `status` shows it is on the fast lane
  - a normal `new-task` (no flag) is provably unchanged (the existing suites stay green untouched)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ RESOLVED at the v1→v2 re-freeze: the v1 bet ("the floor needs NO new enforcement — it's already enforced unconditionally") was FALSE. The `unflagged_freeze` check only fires once §3 is ALREADY frozen (`if _contract_frozen(raw3):`), so a DRAFT-§3 task crossed tests→build to gate=PASS unrefused. The fix (human-chosen "fast implies floor"): wire `--fast` into the freeze-before-build gate so EVERY fast task is freeze-gated regardless of milestone opt-in — a small one-arm extension (`_optin OR fast`), zero-ripple (no existing task carries `fast: True`).
  - [ ] a `fast` state marker (vs reading the TASK.md `fast: true` header) is the right source — state is the engine's truth for status/audit; deny only if the header should be the single source.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: --fast scaffolds the minimal template + records the marker
  Given a locked project
  When I run new-task quick --fast
  Then tasks/quick/TASK.md parses to sections {0,1,3,4,5,6} with a "fast: true" header
  And state["tasks"]["quick"]["fast"] is True

Scenario: without --fast, new-task is byte-identical to today
  Given a locked project
  When I run new-task normal (no flag)
  Then tasks/normal/TASK.md is the full template (sections {0..7})
  And state["tasks"]["normal"] has no "fast" key

Scenario: the trust floor holds — a fast task under a PLAIN milestone is refused at tests→build with a DRAFT §3
  Given a fast task under a NON-opted-in (plain) milestone, advanced to tests, §3 Status still DRAFT
  When I run advance
  Then it dies "contract_not_frozen" (the freeze gate fires because the task is fast, even though the milestone did not opt in)
  And the task stays at tests (no bypass — collapse-never-skip is real for the fast lane itself)

Scenario: a fast task completes through the same gates
  Given a fast task with §3 FROZEN + a well-formed freeze flag and a red→green suite
  When I advance to verify and run gate PASS
  Then the task reaches gate=PASS
  And §6 GATE RECORD Outcome is stamped PASS
  And audit reports the task clean (no malformed_gate_record / gate_record_mismatch)

Scenario: status marks the active fast task
  Given a fast task is active
  When I run status
  Then the active-task line carries a "fast" marker
  And a non-fast active task shows no such marker

Scenario: --fast composes with --from-delta
  Given a prior task with an open SPEC delta
  When I run new-task next --fast --from-delta prior
  Then tasks/next/TASK.md is the minimal template
  And its §1 "Feature:" line is pre-filled from the prior delta
  And state["tasks"]["next"]["fast"] is True
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI   add.py new-task <slug> [--fast] [--from-delta P] [--match S] [--milestone M] [--force] [--title T]
        --fast : store_true, default False — opt into the fast lane

BEHAVIOR (the frozen seam):
  --fast TRUE  -> render via _render_template("TASK.fast.md", …)  [the minimal template,
                  sections {0,1,3,4,5,6}, "fast: true" header]
               -> state["tasks"][<slug>]["fast"] = True   [the durable lane marker]
  --fast FALSE -> render _render_template("TASK.md", …)  [the full template, {0..7}]
               -> NO "fast" key written  ==> output + scaffold + state BYTE-IDENTICAL to today
  composes: --fast + --from-delta both pre-fill §1 "Feature:" (the fast template has it);
            --fast honors --milestone / --force / --title unchanged

FLOOR (fast ⇒ enforced — a NEW guard arm in this task):
  the freeze-before-build gate (cmd_advance, `nxt == "build"`, shipped by freeze-before-build-gate)
  has its firing condition EXTENDED with a fast arm:
      _gated := _optin OR state["tasks"][slug].get("fast") is True
  so a fast task CANNOT cross tests->build with a DRAFT §3 under ANY milestone (opted-in or not) ->
  it cannot reach verify/gate=PASS unfrozen. "collapse-never-skip" is REAL for the fast lane ITSELF,
  not only for opted-in milestones. REJECT reused: contract_not_frozen (the same gate/code).
  The build-expectations gate stays opt-in-only (_optin) — a fast task pre-declares §6 only when its
  milestone opted in. The §6 GATE RECORD is stamped by _stamp_gate_record (the fast template carries it).
  (CORRECTION v1->v2: v1 wrongly claimed the floor was enforced "upstream, UNCONDITIONAL, no new
   guard" — false: the unflagged_freeze check only fires once §3 is ALREADY frozen, so a DRAFT-§3 task
   reached gate=PASS unrefused. The floor is now made real by wiring fast INTO the opt-in freeze gate.)

STATUS render:  an ACTIVE fast task's line carries a "fast" marker (presentation-only,
                existence-gated; a non-fast active task is unchanged).

AUDIT:  a fast task passes audit unchanged (no §2/§7 requirement; §6 GATE RECORD present).

REJECTS: none NEW. Existing guards apply verbatim — task-exists (no --force) · setup_unlocked ·
         milestone_unconfirmed. (--fast is a boolean; no value to reject.)
STATE schema: tasks[<slug>].fast : bool, OPTIONAL (absent == not-fast, grandfathered).
```

Least-sure flag surfaced at freeze: [contract] extending the freeze-before-build gate's firing to `_optin OR task.fast is True` is the new guard arm — the bet is zero-ripple, since no existing task carries `fast: True` (the marker is BORN in this task) so only the new fast-task tests exercise the arm; if wrong, an existing fast-marked fixture would break and the full suite is the backstop. A red scenario ("a fast task under a PLAIN milestone is refused at tests→build with a DRAFT §3") proves the floor before the freeze relies on it.

Status: FROZEN @ v2 — approved by Tin Dang
<!-- v1->v2 change-request (2026-06-23): v1's FLOOR claim ("enforced upstream, UNCONDITIONAL, no new
     guard") was factually wrong — a DRAFT-§3 task reached gate=PASS unrefused. v2: --fast wires the
     task INTO the freeze-before-build gate so a fast task is floor-enforced under ANY milestone
     (human-chosen "fast implies floor" at the re-freeze). -->
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the v2 fast-floor arm (8 behavioral tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fast_scaffolds_minimal_and_marks_state: new-task quick --fast / sections=={0,1,3,4,5,6} + "fast: true" header + state.fast is True
  - test_plain_new_task_unchanged: new-task normal / sections=={0..7} + no "fast" key (zero ripple)
  - test_fast_floor_holds_under_plain_milestone: fast task under a PLAIN milestone, DRAFT §3, advance tests→build / dies "contract_not_frozen" + stays tests (the v2 fast arm)
  - test_plain_task_not_freeze_gated: NON-fast task under the same plain milestone advances tests→build unfrozen (proves the arm is fast-scoped, not all-tasks)
  - test_fast_task_completes_through_gates: fast task frozen+flagged → advance to verify → gate PASS / gate==PASS + §6 Outcome stamped PASS
  - test_status_marks_active_fast_task / test_status_no_marker_for_plain_active_task: the active line carries " · fast" iff the active task is fast
  - test_fast_composes_with_from_delta: new-task next --fast --from-delta prior / minimal template + state.fast + §1 Feature pre-filled from the prior delta
</test_plan>

Tests live in: `add-method/tooling/test_fast_new_task_flag.py` · MUST run red (missing implementation) before Build.
RED confirmed (2026-06-23): with no `--fast` flag, the 5 fast-using tests errored at argparse (unknown `--fast`); the 3 non-fast tests passed. After the build all 8 are green; the full suite is 1628 green.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. add `--fast` to the new-task parser. 2. cmd_new_task: render TASK.fast.md + record `state["tasks"][slug]["fast"]=True` when fast. 3. cmd_advance: extend the freeze gate's firing to `_optin OR fast`. 4. cmd_status: ` · fast` marker on the active line. 5. copy canonical → 2 mirror trees (byte parity). 6. re-pin engine_pin.py.
Safety rule (feature-specific): no new IO/failure path — `--fast` is additive (a store_true + an optional state key + a conditional template name); WITHOUT it every path is byte-identical to today.
Code lives in: `add-method/tooling/add.py` (+ 2 mirror trees)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — test_fast_new_task_flag.py 8 green; full suite 1628 green
- [x] coverage did not decrease — +8 new behavioral tests; no test removed
- [x] no test or contract was altered during build — the §3 (v2) contract is byte-unchanged; no existing test edited (the v2 fast arm is fast-scoped, so no sibling fixture needed — unlike task 2)
- [x] the green was EARNED, not gamed — adversarial mutation refute-read: removing the fast arm (`_freeze_gated = _optin` only) breaks test_fast_floor_holds_under_plain_milestone; restoring returns to green. Tests assert observable behavior (section set, header text, state key, error code, phase, §6 stamp) not internals — not overfit
- [x] concurrency / timing of the risky operation is safe — pure synchronous; no IO/threads added. `--fast` is a store_true + an optional state key + a conditional template name
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reuses `_render_template`, the existing freeze gate, `tasks.get(...)`
- [x] layering & dependencies follow CONVENTIONS.md — additive flag mirrors `--await-confirm`; 3-tree byte parity held (md5 d4807ff9); engine_pin re-pinned + parity green (13 tests)
- [x] a person reviewed and approved the change — §3 FROZEN @ v2 approved by Tin Dang (the v1→v2 change-request was a human-chosen design fork: "fast implies floor"); verify auto-gated on complete evidence (no security/concurrency/architecture residue)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-task quick --fast` writes a TASK.md whose `## ` headings are exactly {0,1,3,4,5,6} with a `fast: true` header, and `state["tasks"]["quick"]["fast"]` is True — confirmed by test_fast_scaffolds_minimal_and_marks_state + a live `new-task --fast` (status shows ` · fast`)
- [x] a `--fast` task under a PLAIN milestone is refused `contract_not_frozen` at tests→build with a DRAFT §3, while a NON-fast task under the same milestone advances — confirmed by test_fast_floor_holds_under_plain_milestone + test_plain_task_not_freeze_gated + the mutation refute-read
- [x] `new-task` with NO flag is byte-identical to today (full template, no `fast` key) — confirmed by test_plain_new_task_unchanged + the unchanged full suite (no existing new-task test touched)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `fast` (cmd_new_task local) feeds both the template-name choice and the state-key write; `--fast` is registered on the `pn` parser; `_freeze_gated` consumes the fast marker in cmd_advance; `_fast_mark` is printed on the cmd_status active line — all four reference sites exercised by the suite
- [x] DEAD-CODE (code) — no orphaned symbol; the only new names (`fast`, `_freeze_gated`, `_fast_mark`) are all read in the same function they're bound
- [x] SEMANTIC (prose / non-code) — engine_pin annotation prepended (append-only); `add.py check` 391/0; the §3 v2 change-request + the v1-was-wrong correction are recorded in §1/§3 and the pin

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
