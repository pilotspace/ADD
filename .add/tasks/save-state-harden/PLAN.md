# TASK: F7: save_state OSError -> _die (named code) + tests for gate/advance

slug: save-state-harden · created: 2026-06-25 · stage: mvp
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
  - `add-method/tooling/add.py:save_state` (608–610) — writes state.json via `_atomic_write` with NO OSError guard; an IO failure propagates a raw Python traceback. THE FIX SITE.
  - `add-method/tooling/add.py:load_state` (574–583) — the fail-closed model to MIRROR: catches `(JSONDecodeError, OSError)` → `_die("state_invalid: ...")`, never a traceback.
  - `add-method/tooling/add.py:_write_retro` — already hardened (catches OSError → `_die("retro_write_failed")`); the naming + test precedent.
  - `add-method/tooling/add.py:_atomic_write` (222–235) — temp + `os.replace`; the `finally` unlinks the temp, so on failure the ORIGINAL state.json is byte-unchanged (the recovery guarantee).
  - `add-method/tooling/add.py:_die(msg, code=1)` (703) — the fail-closed exit.
  - call sites: `cmd_advance` · `cmd_gate` · `cmd_phase` (+ ~every mutating command) all END in `save_state`, so every one degrades gracefully once it is hardened.
Context (working folder):
  - `add-method/tooling/test_state_hardening.py:test_retro_write_is_atomic` (116–130) — the mock pattern to mirror: `mock.patch("add.os.replace", side_effect=OSError("disk full"))` + assert exit 1 + named code + state unchanged. New tests land HERE (the design-for-failure suite).
  - Engine mirrored ×3 under the ENGINE_MD5 pin (`engine_pin.py`); a change re-mirrors + re-pins.
