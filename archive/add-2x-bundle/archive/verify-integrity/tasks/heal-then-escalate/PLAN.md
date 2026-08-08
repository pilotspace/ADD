# TASK: Bounded self-heal then escalate: a confirmed cheat drives ≤3 honest re-build attempts, then HARD-STOPs to the human

slug: heal-then-escalate · created: 2026-06-11 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from the auto default: risk: high (engine change, the method's FIRST mechanical self-heal loop + pin bump) → a human must own this gate (unguarded_high_risk_auto). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_gate` (620–672) — records PASS/RISK-ACCEPTED/HARD-STOP. The `if completing:` block (634–653) calls `_tamper_guard(root, state, slug)` (653) BEFORE the gate write (667). THE mechanical seam: a cheat found here routes into the bounded loop instead of an immediate stop. HARD-STOP (non-completing) never reaches `_tamper_guard`, so the human can always stop directly.
  - `add-method/tooling/add.py:_tamper_guard` (1831–1853) — today `_die`s on `diffs` (1848–1853). REWIRE only the `if diffs:` branch → `_heal_or_escalate(root, state, slug, reason="tamper_detected:"+…, source="tamper")`. The `tripwire_missing` branch (1840–1845) STAYS an immediate `_die` — an erased baseline is not honestly healable.
  - `add-method/tooling/add.py:cmd_phase` (517–527) — UNGUARDED phase setter (`state[...]["phase"] = args.phase`, no human check). This is WHY `attempts` must be MONOTONIC: a reset on a tests→build re-cross would be clearable by `phase tests` + `advance` with zero human action → the cap becomes theater.
  - `add-method/tooling/add.py:cmd_advance` (530–566) — the `if nxt == "build":` block (548–561) re-snapshots the tripwire UNCONDITIONALLY. `_heal_or_escalate` must set `phase="build"` DIRECTLY (not via `advance`) so the baseline is NOT re-snapshotted mid-loop (a re-snapshot would launder the very tamper being healed).
  - `add-method/tooling/add.py:cmd_reopen` (675–711) — the append-only `reopens` history shape `{from,to,reason,at,prior_gate}` that `heal.history` mirrors. reopen requires `phase=="done"` (691), so it CANNOT reset a verify-phase HARD-STOP — the human's post-escalation path is a change-request (re-specify → re-freeze), a genuinely new contract.
  - `add-method/tooling/add.py:_die` (228–230) — prints `add: error:` + `raise SystemExit(code)` (default 1). The bounded RETURN-TO-BUILD is NOT an error; it exits with a distinct redo code (3 — avoids `_die`'s 1 and argparse's usage-2).
  - `add-method/tooling/add.py:_now` (122) · `save_state`/`load_state` (≈180–214) — iso timestamp for history; the attempt increment is `save_state`d BEFORE the `SystemExit` (one atomic write — a re-run must never grant a free attempt; CLAUDE.md design-for-failure).
  - `add-method/tooling/add.py:GATES` (39) — UNCHANGED. `heal` is a new SUBCOMMAND, not a 4th gate outcome (the PASS/RISK-ACCEPTED/HARD-STOP vocabulary is frozen — no silent skips).
  - `add-method/tooling/add.py` argparse block — `sub.add_parser("reopen", …)` (3132–3138). A new `heal` parser slots after it: `slug` (nargs="?") + `--reason` (validated in-body, non-empty), `set_defaults(func=cmd_heal)`.
  - `add-method/tooling/add.py:cmd_check` (≈999–1132) — the standing tripwire WARN (1080–1088). A non-done task mid-heal MAY surface `heal: N/3` as a never-red WARN (the gate is where the cap bites).
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` (`a6eed5e0c374694945cf4273d1a2581d`) — MUST bump (canonical add.py changes). Sync ×3 add.py trees; `test_shared_engine_pin.py::test_pin_matches_all_three_engines` auto-reds until synced + bumped.
  - `add-method/skill/add/run.md` (186 lines; §"The automated quality gate" 94–119, §"adversarial verify" 85) — THE HOME of the bounded self-heal loop prose (the build→verify run guide). ×3 skill trees.
  - `add-method/skill/add/phases/6-verify.md` + `5-build.md` — 6-verify POINTS to run.md's loop (it detects the cheat); 5-build notes the honest-redo re-entry. ×3 skill trees.
  - `add-method/docs/08-step-6-verify.md` (+ the book trees ×4) + `.add/GLOSSARY.md` / `GLOSSARY.md.tmpl` ×3 — the book reflects the loop; "bounded self-heal" gains the cap (3) + monotonic + escalation specifics.
  - `add-method/tooling/test_heal_then_escalate.py` (NEW) — the red guard, mirroring `test_tamper_tripwire.py`'s `_Board` CLI-integration harness (a real temp `.add/` project, `_run` captures SystemExit).
  - `add-method/tooling/test_earned_green_rubric.py:test_principle_no_loop_forward_ref` (179–185) — its premise (task-2-doesn't-pre-empt-task-3) is now FULFILLED. EVOLVE it to assert the loop's PRESENCE in run.md (coverage UP), documented — never a silent token-dodge.

Context (working folder):
  - docs — `.add/milestones/verify-integrity/MILESTONE.md` (the shared "Attempt-counter shape + cap (3) + escalation record" risky contract this task owns/freezes; the "bounded self-heal" + "a confirmed cheat is a HARD-STOP" shared decisions). Task 1 `tamper-tripwire` (the mechanical signal this loop consumes) + task 2 `earned-green-rubric` (the rubric whose refute-read feeds the semantic entry) — both done/PASS.
  - config/data — `.add/state.json` (the live per-task dict the `heal` counter persists into, beside `tripwire`/`flag_verified`/`waiver`/`reopens`).
  - no todos relevant.
Honors (patterns / conventions):
  - **engine pin ×3** — canonical add.py edit → `cp` ×2 mirrors → bump `engine_pin.ENGINE_MD5` → md5 parity (the release-gate idiom).
  - **fail-closed / atomic write** — the increment is durable BEFORE the exit; one `save_state` per call; an unreadable tracked file already counts as divergence (`_tripwire_divergence`).
  - **append-only history** — `heal.history` mirrors `reopens`: never mutate a prior entry; each cheat-arrival appends `{at,reason,source}`.
  - **a cheat is HARD-STOP-class** — never auto-passed, never RISK-ACCEPTED-launderable (the loop sits BEFORE the waiver write, inheriting the tamper-guard placement).
  - **reuse, never re-implement** — the loop consumes `_tripwire_divergence`; it does not re-detect tamper.
  - **the engine COUNTS + CAPS + ESCALATES; the AGENT re-builds** — the engine never auto-fixes a cheat (milestone out-of-scope).
Anchors the contract cites: `cmd_gate` `if completing:` / `_tamper_guard` (653, the mechanical entry) · `_heal_or_escalate` (NEW, the shared count/cap/route) · `cmd_heal` + the `heal` subparser (NEW, the semantic entry) · `state["tasks"][slug]["heal"]={attempts,history}` (the persisted shape) · `HEAL_CAP=3` · `cmd_phase` unguarded (why monotonic) · `cmd_advance` `if nxt=="build":` (the re-snapshot the loop must NOT trigger) · `_die`/SystemExit(3) (escalation vs redo codes) · `engine_pin.ENGINE_MD5` (the bump) · run.md (loop home) · `test_principle_no_loop_forward_ref` (the evolved guard) · `test_heal_then_escalate.py` (the new guard).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Bounded self-heal then escalate — a confirmed cheat loops back to build for an honest redo, capped at 3 attempts, then a forced HARD-STOP that escalates to the human.
Framings weighed: bounded-loop-in-the-engine (chosen — the engine COUNTS/CAPS/ESCALATES, the agent re-builds) · a 4th gate outcome `REDO` (rejected — pollutes the frozen PASS/RISK-ACCEPTED/HARD-STOP vocabulary) · engine auto-fixes the cheat (rejected — milestone out-of-scope; the engine never writes src).
Must:
<must>
  - A confirmed MECHANICAL cheat (tripwire divergence) at a COMPLETING gate, with attempts < 3, returns the task to build (phase→build) for an honest redo and records the attempt — it does NOT record PASS/RISK-ACCEPTED.
  - The agent may report a SEMANTIC cheat (the refute-read's overfit/vacuous/stub finding) via `add.py heal <slug> --reason "<finding>"`, which enters the SAME bounded loop.
  - The attempt counter is MONOTONIC per task — it never auto-resets (not on a tests→build re-cross, not on a phase move); only an honest build (no cheat) escapes the loop.
  - The 4th confirmed cheat (attempts already 3) forces a HARD-STOP that records `gate=HARD-STOP` and escalates to the human — never an auto-PASS, never an unbounded loop.
  - The attempt increment is persisted (save_state) BEFORE the process exits, so a re-run never grants a free attempt (atomic, fail-closed).
  - An HONEST build (clean tripwire, no reported cheat) PASSes normally even at attempts==3 — the cap bites only a CONTINUED cheat, never a recovery.
  - The bounded self-heal loop is documented: run.md (its home) carries it; 6-verify.md points to it; 5-build.md notes the honest re-entry; the glossary defines the cap + monotonic + escalation. ×3 skill / ×4 book synced.
  - The engine pin bumps (×3 add.py + engine_pin.ENGINE_MD5).
</must>
Reject:
<reject>
  - a completing gate (PASS/RISK-ACCEPTED) with a cheat present and attempts < 3 -> "return_to_build" (phase→build, redo signal, no completing outcome recorded)
  - a confirmed cheat with attempts already at the cap (the 4th) -> "heal_exhausted" (gate=HARD-STOP recorded, escalate to the human)
  - `add.py heal` with an empty/absent --reason -> "heal_reason_required" (never a silent loop)
  - `add.py heal` on a task not at the verify phase -> "heal_not_at_verify" (the refute-read is a verify-gate activity)
  - any path that would auto-reset attempts without a recorded human action -> REJECTED at design (monotonic; the freeze's least-sure flag)
</reject>
After:
<after>
  - state["tasks"][slug]["heal"] = {attempts:int, history:[{at,reason,source}]} reflects every cheat-arrival; attempts ≤ 3 while looping, the 4th sets gate=HARD-STOP.
  - A gamed green never reaches a completing outcome; an honest green still passes; the loop is bounded and every transition is recorded.
  - The engine pin matches across ×3 add.py trees; the loop is described identically across the synced surfaces.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] attempts is MONOTONIC (no auto-reset) — lowest confidence because a legit multi-change-request task keeps a "spent" counter; chosen because `cmd_phase` is UNGUARDED, so a reset-on-re-cross is a zero-human cap bypass (the cap would be theater). If wrong: a genuinely-re-specified task that then CHEATS again HARD-STOPs one attempt early — but an HONEST rebuild always passes (the cap bites only a continued cheat), so the practical cost is ~nil. Discriminator applied: "can the bound be cleared without a recorded human action?" → with monotonic, no.
  - [x] the semantic `heal` path is HONOR-SYSTEM (necessary-not-sufficient) — the engine cannot see overfit/vacuous/stub; only the mechanical tripwire has teeth; the human gate is the real backstop. Confirmed: matches task 1's own delta ("a tripwire in agent-writable state is necessary-not-sufficient") — stated plainly, never overclaimed.
  - [x] the redo signal exits 3 (distinct from `_die`'s 1 and argparse's usage-2) — confirmed harmless: the binding invariant is "PASS not recorded", not the code; a tool-agnostic orchestrator may branch on 3=redo vs 1=stop.
  - [x] the loop lives in run.md (not 6-verify.md) so `test_principle_no_loop_forward_ref` stays honest — confirmed: task 3 newly asserts the loop's PRESENCE (coverage up), the earned-green guard is re-scoped+documented, never a silent token-dodge.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: first mechanical cheat returns to build
  Given a task at verify whose tracked red test was gutted after the tests->build snapshot, attempts 0
  When the agent runs `gate PASS`
  Then the engine moves the task to phase build, records heal.attempts == 1, and exits non-zero (redo)
  And no completing outcome is recorded (gate stays "none")

Scenario: the cap holds — the 4th cheat HARD-STOPs
  Given the same gutted test, re-arriving at verify after attempts has reached 3
  When the agent runs `gate PASS`
  Then the engine records gate == "HARD-STOP" and escalates to the human (heal_exhausted)
  And it is never recorded as PASS

Scenario: an honest fix within budget passes
  Given a task that returned to build at attempts 1, whose test is then reverted to the snapshot baseline
  When the agent rebuilds, advances to verify, and runs `gate PASS`
  Then the engine records gate == "PASS" (no cheat -> the loop is never entered)
  And heal.attempts is unchanged (the counter only moves on a confirmed cheat)

Scenario: an honest build still passes at attempts 3
  Given a task at attempts 3 whose tamper is then fully reverted
  When the agent runs `gate PASS`
  Then the gate records PASS (the cap bites a continued cheat, never a recovery)
  And the task reaches phase done

Scenario: semantic cheat enters the same bounded loop
  Given a clean (untampered) task at verify whose refute-read found overfit logic
  When the agent runs `heal <slug> --reason "overfit: src special-cases the literal test inputs"`
  Then the engine moves to phase build, records attempts == 1 with source "refute-read"
  And no completing outcome is recorded

Scenario: heal requires a reason
  Given a task at verify
  When the agent runs `heal <slug>` with no --reason
  Then the engine refuses with "heal_reason_required"
  And attempts and phase are unchanged

Scenario: heal requires the verify phase
  Given a task at build (not verify)
  When the agent runs `heal <slug> --reason "x"`
  Then the engine refuses with "heal_not_at_verify"
  And attempts and phase are unchanged

Scenario: a cheat is not launderable through RISK-ACCEPTED
  Given a task with tripwire divergence at attempts 3
  When the agent runs `gate RISK-ACCEPTED --owner o --ticket t --expires 2099-01-01`
  Then the engine records gate == "HARD-STOP" (escalation), never RISK-ACCEPTED
  And no waiver is recorded

Scenario: the attempt is durable across a re-run
  Given a cheat that returned the task to build at attempts 1
  When the same gate command is re-run after the cheat re-arrives at verify
  Then attempts becomes 2 (the increment persisted) — a re-run never grants a free attempt
  And the counter is monotonic

Scenario: a monotonic counter is not reset by a tests->build re-cross
  Given a task whose attempts has reached 3
  When the agent runs `phase tests` then `advance` (re-cross tests->build) and re-arrives at verify with the cheat still present
  Then attempts is still >= 3 and the next confirmed cheat HARD-STOPs (the cap cannot be cleared without a recorded human action)
  And no completing outcome is recorded
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
heal-then-escalate — the bounded self-heal loop (engine + run.md prose)

STATE SHAPE  (state.json, per task, beside tripwire/flag_verified/waiver/reopens):
  tasks[slug]["heal"] = {
    "attempts": int,                       # MONOTONIC — never auto-resets
    "history":  [ {"at": iso, "reason": str, "source": "tamper" | "refute-read"} ]   # append-only
  }

CONSTANT:
  HEAL_CAP = 3                             # ≤3 honest re-build attempts; the 4th confirmed cheat HARD-STOPs

SHARED ROUTER  _heal_or_escalate(root, state, slug, *, reason, source) -> NoReturn:
  # called ONLY when a cheat is CONFIRMED at this point (divergence found, or a reason reported)
  attempts_now = heal.attempts (default 0)
  if attempts_now >= HEAL_CAP:            # the 4th arrival
      append history {at, reason, source}; state[gate] = "HARD-STOP"; save_state
      _die("heal_exhausted: a confirmed cheat persisted past 3 honest re-build attempts —
            HARD-STOP escalated to the human. Fix the spec (change-request -> re-freeze) or
            abandon; a gamed green is never auto-passed.", code=1)
  else:                                    # arrivals 1..3 -> return to build
      heal.attempts = attempts_now + 1; append history {at, reason, source}
      state[slug]["phase"] = "build"       # DIRECT — never via advance (no tripwire re-snapshot)
      _sync_task_marker(build); save_state  # the increment is durable BEFORE the exit
      print("return_to_build: cheat detected (<reason>) — RETURN TO BUILD for an HONEST redo,
             attempt <N> of 3. Revert the tampered file / de-overfit src, then advance back to verify.")
      raise SystemExit(3)                  # redo signal (distinct from _die's 1, argparse's 2);
                                           # the completing outcome is NOT recorded

ENTRY 1 — MECHANICAL (the only ENFORCED entry), inside _tamper_guard:
  on `diffs` (tripwire divergence)  ->  _heal_or_escalate(reason="tamper_detected:"+",".join(diffs), source="tamper")
  the `tripwire_missing` branch stays an immediate _die (an erased baseline is not honestly healable).
  _tamper_guard runs only on COMPLETING outcomes (PASS/RISK-ACCEPTED), BEFORE the waiver write —
  so a cheat is never RISK-ACCEPTED-launderable, and `gate HARD-STOP` is always allowed (never loops).

ENTRY 2 — SEMANTIC (HONOR-SYSTEM, necessary-not-sufficient), cmd_heal + `heal` subparser:
  `add.py heal <slug> --reason "<refute-read finding>"`
    reject heal_reason_required   if --reason is empty/absent
    reject heal_not_at_verify     if phase != "verify"
    else -> _heal_or_escalate(reason=<reason>, source="refute-read")
  The engine CANNOT detect overfit/vacuous/stub — this is the agent's honest report; the human gate
  stays the real backstop. (The refute-read recommendation lives in 6-verify.md; the engine never spawns it.)

"ATTEMPT" semantics:
  an attempt = a gate-arrival (or heal-report) with a cheat STILL present. The mechanical divergence
  PERSISTS across the loop unless the agent reverts; it is not a count of distinct honest fixes.
  An honest build (clean tripwire, no reported cheat) never calls _heal_or_escalate -> PASSes normally,
  even at attempts==3.

INVARIANTS:
  - a gamed green is NEVER auto-passed (a completing attempt with a cheat -> redo or HARD-STOP)
  - the loop is BOUNDED (≤3 returns-to-build, then a forced HARD-STOP escalation)
  - attempts is MONOTONIC (no auto-reset; cmd_phase is unguarded, so a reset would be a zero-human bypass)
  - scoped to CHEAT findings only (a general verify failure is NOT a heal trigger)
  - GATES vocabulary UNCHANGED (heal is a subcommand, not a 4th outcome)
  - engine pin BUMPS (×3 add.py + engine_pin.ENGINE_MD5)

KNOWN LIMITS:
  - the semantic path is honor-system (no mechanical teeth on overfit/vacuous/stub)
  - no auto-reset of attempts; the human's post-escalation path is a change-request (re-specify->re-freeze),
    not a reset (reopen requires `done`, which a verify-phase HARD-STOP is not)

PROSE SURFACES (the loop documented; ×3 skill / ×4 book):
  - run.md (HOME) — the bounded self-heal loop section
  - 6-verify.md — POINTS to run.md (it detects the cheat) ; 5-build.md — the honest-redo re-entry note
  - GLOSSARY "bounded self-heal" — gains cap (3) + monotonic + escalation
  - test_earned_green_rubric.py:test_principle_no_loop_forward_ref — re-scoped to assert the loop NOW
    lives in run.md (coverage up; documented evolution, never a silent weakening)
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-11.
Least-sure flag surfaced at freeze: [contract] `attempts` is MONOTONIC — no auto-reset on a tests→build re-cross or any phase move. Chosen because `cmd_phase` (517–527) is UNGUARDED: a reset-on-re-cross would let `phase tests` + `advance` clear the bound with zero human action, making the cap theater. Cost if wrong: a legitimately re-specified task keeps a spent counter — but since the cap bites only a CONTINUED cheat (an honest rebuild never calls the router), the practical cost is ~nil. Discriminator: "can the bound be cleared without a recorded human action?" → monotonic answers no.

<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject (the two entry points, the cap boundary, monotonicity, the honest-escape, the honor-system reason/phase guards). Engine behavior, not line %.
Plan (one test per scenario, asserting behavior not internals — each builds a temp `.add/` project via the `_Board` CLI harness, mirroring test_tamper_tripwire):
<test_plan>
  - test_first_mechanical_cheat_returns_to_build: gut a tracked test, gate PASS / assert phase==build, heal.attempts==1, gate=="none", exit!=0
  - test_fourth_cheat_hard_stops: drive 3 returns-to-build (cheat persists), 4th gate PASS / assert gate=="HARD-STOP" (heal_exhausted), never PASS
  - test_honest_fix_within_budget_passes: return-to-build at 1, revert the test, advance+gate PASS / assert gate=="PASS", attempts unchanged at 1
  - test_honest_build_passes_at_attempts_3: at attempts 3, fully revert, gate PASS / assert gate=="PASS", phase done
  - test_semantic_heal_enters_loop: clean task at verify, `heal --reason ...` / assert phase==build, attempts==1, history[-1].source=="refute-read"
  - test_heal_requires_reason: `heal` no --reason / assert heal_reason_required, attempts+phase unchanged
  - test_heal_requires_verify_phase: task at build, `heal --reason x` / assert heal_not_at_verify, unchanged
  - test_cheat_not_launderable_via_risk_accepted: divergence at attempts 3, gate RISK-ACCEPTED / assert gate=="HARD-STOP", no waiver
  - test_attempt_is_durable: cheat re-arrives, gate PASS twice across the loop / assert attempts increments 1->2 (persisted, no free attempt)
  - test_monotonic_no_reset_on_recross: at attempts 3, phase tests + advance (re-cross) + re-arrive, gate PASS / assert attempts>=3 and HARD-STOP (cap not cleared)
  - test_loop_documented_in_run_md: run.md names the bounded self-heal loop + the cap (3) + escalation (the prose presence guard; replaces the task-2 forward-ref absence)
</test_plan>
The ×3 add.py parity + the engine_pin.ENGINE_MD5 bump are NOT re-tested here — `test_shared_engine_pin.py::test_pin_matches_all_three_engines` auto-reds when canonical add.py changes without a synced ×3 + bumped pin.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- The actual engine suite runs from add-method/tooling/test_heal_then_escalate.py (the canonical
     unittest tree, _Board harness). Test files are NOT mirrored ×3 — only add.py / templates / skill / docs are.
     For THIS engine-dogfood task `./tests/` is intentionally empty (the real tests live in the canonical
     tree), so the tripwire snapshot protects this task's §3 contract only — necessary-not-sufficient,
     exactly as §1 states. -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the attempt increment is `save_state`d in ONE atomic write BEFORE the `SystemExit` — a re-run must never grant a free attempt. `_heal_or_escalate` sets `phase="build"` DIRECTLY (never via `advance`) so the tripwire baseline is not re-snapshotted mid-loop. Exit codes: 3 = redo (return-to-build), 1 = stop/escalation — grep the suite for any exit-code-specific assertions before finalizing (the binding invariant is "PASS not recorded", not the code).
Code lives in: engine `add-method/tooling/add.py` (×3 trees) + `engine_pin.py` (bump) + run.md/6-verify.md/5-build.md (×3) + book/glossary (×4) ; the canonical guard `add-method/tooling/test_heal_then_escalate.py`.
Constraints: do NOT change any test or the contract; do NOT touch the security HARD-STOP line or the autonomy model beyond adding the cheat-loop; keep tool-agnostic (the engine never runs tests, never spawns the refute-read); allow-list (stdlib only); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency; ×3 add.py byte-identical + pin bumped. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 839 OK (was 828 + the new 11 heal tests); the 11 ran RED before build (mechanical loop missing + `heal` unregistered + run.md prose absent) → GREEN after.
- [x] coverage did not decrease — +11 behavior tests. The build EDITED 3 EXISTING test files; each is an EVOLUTION tracking a LEGITIMATELY-changed behavior, coverage held or ROSE (disclosed below + independently confirmed by the refute-read):
      • `test_earned_green_rubric::test_engine_unchanged` — dropped the now-FALSE `assertNotIn("refute-read")` (the engine legitimately carries the frozen source LABEL); STRENGTHENED to guard 3 cheat tokens (overfit·vacuous·stubbed-away) + the refute-read PROMPT ("the green was NOT earned"). Coverage ↑.
      • `test_earned_green_rubric::test_principle_no_loop_forward_ref` → `test_loop_homed_in_run_md_verify_guide_points` — the task-2 absence-check's premise is FULFILLED (the loop landed); flipped to a PRESENCE/separation guard (loop in run.md + the verify guide points). Now guards run.md, which the absence-check never did. Coverage ↑.
      • `test_tamper_tripwire::_assert_blocked` — loosened `phase=="verify"` → `phase in ("verify","build")` (a first tamper now returns-to-build by design); kept `gate=="none"` STRICT (the real invariant — a tamper never completes). The new behavior is positively covered by `test_first_mechanical_cheat_returns_to_build` + `test_fourth_cheat_hard_stops`.
      • `test_min_pillar` — ADDED `heal` to the lifecycle coverage + a documented non-zero-exit tolerance (heal is a loop/refusal verb). Coverage ↑.
- [x] no test or contract was altered during build — the FROZEN §3 honored byte-for-byte; the §4 suite (`test_heal_then_escalate.py`) is the new red→green guard. The 3 EXISTING-test edits above are evolutions of OBSOLETE assertions (the behavior changed), NOT weakenings to force a pass — each leaves the real invariant guarded and coverage non-decreasing. NOT a frozen-contract edit.
- [x] the green was EARNED, not gamed — DOGFOODED task 2's own rubric on this task: an INDEPENDENT adversarial refute-read (fresh-context subagent) prompted to argue "the green was NOT earned" returned **EARNED** (EARNED-WITH-CAVEATS, zero HARD findings). It traced every state-touching path (monotonicity holds — no reset anywhere), verified the cap (`>= HEAL_CAP`), the durable-before-exit increment, and exact contract honor. Its ONE nit — a trivially-true `"3" in run_md` assert — was STRENGTHENED to `"3 honest"` BEFORE this gate (close-gap-before-gate). No overfit / vacuous / stub in the §4 suite.
- [x] concurrency / timing — the heal counter is ONE atomic `save_state` BEFORE the `SystemExit` (a re-run never grants a free attempt); `phase="build"` set DIRECTLY (no mid-loop tripwire re-snapshot); fail-closed (an unreadable tracked file already counts as divergence).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (no new dependency); the engine never runs tests and never spawns the refute-read (tool-agnostic — the agent reports a semantic cheat via `heal --reason`).
- [x] layering & dependencies follow CONVENTIONS.md — ×3 add.py byte-identical + `engine_pin` re-aimed (7b05eaf9); run.md/6-verify/5-build ×3, book 08/07 ×4, GLOSSARY.md.tmpl ×3 each ONE md5. The engine names the CHANNEL ("refute-read" source label) but NOT the rubric — overfit/vacuous/stubbed-away were SCRUBBED from the engine and are guarded out by the strengthened `test_engine_unchanged`.
- [x] a person reviewed and approved the change — **Tin Dang approved at the human verify gate (2026-06-11)**, accepting the 3 existing-test edits as evolutions (not weakenings) and the engine change as correct. (risk: high · autonomy: conservative → `unguarded_high_risk_auto` blocked any auto-completion; the engine's FIRST mechanical self-heal loop + a pin bump were human-owned, like task 1.)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_heal_or_escalate` is called by `_tamper_guard` (mechanical) + `cmd_heal` (semantic); `HEAL_CAP` is read in `_heal_or_escalate`; `cmd_heal` is wired to the `heal` subparser (`set_defaults`); all exercised by the 11 heal tests + the min_pillar lifecycle. Suite green confirms.
- [x] DEAD-CODE (code) — no orphan symbol; every new symbol (`HEAL_CAP`, `_heal_or_escalate`, `cmd_heal`, the `heal` parser) has a caller/registration.
- [x] SEMANTIC (prose / non-code) — read the loop prose in full across run.md (home) + 6-verify.md (pointer) + 5-build.md (honest-redo note) + the glossary term: confirmed the cap (3) + MONOTONIC + escalation + the honor-system caveat are stated, and that 6-verify points to run.md without duplicating the machinery.

### GATE RECORD
Outcome: PASS — human-gated (risk: high / conservative). The bounded self-heal loop is built and green (839 OK); a confirmed cheat returns-to-build monotonically ≤3 then HARD-STOPs. The 3 existing-test edits were accepted as evolutions (real invariant still guarded, coverage non-decreasing), and the independent adversarial refute-read returned EARNED (zero hard findings).
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): heal-attempt rate per task (how often a build trips the tripwire or self-reports a cheat) and the escalation rate (heals that exhaust the cap → HARD-STOP). A rising escalation rate is the signal that the spec/contract is mis-fitting the build, not that the loop is broken.
Spec delta for the next loop: the SEMANTIC channel is honor-system — the engine records a `heal --reason` but cannot prove an adversarial refute-read actually ran (tool-agnostic by design). A future production milestone could require a recorded refute-read artifact (verdict + reasoning) before `heal --reason` is accepted, lifting the semantic entry from honor-system toward enforced — without the engine ever spawning the read itself.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] when an engine change legitimately invalidates an EXISTING assertion, the test edit is an EVOLUTION (not a weakening) iff three hold: the real invariant stays guarded, coverage holds-or-rises, and the reason is documented — a reusable discriminator for "is this green earned?" (evidence: 3 existing tests edited under this rule — `_assert_blocked` kept `gate=="none"` strict while loosening phase, `test_engine_unchanged` went 1→3 cheat tokens, `test_min_pillar` added `heal` coverage — and the independent refute-read returned EARNED)
- [ADD · folded] a self-heal cap is only real if it cannot be cleared without a RECORDED HUMAN ACTION — an unguarded reset (e.g. on tests→build re-cross via the open `cmd_phase`) is a trivial bypass; the safe default is MONOTONIC (never auto-reset) (evidence: the advisor BLOCKED reset-on-recross as a cap bypass; froze monotonic, proven by `test_attempts_are_monotonic`)
- [ADD · folded] a confirmed-cheat self-heal is HARD-STOP-class, not RISK-ACCEPTED-class — it returns-to-build for an honest redo and escalates at the cap, but a gamed green is NEVER waived through, exactly like a security finding (evidence: `_heal_or_escalate` records `gate="HARD-STOP"` at exhaustion with no RISK-ACCEPTED branch; `test_fourth_cheat_hard_stops`)
- [ADD · folded] a method can audit its OWN builds — dogfooding task 2's earned-green rubric on task 3's build (a fresh adversarial subagent) caught a real nit before the gate, proving the rubric bites on the method's own work, not just user features (evidence: refute-read flagged the trivially-true `"3" in run_md` assert → strengthened to `"3 honest"` before the gate)
- [SDD · folded] an anchor-PRESENCE test proves a phrase EXISTS, not that two surfaces AGREE on its qualifier — cross-surface contracts need an agreement check, not just a presence check (evidence: task 2's template/guide drift — both carried the earned-green line but disagreed on its qualifier — slipped every presence test; caught only by manual read)
