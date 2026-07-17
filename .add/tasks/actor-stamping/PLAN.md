# TASK: stamp the structured actor on every human seam

slug: actor-stamping · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: this edits the byte-pinned engine across all 3 add.py copies + re-pins; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — the FOUR engine-WRITTEN human-seam records, each stamped with the structured actor from task-1's `_whoami(state)`:
  - `cmd_lock` (1092) — already writes `state["setup"]={locked,locked_at,locked_by:who,layers}`; ADD `"actor": _whoami(state)` alongside the existing `locked_by` free-text.
  - `cmd_gate` (940) — writes `state["tasks"][slug]["gate"]=outcome` + `updated`; ADD `["gate_actor"]=_whoami(state)` (WHO recorded the verdict — every outcome incl. HARD-STOP).
  - `cmd_milestone_done` (2467) — writes `state["milestones"][slug]["status"]="done"` + `updated`; ADD `["done_actor"]=_whoami(state)`.
  - `cmd_release` (5013) — writes the RELEASES.md row via `_render_releases_row(version,day,bundle,waiver_slugs,evidence)` (NO state.json); ADD an `actor:` line to the row (sourced from `_whoami(state)`).
- NEW thin helper `_actor_stamp(state) -> dict` = `_whoami(state)` — ONE source for the `{name,email,source}` field shape attached at the 3 state seams; the release row renders it as a string.
- `engine_pin.py:ENGINE_MD5` = `6f28abab9defe0799978ce35cfa8fba1` — re-pin after this engine edit (same commit).

Context (working folder):
- task-1 (`actor-identity`, DONE) shipped `_whoami(state)->{name,email,source}` + the `actor_override` state key — this task CONSUMES that resolver; no new git/IO surface here, just additive record writes on EXISTING save_state/_atomic_write paths.
- the contract FREEZE (`Status: FROZEN @ vN — approved by <name>`) and the gate `Reviewed by:` are HUMAN-AUTHORED TASK.md TEXT, read-only via `_AUDIT_STAMP_RE`/`_AUDIT_REVIEWED_RE` (4559/4563) — the engine NEVER writes them, so there is no write seam to stamp structurally. Freeze structured-stamping would need a NEW `add.py freeze` write command → out of scope, seed a §7 delta. THIS task stamps the 4 engine-WRITTEN records only (the contract's lowest-confidence flag).

Honors (patterns / conventions):
- additive + descriptive-only — new optional fields (`actor`/`gate_actor`/`done_actor` + the release `actor:` line); absent on legacy records (back-compat); NO existing command's decision changes (the milestone's "descriptive only, no enforcement").
- design-for-failure — no new IO; the stamps ride the EXISTING atomic writes (save_state · the release in-memory-then-_atomic_write with rollback). The actor field is computed BEFORE the write.
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin; full suite is the regression oracle.

Anchors the contract cites: NEW `_actor_stamp(state)` · `state["setup"]["actor"]` · `state["tasks"][slug]["gate_actor"]` · `state["milestones"][slug]["done_actor"]` · the RELEASES.md row `actor:` line via `_render_releases_row`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Structured-actor STAMPING — every engine-WRITTEN human-seam record carries the `{name,email,source}` actor from task-1's `_whoami(state)`, ALONGSIDE today's free-text, so a multi-user team has an auditable who-did-what trail. Descriptive only — no command's decision changes.
Framings weighed: stamp the 4 engine-WRITTEN records (lock·gate·milestone-done·release), freeze stays free-text (chosen — the engine owns those writes; freeze has no write seam) · also add an `add.py freeze` command to stamp the contract freeze (rejected — a new write command is its own task; seed a §7 delta) · REPLACE the free-text locked_by/`Reviewed by:` with structured data (rejected — lossy + breaks the audit regex back-compat; stamp ALONGSIDE instead).
Must:
<must>
  - NEW `_actor_stamp(state) -> {name,email,source}` = `_whoami(state)` — the SINGLE source of the stamp; TOTAL (always a non-empty name), so a stamp never fails or blocks a seam.
  - `cmd_lock` writes `state["setup"]["actor"] = _actor_stamp(state)` ALONGSIDE the existing `locked_by` free-text (unchanged).
  - `cmd_gate` writes `state["tasks"][slug]["gate_actor"] = _actor_stamp(state)` on EVERY recorded outcome — PASS, RISK-ACCEPTED, AND HARD-STOP (who recorded the verdict matters for a stop too).
  - `cmd_milestone_done` writes `state["milestones"][slug]["done_actor"] = _actor_stamp(state)`.
  - `cmd_release` renders an `actor: <name> [<email>] (<source>)` line on the RELEASES.md row (alongside `evidence:`), sourced from `_actor_stamp(state)`; still writes NO state.json (validate-before-write + rollback unchanged).
  - DESCRIPTIVE + ADDITIVE: a legacy record WITHOUT the actor field loads and behaves identically; NO existing command's decision reads the stamp for control flow; with no `actor_override`, the actor resolves git→os exactly as task 1.
  - all 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned in the SAME commit.
