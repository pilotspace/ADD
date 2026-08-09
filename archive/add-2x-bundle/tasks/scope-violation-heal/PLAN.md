# TASK: a scope violation enters the bounded self-heal loop — honest redo, never a silent pass

slug: scope-violation-heal · created: 2026-06-12 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered: engine-change task rewiring gate semantics (method-defining) — the verify gate is human-held. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): VERIFIED 2026-06-12 (seams built THIS session by scope-gate-enforce, reread today) — `add-method/tooling/add.py` (engine change: ENGINE_MD5 re-pin from fadd8f7242d3eb07070f779281d3cb7b + ×3 sync). The rewire target: `_scope_guard` (the three `_die` exits — `scope_anchor_missing` on anchor-erased-sidecar-present · `scope_snapshot_tampered` on missing/diverged/unparseable sidecar · `scope_violation` on out-of-scope touches). The router to route INTO: `_heal_or_escalate(root, state, slug, *, reason, source)` (add.py:2203) — sources today "tamper"/"refute-read"; attempts < HEAL_CAP → record entry {at, reason, source} in `heal.history`, phase→build DIRECTLY (never via advance — no re-snapshot), increment durable BEFORE `SystemExit(3)` (redo signal, distinct from _die's 1); attempts ≥ HEAL_CAP → gate=HARD-STOP durable + `heal_exhausted` _die. Counter MONOTONIC, never auto-resets; the `heal` dict is ONE shared counter per task (tamper + refute + scope all draw on it). PRECEDENT routing in `_tamper_guard` (:2240): DIVERGED baseline → heal (source "tamper"); ERASED baseline (`tripwire_missing`) → die in place. Heal-loop dynamics constraint: the loop returns to BUILD; only a tests→build re-cross re-snapshots — so a condition is loop-healable ONLY if fixable from build (reverting touches ✓, reverting tampered sidecar bytes ✓; recreating an erased baseline ✗ → die-in-place stays correct for the missing/erased cases).
Context (working folder): `.add/milestones/build-scope-lock/MILESTONE.md` — last open task + exit criterion "A scope violation lands in the self-heal loop and counts against the shared cap". Suites coupled: `test_scope_gate_enforce.py` (16 — three asserts pin the CURRENT die-in-place behavior: `_assert_refused` on modify/new-deleted/waiver expect nonzero+gate-none and will need the v(N) heal semantics — they assert refusal, NOT exit code 1, so return-to-build exit 3 still satisfies `assertNotEqual(code, 0)`; BUT `_assert_refused` also asserts `phase != done` ✓ and gate "none" ✓ — heal keeps both. VERIFIED compatible: heal exits 3, gate stays none, phase→build ≠ done) · `test_heal_then_escalate.py` (the router's own suite — cap/monotonic/exit-3 fixtures) · `test_tamper_tripwire.py` (`_assert_blocked` allows phase in (verify, build) — the heal-aware idiom to copy).
Honors (patterns / conventions): heal-then-escalate (verify-integrity): a confirmed mechanical cheat returns to build ≤HEAL_CAP then escalates HARD-STOP — never silent, never launderable (the reroute keeps _scope_guard BEFORE the waiver write); engine pin idiom (re-aim + ×3 sync); named codes; sandbox-only mutating probes (fv28); the scope-gate-enforce §7 delta applied at ground: the state-removing transition (heal exhaustion) and the state-creating one (heal entry) live in the SAME contract; wording sweep done (no banned idiom in planned prose).
Anchors the contract cites: `_scope_guard` (the three exits) · `_heal_or_escalate` + `HEAL_CAP` + `heal{attempts,history}` shared-counter shape · `_tamper_guard` diverged-vs-erased routing precedent · `SystemExit(3)` redo signal · `engine_pin.ENGINE_MD5` (RE-PINNED by this task) · `test_scope_gate_enforce._assert_refused` (compatibility verified above).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: scope-violation-heal — recoverable scope refusals enter the bounded self-heal loop (return-to-build, shared cap, then escalation)
Framings weighed: route-at-the-die-site inside `_scope_guard` (chosen — the exact `_tamper_guard` precedent: the guard itself calls the router; one seam, one placement discipline) · catch-SystemExit-in-cmd_gate (rejected: `_die` is flow control — wrapping it inverts fail-closed and decouples the routing from the finding) · a parallel scope-heal counter (rejected by the milestone shared decision: "reuses heal/heal_exhausted, never a parallel loop")
Must:
<must>
  - an out-of-scope touch at a completing gate routes through `_heal_or_escalate` with source "scope": phase returns to build DIRECTLY, attempts+1 durable BEFORE the exit, exit code 3, and the reason string CARRIES `scope_violation` plus the offending paths (existing token pins survive)
  - a DIVERGED or UNPARSEABLE sidecar (present-but-wrong bytes) routes through `_heal_or_escalate` with source "scope-tamper"; the reason carries `scope_snapshot_tampered` — revertable from build, so it earns the bounded redo
  - the return-to-build never re-arms the baseline: sidecar + anchor survive the loop byte-identical, and the redo gate re-checks against the ORIGINAL snapshot (a heal can never launder the violation it routed)
  - the counter is the ONE shared per-task heal dict: scope attempts add to the same cap as "tamper" and "refute-read"; a finding at attempts ≥ HEAL_CAP records gate=HARD-STOP durable and dies `heal_exhausted`
  - an honest redo (offending touches reverted) PASSes the same gate with no further ceremony
</must>
Reject:
<reject>
  - sidecar ERASED (missing) -> "scope_snapshot_tampered" die-in-place, exit 1, NO heal attempt recorded (erased-baseline parity with tripwire_missing: a redo cannot recreate trust)
  - anchor erased while the sidecar is present -> "scope_anchor_missing" die-in-place, exit 1, NO heal (the state witness is gone; auto-re-anchoring would launder a forged sidecar)
  - a finding when attempts ≥ HEAL_CAP -> "heal_exhausted" + gate=HARD-STOP durable (never a completing outcome)
  - RISK-ACCEPTED with a pending violation -> heals BEFORE the waiver write; no waiver key lands ("scope_violation" in the redo reason)
</reject>
After:
<after>
  - first violation: phase=build · gate="none" · heal.attempts==1 · history[-1] == {at, reason carrying the named code, source "scope"} · sidecar bytes and anchor dict unchanged
  - after the honest redo: the same gate records PASS; attempts stay where the heal left them (monotonic, never auto-reset)
  - `check` is untouched: read-only WARN monitor, exit 0, never increments heal
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [test] the 4 existing `_assert_refused` green pins (test_scope_gate_enforce: modify · new+deleted · waiver · sidecar-tamper) survive the reroute — verified at ground by reading the helper (nonzero ✓ exit-3 · gate "none" ✓ heal never completes · phase build ≠ done ✓ · token ✓ IF every heal reason carries the named code, which the contract pins); if wrong: the sibling suite reds and the contained fix is migrating those asserts to the `_assert_blocked` heal-aware idiom (test_tamper_tripwire precedent)
  - [x] build→verify advance does NOT re-snapshot scope — confirmed: cmd_advance writes sidecar+anchor only in the tests→build block, and `_heal_or_escalate` sets phase DIRECTLY (never via advance)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a scope violation returns to build
  Given an armed task (declared `src/`, sidecar + anchor live) whose build modified other/readme.txt
  When the gate records PASS
  Then exit code 3, output carries "return_to_build" + "scope_violation" + "other/readme.txt", phase=build, heal.attempts==1, history[-1].source=="scope"
  And gate stays "none", and the sidecar bytes + anchor dict are unchanged

Scenario: the cap is shared across cheat sources
  Given the same armed violation but heal seeded at attempts==HEAL_CAP from source "tamper"
  When the gate records PASS
  Then exit code 1, output carries "heal_exhausted", gate=="HARD-STOP" durable, history[-1].source=="scope"
  And phase stays "verify" — the loop never grants a free scope attempt past a tamper-spent cap

Scenario: an honest redo passes the original gate
  Given a healed violation (exit 3, phase=build)
  When the offending file is reverted to its snapshot bytes, the task advances build->verify, and the gate records PASS
  Then exit code 0 and gate=="PASS"
  And heal.attempts stays 1 — monotonic, never auto-reset by success

Scenario: a diverged sidecar heals and a restored sidecar passes
  Given an armed task whose sidecar bytes were rewritten (md5 diverges from the anchor)
  When the gate records PASS
  Then exit code 3, output carries "scope_snapshot_tampered", history[-1].source=="scope-tamper", phase=build
  And after restoring the ORIGINAL sidecar bytes and re-advancing, the same gate PASSes

Scenario: an erased sidecar still dies in place
  Given an armed task whose sidecar file was deleted
  When the gate records PASS
  Then exit code 1 (not 3), output carries "scope_snapshot_tampered" + "missing"
  And phase stays "verify" and NO heal attempt is recorded

Scenario: an erased anchor still dies in place
  Given an armed task whose state.json scope anchor was popped while the sidecar exists
  When the gate records PASS
  Then exit code 1 (not 3), output carries "scope_anchor_missing"
  And phase stays "verify", NO heal attempt is recorded, and the sidecar bytes are untouched

Scenario: a violation cannot be laundered through a waiver
  Given an armed violation
  When the gate records RISK-ACCEPTED with a complete signed waiver
  Then exit code 3 and "scope_violation" in the output (the heal fires BEFORE the waiver write)
  And no "waiver" key lands in the task state

Scenario: check stays a read-only monitor
  Given an armed violation pending at the gate
  When `add.py check` runs
  Then exit 0 with the scope WARN
  And heal stays absent — the monitor never spends an attempt

Scenario: the engine copies stay mirrored and pinned
  Given the rewired add.py
  When the mirror and pin assertions run
  Then add.py is byte-identical x3 and ENGINE_MD5 matches the canonical bytes
  And the pin annotation names this task's re-aim
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE add.py gate <PASS|RISK-ACCEPTED>  —  _scope_guard heal rewire (v1)

_scope_guard(root, state, slug) routing — tripwire-parity (recoverable heals, erased dies):
  anchor absent + sidecar PRESENT     -> _die "scope_anchor_missing"          exit 1  (UNCHANGED: the
                                          state witness is gone; auto-re-anchor would launder a forged sidecar)
  sidecar finding == "missing"        -> _die "scope_snapshot_tampered: … missing …"  exit 1  (NEW SPLIT:
                                          erased baseline — tripwire_missing parity; not in-loop recoverable)
  sidecar finding == "diverged" | "unparseable"
                                      -> _heal_or_escalate(reason="scope_snapshot_tampered: … {finding} …",
                                                           source="scope-tamper")   exit 3
  out-of-scope touches                -> _heal_or_escalate(reason="scope_violation: … {paths[:5]} (N total)",
                                                           source="scope")          exit 3

_heal_or_escalate semantics — REUSED VERBATIM, zero router changes:
  attempts < HEAL_CAP  -> history += {at, reason, source}; attempts+1 durable BEFORE SystemExit(3);
                          phase -> build DIRECT (never via advance: sidecar + anchor SURVIVE byte-identical,
                          the redo gate re-checks the ORIGINAL baseline)
  attempts >= HEAL_CAP -> history += entry; gate=HARD-STOP durable; _die "heal_exhausted"  exit 1
  ONE shared counter: sources "tamper" · "refute-read" · "scope" · "scope-tamper" draw on the same cap.

Invariants (pinned green, must hold before AND after):
  every heal reason CARRIES the named code token  (the 4 _assert_refused pins in
    test_scope_gate_enforce survive: nonzero exit · gate "none" · phase != done · token in output)
  placement unchanged: after _tamper_guard, BEFORE the waiver write — never launderable;
    HARD-STOP never calls the guard (stopping is always allowed)
  `check` stays a read-only WARN monitor — never routes to heal, never increments
  a refusal never rewrites the anchor or the sidecar (evidence, not state)

Schema: state.json tasks[slug].heal {attempts:int, history:[{at,reason,source}]} — EXISTING shape,
  two NEW source values "scope" | "scope-tamper". No new files, no new state keys, no new exit codes
  (3 = redo · 1 = die · 0 = clean).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-12
Least-sure flag surfaced at freeze: ⚠ [contract] `unparseable` is routed to heal alongside `diverged` (present-but-wrong bytes), not die-in-place — the more conservative reading would die. Heal is safe (the gate never completes until findings clear; the shared cap escalates), but if wrong: an attacker gets ≤HEAL_CAP bounded, logged, never-completing redo rounds before HARD-STOP — no laundering path either way; the fix is moving one branch. ⚠ [test] the 4 existing `_assert_refused` sibling pins survive the exit-1→exit-3 reroute — verified by reading the helper (code≠0 · gate "none" · phase≠done · token rides the reason); if wrong: migrate those 4 asserts to the `_assert_blocked` heal-aware idiom (contained).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 9 scenarios 1:1 — every routing branch + every pinned invariant, asserted via subprocess behavior (exit codes · output tokens · state.json reads), never internals. RED for the right reason: 1–4 and 7 red pre-build (today the guard dies exit 1 in place — no heal entry, no phase=build); 5 · 6 · 8 · 9 are GREEN pins at write (die-in-place, monitor, and mirror behavior that must survive the rewire — the sibling-suite idiom).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_violation_returns_to_build: arrange armed `src/` task + out-of-scope modify / act gate PASS / assert exit 3 + "return_to_build" + "scope_violation" + path + phase=build + attempts==1 + source=="scope" + assert gate "none", sidecar bytes + anchor dict unchanged
  - test_cap_is_shared_across_sources: arrange heal seeded {attempts: HEAL_CAP, history: [source "tamper"]} + violation / act gate PASS / assert exit 1 + "heal_exhausted" + gate=="HARD-STOP" + history[-1].source=="scope" + assert phase stays "verify"
  - test_honest_redo_passes: arrange healed violation / act revert offending bytes -> advance -> gate PASS / assert exit 0 + gate=="PASS" + assert attempts stays 1
  - test_sidecar_diverged_heals_then_restores: arrange sidecar bytes rewritten / act gate PASS / assert exit 3 + "scope_snapshot_tampered" + source=="scope-tamper" / then restore ORIGINAL bytes -> advance -> gate PASS / assert exit 0
  - test_sidecar_missing_still_dies: arrange sidecar unlinked / act gate PASS / assert exit 1 (not 3) + "scope_snapshot_tampered" + "missing" + assert phase "verify", no heal key   [GREEN pin]
  - test_anchor_missing_still_dies: arrange anchor popped, sidecar present / act gate PASS / assert exit 1 (not 3) + "scope_anchor_missing" + assert no heal key, sidecar bytes untouched   [GREEN pin]
  - test_waiver_never_lands_on_heal: arrange violation / act gate RISK-ACCEPTED with full waiver / assert exit 3 + "scope_violation" + assert no "waiver" key in task state
  - test_check_never_heals: arrange pending violation / act add.py check / assert exit 0 + scope WARN + assert heal stays absent   [GREEN pin]
  - test_mirrors_and_pin: assert add.py byte-identical x3 + ENGINE_MD5 == md5(canonical bytes) + the pin annotation names scope-violation-heal   [GREEN pin]
</test_plan>

Tests live in: `add-method/tooling/test_scope_violation_heal.py` · MUST run red (missing implementation) before Build.

RED RUN 2026-06-12 (10 tests, python3.14): 6 fail / 4 pass — exactly the contract's split.
  RED (today _scope_guard dies exit 1 where the contract routes to heal exit 3):
    test_violation_returns_to_build · test_cap_is_shared_across_sources · test_honest_redo_passes ·
    test_sidecar_diverged_heals_then_restores · test_waiver_never_lands_on_heal
    (each asserts code==3 / "heal_exhausted"; today's output is "scope_violation: … (1 total)" exit 1)
  RED-then-green-at-repin: test_pin_annotation_names_this_task (annotation still names scope-gate-enforce)
  GREEN pins already holding (must survive the rewire): test_sidecar_missing_still_dies ·
    test_anchor_missing_still_dies · test_check_never_heals · test_mirrors_and_pin
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `engine_pin.py` · `test_scope_violation_heal.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `.add/tooling/add.py`
Strategy (ordered batches): 1. red suite (test_scope_violation_heal.py, recorded red run, green pins verified green) 2. rewire _scope_guard routing in canonical add.py 3. re-aim engine_pin.ENGINE_MD5 + x3 sync 4. full suite x2 interpreters (sibling pins must hold)
Safety rule (feature-specific): the reroute must keep _scope_guard BEFORE the waiver write and OFF the HARD-STOP path — and a heal must never rewrite the sidecar or anchor (evidence survives the loop)
Code lives in: `add-method/tooling/add.py` (engine — no task-local src/)
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

- [x] all tests pass — full tooling suite 897 OK on python3.14.5 AND /opt/homebrew/bin/python3.10 (was 887; +10 new). New suite test_scope_violation_heal: 10/10.
- [x] coverage did not decrease — 9 scenarios 1:1; the rewire reuses _heal_or_escalate (already covered by test_heal_then_escalate) so no new uncovered branch.
- [x] no test or contract was altered during build — §3 frozen v1 untouched; the red suite untouched after its red run (tripwire intact); only the 5 declared §5 files were written.
- [x] the green was EARNED, not gamed — adversarial refute-read (manual + a live sandbox probe): (1) shared cap is real — seeded {attempts: HEAL_CAP, source "tamper"} then a scope arrival escalates heal_exhausted (setdefault returns the EXISTING counter, never resets); (2) PROBED empirically — a violation healed but NOT reverted re-counts (attempts 1→2, gate stays "none"), so a heal can never launder a violation by bare re-gating; (3) no overfit (generic router reuse, not fixture-shaped), no vacuous asserts (each test pins exit code + named token + phase + attempts + source + evidence bytes), no stubs. One documented gap: `unparseable` shares the `if tamper:` branch with `diverged` (both → heal source "scope-tamper") and is covered behaviorally by the diverged test, not separately — a single branch, two triggers, equivalent.
- [x] concurrency / timing of the risky operation is safe — the increment is saved BEFORE SystemExit(3) (fail-closed: a re-run never grants a free attempt); single-process CLI, no shared-state race introduced.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; reason strings interpolate engine-owned slug + already-validated rel paths; no new imports.
- [x] layering & dependencies follow CONVENTIONS.md — the guard calls the existing router at its die-sites; placement unchanged (after _tamper_guard, before the waiver write, off the HARD-STOP path).
- [ ] a person reviewed and approved the change — risk: high · autonomy: conservative → human-held gate (this freeze point).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_scope_guard`'s two new `_heal_or_escalate` calls (source "scope" / "scope-tamper") are reached at the gate (cmd_gate:684); the `missing`-split `_die` is reached for an erased sidecar. All three confirmed by the passing routing tests. No new symbol introduced — the router and HEAL_CAP pre-exist.
- [x] DEAD-CODE (code) — no orphan: the old single `_die(scope_snapshot_tampered)` / `_die(scope_violation)` lines were REPLACED, not left dangling; `grep` confirms no "refuses in place" / stale "NEXT task" reference remains in add.py.
- [x] SEMANTIC (prose / non-code) — read in full: the `_scope_guard` docstring (rewritten to state the routing + tripwire-parity) and the engine_pin annotation (re-aimed @ scope-violation-heal, carrying the scope-gate-enforce + wave-ledger + argv-portability prior gates). Both match the implemented behavior.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-12   (human-held gate, risk: high · conservative)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `check` scope monitor already surfaces a pending violation as WARN; the heal `history` (per-task, source-tagged) is the audit trail — a task accumulating scope/scope-tamper entries is a build whose declared §5 Scope is too narrow (or an agent fighting the gate). Watch heal.attempts approaching HEAL_CAP on real tasks: a recurring scope heal means the Scope declaration needs widening at the next contract, not more redo rounds.
Spec delta for the next loop: the recoverable/erased SPLIT is now the reusable shape for ANY new mechanical guard — route the from-build-fixable findings into the shared loop, keep the erased-evidence findings die-in-place. The trust triangle (shape · proof · scope) is closed: all three guards (frozen contract tripwire, test tripwire, scope gate) now share ONE bounded self-heal loop and ONE cap.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a finding is loop-healable ONLY if fixable from BUILD; erased evidence (missing sidecar, erased anchor) must stay die-in-place — the recoverable/erased split is the reusable routing rule any future guard inherits by calling the shared router (evidence: _scope_guard `missing`-split vs heal, test_sidecar_missing_still_dies + test_anchor_missing_still_dies green-pinned against test_sidecar_diverged_heals_then_restores)
- [TDD · folded] a behavior-FLIP task (same trigger, exit 1 → exit 3) is best pinned by a GREEN-pin partition — the unchanged invariants (die-in-place ×2, monitor, mirrors) pin green-before-AND-after while only the flipped branches red, so the red/green split itself encodes the contract (evidence: test_scope_violation_heal recorded red run 2026-06-12 — 4 green pins + 5 routing reds + 1 repin-flip)
- [ADD · folded] proving a SHARED cap needs a cross-source escalation test, never a same-source one — seeding the counter from "tamper" then triggering a "scope" arrival is the only assertion that distinguishes a shared cap from a parallel one (evidence: test_cap_is_shared_across_sources escalates heal_exhausted with history[-1].source=="scope")
