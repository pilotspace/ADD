# TASK: Grep-Binary-Agnostic Milestone-Exit Test

slug: grep-binary-agnostic-milestone-test · created: 2026-07-03 · stage: mvp
milestone: (none)
sensitivity: mechanical
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/tooling/test_seams_template_wiring.py:ThreeTreeParityTest.test_milestone_exit_grep_lists_all_3` — the milestone-exit parity assertion that shells out to the real `grep -cl` binary; `add-method/tooling/test_ci_tooling_mirror_gap.py:test_fresh_checkout_survives_test_job_sequence` — clones committed HEAD and re-runs the full suite, so it inherits the same failure as a cascading symptom, not a separate bug
Context (working folder): none beyond the two test files above — no config/data/docs touched
Honors (patterns / conventions): CONVENTIONS.md TDD discipline — the fix normalizes the test's assertion, never weakens what it checks (the invariant "all 3 tree paths matched" is unchanged)
Seams consulted: none cited — this is a test-parsing defect, not a scope-token or template seam
Anchors the contract cites: `subprocess.run(["grep", "-cl", LABEL, *paths])` invocation and its stdout-parsing line in `test_milestone_exit_grep_lists_all_3`
Issues/Risks (→ feed §1): BSD grep (macOS default `/usr/bin/grep` 2.6.0-FreeBSD) prints BOTH a `path:1` count line and a separate bare `path` line per match when `-c` and `-l` are combined; GNU grep (Linux CI) prints only the bare filename. `subprocess.run(["grep",...])` does its own PATH lookup and bypasses any shell alias/function — an earlier add-verify aside blaming a `ugrep` shell alias was investigated this session and found WRONG; it is a genuine BSD-vs-GNU binary behavior difference, confirmed by direct invocation
Related intent: seeded from add-advisor + skill-tree-compaction-audit spec-deltas — a pre-existing BSD-vs-GNU `grep -cl` local-only failure (green on CI) independently disclosed by 2 separate tasks [← add-advisor, skill-tree-compaction-audit]. Reconciliation note: the fix was implemented and committed ad hoc during the `reclaim-ticket-race` task's "fix all" cleanup pass (commit `5d0ce30`, 2026-07-04) before this task's own flow was formally advanced — this task is now being back-filled to match that already-shipped, already-verified reality, not to redo the work.
Ground SHA: `5d0ce30` (`git rev-parse --short HEAD`) — the fix commit itself; all cited symbols resolve as of this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: make `test_seams_template_wiring.test_milestone_exit_grep_lists_all_3` grep-binary-agnostic — assert on the set of matched filenames independent of `grep -cl` output format, or pin the grep binary in the subprocess call (from add-advisor spec-delta; duplicate finding also disclosed by skill-tree-compaction-audit, which additionally names a 2nd cascading failure: test_ci_tooling_mirror_gap.py::test_fresh_checkout_survives_test_job_sequence)
Framings weighed: normalize the test's own parsing to strip a trailing `:<digits>` count suffix before comparing (chosen) · pin the subprocess call to a specific grep binary/flags (e.g. `command -p grep` or GNU-only flag combo) — rejected, doesn't fix the same class of drift on any other flavor-diverging flag combo and adds an environment dependency · drop `-c` from the invocation entirely — rejected, the milestone's own exit criterion literally names `grep -cl`, changing the invocation changes what's being verified
Must:
<must>
  - test_milestone_exit_grep_lists_all_3 passes identically under BSD grep (macOS /usr/bin/grep) and GNU grep (Linux CI) without weakening what it asserts (all 3 template tree paths matched)
  - the fix touches only test-parsing logic — the underlying invariant (grep -cl, as the milestone's exit criterion names it) is unchanged
</must>
Reject:
<reject>
  - a grep flavor's stdout shape is misread as "0 matches" or "wrong path" -> the test must still fail loudly on an actual non-match, not silently pass by over-normalizing
</reject>
After:
<after>
  - the test suite is green on both this machine's BSD grep and CI's GNU grep, with no behavior gap between the two environments
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the two grep flavors' `-cl` output only ever differs by the presence/absence of a trailing `:<digits>` count suffix (no other divergent shape exists across common grep implementations) — lowest confidence because only BSD 2.6.0-FreeBSD and GNU (CI) were actually observed; if wrong: a third flavor (e.g. busybox grep, ripgrep-as-grep) could format differently and slip past the `re.sub(r":\d+$", "", line)` normalization undetected
  - [x] the fresh-checkout cascading failure (test_ci_tooling_mirror_gap.py) is the SAME root cause, not an independent bug — confirmed: it clones committed HEAD and re-runs this same test, so fixing the parsing here also fixes that cascade once committed
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: BSD grep -cl output parses correctly   # M1
  Given macOS's default /usr/bin/grep (BSD 2.6.0-FreeBSD) runs `grep -cl LABEL path1 path2 path3`
  When the test parses stdout for matched filenames
  Then all 3 paths are recognized as matches despite BSD's extra "path:1" count line
  And the assertion still checks the same invariant (all 3 tree paths matched)

Scenario: GNU grep -cl output parses correctly   # M1
  Given Linux CI's GNU grep runs the identical `grep -cl LABEL path1 path2 path3` invocation
  When the test parses stdout for matched filenames
  Then all 3 paths are recognized as matches from GNU's bare-filename-only output
  And behavior is identical to the BSD case above — no environment-specific branching

Scenario: a genuine non-match still fails loudly   # R1
  Given one of the 3 template tree paths does NOT contain LABEL (a real drift, not a parsing artifact)
  When the test parses stdout under either grep flavor
  Then the assertion fails with the missing path named in the message
  And no over-normalization silently absorbs the real gap
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION test_milestone_exit_grep_lists_all_3()   body: { grep binary flavor: BSD | GNU }
  invariant -> matched == {str(p) for p in TMPL_COPIES}   # all 3 tree paths recognized regardless of flavor
  parsing   -> raw_lines = stdout.splitlines(); matched = {re.sub(r":\d+$", "", line) for line in raw_lines}
  4xx (real non-match) -> AssertionError naming the raw output, not silently absorbed
Schema: no data/schema touched — pure test-assertion parsing logic
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin Dang (retroactive: reconciling already-shipped, already-verified work — commit `5d0ce30` landed this session under the user's explicit "fix all" authorization, before this task's own flow was formally advanced; per add-advisor guidance this is pure bookkeeping, no fresh gate needed)
Least-sure flag surfaced at freeze: [spec] the ⚠ §1 assumption — the BSD/GNU output-shape normalization is only proven against 2 observed grep flavors (BSD 2.6.0-FreeBSD, GNU/CI); a third flavor with a different divergent shape could slip past undetected. Cost if wrong: a future CI-only or local-only false-green on this same test, requiring a repeat of this diagnostic pass. [test] the real-subprocess integration test never itself exercises a genuine non-match on this machine (all 3 real template trees currently match) — the fixed vacuous-match defect (BSD `path:0`) is guarded solely by a synthetic unit test, not the integration test the milestone's own exit criterion names. Cost if wrong: a future edit to the parsing helper could regress unnoticed by the integration path alone.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — single existing test, parsing-logic fix only
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_milestone_exit_grep_lists_all_3: arrange 3 template tree paths + LABEL / act shell out to real `grep -cl` / assert matched set equals all 3 paths regardless of BSD-vs-GNU output shape + assert a real non-match still fails loudly · covers: M1, R1
  - test_fresh_checkout_survives_test_job_sequence (test_ci_tooling_mirror_gap.py): arrange a fresh clone of committed HEAD / act re-run the full suite in that clone / assert the cascading failure resolves once the fix above is committed · covers: M1 (cascade)
</test_plan>

Tests live in: `add-method/tooling/test_seams_template_wiring.py`, `add-method/tooling/test_ci_tooling_mirror_gap.py` (pre-existing files, no new test file) · confirmed RED before the fix — this session reproduced `peak`-style failure via direct `/usr/bin/grep` invocation on this machine (BSD 2.6.0-FreeBSD), matching the pre-existing local-only failure both add-advisor and skill-tree-compaction-audit had independently disclosed.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/test_seams_template_wiring.py`
Strategy (ordered batches): 1. reproduce RED against real BSD grep (not a shell alias) · 2. normalize stdout parsing to strip a trailing `:<digits>` count suffix before comparing · 3. widen the assertion failure message to include raw output for future debuggability · 4. confirm GREEN locally + verify the fresh-checkout cascade (test_ci_tooling_mirror_gap.py) resolves once committed

