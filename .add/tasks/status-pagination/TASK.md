# TASK: status: sort milestones/tasks by updated desc, cap to top 10 with --all escape hatch

slug: status-pagination · created: 2026-07-02 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/add.py:1793-1827` (`cmd_status`'s `--json` branch — builds `ms_list`/`tasks[]` by iterating `state["milestones"]`/`state["tasks"]` dicts in insertion order, unbounded) · `add-method/tooling/add.py:1882-2008` (`cmd_status`'s text-mode `milestones:`/`tasks   :` loops — same insertion-order iteration, unbounded) · `add-method/tooling/add.py` `build_parser()`'s `status` subparser (currently `--json`, `--task` only) · its 2 tracked mirrors (`.add/tooling/add.py`, `add-method/src/add_method/_bundled/tooling/add.py`) · `add-method/tooling/engine_pin.py` (+ 2 mirrors, re-pin required) · `add-method/tooling/test_machine_state.py`.
Context (working folder): `state.json` already stores full ISO-8601 `created`/`updated` timestamps per milestone/task (confirmed live: `{"created": "2026-07-02T02:44:55+00:00", "updated": "2026-07-02T03:04:18+00:00", ...}`) — no new data field needed, this is a display/sort/cap change only. User-observed friction: `status`'s milestone/task lists grow unbounded (31 milestones / 143 tasks in this project today) with no recency ordering or paging.
Honors (patterns / conventions): the `status-task-filter` precedent — an additive JSON-schema amendment (new fields only, no field removed/renamed) on the SAME frozen `machine-state-json` v1 surface, following the file's own "amended @ v1.1" convention already used for `guide --json`'s null-phase case · existing `--all`-style escape-hatch flags elsewhere in this CLI (none named `--all` yet, but the "flag reverts to full/unfiltered" shape is the established idiom for opt-in filtering, e.g. `--task`'s own additive-only design).
Anchors the contract cites: `cmd_status` · `build_parser()`'s `status` subparser · `test_status_json_describes_project` (the existing sibling scenario this task extends, additively).

---

## 1 · SPECIFY — the rules

Feature: Sort `status`'s milestone and task lists newest-`updated`-first, and cap each to the top 10 by default (both text and JSON output), with an `--all` flag that reverts to the full, still-sorted list — so a growing corpus (31 milestones / 143 tasks today) stays scannable without losing anything.
Must:
  - both the text-mode `milestones:` list and the JSON `milestones[]` array are sorted by each milestone's `updated` timestamp, most-recent first.
  - both the text-mode `tasks   :` list and the JSON `tasks[]` array are sorted by each task's `updated` timestamp, most-recent first.
  - without `--all`, each of the 2 lists (milestones, tasks) is capped to its 10 most-recently-updated entries; `status --json` additionally gains `milestones_total`/`tasks_total` integer fields (the TRUE corpus size, independent of the cap) so a JSON consumer can detect truncation.
  - `status --all` (both text and JSON) reverts to the full, uncapped list — still sorted newest-first.
  - a capped text-mode list prints one trailing note per section (e.g. `  … 21 more (see status --all)`) — silent when not truncated.
  - `status --json --task <slug>` (the existing filter) is untouched — it already returns one object outside the list/array shape and never needed sorting or capping.
  - `add.py check` continues to pass; no engine/test outside this task's declared scope changes.
Reject:
  - a fix that reorders `state.json`'s own on-disk dict (mutating stored order) instead of sorting only at DISPLAY/serialization time -> "state_mutated"
  - a cap that silently drops entries from `status --json` with no `milestones_total`/`tasks_total` signal -> "silent_truncation"
  - a cap that makes the ACTIVE task or milestone (already surfaced via the separate `active`/`streams` lines) harder to find -> "active_item_hidden" (mitigated: those lines are untouched, independent of the capped lists)
Accept: Given a project with 12 milestones whose `updated` timestamps are all distinct, When `add.py status --json` runs (no `--all`), Then `milestones` contains exactly the 10 most-recently-updated milestones in descending `updated` order and `milestones_total` is 12; When `add.py status --json --all` runs, Then `milestones` contains all 12 in the same descending order.
Assumptions: ⚠ sorting by `updated` (not `created`) means a milestone opened long ago but touched today outranks a newer milestone with no recent activity — chosen per the "surfaces what's actively in motion" rationale confirmed by Tin Dang; if wrong: a follow-up task can add a `--sort created` flag without breaking this default, since nothing here hard-codes `updated` as the ONLY possible key.

---

## 3 · CONTRACT — freeze the shape

```
add.py status --json                 (no --task)
  milestones[]: sorted by each milestone's `updated` timestamp, descending; capped to 10
    unless --all. New field: "milestones_total": <int>  (true count, always present).
  tasks[]: sorted by each task's `updated` timestamp, descending; capped to 10 unless --all.
    New field: "tasks_total": <int>  (true count, always present).
  Every other top-level field (project, stage, actor, active_task, active_milestones,
  active_tasks, graduation_ready, stage_criteria) and every per-item field
  (slug/status/done/total/owner/assignee for milestones; slug/phase/gate/milestone/
  owner/assignee for tasks) is UNCHANGED — purely additive (2 new top-level int fields,
  reordered + possibly-shortened arrays).

