# TASK: Opt-in compound ticks: freeze --cross + gate accepted from build

slug: compound-ticks · created: 2026-07-13 · stage: mvp
milestone: call-floor
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: compound ticks — the oneshot lane's 8-9 calls include two PURE ticks with no work between (freeze->tests · build->verify->gate); OPT-IN flags compress them, defaults stay byte-identical (3488+ fixtures pin the sequences)
Must:
  - `freeze --by X --cross`: after a successful stamp at the plan phase, the task lands in tests (state first, marker synced, one `crossed into tests` line); the bare freeze is byte-identical
  - `gate PASS|RISK-ACCEPTED` at the BUILD phase auto-crosses build->verify (state+marker) then records — the same completion checks run; phases before build keep the existing refusal codes verbatim
  - the new-task recipe advertises the compressed lane (freeze --by <name> --cross · gate PASS from build); test_kickoff_truth's >=3-advance pin updates to the new truth (doc-truth ripple, flow-honesty precedent) and gains a --cross mark
Reject:
  - `--cross` when the freeze did not stamp (already frozen / refused) -> no crossing, the existing output unchanged
  - `--cross` at a non-plan phase -> advisory note `--cross: only a plan-phase freeze crosses`, no phase change
  - gate at specify/scenarios/plan/tests -> the existing gate_pass_before_verify / gate_risk_accepted_before_verify refusals, byte-identical
Accept: Given a frozen oneshot task built to green at the build phase, When `gate PASS` runs, Then the task crosses to verify and records PASS in one call; and Given a drafted plan, When `freeze --by X --cross` runs, Then the task is FROZEN and at the tests phase in one call.
Boundary: two flag dialects — the crossing freeze (plan) and the non-plan no-op note; gate from build vs gate from earlier phases (refused)
Assumptions: ⚠ some suite pins the exact gate refusal for phase==build — why: the refusal text embeds the phase name; if wrong: the fence names it and the pin updates to the new truth (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:cmd_freeze (post-stamp tail) · add.py:cmd_gate (the completing-phase guard, ~2120) · add.py:cmd_new_task recipe block (~888) · freeze argparse (~8340) · add-method/tooling/test_kickoff_truth.py:RecipeTest (pin update, declared)
Context (working folder): ENGINE_MD5 re-aims; SEAMS pin drifts (insertions above 5595) — re-pin
Honors (patterns / conventions): state-first then marker (_sync_task_marker, cmd_phase precedent) · defaults byte-identical · refusal codes verbatim · flow-honesty: guard tests pinning old doc update WITH the doc
Anchors the contract cites: cmd_freeze · cmd_gate · cmd_new_task · _sync_task_marker
Ground SHA: a2df502 — stamped by freeze

### Contract

```
freeze parser: pfz.add_argument("--cross", action="store_true", ...)
cmd_freeze tail (after save_state + froze-print + echo, before footer):
    if getattr(args, "cross", False):
        if state phase == "plan": phase -> "tests" (save_state, _sync_task_marker),
            print("crossed into tests — write one failing test per scenario")
        else: print("--cross: only a plan-phase freeze crosses (no-op)")
    (the already-frozen no-op path returns BEFORE this — no crossing)
cmd_gate completing guard:
    current == "build" -> phase -> "verify" (save_state, _sync_task_marker),
        print(f"crossed build -> verify (compound tick)"), then the normal flow
    _phase_index(current) < build -> existing refusals byte-identical
recipe block:
    add.py advance --to plan / add.py freeze --by <name> --cross [human gate; lands in tests]
    / add.py advance (tests -> build after the RED suite) / add.py gate PASS (from build)
test_kickoff_truth.RecipeTest: >=2 advances + "--cross" mark (was >=3)
```

`Least-sure flag surfaced at freeze:` [contract] gate-from-build skips any advance-time build->verify guard — why: grounded cmd_phase verify as the no-guard precedent, but cmd_advance may run extra checks there; if wrong: re-route the auto-cross through the same helper (cost: one re-run)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/../.add/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red tests -> freeze --cross -> gate-from-build -> recipe + RecipeTest pin -> sync x3 + re-pins. Traps: cmd_advance build->verify guard check FIRST (the flag above); defaults byte-identical; never sync tests.
Approach (domain strategy): opt-in compression, state-first writes, refusals untouched

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (cmd_freeze/cmd_gate/recipe/argparse read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced and substantive (build->verify advance-guard question)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T16:55:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_freeze_cross_lands_in_tests · test_bare_freeze_unchanged (no --cross -> plan phase, byte-identical output tail) · test_cross_nonplan_noop · test_gate_pass_from_build (one call: crossed + PASS) · test_gate_refused_before_build (tests phase -> existing code) · test_recipe_advertises_cross.
Tests live in: `add-method/tooling/test_compound_ticks.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `freeze --by X --cross` on a plan-phase draft stamps FROZEN and lands the task in tests in one call; `gate PASS` at build crosses to verify and records in one call; the bare freeze / earlier-phase gate refusals are byte-identical — confirmed by test_compound_ticks.py (7 tests: cross-lands · bare-unchanged · refused-freeze-no-cross · non-plan-note · gate-from-build · gate-refused-at-tests · recipe) RED 6/7 pre-build then green, test_kickoff_truth RecipeTest updated to the new recipe truth (declared in-scope doc-truth ripple), full fence 3503/3503 OK exit 0 (log: scratchpad/fence-compound-ticks.log), engine synced x3, ENGINE_MD5 re-aimed 26f78f04, SEAMS _declared_scope pin 5595->5619. THIS GATE itself runs from the build phase — the feature proves itself on its own task.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

