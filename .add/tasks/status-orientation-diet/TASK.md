# TASK: default status leads with a resume glance card (phase + next verb + file)

slug: status-orientation-diet · created: 2026-07-14 · stage: mvp
milestone: call-residuals
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: default `status` leads with a resume glance card — the plain view opens (right after the do-not-init line) with the active task's phase + next verb + resume file, so a SINGLE status read orients the agent instead of the 3-4×/rep re-reads the WM1 anatomy measured (the resume info exists today but sits at line ~67 of a 69-line dump).
Must:
  - `status` (plain view) with an active task prints a resume glance card as its FIRST content after the do-not-init line: the active slug · `phase=<phase>` · the next-verb line (reusing `_next_footer`) · the resume file `.add/tasks/<slug>/TASK.md`
  - the card appears BEFORE the `project :` line (top-of-view, one glance) and reuses the existing next-verb composer — no divergent wording
  - every existing plain-view line (do-not-init · project · … · the bottom resume block) still prints, in the same relative order, just shifted down (additive)
  - `--brief` / `--json` / `--section` views unchanged; no active task → no card (setup/no-task paths byte-unchanged)
Reject:
  - none — message-layer reorder/surface only; no gate / enforcement / state change (milestone OUT-of-scope)
Accept: Given a project with an active in-progress task, When `add.py status` runs, Then the output's first lines (before `project :`) name the task, its phase, the next verb, and its TASK.md path — so no re-read is needed to resume
Boundary: none — no external input shape; the branch is active-task-present vs absent
Assumptions: ⚠ agents re-read because the resume sits at the BOTTOM, not because it's absent — evidence: the 69-line default view carries the full resume block only at line ~67; if wrong (they re-read for other reasons): the top card still can't hurt, it's additive and derived

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add-method/tooling/add.py:cmd_status` (insert the card right after the do-not-init line, add.py:2824, before the `project :` line); it READS `_active_task` · `_next_footer` (the ONE next-verb composer, also used by --brief) — both unchanged
Context (working folder): `add-method/tooling/` (canonical engine). The full write-set — canonical add.py, its 3 engine twins, engine_pin.py, the new test — is the §5 Scope below; ENGINE_MD5 + SEAMS re-aimed as part of any engine edit
Honors (patterns / conventions): the plain-view "additive — every existing line stays put" idiom (same as the goal/run-mode lines added before it); reuse `_next_footer` (no parallel next-verb logic); the summary-first pattern (report-template) — glance card at top, detailed resume block stays at the bottom for the loop-chapter steering
Anchors the contract cites: `cmd_status` (edited) · `_active_task`, `_next_footer` (read) · `.add/tasks/<slug>/TASK.md` (the resume file)
Ground SHA: 86d9d22 — stamped by freeze

### Contract

```
cmd_status, PLAIN view (not --brief/--json/--section), active task present in state.tasks:
  → immediately AFTER "project exists — do not re-init …" and BEFORE "project :", print:
      line 1: "now     : '<active>' · phase=<phase> · <_next_footer(root, state)>"
      line 2: "          TASK.md: .add/tasks/<active>/TASK.md   ·   re-orient: add.py status --brief"
  → every existing plain-view line still prints, same relative order, shifted down (additive)
cmd_status, PLAIN view, NO active task (setup / done-with-none):
  → no card (byte-unchanged)
cmd_status --brief / --json / --section:
  → unchanged
```

`Least-sure flag surfaced at freeze:` [contract] the card LABEL ("now") + exact 2-line shape — cosmetic; if wrong, a one-string relabel. The one hard edge: the card must NOT reprint the bottom `resume  :` block's prefix (distinct "now" label) so the ~8 tests pinning that block stay green.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/tooling/test_status_orientation_diet.py`
Strategy & known-problem fixes: (1) RED first: new test_status_orientation_diet asserts plain `status` with an active in-progress task emits a "now     :" card carrying the phase + the next verb + the `.add/tasks/<slug>/TASK.md` path, positioned BEFORE the "project :" line; and --brief stays 2-line. (2) in cmd_status after the do-not-init print (add.py:2824), when `_active_task` resolves in state.tasks, print the 2-line card reusing `_next_footer` (trap: distinct "now" label — do NOT collide with the bottom "resume  :" block that ~8 tests pin; and guard on active-task-present so setup/no-task paths stay byte-identical). (3) sync ×4 twins, re-pin ENGINE_MD5 + SEAMS.
Approach (domain strategy): summary-first glance card, additive

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — no divergence. Inserted the 2-line "now" card in cmd_status right after the do-not-init print, guarded on `_active_task in state.tasks`, reusing `_next_footer`. Synced ×4 twins, ENGINE_MD5→c0c972e2, SEAMS _declared_scope 5677→5688.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (full fence)
- [x] green was EARNED — the 3 card asserts RED first (positioned before project:, phase, file); brief-unchanged + no-card guards green throughout; GREEN only after the insert
- [x] input dialect held — the test speaks the real status stdout dialect
- [x] no exposed secrets, injection openings, or unexpected dependencies (pure stdout reorder; security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): `add.py status` on a project with an active task prints, as line 2 (before `project :`), `now     : '<slug>' · phase=<phase> · next: <verb>` then `          TASK.md: .add/tasks/<slug>/TASK.md · re-orient: add.py status --brief`; `--brief` stays 2 lines; no card when no active task — confirmed by test_status_orientation_diet (5 asserts) + the live dogfood status showing the card first + green engine/seams/parity guards in the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