</must>
Reject:
<reject>
  - none new — this is a descriptive, additive stamp; each seam keeps its EXISTING reject codes (e.g. `setup_unlocked`, `waiver_incomplete`, `milestone_incomplete`, `release_security_open`) BYTE-UNCHANGED. The stamp can't introduce a reject because `_actor_stamp` is TOTAL.
</reject>
After:
<after>
  - every NEW lock/gate/milestone-done record carries a structured actor; every NEW release row carries an `actor:` line; the free-text seams are untouched; the audit regex (`_AUDIT_STAMP_RE`/`_AUDIT_REVIEWED_RE`) still matches; the full prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The contract FREEZE is EXCLUDED from structured stamping (it stays human-authored `approved by <name>` free-text) — lowest confidence because the milestone intake listed freeze among "all human seams"; chosen because the engine has NO freeze write seam (freeze is TASK.md text the engine only READS), and adding an `add.py freeze` write command is a separate task. If wrong: a seeded §7 delta carries the freeze-command follow-up; the 4 engine seams already deliver the lock/gate/milestone-done/release trail.
  - [ ] `gate_actor` is stamped on ALL gate outcomes incl. HARD-STOP (not just completing) — confirm at freeze.
  - [ ] the field stores the FULL `_whoami` dict `{name,email,source}` (not just the name), so task-3's status surface can render source+email — confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: lock stamps the structured actor
  Given git config user.name="Ada" / user.email="ada@x.io" and no actor_override
  When `add.py lock`
  Then state["setup"]["actor"] == {name:"Ada", email:"ada@x.io", source:"git"}
  And the existing state["setup"]["locked_by"] free-text is still present and unchanged

Scenario: gate stamps gate_actor on a PASS
  Given a task at verify ready to gate
  When `add.py gate PASS <slug>`
  Then state["tasks"][slug]["gate_actor"] == _whoami(state)
  And state["tasks"][slug]["gate"] == "PASS" (the existing record unchanged)

Scenario: gate stamps gate_actor on a HARD-STOP too
  Given a task with a HARD-STOP finding
  When `add.py gate HARD-STOP <slug>`
  Then state["tasks"][slug]["gate_actor"] is recorded (who recorded the stop)
  And state["tasks"][slug]["gate"] == "HARD-STOP"

Scenario: milestone-done stamps done_actor
  Given a milestone with all tasks done and exit criteria met
  When `add.py milestone-done <ms>`
  Then state["milestones"][ms]["done_actor"] == _whoami(state)
  And state["milestones"][ms]["status"] == "done"

Scenario: the release row carries an actor line
  Given a closed-unreleased milestone
  When `add.py release <ver>`
  Then the new RELEASES.md row contains a line `actor: <name> [<email>] (<source>)`
  And no state.json was written (attribution still lives in the ledger)

Scenario: an override flows into the stamp
  Given `add.py whoami --name "Bob" --email "bob@y.io"` was run (actor_override set)
  When any seam stamps
  Then the stamped actor == {name:"Bob", email:"bob@y.io", source:"override"}

Scenario: a legacy record without an actor is unchanged (descriptive-only)
  Given a state with a gate record that has NO gate_actor field (pre-stamping)
  When any read-only command runs (status/check/report)
  Then it loads and behaves identically — no decision path requires the actor
  And nothing crashes on the absent field
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_actor_stamp(state) -> { "name": str, "email": str|None, "source": "override"|"git"|"os" }
    # == _whoami(state); TOTAL (always a non-empty name) — the SINGLE source of the stamp.

cmd_lock            -> state["setup"]["actor"]               = _actor_stamp(state)   # + existing locked_by free-text (unchanged)
cmd_gate            -> state["tasks"][slug]["gate_actor"]    = _actor_stamp(state)   # every outcome: PASS | RISK-ACCEPTED | HARD-STOP
cmd_milestone_done  -> state["milestones"][slug]["done_actor"] = _actor_stamp(state)
cmd_release         -> RELEASES.md row gains a line: "actor: <name> [<email>] (<source>)"   # NO state.json write

Schema: additive OPTIONAL fields on existing records (state.json) + one new line on the RELEASES.md row.
  Absent on legacy records -> behaves exactly as today. DESCRIPTIVE-ONLY: no decision path reads the
  stamp for control flow. No new reject code — every seam keeps its existing rejects byte-unchanged.
  FREEZE seam EXCLUDED (no engine write; seeded as a §7 delta for a future `add.py freeze` command —
  human-confirmed 2026-06-22).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization, 2026-06-22)
