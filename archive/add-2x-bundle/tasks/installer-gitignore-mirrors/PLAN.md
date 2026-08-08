# TASK: Consumer .add/.gitignore ignores the 3 managed vendor trees

slug: installer-gitignore-mirrors · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/templates/gitignore.tmpl` — the canonical body seeded/appended into a CONSUMER project's `.add/.gitignore` by both installers; currently lists only 4 engine-transient patterns (`scope-snapshot.json`, `pre-archive-state.bak.json`, `pre-update-state.bak.json`, `.update-cache.json`) — no entry for any of the 3 managed vendor trees.
  - `add-method/tooling/add_engine/constants.py:_GITIGNORE_BODY` — a Python string constant, asserted BYTE-IDENTICAL to `gitignore.tmpl` by `test_gitignore_bak_seed.py::test_template_matches_constant` (single-source-of-truth pin, same class as ENGINE_MD5 — both must change together).
  - `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` — the bundled copy, currently byte-identical to the canonical template (confirmed via `diff`); refreshed by `scripts/prepare_bundle.py` (ENGINE-CHANGE CHECKLIST twin for templates).
  - `add-method/bin/cli.js:seedGitignore()` (~l.593) and `add-method/src/add_method/_installer.py:_seed_gitignore()` (~l.845) — the two installer twins that write `.add/.gitignore`: seed-if-missing (whole template body incl. comments) else append-if-absent each non-comment pattern LINE the template carries that the existing file lacks (additive-only, idempotent, never reorders/removes user lines). No code change needed here — behavior already generalizes to any new pattern line added to the template.
  - `add-method/bin/cli.js:MANAGED` (~l.724) — the 3 (soon 4, incl. `skill/add` which is NOT ignored — lives under `.claude/`, a different concern) managed trees dropped into a consumer project: `tooling` -> `.add/tooling` (required), `docs` -> `.add/docs` (required), `personas-teacher` -> `.add/personas-teacher` (in `OPTIONAL` set — a malformed/older package missing it does not abort install, so the gitignore entry must be safe to add even when the tree itself is absent — gitignore patterns for a non-existent path are inert, never an error).
  - `add-method/tooling/add.py:cmd_init` (~l.505-519) — writes `_GITIGNORE_BODY` to `.add/.gitignore` (NOT the project's own root `.gitignore`) only if that file doesn't already exist (never-clobber, mirrors SETUP_FILES idiom) — a THIRD call site sharing the same constant, no separate fix needed.
Context (working folder): `add-method/tooling/templates/gitignore.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` · `add-method/tooling/add_engine/constants.py` · `add-method/tooling/test_gitignore_bak_seed.py` (existing pin/parity suite to extend, not replace) · no change needed in `cli.js`/`_installer.py`/`add.py` themselves (their seed/append logic already generalizes to new template lines).
Honors (patterns / conventions): mirrors THIS repo's own just-shipped `untrack-add-tooling` task (dogfood `.add/tooling` untracked via `.add/.gitignore`'s `tooling/` entry) — applying the identical "vendored/regenerable tree, not project-authored, don't commit it" rationale to every CONSUMER project via the shared installer template, not just this self-hosting repo. Reuses the existing single-source-of-truth pin pattern (`gitignore.tmpl` == `_GITIGNORE_BODY`, already tested) rather than inventing a new one.
Anchors the contract cites: `gitignore.tmpl` (canonical body) · `_GITIGNORE_BODY` (constants.py) · the bundled template copy · `test_gitignore_bak_seed.py::test_template_matches_constant` (the parity pin to extend) · `MANAGED`/`OPTIONAL` (cli.js) as the source of truth for which 3 trees exist.
Issues/Risks (→ feed §1):
  - **the additive-append behavior is non-comment-line keyed** — `seedGitignore`/`_seed_gitignore` skip blank/comment lines when computing `missing` for an EXISTING `.add/.gitignore`; only the bare pattern lines (`.add/tooling/`, `.add/docs/`, `.add/personas-teacher/`) need to be new/absent for an existing consumer project to pick them up on next `update` — the explanatory comment above them is cosmetic for a fresh seed only, never itself load-bearing for the append path.
  - **`.add/personas-teacher/` is OPTIONAL at the tree level but MUST NOT be optional at the gitignore level** — even a consumer whose installed package predates the persona-teacher feature (tree absent) benefits from the ignore pattern being present (harmless no-op today, correct-by-default once they upgrade); the entry is unconditional, not gated on tree presence.
  - **scope discipline** — this task does NOT touch `.add/.gitignore` in THIS repo (AIDD-Book has no `.add/personas-teacher/` of its own — confirmed absent — and already gained a `tooling/` entry via `untrack-add-tooling`); it ONLY touches the installer-facing template + its 2 pinned twins + the existing parity test file.
Related intent: Tin's original request (2026-07-01, via `/add enhance`) — "add.gitignore to skip commit .add/tooling or persona_teacher, just push project artifacts like core documents" — the `.add/tooling` half was addressed for THIS repo by `untrack-add-tooling`; the `persona_teacher` half, and the CONSUMER-project-wide generalization, was confirmed in a follow-up AskUserQuestion ("Yes, add it as a new task") after discovering `.add/personas-teacher/` only exists in installed consumer projects, never in this dogfood repo.
Ground SHA: 16afe85

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: every consumer project's `.add/.gitignore` ignores all 3 installer-managed vendor trees (`.add/tooling/`, `.add/docs/`, `.add/personas-teacher/`), not just the 4 existing engine-transient artifact patterns — so a fresh `git add .` in a newly-installed ADD project pushes only the project's own core artifacts (PROJECT.md, tasks, milestones, state), never the regenerable/vendored copies the installer drops in.
Framings weighed: add the 3 patterns to the single-sourced `gitignore.tmpl` template (tried first — REVERTED, see v2 below) · **v2 chosen: split by where each pattern is allowed to live** — `.add/tooling/` + `.add/docs/` go in the shared `gitignore.tmpl`/`_GITIGNORE_BODY` (both engine-safe); `.add/personas-teacher/` is appended by the installer twins (`cli.js`/`_installer.py`) themselves, since putting it in `_GITIGNORE_BODY` (a file inside `add_engine/`) tripped the existing `test_bundle_teacher.py::test_engine_unchanged_and_handsoff` invariant — "the engine must not read the teacher on any path" — which blind-checks the ENTIRE engine source (`add.py` + `add_engine/*.py`) for the literal substring `"personas-teacher"`. Discovered mid-build (evidence: the substring appeared in `_GITIGNORE_BODY`, breaking that test) · special-case each installer twin to hard-code ALL 3 paths directly (rejected — duplicates data the template already single-sources for the 2 engine-safe patterns; only the 1 hands-off-conflicted pattern needs installer-twin duplication) · narrow/weaken `test_engine_unchanged_and_handsoff` instead (rejected — that test encodes a deliberate design principle from a prior milestone (persona-teacher-bundle); narrowing it to accommodate this task is a judgment call outside this task's scope, confirmed via AskUserQuestion: "Split it out") · make `.add/personas-teacher/`'s ignore entry conditional on the OPTIONAL tree being present (rejected — over-engineers a static gitignore pattern; an inert pattern for an absent path costs nothing, and gates the entry behind install-time detection for no benefit)
Must:
<must>
  - M1: `add-method/tooling/templates/gitignore.tmpl` gains 2 new pattern lines — `.add/tooling/`, `.add/docs/` — with a rationale comment explaining they are installer-managed, regenerable/vendored copies, not project-authored artifacts; the comment does NOT literally name the third managed tree (hands-off boundary).
  - M2: `add-method/tooling/add_engine/constants.py:_GITIGNORE_BODY` is updated to stay BYTE-IDENTICAL to `gitignore.tmpl` (existing pin, `test_template_matches_constant`) — same 2 patterns, same hands-off-safe comment.
  - M3: `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` (the bundled copy) is refreshed to match, via `scripts/prepare_bundle.py` (the existing bundle-refresh mechanism) — confirmed byte-identical to the canonical template afterward.
  - M4: `test_gitignore_bak_seed.py` gains new assertions: (a) a fresh `add.py init` (direct engine path) writes a `.add/.gitignore` containing the 2 engine-safe patterns and explicitly NOT `.add/personas-teacher/`; (b) `_installer._seed_gitignore` and cli.js's `seedGitignore` (both installer twins) seed/append ALL 3 patterns (the 2 template ones + the installer-only extra), preserving any pre-existing user-added line; (c) a new test confirms `gitignore.tmpl`/`_GITIGNORE_BODY` never contain the substring `"personas-teacher"` (belt-and-suspenders alongside the pre-existing `test_engine_unchanged_and_handsoff`).
  - M5 (v2): `cli.js`'s `seedGitignore()` and `_installer.py`'s `_seed_gitignore()` EACH gain one small addition — a new `INSTALLER_MANAGED_IGNORE_EXTRA` / `_INSTALLER_MANAGED_IGNORE_EXTRA` constant (kept OUTSIDE `add_engine/constants.py`, so the hands-off scan never sees it) holding `.add/personas-teacher/`, concatenated onto the template body before the existing seed-if-missing / append-if-absent logic runs (that logic itself is UNCHANGED — it already generalizes to whatever the combined body contains).
</must>
Reject:
<reject>
  - the 2 engine-safe patterns are added to only ONE of {gitignore.tmpl, _GITIGNORE_BODY, the bundled copy} -> "gitignore_source_drift"
  - an EXISTING consumer project's `.add/.gitignore` loses a user-added custom line when the append runs -> "gitignore_append_destructive"
  - the `.add/personas-teacher/` pattern is written conditionally (e.g. only if the tree exists at seed time) -> "gitignore_entry_conditional"
  - this task edits THIS repo's own root `.gitignore` or `.add/.gitignore` (out of scope — already handled by `untrack-add-tooling`; this repo has no `.add/personas-teacher/` of its own) -> "scope_creep_dogfood_gitignore"
  - `add_engine/constants.py` (or `add.py` itself) contains the literal substring `"personas-teacher"` anywhere, including in a comment -> "engine_handsoff_violated" (v2)
</reject>
After:
<after>
  - a fresh npm/pip install (via cli.js/_installer.py) produces a `.add/.gitignore` that ignores all 3 managed vendor trees from day one; a fresh DIRECT `add.py init` (bypassing the installer) ignores the 2 engine-safe trees only, by design; an EXISTING consumer project's `.add/.gitignore` gains whatever patterns it's missing on its next `update` run (via the installer twins), additively, without disturbing any existing line; `gitignore.tmpl`, `_GITIGNORE_BODY`, and the bundled template copy remain byte-identical to each other AND free of the substring `"personas-teacher"`; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ (v2) concatenating `INSTALLER_MANAGED_IGNORE_EXTRA` onto the template body BEFORE the existing seed-if-missing/append-if-absent logic runs is sufficient — i.e. that logic's line-splitting/diffing genuinely doesn't care WHERE a line came from, only that it's present in the combined `body` string. Lowest confidence because this is a NEW code path (the two installer twins each gained real logic, not just data, reversing M5's original "no code change" premise). If wrong: the extra line could silently fail to seed/append in one twin but not the other. Mitigate: M4(b)'s tests exercise BOTH twins directly (Python via `_installer._seed_gitignore`, JS via a real `node cli.js init` subprocess) against the REAL combined body, not a mock.
  - [ ] gitignore glob semantics: a directory-suffixed pattern like `.add/tooling/` correctly ignores the whole subtree the same way `.add/docs/` already does today (confirmed: `.add/docs/` is the proven precedent, already gitignored this exact way in THIS repo's own root `.gitignore` and working as intended).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: direct engine init ignores the 2 engine-safe trees only   # M1, M4(a)
  Given a brand-new directory with no .add/ yet
  When `add.py init` runs (the DIRECT engine path, not via an installer)
  Then `.add/.gitignore` contains `.add/tooling/` and `.add/docs/`
  And it does NOT contain `.add/personas-teacher/`
  And it still contains the 4 pre-existing engine-transient patterns

Scenario: an installer (fresh or existing project) seeds/appends all 3 patterns   # M4(b), M5, R:gitignore_append_destructive
  Given a target project (fresh, or existing with a user-added custom line and none of the 3 patterns)
  When the installer seed/append routine runs (`_installer._seed_gitignore`, or a real `node cli.js init`)
  Then `.add/.gitignore` contains all 3 patterns — `.add/tooling/`, `.add/docs/`, `.add/personas-teacher/`
  And any pre-existing user-added line is still present, unreordered, unremoved

Scenario: the personas-teacher entry is unconditional   # M5, R:gitignore_entry_conditional
  Given a consumer project whose installed package predates persona-teacher (no `.add/personas-teacher/` tree exists on disk)
  When an installer twin seeds or appends `.add/.gitignore`
  Then it still contains the `.add/personas-teacher/` pattern
  And no error or warning is raised because the path doesn't exist

Scenario: the engine stays hands-off — the 2 sources never name the teacher tree   # M1, M2, M3, R:gitignore_source_drift, R:engine_handsoff_violated
  Given `gitignore.tmpl`, `_GITIGNORE_BODY`, and the bundled template copy all changed together (2 patterns each)
  When `test_template_matches_constant`, a canonical/bundled diff check, and a substring check for "personas-teacher" all run
  Then the first two are byte-identical to each other and to the bundled copy
  And none of the three contains the substring "personas-teacher" anywhere, including comments
  And `test_bundle_teacher.py::test_engine_unchanged_and_handsoff` still passes unmodified

Scenario: this repo's own gitignore is untouched   # R:scope_creep_dogfood_gitignore
  Given AIDD-Book's own root `.gitignore` and `.add/.gitignore` already reflect the `untrack-add-tooling` shape
  When this task's build completes
  Then neither file changed as a side effect of this task
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
installer-gitignore-mirrors — frozen shape @ v2 (change request — split it out)

Discovery that forced the split: adding .add/personas-teacher/ to the shared
_GITIGNORE_BODY (add_engine/constants.py) broke the pre-existing engine hands-off
invariant test_bundle_teacher.py::test_engine_unchanged_and_handsoff — the engine
must never contain the literal substrings "personas-teacher" / "update_teacher" on
ANY path. Resolution: keep the 2 engine-safe managed trees in the shared template/
constant; add the teacher-tree pattern ONLY inside the two installer twins, each via
its own small, separately-named constant — never inside add_engine/*.py.

add-method/tooling/templates/gitignore.tmpl — APPEND after the existing 4 lines:

    # ADD-managed vendor trees: regenerable/vendored copies the installer drops in,
    # never project-authored — mirrors the .add/docs/ rationale above, generalized
    # to every consumer project (not just this repo). (one further managed tree is
    # NOT listed here — the engine's own _GITIGNORE_BODY constant must stay hands-
    # off of it by name; the installer twins seed that one pattern themselves.)
    .add/tooling/
    .add/docs/

  (exactly 2 patterns; the comment must not spell the teacher-tree name anywhere —
  a literal mention there trips the same hands-off test as putting it in the body.)

add-method/tooling/add_engine/constants.py — _GITIGNORE_BODY gains the IDENTICAL
append (byte-for-byte match with gitignore.tmpl, per test_template_matches_constant).

add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl — refreshed to
match the canonical template (via scripts/prepare_bundle.py) — byte-identical after.

add-method/src/add_method/_installer.py — a new module-level constant, defined
OUTSIDE add_engine/*.py on purpose:

    _INSTALLER_MANAGED_IGNORE_EXTRA = (".add/personas-teacher/",)

  `_seed_gitignore` reads the template body, then concatenates the extra pattern(s)
  onto `body` BEFORE the existing seed-if-missing / append-if-absent logic runs —
  that logic is otherwise unchanged and generically picks up the extra line since it
  only ever operates on the combined `body` string.

add-method/bin/cli.js — the JS twin, same shape:

    const INSTALLER_MANAGED_IGNORE_EXTRA = [".add/personas-teacher/"];

  `seedGitignore` reads the template body into a `let body` (was `const`), appends
  `INSTALLER_MANAGED_IGNORE_EXTRA.join("\n") + "\n"` before the existing seed/append
  logic, unchanged otherwise.

test_gitignore_bak_seed.py — test methods (final names, all green):
  - test_init_gitignore_lists_managed_trees: direct `add.py init` -> .add/.gitignore
    contains ONLY the 2 engine-safe patterns + the 4 prior ones; asserts
    .add/personas-teacher/ is ABSENT (engine hands-off boundary)
  - test_engine_gitignore_body_excludes_personas_teacher: neither gitignore.tmpl nor
    add._GITIGNORE_BODY contain the substring "personas-teacher" (belt-and-suspenders
    alongside test_bundle_teacher.py::test_engine_unchanged_and_handsoff)
  - test_bundled_template_matches_canonical: bundled copy byte-identical to canonical
  - test_seed_appends_managed_trees_preserves_custom_lines (pip twin, real template):
    _installer._seed_gitignore -> gains ALL 3 patterns (2 engine + 1 installer-extra),
    custom user line preserved
  - test_personas_teacher_entry_unconditional_even_when_absent (pip twin): pattern
    present even when .add/personas-teacher/ doesn't exist on disk at seed time
  - test_cli_js_seed_lists_managed_trees_on_init (npm twin, real `node cli.js init`
    subprocess): all 3 patterns present after a fresh init

Invariants: add.py:cmd_init receives NO code change (still reads the engine's own
_GITIGNORE_BODY, unmodified in shape beyond the 2 patterns); the append path stays
additive-only, never reorders/removes an existing line; test_engine_unchanged_and_
handsoff passes UNMODIFIED (proves the split actually holds the hands-off boundary);
THIS repo's own root .gitignore and .add/.gitignore are untouched (already correct
via untrack-add-tooling); full suite green; ENGINE_PKG_MD5 -> 1c8d608f3d9665590865eeb3c382abca.
```

Least-sure flag surfaced at freeze: [contract] (v2) whether concatenating
`_INSTALLER_MANAGED_IGNORE_EXTRA`/`INSTALLER_MANAGED_IGNORE_EXTRA` onto `body` BEFORE
the existing seed-if-missing/append-if-absent logic is sufficient, vs. needing a
dedicated third code path — cost if wrong: the extra line could theoretically dedupe
oddly against a future custom user line that happens to match it; mitigated by M4(b)'s
direct-function test (`test_seed_appends_managed_trees_preserves_custom_lines`) and the
real-subprocess npm twin test both exercising the ACTUAL concatenation + append logic,
not a mock — so the functional risk is low, this is a wording/design-fit flag only.

Status: FROZEN @ v2 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_gitignore_lists_managed_trees: direct `add.py init` -> .add/.gitignore contains ONLY .add/tooling/, .add/docs/ + the 4 prior patterns; .add/personas-teacher/ ABSENT (engine hands-off boundary)
  - test_engine_gitignore_body_excludes_personas_teacher: gitignore.tmpl and add._GITIGNORE_BODY never contain the substring "personas-teacher" (belt-and-suspenders alongside test_bundle_teacher.py::test_engine_unchanged_and_handsoff)
  - test_bundled_template_matches_canonical: bundled gitignore.tmpl copy byte-identical to canonical
  - test_seed_appends_managed_trees_preserves_custom_lines: existing .add/.gitignore with a custom line + none of the 3 patterns, run through `_installer._seed_gitignore` (real template) -> gains ALL 3 patterns (2 engine + 1 installer-extra), custom line untouched, unreordered
  - test_personas_teacher_entry_unconditional_even_when_absent: pip-twin seed/append runs with no .add/personas-teacher/ tree on disk -> pattern still present, no error/warning
  - test_cli_js_seed_lists_managed_trees_on_init: cli.js's seedGitignore exercised via a real `node cli.js init` subprocess -> all 3 patterns present after a fresh init
</test_plan>

Tests live in: `add-method/tooling/test_gitignore_bak_seed.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/gitignore.tmpl` `add-method/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` `add-method/src/add_method/_installer.py` `add-method/bin/cli.js` `add-method/tooling/test_gitignore_bak_seed.py`
Strategy (ordered batches): 1. append the 2 engine-safe pattern lines + hands-off-safe rationale comment to `gitignore.tmpl`. 2. mirror the identical append into `_GITIGNORE_BODY` in `constants.py`. 3. refresh the bundled template copy via `prepare_bundle.py` and confirm byte-identity. 4. add `_INSTALLER_MANAGED_IGNORE_EXTRA` to `_installer.py` and concatenate it onto `body` inside `_seed_gitignore`, before the existing seed/append logic. 5. add the `INSTALLER_MANAGED_IGNORE_EXTRA` twin to `cli.js`'s `seedGitignore`, same concatenation. 6. extend `test_gitignore_bak_seed.py` with the 6 assertions (direct-init 2-pattern-only + personas-teacher absent, substring-exclusion, bundled parity, pip-twin 3-pattern append, personas-teacher unconditional, npm-twin subprocess). 7. full suite green + confirm THIS repo's own `.gitignore`/`.add/.gitignore` are untouched + `test_engine_unchanged_and_handsoff` still passes unmodified + re-pin `ENGINE_PKG_MD5`.

Persona (optional): absent — generic
Known-problem fixes: a comment mentioning the teacher tree by name trips the same hands-off substring check as putting the pattern in the body → reworded the gitignore.tmpl/_GITIGNORE_BODY comment to describe the excluded tree without naming it.
Strategy actually used: as planned, with one extra loop — the first split attempt (2-pattern body + a comment that still said "personas-teacher") failed `test_engine_unchanged_and_handsoff` and the new substring test; reworded the comment to avoid the literal name, re-ran `prepare_bundle.py`, re-computed `ENGINE_PKG_MD5` a second time (final: `1c8d608f3d9665590865eeb3c382abca`).
Safety rule (feature-specific): the installer-twin concatenation (`body +=`) runs BEFORE the existing seed-if-missing/append-if-absent logic, never replacing or reordering it — additive-only guarantee preserved for the new pattern the same as for the 2 template-sourced ones.
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `python3 -m unittest discover -s tooling -p 'test_*.py'` -> Ran 2570 tests, OK
- [x] coverage did not decrease — 6 new tests added to `test_gitignore_bak_seed.py`, none removed
- [x] no test or contract was altered during build — `git diff HEAD -- add-method/tooling/test_bundle_teacher.py` is empty (the pre-existing hands-off test was never touched)
- [x] the green was EARNED, not gamed — adversarial refute-read by subagent, verdict EARNED (see below)
- [x] concurrency / timing of the risky operation is safe — pure string/file-append logic, no shared/concurrent state
- [x] no exposed secrets, injection openings, or unexpected dependencies — data-only gitignore pattern strings; no new external dependency
- [x] layering & dependencies follow CONVENTIONS.md — installer-only logic stays in the installer twins, never leaks into add_engine/*.py (the very invariant this task had to protect)
- [x] a person reviewed and approved the change — Tin Dang approved freeze @ v2 via AskUserQuestion

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] a direct `add.py init` (bypassing the installer) writes `.add/.gitignore` with `.add/tooling/` + `.add/docs/` and explicitly WITHOUT `.add/personas-teacher/` — confirmed by `test_init_gitignore_lists_managed_trees`, real assertion (would go red if the split leaked)
- [x] both installer twins (pip + npm) seed/append all 3 patterns from a real run, preserving any pre-existing custom line — confirmed by `test_seed_appends_managed_trees_preserves_custom_lines` (real `_installer._seed_gitignore` against the real template) and `test_cli_js_seed_lists_managed_trees_on_init` (real `node cli.js init` subprocess, node v25.8.1 present so it actually ran, did not skip)
- [x] the engine stays hands-off of the teacher tree by name, on every path — confirmed by `test_engine_gitignore_body_excludes_personas_teacher` (direct substring check on gitignore.tmpl + `_GITIGNORE_BODY`) AND `test_bundle_teacher.py::test_engine_unchanged_and_handsoff` passing UNMODIFIED (git diff empty)
- [x] `gitignore.tmpl` == `_GITIGNORE_BODY` == bundled copy, byte-identical — confirmed by `test_template_matches_constant` + `test_bundled_template_matches_canonical`, and a `diff` on the bundled pair reporting "Files are identical"

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_INSTALLER_MANAGED_IGNORE_EXTRA` (Python) and `INSTALLER_MANAGED_IGNORE_EXTRA` (JS) are each referenced exactly once, inside their own `_seed_gitignore`/`seedGitignore`, confirmed structurally parallel (read side-by-side by the subagent: same read-template → ensure-trailing-newline → concatenate-extra → existing seed/append order in both languages)
- [x] DEAD-CODE (code) — no orphaned symbol; both new constants are consumed immediately at their definition site
- [x] SEMANTIC (prose) — `gitignore.tmpl`/`_GITIGNORE_BODY`'s rationale comment read in full by the subagent: confirmed it describes the excluded tree without naming it, so the comment itself can't re-trip the hands-off check

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: agent-id aa05e305dc88b8750 · adversarially checked: (1) whether any test could pass with the feature broken — found `test_init_gitignore_lists_managed_trees` would go red if the split leaked; (2) whether `test_bundle_teacher.py` was weakened to make the split pass — confirmed `git diff` empty, untouched; (3) whether the npm-twin test silently skips (masking JS coverage) — node was present, it actually ran; (4) whether `ENGINE_PKG_MD5`/`ENGINE_MD5` pins match the LIVE computed digests, not stale — both matched exactly (`1c8d608f3d9665590865eeb3c382abca` / `e23cd35ebc910a2b9e7f067b9a3a4f4b`); (5) whether the substring check could be circumvented via an indirect (f-string/docstring) construction — read the live file content verbatim, confirmed a plain literal absence. One non-blocking observation surfaced: on a CI runner without `node` installed, the npm-twin test would silently skip rather than fail, which is a pre-existing pattern (not introduced by this task) — noted as a latent CI-environment risk, not a defect of this build.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent-id aa05e305dc88b8750 (same refute-read pass doubled as the 3-lens review; findings below drawn from its report)
1. Security: CLEAR — data-only gitignore pattern strings, no secrets, no injection surface, no new dependency
2. Concurrency: CLEAR — no shared/concurrent state; file writes are single-threaded CLI-invocation-scoped, same as the pre-existing seed/append logic
3. Architecture: CLEAR — the split keeps installer-only knowledge (the teacher-tree pattern) strictly inside the installer twins, never inside `add_engine/*.py`; this is the exact invariant (`test_engine_unchanged_and_handsoff`) the task was designed to protect, and it was verified to still hold unmodified
Verdict: PASS
Residue: none material — the node-absent-skip observation above is a pre-existing test-infra characteristic, not new residue from this task
Binding: yes — mechanical (installer/CI-adjacent data+logic change, no security or behavioral ambiguity)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with one extra loop — the first split attempt (2-pattern body + a comment that still said "personas-teacher") failed `test_engine_unchanged_and_handsoff` and the new substring test; reworded the comment to avoid the literal name, re-ran `prepare_bundle.py`, re-computed `ENGINE_PKG_MD5` a second time (final: `1c8d608f3d9665590865eeb3c382abca`).
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

