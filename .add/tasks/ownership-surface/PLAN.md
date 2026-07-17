# TASK: surface owner/assignee in status + report + json

slug: ownership-surface · created: 2026-06-22 · stage: mvp · risk: high
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — SURFACE the owner/assignee task-1 writes (READ-ONLY, no new write):
  - `report_data` (task row ~3560, milestone dict ~3582) — each task row gains `owner`/`assignee` (`t.get("owner")`/`t.get("assignee")`, None when unassigned); the milestone dict gains `owner`/`assignee` (`ms.get(...)`). The machine report facts (= report --json).
  - `render_report` (~3810 closed-by, ~3827 GATED BY) — ADD a present-only milestone `owned by` header line (when the milestone has owner/assignee) + an `OWNED BY` per-task block (mirror of `GATED BY`), listing each task with an owner or assignee. Back-compat: omit when absent.
  - `cmd_status` human (active-task block ~1443, beside `autonomy:`/`grounded:`) — ADD a present-only `owned   :` line for the ACTIVE task showing its owner/assignee (only when set).
  - `cmd_status` --json (per-task list ~1338) — each task entry gains `owner`/`assignee` (`.get`, None when unassigned). This is a PER-TASK dict key, NOT a top-level status key, so the frozen-surface guard (test_wave_status_hint, top-level only) is untouched.
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit).
- `_fmt_actor(actor)` (~3696) — REUSE as-is to render an owner/assignee `{name,email,source}` (it already returns "" for None and `name <email>` otherwise). No change.

Context (working folder):
- task-1 (`ownership-model`) WROTE `tasks[slug].owner`/`.assignee` + `milestones[slug].owner`/`.assignee` (each `{name,email,source}`, source ∈ git/os/override/assigned) via `assign`/`unassign`. THIS task READS them to make the trail VISIBLE. Read-only: no save_state, no new state key, no decision change.
- mirrors exactly how the sibling milestone's `identity-in-status` surfaced the ACTOR (gate_actor/done_actor) — same present-only render discipline, same `_fmt_actor` helper, same census posture.

Honors (patterns / conventions):
- additive + read-only — every existing status/report line stays put; new lines are append-only + back-compat (a record without owner/assignee renders no owner line — never a crash, never a placeholder).
- additive-cue convention — the `owned   :`/`OWNED BY`/`owned by` lines show ONLY when a stamp is present, so an unassigned project's output is byte-identical.
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin; full suite is the regression oracle.
- `_fmt_actor` reuse — the owner/assignee share the actor shape, so the existing present-only formatter renders them with zero new helper.

Anchors the contract cites: `report_data` task-row `owner`/`assignee` + milestone `owner`/`assignee` · `render_report` `OWNED BY` block + milestone `owned by` line · `cmd_status` human `owned   :` line + `--json` per-task `owner`/`assignee` · `_fmt_actor` (reused).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SURFACE the owner/assignee task-1 writes — make who-OWNS / who-WORKS visible in `report` (per-task + milestone), `status` (the active task), and the `--json`/report-data machine facts. Read-only; completes the ownership loop (assign → SEE), mirroring how identity-in-status surfaced the actor.
Framings weighed: report (audit) + status (active focus) + json facts (chosen — report is the who-owns-what dashboard, status orients the session, json is the machine surface) · report only (rejected — leaves the active-task owner invisible at the orientation point) · a new `add.py owners` query command (rejected — report already IS the per-task dashboard; no new verb, exactly the identity-in-status precedent).
Must:
<must>
  - `report_data` adds `owner`/`assignee` (`t.get(...)`, None when unassigned) to each task row, and `owner`/`assignee` (`ms.get(...)`) to the milestone dict.
  - `render_report` (human) shows the recorded owner/assignee PRESENT-ONLY: a milestone `owned by` header line when the milestone has owner/assignee, and an `OWNED BY` per-task block (mirror of `GATED BY`) listing each task that has an owner or assignee. A record with neither renders nothing (no placeholder, no crash).
  - `cmd_status` (human) prints a present-only `owned   :` line for the ACTIVE task when it has an owner or assignee (rendered via `_fmt_actor`).
  - `status --json` adds `owner`/`assignee` (`.get`, None when unassigned) to each per-task entry; every existing TOP-LEVEL status key is unchanged (the frozen-surface guard is top-level only — a per-task key is safe).
  - READ-ONLY: no save_state, no new state key, no existing command's decision changes. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - none new — this is a read-only presentation surface; it adds no command, no reject code, no write. An absent owner/assignee renders as ABSENT (omit), never an error.
