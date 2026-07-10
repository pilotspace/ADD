# TASK: add.py advance auto-walks consecutive AI-owned phases in one round-trip, halting at contract-freeze and verify-gate

slug: advance-chain-collapse · created: 2026-07-09 · stage: mvp
milestone: risk-proportional-ceremony
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/add.py:_next_footer(root, state) -> str` — the SINGLE engine-sourced `next:` line every completing mutating verb prints last (add.py:5993). For an in-flight task (gate=="none", phase!="done") it emits, per phase: drafting phases (ground/specify/scenarios/contract/tests) → `"add.py advance --fill <draft>"`; verify → `"add.py gate PASS | RISK-ACCEPTED | HARD-STOP"`; else → `"add.py advance"`. THIS is the lever — it teaches single-step advance, never the collapsed bundle form. · `add.py:cmd_advance` (add.py:1259) — ALREADY implements `--to <phase>` bundle fast-forward: repeats the single-step advance running every crossing guard per step, refuses `advance_to_stops_at_tests` for any target past `tests` (the tests→build crossing carries `_build_entry`'s gate stack), `advance_to_not_forward` if not forward, and `fill_with_to_unsupported` (--to and --fill are mutually exclusive). · `PHASES = ('ground','specify','scenarios','contract','tests','build','verify','observe','done')`; `_FRONT_PHASES = ('specify','scenarios','contract','tests')` (add.py:5708).
Context (working folder): live baseline transcript `scratchpad/baseline-runs/add/wm1/transcript.jsonl` (fixed-harness add WM1, 2026-07-09) — the evidence this task attacks. Milestone doc `.add/milestones/risk-proportional-ceremony/MILESTONE.md`.
Honors (patterns / conventions): `_next_footer` is a PURE render (writes nothing), computed AFTER save_state, fail-soft (any resolution error degrades to `"next: add.py status — re-orient"`, never crashes the saved mutation). It reuses the guide path — ONE next-step source, never a parallel one. Any change must keep it pure + fail-soft. 3-tree byte-parity (canonical/.add dogfood/_bundled) + ENGINE_MD5 pin bind every edit.
Seams consulted: the `next:` footer is the documented single next-step channel (`next-footer-engine`); the batch-op hint convention already lives here (add.py:6020 — "drafting phases teach the batch form at the moment of use … the footer is read every turn").
Anchors the contract cites: `_next_footer`, `cmd_advance` (`--to` semantics), `PHASES`, `_FRONT_PHASES`.
Issues/Risks (→ feed §1): (1) `--to` cannot combine with `--fill` (`fill_with_to_unsupported`) — the collapsed form assumes the agent has PRE-WRITTEN §0–§3 (the live run did exactly this: bare `advance` after Edit, never `--fill`), so the footer must recommend the collapse in a way that doesn't imply --fill. (2) `--to` fast-forwards MECHANICALLY through front crossings (no per-section content gate on the drafting crossings; quality is gated at the human freeze + AI-verify checklist, not at advance) — so `advance --to contract` is mechanically safe on empty sections but the agent must fill first; the footer wording must not imply the engine validates fill. (3) The footer is emitted at EVERY completing verb — changing its text ripples into any test asserting the exact `next:` string (grep the guard tests). (4) Must NOT recommend crossing past the freeze/gate stop — the collapse target is `contract` (last AI-owned drafting phase before the freeze gate), never `build`/`verify`.
Related intent: MILESTONE `risk-proportional-ceremony` goal (cut turn-count by collapsing MECHANICAL round-trips, floor invariant). PROJECT.md: "ship ADD as a lean … method … no lost context across sessions." The measured driver: 7 bare `advance` + 7 `--help` + status×4/guide×2 = the agent single-steps and spelunks because the footer never hands it the collapsed command.
Ground SHA: 94486bb

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the `next:` footer teaches the COLLAPSED bundle-advance — at a front drafting phase it hands the agent `add.py advance --to contract` (cross the whole AI-owned drafting span in ONE round-trip to the freeze point), instead of the single-step `advance --fill <draft>` that made the live run spend 7 separate advance turns.
Framings weighed: enrich `_next_footer` to emit the `--to contract` collapse hint for front phases (chosen — pure-render change, reuses the already-shipped `--to` engine capability, zero control-flow risk, backward-compatible) · change bare `advance` to auto-chain by default (rejected — flips behavior for ~3k single-step tests + duplicates `--to`) · add a new `advance --auto` flag (rejected — new surface the agent still wouldn't discover; the footer is the read-every-turn channel).
Must:
<must>
  - M1 when the active in-flight task's phase ∈ {ground, specify, scenarios} → the footer's recommended command is `add.py advance --to contract` (the collapsed span reaching the last AI-owned drafting phase before the freeze gate).
  - M2 the footer STILL surfaces the single-step `--fill <draft>` form as the granular alternative on the same line — the collapse is the lean default, not a removal (a section-by-section drafter is never stranded).
  - M3 when phase == contract → the footer names the FREEZE action (`add.py freeze`), never another advance/`--to` — the agent is already AT the collapse target; the next real step is the human/proxy freeze gate.
  - M4 the footer NEVER recommends a `--to` target past `contract` (never past the freeze gate; never `tests`/`build`/`verify`) — the collapse stops exactly where a decision point begins.
  - M5 `_next_footer` stays PURE (writes nothing) and fail-soft (any resolution error still degrades to `next: add.py status — re-orient`, never crashing the already-saved mutation); the `[you drive]`/`[human gate]` marker logic is unchanged.
</must>
Reject:
<reject>
  - R1 no active in-flight task (Arm B: milestone rollup / done / HARD-STOP) -> the collapse hint is NOT emitted; the existing `_decide_next_pair` / fail-soft text stands unchanged -> "no_inflight_no_collapse" (behavioral: no front-phase hint outside Arm A).
  - R2 a resolution error mid-render (unreadable state, missing phase) -> the generic `next: add.py status — re-orient` line, no marker -> "footer_failsoft" (never a crash, never a half-built collapse hint).
</reject>
After:
<after>
  - a completing mutating verb at a front drafting phase prints a `next:` line whose command is `add.py advance --to contract` (plus the `--fill` alt), so the agent bundle-advances the drafting span in one call.
  - at contract phase the printed `next:` names the freeze gate; no footer ever names a `--to` past `contract`.
  - `_next_footer` purity + fail-soft + driver-marker behavior are byte-unchanged except the recommended-command text.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that the agent, handed `advance --to contract`, PRE-DRAFTS §0–§3 before running it (—`--to` can't combine with `--fill`, so the collapse only pays off if sections are written first) — lowest confidence because it depends on agent behavior, not engine enforcement; if wrong: the agent runs `--to contract` on empty sections, crosses to contract with stub content, and the freeze/AI-verify gate catches the thinness (a re-cross, not a floor breach) — so fail-safe, cost = one wasted crossing, not a bad build. Mitigation: the footer wording pairs the collapse with "draft §0–§3 first".
  - [ ] that no existing test pins the exact current `next:` string for a front drafting phase (would break on the text change) — confirm by grepping the guard/footer tests before build; if pinned, update those asserts in the TESTS phase (tamper-safe: test edits belong in §4, not build).
  - [ ] that `contract`-phase footer currently emitting `advance --fill <draft>` (contract is in the drafting tuple at add.py:6025) is safe to repoint to the freeze action without breaking the freeze→advance flow — confirm the freeze verb is the correct next action at contract (it is: freeze then advance to tests).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: front phase teaches the collapse   # M1
  Given an active in-flight task at phase ground (or specify/scenarios)
  When a completing mutating verb prints its next: footer
  Then the footer's recommended command is "add.py advance --to contract"
  And the footer still starts with "next: add.py advance" (existing prefix asserts hold)

Scenario: the single-step form stays discoverable   # M2
  Given an active in-flight task at phase ground/specify/scenarios
  When the next: footer renders
  Then the same line still contains "add.py advance --fill <draft>" as the granular alternative

Scenario: at contract the footer names the freeze gate   # M3
  Given an active in-flight task at phase contract
  When the next: footer renders
  Then the recommended command names "add.py freeze" (the human/proxy freeze gate)
  And the footer does NOT recommend another advance or a "--to" command

Scenario: the collapse never crosses a gate   # M4
  Given an active in-flight task at any front phase
  When the next: footer renders
  Then no printed "--to" target is past "contract" (never tests/build/verify)

Scenario: purity + fail-soft preserved   # M5
  Given _next_footer is called on any state
  When it renders (or hits a resolution error)
  Then it writes nothing to disk
  And on error it returns exactly "next: add.py status — re-orient" (no marker), never raising

Scenario: no in-flight task -> no collapse hint   # R1
  Given no active in-flight task (a gated/done task, or an empty milestone)
  When the next: footer renders
  Then the collapse hint is absent and the existing Arm-B / rollup text is byte-unchanged
  And the driver marker still reflects the rollup's own human_stop

Scenario: resolution error degrades safely   # R2
  Given _next_footer hits an internal error mid-resolution
  When it returns
  Then the output is exactly "next: add.py status — re-orient"
  And no partial collapse hint and no marker are emitted
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_next_footer(root: Path, state: dict) -> str      (add-method/tooling/add.py:5993)
  # signature UNCHANGED · PURE (writes nothing) · fail-soft (never raises)

Arm A  (active in-flight task: gate=="none" AND phase!="done") — recommended command by phase:
  ground | specify | scenarios
     -> f"next: add.py advance --to contract (or --fill <draft> per section) — {why}{marker}"
        # MUST contain BOTH "add.py advance --to contract"  AND  "add.py advance --fill <draft>"
  contract
     -> f"next: add.py freeze — {why}{marker}"
        # names the freeze gate; MUST NOT contain "advance" or "--to"
  tests
     -> f"next: add.py advance --fill <draft> — {why}{marker}"      # UNCHANGED
  verify
     -> f"next: add.py gate PASS | RISK-ACCEPTED | HARD-STOP — {why}{marker}"   # UNCHANGED
  build | observe (else)
     -> f"next: add.py advance — {why}{marker}"                     # UNCHANGED
  INVARIANT: no Arm-A command string names a "--to" target past "contract".

Arm B  (no in-flight task) AND fail-soft path: BYTE-UNCHANGED from today
  # rollup via _decide_next_pair(...) + _driver_marker(human_stop)
  # any resolution error -> exactly "next: add.py status — re-orient"  (no marker)

  where  why    = PHASE_GUIDE[phase][0].split(" — ")[0].strip()      (unchanged)
         marker = _driver_marker(_driver_stop(root, state, slug, phase))   (unchanged)
```

