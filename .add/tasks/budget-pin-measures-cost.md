---
type: Task
title: The always-loaded budget pin measures the cost it names
status: done
depth: quick
scope:
  - add-method/tests/skill/test_surface.py
gives:
  - S1 `tests/skill/test_surface.py::test_skill_byte_budget_holds` — a byte-count pin on SKILL.md, ratcheted to the currently measured real cost
  - S2 `tests/skill/test_surface.py::test_byte_pin_catches_a_pure_reflow_the_line_pin_would_miss` — proof the byte pin fires on a reflow fixture (same content, fewer lines, more bytes) that the line-only pin would pass
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: freeze, authority: process, direction: "sha256:967eac72a5f63171", binding: "sha256:acdb0e90280747a4" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:17259bb82ed0dc11" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/budget-pin-measures-cost.d/runs/1.md }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/budget-pin-measures-cost.d/runs/2.md }
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: refreeze, authority: process, direction: "sha256:660706739d5d5eb6", binding: "sha256:acdb0e90280747a4" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:af05bb630715b5cd" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/budget-pin-measures-cost.d/runs/3.md }
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/budget-pin-measures-cost.d/runs/3.md, brief: "sha256:af05bb630715b5cd" }
---
## CARD
goal: add a byte-count pin alongside the existing line-count pin so SKILL.md's real always-loaded cost cannot rise while its line count falls
why: `test_router_within_line_budget` counts newlines and calls itself "the only always-loaded cost" — a reflow (same content, fewer lines, more bytes) moves the metric without moving the cost, and this session it happened for real (176/176 lines held while the file grew 189 bytes)
beat: done · next: add status

## RULES
<must>
- M1 the budget suite rejects a change that grows SKILL.md's real byte cost even when it shrinks the line count — the reflow hole is closed, not narrowed
- M2 the existing human-set line pin (176, "re-pinned from 150 at 3.1.0, human call") stays in its own unit, unedited, unreplaced — this task never silently re-casts a human's number to a different unit
- M3 the new byte pin is set at the CURRENTLY measured byte count of `skill/add/SKILL.md` and never grants headroom — it is a ratchet, not a new allowance
- M4 the `n <= (\d+)` regex in `test_deltas_before_planning.py::test_skill_budget_holds_at_the_pinned_line_count` keeps harvesting the LINE pin (176) correctly — no earlier or colliding "n followed by <= and digits" text is introduced upstream of it
- M5 no skill-tree prose file (`SKILL.md`, `intake.md`, or anything under `skill/add/`) is edited by this task — a new pin that is red against shipped content is a finding to report, never prose to fix
</must>
<reject>
- R:REDUNDANT_DELETE a reader treats the byte pin as a duplicate of the line pin and deletes one -> "REDUNDANT_DELETE"
- R:PROSE_FIX editing skill-tree content to make the new pin pass, instead of reporting a red pin against current content -> "PROSE_FIX"
- R:SILENT_REPIN converting the human's 176-line number to a byte number instead of adding a second pin alongside it -> "SILENT_REPIN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say who is expected to act when the byte pin trips (human vs. building agent); taking "the same actor the line pin already binds — any agent growing SKILL.md pays down elsewhere; no new class of responsible party" -> cost if wrong: n/a, this is the pre-existing behavior of the sibling line pin, not a new obligation · probe: the byte pin's failure message is self-sufficient (states the number and the two-pins rationale) without needing a human referee
- A2 [which] covers: S1,S2 · the request does not say which of the three shipped skill trees the byte pin measures; taking "the SOURCE tree only (`skill/add/SKILL.md`), same scope as the existing line pin — the two mirror trees stay bound by the pre-existing byte-identical parity test (`test_quick_lane_size_gate.py::test_three_skill_trees_identical`), not duplicated here" -> cost if wrong: a mirror-tree drift goes uncaught by THIS pin, but is already caught by the parity test, so the practical exposure is near zero · probe: the new test opens only `SKILL / "SKILL.md"`, never iterates the three-tree TREES tuple
- A3 [when] covers: S1 · the request does not say what byte value to ratchet against; taking "the CURRENT measured byte count at authoring time — 13258, `len((SKILL/'SKILL.md').read_bytes())` on this branch's HEAD" -> cost if wrong: a mismeasurement makes the pin red immediately at freeze/build (the intended fail-safe — report, never silence), not a silent miss · probe: `test_skill_byte_budget_holds` compares real `read_bytes()` length to the literal 13258
- A4 [absent] covers: S1,S2 · the request does not say what happens if SKILL.md is missing or unreadable; taking "unchanged from every other test in this file — `read_bytes()`/`read_text()` raises and the test errors; no new guard added, no new risk introduced" -> cost if wrong: an unhelpful raw traceback on a missing file, a pre-existing risk this task does not change
- A5 [order] covers: S1,S2 · the request does not say where the new tests sit relative to `test_router_within_line_budget`; taking "immediately after it, before `test_no_single_ref_over_split_threshold`, using the variable name `nbytes` (never a name ending in the letter `n` before ` <= `) so no earlier or colliding match for the harvesting regex `n <= (\d+)` is introduced" -> cost if wrong: `test_skill_budget_holds_at_the_pinned_line_count` in test_deltas_before_planning.py silently reads the WRONG pin · probe: that sibling test still asserts pin == 176 after this file changes (E2)
- A6 [experience] covers: S1,S2 · the request does not say how the next reader is kept from treating the byte pin as redundant with the line pin; taking "the byte pin's own assertion failure message states, inline, why two pins exist (different units, different vulnerability closed) and what deleting either one reopens" -> cost if wrong: exactly the failure class this task exists to close reopens the next time someone "simplifies" the budget suite · probe: the failure message in `_assert_within_byte_budget` names both pins and the reflow hole