</reject>
After:
<after>
  - `add.py report <ms>` shows who owns/works each task + the milestone; `add.py status` shows the active task's owner/assignee when set; `status --json` carries per-task owner/assignee; an unassigned record renders cleanly; the full prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Adding `owner`/`assignee` to each `status --json` per-task entry does not break a consumer that pins the per-task dict shape — lowest confidence because the frozen-surface test guards only TOP-LEVEL keys, leaving per-task entry shape un-pinned (so a hidden consumer could exist). Chosen because it is genuinely additive (new keys, existing ones untouched) and mirrors report_data's gate_actor precedent; if wrong: drop the json per-task keys and surface owner/assignee in report + human status only (the trail stays visible) — the full suite is the oracle that catches it.
  - [ ] `_fmt_actor` correctly renders an owner/assignee (same `{name,email,source}` shape) — confirmed: it is shape-agnostic (`name <email>`, "" for None), proven on the actor in identity-in-status.
  - [ ] an `OWNED BY` block listing a task with EITHER owner OR assignee (not requiring both) is the right inclusion rule — confirmed: partial ownership (only an assignee) is a real state task-1 allows, so the surface must show it.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: report shows the owner/assignee of an assigned task
  Given a milestone "m" with a task "t" assigned owner Bob + assignee Cy
  When `add.py report m`
  Then report_data's "t" row carries owner==Bob and assignee==Cy
  And the human render contains an "OWNED BY" block naming Bob and Cy

Scenario: report shows the milestone owner present-only
  Given a milestone "m" assigned owner Bob (the milestone record itself)
  When `add.py report m`
  Then report_data["milestone"] carries owner==Bob
  And the human render contains an "owned by" header line naming Bob

Scenario: report omits ownership for an unassigned project
  Given a milestone "m" whose tasks have no owner/assignee
  When `add.py report m`
  Then the render contains no "OWNED BY" block and no "owned by" line
  And every existing report line (VERDICT/TASKS/GATES/...) is unchanged

Scenario: status shows the active task's owner/assignee
  Given the active task "t" assigned owner Bob + assignee Cy
  When `add.py status`
  Then the output contains an "owned   :" line naming Bob and Cy

Scenario: status omits the owned line when the active task is unassigned
  Given the active task "t" with no owner/assignee
  When `add.py status`
  Then the output contains no "owned   :" line
  And every existing status line is unchanged

Scenario: status --json carries per-task owner/assignee
  Given a task "t" assigned owner Bob
  When `add.py status --json`
  Then the parsed task entry for "t" has owner==Bob and assignee==None
  And every existing TOP-LEVEL key (project, stage, actor, milestones, tasks, ...) is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
report_data(root, state, mslug) -> { ..., tasks: [ {..., owner, assignee} ], milestone: {..., owner, assignee} }
  owner/assignee = t.get("owner")/t.get("assignee")  (None when unassigned)   # task rows
  owner/assignee = ms.get("owner")/ms.get("assignee") (None when unassigned)  # milestone dict

render_report(...) human DASHBOARD (present-only, never a placeholder):
  milestone owner/assignee -> ` owned by owner: <name> · assignee: <name>`   (only present roles)
  per-task                 -> ` OWNED BY` block, one row per task with owner OR assignee:
                                `   <slug>  owner: <name> · assignee: <name>`   (present roles only)
  rendered via _fmt_actor (reused — "" for None, `name <email>` otherwise)

cmd_status human  -> ` owned   : owner: <name> · assignee: <name>`  for the ACTIVE task, present-only
cmd_status --json -> each tasks[] entry gains owner, assignee (.get -> None when unassigned)

