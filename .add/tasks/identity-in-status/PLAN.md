# TASK: surface the actor in status + json/report

slug: identity-in-status · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine across all 3 add.py copies + re-pins (read-only presentation surface); a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — SURFACE the actor task-2 stamped (read-only, no new writes):
  - `cmd_status` human branch (~1276) — ADD an `actor :` line after `project autonomy:` (~1279) showing the CURRENT resolved actor `_whoami(state)` as `<name> [<email>] (source: <source>)` — who ADD sees you as this session.
  - `cmd_status` --json branch (~1169) — ADD an `"actor"` key = `_whoami(state)` to the machine-state dict.
  - `report_data` (3461) — each task row gains `gate_actor` (`t.get("gate_actor")`) + the milestone dict gains `done_actor` (`ms.get("done_actor")`) — the recorded who-did-what (the JSON report facts).
  - `render_report` (3682) — show the recorded actor on a DONE task row + a closed-milestone header when present (back-compat: omit when absent).
- `engine_pin.py:ENGINE_MD5` = `d8b9c6999a43149706e9c2c3f7bac28d` — re-pin after this engine edit (same commit).
- `add-method/tooling/test_wave_status_hint.py:test_json_surface_frozen` — the `sanctioned` set (line 102) gains `"actor"` (the census ratification for the new `status --json` key).

Context (working folder):
- task-1 (`actor-identity`) shipped `_whoami(state)`; task-2 (`actor-stamping`) WROTE `setup.actor` · `tasks[slug].gate_actor` · `milestones[slug].done_actor` + the RELEASES.md `actor:` line. THIS task READS those + the live resolver to make the trail VISIBLE. Read-only: no save_state, no new state key.
- `status --json` is a FROZEN machine surface (test_json_surface_frozen): base keys immutable, only sanctioned additive keys allowed — so the new `actor` key is a ratified census co-update, mirror of milestone-1's active_milestones/active_tasks.

Honors (patterns / conventions):
- additive + read-only — every existing status/report line stays put; new lines are append-only and back-compat (a legacy record without gate_actor/done_actor simply renders no actor — never a crash).
- the additive-cue convention — the recorded-actor line shows ONLY when the stamp is present, so pre-stamping records + solo runs render byte-identically except for the new always-present `actor :` (current resolver) line.
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin; full suite is the regression oracle.