Glossary deltas: collapse-hint: the front-phase `next:` footer form that recommends the bundled `advance --to contract` (crossing ground→contract in one round-trip) while still naming the per-section `--fill` alternative — the lean default the agent reads every turn.
Least-sure flag surfaced at freeze: [spec] the collapse pays off ONLY if the agent pre-drafts §0–§3 before running `advance --to contract` (`--to` can't combine with `--fill`); this is agent behavior, not engine-enforced. If wrong, the agent crosses to contract on stub sections and the freeze + AI-verify gate catches the thinness (a re-cross, fail-safe) — never a floor breach. Mitigated by the paired "or --fill <draft> per section" wording in the emitted hint.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §1 Must + Reject has a render-blind footer assertion (behavior, not internals).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ground_footer_teaches_collapse: fresh task @ ground / read footer / assert contains "add.py advance --to contract" AND "add.py advance --fill <draft>" · covers: M1, M2
  - test_specify_footer_teaches_collapse: advance→specify / footer / same two tokens · covers: M1, M2
  - test_scenarios_footer_teaches_collapse: advance→scenarios / footer / "add.py advance --to contract" · covers: M1
  - test_contract_footer_points_at_freeze: advance→contract / footer / assert "add.py freeze" present, "advance"/"--to" ABSENT · covers: M3
  - test_no_front_footer_names_a_to_past_contract: walk ground→contract / assert no footer names "--to tests|build|verify|observe|done" · covers: M4
  - test_failsoft_and_pure: call _next_footer("/nonexistent", {}) / assert == "next: add.py status — re-orient" AND no files written · covers: M5, R2
  - test_done_task_has_no_collapse_hint: arm+gate PASS (done) / footer / assert no "advance --to contract" (Arm B) · covers: R1
  - test_hint_batch_ops.test_walk_phases_fill_then_bare (UPDATED): contract-phase expectation flipped from --fill to freeze; ground/specify/scenarios now also require --to contract; source-branch anchor moved to `elif phase == "tests"` · covers: M1/M2/M3 via the existing walk
</test_plan>

Tests live in: `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_hint_batch_ops.py` · ran RED (4 collapse-hint + 1 walk fail; missing collapse-hint + contract→freeze) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_hint_batch_ops.py`
Strategy (ordered batches): 1. edit `_next_footer` Arm-A branch in canonical `add-method/tooling/add.py` — split the front-drafting elif so {ground,specify,scenarios} emit the `--to contract (or --fill <draft> per section)` collapse-hint and `contract` emits `add.py freeze`; keep tests/verify/build/observe branches byte-identical. 2. sync the two twins (`prepare_bundle.py` / copy) so all 3 add.py are byte-identical. 3. re-pin ENGINE_MD5 = md5(add.py) across the 3 engine_pin.py (via `engine_manifest.py`), rm every `__pycache__` first. 4. run parity + footer suites green.
Approach (domain strategy): a pure-render string change in the one next-step composer — no control-flow, no new flag, no engine capability added; reuse the already-shipped `--to` bundle-advance. Deterministic, fail-loud, backward-compatible (the methodology-engine-dev stance).
Data strategy: no data-shape change — `_next_footer` returns the same `str`; only the recommended-command substring per front phase changes. The 3-tree byte-parity + ENGINE_MD5 pin are the invariant the change must re-satisfy.
Pattern: extends the existing "footer teaches the batch form at the moment of use" convention (add.py:6020) — this task makes the taught form the COLLAPSED one.
Optimization stance: token-cost (turn-count) is the optimization — fewer engine round-trips per feature; budget = beat the 63-turn/$3.99 baseline. ⚠ least-trusted facet: whether the agent actually pre-drafts before running `--to contract` (behavioral, not enforced) — mitigated by the paired "or --fill <draft> per section" wording. correctness-first otherwise.

Persona (required): methodology-engine-dev — builds the engine that drives builds; deterministic, fail-loud, no lost context.
Spawn isolation (default): none — single-author pure-render edit + mechanical twin sync; no parallel subagent build, so no worktree needed.
Known-problem fixes: (a) 3-tree drift → run prepare_bundle + repin + rm __pycache__ before any parity check (memory lesson). (b) `test_hint_batch_ops` pins `--fill` for ALL 5 front phases + the source `elif ("ground",…,"tests")` split → update the contract-phase expectation to `add.py freeze` and the source-branch anchor IN THE §4 TESTS PHASE (never during build — tamper tripwire). (c) footer text ripples → run the full add.py suite red-first to enumerate every pinned-string breakage, not just the two known files.
Strategy actually used: as planned — split the `_next_footer` Arm-A elif into `{ground,specify,scenarios}`→`"add.py advance --to contract   (or step-by-step: add.py advance --fill <draft>)"`, `contract`→`"add.py freeze"`, `elif phase == "tests"`→`"add.py advance --fill <draft>"`, else→bare advance (verify/build/observe byte-unchanged). Twin sync: prepare_bundle.py (canonical→_bundled) + `cp` canonical→.add dogfood; NOTE prepare_bundle DELETES the bundled `engine_pin.py` (it copies add.py+add_engine+templates only) → git-restored it, then hand-repinned ENGINE_MD5=6bb8630… across all 3 pin copies (identical), rm __pycache__ first. Live smoke + 727/0 check + 93 targeted tests green.
Safety rule (feature-specific): the collapse target is hard-capped at `contract`; no branch emits a `--to` past the freeze gate — the floor stop-point is encoded in the per-phase map, not left to the caller.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full add.py suite 3334 passed + 162 subtests, 0 fail (285s); 93 targeted footer/parity/pin tests green; `add.py check` 727/0
- [x] coverage did not decrease — added 7 new footer tests + tightened the walk test; no test removed
- [x] no test or contract was altered during build — the 2 test files were edited in the TESTS phase (red-first); build touched only add.py + engine_pin twins
- [x] the green was EARNED, not gamed — refute-read EARNED (render-blind CLI asserts + independent live smoke; RED→GREEN confirmed)
- [x] concurrency / timing of the risky operation is safe — pure function, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — static-string render, no IO/eval; stdlib-only
- [x] layering & dependencies follow CONVENTIONS.md — reuses the single next-step channel; 3-tree byte-parity + pin re-satisfied
- [x] a person reviewed and approved the change — Tin Dang approved the freeze (the one human decision); auto-gated on complete evidence (autonomy: auto, no security/concurrency/architecture residue)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] at ground/specify/scenarios, a completing verb's `next:` line reads `add.py advance --to contract` AND still names `add.py advance --fill <draft>` — CONFIRMED by live smoke (all 3 printed both tokens)
- [x] at contract, the `next:` line names `add.py freeze` with no `advance`/`--to` — CONFIRMED by live smoke (`next: add.py freeze — freeze the shape [human gate]`)
- [x] tests/verify/build/observe footers + Arm B + fail-soft are byte-unchanged — CONFIRMED by the full `test_next_footer_engine` + `test_hint_batch_ops` suites green (incl. Arm-B + fail-soft + sweep)
- [x] the 3 add.py twins are byte-identical and `engine_pin.ENGINE_MD5` matches — CONFIRMED by `EnginePinTest.test_mirrors_and_pin` green + md5 trio 6bb8630…

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the changed branch is inside `_next_footer`, already called by every completing verb (add.py:808 `print(_next_footer(...))`); the new per-phase strings are reached by the phase dispatch — confirmed by the live smoke printing each one.
- [x] DEAD-CODE (code) — no new symbol added (a string-value change in an existing branch); the removed dead `_foot_at` test helper was pruned. No orphan.
- [x] SEMANTIC (prose / non-code) — the emitted hint wording read in full: it names both the collapse and the per-section alt, and pairs the collapse with "step-by-step" so a section drafter isn't misled; matches the frozen §3 "MUST contain BOTH tokens".

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — `_next_footer` (edited in place), `cmd_advance`/`--to` (unchanged), `PHASES`, `_FRONT_PHASES` all present; `PHASE_GUIDE` + `_driver_marker` unchanged.
- [x] no anchor moved/renamed since Ground SHA 94486bb — only the string values inside the existing `_next_footer` branch changed.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed for overfit — tests assert observable footer strings via the REAL CLI (render-blind, not internals); tried to break M3 with the `why`/marker ("freeze the shape [human gate]" contains no "advance"/"--to"); confirmed the green is not vacuous by the independent live smoke printing the exact contracted strings at each phase; confirmed RED→GREEN (5 tests failed pre-build for missing behavior).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — pure static-string render; no IO/eval/network/secret; no user input reaches the footer.
2. Concurrency: CLEAR — `_next_footer` is a pure function computed after save_state; no shared mutable state, no timing.
3. Architecture: CLEAR — reuses the single next-step channel + the already-shipped `--to`; no new surface/flag; backward-compatible; 3-tree byte-parity + ENGINE_MD5 re-satisfied.
Verdict: PASS
Residue: none
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-09

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose enrich `_next_footer` to emit the `--to contract` collapse hint for front phases; rejected change bare `advance` to auto-chain by default (rejected — flips behavior for ~3k single-step tests + duplicates `--to`) · add a new `advance --auto` flag (rejected — new surface the agent still wouldn't discover; the footer is the read-every-turn channel).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: a pure-render string change in the one next-step composer — no control-flow, no new flag, no engine capability added; reuse the already-shipped `--to` bundle-advance. Deterministic, fail-loud, backward-compatible (the methodology-engine-dev stance).
- [AI] build — data strategy: no data-shape change — `_next_footer` returns the same `str`; only the recommended-command substring per front phase changes. The 3-tree byte-parity + ENGINE_MD5 pin are the invariant the change must re-satisfy.
- [AI] build — pattern: extends the existing "footer teaches the batch form at the moment of use" convention (add.py:6020) — this task makes the taught form the COLLAPSED one.
- [AI] build — optimization stance: token-cost (turn-count) is the optimization — fewer engine round-trips per feature; budget = beat the 63-turn/$3.99 baseline. ⚠ least-trusted facet: whether the agent actually pre-drafts before running `--to contract` (behavioral, not enforced) — mitigated by the paired "or --fill <draft> per section" wording. correctness-first otherwise.
- [AI] build — strategy used: as planned — split the `_next_footer` Arm-A elif into `{ground,specify,scenarios}`→`"add.py advance --to contract   (or step-by-step: add.py advance --fill <draft>)"`, `contract`→`"add.py freeze"`, `elif phase == "tests"`→`"add.py advance --fill <draft>"`, else→bare advance (verify/build/observe byte-unchanged). Twin sync: prepare_bundle.py (canonical→_bundled) + `cp` canonical→.add dogfood; NOTE prepare_bundle DELETES the bundled `engine_pin.py` (it copies add.py+add_engine+templates only) → git-restored it, then hand-repinned ENGINE_MD5=6bb8630… across all 3 pin copies (identical), rm __pycache__ first. Live smoke + 727/0 check + 93 targeted tests green.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

