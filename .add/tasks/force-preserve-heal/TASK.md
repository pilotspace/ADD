# TASK: F8: new-task --force preserves the monotonic heal counter

slug: force-preserve-heal · created: 2026-06-25 · stage: mvp
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
  - `add-method/tooling/add.py:cmd_new_task` (1030–1119) — at line 1107 `state["tasks"][slug] = {fresh ground record}` REPLACES the entire task record on a `--force` overwrite, dropping `heal`. THE FIX SITE.
  - `add-method/tooling/add.py:cmd_new_task` force guard (1041–1042) — `task_md.exists() and not args.force -> _die("already exists")`; WITH `--force` the overwrite proceeds (the path that loses `heal`).
  - `add-method/tooling/add.py:_heal_or_escalate` (4515–4549) — owns `t["heal"] = {"attempts", "history"}`; the MONOTONIC counter (line 4527: "never auto-resets — cmd_phase is unguarded, so a reset would be a zero-human cap bypass").
  - `add-method/tooling/add.py:HEAL_CAP` (line 61) = 3 — the cap a reset would launder.
Context (working folder):
  - `add-method/tooling/test_heal_then_escalate.py` — the heal suite + the monotonic-counter charter (lines 15–18). The F8 test lands HERE (`_Board` harness: `_silent` / `_run`).
  - Engine mirrored ×3 under the ENGINE_MD5 pin (`engine_pin.py`); a change re-mirrors + re-pins.
Honors (patterns / conventions):
  - The MONOTONIC heal invariant (verify-integrity): the cap counts confirmed cheats; it must not reset without a human. A `--force` re-create is not an auto-reset by intent, but it drops `heal` as collateral — same cap-bypass risk.
  - validate-then-write; minimal record carry-forward (preserve only what the invariant needs).
  - Mirror-3-trees + ENGINE_MD5 re-pin on any add.py edit; red/green TDD.
Anchors the contract cites: `cmd_new_task` · `heal` (attempts/history) · `HEAL_CAP`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `new-task --force` over an existing task PRESERVES the monotonic `heal` counter — a `--force` re-create cannot launder the self-heal cap back to zero.
Framings weighed: preserve-heal (chosen) · refuse-force-while-healing · preserve-all-forensic-keys
  - chosen: capture the prior record's `heal` BEFORE the overwrite and re-attach it to the fresh record; everything else resets (it IS an overwrite). Honors the monotonic invariant with one carry-forward line.
  - refuse-force-while-healing: `--force` dies when `heal.attempts > 0`. Rejected — over-restricts a legitimate TASK.md rewrite; the cap counts cheats, it does not forbid edits.
  - preserve-all-forensic-keys (heal + tripwire + reopens): broader. Rejected for scope — only `heal` is a cap-bypass vector (tripwire re-snapshots at tests->build; reopens/waiver are history, not gates). Noted as a possible follow-up.
Must:
<must>
  - A `new-task --force` over a task whose record has a `heal` key carries that `heal` (attempts + history) UNCHANGED into the new record.
  - A `new-task --force` over a task with NO `heal` key adds none — no fabricated counter.
  - The rest of the overwrite is unchanged: phase resets to `ground`, fresh title/created/updated, TASK.md re-rendered.
  - `new-task` WITHOUT `--force` on an existing task still refuses `already exists` (unchanged).
</must>
Reject:
<reject>
  - `new-task <existing>` without `--force` -> "already exists" (unchanged behaviour)
</reject>
After:
<after>
  - The monotonic heal counter survives a `--force` re-create; the self-heal cap cannot be reset to zero without a human.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] Scope = preserve `heal` ONLY — CONFIRMED heal-only (human 2026-06-25). Tripwire was weighed and REJECTED as a no-op: `_build_entry` re-snapshots the tripwire UNCONDITIONALLY at every tests->build (add.py:1252, "a legit change-request re-snapshots cleanly"), and `--force` resets the task to `ground`, so any preserved baseline is overwritten before `_tamper_guard` ever reads it. `heal` is the ONLY anti-cheat state that survives a re-crossing (only `_heal_or_escalate` touches it) — so it is the only one worth carrying. `reopens`/`waiver` are forensic history, not gates.
  - [x] `--force` is a re-create, not an intentional reset — confirmed: line 1107 unconditionally replaces the record, so `heal` is collateral loss, not by design.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: --force preserves an accrued heal counter
  Given an existing task whose record has heal {attempts: 2, history: [...]}
  When I run `add.py new-task <slug> --force`
  Then the new record carries heal.attempts == 2 and the history unchanged
  And the rest of the record is fresh (phase == ground)

Scenario: --force over a task with no heal fabricates none
  Given an existing task with no heal key
  When I run `add.py new-task <slug> --force`
  Then the new record has no heal key (no zero-counter invented)