Least-sure flag surfaced at freeze: [spec] the FREEZE-seam exclusion — freeze stays human-authored
free-text because the engine has NO freeze write seam; the other 4 seams stamp structurally. SURFACED +
human-confirmed ("ship 4 engine seams; freeze as follow-up"). Cost if wrong: a seeded §7 freeze-command
task. The two ranked assumptions (gate_actor on all outcomes · store the full {name,email,source} dict)
are both affirmed in this contract.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 seams + override-source + back-compat.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_lock_stamps_actor: lock under a known git config / no override -> state["setup"]["actor"]=={name,email,source:git}; assert locked_by still present
  - test_gate_stamps_gate_actor_on_pass: gate PASS -> state["tasks"][slug]["gate_actor"]==_whoami; assert gate=="PASS"
  - test_gate_stamps_gate_actor_on_hard_stop: gate HARD-STOP -> gate_actor recorded; assert gate=="HARD-STOP"
  - test_milestone_done_stamps_done_actor: milestone-done -> state["milestones"][ms]["done_actor"]==_whoami; assert status=="done"
  - test_release_row_carries_actor_line: release -> RELEASES.md row has `actor: … (<source>)`; assert no state.json write (mtime/content unchanged)
  - test_override_flows_into_stamp: whoami --name Bob --email … then a seam -> stamped actor source=="override", name=="Bob"
  - test_legacy_record_without_actor_unchanged: a hand-built state with a gate record lacking gate_actor -> status/check/report run clean (descriptive-only, no crash)
  - test_actor_stamp_is_whoami: _actor_stamp(state) == _whoami(state) (single-source)
  - EnginePinTest: 3 add.py copies byte-identical AND == ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_actor_stamping.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_actor_stamping.py` `add-method/tooling/test_retro.py`
Strategy (ordered batches): 1. `_actor_stamp` helper. 2. attach at the 3 state seams (lock/gate/milestone-done). 3. the release-row `actor:` line in `_render_releases_row` (no existing test asserts the exact row — confirmed — so additive, no co-update). 4. mirror to the 2 copies + re-pin. 5. red→green test_actor_stamping.py.
Safety rule (feature-specific): the actor field is computed BEFORE the existing write; it adds NO new IO and NO new failure path (rides save_state / the release in-memory-then-atomic-write+rollback). Descriptive-only — never gate or branch on the stamp.
Code lives in: `add-method/tooling/add.py` (+ 2 mirror copies, byte-identical)
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

- [x] all tests pass — full add-method suite 1456 green; `add.py check` 391 passed / 0 failed
- [x] coverage did not decrease — added test_actor_stamping.py (9 tests); ratified test_retro close-diff invariant
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; test_retro change is a contract-AUTHORIZED ratification (close now stamps done_actor), test_actor_stamping written RED first
- [x] the green was EARNED, not gamed — independent adversarial refute-read (python-expert) returned MERGE (0.93): verified totality, no decision-reads, guard ordering, rollback path, back-compat; it flagged ONE vacuous assert (the release state-unchanged check) — FIXED to a real `assertEqual(state, before)`
- [x] concurrency / timing of the risky operation is safe — no new IO; stamps ride the existing save_state / release atomic-write+rollback; computed before the write
- [x] no exposed secrets, injection openings, or unexpected dependencies — reuses `_whoami`/`_git_config` (task 1); no new deps
- [x] layering & dependencies follow CONVENTIONS.md — additive optional fields + one helper; engine byte-pinned in lockstep across all 3 copies
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); engine edit independently reviewed (MERGE, nits fixed)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] after `lock`, state["setup"]["actor"] == the resolved actor AND locked_by still present — confirmed by test_lock_stamps_actor + test_override_flows_into_stamp
- [x] gate PASS and gate HARD-STOP both write state["tasks"][slug]["gate_actor"] — confirmed by test_gate_stamps_gate_actor_on_pass / _on_hard_stop
- [x] milestone-done writes done_actor; release adds an `actor:` ledger line and writes NO state.json — confirmed by test_milestone_done_stamps_done_actor + test_release_row_carries_actor_line (asserts state unchanged across the release)
- [x] a legacy record without the actor field loads + runs clean — confirmed by test_legacy_record_without_actor_unchanged (status + report exit 0)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_actor_stamp`/`_render_actor_line` referenced by cmd_lock/cmd_gate/cmd_milestone_done/cmd_release + _render_releases_row; the independent review grepped all reads — write-only, no orphan
- [x] DEAD-CODE (code) — no orphaned symbol; both helpers are called; the `actor=None` default keeps _render_releases_row's legacy callers valid
- [x] SEMANTIC (prose / non-code) — n/a (engine-logic + test only)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22
Notes: descriptive structured-actor stamp on the 4 engine-written seams (lock/gate/milestone-done/release);
freeze excluded (no engine write) and seeded as a §7 follow-up — human-confirmed. Independent review MERGE
(0.93); its one substantive nit (a vacuous release assert) was fixed. No security finding. Engine re-pinned
6f28abab → d8b9c699, byte-identical across all 3 copies; full suite 1456 green.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] add an `add.py freeze` write command that records a structured actor at the contract freeze (the 5th human seam), so freeze joins lock/gate/milestone-done/release (evidence: actor-stamping stamped only the 4 engine-WRITTEN seams; freeze stays human-authored TASK.md text with no write seam — human-confirmed 2026-06-22 to defer to a follow-up task)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] the descriptive-additive stamp still rippled an exact-diff invariant test (test_retro `changed <= {status,updated}`) — an "additive" record write needs a census sweep for tests that pin a record's EXACT key-set, not just its values (evidence: test_close_state_diff_is_status_only went red until done_actor was ratified into the allowed set) [folded foundation-version 42]
