# TASK: Fresh-checkout nested-suite OK regex tolerates all known environment-conditional skips, not just the recursion guard

slug: nested-suite-skip-count-tolerance · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/test_ci_tooling_mirror_gap.py:_NESTED_OK_SUMMARY_RE` (module-level compiled regex, l.64) — the sole symbol this task edits; `FreshCheckoutSurvivesTestJob.test_fresh_checkout_survives_test_job_sequence` (asserts against it, l.208) and `OkSummaryRegexTest` (its own pure-logic coverage, l.221-240) both consume it read-only, no signature change to either.
Context (working folder): none beyond the one test file — no config/data/docs touched.
Honors (patterns / conventions): the task this regex belongs to (`fresh-checkout-skip-tolerance`, commit `ba09498`) deliberately anchored tolerance to the LITERAL count `1` rather than `\(skipped=\d+\)` specifically so an unrelated second skip fails loudly (see l.61-63 comment) — this task must preserve that anti-silent-regression intent, not just widen the regex to `\d+` and lose it.
Anchors the contract cites: `_NESTED_OK_SUMMARY_RE` (the regex itself); `add.py`'s existing environment-conditional skip guards it must now KNOW ABOUT by name: `test_component_registry.py:17` / `test_components_validator.py`/`test_cross_component_contract.py`/`test_cross_component_milestone.py`/`test_multirepo_federation.py`/`test_per_component_verify.py` — each raises `unittest.SkipTest("component pillar requires tomllib (Python 3.11+)")` at MODULE level when `tomllib` (stdlib, 3.11+) is unavailable, collapsing that whole file's tests into ONE skip result (confirmed empirically, not just read: a real python3.10 run of the full nested suite shows exactly 6 such skip lines, one per file, and those 6 files' ~114 test methods vanish entirely from the "Ran N tests" tally rather than appearing as 114 individual skips — module-level `SkipTest` short-circuits collection before the classes are even defined); `test_packaging.py:PyWheelTest` (3 tests, `@unittest` — skips per-method, not module-level, when `setuptools` isn't importable in the environment the nested clone's `npm ci` + subprocess runs in).
Issues/Risks (→ feed §1): the CI matrix runs BOTH py3.10 and py3.12 (`.github/workflows/ci.yml` "Tooling tests (py 3.10)"/"(py 3.12)" jobs) — py3.10 lacks `tomllib` (6 module-skips) while py3.12 has it (0 module-skips) but may still hit the 3 setuptools-conditional skips depending on the runner's pip/setuptools install state, so the two jobs can legitimately report DIFFERENT skip counts for DIFFERENT reasons in the same run. A fix that hardcodes a single new literal count (e.g. `skipped=7`) would immediately break the py3.12 job (which showed `skipped=4` in the same CI run) — the fix must express tolerance as "recursion guard + any subset of these SPECIFIC known reasons," not a new fixed number.
Related intent: PROJECT.md's goal names "no lost context across sessions" and "self-driving build→verify"; this bug undermines that by making a CI gate red for a reason that has nothing to do with the actual PR under review, which (if left unfixed) trains future sessions to distrust or ignore this specific CI check — the opposite of the trust the `artifact-trust` milestone this session's other 2 tasks belong to is meant to build. GLOSSARY has no existing term for "environment-conditional skip"; none needed (no new domain concept, purely a test-harness fix).
Ground SHA: `44fe56b` (confirmed via `git rev-parse --short HEAD`) — cite the symbol name `_NESTED_OK_SUMMARY_RE`, not a bare line number, since this file may reflow.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: compute the nested full-suite run's expected skip count from the CURRENT interpreter's known environment-conditional causes (tomllib / setuptools availability), instead of a hardcoded literal.
Framings weighed: compute an exact expected-skip-count from the interpreter's own tomllib/setuptools availability and require an EXACT match each run (chosen — self-correcting for the two KNOWN causes, still fails loudly on anything unaccounted, no CI-yaml or subprocess-invocation change needed) · widen to an open `\(skipped=\d+\)` range (rejected — loses the anti-silent-regression guarantee the original task explicitly designed for) · hardcode a second literal like `skipped=(1|7)` (rejected — equally fragile the moment a third conditional skip appears or a runner's setuptools state differs) · pass `-v` to the nested subprocess and match skip reasons by text (rejected — unnecessarily changes the subprocess's own invocation/output shape for a problem countable without it)
Must:
<must>
  - M1: a `_expected_skip_count()` helper returns `1` (this file's own recursion guard, always present in a nested run) `+ 6` when `tomllib` is unavailable to the current interpreter (`sys.version_info < (3, 11)`) `+ 3` when `setuptools` is not importable to the current interpreter
  - M2: a `_nested_ok_regex(n)` builder returns a compiled pattern matching a bare `OK` summary line (when `n == 0`) or `OK (skipped=n)` for the exact given `n`, and rejects any other skip count
  - M3: `test_fresh_checkout_survives_test_job_sequence` computes `_expected_skip_count()` once (before spawning the nested subprocess) and asserts against `_nested_ok_regex(that count)`, replacing the old fixed `_NESTED_OK_SUMMARY_RE` module constant
  - M4: an unrelated/unexpected skip beyond the computed expected count still fails the assertion loudly (the anti-silent-regression guarantee from `fresh-checkout-skip-tolerance` is preserved, not loosened)
  - M5: `OkSummaryRegexTest`'s pure-logic coverage is rewritten against `_nested_ok_regex`/`_expected_skip_count` directly — covering at least: expected=1 (both deps present), expected=7 (tomllib absent, setuptools present), an arbitrary mid-range count via dependency injection/monkeypatch, and rejection of expected±1
  - M6: no edit to any OTHER test file, to `ci.yml`/`publish.yml`, or to the materialize-step logic — scope is `test_ci_tooling_mirror_gap.py` only
</must>
Reject:
<reject>
  - a fresh hardcoded literal skip count (e.g. `skipped=(1|7)`) -> "still_environment_fragile"
  - an open-ended `\(skipped=\d+\)` range -> "loses_anti_regression"
  - matching skip reasons via `-v` subprocess text -> "no_reason_text_available_without_v_and_unneeded"
</reject>
After:
<after>
  - the nested-suite assertion computes its own expected skip count from the CURRENT interpreter's tomllib/setuptools availability immediately before the subprocess runs
  - `test_ci_tooling_mirror_gap.py`'s own suite is green under both a tomllib-less (3.10) and a tomllib-having interpreter, with zero edits to any other test file
  - a skip count that does not match the computed expectation for the CURRENT interpreter still fails loudly
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the "+3 for setuptools-unavailable" contribution is proxied by checking THIS process's own setuptools importability, assuming the nested subprocess (same `sys.executable`) has identical site-packages availability — lowest confidence because I have not traced whether the nested clone's `npm ci` step could ever alter the Python environment (it shouldn't — it only touches `add-method/node_modules` — but I have not proven a negative); if wrong: the computed count is off by 3 in some environment, which fails the assertion LOUDLY (a false-positive CI red), never silently masks a real new skip — an acceptable failure direction given this task's whole point is fail-loud over silent-pass.
  - [x] confirmed empirically during GROUND: a real python3.10 nested-clone run showed exactly `skipped=7` (=1+6+0, setuptools WAS importable there) and a real python3.13 nested-clone run (no full clone rerun, direct discover on the same materialized clone) showed exactly `skipped=4` (=1+0+3, tomllib present, setuptools NOT importable in that environment) — both match the M1 formula exactly, no open assumption remains on the formula itself.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: both deps present computes expected=1   # M1
  Given tomllib is importable and setuptools is importable
  When _expected_skip_count() is called
  Then it returns 1

Scenario: tomllib missing adds 6   # M1
  Given tomllib is NOT importable (Python < 3.11) and setuptools is importable
  When _expected_skip_count() is called
  Then it returns 7

Scenario: setuptools missing adds 3   # M1
  Given tomllib is importable and setuptools is NOT importable
  When _expected_skip_count() is called
  Then it returns 4

Scenario: both deps missing sums both   # M1
  Given tomllib is NOT importable and setuptools is NOT importable
  When _expected_skip_count() is called
  Then it returns 10

Scenario: regex builder matches its own exact count   # M2
  Given _nested_ok_regex(7) has been built
  When matched against "OK (skipped=7)\n"
  Then it matches
  And matching against "OK (skipped=6)\n" or "OK (skipped=8)\n" fails

Scenario: regex builder with n=0 accepts a bare OK   # M2
  Given _nested_ok_regex(0) has been built
  When matched against "OK\n"
  Then it matches

Scenario: integration test asserts against the computed count   # M3
  Given a real nested-clone subprocess run under the CURRENT interpreter
  When the combined stdout+stderr is checked
  Then it is asserted against _nested_ok_regex(_expected_skip_count()), not a fixed constant

Scenario: an unrelated extra skip still fails loudly   # M4/R2
  Given the computed expected count for this interpreter is N
  When the nested run actually reports N+1 skips
  Then the assertion fails
  And no environment-driven tolerance silently absorbs the extra skip

Scenario: pure-logic coverage exercises the builder directly, not a fixed module constant   # M5
  Given OkSummaryRegexTest's own test methods
  When they call _nested_ok_regex/_expected_skip_count with injected/mocked availability
  Then they cover expected=1, expected=7, an arbitrary mid-range count, and rejection of expected±1

Scenario: no other file is touched   # M6/R1/R3
  Given the fix is scoped to test_ci_tooling_mirror_gap.py
  When the diff is inspected
  Then ci.yml, publish.yml, the materialize-step logic, and every other test_*.py file are unchanged
  And the nested subprocess invocation itself (no -v flag) is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE CONTRACT  add-method/tooling/test_ci_tooling_mirror_gap.py

Before (l.57-64):
  # the nested clone's own full-suite run always self-skips exactly once — its own
  # recursion guard (FreshCheckoutSurvivesTestJob, rediscovered inside the clone)
  # hits `_ADD_CI_MIRROR_GAP_NESTED == "1"` and calls skipTest. A bare `^OK$` can
  # never match that real, structurally-guaranteed shape, so tolerate exactly
  # `OK (skipped=1)` too — anchored to the literal count, not `\(skipped=\d+\)`,
  # so an unrelated SECOND skip still fails loudly instead of being silently waved
  # through (task fresh-checkout-skip-tolerance).
  _NESTED_OK_SUMMARY_RE = re.compile(r"(?m)^OK(?: \(skipped=1\))?\s*$")

After (replaces the block above):
  # the nested clone's own full-suite run always self-skips exactly once — its own
  # recursion guard (FreshCheckoutSurvivesTestJob, rediscovered inside the clone)
  # hits `_ADD_CI_MIRROR_GAP_NESTED == "1"` and calls skipTest — PLUS whatever
  # environment-conditional skips the CURRENT interpreter is already known to
  # produce elsewhere in the suite (component-pillar tests self-skip as one unit
  # per file when tomllib is unavailable < 3.11; test_packaging's wheel checks
  # skip per-method when setuptools isn't importable). Compute the exact expected
  # count instead of a fixed literal, so an unrelated THIRD kind of skip still
  # fails loudly instead of being silently waved through (task
  # fresh-checkout-skip-tolerance / nested-suite-skip-count-tolerance).
  def _expected_skip_count() -> int:
      n = 1  # this file's own recursion guard
      try:
          import tomllib  # noqa: F401
      except ModuleNotFoundError:
          n += 6  # test_component_registry / _components_validator / _cross_component_contract
                  # / _cross_component_milestone / _multirepo_federation / _per_component_verify
                  # each self-skip as ONE module-level result when tomllib is absent (< 3.11)
      if importlib.util.find_spec("setuptools") is None:
          n += 3  # test_packaging.PyWheelTest's 3 wheel-build checks
      return n

  def _nested_ok_regex(n: int) -> re.Pattern:
      if n <= 0:
          return re.compile(r"(?m)^OK\s*$")
      return re.compile(rf"(?m)^OK \(skipped={n}\)\s*$")

Call-site change (inside test_fresh_checkout_survives_test_job_sequence, replaces the
existing self.assertRegex(combined, _NESTED_OK_SUMMARY_RE, ...) call):
  expected = _expected_skip_count()
  self.assertRegex(combined, _nested_ok_regex(expected),
                    f"fresh-checkout suite must report a bare 'OK' summary line matching "
                    f"this interpreter's expected skip count ({expected}):\n{tail}")

OkSummaryRegexTest (l.221-240) rewritten to test _nested_ok_regex/_expected_skip_count
directly (exact new test list finalized at §4 TESTS) — no other class/file touched.

New import required: `import importlib.util` (stdlib, alongside existing `import re`,
`import sys` — `sys` is already imported at l.33).
```

