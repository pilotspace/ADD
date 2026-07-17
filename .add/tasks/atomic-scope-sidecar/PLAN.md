# TASK: cmd_advance scope-sidecar write uses _atomic_write (crash-safe, was non-atomic)

slug: atomic-scope-sidecar · created: 2026-06-25 · stage: mvp
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
  - `add-method/tooling/add.py:_build_entry` (line 1273) — `side.write_text(payload, encoding="utf-8")` writes the §5 scope sidecar (`tasks/<slug>/scope-snapshot.json`) NON-atomically; a crash mid-write leaves a half-written/empty sidecar → next gate reads it as `scope_snapshot_tampered` (false tamper) or "missing". THE fix site: route through `_atomic_write`. Deep-audit F11.
  - `add-method/tooling/add.py:_atomic_write` (222) — temp-file + `os.replace` atomic writer; writes `text` VERBATIM (no newline added), so the sidecar bytes — and thus `_md5_text(payload)` stored as `state.tasks[slug].scope.snapshot_md5` — are byte-identical to today (the integrity check stays valid).
  - `add-method/tooling/add.py:_scope_findings` (4456) — the READER: `_md5_text(raw) != anchor["snapshot_md5"]` → "diverged". Confirms a trailing-newline change would break it (it would not — _atomic_write adds none).
  - `add-method/tooling/add.py:save_state` (611) — precedent: already uses `_atomic_write` (state.json). This makes the sidecar match.
Context (working folder):
  - `add-method/tooling/test_scope_gate_enforce.py` — `_Board` harness: `_arm(slug, scope_line)` crosses tests→build (fires the sidecar write), `_sidecar(slug)`, `_task_state`. The new test lands here.
  - Engine mirrored ×3 under ENGINE_MD5 → a change re-mirrors (_bundled + .add) + re-pins.
Honors (patterns / conventions):
  - "design for failure" (global rule): durable IO must be atomic (temp+replace) so a crash can't leave a torn file — the save-state-harden (F7) theme.
  - byte-identical sidecar (md5 anchor preserved); red/green TDD; mirror-3-trees + re-pin.
