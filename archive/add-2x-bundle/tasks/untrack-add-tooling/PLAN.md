# TASK: Stop tracking .add/tooling — regenerable dogfood mirror of add-method/tooling

slug: untrack-add-tooling · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `.gitignore` (repo root) — the existing `.add/docs/` block ("ADD runtime: keep state + tasks + survivor files, but not the bundled book copy") — ADD a sibling block for `.add/tooling/` with the same rationale (the tooling source already lives in `add-method/tooling/`).
  - `.add/tooling/{add.py,add_engine/,engine_pin.py,templates/}` — 34 currently-TRACKED files (confirmed via `git ls-files .add/tooling`) — `git rm --cached` (stay on disk, untracked going forward; this task does NOT delete the working files, the dogfood copy keeps working locally).
  - `.github/workflows/ci.yml:63` — the sole CI reference to `.add/tooling` (`python3 .add/tooling/add.py audit`) — repoint at `python3 add-method/tooling/add.py audit` (the canonical copy).
  - `add-method/tooling/add_engine/io_state.py:find_root/_require_root` — confirmed root-finding walks up from `Path.cwd()`, independent of the invoking script's own path — so repointing CI to the canonical copy is behavior-identical, not a new materialization step.
  - `add-method/tooling/test_argv_portability.py` (~line 192) and `add-method/tooling/test_merge_base_enforcement.py` (~line 350) — the 2 of 13 `ADD_PY_COPIES`-style pin tests that do NOT yet filter by `.exists()` before hashing (would raise FileNotFoundError once `.add/tooling/add.py` can be legitimately absent) — add the same `present = [p for p in ADD_PY_COPIES if p.exists()]` guard the other 11 sibling files already use.
Context (working folder): `.gitignore` (root) · `.github/workflows/ci.yml` · the 13 test files matching `ADD_PY_COPIES` (11 already safe, 2 need the fix) · no other CI/script call site references `.add/tooling` (confirmed via repo-wide grep).
Honors (patterns / conventions): mirrors the EXISTING `.add/docs/` precedent byte-for-byte (already gitignored, no auto-materialization script, working tree tolerates the gap — `.add/docs/` has 31 files present locally today purely because nobody deleted them, not because anything regenerates them); the `.exists()`-filter soft-skip pattern is already the majority convention (11/13 files), not a new idiom.
Anchors the contract cites: `.gitignore`'s `.add/docs/` block (the pattern to mirror) · `ci.yml:63` · `find_root`/`_require_root` (cwd-based, script-path-independent) · the `.exists()`-filter idiom in the 11 already-safe test files
Issues/Risks (→ feed §1):
  - **generated CLAUDE.md guidance is untouched, deliberately** — `add_engine/guidelines.py:_guideline_block()` emits a UNIVERSAL, consumer-project-facing instruction ("Run `python3 .add/tooling/add.py status`") used by every ADD-installed project, not just this self-hosting repo. This task does NOT special-case the generator for this repo's own meta-nature — a fresh contributor to AIDD-Book itself who wants to dogfood via `.add/tooling/add.py` needs a locally-present copy first (same pre-existing gap `.add/docs/` already has; not solved here, not worse than today).
  - **git rm --cached is the only non-trivial git operation** — must NOT delete the working-tree files (they stay on disk, gitignored, so the current dogfood loop keeps working for anyone who already has them locally; only NEW clones lack them until manually materialized).
  - **scope discipline** — only the 4 touches above; no change to the ENGINE-CHANGE CHECKLIST semantics (canonical + bundled copies still byte-identical and still the 2 REQUIRED, git-tracked pins; `.add/tooling` becomes the 3rd, OPTIONAL, locally-materialized mirror).