add.py status --json --all
  identical shape, milestones[]/tasks[] uncapped (still sorted, same 2 new *_total fields
  now equal to len(milestones[])/len(tasks[])).

add.py status --json --task <SLUG>   (unchanged — no --all interaction, no sort/cap)

add.py status                        (text mode, no --all)
  the "milestones:" block lists the 10 most-recently-updated milestones (was: insertion
  order, unbounded); if more exist, one trailing line:
    "  … <N> more (see status --all)"
  the "tasks   :" block lists the 10 most-recently-updated tasks (was: insertion order,
  unbounded); same trailing-note convention when truncated.
  Every other text-mode line (project/stage/actor/goal/active/streams/archived/deltas/
  spec/resume/etc.) is UNCHANGED.

add.py status --all                  (text mode)
  both blocks list every milestone/task, sorted newest-first; no trailing note.

Code change: a new helper `_sorted_by_updated(items: dict) -> list[tuple[str, dict]]`
returning `sorted(items.items(), key=lambda kv: kv[1].get("updated") or "", reverse=True)`,
used by both the JSON branch (ms_list/tasks[] construction) and the two text-mode loops
(milestones:/tasks   :). Capping is `[:10]` applied to the sorted list unless
`getattr(args, "all", False)`. Sorting happens at read/serialization time only —
state.json's own on-disk dict order is never rewritten.
Parser change: `pst.add_argument("--all", action="store_true", help="...")` on the
existing `status` subparser (build_parser()), no new subcommand.

New tests: add-method/tooling/test_machine_state.py — new methods:
  test_status_json_milestones_sorted_by_updated_desc
  test_status_json_tasks_sorted_by_updated_desc
  test_status_json_caps_to_10_with_total_fields
  test_status_json_all_flag_returns_uncapped
  test_status_text_mode_shows_truncation_note
  test_status_text_mode_all_flag_shows_everything
