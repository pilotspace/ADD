# TASK: F5: cmd_gate refuses a completing outcome when the pinned contract hash is stale

slug: consumer-stale-gate · created: 2026-06-25 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_gate` (1487–1539) — the completing-gate path. After `_tamper_guard` (1520) + `_scope_guard` (1523) + the green-bar cite, NOTHING checks the consumer's pin freshness. THE FIX SITE — add a stale-pin guard here (before the waiver write, like the others).
  - `add-method/tooling/add.py` cmd_check stale logic (2765–2778) — the EXISTING drift detection: read `contract_pin = {id, hash}`, compare to `_contract_snapshot(id)`'s live hash; `_live != pin.hash` ⇒ `contract_consumer_stale` WARNING (today: surfaced, not gated). Reuse this exact predicate.
  - `add-method/tooling/add.py:contract_pin` write (1368–1379, cmd_advance) — a `consumes:` task pins the producer's live hash at the contract→tests crossing. The pin the guard validates.
  - `add-method/tooling/add.py:_contract_snapshot(root, cid) -> Path` (4341) — the producer's published snapshot (`.add/contracts/<id>.json`, `{hash}`).
  - `add-method/tooling/add.py:_die` — the fail-closed refusal (a stale pin is recoverable: re-pin via re-cross contract→tests, NOT a cheat/heal).
Context (working folder):
  - `add-method/tooling/test_cross_component_contract.py` — the contract-pin suite; `CheckFindings.test_consumer_stale_when_producer_refroze_changed_shape` (207) already arranges the stale scenario end-to-end (`_Board` harness: `_new_at_contract` · `_advance` · `_check`). The F5 gate tests land HERE.
  - Component pillar requires `tomllib` (py3.11+); the suite SkipTests below that (setUpModule).
  - Engine mirrored ×3 under the ENGINE_MD5 pin; a change re-mirrors + re-pins.
Honors (patterns / conventions):
  - Reuse the EXISTING `contract_consumer_stale` predicate + ubiquitous code (no new condition for the same drift).
  - Same completing-guard discipline as `_tamper_guard`/`_scope_guard`: refuse BEFORE the waiver write (never launderable through RISK-ACCEPTED), never on HARD-STOP.
  - Degrade-safe: an unreadable snapshot is NOT decided at the gate (stays a cmd_check warning; the missing-snapshot HARD-STOP already lives at the advance crossing) — only a CONFIRMED drift blocks.
  - Mirror-3-trees + ENGINE_MD5 re-pin; red/green TDD.
Anchors the contract cites: `cmd_gate` · `contract_pin` · `_contract_snapshot` · reject code `contract_consumer_stale`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `cmd_gate` refuses a COMPLETING outcome (PASS / RISK-ACCEPTED) when the task's pinned consumer contract hash is STALE — the producer re-froze a changed shape since the pin, so the consumer built against an out-of-date contract.
Framings weighed: gate-guard-reuse-predicate (chosen) · block-PASS-only · promote-to-HARD-STOP-heal
  - chosen: add a `_consumer_stale_guard` to cmd_gate's completing block (beside `_tamper_guard`/`_scope_guard`, before the waiver) that reuses the cmd_check drift predicate; a confirmed drift `_die`s with the re-pin remedy. Blocks BOTH completing outcomes (the title's "a completing outcome").
  - block-PASS-only: let RISK-ACCEPTED waive a stale pin. Rejected as the default — re-pinning (re-cross contract→tests) is cheap and correct; waiving "I built against an old contract" is rarely intended. (Offered as the flag's alternative.)
  - promote-to-HARD-STOP-heal: route through `_heal_or_escalate`. Rejected — staleness is not a CHEAT (no tamper); it is a stale INPUT, fixed by re-pinning, not by an honest-redo loop. A plain named `_die` fits.
Must:
<must>
  - A completing `gate` (PASS or RISK-ACCEPTED) on a task whose `contract_pin` hash differs from the live `_contract_snapshot` hash is REFUSED with `contract_consumer_stale` (exit 1); the gate/phase are NOT recorded (validate-then-write).
  - The guard runs in the completing block only — a HARD-STOP outcome is never blocked (stopping is always allowed).
  - It runs BEFORE the waiver write, so a stale pin is not launderable through RISK-ACCEPTED.
  - A FRESH pin (live hash == pinned hash) completes normally — no false refusal.
  - A pure version bump (producer re-froze the SAME shape → same hash) is NOT stale → completes normally.
  - A task with no `contract_pin` (no `consumes:`) is unaffected — byte-identical to today.
</must>
Reject:
<reject>
  - completing gate + `contract_pin.hash` != live snapshot hash -> "contract_consumer_stale"
</reject>
After:
<after>
  - No consumer can record a completing verdict while pinned to a contract the producer has since changed; the only path forward is to re-pin (re-cross contract→tests) after reviewing the new frozen shape.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The guard blocks RISK-ACCEPTED too (placed before the waiver, like tamper/scope). Lowest confidence because, unlike a cheat, a stale pin is a non-security risk a human MIGHT consciously accept. If you'd rather allow a signed waiver: gate the refusal on `args.outcome == "PASS"` instead (one-line change). Flagged at freeze.
  - [x] An UNREADABLE/missing live snapshot is NOT decided at the gate — confirmed scope choice: it stays a cmd_check warning + the advance-time `contract_snapshot_missing` HARD-STOP; only a CONFIRMED hash drift blocks here (avoids a transient read error blocking completion).
  - [x] Only `consumes:` tasks carry a `contract_pin`, so producers/plain tasks are unaffected — confirmed (pin written only on the consumes path, 1368–1379).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a stale consumer pin is refused at the completing gate
  Given a consumer task at verify whose pinned contract hash drifted (producer re-froze a changed shape)
  When I run `add.py gate PASS <consumer>`
  Then it exits 1 with "contract_consumer_stale"
  And the task is NOT marked done (gate not recorded)

Scenario: a RISK-ACCEPTED outcome on a stale pin is also refused
  Given the same stale consumer at verify
  When I run `add.py gate RISK-ACCEPTED ... <consumer>`
  Then it exits 1 with "contract_consumer_stale" (not launderable through a waiver)
  And no waiver is recorded

Scenario: a fresh consumer pin completes normally
  Given a consumer at verify whose pinned hash equals the live snapshot
  When I run `add.py gate PASS <consumer>`
  Then it succeeds and the task is done

Scenario: a pure producer version bump is not stale
  Given a consumer at verify and the producer re-froze the SAME shape (v2, same hash)
  When I run `add.py gate PASS <consumer>`
  Then it succeeds (a version bump is not a shape change)

Scenario: a task with no consumer pin is unaffected
  Given a plain task at verify (no consumes:)
  When I run `add.py gate PASS <task>`
  Then it succeeds exactly as today
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_consumer_stale_guard(root, state, slug) -> None   # called in cmd_gate's `if completing:` block,
                                                    # AFTER _scope_guard, BEFORE the waiver write
    pin = state["tasks"][slug].get("contract_pin")
    if not pin: return                              # no consumes: -> unaffected (byte-identical)
    try:    live = json.loads(_contract_snapshot(root, pin["id"]).read_text()).get("hash")
    except (OSError, ValueError, KeyError, TypeError, AttributeError): return   # unreadable -> not decided here
    if live is not None and live != pin.get("hash"):
        _die("contract_consumer_stale: task '<slug>' pinned contract '<id>' changed shape since "
             "the pin (producer re-froze) — re-pin by re-crossing contract→tests after reviewing "
             "the new frozen shape; never complete against a stale contract")
  ok (fresh pin / version bump / no pin) -> completes normally
  4xx -> _die "contract_consumer_stale"  (exit 1; gate + phase NOT recorded — validate-then-write)
Schema (read-only): state.tasks[slug].contract_pin {id, hash}  vs  .add/contracts/<id>.json {hash}.
Reuses the cmd_check drift predicate (2765–2778); blocks PASS AND RISK-ACCEPTED.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (block both PASS and RISK-ACCEPTED).
Least-sure flag surfaced at freeze: [contract] the guard blocks RISK-ACCEPTED too (placed before the waiver write, like tamper/scope) — a stale pin is not launderable through a signed waiver; the human chose re-pin as the only path over allowing a conscious waiver. [test] the stale arrangement re-freezes the PRODUCER's §3 to a changed shape end-to-end (real engine hash drift), not a hand-mutated pin; the consumer carries a well-formed freeze flag so its tests→build crossing doesn't trip unflagged_freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject (the 5 scenarios), in the contract-pin suite.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_gate_refuses_stale_consumer_pin: arrange p+c, advance c to verify (pinned); producer re-freezes SHAPE B; `gate PASS c` -> SystemExit, "contract_consumer_stale" in err, c phase != done
  - test_risk_accepted_also_refused_on_stale_pin: same stale c; `gate RISK-ACCEPTED c` (+waiver flags) -> exit 1 + "contract_consumer_stale" + no waiver recorded
  - test_gate_passes_fresh_consumer_pin: p+c to verify, producer UNCHANGED; `gate PASS c` -> ok, c done
  - test_gate_passes_on_pure_version_bump: producer re-freezes v2 SAME shape; `gate PASS c` -> ok, c done
  - test_plain_task_unaffected: a no-consumes task to verify; `gate PASS` -> ok, done (byte-identical control)
</test_plan>

Tests live in: `add-method/tooling/test_cross_component_contract.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_cross_component_contract.py`   <!-- canonical engine + bundled mirror + the ENGINE_MD5 pin + the contract-pin suite; dogfood .add tree pruned from the scope walk -->
Strategy (ordered batches): 1. add the 5 tests to test_cross_component_contract.py (1 red core + controls). 2. add `_consumer_stale_guard` + call it in cmd_gate's completing block after `_scope_guard`. 3. green; mirror canonical -> .add/tooling + _bundled + re-pin ENGINE_MD5; full suite + parity green.
Safety rule (feature-specific): degrade-safe read — an unreadable snapshot returns (no block); only a CONFIRMED hash drift dies. Refuse BEFORE any state write (validate-then-write), and only inside the completing block.
Code lives in: `add-method/tooling/add.py` (+ its two mirrors)
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

- [x] all tests pass — full suite 1797/0 (was 1792; +5 F5 tests), parity + dual-tree-md5 green on the re-pin
- [x] coverage did not decrease — +5 behavioral tests (1 stale-PASS · 1 stale-RISK-ACCEPTED · 3 controls); none removed
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; build added `_consumer_stale_guard` + one call site in cmd_gate (×3 trees) + engine_pin re-pin; the 5 tests were authored in the tests phase (2 red), unchanged since (the range(5)→range(6) fix was a tests-phase correction, pre-build)
- [x] the green was EARNED, not gamed — refute-read (manual): the stale tests re-freeze the PRODUCER's §3 end-to-end so a REAL engine hash drift flips the pin (not a hand-mutated pin); the controls prove no false-positive (fresh pin + pure version bump both complete); the guard reuses the exact cmd_check drift predicate (no divergent second definition of "stale")
- [x] concurrency / timing of the risky operation is safe — pure read of an existing snapshot + state key, before the single save_state; degrade-safe on an unreadable snapshot (returns, no block)
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reads `.add/contracts/<id>.json`
- [x] layering & dependencies follow CONVENTIONS.md — mirror-3-trees synced + ENGINE_MD5 re-pinned a3f99f72 → 310a8ed7
- [x] a person reviewed and approved the change — Tin Dang froze the contract (block both PASS and RISK-ACCEPTED) 2026-06-25

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a consumer at verify with a drifted pin: `gate PASS` exits 1 with `contract_consumer_stale` and the task stays not-done — confirmed by test_gate_refuses_stale_consumer_pin
- [x] the same drift refuses `gate RISK-ACCEPTED` with NO waiver written (before-the-waiver placement) — confirmed by test_risk_accepted_also_refused_on_stale_pin; fresh pin + version bump still complete (the two control tests)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_consumer_stale_guard` is called in cmd_gate's completing block (after `_scope_guard`); it reads the existing `contract_pin` + `_contract_snapshot`; referenced exactly once, intentionally (one gate)
- [x] DEAD-CODE (code) — no orphaned symbol; the guard returns early for no-pin/unreadable, dies on confirmed drift — every branch reachable (proven by the 5 tests)
- [x] SEMANTIC (code) — re-read the cmd_check predicate (2765–2778) the guard mirrors: same `live is not None and live != pin.hash` test, same degrade-safe except-tuple → no divergent definition of "stale"; placement matches the tamper/scope before-the-waiver discipline

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

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
