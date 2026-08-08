# TASK: Materialize .add/tooling mirror in CI's test + publish guard jobs

slug: ci-tooling-mirror-gap · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `.github/workflows/ci.yml:52-71` — the `seam-audit` job. ALREADY carries a "Materialize the dogfood tooling mirror" step (5 lines: `mkdir -p .add/tooling` + 4 `cp`/`cp -r` lines copying `add.py`/`add_engine`/`engine_pin.py`/`templates` from `add-method/tooling/`) BEFORE its `python3 .add/tooling/add.py audit` step — shipped by `untrack-add-tooling` (commit `16afe85`). This is the WORKING precedent to replicate, not to touch.
  - `.github/workflows/ci.yml:21-50` — the `test` job ("Tooling tests (py …)"). Runs `python3 -m unittest discover -s tooling -p 'test_*.py'` with `working-directory: add-method` on every push/PR. Has NO materialize step — `actions/checkout@v7` alone leaves `.add/tooling` absent (it is gitignored/untracked as of `16afe85`), yet dozens of tests under `add-method/tooling/test_*.py` hard-require `.add/tooling/add_engine/*.py` to exist (no `.exists()` soft-skip), e.g. `test_engine_package_skeleton.py::test_pkg_digest_3tree_parity` and ~60 similar `_3tree`/`_3tree_parity`/`mirrors_and_pin` tests across many files.
  - `.github/workflows/publish.yml:52-77` — the `guard` job ("Test suite + tag/version match"), the release gate run at tag time. Same `python3 -m unittest discover -s tooling -p 'test_*.py'` invocation, same missing-materialize gap.
  - `add-method/tooling/test_untrack_add_tooling.py:56-77` (`_REQUIRED_MATERIALIZE_LINES`, `CiMaterializes.test_ci_materializes_before_untouched_audit`) — the EXISTING position-based wiring test for seam-audit's materialize step; the pattern this task's new test(s) will replicate for the other 2 jobs.
  - `add-method/tooling/test_audit_ci.py:40-63` (`_jobs_keys`, `_seam_audit_run_line`) — shows the established style for parsing a named job's block out of `ci.yml` via regex, without executing real GitHub Actions.