```

`Least-sure flag surfaced at freeze:` [contract] sorting by `updated` rather than `created` (confirmed via AskUserQuestion — Tin Dang chose "updated" for "surfaces what's actively in motion") — lowest confidence because a caller expecting strict creation-order history browsing would need `--all` plus manual re-sort; if wrong: add a `--sort created|updated` flag later, additive, no break to this contract's default.
Status: FROZEN @ v1 — approved by Tin Dang (via the "updated sort key + cap both text and JSON + --all escape hatch" 3-part decision)

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `.add/tooling/engine_pin.py` · `add-method/src/add_method/_bundled/tooling/engine_pin.py` · `add-method/tooling/test_machine_state.py` · `add-method/tooling/test_wave_status_hint.py` · `add-method/tooling/test_per_stream_owner.py`
Strategy & known-problem fixes: 1. write the 6 new test methods in `test_machine_state.py` red-first (extend the file's existing `_run`/`_json_only` helpers with a small `_set_updated(kind, slug, ts)` fixture helper to set distinct `updated` timestamps); 2. add the `_sorted_by_updated` helper + wire it into the JSON branch and the 2 text-mode loops + the `--all` argparse flag in canonical `add.py`; 3. propagate byte-identically to the 2 mirror trees; 4. run the new tests + the full `test_machine_state.py` file green; 5. re-pin `ENGINE_MD5` (3 trees, narrated-history comment); `ENGINE_PKG_MD5` stays UNCHANGED; 6. run `test_shared_engine_pin` + `test_engine_repin_parity`; 7. run the full `add-method/tooling` suite to confirm zero regressions beyond already-known, disclosed pre-existing failures. Known-problem: existing tests create only 1-3 milestones/tasks per fixture, so the cap (10) never trips them — sort-order changes are the only behavior those tests could notice, and none of them assert positional order today, so this is provably additive against the existing suite; confirmed by reading every existing `status --json`-touching test before starting.
Strategy actually used: as planned, with one discovered addition to Scope: two pre-existing "frozen JSON surface" guard tests (`test_wave_status_hint.test_json_surface_frozen`, `test_per_stream_owner.test_json_milestone_owner_assignee`) each independently enumerate a `sanctioned` set of top-level `status --json` keys allowed to extend the base v4-1 shape — surfaced only by the full-suite run, not by `test_machine_state.py` alone. Both extended with `milestones_total`/`tasks_total`, mirroring the exact ratification style already used for every prior additive key (`actor`, `active_milestones`, etc.); the human's own "cap both text and JSON" decision (this task's freeze) is the ratification.
Code lives in: `add-method/tooling/add.py` (`cmd_status`, 3-tree mirrored)   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `status --json` sorts `milestones[]`/`tasks[]` newest-`updated`-first and caps each to 10 with `milestones_total`/`tasks_total` fields; `--all` reverts to the full sorted list; text mode mirrors both behaviors with a trailing "… N more" note — confirmed green by 6 new methods in `test_machine_state.py` (19/19 in-file) AND confirmed live against this project's real 31-milestone/144-task corpus (`status` shows the 10 most-recently-touched milestones with `… 21 more (see status --all)`; `status --json` reports `tasks_total: 144` while returning 10; `status --all`/`status --json --all` both return the full 31/144). Two pre-existing frozen-JSON-surface guard tests (`test_wave_status_hint`, `test_per_stream_owner`) needed their `sanctioned` key sets extended with `milestones_total`/`tasks_total` — the human's own freeze decision (cap both text AND JSON) is the ratification these tests require by design, not a weakening.

Refute-read (self-adversarial): probed whether extending 2 frozen-surface guard tests was a disguised weakening rather than a legitimate ratification — confirmed by re-reading both tests' own comments, which explicitly document "ONLY sanctioned keys may extend it" as an ADDITIVE amendment mechanism (the exact same mechanism already used 3 times before for `actor`/`active_milestones`/`active_tasks`/`graduation_ready`/`stage_criteria`) — no assertion was loosened, only the sanctioned SET was extended, and the base-key immutability check (`base <= keys`) is untouched. Probed whether the active task/milestone could become invisible under the cap — confirmed the standalone `active  :`/`streams :` lines are untouched and independent of the capped lists, so identity is never lost, only the marked `*` position within a long list. Ran the full `add-method/tooling` suite (2718 tests, one undisturbed run): 9 pre-existing failures — 8 stale `EnginePinTest.test_pin_annotation_names_this_task` checks + the disclosed macOS `grep -cl` portability quirk in `seams-template-wiring`'s own test, both predating this task. `git diff --stat` confirms only the declared 9 files changed. `add.py check`: 655 passed, 0 failed.
Verdict: EARNED. By: self. Adversarially checked: frozen-surface-ratification legitimacy, active-item visibility under the cap, whole-suite regression sweep.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (via the "updated sort key + cap both text and JSON + --all escape hatch" 3-part decision) · date: 2026-07-02

