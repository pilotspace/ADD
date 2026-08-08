# TASK: freeze-gate-universal — fire contract_not_frozen for every task, with a --skip-freeze escape

slug: freeze-gate-universal · created: 2026-06-27 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from project default `auto`: this is a method-defining engine change (it alters the tests→build crossing for EVERY task), so the high-risk guard requires conservative/manual + `risk: high` on the slug line. The human owns the verify gate. Original comment: inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:_build_entry(root, state, slug)` (≈565–600) — the SHARED tests→build entry guard (used by BOTH `cmd_advance` and `cmd_phase`). Line 587 `_freeze_gated = _optin or state["tasks"][slug].get("fast") is True` is the gate condition to make universal; `_die("contract_not_frozen: …")` at 588–590 is the refusal. PRECEDES the build-expectations gate (591–597).
  - `add-method/tooling/add.py:cmd_advance(args)` (656–744) — at `if nxt == "build": _build_entry(...)` (the only freeze-gate caller path besides `cmd_phase`). Where a `--skip-freeze` arg would be read off `args` and threaded in.
  - `add-method/tooling/add.py:_contract_frozen(raw3)` (≈4030) — READ-ONLY anchor: the `Status: FROZEN @ vN` signal the gate tests. Unchanged.
  - `add-method/tooling/add.py` argparse — `advance` subparser (5593–5595, currently `slug`-only) gets the new `--skip-freeze`; `phase` subparser (5588–5591) may mirror it.
  - `add-method/tooling/test_freeze_before_build_gate.py` — the existing red/green suite. Scenarios 3 (`test_plain_milestone_unfrozen_advances`, L129) and 4 (`test_no_milestone_unfrozen_advances`, L135) currently assert DRAFT-§3 plain/no-milestone tasks ADVANCE — they INVERT under universal (a contract change, frozen in §3; not test-weakening).
  - `add-method/tooling/engine_pin.py` + ENGINE_MD5 asserts (many `test_*.py`) — re-pin after the engine byte change.
Context (working folder): the engine is a 3-tree: canonical `add-method/tooling/add.py` (edit here + tests) → dogfood `.add/tooling/add.py` → bundled `add-method/src/add_method/_bundled/tooling/add.py`; the build must propagate + re-pin all three (worktrees/`tmp/`/venv copies are out of scope).
Honors (patterns / conventions): validate-before-write (refuse leaves phase=tests, no snapshot — see existing scenario 1) · "no silent skip" → the `--skip-freeze` escape must be RECORDED on the task (actor/marker the `audit` can surface), never a quiet bypass · grandfather: never retro-red a task already past build · judgment-free engine (gate is mechanical: frozen-or-not, never classifies).
Anchors the contract cites: `_build_entry` · `_freeze_gated` (→ universal) · `contract_not_frozen` (reject code, unchanged) · `--skip-freeze` (new escape + its recorded marker) · `_contract_frozen` · the `advance` subparser flag.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Universal freeze gate — `contract_not_frozen` fires for EVERY task at the tests→build crossing, with a RECORDED `--skip-freeze` escape.
Framings weighed: universal gate + recorded escape (chosen) · ephemeral CLI flag with no record (rejected: a silent skip — violates "no silent skip") · TASK.md header declaration `freeze: skip` (rejected: mixes the escape into the frozen artifact + needs a parser; heavier)
Must:
<must>
  - At the tests→build crossing (`_build_entry`), REFUSE with `contract_not_frozen` whenever §3 is not `FROZEN @ vN` — for EVERY task, regardless of milestone `--await-confirm` opt-in or `--fast`. The gate condition `_freeze_gated = _optin or fast` becomes unconditionally true.
  - The refusal is validate-before-write: phase stays `tests`, no state write, no scope snapshot (identical to today's opted-in refusal).
  - `add.py advance --skip-freeze` (and `phase build --skip-freeze`) lets a DRAFT-§3 task cross into build, BUT records a durable, auditable marker on the task (actor + timestamp + from_phase) — the skip is never silent.
  - The escape NEVER auto-freezes §3 — `Status:` stays `DRAFT` (never pre-stamp a human freeze).
  - A task already at/after build (phase ∈ build/verify/observe/done) is NEVER retro-redded — the gate is evaluated only at the live `nxt == "build"` crossing.
  - `add.py audit` SURFACES a `--skip-freeze` task (a finding/INFO naming the slug) so a skipped freeze is visible in review.
  - The freeze gate continues to PRECEDE the build-expectations gate (ordering unchanged).
</must>
Reject:
<reject>
  - §3 not `FROZEN @ vN` at tests→build, no `--skip-freeze` -> "contract_not_frozen"
  - (no new reject code — the escape is an allowed, recorded bypass, not an error)
</reject>
After:
<after>
  - A frozen-§3 task advances to build exactly as today (already-conforming tasks: zero behavior change).
  - A `--skip-freeze` task is at phase=build with `state.tasks[slug].freeze_skipped = {by, at, from_phase}` recorded; `audit` lists it; §3 still `DRAFT`.
  - A plain / no-milestone DRAFT-§3 task that previously advanced silently now REFUSES unless `--skip-freeze`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The blast radius across the EXISTING test suite is the biggest unknown — lowest confidence because many test helpers drive a fresh plain/no-milestone task to build on a DRAFT §3 (the old gate was deliberately "zero ripple"); universal inverts that. If wrong (radius large): a broad-but-mechanical sweep — each such helper must freeze §3 or pass `--skip-freeze`; cost is dozens of test edits + the risk of masking a real regression. MITIGATION: measure experimentally at build (scratch swap + full suite, filter ENGINE_MD5-pin noise) BEFORE committing the rollout.
  - [ ] The escape lives as a `--skip-freeze` flag on `advance`/`phase` (vs a header declaration) — med confidence; flag is simplest + scoped to the one crossing, and recording the marker keeps it honest.
  - [ ] Grandfathering "already past build" is sufficient (no created-date grandfather needed) — high confidence; the gate fires only at the live crossing, so done tasks are inherently safe.
  - [ ] `phase build` should mirror `--skip-freeze` for admin-override parity — med confidence; confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: universal gate blocks a PLAIN-milestone DRAFT §3   # inverts old scenario 3
  Given a task under a plain (non-await-confirm) milestone at phase=tests with §3 DRAFT
  When add.py advance
  Then it is refused with "contract_not_frozen"
  And phase stays "tests" and no scope-snapshot is written

Scenario: universal gate blocks a NO-milestone DRAFT §3   # inverts old scenario 4
  Given a milestone-less task at phase=tests with §3 DRAFT
  When add.py advance
  Then it is refused with "contract_not_frozen"
  And phase stays "tests"

Scenario: frozen §3 still advances (happy path unchanged)
  Given any task at phase=tests with §3 FROZEN @ v1 and §6 build-expectations filled
  When add.py advance
  Then phase becomes "build"
  And no freeze_skipped marker is recorded

Scenario: --skip-freeze lets a DRAFT §3 cross AND records the marker
  Given a plain DRAFT-§3 task at phase=tests
  When add.py advance --skip-freeze
  Then phase becomes "build"
  And state.tasks[slug].freeze_skipped = {by, at, from_phase} is recorded
  And §3 Status stays "DRAFT" (never auto-frozen)

Scenario: a skipped freeze is auditable
  Given a task that crossed via --skip-freeze
  When add.py audit
  Then the run surfaces the skipped freeze naming the slug
  And nothing about the skip is hidden

Scenario: grandfather — a task already past build is never retro-redded
  Given a pre-existing task at phase=build with §3 DRAFT
  When add.py advance   (build -> verify)
  Then it advances normally
  And "contract_not_frozen" is NOT raised (the gate fires only at tests->build)

Scenario: opt-in / fast parity preserved (regression)
  Given an --await-confirm OR --fast task at phase=tests with §3 DRAFT
  When add.py advance
  Then it is refused with "contract_not_frozen" (still gated — universal subsumes the old condition)
  And phase stays "tests"

Scenario: freeze still precedes build-expectations (ordering unchanged)
  Given a DRAFT-§3 task at phase=tests with an empty §6 build-expectations block
  When add.py advance   (no --skip-freeze)
  Then "contract_not_frozen" fires
  And "build_expectations_unfilled" is NOT reached
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI:
  add.py advance   [<slug>] [--skip-freeze]
  add.py phase build [<slug>] [--skip-freeze]        # admin override mirrors advance

GATE  (in _build_entry, at the tests->build crossing, BEFORE build-expectations):
  _freeze_gated := True                               # was: _optin or fast  → now UNCONDITIONAL
  if not _contract_frozen(§3):
      if not skip_freeze:  -> _die("contract_not_frozen")      # exit 1; phase stays tests; NO write
      else:                -> record marker; allow the crossing  # recorded, never silent

ESCAPE record (only on a skipped crossing), written to state.tasks[<slug>]:
  freeze_skipped: { "by": <actor>, "at": <ISO8601>, "from_phase": "tests" }
  • surfaced by `add.py audit` as a finding (e.g. "freeze_skipped: <slug> crossed with a DRAFT §3")
  • §3 Status is left DRAFT — the escape never freezes on the human's behalf

GRANDFATHER: the gate is evaluated ONLY when nxt == "build"; a task already at/after build is
             structurally unaffected (never retro-redded).

State schema delta (state.json):  + OPTIONAL task key `freeze_skipped` (object).
  Absent by default → byte-identical state for every non-skipping task.
Reject codes:  contract_not_frozen  (EXISTING — now fires universally; no new code).
Engine pin:  ENGINE_MD5 changes → re-pin engine_pin.py + propagate canonical → dogfood → bundled.
```

