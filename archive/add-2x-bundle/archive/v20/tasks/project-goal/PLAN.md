# TASK: Explicit project GOAL in the foundation, surfaced by status/guide

slug: project-goal · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — edits the always-read foundation (PROJECT.md) and the frozen status/guide output
     seam; "method/trust-layer edits are a residue category" (foundation §Domain). autonomy lowered to
     conservative: the verify gate stops for the human. The fields on the slug line ARE the declaration. -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: give the project an explicit GOAL — the durable outcome the whole project runs toward — declared once in PROJECT.md and surfaced by `status` (and `guide`) alongside the active milestone's goal, so every session and every loop orients to the goal before the next step. The loop's anchor: the rest of v20 (deep verify · reopen · dynamic tasks) drives toward THIS.
Framings weighed: top-of-PROJECT.md `goal:` line, read LIVE from the file, status shows project-GOAL + active-milestone-goal (chosen — mirrors how MILESTONE.md already carries `goal:`; single-source = no drift; "both goals" answers the user's "project AND milestone have goals") · a `## Goal` prose section (rejected: heavier on the one-screen foundation; a one-line `goal:` is greppable like the milestone's) · duplicate the goal into state.json for the engine (rejected: state.json would drift from PROJECT.md — the foundation is the source of truth; report already reads milestone `goal:` straight from MILESTONE.md)
Must:
<must>
  - PROJECT.md carries an explicit project GOAL as a single `goal:` line near the top (parallel to MILESTONE.md's `goal:` line) — one durable outcome sentence
  - `add.py status` prints the project GOAL in its orientation output, read LIVE from PROJECT.md (never duplicated into state.json)
  - `add.py status` ALSO prints the active milestone's goal (read from that milestone's MILESTONE.md) next to the project GOAL — so the orientation shows project-goal + milestone-goal together
  - `add.py guide` prints the project GOAL on its orientation line too (the per-task next-step surface still shows what the work is FOR)
  - the GOAL line is ADDITIVE on the status/guide output seam — every existing line, field, and exit code is byte-unchanged for existing consumers (additive-evolution)
  - GOAL is added to GLOSSARY.md as a defined term (the durable project/milestone outcome the loop runs toward; distinct from a task's §1 Must)
</must>
Reject:
<reject>
  - PROJECT.md has no `goal:` line (or it is blank) -> status/guide render an actionable `goal: (unset — add a 'goal:' line to PROJECT.md)` hint, never a blank line and never a stack trace -> "goal_unset"
  - the active milestone's MILESTONE.md is unreadable / has no `goal:` -> the milestone-goal slot renders `(unset)`, the project GOAL still prints (one missing source never blanks the other) -> "milestone_goal_unreadable"
</reject>
After:
<after>
  - PROJECT.md has a top `goal:` line; `status` and `guide` print the project GOAL sourced live from the file, `status` also prints the active milestone's goal; a missing source degrades to a named `(unset)` hint, never a blank or a trace; existing status/guide output is otherwise byte-identical; GLOSSARY defines GOAL.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ surfacing BOTH the project GOAL and the active-milestone goal on `status` is what's wanted (vs the project GOAL only) — lowest confidence because "project AND milestone have goals" may mean "both must EXIST" (milestone goal already does) rather than "both must RENDER on status"; if wrong: drop the milestone-goal line from the render — a one-line change, the project-GOAL Must is unaffected
  ⚠ placement as a single top-of-PROJECT.md `goal:` line (vs a `## Goal` section) — low confidence on FORM, not substance; if wrong: move the line into a section and re-point the one grep — the render + tests are unchanged
  - [ ] reading the GOAL live from PROJECT.md / MILESTONE.md (never copied into state.json) is correct — high confidence: matches the milestone-goal precedent (report reads MILESTONE.md `goal:` directly) and "the foundation is the source of truth"
  - [ ] `guide` showing the project GOAL (not the milestone goal) is the right split — high confidence: guide is the per-task next-step surface; the full project+milestone orientation belongs on `status`
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: status surfaces the project GOAL live from PROJECT.md
  Given a project whose PROJECT.md has a `goal:` line "ship ADD as a product"
  When I run `add.py status`
  Then the output shows a goal line containing "ship ADD as a product"
  And the project / stage / context / active lines are all still present (additive)

Scenario: status surfaces the active milestone's goal next to the project GOAL
  Given a project with a project `goal:` line and an active milestone whose MILESTONE.md goal is "deepen verify"
  When I run `add.py status`
  Then the output shows the active milestone's goal "deepen verify" attributed to its slug
  And the project GOAL line is still present (both goals render together)

Scenario: guide surfaces the project GOAL on its orientation block
  Given a project whose PROJECT.md has a `goal:` line and an active task
  When I run `add.py guide`
  Then the output shows the project GOAL
  And the existing active / next / read lines are unchanged (additive)

Scenario: a missing project goal renders an actionable hint, never blank or a trace   # goal_unset
  Given a PROJECT.md with NO `goal:` line
  When I run `add.py status`
  Then the goal line reads "(unset — add a 'goal:' line to PROJECT.md)"
  And status exits 0 and still prints the rest of its output (no crash, no blank line)

Scenario: an unreadable active-milestone goal degrades without blanking the project GOAL   # milestone_goal_unreadable
  Given a project with a project `goal:` line but the active milestone's MILESTONE.md missing / without a goal
  When I run `add.py status`
  Then the milestone-goal slot renders "(unknown)"
  And the project GOAL line still prints (one missing source never blanks the other)

Scenario: GOAL is a defined GLOSSARY term
  Given the shipped GLOSSARY.md
  When I read it
  Then it defines GOAL as the durable project / milestone outcome the loop runs toward
  And it distinguishes GOAL from a task's §1 Must

Scenario: the PROJECT.md scaffold template carries a goal line
  Given a freshly `init`-ed project
  When I read its .add/PROJECT.md
  Then it has a `goal:` line (a placeholder a new project fills at setup)
  And the existing foundation sections (Domain / Spec / UDD) are unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# CLI output-seam contract — read-only orientation surfaces. Goal sources are READ, never written;
# a missing/blank source degrades to a sentinel and the command STILL exits 0 (orientation never crashes).

helper  _project_goal(root: Path) -> str
  returns the value of the FIRST line in PROJECT.md that starts with "goal:" (stripped),
  else the sentinel  GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
  when PROJECT.md is missing / has no goal: line / the value is blank.
  Read-only; never raises on a missing or unreadable file (fail-closed -> sentinel).

add.py status   (human / non-json)
  ADDS, in the top orientation block:
      goal    : <project GOAL | GOAL_UNSET>
  ADDS, when an active milestone exists (goal via the existing _milestone_doc):
      m-goal  : <active-milestone goal | "(unknown)">   (← <active-milestone-slug>)
  UNCHANGED: every pre-existing line (project/stage/context/wave/milestones/archived/active/
             tasks/deltas/setup/resume), their labels + order, and exit code 0.

add.py guide    (human / non-json)
  ADDS, in the orientation block (printed whenever a task context is shown):
      goal   : <project GOAL | GOAL_UNSET>
  UNCHANGED: active/next/read/guide/then lines and the exit code.

templates/PROJECT.md.tmpl
  ADDS a `goal:` line under the slug line (a placeholder a new project fills at setup);
  Domain / Spec / UDD sections unchanged.

GLOSSARY.md
  ADDS a GOAL term (durable project/milestone outcome the loop runs toward; ≠ a task §1 Must).

Reject (render states, NOT non-zero exits):
  goal_unset                 -> status + guide print GOAL_UNSET, exit 0
  milestone_goal_unreadable  -> status m-goal prints "(unknown)", project goal still prints, exit 0

Out of scope (additive, deferred — no existing key altered): a `goal` key in `status --json` /
  `guide --json`. The JSON facts seam is NOT extended here (milestone goal is likewise absent from
  --json today — the goal lives on the human orientation surface).

Schema: reads PROJECT.md (first `goal:` line) + active milestone MILESTONE.md (via _milestone_doc).
        No writes. No state.json field added — single-source from the docs (no drift).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08 (both ⚠ flags accepted: render both goals; goal: line placement)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every new line/branch in `_project_goal` + the status/guide goal renders is covered; the full suite stays green (586 → 586+9).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_project_goal_reads_first_line:        PROJECT.md `goal: X` -> `_project_goal(root) == "X"`
  - test_project_goal_unset_sentinel:          PROJECT.md with no goal: line -> `_project_goal(root) == GOAL_UNSET`
  - test_status_prints_project_goal:           status out contains the project GOAL AND the existing project/stage/active lines (additive)
  - test_status_prints_active_milestone_goal:  status out shows the active milestone goal attributed to its slug; project GOAL still present
  - test_guide_prints_project_goal:            guide out contains the project GOAL AND the existing active/next/read lines (additive)
  - test_status_goal_unset_hint_not_blank:     status with no goal: line shows the unset hint, exits 0, still prints the rest
  - test_status_milestone_goal_unreadable:     active MILESTONE.md gone -> m-goal "(unknown)", project GOAL still prints, exit 0
  - test_glossary_defines_goal:                init-scaffolded GLOSSARY.md defines GOAL and separates it from a task §1 Must
  - test_project_template_has_goal_line:       a freshly init-ed .add/PROJECT.md has a `goal:` line; Domain/Spec/UDD intact
</test_plan>

Tests live in: `add-method/tooling/test_project_goal.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the goal sources are READ-ONLY and FAIL-CLOSED — `_project_goal`/`_milestone_doc` never raise on a missing/unreadable doc; `status`/`guide` keep exit code 0. No state.json field (single-source from the docs → no drift).
Code lives in: `add-method/tooling/add.py` (canonical) — mirrored byte-identical to `.add/tooling/add.py` + `add-method/src/add_method/_bundled/tooling/add.py`; `templates/{PROJECT,GLOSSARY}.md.tmpl` (3 trees); living `.add/PROJECT.md` (real goal) + `.add/GLOSSARY.md` (GOAL term); pin re-aimed in `engine_pin.py`.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — no new dep); ask if unclear.

BUILT: `GOAL_UNSET` const + `_project_goal(root)` reader (mirrors `_milestone_doc`); `cmd_status` prints `goal`/`m-goal` (additive, after stage); `cmd_guide` prints `goal` (additive, after active). 3 engine copies md5-identical (54f54e3…); ENGINE_MD5 pin re-aimed 1082fd0…→54f54e3…. Suite: 586→595 green (9 new, 0 regressions). Dogfood: `status`/`guide` render the real project GOAL + v20 milestone goal live.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 586 → 595 green (9 new project-goal tests, 0 regressions)
- [x] coverage did not decrease — every new branch in `_project_goal` + the goal/m-goal/guide renders is exercised
- [x] no test or contract was altered during build — only ADDED `test_project_goal.py` (untracked); contract FROZEN @ v1 untouched
- [x] concurrency / timing — N/A: read-only orientation commands, no shared mutable state, no writes
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (no new import); reads are utf-8 + OSError-guarded, fail-closed
- [x] layering & dependencies follow CONVENTIONS.md — additive-evolution (existing lines/exit codes unchanged), single-source (no state.json field), dogfood-parity (3 engine copies md5-identical 54f54e3…; pin re-aimed)
- [x] a person reviewed and approved the change — Tin Dang recorded PASS at the conservative gate 2026-06-08

### Deep checks (dogfooding v20's deepened verify on the first task)
- [x] WIRING cross-check — `_project_goal` is referenced by cmd_status (L669) AND cmd_guide (L813); serena find_referencing_symbols confirms 2 callers. Not orphaned.
- [x] NEW unused/dead code — none: no defined-but-unused symbol; `_active_ms` is read+used, does not shadow the later `active_ms`.
- [x] SEMANTIC re-read (no skim) — `m-goal` degrades to `(unknown)` via the existing `_milestone_doc` when the doc is gone; project GOAL prints independently; `goal_unset` → GOAL_UNSET sentinel, exit 0. The two ⚠ freeze flags (render both goals · `goal:` line placement) were accepted at the freeze.
- [x] SECURITY — no finding (HARD-STOP would be mandatory otherwise). Read-only file access, no eval/exec, no network, no new dep.

### GATE RECORD
Outcome: PASS   (conservative, human-gated — Tin Dang owned the gate)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): on real sessions, does `goal:` actually re-orient — does an agent
resuming mid-milestone read the goal line and stay on-theme, or scroll past it? Does any project ship with
the goal still unset (sentinel printed but ignored)? Does the m-goal render survive a milestone archive
(does `_milestone_doc` still resolve, or degrade to `(unknown)`)?
Spec delta for the next loop: the goal line is now an always-on orientation surface — the first ADD output
seam that reads live from a foundation doc rather than state.json. If later work adds more such live-read
surfaces (e.g. exit-criteria progress on status), they should share one reader convention, not each re-walk
PROJECT.md. Disclosed here; no contract owns it yet.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [UDD · folded] a freshly-`init`'d project's `status` prints the PROJECT.md template's literal `goal: <the one
  durable outcome…>` placeholder verbatim, at the most-lost moment — colliding with the UDD principle "one
  clear next step at the most-lost moment" (evidence: template ships an angle-bracket placeholder; `goal_unset`
  rejects only absent/blank, so a placeholder passes through; goal line prints before the first-run panel).
  Contract-compliant (mapping placeholder→GOAL_UNSET would be a contract change, not a fix), so it did NOT
  block this gate — it is the first real feed-forward item for **dynamic-task-loop** to turn into a follow-up
  task (soften the template text to drop the brackets, or teach `_project_goal` a placeholder sentinel).
