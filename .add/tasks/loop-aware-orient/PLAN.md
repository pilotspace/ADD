# TASK: status+guide route into the loop at the loop juncture; fix loop.md cue

slug: loop-aware-orient · created: 2026-06-24 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
  - `add-method/tooling/add.py:cmd_status` — done-task resume branch (the `if ph == "done":` arm,
    today prints "start the next feature: add.py new-task <slug>" UNCONDITIONALLY — milestone-goal-blind)
  - `add-method/tooling/add.py:cmd_guide` — done-phase branch (`next:`/`read:`/`then:` lines) +
    its `--json` surface (`next_step`/`chapter`), both sourced from `PHASE_GUIDE["done"]`
  - `add-method/tooling/add.py:PHASE_GUIDE` — the `"done": (…, "02-the-flow.md")` entry (the static route)
  - `add-method/tooling/add.py:_exit_criteria(root, mslug)` — (met, total) tally helper (READ-ONLY, exists)
  - `add-method/tooling/add.py:_active_milestone` / task `.milestone` key — to resolve the active milestone
Engine parity (build must propagate + repin): 3 trees —
  `add-method/tooling/add.py` (canonical) · `.add/tooling/add.py` (dogfood) ·
  `add-method/src/add_method/_bundled/tooling/add.py` (bundled); pin = `add-method/tooling/engine_pin.py:ENGINE_MD5`
Docs: skill guide `loop.md` (the cue-attribution claim "status shows goal not met (m/n)") + book `09-the-loop.md`
Anchors the contract cites: `cmd_status`, `cmd_guide`, `_exit_criteria`, a new `_done_resume` helper

---

## 1 · SPECIFY — the rules

Feature: milestone-goal-aware "what next" on the orient surfaces (status + guide) at a done task
Must:
  - A new pure helper `_done_resume(root, state, slug)` classifies a DONE task's next move from its
    milestone's exit-criteria tally (`_exit_criteria`): LOOP-JUNCTURE (total>0 and met<total) ·
    GOAL-MET (total>0 and met==total) · PLAIN (total==0 or no milestone).
  - `cmd_status` done-task resume uses it: LOOP-JUNCTURE → names the unmet milestone + (m/n) and
    points to the loop; GOAL-MET → points to `add.py milestone-done <ms>`; PLAIN → today's
    "start the next feature: add.py new-task <slug>" (byte-identical).
  - `cmd_guide` done-phase branch (human AND --json) routes via the same helper: LOOP-JUNCTURE/GOAL-MET
    → chapter `09-the-loop.md`; PLAIN → `02-the-flow.md` (today's route). The `then:`/`next_step`
    line names the matching command (loop / milestone-done / new-task).
  - Helper is READ-ONLY (no save_state); both surfaces stay strictly read-only as today.
  - `loop.md` (skill guide) cue claim is aligned to the ACTUAL status copy now printed (no longer a
    false attribution); `09-the-loop.md` checked for the same claim.
Reject:
  - corrupted/missing milestone or unreadable MILESTONE.md -> fall back to PLAIN (never raise) -> "plain_fallback"
Accept: Given an active milestone with all tasks done and 0/1 exit criteria met, When `add.py status`
  and `add.py guide` run, Then status resume names "goal not met (0/1)" + the loop and guide reads
  `09-the-loop.md` — AND with the box checked (1/1) both point to `milestone-done`, AND with no
  criteria both are byte-identical to today.
Assumptions: ⚠ status/guide output is asserted byte-wise by sibling tests (test_status*, test_guide*,
  test_dynamic_task_loop) — the PLAIN branch MUST stay byte-identical or those go red. If wrong: a
  rebaseline of unrelated tests (caught at build, not a real regression). Biggest design risk: whether
  to touch --json (chosen: yes, to avoid a human-says-loop/json-says-flow split).

---

## 3 · CONTRACT — freeze the shape

```
# New pure helper (READ-ONLY; no save_state):
_done_resume(root: Path, state: dict, slug: str) -> tuple[str, str, str]
    returns (headline, next_step, chapter)
    where chapter ∈ {"09-the-loop.md", "02-the-flow.md"} (a docs/ filename, no path prefix)
    cases (read milestone = state["tasks"][slug].get("milestone"); met,total = _exit_criteria(root, ms)):
      LOOP-JUNCTURE  total>0 and met<total :
        ("milestone '<ms>' goal not met (<m>/<n> exit criteria)",
         "propose the next tasks from open deltas / the unscaffolded plan -> add.py deltas",
         "09-the-loop.md")
      GOAL-MET       total>0 and met==total :
        ("milestone '<ms>' goal met (<m>/<n>)",
         "close it -> add.py milestone-done <ms>",
         "09-the-loop.md")
      PLAIN          total==0 or no milestone or any read error :
        ("this task is done",
         "start the next feature -> add.py new-task <slug>",
         "02-the-flow.md")

# cmd_status — done branch (line ~1893), LOOP-JUNCTURE example:
resume  : task '<slug>' is done (PASS).
          milestone '<ms>' goal not met (0/1 exit criteria) — propose the next tasks
          from open deltas / the unscaffolded plan -> add.py deltas   (the loop: 09-the-loop.md)
#   GOAL-MET -> "...goal met (1/1) — close it -> add.py milestone-done <ms>"
#   PLAIN    -> BYTE-IDENTICAL to today: "start the next feature: add.py new-task <slug>"

# cmd_guide — done branch (human), LOOP-JUNCTURE:
next   : <next_step from helper>{marker}
read   : .add/docs/09-the-loop.md
then   : add.py deltas        # GOAL-MET -> milestone-done <ms> ; PLAIN -> new-task <slug>
# cmd_guide --json done -> next_step + chapter follow the SAME helper (".add/docs/<chapter>")
```

`Least-sure flag surfaced at freeze:` [spec] the exact resume COPY at the loop juncture (wording of the
headline + whether `then:`/next_step points at `add.py deltas` vs a generic "propose next tasks"). If
wrong: pure copy churn — a test string update, no logic change. Functionally low-risk; named so the
human freezes the WORDING now, since tests will pin it.
Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization; freeze confirmed 2026-06-24)
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: `add-method/tooling/test_loop_aware_orient.py` — a live board (like test_dynamic_task_loop):
init → milestone → drive task to done, then set the box, and assert the orient copy:
  - test_status_loop_juncture_names_goal_and_loop — 0/1 met → status resume contains
    "goal not met (0/1" AND "09-the-loop.md" AND NOT "start the next feature"
  - test_guide_loop_juncture_routes_to_loop_chapter — 0/1 met → guide `read:` line == 09-the-loop.md
    (human) AND `guide --json` chapter ends "/09-the-loop.md"
  - test_goal_met_points_to_milestone_done — 1/1 met → status + guide name "milestone-done"
  - test_no_criteria_byte_identical — 0 criteria → status resume + guide done branch byte-identical
    to a pre-change golden ("start the next feature" / 02-the-flow.md)
  - test_done_resume_fallback_on_unreadable_milestone — missing/garbled MILESTONE.md → PLAIN (no raise)
  - test_loop_md_cue_matches_engine — loop.md's quoted status cue string is a substring the engine
    actually prints at the loop juncture (doc-accord; the misattribution guard)
