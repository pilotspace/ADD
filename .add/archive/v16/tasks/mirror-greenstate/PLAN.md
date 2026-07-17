# TASK: v16 green-state sweep: full suite + 3-mirror parity + audit

slug: mirror-greenstate · created: 2026-06-06 · stage: mvp
autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the v16 closing GATE — prove the XML convention is applied consistently across the ENTIRE
prompt surface and that all 3 distribution mirrors are byte-identical and green. This task writes NO new
prose tags; it is the integration sweep the milestone's final exit criterion names.
Framings weighed: full-sweep-as-its-own-task (chosen) · fold-sweep-into-task-4 · trust-per-task-greens-only

Must:
  - The WHOLE unittest suite passes (every test file, not just the convention guard).
  - `test_bundle_parity` is green — canonical `skill/add` + `tooling/` + `docs/` + `add.py` are byte-identical
    to the Python package `_bundled/` tree, with zero test/junk files shipped.
  - `test_tree_parity` is green — canonical `skill/add` is byte-identical to `.claude/skills/add`.
  - `add.py audit` is clean across every task.
  - The convention vocabulary is fully and ONLY the frozen 5 across the v16 surface — a census of
    `<prompt>/<exit_gate>/<output_format>/<constraints>/<reject_codes>` shows each tag in active use and
    no 6th tag anywhere.
Reject:
  - any test red                                                               -> "suite_red"
  - any mirror drift (bundle or tree parity fails)                             -> "mirror_drift"
  - an audit finding                                                            -> "audit_dirty"
  - a convention tag outside the frozen 5 found anywhere on the surface         -> "vocab_offmidiom"
After:
  - Full suite + both parity guards + audit are all green; the 5-tag census confirms the convention is
    whole (all five used) and closed (no others). v16's exit criteria are all observably met.
Assumptions — least-sure first:
  ⚠ The per-task greens compose into a whole-surface green with no cross-task interaction. Least sure because
    each task verified its own slice; this is the first run that asserts ALL of it at once. If wrong: a
    cross-file regression hides behind green per-task runs. Mitigation: the full `discover` run + both parity
    guards + audit + the vocab census are exactly the cross-cutting checks; all green this build. Cost if
    wrong: a follow-up fix task — but the sweep is precisely what would surface it, and it did not.
  - [ ] No 6th convention tag crept in across 18 skill files + appendix-b — grounded: the census returns only
        the frozen 5, and every per-file vocab test asserts a STRICT subset.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the whole suite is green                     # Must: full suite passes
  Given the converted v16 surface (skill/ tasks 1–3 + appendix-b task 4)
  When `python3 -m unittest discover` runs over every test_*.py
  Then it reports OK with 0 failures

Scenario: the Python bundle is byte-identical          # Reject: mirror_drift
  Given canonical skill/ + tooling/ + docs/ + add.py
  When test_bundle_parity runs
  Then _bundled/ matches byte-for-byte with no test/junk files

Scenario: the Claude skill mirror is byte-identical    # Reject: mirror_drift
  Given canonical skill/add
  When test_tree_parity runs
  Then .claude/skills/add matches byte-for-byte

Scenario: the engine audit is clean                    # Reject: audit_dirty
  Given every .add task
  When `add.py audit` runs
  Then it reports clean with 0 findings

Scenario: the convention vocabulary is whole & closed  # Reject: vocab_offmidiom
  Given the v16 surface (skill/add + appendix-b)
  When the paired convention tags are censused
  Then exactly the frozen 5 appear (prompt, exit_gate, output_format, constraints, reject_codes)
  And no other paired tag is present
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

No new artifact contract — this task runs the existing guards. The "contract" is the green bar itself:

```
v16 GREEN-STATE BAR (all must hold simultaneously)
  full unittest suite ............ OK, 0 failed
  test_bundle_parity ............. OK (canonical == _bundled, no junk)
  test_tree_parity ............... OK (canonical == .claude/skills/add)
  add.py audit ................... clean
  5-tag census ................... prompt · exit_gate · output_format · constraints · reject_codes, and no 6th
```