Anchors the contract cites: `_build_entry` (the sidecar write) · `_atomic_write` · `scope-snapshot.json` · `snapshot_md5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: route the §5 scope-sidecar write in `_build_entry` through `_atomic_write` (temp-file + os.replace) instead of a raw `write_text`, so a crash mid-write can never leave a torn/empty `scope-snapshot.json` that the next gate misreads as tamper.
Framings weighed: use-_atomic_write (chosen) · _atomic_write_bytes · leave-as-is
  - chosen: swap `side.write_text(payload, …)` → `_atomic_write(side, payload)`. One line; byte-identical output (no newline added) so the stored `snapshot_md5` and the `_scope_findings` integrity check are unchanged; matches save_state's precedent.
  - _atomic_write_bytes: encode payload and use the binary writer. Rejected — the payload is plain JSON text; the text writer is the right tool and what state.json uses.
  - leave-as-is: accept the torn-file risk. Rejected — the audit (F11) flagged it; a torn sidecar manifests as a confusing false `scope_snapshot_tampered`/"missing" at the gate.
Must:
<must>
  - The sidecar (`tasks/<slug>/scope-snapshot.json`) is written via `_atomic_write` at the tests→build crossing — a half-written file can't survive a crash (temp+replace).
  - The sidecar BYTES are unchanged (no trailing newline): `state.tasks[slug].scope.snapshot_md5 == _md5_text(on-disk)` still holds, and `_scope_findings` neither false-"diverged"s nor false-"missing"es a clean build.
  - UNDECLARED tasks still take/clean up no sidecar (the `else: unlink` path is untouched).
</must>
Reject:
<reject>
  - (no new reject code — this is a write-durability swap, not a new gate; the existing `scope_snapshot_tampered`/"missing"/"diverged" reads are unchanged in meaning)
</reject>
After:
<after>
  - The scope sidecar has the same crash-safety guarantee as state.json; the integrity anchor is preserved byte-for-byte.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `_atomic_write` adds NO trailing newline (writes `text` verbatim), so the sidecar md5 stays identical and the integrity check doesn't false-trip. Lowest confidence because save_state's caller appends `"\n"` to its payload — if I mistakenly mirror that, every existing snapshot_md5 would mismatch (mass false tamper). Verified by reading `_atomic_write` (line 230-231: `fh.write(text)`, no newline) — I pass `payload` with NO added newline. Flagged at freeze.
  - [x] engine change → 3-tree mirror + ENGINE_MD5 re-pin — confirmed (add.py is mirrored).
  - [x] only the write changes; the reader (`_scope_findings`) and the UNDECLARED unlink path are untouched — confirmed.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the scope sidecar is written atomically
  Given a task with a declared §5 scope crossing tests->build
  When _build_entry writes scope-snapshot.json
  Then the write goes through _atomic_write (temp file + os.replace)

Scenario: the integrity anchor is preserved byte-for-byte
  Given the sidecar written via _atomic_write
  When _scope_findings re-reads it
  Then _md5_text(on-disk) == state.tasks[slug].scope.snapshot_md5 (no false diverged/missing)
  And a clean build gate still PASSes

Scenario: an undeclared task still writes no sidecar
  Given a task with NO §5 Scope line crossing tests->build
  When _build_entry runs
  Then no scope-snapshot.json exists (the unlink/skip path is unchanged)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_build_entry (add.py ~1273), the declared-scope branch:
  - side.write_text(payload, encoding="utf-8")
  + _atomic_write(side, payload)          # temp file + os.replace; payload UNCHANGED (no newline)

Unchanged: payload = json.dumps({"version":1,"files":_scope_walk(...)}, sort_keys=True)
           state.tasks[slug].scope.snapshot_md5 = _md5_text(payload)   # same bytes -> same md5
           the `else:` UNDECLARED branch (pop scope + unlink sidecar)
           _scope_findings reader (md5 compare)

Invariants: byte-identical sidecar (md5 anchor preserved) · 3-tree mirror + ENGINE_MD5 re-pin ·
            no new reject code · no behavior change beyond crash-safety.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (route the scope-sidecar write through _atomic_write).
Least-sure flag surfaced at freeze: [contract] _atomic_write writes `text` VERBATIM (no trailing newline, verified at add.py:231 `fh.write(text)`), so `payload` lands byte-identical and `state.tasks[slug].scope.snapshot_md5` stays valid; cost if wrong = appending "\n" like save_state's caller would mismatch every snapshot md5 (mass false tamper) — the md5_anchor_preserved test guards exactly that. Engine change → 3-tree mirror + ENGINE_MD5 re-pin.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the atomic-write seam + the preserved anchor (3 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_scope_sidecar_written_atomically: spy on add._atomic_write; _arm a declared-scope task across tests->build; assert the sidecar path is among the _atomic_write calls (RED now — raw write_text, not in calls)
  - test_sidecar_md5_anchor_preserved: after _arm, assert _md5_text(sidecar on-disk) == state.tasks[slug].scope.snapshot_md5 AND the build gate PASSes (guards against a trailing-newline regression)
  - test_undeclared_task_writes_no_sidecar: _arm with NO §5 Scope line; assert scope-snapshot.json does not exist (the unlink/skip path unchanged)
</test_plan>

Tests live in: `add-method/tooling/test_scope_gate_enforce.py` · MUST run red (raw write_text) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_scope_gate_enforce.py`   <!-- canonical engine + bundled mirror + the ENGINE_MD5 pin + the test home; .add/tooling/add.py dogfood mirror is pruned (.add excluded), synced via prepare_bundle -->
Strategy (ordered batches): 1. add the 3 tests to test_scope_gate_enforce.py (1 red atomic-spy + 2 controls). 2. swap the one line in _build_entry to _atomic_write. 3. green; mirror canonical -> .add + _bundled + re-pin ENGINE_MD5; full suite + parity green.
Safety rule (feature-specific): pass `payload` with NO added newline (preserve the md5 anchor). Validate-then-write order untouched.
Code lives in: `add-method/tooling/add.py` (+ its two mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.
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

- [x] all tests pass — full suite 1806/0 (was 1803 on this branch; +3 F11 tests); parity + dual-tree md5 green on the re-pin
- [x] coverage did not decrease — +3 tests (atomic-write seam + md5-anchor-preserved + undeclared-skip); none removed
- [x] no test or contract was altered during build — the 3 §4 tests were authored in the tests phase (1 RED) and unchanged since; build edited only add.py (the one-line swap) + engine_pin re-pin + the _bundled mirror — not the test file (no tripwire divergence)
- [x] the green was EARNED, not gamed — refute-read (manual): the atomic-write test SPIES on the real _atomic_write and asserts the sidecar Path is among its calls (RED proven when it was a raw write_text); the md5-anchor test reads the ON-DISK sidecar and compares to the state anchor + drives a real gate PASS — it would catch a trailing-newline regression; not vacuous
- [x] concurrency / timing of the risky operation is safe — THIS IS the safety fix: temp-file + os.replace makes the sidecar write crash-atomic (a torn file can no longer survive), matching save_state
- [x] no exposed secrets, injection openings, or unexpected dependencies — one-line swap to an existing helper; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — engine mirrored ×3, ENGINE_MD5 re-pinned 310a8ed7 → 73f9609e
- [x] a person reviewed and approved the change — Tin Dang froze v1 (route the sidecar write through _atomic_write)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] crossing tests→build writes scope-snapshot.json via _atomic_write (temp+replace) — confirmed by test_scope_sidecar_written_atomically (the sidecar Path appears in the _atomic_write call list)
- [x] the integrity anchor is byte-preserved — confirmed: _md5_text(on-disk sidecar) == state anchor, and a clean build gate PASSes (test_sidecar_md5_anchor_preserved); the UNDECLARED skip path is unchanged

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_atomic_write(side, payload)` calls the existing helper (line 222); `side` and `payload` are the same locals as before; the reader `_scope_findings` and the `else` unlink branch are untouched
- [x] DEAD-CODE — no orphaned symbol; the raw write_text is replaced, not left behind
- [x] SEMANTIC (code) — re-read _atomic_write: writes `text` verbatim via `fh.write(text)` (no newline), so `payload` lands byte-identical → snapshot_md5 holds; confirmed empirically by the md5-anchor test

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
