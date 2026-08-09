# PLAN: Retire fold-stale instructions from the scaffold templates

slug: fold-residue-templates · created: 2026-07-24 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the scaffold templates stop teaching instructions the engine retired — a milestone flag that errors, a phase vocabulary that no longer exists, and a bundle enumeration that disagrees with the engine's own.
Framings weighed: guard the CLASS, not the three strings (chosen — the scenarios fold shipped a dead link and two dead instructions precisely because each sweep fixed instances by hand with nothing left behind to object; a check that resolves every template-cited flag against argparse makes the whole class impossible) · hand-edit the three lines (rejected — leaves the next retirement free to reintroduce the same defect)
Must:
<must>
  - M1 no scaffold template advertises a CLI flag the engine's argparse rejects
  - M2 no scaffold template names a phase outside the engine's PHASES as if it were live
  - M3 PLAN.md.tmpl's Direction-bundle enumeration lists the same items the engine's own scaffold string lists
  - M4 all four template trees remain byte-identical to each other
</must>
Reject:
<reject>
  - a template citing a long flag no verb accepts -> "dead_flag"
  - a template describing a retired phase as a live step -> "retired_phase_vocab"
</reject>
After:
<after>
  - every long flag written in a template resolves to a real option on a real verb
  - GLOSSARY defines ground in terms of the shipped flow, not a phase-0 that was folded away
