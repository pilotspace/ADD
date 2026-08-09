# TASK: add.py status --json --task <slug> filter

slug: status-task-filter · created: 2026-07-02 · stage: mvp
milestone: seams
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/add.py:1793-1819` (`cmd_status`, the `--json` branch — currently builds the full `tasks` list unconditionally) · `add-method/tooling/add.py` `build_parser()`'s `status` subparser (`~line 6980`, currently only accepts `--json`) · its 2 tracked mirrors (`.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`) · `add-method/tooling/engine_pin.py` (+ 2 mirrors, re-pin required) · `add-method/tooling/test_machine_state.py` (the `machine-state-json` task's frozen-@v1 test home for `status --json`'s schema — `test_status_json_describes_project` is the existing sibling scenario to extend, additively).
Context (working folder): user-observed friction this session — repeatedly hand-rolling `python3 -c "import json; state = json.load(open('.add/state.json')); ..."` and fragile `add.py status | grep -A2 <name>` text scraping to read one task's phase/gate, instead of using the engine's own interface.
Honors (patterns / conventions): `status --json`'s existing per-task object shape (`{slug, phase, gate, milestone, owner, assignee}` — already emitted inside the `tasks` array) — this task reuses that EXACT shape for the filtered single-object response, no new fields invented · `_die("unknown_task")` — the existing error code already used elsewhere in add.py for an unresolvable task slug (`add-method/tooling/add.py:3983`, `:4054`) · `_load_state_for_json`'s fail-closed contract (missing project -> stderr + exit 1 + EMPTY stdout, never partial JSON).
Anchors the contract cites: `cmd_status` · `_load_state_for_json` · `_die`.

---

## 1 · SPECIFY — the rules

Feature: Add an optional `--task <slug>` filter to `add.py status --json`, returning just that one task's `{slug, phase, gate, milestone, owner, assignee}` object instead of the full `tasks[]` array — so an AI/CLI caller never needs to open `.add/state.json` directly or grep text output to read one task's phase/gate.
Must:
  - `add.py status --json --task <slug>` prints exactly one JSON object (not a list) with the same 5 keys already emitted per-item in the unfiltered `tasks[]` array — no new/renamed fields.
  - an unknown slug dies with the existing `unknown_task` error code (stderr + exit 1 + EMPTY stdout), matching the convention already used elsewhere in add.py for an unresolvable task.
  - `--task` is a no-op without `--json` (text-mode `status` output is byte-unchanged) — this is a JSON-only affordance, not a new text-mode flag.
  - `add.py status --json` with NO `--task` is byte-for-byte unchanged from today (the full tasks[] array, milestones, etc.) — purely additive.
Reject:
  - a `--task` value that resolves to no task in state.json silently returning `{}` or exit 0 -> "unknown_task_silent"
  - filtering breaking the existing unfiltered `status --json` shape/fields -> "unfiltered_shape_regressed"
Accept: Given a project with task `phase-search-wiring` at `phase=done, gate=PASS`, When `add.py status --json --task phase-search-wiring` runs, Then stdout is exactly `{"slug": "phase-search-wiring", "phase": "done", "gate": "PASS", "milestone": "context-search", "owner": null, "assignee": null}` (order-insensitive) and exit code is 0.
Assumptions: none material — biggest risk: a caller expecting the filtered object nested under a `"task"` key (matching `guide --json`'s `"task"` field name) instead of a bare top-level object; mitigated by matching the already-established unfiltered array's flat per-item shape exactly, so behavior is predictable from the existing `status --json` docs alone.

---

## 3 · CONTRACT — freeze the shape

```
add.py status --json --task <SLUG>

  200 (found)   -> one JSON object, stdout only:
    {"slug": <SLUG>, "phase": <str|null>, "gate": <str|null>,
     "milestone": <str|null>, "owner": <str|null>, "assignee": <str|null>}
  error (unknown slug) -> stderr: "add: error: unknown_task", exit 1, EMPTY stdout

add.py status --json                 (no --task, unchanged)
  -> identical to today's full {project, stage, actor, active_task, active_milestones,
     active_tasks, milestones, tasks[...], graduation_ready, stage_criteria} object.