Context (working folder): `.github/workflows/ci.yml` · `.github/workflows/publish.yml` · a new test file under `add-method/tooling/` (this task's own, mirroring how `untrack-add-tooling` got `test_untrack_add_tooling.py`).
Honors (patterns / conventions): exact repeat of the "materialize the dogfood tooling mirror; installer does this for consumers" step already proven in `seam-audit` — no new design, pure replication to close a gap in coverage. Reuses the position-based (not loose-regex) assertion style `test_untrack_add_tooling.py::CiMaterializes` established, per that task's own change-request lesson (a loosely-anchored regex missed a dropped middle `cp` line).
Anchors the contract cites: `ci.yml:test` job · `ci.yml:seam-audit` job (untouched reference) · `publish.yml:guard` job · `_REQUIRED_MATERIALIZE_LINES`.
Issues/Risks (→ feed §1):
  - **this is a CONFIRMED regression already shipped in `16afe85`**, not a hypothetical — verified via an actual isolated `git clone` + `git checkout feat/artifact-trust` (not the working tree) followed by `python3 -m unittest discover -s tooling -p 'test_*.py'` from that clone's `add-method/`: **38 failures + 68 errors** out of 2570 tests, all traceable to `.add/tooling/add_engine/*.py` being absent.
  - **publish.yml's `guard` job is equally affected** — a release tag pushed today would fail closed before either registry publish step runs, since `guard` gates both `npm`/`pypi` jobs via `needs: guard`.
  - **duplication, not abstraction** — 3 jobs will each carry their own copy of the same 5-line materialize block (no shared composite action). This mirrors the repo's existing style (e.g. the audited invocation `python3 .add/tooling/add.py audit` is ALSO duplicated verbatim into `GETTING-STARTED.md` for consumers, per `test_audit_ci.py::ConsumerShipTest`) — introducing a composite action here would be a bigger, out-of-scope change for a 2-job copy-paste fix.
Related intent: self-discovered while closing out `installer-gitignore-mirrors` (this same session) — found mid-work on `untrack-add-tooling`, restored `.add/tooling` locally and deferred, then raised to Tin via AskUserQuestion after finishing that task; Tin confirmed "New task, fix now" (2026-07-01) rather than deferring or doing a lighter-process patch.
Ground SHA: fcdf0aa

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `.github/workflows/ci.yml`'s `test` job and `.github/workflows/publish.yml`'s `guard` job each materialize the `.add/tooling` dogfood mirror before running the tooling test suite — the same fix `seam-audit` already got in `untrack-add-tooling` — so a truly fresh checkout (no `.add/tooling` on disk, since it's gitignored/untracked) doesn't fail the ~60+ tests that hard-require `.add/tooling/add_engine/*.py` to exist.
Framings weighed: **chosen — copy the exact 5-line materialize step into both jobs**, before their existing `run: python3 -m unittest discover …` step · extract a shared composite GitHub Action (`.github/actions/materialize-tooling/action.yml`) and reference it from all 3 jobs (rejected — over-engineers a 2-job copy-paste fix; the repo's existing style already duplicates the audit invocation itself into `GETTING-STARTED.md`, so duplication here is consistent, not a new pattern) · soft-skip the ~60 affected tests instead (via `.exists()` guards, the same fix already applied to the 2 tests in `untrack-add-tooling`) so CI never needs `.add/tooling` at all (rejected — those tests exist specifically to PROVE 3-tree byte-parity across `add-method/tooling`, `.add/tooling`, and the bundled copy; soft-skipping them on CI would silently stop testing the parity invariant on every push, which is worse than restoring the mirror) · revert `untrack-add-tooling` entirely (rejected — that task's actual goal, keeping a huge regenerable tree out of git history, is sound and already shipped/gated; the gap is narrowly in 2 CI jobs missing a step the 3rd already has, not a flaw in the untracking decision itself)
Must:
<must>
  - M1: `ci.yml`'s `test` job gains the identical materialize step (`mkdir -p .add/tooling` + the 4 `cp`/`cp -r` lines) BEFORE its `Run tooling test suite` step.
  - M2: `publish.yml`'s `guard` job gains the identical materialize step BEFORE its `Run tooling test suite (red/green gate)` step.
  - M3: a new test file asserts, by content AND position (not a loose regex — per `untrack-add-tooling`'s own change-request lesson), that each of the 5 required materialize lines appears in the `test` job's block before its test-run step, and separately in the `guard` job's block before ITS test-run step.
  - M4: the existing `seam-audit` job and its test coverage (`test_untrack_add_tooling.py::CiMaterializes`) are provably untouched by this build.
  - M5: re-run the exact fresh-checkout simulation that surfaced the regression (isolated `git clone` + `git checkout`, no working-tree state) — with the fix applied, the `test`-job command sequence (materialize then run the suite) must produce 2570 tests, 0 failures, 0 errors, matching what `seam-audit`'s job already achieves today.
</must>
Reject:
<reject>
  - the `test` or `guard` job's materialize step diverges in content from `seam-audit`'s (drops `add_engine/`, `templates/`, or `engine_pin.py`) -> "materialize_step_incomplete"
  - a materialize step is added AFTER the test-run step in either job (order matters — the mirror must exist before tests import it) -> "materialize_step_misordered"
  - `seam-audit`'s existing materialize step, its `run:` line, or `test_untrack_add_tooling.py` are modified by this build -> "seam_audit_regressed"
</reject>
After:
<after>
  - a genuinely fresh checkout of any commit on this branch, run through `ci.yml`'s `test` job OR `publish.yml`'s `guard` job, passes the full 2570-test suite with 0 failures/errors — the same guarantee `seam-audit` already provides, now held by all 3 jobs that touch the tooling suite.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ copying the same 5-line step verbatim into 2 more jobs (rather than factoring out a shared composite action) stays maintainable — lowest confidence because a future 4th change to the materialize step (e.g. a new file the mirror must carry) now needs 3 edits instead of 1. If wrong: a future edit misses one of the 3 copies, silently reintroducing this exact class of gap. Mitigate: M3's new test pins all 3 jobs' materialize content directly from the YAML, so a missed copy would fail that test immediately, not silently in production CI.
  - [x] the `test` job's tests actually need `.add/tooling` (not some other absent path) — confirmed: the fresh-clone simulation's failures/errors are 100% `_3tree`/`mirrors_and_pin`/`engine_untouched` style tests reading `.add/tooling/add_engine/*.py` or `.add/tooling/add.py` directly.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the ci.yml test job materializes before running the suite   # M1, M3
  Given `.github/workflows/ci.yml`'s `test` job
  When its YAML block is parsed for `run:` steps
  Then all 5 required materialize lines appear in the block
  And each one's position is BEFORE the "Run tooling test suite" step's position

Scenario: the publish.yml guard job materializes before running the suite   # M2, M3
  Given `.github/workflows/publish.yml`'s `guard` job
  When its YAML block is parsed for `run:` steps
  Then all 5 required materialize lines appear in the block
  And each one's position is BEFORE the "Run tooling test suite (red/green gate)" step's position

Scenario: seam-audit is untouched   # M4, R:seam_audit_regressed
  Given `ci.yml`'s `seam-audit` job and `test_untrack_add_tooling.py`
  When this task's build completes
  Then `git diff` against the pre-build state shows no change to the `seam-audit` job block or to `test_untrack_add_tooling.py`
  And `test_untrack_add_tooling.py::CiMaterializes::test_ci_materializes_before_untouched_audit` still passes unmodified

Scenario: a fresh checkout survives the test job's command sequence   # M5, R:materialize_step_incomplete, R:materialize_step_misordered
  Given an isolated `git clone` + `git checkout` of this branch (not the working tree), where `.add/tooling` is absent because it is gitignored/untracked
  When the extracted materialize lines from the `test` job's block are run via subprocess, THEN `python3 -m unittest discover -s tooling -p 'test_*.py'` is run from that clone's `add-method/`
  Then the suite reports 2570 tests, 0 failures, 0 errors
  And this matches what `seam-audit`'s own materialize+run sequence already achieves today
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ci-tooling-mirror-gap — frozen shape @ v1

.github/workflows/ci.yml — the `test` job gains, immediately before its
existing "Run tooling test suite" step:

    - name: Materialize the dogfood tooling mirror (untracked; installer does this for consumers)
      run: |
        mkdir -p .add/tooling
        cp add-method/tooling/add.py .add/tooling/add.py
        cp -r add-method/tooling/add_engine .add/tooling/add_engine
        cp add-method/tooling/engine_pin.py .add/tooling/engine_pin.py
        cp -r add-method/tooling/templates .add/tooling/templates

  byte-identical to the step already present in the `seam-audit` job — same
  name, same 5 lines, same order.

.github/workflows/publish.yml — the `guard` job gains the IDENTICAL step,
immediately before its existing "Run tooling test suite (red/green gate)" step.

add-method/tooling/test_ci_tooling_mirror_gap.py — new file, this task's own
(parity with test_untrack_add_tooling.py's ownership-per-task convention):
  - reuses the position-based line-by-line assertion style (not a loose
    first-match regex) proven in test_untrack_add_tooling.py::CiMaterializes
  - asserts all 5 required lines are present AND positioned before the
    test-run step, independently for the `test` job block and the `guard`
    job block (parsed the same regex-block-extraction way test_audit_ci.py
    already does for `seam-audit`)
  - asserts `seam-audit`'s own block is untouched (git diff against the
    pre-build state is empty for that job's lines)

Invariants: `seam-audit`'s job block, its `run:` line, and
test_untrack_add_tooling.py receive NO edits; the 2 new materialize steps are
pure duplication of the proven `seam-audit` step, not a new mechanism; no
new GitHub Action version, permission, or secret is introduced; full suite
green; a from-scratch clone + checkout, run through the `test` job's exact
command sequence, produces 2570 tests / 0 failures / 0 errors.
```

Status: FROZEN @ v1 — approved by Tin Dang

Least-sure flag surfaced at freeze: [spec] whether plain 3-way duplication of the
materialize step (rather than a shared composite action) stays maintainable long-term —
cost if wrong: a future materialize-step change needs 3 synchronized edits instead of 1,
but M3's new pinning test catches a missed copy immediately rather than silently, so the
functional risk is low; this is a maintainability-style judgment call, not a correctness one.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete (one test per Must + per Reject)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ci_test_job_materializes_before_suite: ci.yml's `test` job block contains all 5 required materialize lines, each positioned before the "Run tooling test suite" step
  - test_publish_guard_job_materializes_before_suite: publish.yml's `guard` job block contains all 5 required materialize lines, each positioned before the "Run tooling test suite (red/green gate)" step
  - test_seam_audit_job_untouched: the `seam-audit` job block in ci.yml is byte-identical to its pre-build content; test_untrack_add_tooling.py is unmodified
  - test_fresh_checkout_survives_test_job_sequence: an isolated clone (no `.add/tooling` on disk) runs the extracted `test`-job materialize lines then the full suite -> 2570 tests, 0 failures, 0 errors
</test_plan>

Tests live in: `add-method/tooling/test_ci_tooling_mirror_gap.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `.github/workflows/ci.yml` `.github/workflows/publish.yml` `add-method/tooling/test_ci_tooling_mirror_gap.py`
Strategy (ordered batches): 1. add the materialize step to ci.yml's `test` job, byte-identical to seam-audit's, positioned before "Run tooling test suite". 2. add the same step to publish.yml's `guard` job, before "Run tooling test suite (red/green gate)". 3. write `test_ci_tooling_mirror_gap.py` with the 4 planned tests, reusing the position-based assertion style from `test_untrack_add_tooling.py`. 4. run the full suite locally to confirm green. 5. re-run the isolated fresh-clone simulation with the fix applied to confirm 2570/0/0.

Persona (optional): absent — generic
Known-problem fixes: a loosely-anchored regex could miss a dropped middle `cp` line (the exact lesson from `untrack-add-tooling`'s own change-request) → reuse the individual per-line + position-based assertion style, not a single multi-line regex.
Strategy actually used: as planned, with one real-code correction to the M5 test itself, found while confirming it went red for the right reason. The first draft of `test_fresh_checkout_survives_test_job_sequence` cloned the repo, materialized `.add/tooling`, then ran the full suite directly — it failed on `test_pty_clack.py`'s pty-timing tests. Investigating (not assuming) showed the real cause: the clone had no `node_modules` (`npm ci` never ran there), so the interactive-clack code path degraded to its plain-text fallback, producing different timeouts/exit codes than the real CI `test` job (which runs `setup-node` + `npm ci` before the suite). Fixed by adding the same `npm ci` step to the test's own clone-then-run sequence — matching ci.yml's actual fidelity — plus a recursion guard (`_ADD_CI_MIRROR_GAP_NESTED` env var) so a future nested clone (once this test file itself is committed and picked up by `unittest discover`) skips instead of cloning itself forever. After that fix the same test passed cleanly, confirming the fresh-checkout regression this task targets is genuinely resolved, not masked by an unrelated environment gap.
Safety rule (feature-specific): the materialize step must be copied VERBATIM from seam-audit's existing step (not retyped) to avoid introducing an accidental divergence between the 3 copies.
Code lives in: `.github/workflows/`, `add-method/tooling/`
Constraints: do NOT change any test or the contract; do NOT touch the `seam-audit` job or `test_untrack_add_tooling.py`; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `python3 -m unittest discover -s tooling -p 'test_*.py'` -> Ran 2574 tests, OK
- [x] coverage did not decrease — 4 new tests added (`test_ci_tooling_mirror_gap.py`), none removed
- [x] no test or contract was altered during build — `git diff HEAD -- add-method/tooling/test_untrack_add_tooling.py add-method/tooling/test_audit_ci.py` is empty
- [x] the green was EARNED, not gamed — adversarial refute-read by subagent found a real gap (nothing committed yet) and 2 minor test-design defects; both closed before this gate (see below)
- [x] concurrency / timing of the risky operation is safe — pure YAML step addition; no shared/concurrent state
- [x] no exposed secrets, injection openings, or unexpected dependencies — static copy commands, no interpolated event data, no new dependency
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the existing seam-audit step exactly, no new pattern introduced
- [x] a person reviewed and approved the change — Tin Dang approved freeze @ v1 via AskUserQuestion

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] a truly fresh checkout (no `.add/tooling` on disk) survives the `test` job's exact command sequence (materialize → npm ci → run suite) — confirmed by `test_fresh_checkout_survives_test_job_sequence`, which clones the repo, extracts the ACTUAL materialize lines from `ci.yml`'s own text (not a hardcoded copy), runs them, then runs the full suite: 0 failures/errors, `Ran 2574 tests` / `OK`
- [x] `ci.yml`'s `test` job and `publish.yml`'s `guard` job each carry the materialize step, byte-identical to `seam-audit`'s, positioned before their respective test-run step — confirmed by `test_ci_test_job_materializes_before_suite` and `test_publish_guard_job_materializes_before_suite` (content + position, not a loose regex)
- [x] `seam-audit` and its existing test coverage are untouched — confirmed by `test_seam_audit_job_untouched` (git diff empty on `test_untrack_add_tooling.py`; seam-audit's own block still carries all 5 materialize lines before its audit line)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_job_block`/`_materialize_run_block` are each referenced by all 4 test methods that need them; no orphaned helper
- [x] DEAD-CODE (code) — none introduced
- [x] SEMANTIC (prose) — the 2 new YAML steps read in full against `seam-audit`'s existing step: byte-identical name, mkdir line, and all 4 cp/cp -r lines, confirmed via direct extraction+comparison, not eyeballing

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (after closing a disclosed gap — Pass 1 NOT-EARNED)
By: agent-id a534ad63566e26de0 · adversarially checked: (1) whether the fix was actually committed — Pass 1 found `git status` showed the fix was STILL UNCOMMITTED at HEAD `fcdf0aa`, meaning the regression this task targets was still 100% present in real git history; correctly called NOT-EARNED on that basis, independent of whether the code itself was correct. (2) independently re-verified the fix mechanism by hand (its own clone, its own manually-copied materialize lines, its own `npm ci`) — confirmed genuinely green, not a fluke of the test's own code. (3) stress-tested the recursion guard by committing into a disposable scratch clone and manually replaying a nested invocation — confirmed `unittest`'s output distinguishes a real `... ok` pass from a guarded `... skipped '...'`, `OK (skipped=1)`. (4) found 2 concrete defects: `test_fresh_checkout_survives_test_job_sequence` reused the hardcoded `_REQUIRED_MATERIALIZE_LINES` constant instead of parsing the lines out of `ci.yml`'s own text (spec-vs-implementation mismatch), and the pass criterion only checked `returncode==0` + a loose `"OK"` substring rather than the exact zero-failures/errors the contract promised. Both fixed: added `_materialize_run_block()` to extract the real `run: |` body from the job's own YAML text, and tightened the assertion to a bare `^OK$` summary-line regex plus a discovered-test-count sanity floor (a second full local-suite subprocess to get an exact sibling count was considered and rejected — it would reintroduce the same recursion risk the guard exists to prevent). Re-ran the isolated test file and the full suite after both fixes: still green (2574/0). Then committed the actual task deliverables (this was the missing step Pass 1 caught).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent-id a534ad63566e26de0 (same refute-read pass doubled as the 3-lens review)
1. Security: CLEAR — static YAML copy commands, no interpolated untrusted input (github.event.* etc never touched), no new secret/permission/dependency
2. Concurrency: CLEAR — no shared/concurrent state; each job step runs in its own isolated runner
3. Architecture: CLEAR — pure duplication of an already-proven step into 2 more jobs; no new mechanism, no layering change
Verdict: PASS
Residue: none material
Binding: yes — mechanical (CI/publish-workflow change, no security or behavioral ambiguity)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with one real-code correction to the M5 test itself, found while confirming it went red for the right reason. The first draft of `test_fresh_checkout_survives_test_job_sequence` cloned the repo, materialized `.add/tooling`, then ran the full suite directly — it failed on `test_pty_clack.py`'s pty-timing tests. Investigating (not assuming) showed the real cause: the clone had no `node_modules` (`npm ci` never ran there), so the interactive-clack code path degraded to its plain-text fallback, producing different timeouts/exit codes than the real CI `test` job (which runs `setup-node` + `npm ci` before the suite). Fixed by adding the same `npm ci` step to the test's own clone-then-run sequence — matching ci.yml's actual fidelity — plus a recursion guard (`_ADD_CI_MIRROR_GAP_NESTED` env var) so a future nested clone (once this test file itself is committed and picked up by `unittest discover`) skips instead of cloning itself forever. After that fix the same test passed cleanly, confirming the fresh-checkout regression this task targets is genuinely resolved, not masked by an unrelated environment gap.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