Persona (optional): methodology-engine-dev — engine/tooling test discipline
Known-problem fixes: an earlier add-verify aside had misattributed this to a `ugrep` shell alias → planned fix: verify the actual binary invoked by `subprocess.run` (does its own PATH lookup, bypasses shell aliases/functions) before touching any code, so the real BSD-vs-GNU root cause is fixed rather than a phantom shell-config issue
Strategy actually used: DIVERGED from the plan reconciled from commit 5d0ce30 — an add-verify refute-read (this session) found the `re.sub(r":\d+$", "", line)` normalization vacuous: BSD grep prints "path:0" for a genuine NON-match, which the suffix-strip cannot distinguish from a real match, silently absorbing a real regression on this test's own platform. Empirically confirmed via direct `/usr/bin/grep` invocation (seeded a real non-matching file — got "nomatch.txt:0", stripped to "nomatch.txt", indistinguishable from a match). Fixed by replacing the strip with `_parse_grep_cl_matches()`, a pure helper that only treats a ":N" suffix as a BSD count line when N parses as an int > 0; added 3 direct unit tests (`GrepClParsingTest`) covering GNU-bare, BSD-count+bare, and the BSD-zero-count exclusion regression. Re-verified green (both the helper's unit tests and the real subprocess integration test).
Safety rule (feature-specific): must not weaken what the test verifies — the invariant (all 3 tree paths matched) is unchanged; only the output-shape parsing is normalized
Code lives in: `add-method/tooling/test_seams_template_wiring.py`
Constraints: do NOT change any test's asserted invariant or the contract; allow-list packages only (stdlib `re`, already imported); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — targeted: `test_seams_template_wiring.py` 27/27, `test_ci_tooling_mirror_gap.py` 12/12; full tooling suite discover run completed exit code 0 (background run, ~2500 tests, per repo convention of not blocking synchronously on the full suite)
- [x] coverage did not decrease — 3 NEW unit tests added (`GrepClParsingTest`), 0 removed
- [x] no test or contract was altered during build — the invariant asserted by `test_milestone_exit_grep_lists_all_3` is unchanged (all 3 tree paths matched); only its parsing helper changed, plus new tests added
- [x] the green was EARNED, not gamed — TWO rounds of adversarial refute-read: round 1 (add-verify) found the FIRST fix attempt (bare `re.sub` suffix-strip) vacuous — it could not distinguish BSD grep's genuine-non-match `path:0` line from a real match, confirmed empirically. Round 2 (add-verify, after the corrected `_parse_grep_cl_matches` helper) verdict: EARNED — confirmed the `:0` case is now correctly excluded (falls into the count branch, fails `>0`, not re-added by the else), confirmed against the real BSD binary, confirmed the new unit test is non-vacuous
- [x] concurrency / timing of the risky operation is safe — n/a, no concurrency in scope
- [x] no exposed secrets, injection openings, or unexpected dependencies — n/a, test-parsing logic only, stdlib only (no new imports)
- [x] layering & dependencies follow CONVENTIONS.md — pure helper function, no IO, matches existing test-file conventions
- [x] a person reviewed and approved the change — Tin Dang authorized this reconciliation pass via "fix all" → "All 7 backlog tasks + reconcile + JS twin"; sensitivity: mechanical + autonomy: auto permits AI auto-resolution on complete, non-residue evidence per this project's own advisor-gate-relax convention

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] `test_milestone_exit_grep_lists_all_3` passes on this machine's real BSD grep (not mocked) — confirmed by direct `python3 -m unittest` run, and by the earlier standalone `/usr/bin/grep -cl` reproduction showing exact raw output shape
- [x] a genuine non-match is NOT silently absorbed — confirmed by `test_parse_grep_cl_matches_excludes_bsd_zero_count`, which asserts `assertNotIn("nomatch.txt", ...)` against a synthetic BSD-shaped `path:0` line

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_parse_grep_cl_matches` is referenced by both `test_milestone_exit_grep_lists_all_3` (real subprocess call) and all 3 `GrepClParsingTest` methods (synthetic input) — no orphaned symbol
- [x] DEAD-CODE (code) — no unused symbol introduced; the old `re.sub(r":\d+$", ...)` inline expression was fully replaced, not left dangling
- [ ] SEMANTIC (prose / non-code) — n/a, this task is code/test-only

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `test_milestone_exit_grep_lists_all_3` and `_parse_grep_cl_matches` both confirmed present and passing at time of this gate (post-fix, uncommitted working tree)
- [x] no anchor moved/renamed since Ground SHA — the function was extended (new helper added, call site updated in place), not moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED (on the second round — round 1 was NOT-EARNED and drove a real fix, not a rubber stamp)
By: agent ab3b6fa1769f32376 (round 1, NOT-EARNED, found the `:0` vacuous-match defect) → agent ad769a68dbe2cb357 (round 2, EARNED, confirmed the corrected `_parse_grep_cl_matches` helper closes it) · adversarially checked: whether the suffix-strip/parse could misclassify a genuine non-match as a match (it could, round 1; fixed and reconfirmed, round 2), whether the fix is overfit to exactly-observed flavors, whether the new unit tests are non-vacuous (verified by reasoning through assertions + independently re-running the real BSD binary)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: agent ad769a68dbe2cb357 (add-verify, round 2)
1. Security: CLEAR — test-parsing only, no prod code touched, no new dependency
2. Concurrency: CLEAR — n/a, no concurrent operation in scope
3. Architecture: CLEAR — pure helper function, correctly wired, no dead code
Verdict: PASS
Residue: none — noted (non-blocking) observation: the real-subprocess integration test (`test_milestone_exit_grep_lists_all_3`) doesn't itself exercise the `:0` path since all 3 real template trees currently match; the synthetic unit test (`test_parse_grep_cl_matches_excludes_bsd_zero_count`) is the sole guard for the fixed defect — acceptable, worth remembering if this helper is touched again
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (via standing "fix all" → "All 7 backlog tasks + reconcile" authorization) · date: 2026-07-04

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): re-check `test_milestone_exit_grep_lists_all_3` + `GrepClParsingTest` on any future grep-invocation change; watch for a 3rd grep flavor (busybox/toybox/ripgrep-as-grep) appearing in a future CI runner image, which the §1 ⚠ assumption flags as untested.

### Decisions (ADR)
- [AI] chose a pure, independently-unit-testable `_parse_grep_cl_matches` helper over a bare inline `re.sub` strip, specifically so the BSD `:0` non-match case could be asserted directly without needing a real non-matching fixture in the integration test (§5 BUILD)
- [AI] rejected pinning the subprocess call to a specific grep binary/GNU-only flags — dodges the immediate bug but reintroduces an environment dependency without fixing the underlying parsing assumption (§1 SPECIFY, Framings weighed)

### Spec delta
- [SPEC · carried] `test_milestone_exit_grep_lists_all_3` never itself exercises the BSD `:0` non-match path (all 3 real template trees currently match) — the fixed defect is guarded solely by the synthetic `GrepClParsingTest` unit test, not the integration test the milestone's own exit criterion names (evidence: round-2 refute-read, agent ad769a68dbe2cb357) [carried: low-value/low-risk right now — the synthetic GrepClParsingTest already covers the actual defect; revisit only if a BSD CI runner is added or the integration test's own coverage becomes a release blocker]

### Competency deltas
- [TDD · folded] a "fix the flaky test" pass should default to extracting parsing/comparison logic into a small pure helper BEFORE patching inline — this makes the actual defect unit-testable with synthetic edge-case input (a genuine non-match), instead of relying only on the real integration path, which may never exercise that edge case in the current repo state (evidence: round-1 refute-read caught a vacuous fix that an integration-only test run had already shown "green") [folded foundation-version 64]
- [ADD · folded] a mechanical/low-risk reconciliation task (backfilling TASK.md for already-shipped work) still surfaced a real, previously-undetected defect in that shipped work — reconciliation is not pure paperwork; a genuine refute-read against already-merged code caught a bug the original ad hoc fix (commit 5d0ce30) had missed, requiring a follow-up correction before Verify could record PASS (evidence: this task) [folded foundation-version 64]