add.py status                        (no --json, unchanged)
  -> identical text-mode output; --task is silently ignored without --json (not an error —
     mirrors how other flag combinations that don't apply are simply no-ops in this CLI).

Code change: in cmd_status's `if getattr(args, "json", False):` branch, read
`getattr(args, "task", None)` before building `ms_list`; if set, look up
`tasks.get(task_slug)`, `_die("unknown_task")` if missing, else `print(json.dumps({...}))`
and `return` early — the rest of the function (milestones list, full tasks array,
graduation fields) is untouched, only reached when `--task` is absent.
Parser change: `pst.add_argument("--task", metavar="SLUG", help="...")` on the existing
`status` subparser (`build_parser()`), no new subcommand.

New tests: add-method/tooling/test_machine_state.py (the frozen-@v1 machine-state-json
task's existing home for status --json schema) — 2 new methods:
  test_status_json_task_filter_returns_one_object
  test_status_json_task_filter_unknown_slug_dies_unknown_task
```

`Least-sure flag surfaced at freeze:` [contract] the filtered object's field set is intentionally IDENTICAL to the unfiltered array's per-item shape (no extra fields like a full §3 CONTRACT dump or declared Scope) — lowest confidence because a caller might want richer per-task detail than phase/gate/milestone/owner/assignee; if wrong: a follow-up task can add a `--verbose`/richer dedicated command without breaking this one, since this stays additive and minimal by design.
Status: FROZEN @ v1 — approved by Tin Dang (via the "Add --task <slug> filter to status --json" decision)

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `.add/tooling/engine_pin.py` · `add-method/src/add_method/_bundled/tooling/engine_pin.py` · `add-method/tooling/test_machine_state.py`
Strategy & known-problem fixes: 1. write the 2 new test methods in `test_machine_state.py` red-first (using the file's existing `_run`/`_json_only` helpers, no new helper needed); 2. apply the `cmd_status` early-return branch + the `--task` argparse argument to canonical `add.py`; 3. propagate byte-identically to the 2 mirror trees; 4. run the new tests + the full `test_machine_state.py` file green; 5. compute the new whole-file md5, re-pin `ENGINE_MD5` (3 trees, narrated-history comment citing this task); `ENGINE_PKG_MD5` stays UNCHANGED (no `add_engine/` touch); 6. run `test_shared_engine_pin` + `test_engine_repin_parity` for pin currency; 7. run the full `add-method/tooling` suite to confirm zero regressions beyond the already-known, disclosed pre-existing failures. Known-problem: the unfiltered `status --json` path must stay byte-identical — dodged by placing the new branch as an early-return BEFORE any of the existing milestone/task-list-building code runs, so that code path is untouched when `--task` is absent.
Strategy actually used: as planned — no deviation.
Code lives in: `add-method/tooling/add.py` (`cmd_status`, 3-tree mirrored)   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `status --json --task <slug>` prints exactly one `{slug, phase, gate, milestone, owner, assignee}` object for a known task, and dies with `unknown_task` (stderr, exit 1, empty stdout) for an unknown slug — confirmed green by `test_status_json_task_filter_returns_one_object` + `test_status_json_task_filter_unknown_slug_dies_unknown_task` in `test_machine_state.py` (13/13 in-file, `python3 -m unittest test_machine_state`). Unfiltered `status --json`/text mode confirmed byte-unchanged (pre-existing `test_status_json_describes_project` + `test_text_mode_is_unchanged` still green, untouched by this build). All 3 engine trees (`add-method/tooling/`, `.add/tooling/`, `add-method/src/add_method/_bundled/tooling/`) confirmed byte-identical via `test_engine_repin_parity.test_three_engines_byte_identical_and_current`; `ENGINE_MD5` re-pinned to `ff7d9971c869cfacd552f03c23612990` with a changelog comment naming this task and the prior digest; `ENGINE_PKG_MD5` confirmed unchanged (no `add_engine/` touch).

Refute-read (self-adversarial): probed whether the new `--task` branch could leak into the unfiltered path or silently swallow a real state-read failure — confirmed it is an early-return branch taken only when `--task` is passed, sharing the same `load_state`/`_die` fail-closed convention as the rest of `cmd_status` (no new except-and-continue). Probed the `gate: "none"` vs `null` question directly against the unfiltered array's existing pass-through behavior (`t.get("gate")`) — confirmed consistent, not a new inconsistency (this was a test-expectation fix, not a code change). Ran the full `add-method/tooling` suite (2712 tests, one undisturbed run after all edits settled — a prior concurrent run mid-edit had shown a misleading 104-failure race, discarded): 10 pre-existing failures, all independently confirmed unrelated to this change.
Verdict: EARNED. By: self. Adversarially checked: fail-closed consistency with the unfiltered path, whole-suite regression sweep.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-02
