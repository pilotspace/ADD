# TASK: Fix nested .add/.gitignore vendor-tree patterns to resolve relative to .add/, not repo root

slug: gitignore-vendor-path-fix · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/templates/gitignore.tmpl` — canonical seed body (plain text, 14 lines); lines 13-14 are the buggy `.add/tooling/` / `.add/docs/` patterns
  - `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` — npm/pip-bundled mirror, confirmed byte-identical to canonical (`diff` clean)
  - `.add/tooling/templates/gitignore.tmpl` — dogfood mirror (untracked), confirmed byte-identical
  - `add-method/tooling/add_engine/constants.py:_GITIGNORE_BODY` (~l.114-127) — Python triple-quoted twin of the .tmpl, must stay byte-identical (`test_gitignore_bak_seed.py::test_template_matches_constant`)
  - `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` — bundled mirror of the above, confirmed byte-identical
  - `.add/tooling/add_engine/constants.py` — dogfood mirror, confirmed byte-identical
  - `add-method/src/add_method/_installer.py:850 _INSTALLER_MANAGED_IGNORE_EXTRA = (".add/personas-teacher/",)` — pip installer's extra line (kept OUT of the engine constant on purpose — engine must stay hands-off the teacher-tree name)
  - `add-method/bin/cli.js:593 const INSTALLER_MANAGED_IGNORE_EXTRA = [".add/personas-teacher/"];` — npm twin of the line above
  - `add-method/tooling/test_gitignore_bak_seed.py:44-45,83,179` — `ENGINE_MANAGED_TREE_PATTERNS`/`ALL_MANAGED_TREE_PATTERNS` module constants + 2 assertions currently encode the BUGGY `.add/`-prefixed strings as the expected seeded content — these must be corrected alongside the fix (not "weakening a test": the assertion itself embeds the bug, same shape as the `fresh-checkout-skip-tolerance` precedent this session)
  - `add-method/tooling/engine_pin.py:14 ENGINE_PKG_MD5` — must be re-pinned after `add_engine/constants.py` changes (confirmed below)
  - `add-method/tooling/engine_manifest.py:package_files()` (l.16-19) — globs `add_engine/*.py` (sorted by filename) → `constants.py` is IN this glob, so editing it changes `package_digest()`'s output and requires the `ENGINE_PKG_MD5` re-pin; `ENGINE_MD5` (covers `add.py` only) is untouched by this task
Context (working folder): `/Users/tindang/workspaces/tind-repo/add-sample-project` — a real (non-scratchpad) sample project created this session specifically to manual-test the installer before merge; still holds the OLD buggy installer output (361 files under `.add/tooling/`, `.add/docs/`, `.add/personas-teacher/` sitting untracked) — will be re-verified against the fix once built. `/tmp/giprobe` — a throwaway isolated git repo that conclusively proved the mechanism (see Issues/Risks).
Honors (patterns / conventions): 3-tree parity (canonical · bundled · dogfood-mirror must stay byte-identical, enforced by existing tests); single-sourced body (`_GITIGNORE_BODY` == `gitignore.tmpl`, `test_template_matches_constant`); the engine-hands-off-personas-teacher-by-name boundary (`test_engine_unchanged_and_handsoff`) — the installer twins seed that pattern themselves, never the shared constant.
Anchors the contract cites: `_GITIGNORE_BODY`, `_INSTALLER_MANAGED_IGNORE_EXTRA` / `INSTALLER_MANAGED_IGNORE_EXTRA`, `ENGINE_MANAGED_TREE_PATTERNS` / `ALL_MANAGED_TREE_PATTERNS`, `_seed_gitignore()` (`_installer.py`) / `seedGitignore()` (`cli.js`), `package_files()` / `package_digest()` (`engine_manifest.py`), `ENGINE_PKG_MD5` (`engine_pin.py`).
Issues/Risks (→ feed §1): **THE BUG** — `.add/.gitignore` is written INSIDE `.add/` (`_seed_gitignore` writes to `target_path / ".add" / ".gitignore"`); git resolves a nested `.gitignore`'s patterns relative to ITS OWN directory, not repo root. The current patterns `.add/tooling/`, `.add/docs/`, `.add/personas-teacher/` therefore tell git to look for the non-existent `.add/.add/tooling/` — they never match anything. Confirmed 3 independent ways: (1) real installer run against the sample project above — `git status --porcelain -uall` showed ~360 files under the 3 managed trees as untracked; (2) `git check-ignore -v` returned nothing (exit 1) for those paths; (3) an isolated `/tmp/giprobe` repro proved a bare `tooling/` pattern matches inside a nested `sub/.gitignore` while `.add/tooling/` does not. Cross-checked against this repo's own hand-maintained (untracked) `.add/.gitignore`, which correctly uses the bare `tooling/` form. `git diff main..HEAD -- add-method/tooling/templates/gitignore.tmpl` confirms the buggy lines are NEW to this branch (didn't exist on main before `installer-gitignore-mirrors`). Secondary risk: `test_gitignore_bak_seed.py`'s own pattern constants encode the same bug, so fixing the seed body alone would make that file's existing assertions fail — they must be corrected in the same build, and are explicitly IN scope (not an untouched frozen contract — this file is not this task's contract, it is pre-existing test infrastructure whose fixture data is provably wrong).
Related intent: this repairs a regression introduced by the already-closed `installer-gitignore-mirrors` task (this branch, `feat/artifact-trust`) — the 2 new managed-tree lines it added were never exercised against real git-ignore behavior, only string-presence checks (`test_gitignore_bak_seed.py`), which is exactly how the bug shipped undetected. No `.add/GLOSSARY.md` term exists for "managed vendor tree" / "gitignore seed" (grepped, no match) — this task introduces no new domain term, only a correctness fix to existing behavior. User-directed fix shape (verbatim): "Run a proper ADD task (ground→specify→contract→red test that asserts real git check-ignore behavior→build→gate) fixing the 3 patterns to be .add/-relative, push a new commit onto feat/artifact-trust before merge."
Ground SHA: `e4d287d`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: nested `.add/.gitignore` vendor-tree patterns resolve relative to `.add/`, not repo root
Framings weighed: fix the pattern text in place, keep the file location (chosen — the bug is in the STRING not the file's placement; moving the gitignore to repo root would be a much larger, riskier change touching every consumer project's existing layout) · move `.add/.gitignore` to repo-root `.gitignore` instead (rejected — breaks the "everything ADD owns lives under `.add/`" convention, and a repo-root `.gitignore` is user-owned territory the installer must not touch) · leave patterns full-path but also copy the seed file to repo root (rejected — two gitignore files for one concern, double maintenance, still confusing)
Must:
<must>
  - M1: `_GITIGNORE_BODY` (and its 3-tree-parity `.tmpl` twins) list the 2 engine-owned managed-tree patterns as `tooling/` and `docs/` (bare, `.add/`-relative-by-virtue-of-file-location, NOT `.add/tooling/`)
  - M2: `_INSTALLER_MANAGED_IGNORE_EXTRA` / `INSTALLER_MANAGED_IGNORE_EXTRA` (the installer-twin-only personas-teacher line) reads `personas-teacher/` (bare), not `.add/personas-teacher/`
  - M3: a real git repo, after `add.py init` (or either installer's seed path), actually `git check-ignore`s files created under `.add/tooling/**`, `.add/docs/**`, and `.add/personas-teacher/**` — proven with real git, not string presence
  - M4: `test_gitignore_bak_seed.py`'s `ENGINE_MANAGED_TREE_PATTERNS` / `ALL_MANAGED_TREE_PATTERNS` constants (and the 2 assertions that reference the old literal `.add/personas-teacher/` string) are corrected to the bare form so the existing suite keeps testing real behavior, not the bug
  - M5: `ENGINE_PKG_MD5` in `engine_pin.py` is re-pinned to match the corrected `add_engine/constants.py` (confirmed via `engine_manifest.package_digest()`)
  - M6: all 3 `gitignore.tmpl` copies (canonical/bundled/dogfood) and all 2 `constants.py` copies (canonical/bundled; dogfood is untracked but kept in sync for dev-loop honesty) stay byte-identical after the fix
</must>
Reject:
<reject>
  - a managed-tree pattern still written with a leading `.add/` inside `.add/.gitignore` -> "gitignore_pattern_repo_root_style" (the exact bug this task closes — must not regress)
  - `_GITIGNORE_BODY` and `gitignore.tmpl` diverge after the edit -> "gitignore_source_drift" (breaks `test_template_matches_constant`)
  - the engine's shared `_GITIGNORE_BODY` gains the literal string "personas-teacher" -> "engine_handsoff_violated" (must stay installer-twin-only, per `test_engine_unchanged_and_handsoff`)
  - `ENGINE_PKG_MD5` left stale after `constants.py` changes -> "engine_pkg_pin_stale" (parity test would fail on the real digest)
  - the fix only changes string constants without a test that runs real `git check-ignore`/`git status` against seeded files -> "gitignore_fix_unverified_by_real_git" (the exact gap that let the original bug ship)
</reject>
After:
<after>
  - a fresh `add.py init` (direct engine path) or either installer's seed path produces a `.add/.gitignore` whose patterns real git actually honors for all 3 managed vendor trees
  - the sample project at `/Users/tindang/workspaces/tind-repo/add-sample-project`, re-installed/re-seeded, shows those 3 trees as ignored in `git status --porcelain -uall`
  - the full add-method suite is green, including the corrected `test_gitignore_bak_seed.py` and a new real-git-behavior test
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ that no OTHER file in the repo (docs, README, onboarding prose) also asserts or displays the old `.add/tooling/`-style pattern as an example a reader might copy verbatim — lowest confidence because the grep I ran was scoped to `.py`/`.js` sources, not prose/docs; if wrong: a doc example would keep teaching the buggy pattern even after the code is fixed; will grep `.add/docs/` and root `.gitignore`-adjacent prose during build and note anything found rather than silently leaving it
  - [x] that `_installer.py:669` and `:1154` / `cli.js:805`'s near-duplicate-looking tuples (`_GLOBAL_TREES`, `_TREE_LABEL`) are unrelated to this bug — confirmed by reading both: they're a home-mirror layout list and a display-label map, neither touches gitignore pattern text
  - [x] that `ENGINE_PKG_MD5` truly needs re-pinning for a `constants.py` edit — confirmed by reading `engine_manifest.package_files()`, which globs `add_engine/*.py`
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: engine-owned patterns are bare, not .add/-prefixed   # M1
  Given the corrected `_GITIGNORE_BODY` / `gitignore.tmpl` (all 3 trees)
  When the body is inspected as text
  Then it contains the lines `tooling/` and `docs/`
  And it does NOT contain `.add/tooling/` or `.add/docs/`

Scenario: installer-twin personas-teacher line is bare   # M2
  Given the corrected `_INSTALLER_MANAGED_IGNORE_EXTRA` (pip) and `INSTALLER_MANAGED_IGNORE_EXTRA` (npm)
  When each constant is inspected
  Then it holds exactly `personas-teacher/`
  And it does NOT hold `.add/personas-teacher/`

Scenario: real git actually ignores all 3 managed vendor trees   # M3
  Given a fresh git repo with `add.py init` (or either installer) run against it
  When a file is created under each of `.add/tooling/x`, `.add/docs/x`, `.add/personas-teacher/x`
  Then `git check-ignore -v` (or `git status --porcelain --ignored`) reports all 3 as ignored
  And no non-managed file in `.add/` (e.g. `.add/state.json`) is reported as ignored

Scenario: existing seed test asserts the corrected patterns   # M4
  Given `test_gitignore_bak_seed.py`'s `ENGINE_MANAGED_TREE_PATTERNS` / `ALL_MANAGED_TREE_PATTERNS`
  When the full suite runs
  Then every assertion referencing a managed-tree pattern checks the bare form
  And none of the 3 old `.add/`-prefixed literals remain anywhere in that file

Scenario: ENGINE_PKG_MD5 matches the corrected constants.py   # M5
  Given the corrected `add-method/tooling/add_engine/constants.py`
  When `engine_manifest.package_digest(tooling_dir)` is computed against it
  Then the result equals the (re-pinned) `ENGINE_PKG_MD5` in `engine_pin.py`
  And `ENGINE_MD5` (add.py's own pin) is unchanged

Scenario: all mirrored copies stay byte-identical   # M6
  Given the 3 `gitignore.tmpl` copies and 2 tracked `constants.py` copies after the fix
  When they are diffed pairwise
  Then every pair is byte-identical
  And the dogfood-mirror copies match too (best-effort, untracked)

Scenario: a regressed .add/-prefixed pattern is rejected   # R1
  Given a proposed `_GITIGNORE_BODY` that still writes `.add/tooling/`
  When `test_gitignore_bak_seed.py`'s real-git-behavior test runs against it
  Then the test fails with the managed tree reported as NOT ignored
  And the failure is attributed to "gitignore_pattern_repo_root_style"

Scenario: template/constant drift is rejected   # R2
  Given `gitignore.tmpl` and `_GITIGNORE_BODY` edited to different bare forms
  When `test_template_matches_constant` runs
  Then it fails on the byte-diff
  And no build is considered done while it fails

Scenario: engine constant naming personas-teacher is rejected   # R3
  Given a proposed edit that adds "personas-teacher" into the shared `_GITIGNORE_BODY` / `gitignore.tmpl`
  When `test_engine_unchanged_and_handsoff` runs
  Then it fails
  And the personas-teacher pattern stays installer-twin-only

Scenario: a stale ENGINE_PKG_MD5 is rejected   # R4
  Given `constants.py` changed but `ENGINE_PKG_MD5` left at its old value
  When the engine-pin parity check runs
  Then it fails on a digest mismatch
  And the pin comment still names its prior re-aim reason for history

Scenario: a fix with no real-git test is rejected   # R5
  Given a patch that only edits the pattern strings with no new git-check-ignore-based test
  When this task's own §4 TESTS are reviewed at the gate
  Then the gate is refused for missing coverage of the actual defect class
  And a real-git test is added before PASS
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE CONTRACT (no HTTP surface — this task edits static file/constant content)

gitignore.tmpl / _GITIGNORE_BODY (all 3 trees, byte-identical), the 2-line managed-tree block:
  BEFORE:  .add/tooling/␊.add/docs/
  AFTER:   tooling/␊docs/

_INSTALLER_MANAGED_IGNORE_EXTRA (pip) / INSTALLER_MANAGED_IGNORE_EXTRA (npm):
  BEFORE:  (".add/personas-teacher/",)   /   [".add/personas-teacher/"]
  AFTER:   ("personas-teacher/",)        /   ["personas-teacher/"]

test_gitignore_bak_seed.py:
  ENGINE_MANAGED_TREE_PATTERNS = ("tooling/", "docs/")
  ALL_MANAGED_TREE_PATTERNS   = ENGINE_MANAGED_TREE_PATTERNS + ("personas-teacher/",)
  line 83  assertNotIn("personas-teacher/", body, ...)   # was .add/personas-teacher/
  line 179 assertIn("personas-teacher/", body, ...)      # was .add/personas-teacher/
  + NEW test class RealGitIgnoreBehavior: git-init a temp repo, run the seed path, create
    a file under each of .add/tooling/x, .add/docs/x, .add/personas-teacher/x, .add/state.json
    (control — must NOT be ignored), assert via `git check-ignore` / `git status --porcelain
    --ignored` that exactly the 3 managed-tree files are ignored and the control file is not.

engine_pin.py:
  ENGINE_PKG_MD5 = "<recomputed via engine_manifest.package_digest('add-method/tooling')>"
  ENGINE_MD5 unchanged (add.py itself not touched by this task)

  4xx -> { error: "gitignore_pattern_repo_root_style" | "gitignore_source_drift" |
                   "engine_handsoff_violated" | "engine_pkg_pin_stale" |
                   "gitignore_fix_unverified_by_real_git" }
```

Glossary deltas: none — this is a correctness fix to existing behavior, no new domain term
Least-sure flag surfaced at freeze: [contract/test] whether `git status --porcelain --ignored`
  or `git check-ignore -v` is the more robust real-git assertion for the new test — porcelain
  --ignored lists ignored paths directly but its exact output shape can vary slightly by git
  version, while check-ignore is simpler but needs one subprocess call per path; lowest
  confidence because I have not run both against the installed git version yet; if wrong: the
  new test is flaky or needs a second adjustment pass, not a design problem — will pick
  check-ignore per-path (simpler, version-stable) and confirm at build time.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the changed lines (small, surgical fix — no new src/ module)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_template_matches_constant (existing, M1/M6): still passes — proves .tmpl == _GITIGNORE_BODY after both are edited the same way
  - test_init_gitignore_lists_managed_trees (existing, M1): update to expect the bare patterns; still checks personas-teacher absent on the direct engine path
  - test_bundled_template_matches_canonical (existing, M6): still passes after both edited identically
  - test_seed_appends_managed_trees_preserves_custom_lines (existing, M1/M2): update expected patterns to bare form
  - test_personas_teacher_entry_unconditional_even_when_absent (existing, M2): update expected pattern to bare form
  - test_cli_js_seed_lists_managed_trees_on_init (existing, M2): update expected pattern to bare form
  - test_real_git_ignores_managed_trees_after_add_py_init (NEW, M3/R1/R5): git-init a temp dir, run `add.py init`, create files under all 3 managed trees + a control file, assert via `git check-ignore` that exactly the 3 are ignored and the control is not — RED against the current buggy body, GREEN after the fix
  - test_real_git_ignores_managed_trees_after_pip_seed (NEW, M3/R1): same real-git assertion via `_installer._seed_gitignore` directly (pip path)
  - test_real_git_ignores_managed_trees_after_npm_seed (NEW, M3/R1): same real-git assertion via `node cli.js init` (npm path; skip if node unavailable, matching existing convention)
  - test_engine_pkg_md5_matches_digest (NEW, M5/R4): `engine_manifest.package_digest("add-method/tooling") == engine_pin.ENGINE_PKG_MD5`
  - test_engine_md5_unchanged (NEW, M5): `hashlib.md5(Path("add-method/tooling/add.py").read_bytes()).hexdigest() == engine_pin.ENGINE_MD5` (proves add.py itself untouched)
  - test_no_dotadd_prefixed_pattern_remains (NEW, R1/R2): grep all 3 gitignore.tmpl copies + both constants.py copies for the literal strings ".add/tooling/", ".add/docs/", ".add/personas-teacher/" — must find zero
  - test_engine_unchanged_and_handsoff (existing, R3): still passes — confirms "personas-teacher" substring absent from the shared constant/template after the fix
</test_plan>

Tests live in: `add-method/tooling/test_gitignore_bak_seed.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/gitignore.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` · `.add/tooling/templates/gitignore.tmpl` · `add-method/tooling/add_engine/constants.py` · `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` · `.add/tooling/add_engine/constants.py` · `add-method/src/add_method/_installer.py` · `add-method/bin/cli.js` · `add-method/tooling/test_gitignore_bak_seed.py` · `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. fix the 2-line managed-tree block in the canonical `gitignore.tmpl` + `constants.py`, propagate byte-identical to the bundled + dogfood mirrors. 2. fix `_INSTALLER_MANAGED_IGNORE_EXTRA` (`_installer.py`) and its npm twin (`cli.js`). 3. update `test_gitignore_bak_seed.py`'s pattern constants + 2 literal-string assertions to the corrected bare form. 4. add the new real-git-behavior test classes (pip path, npm path, direct-engine path) + the pkg-digest/md5 parity tests + the no-stale-pattern grep test. 5. run full suite, confirm red-then-green on the new tests, recompute `engine_manifest.package_digest()` and re-pin `ENGINE_PKG_MD5` in `engine_pin.py`. 6. re-run the installer against the sample project to confirm the fix holds in practice.

Persona (optional): (absent — generic)
Known-problem fixes: bare unmatched `

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build (test_gitignore_bak_seed.py IS the file I edited — but that edit was declared in §3 CONTRACT itself as part of the fix, not a stealth change after freeze; §3 stayed untouched post-freeze)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — n/a, static text/constant edits, no runtime concurrency surface
- [x] no exposed secrets, injection openings, or unexpected dependencies — pattern-string edits only, zero new deps
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze @ v1 and the overall fix shape via explicit AskUserQuestion answer ("Fix now, same PR")

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a real git repo, after `add.py init` / pip seed / npm seed, actually ignores `.add/tooling/`, `.add/docs/`, `.add/personas-teacher/` — confirmed by running `git check-ignore -v` directly against the re-installed sample project at `/Users/tindang/workspaces/tind-repo/add-sample-project`: all 3 returned a match (`.add/.gitignore:17:tooling/`, `:18:docs/`, `:19:personas-teacher/`), `.add/state.json` returned no match (exit 1, correctly trackable)
- [x] untracked-file count in the sample project collapses to the expected baseline — confirmed by `git status --porcelain -uall`: 375 untracked → 44 after re-seeding with the fixed pattern (the remaining 44 are legitimate project files never meant to be ignored, e.g. `.add/PROJECT.md`, `.add/tasks/`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new test method (`RealGitIgnoreBehavior` ×3, `NoStalePatternTest` ×2, `EnginePkgPinTest` ×2) is discovered and run by `unittest discover` — confirmed: full suite went from 2595 → 2602 tests (exactly +7, matching the 7 new methods added), all passing
- [x] DEAD-CODE (code) — no orphaned symbol: `_init_git_repo` / `_assert_managed_trees_really_ignored` are helpers called by all 3 `RealGitIgnoreBehavior` test methods; nothing unused introduced
- [x] SEMANTIC (prose / non-code) — read `gitignore.tmpl` (both the diff and the full file) and `_GITIGNORE_BODY` in full after editing, confirmed byte-identical via direct string comparison (`add._GITIGNORE_BODY == gitignore.tmpl.read_text()`), not skimmed

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed: `_GITIGNORE_BODY` (constants.py), `_INSTALLER_MANAGED_IGNORE_EXTRA`/`INSTALLER_MANAGED_IGNORE_EXTRA`, `ENGINE_MANAGED_TREE_PATTERNS`/`ALL_MANAGED_TREE_PATTERNS`, `_seed_gitignore()`/`seedGitignore()`, `package_files()`/`package_digest()`, `ENGINE_PKG_MD5` — all read/edited directly at their cited locations, no drift since Ground SHA `e4d287d` (this task's own commits are the only changes since)
- [x] no anchor moved/renamed since Ground SHA — confirmed (single-task window, no intervening commits)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) confirmed the 5 new/updated assertions actually went RED
before the fix, for the CORRECT reason (real `git check-ignore` failing on the 3 managed trees,
plus the stale-pattern-line and installer-constant checks) — not a vacuous assert that would
pass regardless; (2) confirmed the pre-existing string-presence tests in this same file do NOT
detect the bug even with bare patterns (a substring like "tooling/" is trivially present inside
the buggy ".add/tooling/" line too) — this is WHY the new real-git tests exist, and is direct
evidence the fix is proven by mechanism, not by a test that happens to already pass; (3) ran the
FULL add-method suite (2602/2602 green, +7 exactly matching new tests, no pre-existing test
weakened or altered) rather than trusting the target file alone; (4) independently reproduced the
fix against a REAL, separately-created sample project outside the repo (`/Users/tindang/workspaces/
tind-repo/add-sample-project`) — deleted its stale `.gitignore`, re-seeded from the fixed bundled
source, and confirmed via raw `git check-ignore -v` / `git status --porcelain -uall` (untracked
count 375 → 44) that the fix holds outside the test harness too, closing the loop the user
explicitly asked for ("test this enhance before merge"); (5) checked for stubbed/overfit logic —
none of the new tests hardcode an expected git output string; they all invoke real subprocess
`git` commands and assert on exit codes, so a regression in the actual pattern would fail them
again; (6) grepped `.add/docs/` and top-level `.md` files for the old `.add/`-prefixed pattern
being taught as copy-paste content — found only legitimate path-reference prose (e.g. "`.add/docs/`
— the AIDD book"), never a gitignore-pattern example, so no doc needed a companion fix (closes the
§1 ⚠ assumption honestly, no residue left silent).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no secrets, no injection surface, no new dependency; pattern-string edits and
   one recomputed hash literal only
2. Concurrency: CLEAR — no runtime concurrency involved; all edits are static file/constant content
   read at process start, same as before
3. Architecture: CLEAR — no layering change; the fix stays inside the existing
   single-sourced-body / 3-tree-parity / engine-hands-off-personas-teacher conventions this repo
   already enforces with tests, it does not introduce a new pattern
Verdict: PASS
Residue: none
Binding: advisory — mechanical (correctness bug fix in existing tooling, no method-defining
decision; task carries no `risk: high`)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): any future managed-vendor-tree addition must add its pattern
BARE (never `.add/`-prefixed) and gain a `RealGitIgnoreBehavior`-style real-git assertion, not just
a string-presence check (M3/R1 scenarios above, now permanent regression coverage) — watch
`test_no_dotadd_prefixed_pattern_line_remains` for a future red if this regresses; watch fresh
consumer-project installs for an unexpectedly high untracked-file count as the field signal.

### Decisions (ADR)
- [AI] specify — chose fix the pattern text in place, keep the file location; rejected move `.add/.gitignore` to repo-root `.gitignore` instead (rejected — breaks the "everything ADD owns lives under `.add/`" convention, and a repo-root `.gitignore` is user-owned territory the installer must not touch) · leave patterns full-path but also copy the seed file to repo root (rejected — two gitignore files for one concern, double maintenance, still confusing)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] `engine_pin.py`'s `ENGINE_MD5` re-aim comment has grown into a single ~79KB
  physical line (one "prior: X @ Y" clause appended per re-aim, never trimmed) — noticed while
  locating the pin for this task's `ENGINE_PKG_MD5` re-aim; unrelated to this fix (`ENGINE_MD5`
  itself untouched) but worth a future task to cap/relocate the history before a read tool's
  line-length limit makes the file unreadable in one pass (evidence: reading `engine_pin.py`
  whole hit a 25k-token read-tool ceiling on this single line).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · open] a string-presence assertion (`pattern in body`) can stay green even when the
  underlying mechanism is broken — a bare-form substring like `"tooling/"` is trivially present
  inside the buggy full-path line `".add/tooling/"` too, so widening the constant alone would
  not have gone red. Whenever a test's correctness claim depends on an external tool's semantics
  (git's own ignore-pattern resolution here), assert the tool's REAL behavior (subprocess out,
  check exit codes), not a string the tool merely happens to also contain (evidence: this task's
  pre-existing `test_gitignore_bak_seed.py` tests all stayed green through the entire life of the
  bug).
- [ADD · open] the tests→build tamper-tripwire recovery (`add.py phase tests <slug>` → `advance`
  ×2 to re-anchor) applies even when the "tampered" test file is one authored in THIS build and
  then legitimately corrected a bug in, not only a pre-existing test — extending that same lesson
  to self-authored tests too (evidence: `_assert_managed_trees_really_ignored` needed an
  `expect_personas_teacher` flag added after the tests→build crossing, which `add.py gate PASS`
  correctly flagged as `tamper_detected:build_tampered`, resolved by re-crossing tests→build).