</after>
Boundary: template flag tokens come in TWO shapes the checks must tell apart — ADD CLI flags (`--tiny`, `--cross`) and CSS custom properties in the UDD sample files (`--semantic-color-text`); only the former are engine flags.
<assumptions>
  ⚠ argparse `--help` per verb is a COMPLETE list of accepted flags — if a verb accepts an undocumented/suppressed flag, the check would wrongly call a legitimate citation dead; mitigated because the check only ever flags a template string, never blocks the engine
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
Three prose fixes, applied identically to ALL FOUR template trees (they are
byte-identical today and must stay so):
    add-method/tooling/templates/                     (source of truth)
    .add/tooling/templates/                           (this project's copy)
    add-method/.add/tooling/templates/                (dogfood copy)
    add-method/src/add_method/_bundled/tooling/templates/   (PyPI bundle)

MILESTONE.md.tmpl  — the Strategy heading's parenthetical
  "drafted-blank for a micro/--fast milestone"
    -> "drafted-blank for a micro/--tiny milestone"
  WHY: `new-milestone --fast` exits with "unrecognized arguments: --fast";
       --tiny is the real flag. This line reaches EVERY scaffolded MILESTONE.md.

GLOSSARY.md.tmpl   — the `ground:` definition
  "the phase-0 preamble before specify"
    -> wording that describes grounding as part of the DIRECTION phase
  WHY: PHASES = (direction, build, verify, done). Neither "phase-0" nor a
       "specify" phase exists; add.py:264 records §0 "moved from a standalone
       §0 into the plan phase".

PLAN.md.tmpl       — the line-6 phase-marker comment
  "(rules · scenarios · change plan · red suite)"   [4 items]
    -> "(rules · change plan · red suite)"          [3 items, matches add.py:944]
  WHY: cosmetic only — new-task OVERWRITES line 6 from add.py, so this text
       never reaches a user file. Fixed for maintainer accuracy, NOT user impact.

Guard shipped with the fix (new, in the engine test suite):
  every long flag appearing in a template resolves to a real argparse option on
  a real verb; CSS custom properties (--primitive-*/--semantic-*) are excluded.
```

Grounding anchors (verified in-context): MILESTONE.md.tmpl:43 · GLOSSARY.md.tmpl:32 · PLAN.md.tmpl:6 · add.py:944 (the engine's own 3-item string) · add.py:264 (§0 fold note) · add_engine/constants.py PHASES · `new-milestone --help` shows --tiny and no --fast · `diff -r` proves the four trees identical.

NOT in scope: add_engine/constants.py:85's PHASE_GUIDE["direction"] "§2 one scenario per rule" — the HIGHEST-impact residual, but it sits inside ENGINE_PKG_MD5's digest (add_engine/*.py) and needs a pin repin. Split into its own task deliberately.

Target (measurable): dead template flags 1 -> 0 · retired-phase phrases in templates 1 -> 0 · template trees byte-identical 4/4 (unchanged) · 4 new checks red before, green after · engine suite `add.py check` stays 253 passed / 0 failed.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/templates/` `.add/tooling/templates/` `add-method/.add/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/tooling/test_template_flag_vocabulary.py` `./tests/`
Regression floor: `add.py check` (253 passed / 0 failed) plus `add-method/tooling/test_scenarios_folded.py` — the fold's own guard — must stay green.
Persona (optional): `.add/personas/book-technical-writer.md` — every string here ships into a user's scaffolded project.

Strategy (preferred, not hard): write the guard as a permanent test in the ENGINE suite (test_template_flag_vocabulary.py) rather than only as a task-local check, so the class stays closed after this task archives; run red, apply the three edits to the source-of-truth tree, mirror to the other three, re-run green + confirm byte-identity.

Least-sure flag surfaced at freeze: [test] the flag-vocabulary check's ability to separate ADD CLI flags from CSS custom properties. It excludes `--primitive-*`/`--semantic-*`, which is a PREFIX rule, not a proof: a future sample file using some other custom-property prefix would trip a false "dead_flag". Accepted because the failure mode is a noisy test on a template string — never a blocked build or a weakened gate — and the check names the offending token so a false positive is obvious on sight.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_no_dead_cli_flag: every long flag in a template resolves to a real argparse option on a real verb · covers: M1, R:dead_flag
  - test_no_retired_phase_vocabulary: no template names a phase outside PHASES as a live step · covers: M2, R:retired_phase_vocab
  - test_bundle_enumeration_matches_engine: PLAN.md.tmpl's line-6 item list equals the engine's own · covers: M3
  - test_template_trees_identical: all four template trees are byte-identical · covers: M4
</test_plan>

Kind: method/docs — these assert on SHIPPED TEMPLATE TEXT, so they are executable checks over files, not behavioral unit tests. Each must run RED against the templates as they stand.

Note on M4: test_template_trees_identical is expected to be GREEN from the start — it is a REGRESSION guard, not a red-first case. It exists so the three edits cannot land in one tree and miss the others, which is the exact twin-drift failure this repo has hit before. Its red-first duty is discharged by mutation instead: drop the edit from one tree and it must fail.

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned for the three edits + twin mirroring, but the guard needed a RE-CROSS mid-build. The first `_verbs()` helper scraped `add.py --help` for argparse's `{verb,...}` list; add.py prints a HAND-WRITTEN help with no such list and intercepts unknown verbs with its own message, so M1 was failing inside the helper — red, but for the wrong reason, never actually detecting `--fast`. Disclosed rather than quietly patched; `re-cross --by "Tin Dang"` (human-approved, as that verb requires) returned the task to direction. The helper was rebuilt to IMPORT `add.build_parser()` (add.py:6927) and walk the real `_SubParsersAction` option objects — authoritative, cannot drift from the CLI, and removes ~34 subprocess calls. M1 was then proven red on the real defect (`MILESTONE.md.tmpl:43 cites --fast`) before the fix was restored.
Code lives in: `src/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — guard 4/4 under pytest AND under `unittest` (the runner CI actually uses); regression floor test_scenarios_folded.py 9/9; the prior task's 5 acceptance checks still 5/5
- [x] coverage did not decrease — 4 checks added, none removed
- [~] no test or contract was altered during build — the CONTRACT was untouched; the TEST was altered, disclosed and human-approved via `re-cross --by "Tin Dang"`, which is the method's sanctioned path for exactly this. Not a silent edit.
- [x] the green was EARNED, not gamed — M1 proven red on the real defect string before the fix was restored; M2/M3 red-first from the outset; M4 is a declared regression guard, green by design
- [x] concurrency / timing — n/a, prose templates + a read-only test
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency; the guard imports add.py in-process rather than shelling out, which REDUCES subprocess surface
- [x] layering & dependencies — guard lives in the engine suite (`tooling/test_*.py`), matching CI's `unittest discover -s tooling` pattern, so it protects every future change
- [x] a person reviewed and approved the change — Tin Dang approved the freeze AND the re-cross

TARGET — recorded honestly, one clause was mis-specified:
  · dead template flags 1 -> 0 ✓
  · retired-phase phrases 1 -> 0 ✓
  · template trees byte-identical 4/4 ✓ (re-verified after mirroring)
  · 4 checks red-before/green-after ✓ (M4 by design green; its red-first duty discharged by mutation)
  · "engine suite `add.py check` stays 253 passed / 0 failed" — MIS-SPECIFIED. `add.py check` is the
    engine's STATE consistency check and does not run pytest at all; the two were conflated when the
    contract was drafted. Actual: check = 256 passed / 0 failed (the count moved because this task
    added task artifacts, NOT because of the new tests). The 0-failed intent is met; the test-suite
    evidence is the pytest/unittest runs above. Recorded rather than quietly reinterpreted.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) the strongest doubt was M1 itself — it passed while never testing anything, which is the textbook vacuous green; caught by reading the FAILURE REASON rather than the pass/fail count, then proven by restoring the defect and confirming the check names `MILESTONE.md.tmpl:43 cites --fast`; (2) guard durability — confirmed CI runs `unittest discover -s tooling -p 'test_*.py'` (ci.yml:53, publish.yml:85) and that the file passes under unittest, so the class stays closed after this task archives rather than only while I am watching; (3) twin parity re-checked AFTER the final edit, since the mid-build sed touched only the source tree.

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose guard the CLASS, not the three strings; rejected hand-edit the three lines (rejected — leaves the next retirement free to reintroduce the same defect)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned for the three edits + twin mirroring, but the guard needed a RE-CROSS mid-build. The first `_verbs()` helper scraped `add.py --help` for argparse's `{verb,...}` list; add.py prints a HAND-WRITTEN help with no such list and intercepts unknown verbs with its own message, so M1 was failing inside the helper — red, but for the wrong reason, never actually detecting `--fast`. Disclosed rather than quietly patched; `re-cross --by "Tin Dang"` (human-approved, as that verb requires) returned the task to direction. The helper was rebuilt to IMPORT `add.build_parser()` (add.py:6927) and walk the real `_SubParsersAction` option objects — authoritative, cannot drift from the CLI, and removes ~34 subprocess calls. M1 was then proven red on the real defect (`MILESTONE.md.tmpl:43 cites --fast`) before the fix was restored.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] add_engine/constants.py:85 PHASE_GUIDE["direction"] still instructs "§2 one scenario per rule" — the highest-impact fold residual, printed by `add.py guide` to every user in the direction phase on every install; deliberately split out because it sits inside ENGINE_PKG_MD5's digest and needs a pin repin (evidence: reproduced in a scratch project 2026-07-24; all 4 engine twins stale; no live test pins the string)
- [SPEC · open] a template-flag guard now exists but there is no equivalent guard over the ENGINE's own user-facing instruction strings — the §2 residual above would not be caught by anything (evidence: it survived the fold, a milestone close, and a release cut)

### Competency deltas
- [TDD · open] a red test is only evidence if you read WHY it is red — M1 was red twice for a helper bug and would have shipped as a guard that guards nothing; the pass/fail count said "working", the failure text said otherwise (evidence: `AssertionError: could not parse the verb list` where the expected failure was `cites --fast`)
- [TDD · open] prefer importing a program's real parser over scraping its `--help` — add.py prints hand-written help and intercepts unknown verbs, so every scrape strategy failed; `build_parser()` was authoritative, cannot drift from the CLI, and removed ~34 subprocess calls (evidence: three failed scrape attempts before the import approach worked first try)
- [ADD · open] when a mid-build test defect appears, `re-cross --by` is the honest path and it is cheap — one call, audited, human-approved, tripwire and scope re-snapshotted; quietly patching the test would have inverted the method for no saved time (evidence: re-cross took one command and the task still closed in the same session)
- [SDD · open] a Target clause can be wrong in a FROZEN contract — "add.py check stays 253 passed" conflated the state-consistency verb with the pytest suite; the right move at verify is to record the mis-specification plainly, not to reinterpret the clause into something the evidence happens to satisfy (evidence: check does not run pytest at all; 253→256 came from new task artifacts)