Schema: READ-ONLY — no state.json write, no new state key, no migration. Reads the
  owner/assignee keys ownership-model writes. No existing key/line/decision touched.
  source ∈ {git, os, override, assigned} rendered verbatim by _fmt_actor (email only).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [contract] adding `owner`/`assignee` to each `status --json` PER-TASK entry — the frozen-surface guard (test_wave_status_hint) checks only TOP-LEVEL keys, so the per-task entry shape is un-pinned and a hidden consumer could in principle break. Chosen because it is purely additive (mirrors report_data's gate_actor) and the full suite is the oracle. Cost if wrong: drop the json per-task keys, keep owner/assignee in report + human status (trail still visible); the freeze holds (report_data + render are the primary surface).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 6 scenarios + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_report_surfaces_task_owner_assignee: assign t owner Bob + assignee Cy; report_data row has owner==Bob, assignee==Cy; human render has "OWNED BY" + Bob + Cy
  - test_report_surfaces_milestone_owner: assign m --owner Bob; report_data milestone owner==Bob; render has "owned by" line + Bob
  - test_report_omits_unassigned: no assignment; render has no "OWNED BY"/"owned by"; a known existing line ("VERDICT") still present
  - test_status_shows_active_owned_line: active t assigned owner Bob + assignee Cy; status human has "owned   :" + Bob + Cy
  - test_status_omits_owned_when_unassigned: active t unassigned; status human has no "owned   :" line
  - test_status_json_per_task_ownership: assign t --owner Bob; status --json task entry owner==Bob, assignee None; top-level keys intact
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_ownership_surface.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. report_data — add owner/assignee to the task row + milestone dict. 2. render_report — add the milestone `owned by` line + the `OWNED BY` per-task block (reuse `_fmt_actor`). 3. cmd_status human `owned   :` line + --json per-task keys. 4. mirror to the other 2 copies (`cp`) + re-pin ENGINE_MD5. 5. run the red suite green.
Safety rule (feature-specific): READ-ONLY — no save_state, no new state key; every new render is present-only (guarded by `if rec.get("owner") or rec.get("assignee")`) so an unassigned record's output is byte-identical.
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only, nothing new); ask if unclear. NO census co-update needed (no new subcommand; status --json gains only a PER-TASK key, not a top-level one).

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite Ran 1480, OK; `add.py check` 387 passed / 0 failed
- [x] coverage did not decrease — +7 tests (test_ownership_surface.py); no test removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; build only added read-only render code
- [x] the green was EARNED, not gamed — independent python-expert refute-read: VERDICT MERGE (0.93), 0 blocking; confirmed present-only suppression, no vacuous assert, partial-record (assignee-only) rendering correct. Applied its one NIT (`_fmt_ownership` blank-name guard).
- [x] concurrency / timing safe — read-only surface, no new write; single-process CLI
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new import; owner/assignee are stored display data, never eval'd/shelled
- [x] layering & dependencies follow CONVENTIONS.md — additive-cue convention honored (unassigned output byte-identical); reuses `_fmt_actor`; new `_fmt_ownership` is the single render helper, mirroring identity-in-status
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); risk:high → conservative gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `report <ms>` shows an `OWNED BY` block + a milestone `owned by` line — confirmed on the real project: `report ownership-assignment` rendered `owned by owner: Tin Dang` + `OWNED BY` with `ownership-surface  owner: Tin Dang <…> · assignee: Tin Dang`
- [x] `status` shows the active task's `owned   :` line present-only — confirmed: `owned   : owner: Tin Dang <tindang.ht97@gmail.com> · assignee: Tin Dang`
- [x] `status --json` carries per-task owner/assignee — confirmed by test_status_json_per_task_ownership (owner==Bob, assignee None, top-level keys intact)
- [x] an unassigned record renders no owner line/block — confirmed by test_report_omits_unassigned + test_status_omits_owned_when_unassigned + the post-cleanup demo (state clean, no lines)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_fmt_ownership` called in render_report (milestone + OWNED BY) and cmd_status (active task); owner/assignee threaded through report_data into render_report + the json task list (verified by the real-project demo)
- [x] DEAD-CODE (code) — no orphan; the review confirmed every new field is read by a display path only
- [x] SEMANTIC (prose / non-code) — read the refute-read in full: confirmed present-only/back-compat/read-only invariants hold; applied the blank-name NIT for fail-safe rendering

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): an unassigned project ever rendering a blank `owned by`/`OWNED BY`/`owned   :` line (back-compat regression) · a `status --json` per-task consumer breaking on the new owner/assignee keys.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] the multi-active `streams :` block (parallel-status-view) could show each active milestone's owner/assignee next to its task=…/phase=… so a team reads "who drives which stream" at a glance — the sibling `multi-active-UX` is the natural home (evidence: ownership-surface shows only the SINGLE active task's owner; a parallel-fronts team needs per-stream ownership). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a second record-typed field that shares the actor `{name,email,source}` shape (owner/assignee, after gate_actor/done_actor) confirmed a reusable surface pattern: one `_fmt_actor` + a thin per-feature `_fmt_*` wrapper + a present-only render guard — adding a surface is now a 3-edit recipe (report_data row + render block + status line) (evidence: ownership-surface reused identity-in-status's exact shape with zero new primitives). [folded foundation-version 43]