Status: FROZEN @ v16 — approved by Tin Dang, 2026-06-06 (standing authorization for the autonomous v16 run)
<!-- Verification-only sweep; no shape to design. Least-sure flag: ⚠ none material — the bar is mechanical;
     either every guard is green or it is not. This build: all green. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the union of every existing guard (no new test authored — this task is the sweep that RUNS
them together). The guards that compose the bar already exist:
  - `test_xml_convention.py` (17 tests) — pilot + 7 phase guides + 10 engine docs + appendix-b.
  - `test_bundle_parity.py` (7) · `test_tree_parity.py` (1) — the 3-mirror backstop.
  - the full project suite (474 total).

Tests live in: `add-method/tooling/test_*.py` (reused). No RED step — this is an integration sweep over
already-green guards, not a new feature.
<!-- A green-state sweep has no red-for-the-right-reason author step: it asserts the COMPOSITION of guards
     that each already ran red→green in their own task. The honest check is that the union is green at once. -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): change NOTHING — a sweep that edits code is no longer a sweep. If a guard is
red, STOP and open a fix task (do not mutate to green).
Code lives in: nothing written — this task only runs the guards and records the result.
Constraints: read-only over the surface; no test/contract/doc edits.

What was run (evidence):
  - `python3 -m unittest discover -s add-method/tooling -p 'test_*.py'` → **Ran 474 tests, OK** (0 failed).
  - `test_bundle_parity` → **Ran 7, OK** (canonical == _bundled; no test/junk shipped).
  - `test_tree_parity` → **Ran 1, OK** (canonical == .claude/skills/add).
  - `add.py audit` → **clean (47 tasks checked)**.
  - 5-tag census over `skill/add` + `docs/appendix-b-prompts.md` (open+close counts):
    prompt 26 (13 blocks) · exit_gate 16 (8) · output_format 8 (4) · constraints 12 (6) · reject_codes 8 (4).
    All five frozen tags in active use; no 6th tag present.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — **474 passed / 0 failed** (whole suite via discover)
- [x] coverage did not decrease — no code touched; guards reused, all green
- [x] no test or contract was altered during build — this task wrote nothing; it ran the existing guards
- [x] concurrency / timing — N/A (static markdown surface; no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — read-only sweep; no edits, no deps
- [x] layering & dependencies follow CONVENTIONS — 3 mirrors byte-identical (bundle + tree parity green); the convention vocabulary is whole (all 5) and closed (no 6th)
- [x] auto-resolved (autonomy: auto, no residue) — the accountable run

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved on evidence — autonomy: auto, no residue (the autonomous v16 run) · date: 2026-06-06
Note: integration sweep — no code written; asserts the COMPOSITION of every v16 guard at once. Evidence:
full suite 474 green, test_bundle_parity 7 green, test_tree_parity 1 green, add.py audit clean (47), and a
5-tag census proving the convention is whole and closed. All v16 exit criteria observably met. Resolved
under Tin Dang's standing authorization for the autonomous v16 run.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the green-state bar (full suite + both parity guards + audit + census)
is the standing CI gate for any future edit to the prompt surface — it catches mirror drift and off-vocab
tags before a publish.
Spec delta for the next loop: v16 is complete — the XML convention is applied across the whole prompt
surface (skill files + published prompt library), 3 mirrors byte-identical, vocabulary whole and closed.
The version/release bump for these changes was deferred OUT of v16 scope (per the milestone) — it is the
natural next milestone when the team decides to ship the convention.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a multi-file convention needs a CENSUS guard, not just per-file subset checks: counting that
  all N expected tags appear (whole) AND no unexpected tag appears (closed) across the surface catches a tag
  that drifted off-vocabulary in a file the per-file table forgot to enumerate. (evidence: the 5-tag census this sweep; per-file tests only assert each listed file.)
- [ADD · folded] a milestone with several conversion tasks benefits from a dedicated green-state SWEEP task
  whose only job is to run the union of guards at once — per-task greens can each pass while a cross-file
  interaction is red. (evidence: this task; the composition was green, but it is the only run that proves it.)