Related intent: Tin's request (2026-07-01) — "add .gitignore to skip commit .add/tooling ... just push project artifacts like core documents"; mirrors the already-accepted `.add/docs/` convention (repo hygiene, not a method feature); GLOSSARY has no "dogfood mirror" term yet — this task doesn't coin one, it just applies the existing docs-gitignore rationale to a second tree.
Ground SHA: 1fa91ca

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `.add/tooling/` becomes an untracked, regenerable dogfood mirror of `add-method/tooling/` (the canonical engine source) — git stops tracking it, CI and the two non-soft-skip pin tests are updated so nothing breaks
Framings weighed: gitignore + untrack + repoint CI at canonical + fix the 2 non-soft-skip tests (chosen — mirrors the existing `.add/docs/` precedent exactly, minimal ripple, no new engine logic) · special-case `guidelines.py`'s generator to detect this self-hosting repo and emit a different CLAUDE.md instruction (rejected — over-engineers a universal, consumer-project-facing generator for one repo's meta-nature; the same gap already exists for `.add/docs/` and is tolerated) · add a bootstrap/materialize script for fresh clones (rejected — not requested, and `.add/docs/` sets the precedent that this gap is acceptable; can be added later as its own task if it becomes a real pain point)
Must:
<must>
  - M1: `.gitignore` gains a `.add/tooling/` entry, in the same style/location as the existing `.add/docs/` block (same rationale comment pattern: the source lives elsewhere).
  - M2: all 34 currently-tracked files under `.add/tooling/` (`add.py`, `add_engine/*.py`, `engine_pin.py`, `templates/*`) are removed from git's index via `git rm --cached` — the working-tree files are NOT deleted (the local dogfood copy keeps working).
  - M3 (v2 — change request): `.github/workflows/ci.yml`'s `seam-audit` job gains a materialize step (`mkdir -p .add/tooling` + copy `add.py`/`add_engine/`/`engine_pin.py`/`templates/` from `add-method/tooling/`) BEFORE the existing audit step; the audit step's `run:` line itself is UNCHANGED (`python3 .add/tooling/add.py audit`) — it is a tested, shipped invariant (`test_audit_ci.py::test_ci_audit_command_is_canonical`: "one canonical invocation works in dogfood AND consumer repos"; GETTING-STARTED.md ships the identical string as the copy-paste consumer CI snippet). Repointing that line at `add-method/tooling/add.py` was tried and REVERTED — that path doesn't exist in a real consumer repo, so it breaks the portability invariant (confirmed: 16 cascading test failures across `test_audit_ci.py`, all 13 `test_release_1_X_Y.py::test_audit_line_survives_bumps` forward pins, and the 2 meta-guards `test_four_guards_still_green`/`test_five_guards_still_green`).
  - M4: `test_argv_portability.py` and `test_merge_base_enforcement.py` gain the same `present = [p for p in ADD_PY_COPIES if p.exists()]` filter the other 11 sibling pin-test files already use, so a fresh clone (where `.add/tooling/add.py` doesn't yet exist) doesn't raise `FileNotFoundError`.
  - M5: after the change, canonical (`add-method/tooling/add.py`) and bundled (`add-method/src/add_method/_bundled/tooling/add.py`) still MUST be byte-identical and == `engine_pin.ENGINE_MD5` (the 2 REQUIRED, git-tracked pins are untouched by this task); `.add/tooling/add.py`, if present locally, is checked for parity too but its ABSENCE is never a failure.
  - M6 (discovered at full-suite re-run, post-M3 materialize step): `test_audit_ci.py::_seam_audit_run_line()` — a helper from a prior, unrelated task (audit-ci, v14) — assumed the `seam-audit` job carries exactly one `run:` step; M3's new materialize step is a second `run: |` block-scalar step in the SAME job, so the helper grabbed `|` instead of the audit line (4 cascading failures: 2 `WiringBehaviorTest`, 1 `WiringShapeTest`, 1 meta-guard `test_four_guards_still_green`). Fixed by making the helper skip block-scalar `run:` values and return the first single-line command — the CANONICAL audit string itself is untouched.
</must>
Reject:
<reject>
  - the working-tree files under `.add/tooling/` are deleted (not just untracked) -> "tooling_files_deleted"
  - CI fails because `.add/tooling/add.py` is absent in a fresh checkout -> "ci_tooling_path_broken"
  - the `seam-audit` job's `run:` line is changed away from the canonical `python3 .add/tooling/add.py audit` string -> "canonical_invocation_drifted"
  - a pin test raises FileNotFoundError instead of gracefully skipping an absent `.add/tooling/add.py` -> "pin_test_hard_fails_on_absence"
  - canonical and bundled add.py diverge, or engine_pin.ENGINE_MD5 goes stale, as a side effect of this task -> "engine_pin_drift"
</reject>
After:
<after>
  - `.add/tooling/` is gitignored and untracked (34 fewer tracked files); the working copy is untouched on disk; CI's audit step runs against the canonical copy and still passes; all 13 `ADD_PY_COPIES`-style pin tests pass whether or not `.add/tooling/add.py` exists locally; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ No OTHER script/doc/test outside the 13 grepped files + the 1 CI line silently depends on `.add/tooling/add.py` existing — lowest confidence because the repo is large and grep coverage, while broad (`ADD_PY_COPIES`, `.add/tooling`, workflows/*.yml, scripts/*.py, bin/*.js), can still miss a dynamic string-built path. If wrong: some other consumer breaks silently on a fresh clone / CI run. Mitigate: after the build, re-run the FULL suite (not just the touched files) and grep once more for `\.add/tooling` repo-wide to confirm only the intended 4 touch-points remain live dependents.
  - [ ] `git rm --cached` on this exact fileset leaves the working tree byte-identical (git guarantees this; confirmed by re-hashing all 34 files before/after and diffing `git status` shows them as untracked, not modified/deleted).
  - [ ] The generated CLAUDE.md block (guidelines.py) is out of scope — confirmed: it's a universal per-consumer-project template with no repo-specific logic; changing it is a separate, larger design decision this task deliberately does not take on.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: .add/tooling is gitignored and untracked   # M1, M2
  Given 34 tracked files under .add/tooling/
  When the build runs `git rm --cached` on them and adds the .gitignore entry
  Then `git ls-files .add/tooling` is empty
  And every file still exists on disk, byte-identical to before

Scenario: CI materializes the mirror before auditing   # M3, R:canonical_invocation_drifted
  Given .add/tooling/ is now untracked (absent on a fresh CI checkout)
  When the seam-audit job runs
  Then a materialize step copies add.py/add_engine/engine_pin.py/templates from add-method/tooling/ into .add/tooling/ first
  And the existing `run: python3 .add/tooling/add.py audit` line is BYTE-IDENTICAL to before (untouched)
  And test_audit_ci.py / the 13 release pins / the 2 meta-guards all still pass

Scenario: a pin test tolerates an absent .add/tooling/add.py   # M4, R:pin_test_hard_fails_on_absence
  Given `.add/tooling/add.py` does not exist (simulating a fresh clone)
  When test_argv_portability / test_merge_base_enforcement run their pin-parity test
  Then they skip the absent copy (no FileNotFoundError) and still verify canonical == bundled == ENGINE_MD5

Scenario: canonical/bundled parity holds regardless of .add/tooling presence   # M5, R:engine_pin_drift
  Given .add/tooling/add.py present locally (this dev's working tree)
  When the full suite runs
  Then canonical, bundled, and (if present) .add/tooling copies are all byte-identical and == engine_pin.ENGINE_MD5

Scenario: the working tree is never deleted   # R:tooling_files_deleted
  Given the git rm --cached step ran
  When I inspect the filesystem
  Then all 34 files under .add/tooling/ are still present with unchanged content
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
untrack .add/tooling — frozen shape @ v2   (repo hygiene; mirrors the existing .add/docs/ precedent)

.add/.gitignore — new entry, `.add`-relative, sibling to the existing transient-artifact entries
(NOT the root .gitignore — mid-build steer, keeps the .add-scoped ignore with its siblings):
    # ADD dogfood mirror: tooling/ is a regenerable copy of add-method/tooling/
    # (the canonical engine source) — not committed, mirrors the docs/ rationale above.
    tooling/

git rm --cached (working-tree files untouched):
    git rm -r --cached .add/tooling/add.py .add/tooling/add_engine .add/tooling/engine_pin.py \
        .add/tooling/templates

.github/workflows/ci.yml `seam-audit` job — the audit `run:` line is UNTOUCHED (a tested,
shipped invariant: test_audit_ci.py's CANONICAL, "one canonical invocation works in dogfood
AND consumer repos" — GETTING-STARTED.md ships the identical string to consumers). Instead,
ADD a materialize step immediately before it:
    - name: Materialize the dogfood tooling mirror (untracked; installer does this for consumers)
      run: |
        mkdir -p .add/tooling
        cp add-method/tooling/add.py .add/tooling/add.py
        cp -r add-method/tooling/add_engine .add/tooling/add_engine
        cp add-method/tooling/engine_pin.py .add/tooling/engine_pin.py
        cp -r add-method/tooling/templates .add/tooling/templates
    - name: Audit the dogfood board (.add)
      run: python3 .add/tooling/add.py audit          # UNCHANGED line

add-method/tooling/test_argv_portability.py (~l.192) + test_merge_base_enforcement.py (~l.350):
    - digests = {_md5(p) for p in ADD_PY_COPIES}                    # (or hashlib.md5(...) inline)
    + present = [p for p in ADD_PY_COPIES if p.exists()]
    + digests = {_md5(p) for p in present}                          # matches the 11 sibling files

Invariants: canonical add.py == bundled add.py == engine_pin.ENGINE_MD5 (2 REQUIRED tracked pins,
untouched); .add/tooling/add.py, if present locally, is checked too but its ABSENCE never fails;
the seam-audit `run:` line stays byte-identical to before (test_audit_ci.py CANONICAL + the 13
release-test forward pins + the 2 meta-guards all still pass); full suite green; no engine code
(add.py itself) is edited by this task.
```

Least-sure flag surfaced at freeze: (v2) [contract] the CI materialize step correctly stages EVERYTHING `python3 .add/tooling/add.py audit` needs at runtime (add.py + add_engine/ + engine_pin.py + templates/) — cost if wrong: CI passes locally in the fixture but fails on the real `seam-audit` job for a missing import/asset. Mitigated: the v1 discovery itself (test_audit_ci.py's WiringBehaviorTest already builds and exercises this EXACT installed-layout fixture — add.py + add_engine copied into a tmp `.add/tooling/` — so the fixture's own construction is the template for the CI materialize step, not a guess). Secondary [contract]: the grep-based confirmation that no OTHER file depends on `.add/tooling/add.py` existing, beyond the now-corrected touch list — mitigated by a full-suite run (done once already, surfaced exactly this gap) + a final repo-wide re-grep after the fix. Tertiary [spec]: the generated CLAUDE.md instruction (`python3 .add/tooling/add.py status`) is deliberately left as-is — a fresh AIDD-Book contributor hits the same pre-existing gap `.add/docs/` already has, not a new one.

Status: FROZEN @ v2 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_tooling_untracked_and_ignored: git ls-files .add/tooling is empty after the build; .gitignore matches the path (git check-ignore)
  - test_ci_materializes_before_untouched_audit: ci.yml gains a materialize step (mkdir + copy add.py/add_engine/engine_pin.py/templates) BEFORE the audit step; the audit step's `run:` line stays byte-identical to `python3 .add/tooling/add.py audit`
  - test_argv_portability_tolerates_absent_tooling_copy: simulate .add/tooling/add.py absent (tmp fixture) / no FileNotFoundError / canonical==bundled==ENGINE_MD5 still asserted
  - test_merge_base_enforcement_tolerates_absent_tooling_copy: same, for the sibling file
  - test_working_tree_files_unchanged: the 34 files' bytes are identical before/after `git rm --cached` (content untouched, only index entry removed)
</test_plan>

Tests live in: `add-method/tooling/test_untrack_add_tooling.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.gitignore` `.add/.gitignore` `.github/workflows/ci.yml` `add-method/tooling/test_argv_portability.py` `add-method/tooling/test_merge_base_enforcement.py` `add-method/tooling/test_untrack_add_tooling.py` `add-method/tooling/test_audit_ci.py`
Strategy (ordered batches): 1. add the ignore rule for the tooling mirror — placed in `.add/.gitignore` (as `tooling/`, `.add`-relative) rather than the root `.gitignore`, per Tin's steer mid-build: keeps the `.add/`-scoped ignore alongside its sibling (`scope-snapshot.json` etc.) instead of duplicating a `.add/`-specific concern into the root file. 2. `git rm -r --cached` the 34 tracked files under `.add/tooling/` (working tree untouched — confirm via `git status` shows them untracked, not deleted). 3. (v2, corrected) revert the ci.yml `run:` line back to the untouched canonical `python3 .add/tooling/add.py audit`; instead ADD a `Materialize the dogfood tooling mirror` step immediately before the audit step, copying add.py/add_engine/engine_pin.py/templates from `add-method/tooling/`. 4. add the `.exists()`-filter guard to the 2 non-soft-skip pin tests. 5. write test_untrack_add_tooling.py (git-state assertions, no sandbox needed — this is a repo-hygiene check, not an engine feature). 6. full suite green + a fresh repo-wide grep for `\.add/tooling` to confirm no missed dependent. 7. (discovered at full-suite run — the exact contingency §1's ⚠ assumption anticipated) fix `test_audit_ci.py::_seam_audit_run_line()`, which assumed the seam-audit job carries exactly one `run:` step — it now grabs the materialize step's block-scalar `|` instead of the audit line; made it skip block-scalar `run:` values and return the first single-line command (the CANONICAL audit line stays untouched).

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: as planned (batches 1-6), plus one unplanned batch 7 discovered at the full-suite run: fixed `test_audit_ci.py::_seam_audit_run_line()`, whose single-`run:`-step assumption broke once M3 added a second `run:` step to the same job (4 cascading failures) — scope widened + re-snapshotted before fixing, per the task's own flagged mitigation. A refute-read subagent then found the new `test_ci_materializes_before_untouched_audit` itself was under-specified (loosely-anchored regex didn't check the middle `cp` lines) — strengthened to assert each required line individually + by position, confirmed RED-for-the-right-reason then GREEN.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2564/0 (add-method: `python3 -m unittest discover -s tooling -p 'test_*.py'`), incl. the 5 new + 6 test_audit_ci + 12 test_md_section + 11 forward-pinned release + test_five_guards_still_green
- [x] coverage did not decrease — net +1 test file (5 tests), 2 sibling files gained a guard branch, 0 removed
- [x] no test or contract was altered during build in a weakening sense — test_audit_ci.py's helper was FIXED (its own assumption of a single `run:` step broke on the new materialize step), not weakened; the CANONICAL string it asserts against is untouched
- [ ] the green was EARNED, not gamed — pending subagent refute-read (below)
- [x] concurrency / timing of the risky operation is safe — no concurrent writers; `git rm --cached` + CI YAML edits are static, no runtime race
- [x] no exposed secrets, injection openings, or unexpected dependencies — CI step only copies local repo files, no new external input/secret surface
- [x] layering & dependencies follow CONVENTIONS.md — no new package deps; test files follow the existing ADD_PY_COPIES / git-state-assertion conventions
- [ ] a person reviewed and approved the change — pending Tin's confirmation at this gate (CI/CD-touching change)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `git ls-files .add/tooling` is empty — confirmed via `test_tooling_untracked_and_ignored`; `git check-ignore -q .add/tooling/add.py` exits 0
- [x] the 34 working-tree files are byte-present, untouched — confirmed via `test_working_tree_files_unchanged` + `git status --short` shows them `D` (staged deletion from index only, not from disk)
- [x] ci.yml's seam-audit `run:` line for the audit step is byte-identical to before — confirmed via `test_ci_materializes_before_untouched_audit` + `test_audit_ci.py`'s CANONICAL assertion (both green)
- [x] a materialize step precedes the audit step in ci.yml — confirmed via regex position check in `test_ci_materializes_before_untouched_audit`
- [x] canonical/bundled/`.add/tooling` add.py copies stay byte-identical and == `engine_pin.ENGINE_MD5` — confirmed via manual md5 (all three: `e23cd35ebc910a2b9e7f067b9a3a4f4b`)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_seam_audit_run_line()`'s new block-scalar skip is referenced by all 4 `test_audit_ci.py` tests that call it (WiringShapeTest x2, WiringBehaviorTest x2 via `_run_ci_command`)
- [x] DEAD-CODE (code) — no new unused symbol; the `.exists()` filters reuse the existing `present` idiom, no new helper introduced
- [x] SEMANTIC (prose / non-code) — read `.github/workflows/ci.yml` in full: confirmed the materialize step's copy list (add.py, add_engine/, engine_pin.py, templates/) matches add.py's own import graph (`import add_engine.constants` et al. + `engine_pin`) and the templates dir `new-task`/`init` read from

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (after heal — Pass 1 NOT-EARNED)
By: subagent (refute-read) · adversarially checked: whether each new/modified test could pass
for the wrong reason. Pass 1 (NOT-EARNED): `test_ci_materializes_before_untouched_audit`'s
first-...-last DOTALL regex only anchored on the opening `mkdir -p .add/tooling` and closing
`add-method/tooling/templates` lines — it passed even with the middle `cp` lines (add.py,
add_engine/, engine_pin.py) deleted, which would break CI exactly as Reject item
`ci_tooling_path_broken` describes. Confirmed empirically by deleting the `add_engine` cp line
and re-running: the old test still passed. Fixed by asserting each of the 5 required lines
individually + by position (must precede the audit line) — re-confirmed RED when a line is
missing, GREEN when complete. Also independently verified: `.exists()` filters can't vacuously
pass (canonical+bundled always present, digests never empty); the materialize copy list is a
safe superset of add.py's actual import graph; `.add/tooling` truly untracked yet disk-intact.
Residue closed: `_seam_audit_run_line()` now also skips `run: >` folded scalars, not just `|`.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new secrets, external input, or injection surface; CI step only copies local repo files with static, non-parameterized paths
2. Concurrency: CLEAR — no runtime concurrency; `git rm --cached` and the CI YAML edit are static, single-writer changes
3. Architecture: CLEAR — mirrors the existing `.add/docs/` gitignore precedent; the materialize-step pattern mirrors `test_audit_ci.py`'s own `WiringBehaviorTest` fixture construction, not a new idiom
Verdict: PASS
Residue: none material — the one fragility found (block-scalar detection) was closed during this verify, not carried forward
Binding: advisory — mechanical (repo hygiene; risk: normal)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose gitignore + untrack + repoint CI at canonical + fix the 2 non-soft-skip tests; rejected special-case `guidelines.py`'s generator to detect this self-hosting repo and emit a different CLAUDE.md instruction (rejected — over-engineers a universal, consumer-project-facing generator for one repo's meta-nature; the same gap already exists for `.add/docs/` and is tolerated) · add a bootstrap/materialize script for fresh clones (rejected — not requested, and `.add/docs/` sets the precedent that this gap is acceptable; can be added later as its own task if it becomes a real pain point)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned (batches 1-6), plus one unplanned batch 7 discovered at the full-suite run: fixed `test_audit_ci.py::_seam_audit_run_line()`, whose single-`run:`-step assumption broke once M3 added a second `run:` step to the same job (4 cascading failures) — scope widened + re-snapshotted before fixing, per the task's own flagged mitigation. A refute-read subagent then found the new `test_ci_materializes_before_untouched_audit` itself was under-specified (loosely-anchored regex didn't check the middle `cp` lines) — strengthened to assert each required line individually + by position, confirmed RED-for-the-right-reason then GREEN.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

