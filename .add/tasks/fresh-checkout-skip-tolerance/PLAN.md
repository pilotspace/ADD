# TASK: Tolerate the expected recursion-guard self-skip in the fresh-checkout suite check

slug: fresh-checkout-skip-tolerance · created: 2026-07-01 · stage: mvp
milestone: traceability-ids
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/test_ci_tooling_mirror_gap.py:FreshCheckoutSurvivesTestJob.test_fresh_checkout_survives_test_job_sequence` (committed `c22a43c`, this session's `ci-tooling-mirror-gap` task) — clones the repo, checks out HEAD, runs the real materialize step, then runs the FULL suite inside the clone with `_ADD_CI_MIRROR_GAP_NESTED=1` set on that subprocess only. That same test file's OWN recursion guard (`if os.environ.get("_ADD_CI_MIRROR_GAP_NESTED") == "1"): self.skipTest(...)`) is rediscovered inside the nested run and self-skips — deterministically producing exactly 1 skipped test every time the nested suite executes for real. The current assertion `self.assertRegex(combined, r"(?m)^OK\s*$", ...)` requires a BARE `OK` line with zero skips, which this structural self-skip can never satisfy — confirmed via isolated re-run today (`python3 -m unittest test_ci_tooling_mirror_gap.FreshCheckoutSurvivesTestJob -v`): fails every time git+npm are available, with the nested run's own combined output ending in `OK (skipped=1)`.
Context (working folder): none beyond the one test file — a pure test-assertion fix, no production code, no CI YAML, no other test file touched.
Honors (patterns / conventions): the SAME test file's own documented rationale for `assertRegex` over a loose substring check — "exact zero-failures/errors, not a loose substring check" — this fix preserves that strictness for any UNEXPECTED skip/failure/error, it only carves out the ONE specific, structurally-guaranteed self-skip.
Anchors the contract cites: `add-method/tooling/test_ci_tooling_mirror_gap.py:198` (the `assertRegex` line and its regex literal).

---

## 1 · SPECIFY — the rules

Feature: `test_fresh_checkout_survives_test_job_sequence`'s bare-`OK` assertion tolerates the ONE structurally-guaranteed recursion-guard self-skip, while still failing on any other skip/failure/error.
Must:
  - the assertion accepts a nested-suite summary of exactly `OK` OR exactly `OK (skipped=1)` (the recursion guard's own expected self-skip), nothing else.
Reject:
  - a nested-suite summary reporting any failure or error (e.g. `FAILED (failures=1)`) -> "suite_not_green"
  - a nested-suite summary reporting more than 1 skip (e.g. `OK (skipped=2)`) -> "unexpected_skip"
Accept: Given the nested clone's full suite runs for real (git+npm available), When its own recursion guard self-skips exactly once, Then the outer assertion passes; Given the same run instead reports any failure/error or more than 1 skip, Then the outer assertion still fails.
Assumptions: ⚠ exactly 1 is the right tolerance (not "any N") — lowest confidence because a future test-suite change could add a second, unrelated legitimate skip inside the same nested run, which this fix would then wrongly reject; if wrong: a future legitimate skip would need this same fix's tolerance widened by one more explicit case, not a silent "any skip count" loosening (kept narrow on purpose so an unexpected skip still surfaces).

---

## 3 · CONTRACT — freeze the shape

```
fresh-checkout-skip-tolerance — frozen shape @ v1

add-method/tooling/test_ci_tooling_mirror_gap.py — FreshCheckoutSurvivesTestJob.
test_fresh_checkout_survives_test_job_sequence, the `assertRegex` line (currently
line 197-198): the pattern

    r"(?m)^OK\s*$"

becomes

    r"(?m)^OK(?: \(skipped=1\))?\s*$"

— matches a bare `OK` line OR exactly `OK (skipped=1)` (the recursion guard's own
structurally-guaranteed self-skip), nothing else. The assertion message stays the
same wording (still names "bare 'OK' summary" for a human reading a failure, since
the skip-1 case is the expected/tolerated shape, not a new success message to word
differently). No other line in the test changes; `ran_match` / `assertGreater`
checks below it are untouched.