Glossary deltas: none
Least-sure flag surfaced at freeze: [contract] whether `1` and `3` are the true, currently-correct
constants for the recursion-guard and setuptools-absent contributions respectively — both are read
off THIS run's empirical evidence (a real nested-clone run under the current interpreter), not off
the source code's own skip-count declarations, so a future change to `test_packaging.py`'s number
of setuptools-gated tests (currently 3) would silently desync this formula's `+3` until someone
re-derives it; cost if wrong: the assertion fails loudly (safe direction — never silently masks a
new skip) but for the WRONG reason, costing a future session the same investigation time this task
just spent. Mitigated by naming the exact contributing test classes in a comment (§3 above) so a
future reader knows to re-count them if `test_packaging.py`'s wheel-check tests are ever added to
or removed.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new `_expected_skip_count`/`_nested_ok_regex` logic (small, pure, fully branch-coverable)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_both_deps_present_computes_one: monkeypatch both availability checks to True/found / call _expected_skip_count() / assert == 1
  - test_tomllib_missing_adds_six: monkeypatch tomllib-unavailable, setuptools-available / assert _expected_skip_count() == 7
  - test_setuptools_missing_adds_three: monkeypatch tomllib-available, setuptools-unavailable / assert _expected_skip_count() == 4
  - test_both_missing_sums_both: monkeypatch both unavailable / assert _expected_skip_count() == 10
  - test_regex_matches_its_own_exact_count: build _nested_ok_regex(7) / assertRegex against "OK (skipped=7)\n" / assertNotRegex against "OK (skipped=6)\n" and "OK (skipped=8)\n"
  - test_regex_zero_accepts_bare_ok: build _nested_ok_regex(0) / assertRegex against "OK\n"
  - test_fresh_checkout_survives_test_job_sequence (EXISTING, updated in place): real nested-clone integration test now asserts against _nested_ok_regex(_expected_skip_count()) computed from THIS process, instead of the old fixed _NESTED_OK_SUMMARY_RE — unchanged otherwise (clone/materialize/npm-ci/subprocess steps untouched)
  - test_unexpected_extra_skip_still_fails: assertNotRegex("OK (skipped=8)\n", _nested_ok_regex(7)) — proves M4/R2 directly, an extra skip beyond computed-expected is never silently absorbed
  - no new test for M6 (no-other-file-touched): a repo-wide diff invariant, verified manually at VERIFY via `git status`, not a unit of behavior