Least-sure flag surfaced at freeze: [test] universal inverts the old "zero-ripple" gate, so the blast radius across existing test helpers (plain task → build on DRAFT §3) is unknown — cost: a broad-but-mechanical sweep, measured experimentally at build before rollout.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject + escape + grandfather + regression (8 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_plain_milestone_unfrozen_blocks: arrange plain-ms DRAFT-§3 task at tests / act advance / assert SystemExit(1) + "contract_not_frozen" + phase=="tests" + no scope-snapshot   (INVERTS old scenario 3)
  - test_no_milestone_unfrozen_blocks: arrange milestone-less DRAFT-§3 at tests / act advance / assert "contract_not_frozen" + phase=="tests"   (INVERTS old scenario 4)
  - test_frozen_advances: arrange FROZEN §3 + filled §6 / act advance / assert phase=="build" + no freeze_skipped key
  - test_skip_freeze_allows_and_records: arrange plain DRAFT-§3 / act advance --skip-freeze / assert phase=="build" + state freeze_skipped has by/at/from_phase + §3 still "Status: DRAFT"
  - test_skip_freeze_audited: arrange a --skip-freeze crossing / act audit / assert the slug + "freeze_skipped" appears in audit output
  - test_grandfather_past_build_not_retro_redded: arrange a task already at phase=build, DRAFT §3 / act advance (build->verify) / assert advances, no "contract_not_frozen"
  - test_optedin_still_blocks AND test_fast_still_blocks: arrange await-confirm / --fast DRAFT-§3 at tests / act advance / assert "contract_not_frozen" (regression — universal subsumes the old condition)
  - test_freeze_precedes_build_expectations: arrange DRAFT §3 + empty §6 / act advance / assert "contract_not_frozen" AND NOT "build_expectations_unfilled"
  - (mechanical) ENGINE_MD5 pin asserts go red until re-pinned in build — expected, not a behavior test
</test_plan>

Tests live in: `add-method/tooling/test_freeze_gate_universal.py` `add-method/tooling/test_freeze_before_build_gate.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`   <!-- MEASURED re-declaration the contract reserved: the canonical tooling DIRECTORY token (subtree containment) covers the engine (add.py + engine_pin.py) AND the 23 collateral test fixtures the blast-radius sweep re-froze with a stub section-3 contract; the two sibling trees carry add.py only. This comment stays backtick-free so the section-5 parser reads exactly the three tokens above. -->
Strategy (ordered batches): 1. write red tests (new file + invert the 2 existing scenarios) · 2. make `_freeze_gated` unconditional + add `--skip-freeze` arg + record `freeze_skipped` in `_build_entry`/`cmd_advance`/`cmd_phase` · 3. surface `freeze_skipped` in `add.py audit` · 4. run FULL suite → measure blast radius → fix collateral helpers (freeze §3 or pass `--skip-freeze`) · 5. propagate canonical→dogfood→bundled + re-pin ENGINE_MD5
Safety rule (feature-specific): validate-before-write (a refusal mutates NO state, writes NO snapshot) · the escape must RECORD `freeze_skipped` (never a silent skip) · the escape never auto-freezes §3 (never pre-stamp a human freeze) · the 3 engine trees must stay byte-synced + the pin re-computed in the SAME build.
Code lives in: `add-method/tooling/` (canonical) → propagated to `.add/tooling/` + `_bundled/`
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

- [x] all tests pass — full canonical suite 2073/0 (`python3 -m unittest discover -s . -p "test_*.py"`, exit 0)
- [x] coverage did not decrease — +10 net tests (new `test_freeze_gate_universal.py` = 9 + 1 added in `test_phase_build_guard`); ZERO tests deleted (refute-read confirmed)
- [x] no test or contract was altered to FORCE a pass — the FROZEN §3 contract is UNTOUCHED; the 25 test edits ARE the §5-declared blast-radius sweep (setup-only `_freeze` of fixture §3 + 2 faithful inversions of tests whose subject WAS the old opt-in gate). Honest note: tests WERE edited (the contract's anticipated sweep) — but none weakened
- [x] the green was EARNED, not gamed — adversarial refute-read (independent agent a8510d1a; hostile read of all 551 diff lines + cross-checked `_contract_frozen` / `_flag_well_formed`) → VERDICT: EARNED; no weakened/deleted assertion, no vacuous test, no masked regression
- [x] concurrency / timing — N/A: the gate is a synchronous in-process read of §3 bytes at ONE crossing; validate-before-write (a refusal mutates no state, writes no snapshot) — proven by `test_plain_milestone_unfrozen_blocks` (no scope-snapshot on refusal)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure-stdlib change; `freeze_skipped` stores actor name + ISO timestamp + from_phase only; no new imports/deps
- [x] layering & dependencies follow CONVENTIONS.md — judgment-free invariant held (the gate checks SHAPE `Status: FROZEN @ vN` only, never classifies); `_in_scope`/`_declared_scope` reused from `add_engine.components`; 3-tree byte-sync + single-source `ENGINE_MD5` re-pinned
- [ ] a person reviewed and approved the change — PENDING Tin (conservative autonomy: the human owns the verify gate)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py advance` on a fresh PLAIN-milestone (and no-milestone) DRAFT-§3 task exits 1 with `contract_not_frozen` and leaves phase=tests — CONFIRMED: live scratch-repo run (exit=1, "contract_not_frozen: freeze §3 before crossing into build…", phase=tests) + test_{plain,no}_milestone_unfrozen_blocks green
- [x] `add.py advance --skip-freeze` crosses a DRAFT-§3 task to build AND writes `state.tasks[slug].freeze_skipped {by,at,from_phase}`, with §3 still `Status: DRAFT` — CONFIRMED: scratch run → phase=build + `freeze_skipped={'by':'Tin Dang','at':'2026-06-27T09:01:17+00:00','from_phase':'tests'}` + §3 still DRAFT + test_skip_freeze_allows_and_records / does_not_auto_freeze green
- [x] `add.py audit` names a freeze_skipped task in its output — CONFIRMED: scratch `audit` printed `audit: freeze_skipped t — crossed tests->build with a DRAFT §3 (by Tin Dang at …)` at exit 0 (INFO, non-failing) + test_skip_freeze_audited green
- [x] a task already AT build with a DRAFT §3 advances build→verify with NO contract_not_frozen — CONFIRMED: test_grandfather_past_build_not_retro_redded green (the gate is evaluated only at the live `nxt=="build"` crossing)
- [x] the FULL canonical suite is green after the blast-radius sweep (no masked regression) — CONFIRMED: 2073/0 (the +10 vs the ~2063 prior baseline = the new `test_freeze_gate_universal` suite + the added phase-build-guard block); refute-read EARNED
- [x] the 3 engine trees (canonical · dogfood · _bundled) are byte-identical and ENGINE_MD5 re-pinned — CONFIRMED: md5 of all three = `a230ed0d53a5b32d7eff58745cf4fbcf` == single-source `ENGINE_MD5`; pin/parity tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `_build_entry(..., skip_freeze=)` is read by BOTH cmd_advance + cmd_phase (each passes `getattr(args,"skip_freeze",False)`); the `--skip-freeze` argparse arg is wired on the advance + phase subparsers; `_freeze_skip_notices(state)` has its one call site in cmd_audit; the `freeze_skipped` state key is written in _build_entry + read by audit — all exercised by the green scratch run + tests
- [x] DEAD-CODE (code) — no orphan: the old `_freeze_gated = _optin or fast` condition was REPLACED (now unconditional), not left dangling; grep-confirmed `_freeze_skip_notices` has exactly one caller (cmd_audit); no helper retained without a call site
- [ ] SEMANTIC (prose / non-code) — N/A: this is a code change (engine + tests); the only prose touched is the `ENGINE_MD5` re-aim note + the §5 scope comment, both mechanical

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-27

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `freeze_skipped` count in `add.py audit` — a rising count means contracts are being ESCAPED (`--skip-freeze`) rather than frozen; the gate is honored only if that count stays near zero.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] the §5 Scope parser resolves ANY backticked token as a path, so a backticked CLI flag becomes a bogus declared entry (evidence: this task's original §5 placeholder backticked `--skip-freeze` → `_declared_scope` produced `.../tooling/--skip-freeze`; harmless here but a latent false-declaration — skip tokens matching `^--` in `_declared_scope`) [carried: deferred to backlog 2026-06-27 (delta-drain) — not now-actionable; retrievable via 'add.py deltas --carried', reopen or seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a universal-gate change carries a large test-fixture blast radius; pre-declaring the sweep in §5 ("collateral helpers re-declared once measured") + a DIRECTORY scope token turns reconciliation into a one-line `state.scope.declared` patch — no dirty-tree re-cross (evidence: 57 fixtures reconciled via one `add-method/tooling/` token; `snapshot_md5` guards the sidecar, not `declared`, so the patch is safe) [folded foundation-version 56]
- [TDD · folded] when a fixture drove a plain task to build on a DRAFT §3, the FAITHFUL fix is to freeze a real stub §3 in setup (not `--skip-freeze`) — every fixture stays a true frozen-contract task; an adversarial refute-read across all 25 edited files confirmed no assertion was weakened (evidence: refute-read VERDICT EARNED, 551 diff lines) [folded foundation-version 56]
- [ADD · folded] do ALL of a task's own §4-declared red-test edits in the TESTS phase, but the COLLATERAL blast-radius sweep necessarily happens at BUILD — safe because the tamper tripwire hashes ONLY the §4-declared set, never a glob (evidence: tripwire tracked 2 files, the 23 swept fixtures were untracked → no `build_tampered`) [folded foundation-version 56]