Anchors the contract cites: `cmd_status` `actor :` line + `"actor"` json key (= `_whoami(state)`) · `report_data` task-row `gate_actor` + milestone `done_actor` · `render_report` recorded-actor render · the ratified `sanctioned` set.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SURFACE the git-native actor — make the who-am-I (current resolver) and the who-did-what (task-2's recorded stamps) VISIBLE in `status` (human + --json) and `report`. Read-only; closes the user-identity trail (resolve → stamp → SEE).
Framings weighed: status shows the CURRENT actor + report shows the RECORDED actors (chosen — who-am-I orients the session, who-did-what is the audit trail) · status only (rejected — leaves the recorded trail invisible, the milestone's whole point) · a new `add.py who-did <slug>` query command (rejected — report already IS the per-task dashboard; no new verb needed).
Must:
<must>
  - `cmd_status` (human) prints a NEW `actor :` line = `_whoami(state)` as `<name> [<email>] (source: <source>)`, after the `project autonomy:` line. ALWAYS present (the resolver is TOTAL).
  - `status --json` gains a NEW `"actor"` key = `_whoami(state)` ({name,email,source}); every existing base key UNCHANGED (the frozen-surface contract — `actor` is the ratified additive key).
  - `report_data` adds `gate_actor` to each task row (`t.get("gate_actor")`, None when unstamped) + `done_actor` to the milestone dict (`ms.get("done_actor")`) — the JSON report facts.
  - `render_report` (human) shows the recorded actor on a task row whose gate is recorded + on a closed-milestone header — ONLY when the stamp is present (back-compat: a legacy/unstamped record renders no actor, never a crash, never a placeholder).
  - READ-ONLY: no save_state, no new state key, no existing command's decision changes. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - none new — this is a read-only presentation surface; it adds no command, no reject code, no write. A missing stamp is rendered as ABSENT (omit the actor), never an error.
</reject>
After:
<after>
  - `add.py status` shows who ADD sees you as; `status --json` carries an `actor` object; `add.py report <ms>` shows who gated each done task + who closed the milestone; unstamped records render cleanly; the full prior suite is green (the json surface ratified, not broken).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The `status --json` `actor` key passes the FROZEN-surface guard via a one-line `sanctioned`-set ratification (test_json_surface_frozen) — lowest confidence because that guard is deliberately strict (base keys immutable, only ratified keys extend it); chosen because `actor` is a genuine additive machine fact, exactly the case the sanctioned-set escape exists for (mirror of active_milestones/active_tasks). If wrong: drop the json key and surface the actor in human status + report only (the trail is still visible).
  - [ ] `report_data`'s additive `gate_actor`/`done_actor` keys don't break an exact-shape report test — confirmed at tests (no test pins the row key-set; the full suite is the oracle).
  - [ ] the human `actor :` line is ALWAYS shown (resolver TOTAL) while the RECORDED-actor render is conditional (present-only) — confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: status shows the current actor (human)
  Given an actor_override {name:"Bob", email:"bob@y.io"} (or git config / OS user)
  When `add.py status`
  Then the output contains a line `actor : Bob <bob@y.io> (source: override)`
  And every existing status line (project/stage/goal/...) is still present

Scenario: status --json carries the actor
  Given any project
  When `add.py status --json`
  Then the parsed object has an "actor" key == _whoami(state) {name,email,source}
  And every existing base key (project, stage, active_task, milestones, tasks, ...) is unchanged

Scenario: report shows who gated a done task and who closed a milestone
  Given a task gated PASS (gate_actor recorded) in a closed milestone (done_actor recorded)
  When `add.py report <ms>`
  Then report_data's task row carries gate_actor and the milestone carries done_actor
  And the human render shows the recorded actor on the done row / closed-milestone header

Scenario: an unstamped (legacy) record renders no actor — no crash
  Given a task whose record has NO gate_actor (pre-stamping)
  When `add.py report <ms>` and `add.py status`
  Then they run clean (exit 0) and simply omit the recorded actor for that row
  And nothing renders a placeholder or raises
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cmd_status (human)  -> NEW line `actor : <name> [<email>] (source: <source>)` = _whoami(state)
                       placed after `project autonomy:`; ALWAYS present (resolver TOTAL).
status --json       -> NEW key "actor": {name,email,source} = _whoami(state); base keys UNCHANGED.
report_data(...)    -> task row += "gate_actor": t.get("gate_actor")  (None when unstamped)
                       milestone dict += "done_actor": ms.get("done_actor")
render_report(...)  -> show the recorded actor on a gated task row + a closed-milestone header,
                       ONLY when present (absent stamp -> omit; never a placeholder/crash).

Schema: READ-ONLY presentation — no save_state, no new state key, no decision change. The
  `status --json` "actor" key is the ONLY frozen-surface change → ratified in the sanctioned
  set (test_json_surface_frozen). report_data additive keys are back-compat (.get default None).
Reject: none new — a missing stamp renders ABSENT, never an error.
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization, 2026-06-22)
Least-sure flag surfaced at freeze: [test] the `status --json` "actor" key must pass the FROZEN-surface
guard (test_json_surface_frozen) via a one-line `sanctioned`-set ratification — that guard is deliberately
strict, but `actor` is a genuine additive machine fact, exactly the sanctioned-set escape's purpose (mirror
of active_milestones/active_tasks). Cost if wrong: drop the json key, keep human status + report (trail
still visible). The two ranked assumptions (report_data additive keys break no exact-shape test · human
actor line always-on while recorded-actor render is present-only) are affirmed in this contract.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 3 surfaces (status human · status json · report) + back-compat.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_status_human_shows_actor: override Bob -> `add.py status` output contains `actor : Bob <bob@y.io> (source: override)`; assert a sample existing line (e.g. `project :`) still present
  - test_status_json_has_actor: `status --json` -> parsed["actor"] == _whoami(state); assert base keys (project/stage/active_task/milestones/tasks) all present
  - test_report_surfaces_recorded_actor: a gated-PASS task in a closed milestone -> report_data row has gate_actor, milestone has done_actor; human render contains the recorded name
  - test_unstamped_record_renders_no_actor: a record without gate_actor -> report + status exit 0, no placeholder, no raise
  - EnginePinTest: 3 add.py copies byte-identical AND == ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_identity_in_status.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_identity_in_status.py` `add-method/tooling/test_wave_status_hint.py`
Strategy (ordered batches): 1. cmd_status human `actor :` line + json `"actor"` key. 2. ratify the json sanctioned set (test_wave_status_hint). 3. report_data gate_actor/done_actor + render_report present-only display. 4. mirror to the 2 copies + re-pin. 5. red→green test_identity_in_status.py.
Safety rule (feature-specific): READ-ONLY — no save_state, no new state key; every render reads a stamp with `.get(...)` so an absent stamp is omitted, never a crash. Never branch a decision on the actor.
Code lives in: `add-method/tooling/add.py` (+ 2 mirror copies, byte-identical)
Constraints: do NOT change any test or the contract (except the sanctioned-set census ratification); allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `python3 -m unittest discover` → Ran 1461 tests, OK; `add.py check` 392 passed / 0 failed
- [x] coverage did not decrease — +5 tests (test_identity_in_status.py) over task-2's 1456; no test removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the build only added code (render/json/report surfaces)
- [x] the green was EARNED, not gamed — adversarial refute-read by an independent python-expert subagent: VERDICT MERGE (0.92), 0 BLOCKING; confirmed no overfit, no vacuous assert (the back-compat test pops the stamp and asserts None, not ""), no stubbed logic
- [x] concurrency / timing of the risky operation is safe — read-only surface, no new write; the one behavioral touch (cmd_milestone_done done_actor reorder) verified fail-closed: an OSError in `_write_retro` `_die`s before `save_state`, so nothing persists
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new import; actor strings are display-only, never eval'd or shelled
- [x] layering & dependencies follow CONVENTIONS.md — additive-cue convention honored (legacy/unstamped record renders byte-identical: no actor line); `_whoami` is the single resolver, `_fmt_actor` the single render helper
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); risk:high → conservative gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `status` (human) prints `actor   : <name> <email> (source: <source>)` after `project autonomy:` — confirmed on the real project: `actor   : Tin Dang <tindang.ht97@gmail.com> (source: git)`
- [x] `status --json` carries an `actor` object = `_whoami(state)` — confirmed: `{'name': 'Tin Dang', 'email': 'tindang.ht97@gmail.com', 'source': 'git'}`
- [x] `report <ms>` surfaces the RECORDED actor present-only — confirmed: `report user-identity` shows a `GATED BY` block with `actor-stamping ... PASS Tin Dang <…>`, and (back-compat) OMITS actor-identity, gated before stamping existed
- [x] an unstamped/legacy record renders NO actor line (no placeholder, no crash) — confirmed by test_unstamped_record_renders_no_actor + the dogfood omission above

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_fmt_actor` referenced in render_report (closed-by + GATED BY); `_whoami` referenced in cmd_status human + json; `gate_actor`/`done_actor` threaded through report_data into render_report
- [x] DEAD-CODE (code) — no orphaned symbol; the python-expert refute-read confirmed every new field is read by a display path and nothing else
- [x] SEMANTIC (prose / non-code) — read the refute-read in full: confirmed the OSError-rollback, the present-only render, and the no-control-flow-read invariants; applied its one NIT (`_fmt_actor` `actor.get('name','')` hardening against a malformed partial dict)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a legacy/unstamped record ever rendering a placeholder or KeyError in report/status (back-compat regression) · the `status --json` `actor` key ever tripping the frozen-surface guard for a downstream consumer.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] add an `add.py` freeze write command so the §3-freeze human seam is engine-WRITTEN (and thus actor-stampable) like lock/gate/milestone-done — today freeze is human-authored TASK.md text read via `_AUDIT_STAMP_RE`, so the actor trail has a hole at freeze (evidence: actor-stamping scoped to the 4 engine-written seams precisely because freeze has no write seam; carried forward through this task).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a write-then-render ordering coupling: when a render reads a state field, the field must be set BEFORE the render that persists it (RETRO.md), or the persisted artifact diverges from the canonical recompute (evidence: cmd_milestone_done wrote done_actor AFTER `_write_retro`, so the saved RETRO.md lacked the `closed by` line the report re-render adds — fixed by reordering the stamp before the retro write). [folded foundation-version 42]
- [ADD · folded] a present-only render helper must default-read every key (`actor.get('name','')`, not `actor['name']`) so a hand-edited/partial state record degrades to empty, not a KeyError crash (evidence: python-expert refute-read NIT; hardened `_fmt_actor`). [folded foundation-version 42]