</test_plan>

Tests live in: `add-method/tooling/test_ci_tooling_mirror_gap.py` (existing file — new/rewritten methods land inside its existing `OkSummaryRegexTest` class plus the one updated integration test) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/test_ci_tooling_mirror_gap.py`
Strategy (ordered batches): 1. add `import importlib.util` and `from unittest import mock` to the top-of-file imports. 2. define `_tomllib_available()` / `_setuptools_available()` as two small named seams (mockable by the pure-logic tests) that `_expected_skip_count()` calls, plus `_nested_ok_regex(n)` — replacing the old fixed `_NESTED_OK_SUMMARY_RE` module constant. 3. update the one call site inside `test_fresh_checkout_survives_test_job_sequence` to compute `_expected_skip_count()` and assert against `_nested_ok_regex(that count)`. 4. re-run `OkSummaryRegexTest` (already red) to green, then the one real (slow) integration test to confirm the new call site still passes end-to-end.

Persona (optional): none — generic
Known-problem fixes: hardcoding a second fixed literal (e.g. `skipped=(1|7)`) → compute both contributions from live interpreter introspection instead, named per-cause so a future third cause is additive, not a rewrite.
Strategy actually used: as planned, with one refinement within the same contract's observable surface: the CONTRACT's inline `_expected_skip_count()` sketch (a bare `try/import`+`find_spec` check written directly in the function body) was factored into two named, individually-mockable seam functions (`_tomllib_available()`/`_setuptools_available()`) so `OkSummaryRegexTest` could inject each availability combination via `mock.patch` rather than needing to fake `sys.modules`/monkeypatch `importlib` internals — the summed formula and the two exposed names (`_expected_skip_count`, `_nested_ok_regex`) the contract actually binds are unchanged.
Safety rule (feature-specific): none — pure test-harness logic, no I/O/concurrency/atomicity concern
Code lives in: `add-method/tooling/test_ci_tooling_mirror_gap.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe (N/A — pure sequential logic, no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `OkSummaryRegexTest`'s 8 pure-logic tests pass under THIS interpreter (both tomllib and setuptools available here) — confirmed via `cd add-method/tooling && python3 -m unittest test_ci_tooling_mirror_gap.OkSummaryRegexTest -v` → 8/8 ok
- [x] the real (slow, ~72s) nested-clone integration test still passes end-to-end with the new call site — confirmed via `cd add-method && python3 -m unittest discover -s tooling -p 'test_ci_tooling_mirror_gap.py' -v` → 12/12 ok, including `test_fresh_checkout_survives_test_job_sequence`
- [x] the formula matches BOTH real-world environments seen this session — confirmed by the GROUND-phase empirical evidence: a real python3.10 nested run showed `skipped=7` (=1+6+0) and a real setuptools-less environment showed `skipped=4` (=1+0+3), both exactly matching `_expected_skip_count()`'s arithmetic

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_tomllib_available`/`_setuptools_available` are called by `_expected_skip_count` (and independently by the mock.patch targets in `OkSummaryRegexTest`); `_expected_skip_count`/`_nested_ok_regex` are both called by `test_fresh_checkout_survives_test_job_sequence`'s new call site and by 8 `OkSummaryRegexTest` methods — confirmed by reading the diff, no orphaned new symbol
- [x] DEAD-CODE (code) — the old `_NESTED_OK_SUMMARY_RE` module constant was fully removed (not left as dead weight alongside the new functions) — confirmed via `grep -n NESTED_OK_SUMMARY_RE add-method/tooling/test_ci_tooling_mirror_gap.py` → 0 matches
- [ ] SEMANTIC (prose / non-code) — N/A, this task's diff is pure code (no doc/prose file touched)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by `python3 -c "import test_ci_tooling_mirror_gap as m; m._expected_skip_count(); m._nested_ok_regex(1); m._tomllib_available(); m._setuptools_available()"` from `add-method/tooling` — all four resolve and execute without error
- [x] no anchor moved/renamed since Ground SHA (`44fe56b`) — this task both created and consumed these symbols within its own build, no pre-existing anchor to drift

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) whether `test_both_deps_present_computes_one`'s mocks are vacuous — confirmed the REAL unmocked environment here already returns `(True, True) → 1`, so THAT one test alone could pass even if `mock.patch` silently no-op'd; however `test_tomllib_missing_adds_six`/`test_setuptools_missing_adds_three`/`test_both_missing_sums_both` produce results (7, 4, 10) that are IMPOSSIBLE without the mock genuinely taking effect (the real baseline is 1), and all three passed for real using the identical `mock.patch("test_ci_tooling_mirror_gap._X", ...)` target-string mechanism — so the mechanism is proven to work by the sibling tests, the same "vacuous-alone, validated-by-siblings" pattern flagged as a lesson on the prior task this session. (2) whether the regex builder actually rejects near-miss counts, not just accepts the exact one — `test_regex_matches_its_own_exact_count` asserts BOTH `assertNotRegex` for n-1 and n+1, not just the positive case. (3) whether the real (slow) integration test's new call site actually exercises the new code path rather than accidentally always taking the `n<=0` branch — confirmed via the live nested run itself: `Ran 2609 tests ... OK (skipped=1)` locally (this dev environment's true expected count, matching `_expected_skip_count()`'s real unmocked output of 1 confirmed above) — the non-trivial `n>=1` branch of `_nested_ok_regex` is what actually matched, not the `n<=0` fallback. (4) full 2613-test suite run stayed green (`add-method`, `python3 -m unittest discover -s tooling -p 'test_*.py'` → `Ran 2613 tests ... OK`) — no collateral breakage elsewhere.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — no new I/O, no new subprocess/network call, no secret handling; the diff only reads interpreter introspection (`importlib.util.find_spec`, a bare `try/import`) and builds a `re.Pattern` from an integer — no injection surface.
2. Concurrency: CLEAR — pure, stateless, single-threaded helper functions; no shared mutable state, no new thread/process (the existing subprocess call site is unchanged in its own concurrency shape, only the assertion afterward changed).
3. Architecture: CLEAR — the fix stays entirely inside the one test file it diagnoses, matches the existing "small pure-logic helper + a slow real-integration test exercising it" split already used by this file (`_job_block`/`_materialize_run_block` are the same shape), no new cross-file coupling introduced.
Verdict: PASS
Residue: none
Binding: advisory — mechanical (a test-harness arithmetic fix, no method-defining decision; task carries no `risk: high`)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): CI's "Tooling tests (py 3.10)"/"(py 3.12)" jobs on future
pushes — both should go green with the `test_fresh_checkout_survives_test_job_sequence` assertion
now computing its tolerance per-interpreter instead of failing on the pre-existing tomllib/setuptools
gap; a red CI on this specific test again would mean a THIRD environment-conditional skip appeared
somewhere in the suite that `_expected_skip_count()` doesn't yet account for.

### Decisions (ADR)
- [AI] specify — chose compute an exact expected-skip-count from the interpreter's own tomllib/setuptools availability and require an EXACT match each run; rejected widen to an open `\(skipped=\d+\)` range (rejected — loses the anti-silent-regression guarantee the original task explicitly designed for) · hardcode a second literal like `skipped=(1|7)` (rejected — equally fragile the moment a third conditional skip appears or a runner's setuptools state differs) · pass `-v` to the nested subprocess and match skip reasons by text (rejected — unnecessarily changes the subprocess's own invocation/output shape for a problem countable without it)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with one refinement within the same contract's observable surface: the CONTRACT's inline `_expected_skip_count()` sketch (a bare `try/import`+`find_spec` check written directly in the function body) was factored into two named, individually-mockable seam functions (`_tomllib_available()`/`_setuptools_available()`) so `OkSummaryRegexTest` could inject each availability combination via `mock.patch` rather than needing to fake `sys.modules`/monkeypatch `importlib` internals — the summed formula and the two exposed names (`_expected_skip_count`, `_nested_ok_regex`) the contract actually binds are unchanged.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] if `test_packaging.py`'s `PyWheelTest` ever gains or loses a setuptools-gated test
  method (currently exactly 3), or a 7th component-pillar test file is ever added, this task's `+3`/
  `+6` literals inside `_expected_skip_count()` silently desync until someone re-derives them by hand
  — consider a follow-up that counts these programmatically (e.g. by importing the gated modules and
  counting `TestLoader().loadTestsFromModule` results) instead of a hand-maintained constant (evidence:
  the Least-sure flag surfaced at this task's own freeze named exactly this risk)

### Competency deltas
- [TDD · open] a mock-patched test can be vacuous in its OWN environment if the real (unmocked) value
  already matches the mocked expectation — always pair at least one "mock changes the outcome away from
  the real baseline" case among a group of mock-based tests, so the group as a whole proves the
  patching mechanism actually took effect rather than merely restating the ambient environment
  (evidence: `test_both_deps_present_computes_one` alone would pass even with a silently broken
  `mock.patch` target string in THIS dev environment, since the real unmocked `_expected_skip_count()`
  already returns 1 here — validated only because 3 sibling tests in the same class produce results
  (7, 4, 10) impossible without the mock genuinely working, recorded in this task's own refute-read)
- [ADD · open] a CI failure should be checked against run history (`gh run list`) before assuming it
  was caused by the commit under review — this task exists because a red check on PR #121 was traced
  to a PRE-EXISTING failure already present 2 commits earlier, not a regression from this session's
  own 2 fixes; skipping that history check would have wasted effort "fixing" the wrong commit or,
  worse, prompted reverting good work to chase a phantom regression (evidence: `gh run list --branch
  feat/artifact-trust` showed the identical `test_fresh_checkout_survives_test_job_sequence` failure
  at commit `e4d287d`, authored in the prior session before this session's 2 gitignore fixes existed)