Scenario: new-task without --force still refuses an existing task
  Given an existing task
  When I run `add.py new-task <slug>` (no --force)
  Then it exits 1 with "already exists"
  And the task's record is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cmd_new_task(args)  — when args.force AND state["tasks"][slug] already exists:
    prior_heal = state["tasks"].get(slug, {}).get("heal")   # capture BEFORE the overwrite
    state["tasks"][slug] = { title, phase:"ground", gate:"none", milestone, depends_on, created, updated }
    if prior_heal is not None:
        state["tasks"][slug]["heal"] = prior_heal           # monotonic — survives the --force re-create
  ok                       -> task re-created; heal carried forward iff it existed
  (exists & not --force)   -> _die "already exists"   (unchanged)
Schema: state.tasks[slug].heal = {attempts:int, history:list} — PRESERVED across a --force overwrite.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (heal-only).
Least-sure flag surfaced at freeze: [scope] heal-only — `tripwire` was considered and REJECTED as a no-op (re-snapshotted unconditionally at the next tests->build per add.py:1252, so a preserved baseline is overwritten before `_tamper_guard` reads it; `heal` is the only anti-cheat state that survives a re-crossing). [test] the preservation test pokes `heal` into state directly (it asserts the --force CARRY behavior, not the heal mechanism); the other two scenarios stay green before+after (they pin unchanged behavior).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject (3 scenarios), in the heal suite.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_force_preserves_heal_counter: new-task t; poke state heal={attempts:2, history:[{...}]}; `new-task t --force`; assert state heal.attempts==2 + history intact + phase=="ground"
  - test_force_over_fresh_task_adds_no_heal: new-task t (no heal); `new-task t --force`; assert "heal" not in the record
  - test_new_task_no_force_still_refuses_existing: new-task t; `new-task t` (no --force) -> exit 1 + "already exists" + record unchanged
</test_plan>

Tests live in: `add-method/tooling/test_heal_then_escalate.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_heal_then_escalate.py`   <!-- canonical engine + bundled mirror + the ENGINE_MD5 pin + the heal suite; the dogfood .add tree is pruned from the scope walk so needs no token -->
Strategy (ordered batches): 1. add the 3 red tests to test_heal_then_escalate.py. 2. in cmd_new_task, capture prior heal before the overwrite and re-attach it after building the fresh record. 3. green; mirror canonical -> .add/tooling + _bundled + re-pin ENGINE_MD5; full suite + parity green.
Safety rule (feature-specific): preserve ONLY `heal` (the cap-bypass vector); do not carry any other prior key (the overwrite must stay a real reset for everything else).
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

- [x] all tests pass — full suite 1787/0 (was 1784; +3 F8 tests), parity + dual-tree-md5 green on the re-pin
- [x] coverage did not decrease — +3 behavioral tests in the heal suite; none removed
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; build edited only cmd_new_task (×3 trees) + engine_pin.py; the 3 tests were authored in the tests phase (1 red), unchanged since
- [x] the green was EARNED, not gamed — refute-read (manual, change is one capture+re-attach): the carry-forward is guarded by `if args.force` and `if prior_heal is not None`, so a non-force create and a never-healed task are untouched (proven by test_force_over_fresh_task_adds_no_heal staying green before+after); the preservation test pokes a real heal record and asserts attempts==2 survives — not a stubbed value
- [x] concurrency / timing of the risky operation is safe — pure in-memory dict capture before the single save_state; no new IO
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reads an existing state key
- [x] layering & dependencies follow CONVENTIONS.md — mirror-3-trees synced + ENGINE_MD5 re-pinned 4d682bcf → a3f99f72
- [x] a person reviewed and approved the change — Tin Dang froze the contract heal-only (2026-06-25), after I surfaced that the tripwire fold-in would be a no-op

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] after `new-task --force` over a task with heal.attempts=2, state.tasks[slug].heal.attempts is still 2 (counter not laundered) — confirmed by test_force_preserves_heal_counter reading state.json
- [x] after `new-task --force` over a never-healed task, the record has no `heal` key (no fabricated zero-counter) — confirmed by test_force_over_fresh_task_adds_no_heal

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — new local `prior_heal` is read at the re-attach `if prior_heal is not None` two lines down; no orphan
- [x] DEAD-CODE (code) — no unused symbol; the capture is consumed in the same function
- [x] SEMANTIC (prose / non-code) — read _build_entry (add.py:1248–1252) + _heal_or_escalate (4515–4549): confirmed the tripwire is re-snapshotted unconditionally at tests->build (so cross-force preservation is a no-op) while heal is only touched by the router (so its preservation is real) — the heal-only scope is correct, not a shortcut

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of `new-task --force` over a healing task (a forced re-create that carries heal forward is the monitor that the cap held).

### Spec delta
- [SPEC · open] anti-cheat state that is RE-DERIVED at a phase crossing (the tripwire, re-snapshotted unconditionally at tests->build) cannot be protected by carry-forward — closing a `--force`/`reopen` tamper-launder needs a REFUSE-style barrier instead (evidence: F8 tripwire fold-in proved a no-op at add.py:1252).

### Competency deltas
- [ADD · folded] before "preserving" state across a re-create, check whether the engine RE-DERIVES it downstream — a carry-forward of re-derived state (tripwire) is a hollow guard; only state owned by a single writer (heal ← _heal_or_escalate) survives meaningfully (evidence: F8 — the approved tripwire fold-in was withdrawn after reading _build_entry's unconditional re-snapshot). [folded foundation-version 51]
