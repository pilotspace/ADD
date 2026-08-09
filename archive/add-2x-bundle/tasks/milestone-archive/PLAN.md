# TASK: collapse done milestones

slug: milestone-archive · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

`add.py archive-milestone <slug>` collapses a FINISHED milestone so state.json and
`status` stay small as the project grows. Decision (user-picked): LIGHT archive —
shrink the active state only; files on disk are untouched (history preserved).

Must:
  - Require the milestone be done (`status == "done"`, set by `milestone-done`).
  - **(v2)** Re-check that EVERY member task is `_task_done` at archive time — the
    `status` flag can go stale when a task is attached AFTER `milestone-done` ran.
  - Remove the milestone from `state["milestones"]` AND remove its member tasks from
    `state["tasks"]` (this is the actual state shrink).
  - Append ONE compact record to `state["archived"]` (a list): `{slug, title, tasks:
    <count>, task_slugs: [...], archived: <date>}` — a summary + the member slugs (so
    cross-milestone deps still resolve), never the task bodies.
  - **(v2)** A dependency on an archived task still resolves: `check` must not flag it
    "unknown task" and `ready` must treat it as satisfied (archived ⇒ was PASS-done).
  - If `active_milestone` was this slug -> set it None; if `active_task` was one of the
    archived tasks -> set it None (only for member tasks — a non-member active task survives).
  - Files on disk (MILESTONE.md, each TASK.md) are NOT moved or deleted.
  - `status` prints a one-line "archived: N milestone(s) (M tasks)" rollup when any exist.
  - Backward-compatible: read archived via `.get("archived", [])` and slugs via
    `.get("task_slugs", [])`; an old state.json with no `archived`/`task_slugs` keeps working.
Reject:
  - Unknown milestone slug -> `_die("unknown_milestone")`.
  - Milestone not done -> `_die("milestone_not_done")` (run `milestone-done` first).
  - **(v2)** Milestone whose `status == "done"` is stale (a live incomplete member exists)
    -> `_die("milestone_has_incomplete_tasks")`; NEVER silently delete live work.
After:
  - `state["milestones"]`/`state["tasks"]` no longer contain the milestone or its tasks;
    `state["archived"]` has the summary; `status` stays small; the files still exist.
Assumptions (confirm before building):
  - [x] LIGHT archive — shrink state, keep files (user-picked)
  - [x] **(v2 CORRECTION)** gate on `status == "done"` AND re-verify members — review proved
    `status` can go stale, so a status-only gate could silently destroy a live task
  - [x] compact record carries a COUNT + member slugs (not bodies) — count keeps state small,
    slugs keep cross-milestone deps resolvable

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: archive a done milestone collapses it out of active state
  Given a done milestone "m1" with 2 PASS tasks
  When I run `add.py archive-milestone m1`
  Then state.milestones has no "m1" and state.tasks has neither member task
  And state.archived has one record {slug: m1, tasks: 2}

Scenario: the milestone + task files stay on disk
  Given the same archived milestone
  When I inspect the filesystem
  Then .add/milestones/m1/MILESTONE.md and each task's TASK.md still exist

Scenario: status shows the archived rollup
  Given one archived milestone with 2 tasks
  When I run `add.py status`
  Then output contains "archived: 1 milestone (2 tasks)"

Scenario: archiving clears active pointers that referenced it
  Given m1 is the active milestone and a member task is the active task
  When I archive m1
  Then active_milestone is null and active_task is null

Scenario: an unknown milestone is rejected
  Given any project
  When I run `add.py archive-milestone nope`
  Then it exits non-zero with "unknown_milestone"
  And state.json is unchanged

Scenario: a not-done milestone is refused (no data loss)
  Given an active milestone "m2" with an unfinished task
  When I run `add.py archive-milestone m2`
  Then it exits non-zero with "milestone_not_done"
  And m2 and its task are still in active state

Scenario (v2): a stale-done milestone with a live task is refused
  Given a done milestone "m1" that gained a new incomplete task "late" after milestone-done
  When I run `add.py archive-milestone m1`
  Then it exits non-zero with "milestone_has_incomplete_tasks"
  And m1 and "late" are still in active state (the live task is NOT destroyed)

Scenario (v2): a non-member active task survives the archive
  Given m1 is done and a task from another milestone m2 is the active task
  When I archive m1
  Then active_task is still that m2 task (clearing is conditional, not blanket)

Scenario (v2): a cross-milestone dep on an archived task still resolves
  Given m2's task "transfer" depends on m1's done task "auth", then m1 is archived
  When I run `add.py check` and `add.py ready`
  Then check passes (the archived dep resolves) and "transfer" is listed ready
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cli:  add.py archive-milestone <slug>      (new subcommand; requires a .add/ root)

cmd_archive_milestone(args):
  - slug not in state["milestones"]            -> _die("unknown_milestone")
  - state["milestones"][slug]["status"] != done -> _die("milestone_not_done")
  - members = [s for s,t in tasks if t.milestone == slug]
  - incomplete = [s for s in members if not _task_done(tasks[s])]   # (v2)
  - incomplete                                  -> _die("milestone_has_incomplete_tasks")
  - state.setdefault("archived", []).append(
        { "slug": slug, "title": <title>, "tasks": len(members),
          "task_slugs": members, "archived": date.today().isoformat() })   # (v2: +task_slugs)
  - del state["milestones"][slug]; for s in members: del state["tasks"][s]
  - active_milestone == slug   -> None
  - active_task in members      -> None       # conditional: a non-member active task survives
  - save_state