Honors (patterns / conventions):
  - Design-for-failure (CLAUDE.md core rule + this suite's charter): fail CLOSED with a NAMED code, never a raw traceback.
  - Atomicity preserved: a failed write leaves state.json byte-unchanged.
  - Mirror-3-trees + ENGINE_MD5 re-pin on any add.py edit.
  - Red/green TDD.
Anchors the contract cites: `save_state` · `_atomic_write` · `_die` · reject code `state_write_failed`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `save_state` fails CLOSED on an IO error — a clean, named `state_write_failed` (never a raw traceback), with state.json left byte-unchanged.
Framings weighed: mirror-load_state (chosen) · let-it-raise · retry-with-backoff
  - chosen: wrap `save_state`'s `_atomic_write` in `try/except OSError -> _die("state_write_failed: ...")`, mirroring `load_state`'s fail-closed shape and `_write_retro`'s `retro_write_failed` precedent. One symmetric, named seam.
  - let-it-raise: the status quo — a raw Python traceback on a full disk / read-only FS. Rejected (violates design-for-failure; the brief's core rule).
  - retry-with-backoff: over-engineered for a local CLI state write; a transient FS error is rare and the user can re-run. Rejected (a named, recoverable error is the right altitude).
Must:
<must>
  - `save_state` wraps its `_atomic_write` call in `try/except OSError` and calls `_die("state_write_failed: ...")` (exit 1) instead of propagating a traceback.
  - On that failure, state.json is byte-unchanged (the atomic temp+replace guarantees the prior file is never touched).
  - The message names the path + the exception class + a recovery hint (free disk / fix permissions / the prior state survives).
  - Every command that ends in `save_state` (advance · gate · phase · …) degrades gracefully — no raw traceback on a state-write IO failure.
  - (F12, folded in) `save_state` runs BEFORE `_sync_task_marker` at every task-progress site — `cmd_gate` · `cmd_advance` · `cmd_phase` · `cmd_reopen` — so state (the source of truth) is durable first and the TASK.md marker only mirrors it. A failed save dies before the marker moves → no split-brain (TASK.md never ahead of state.json).
</must>
Reject:
<reject>
  - `save_state`'s atomic write raises OSError -> "state_write_failed"
</reject>
After:
<after>
  - No engine command exits with a raw Python traceback on a state-write IO failure; the prior state.json survives intact and the named error tells the user how to recover.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] F12 split-brain — FOLDED IN (human-approved 2026-06-25). Applied uniformly at all 4 task-progress sites (cmd_gate · cmd_advance · cmd_phase · cmd_reopen), not just cmd_gate, because it is the SAME documented invariant ("state is the source of truth; the file only mirrors it", add.py:667) — fixing only 2 would leave the identical latent split-brain in cmd_phase (`phase done`) + cmd_reopen. Mechanical swap; existing suite covers the success path (marker still written, just after save).
  - [x] Atomicity ⇒ byte-unchanged on failure — confirmed: `_atomic_write` writes a temp then `os.replace`s; on an exception the `finally` unlinks the temp and the original is never overwritten.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: save_state dies clean on an IO failure
  Given an initialised project and a state write that raises OSError
  When save_state is called
  Then it exits 1 with "state_write_failed" (not a raw traceback)
  And state.json is byte-identical to before the failed write

Scenario: advance degrades gracefully when the state write fails
  Given a task at phase=ground and a failing state.json write
  When I run `add.py advance <slug>`
  Then it exits 1 with "state_write_failed"
  And state.json is byte-unchanged (the task is still at ground)

Scenario: gate degrades gracefully when the state write fails
  Given a task at phase=verify and a failing state.json write
  When I run `add.py gate PASS <slug>`
  Then it exits 1 with "state_write_failed"
  And state.json is byte-unchanged (no gate recorded in state)

Scenario: (F12) a failed gate save leaves NO split-brain
  Given a task at phase=verify and a failing state.json write
  When I run `add.py gate PASS <slug>`
  Then it exits 1 with "state_write_failed"
  And the TASK.md phase marker is NOT advanced to "done" (the file is not ahead of state)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
save_state(root, state) -> None
    state["updated"] = _now()
    try:
        _atomic_write(root / STATE_FILE, json.dumps(state, indent=2) + "\n")
    except OSError as e:
        _die(f"state_write_failed: could not write {root / STATE_FILE} "
             f"({e.__class__.__name__}) — the prior state.json is intact; "
             "free disk / fix permissions and re-run")
  ok   -> state.json written (unchanged behaviour)
  4xx  -> _die "state_write_failed"   (exit 1; prior state.json BYTE-UNCHANGED via atomic temp+replace)
Mirrors: load_state's `state_invalid` + _write_retro's `retro_write_failed` fail-closed shape.

F12 (folded in) — write ORDER at every task-progress site (cmd_gate · cmd_advance · cmd_phase · cmd_reopen):
    state["tasks"][slug][...] = ...   # mutate in-memory state
    save_state(root, state)           # 1. durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, phase)   # 2. mirror into TASK.md AFTER (best-effort)
  invariant: state is authoritative; TASK.md only mirrors it (add.py:667). A failed save dies
  at step 1, so the marker never moves -> the file is never ahead of state (no split-brain).
  (cmd_gate: _stamp_gate_record already sits after save_state — _sync_task_marker joins it there.)
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (with F12 folded in).
Least-sure flag surfaced at freeze: [scope] F7 = save_state hardening + the F12 write-order reorder, folded in per the human's approval; applied uniformly at all 4 task-progress sites (not just cmd_gate) since it is one documented invariant — leaving cmd_phase/cmd_reopen unfixed would keep the identical latent split-brain. [test] the failure-injection mock must fail ONLY on the state.json path (a function side_effect) so an earlier snapshot write is not what trips; the F12 test asserts the TASK.md marker is NOT advanced on a failed gate save.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject (3 scenarios), added to the design-for-failure suite.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_save_state_oserror_dies_named: init; patch `add._atomic_write` to raise OSError on the state.json path; call `add.save_state` / a bare advance / capture bytes before+after / assert SystemExit 1 + "state_write_failed" in stderr + state.json byte-identical
  - test_advance_state_write_failure_named: task at ground; patch the state write to fail; `add.py advance` / assert exit 1 + "state_write_failed" + state.json byte-unchanged (phase still ground)
  - test_gate_state_write_failure_named: task at verify; patch the state write to fail; `add.py gate PASS` / assert exit 1 + "state_write_failed" + state.json byte-unchanged (no gate in state)
  - test_gate_save_failure_no_split_brain (F12): task at verify; patch the state write to fail; `add.py gate PASS` / assert exit 1 + the TASK.md `phase:` marker is still "verify" (NOT advanced to "done") — the file is not ahead of state
</test_plan>

Tests live in: `add-method/tooling/test_state_hardening.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_state_hardening.py`   <!-- canonical engine + bundled mirror + the ENGINE_MD5 pin + the design-for-failure suite; the dogfood .add tree is pruned from the scope walk so needs no token -->
Strategy (ordered batches): 1. add the 3 red tests to test_state_hardening.py. 2. wrap save_state's _atomic_write in try/except OSError -> _die("state_write_failed"). 3. green; mirror canonical -> .add/tooling + _bundled + re-pin ENGINE_MD5; full suite + parity green.
Safety rule (feature-specific): the wrap must NOT swallow a non-OSError (a programming bug stays loud); only OSError fails closed, mirroring load_state.
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

- [x] all tests pass — full suite 1784/0 (was 1780; +4 F7/F12 tests), parity + dual-tree-md5 green on the re-pin
- [x] coverage did not decrease — +4 behavioral tests in the design-for-failure suite; no test removed
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; build edited only add.py (×3 trees) + engine_pin.py; the 4 tests were authored in the tests phase (red), unchanged since
- [x] the green was EARNED, not gamed — refute-read (manual, change is 5 small edits): the wrap catches ONLY OSError (a real bug still raises loud, per the §5 safety rule); _die exits non-zero with a named code (no silent swallow); the reorder's success path is proven by the 1700+ pre-existing advance/gate/phase/reopen tests that still pass (marker still written, just after save); no test asserted the OLD marker-before-save order (none went red)
- [x] concurrency / timing of the risky operation is safe — the reorder IMPROVES crash-safety: durable state precedes the file mirror; save_state stays atomic (temp+replace)
- [x] no exposed secrets, injection openings, or unexpected dependencies — the message interpolates a local path + exception class name only; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — mirror-3-trees synced (prepare_bundle + cp dogfood) + ENGINE_MD5 re-pinned 612a60ef → 4d682bcf
- [x] a person reviewed and approved the change — Tin Dang approved the contract + the F12 fold-in (2026-06-25)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a state-write OSError now prints `state_write_failed: …` and exits 1 (no raw traceback), state.json byte-identical — confirmed by the 3 F7 tests (save_state direct · advance · gate) reading bytes before/after
- [x] a failed gate save leaves the TASK.md `phase:` marker at `verify` (NOT advanced to `done`) — confirmed by test_gate_save_failure_no_split_brain: the file is never ahead of state

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no NEW symbol introduced; save_state hardened in place, and the pre-existing save_state/_sync_task_marker calls are reordered (not removed) at all 4 sites — every call still referenced
- [x] DEAD-CODE (code) — the cmd_gate `_sync_task_marker(root, slug, "done")` moved INTO the post-save `if completing:` block (still called); no orphaned/unused symbol
- [x] SEMANTIC (prose / non-code) — read the frozen §3 + the invariant at add.py:667 ("state is the source of truth; the file only mirrors it"): the reorder makes _sync_task_marker honor the same rule _stamp_gate_record already followed; consistent, not contradictory

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