Invariants: no other assertion in this test loosens; a run reporting ANY failure,
ANY error, or 2+ skips still fails exactly as before; the rest of
test_ci_tooling_mirror_gap.py (CiTestJobMaterializes, PublishGuardJobMaterializes,
SeamAuditUntouched) receives no edits; full add-method suite green afterward,
including this test itself running for real (git+npm available).
```

`Least-sure flag surfaced at freeze:` [test] whether tolerating exactly `(skipped=1)` (vs. a looser "any skip count is fine as long as 0 failures/errors") is the right narrowness — why: a stricter carve-out is safer (won't mask a NEW unrelated skip introduced later) but is also the more brittle choice if the suite's skip count for other, unrelated reasons ever legitimately becomes 2 inside the same nested run; if wrong: a future legitimate second skip would need this same regex widened by one more explicit alternative, a small, visible follow-up — not a silent failure.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: `OkSummaryRegexTest` (4 tests, in `test_ci_tooling_mirror_gap.py` itself — fast, pure-logic coverage decoupled from the expensive clone-based integration test it backs) — test_accepts_bare_ok / test_accepts_the_recursion_guards_own_expected_self_skip / test_rejects_a_failure_summary / test_rejects_more_than_one_skip, each asserting against a module-level `_NESTED_OK_SUMMARY_RE` constant (not yet extracted).
Tests live in: `add-method/tooling/test_ci_tooling_mirror_gap.py` · confirmed red (4 errors: `NameError: name '_NESTED_OK_SUMMARY_RE' is not defined` — the right reason, no implementation exists yet) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/test_ci_tooling_mirror_gap.py`
Strategy & known-problem fixes: 1. extract a module-level `_NESTED_OK_SUMMARY_RE = re.compile(r"(?m)^OK(?: \(skipped=1\))?\s*$")` constant near `_REQUIRED_MATERIALIZE_LINES` 2. rewire the existing `assertRegex` call in `test_fresh_checkout_survives_test_job_sequence` to use the constant instead of its inline literal 3. run `OkSummaryRegexTest` to green 4. run the real (non-nested) `FreshCheckoutSurvivesTestJob` to confirm it now passes for real, not just via the pure-logic test. Known trap: widening the regex to tolerate ANY skip count would silently mask a future unrelated failure inside the nested run — dodged by anchoring the tolerance to the literal `(skipped=1)` text, not a bare `\(skipped=\d+\)`.
Strategy actually used: as planned.
Code lives in: `add-method/tooling/test_ci_tooling_mirror_gap.py`   ·   Constraints: change no OTHER test or the contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full add-method suite: 2586 tests, bare `OK` (was 2582 pre-build; +4 for `OkSummaryRegexTest`); `git diff --stat` confirms only `test_ci_tooling_mirror_gap.py` changed.
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic — `OkSummaryRegexTest`'s 4 cases are independent positive/negative pairs (bare OK / skip=1 accepted; a failure summary / skip=2 rejected) using `assertRegex`/`assertNotRegex` directly against sample strings, not against the real subprocess output, so they can't be gamed by the subprocess's own behavior; the real `FreshCheckoutSurvivesTestJob` integration test (previously failing) now passes for real, confirming the fix works end-to-end, not just against the isolated unit tests.
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — pure regex/test-assertion change, no new dependency, no secret, no I/O beyond what the pre-existing test already did. CLEAR.

Build expectations (from §1 Accept + §3 CONTRACT): the nested-run summary `OK (skipped=1)` now passes `test_fresh_checkout_survives_test_job_sequence` — confirmed by running that exact test in isolation (`python3 -m unittest test_ci_tooling_mirror_gap.FreshCheckoutSurvivesTestJob -v` → `ok`, ~72s, real git clone + npm ci + nested suite run) and by the full suite reporting bare `OK` (2586/2586) afterward. A synthetic `FAILED (failures=1)` or `OK (skipped=2)` still fails the regex (confirmed by `OkSummaryRegexTest`'s 2 negative cases) — the narrowing did not silently widen past its declared scope.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under `autonomy: auto` — no residue: no security/concurrency/architecture finding; self-reviewed, mechanical single-regex change) · date: 2026-07-01