_archived_task_slugs(state) -> set:   # (v2) union of rec.get("task_slugs", []) over archived
cmd_check / cmd_ready: a dep resolves / is satisfied if `dep in tasks OR dep in
  _archived_task_slugs(state)` (archived ⇒ was PASS-done).

cmd_status: after the milestone rollup, if state.get("archived"):
  print "archived: <N> milestone(s) (<M> tasks)"   where M = sum(rec["tasks"])

Schema delta (backward-compatible): state["archived"]: list[{slug,title,tasks,task_slugs,archived}]
  read via state.get("archived", []) and rec.get("task_slugs", []) (pre-v2 records lack slugs).
```

Status: FROZEN @ v2 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)
  <!-- v1 -> v2 change request (2026-05-29, from v1-1 adversarial review): a status-only
       gate could silently delete a live task attached after milestone-done, and archiving
       broke cross-milestone deps. Re-specified above; v1 shipped @ f5dadca, v2 fixes follow. -->
  <!-- PROCEDURE NOTE (dogfood): a frozen-contract change is a change request back to SPECIFY.
       Here the task was already `phase: done`, so this is an in-place v2 re-spec (SPECIFY/
       SCENARIOS/CONTRACT/TESTS updated together, re-gated PASS) — NOT a phase reset to specify.
       Reopen to `specify` only when the change is large enough to re-run the loop end-to-end. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 6 scenarios (new file add-method/tooling/test_milestone_archive.py).
Plan (one test per scenario; assert state shape + filesystem + output + immutability-on-reject):
  - test_archive_collapses_state:      done m1(2 tasks) / archive / milestones&tasks gone, record present
  - test_archive_keeps_files_on_disk:  archive / MILESTONE.md + TASK.md still exist
  - test_status_shows_archived_rollup: archive / status / "archived: 1 milestone (2 tasks)"
  - test_archive_clears_active_pointers: archive active m1 / active_milestone & active_task -> null
  - test_archive_rejects_unknown:      archive nope / SystemExit + "unknown_milestone" + state unchanged
  - test_archive_rejects_not_done:     active m2 w/ unfinished task / archive / "milestone_not_done" + m2 intact
v2 regression guards (from the v1-1 adversarial review):
  - test_archive_rejects_incomplete_member:       stale-done m1 + live "late" / "milestone_has_incomplete_tasks" + both intact
  - test_archive_preserves_non_member_active_task: archive m1 / a non-member active task & milestone survive
  - test_archive_keeps_cross_milestone_dep_resolvable: archive m1 / check passes + "transfer" is ready

Tests live in: `add-method/tooling/test_milestone_archive.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): NEVER collapse a not-done milestone (reject first, before
any mutation); the archived record is a COUNT-only summary so state can't regrow; the
write is atomic via save_state; on any reject, state.json is left byte-for-byte unchanged
(validate-before-mutate). stdlib only.
Code lives in: `add-method/tooling/add.py` (cmd_archive_milestone + status rollup + subparser).
Keep `.add/tooling/add.py` byte-identical to source.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 63/63 green; 9 in test_milestone_archive.py (6 v1 + 3 v2 guards)
- [x] coverage did not decrease — tests only added; v2 red-first confirmed (2 FAIL + 1 guard-green
      for the right reason: "SystemExit not raised" + "check must pass after archive")
- [x] no test or contract was altered during build — contract re-specified v1->v2 FIRST (change
      request), then tests, then code; no test edited to fit the implementation
- [x] concurrency / timing safe — validate-before-mutate; single atomic save_state; no shared state
- [x] no exposed secrets / injection / unexpected deps — stdlib only; record is a slug+count summary
- [x] layering & deps follow CONVENTIONS.md — flat stdlib add.py; backward-compat via .get defaults
- [x] a person reviewed — v1-1 multi-lens adversarial-review workflow ran over the diff; it found
      the stale-done data-loss path (HIGH) + the cross-milestone dep break (MEDIUM), both fixed here.
      Human author sign-off: pending pre-push.

### GATE RECORD
Outcome: PASS
Reviewed by: v1-1 adversarial-review workflow + author (self) · date: 2026-05-29 · author sign-off pre-push
Evidence (v2): 63/63 green · the HIGH data-loss path is now refused (test_archive_rejects_incomplete_member,
RED→GREEN) · archived deps resolve in check & ready (test_archive_keeps_cross_milestone_dep_resolvable) ·
non-member active task survives (test_archive_preserves_non_member_active_task) · v1 evidence still holds.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does state.json actually stay small across many
milestones? do users want to LIST or RESTORE an archived milestone? Spec delta for the
next loop: `add.py archived` (list records), an `un-archive`/restore path, and optional
heavy archive (move files to `.add/milestones/_archive/<slug>/`) if the tree gets noisy.