## PLAN
contract: two new test functions plus one private helper added to `add-method/tests/skill/test_surface.py` — `_assert_within_byte_budget(nbytes, budget)` (the reusable guard body, its message carrying the two-pins rationale), `test_skill_byte_budget_holds` (the real pin, ratcheted to 13258 bytes on `skill/add/SKILL.md`), and `test_byte_pin_catches_a_pure_reflow_the_line_pin_would_miss` (a fixture-built proof that the guard fires on a reflow the line pin would miss). No production code changes; no skill-tree prose changes.

## EDGES
- E1 a reflow that keeps bytes flat or shrinks them while cutting lines (real compression, not a reflow) must still pass both pins — not a dedicated new check; the existing green run of both pins against the real, currently-shipped SKILL.md already demonstrates legitimate content passes
- E2 the sibling regex consumer `test_deltas_before_planning.py::test_skill_budget_holds_at_the_pinned_line_count` must still harvest pin == 176 and stay green after this file's edit
- E3 the new byte pin, run as-is against the CURRENTLY SHIPPED SKILL.md, must be GREEN — it is a ratchet at the measured cost, not a stricter unmet bar; if it comes up red, that is a real finding to report, never prose to silence (M5)

## CHECKS
- test_skill_byte_budget_holds · covers: M1,M3,A3,E3 · SKILL.md's real byte count stays at/under the pinned ceiling (13258)
- test_byte_pin_catches_a_pure_reflow_the_line_pin_would_miss · covers: M1,E1,A1,A6,R:REDUNDANT_DELETE · proves a reflow fixture that shrinks lines 176→88 while growing bytes 13258→13698 passes the OLD line-only pin but fails the new byte guard, via the same self-sufficient message A1 requires
- test_line_pin_survives_unreplaced_by_this_task · covers: M2,R:SILENT_REPIN · the line-pin test, its 176 literal and its human-call rationale are still present and unedited in test_surface.py
- test_byte_pin_scoped_to_source_tree_only · covers: A2 · the byte pin's own source reads only `SKILL / "SKILL.md"`, never iterates the three-tree TREES tuple
- test_skill_tree_prose_unedited_by_this_task · covers: M5,R:PROSE_FIX · SKILL.md and intake.md sha256-match the hashes measured when this task was authored — no skill-tree prose touched
- test_skill_budget_holds_at_the_pinned_line_count · covers: M4,A5,E2 · pre-existing regression check (test_deltas_before_planning.py) — the harvested line pin stays 176 and the new tests' placement (after the line pin, before the split-threshold test) never disturbs it
red-first: every check MUST fail first, or — for the two check shapes that are ratchets/regressions pinned to the CURRENT measured state and so expected green on first run (`test_skill_byte_budget_holds`; the three new introspective proofs `test_line_pin_survives_unreplaced_by_this_task`, `test_byte_pin_scoped_to_source_tree_only`, `test_skill_tree_prose_unedited_by_this_task`) — proven non-vacuous by a temporary perturbation of the subject (a wrong literal, a wrong hash, an injected disqualifying string), confirming the assertion fires, then restoring the true value. Evidence: byte-budget perturbation run live against the suite (see receipt 1); the three introspective proofs perturbed via an isolated interpreter run outside the file (never landed on disk) — see the task's Return for the transcript.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