Tests live in: `add-method/tooling/test_loop_aware_orient.py` · MUST run red (helper absent /
old copy) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` · `add-method/src/add_method/_bundled/tooling/` · `.add/tooling/`
  <!-- dir tokens (whole-subtree): canonical add.py + engine_pin.py + the new test · bundled add.py · dogfood add.py. ALL on this first line — the scope parser reads only the first declaring line. loop.md/09-the-loop.md NOT edited (the engine change healed the doc cue), so not in scope. -->
Code lives in: `add-method/tooling/`   ·   Constraints: change no test, no contract; allow-list packages only (stdlib only — no new deps).

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 1666/0 (was 1657 + my 9); test_dynamic_task_loop + test_tree_parity green; no frozen-contract or pre-existing test edited
- [x] green was EARNED — the 9 tests ran RED first (5 fail + 2 AttributeError on absent `_done_resume`), then GREEN after the build; the 2 PLAIN-case tests were green BEFORE the build too (they pin byte-identical legacy output — proving no overfit)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — pure stdlib; `_done_resume` is READ-ONLY (no save_state), broad `except` only degrades to PLAIN; no new deps; SECURITY = clean
- [x] §5 scope honored — anchor `declared` corrected to the live 3 dir-tokens (the multi-line capture bug; file-baseline kept pre-build); `add.py check` 382/0, scope_violation cleared; `add.py audit` clean (74 tasks)
- [x] 3-tree engine parity + repin — canonical == bundled == dogfood, ENGINE_MD5 → ba1f21fbfbf5df15702bec9a14511155

Build expectations (from §1 Accept + §3 CONTRACT): at a live loop juncture (all tasks done, 0/n met),
`add.py status` resume prints "milestone '<ms>' goal not met (m/n exit criteria) … add.py deltas" + the
loop pointer, and `add.py guide` (human `read:` AND `--json` `chapter`) routes to `09-the-loop.md`, NOT
"start the next feature"/02-the-flow.md — confirmed by test_status_loop_juncture_names_goal_and_loop +
test_guide_loop_juncture_routes_to_loop_chapter + test_guide_json_loop_juncture_chapter. Box checked
(m==n) → both name `milestone-done` (test_status_goal_met_points_to_milestone_done). No criteria →
byte-identical to today (test_status_no_criteria_keeps_plain_resume + test_guide_no_criteria_keeps_flow_chapter).
loop.md cue HEALED: the engine now prints "goal not met (m/n exit criteria)", making loop.md's status
attribution TRUE (test_loop_md_cue_matches_engine) — no doc edit needed.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-24
OBSERVE: [SPEC · open] consider renaming `report <ms>` VERDICT from `DONE` to `IN-LOOP` when tasks are all done but exit criteria are unmet — today the header reads DONE while CRITERIA shows m/n<1, corrected only by the DECIDE-NEXT footer (evidence: live probe at the loop juncture — VERDICT DONE with CRITERIA 0/1 met)
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
