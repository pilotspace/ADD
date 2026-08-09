# TASK: fence-aware section slicer for words-exist guards

slug: fence-aware-section · created: 2026-06-07 · stage: mvp · autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- autonomy: auto — test-infrastructure refactor, engine untouched, no judgment surface;
     the bundle freeze stays human, as always. Wave context: v19 worker B. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: one fence-aware section slicer (`md_section.py`); the four guard files that slice prose at "\n## " import it
Framings weighed: a shared module whose terminator scan skips fenced lines (chosen) · keep per-file slicers and fix each (rejected: four copies of the same subtle scan is how the hazard shipped in the first place — single source, like sibling task engine_pin) · forbid "## " inside fences by lint instead (rejected: pushes the burden onto every future author; the wave-ledger workaround — ### headings in templates — already proved that convention-by-memory leaks)
Must:
<must>
  - `add-method/tooling/md_section.py` exposes `section(text: str, heading: str) -> str`
  - returns the slice from the first occurrence of `heading` (INCLUSIVE) up to — not including — the next line that starts with `## ` OUTSIDE a ``` fence; to end-of-text if no such line
  - lines starting with ``` toggle fence state; a `## ` line inside an open fence never terminates the slice (the hazard, closed)
  - `heading` absent -> returns "" (empty string, never an exception)
  - an unclosed fence scans to end-of-text — no crash, no truncation
  - the four slicing guard files (test_wave_ledger, test_audit_ci, test_intake_interview, test_review_checklist) route their section slicing through md_section.section; their own `"\n## "` split/find idioms are deleted
  - every existing assertion in those four suites stays green and unweakened — only the slicing mechanism moves, never a guard's teeth
</must>
Reject:
<reject>
  - a fenced "## " line terminating a slice -> "fenced_h2_truncates"  (the hazard test fails)
  - a leftover `"\n## "` slice idiom in any of the four guard files -> "slicer_not_single_source"  (sweep test fails)
  - any byte change to the three add.py engine copies -> "engine_touched"  (engine_pin guards; this task is tooling-tests only)
</reject>
After:
<after>
  - a template embedded in a guarded section may use real `## ` headings inside its fence without silently shrinking the guard's scan — the wave-ledger workaround (### headings forced into the WAVE.md template) becomes unnecessary for future sections
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ heading-INSIDE-a-fence mis-anchoring stays out of scope — lowest confidence as a scope cut, not a behavior: only the TERMINATOR becomes fence-aware, so a `## ` heading inside a fence can still match as the slice START; if wrong (it bites): cost is one more fence-state pass in the same module, importers unchanged — deliberate minimal scope, named here
  ⚠ heading inclusion is harmless to all four importers — the three inline-split sites previously EXCLUDED the heading; every downstream check is assertIn / line-prefix counting, where one extra heading line cannot flip a verdict; if wrong: one importer keeps a `[len(heading):]` strip — one-line cost
  - [x] ~~~ tildes-fenced blocks don't occur in the guarded skill files — only ``` fences (verified by grep before freeze)
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: basic slice — heading to next H2
  Given text with "## A" prose then "## B"
  When section(text, "## A") is called
  Then the slice starts with "## A", contains A's prose, and excludes "## B"

Scenario: a fenced H2 does not terminate (the hazard)
  Given a "## A" section whose body holds a ``` fence containing a "## Fake" line,
        prose AFTER the fence, then a real "## B"
  When section(text, "## A") is called
  Then the after-the-fence prose IS in the slice          # fenced_h2_truncates
  And "## B" is not

Scenario: missing heading returns empty
  Given text without the heading
  When section(text, "## Nope") is called
  Then "" is returned and no exception raised

Scenario: unclosed fence scans to end
  Given a "## A" section whose fence never closes, followed by a "## B" line
  When section(text, "## A") is called
  Then the slice runs to end-of-text (the still-open fence swallows "## B")
  And no exception is raised

Scenario: four importers, zero leftover idioms
  Given the four slicing guard files
  When their source is scanned
  Then each references md_section
  And none still contains a '\n## ' split/find slice      # slicer_not_single_source

Scenario: the four guards keep their teeth
  Given the refactored suites
  When the four suites run via the unittest loader
  Then all pass — same assertions, new slicing mechanism
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
MODULE add-method/tooling/md_section.py        (new; the ONLY slicer home)
  section(text: str, heading: str) -> str
    heading found    -> text[heading_start : next-unfenced-"## "-line)   (heading INCLUSIVE)
    no terminator    -> text[heading_start:]                              (to end)
    heading absent   -> ""                                                (never raises)
    fence rule: lines starting with ``` toggle state; "## " inside an open fence
    never terminates; an unclosed fence runs to end-of-text
  stdlib-only, pure function — no IO, no regex backtracking hazard
IMPORTERS (exactly these four, in-lane edits only)
  test_wave_ledger.py      — local _section body delegates to md_section.section
  test_audit_ci.py         — inline split at :149 replaced by md_section.section
  test_intake_interview.py — inline split at :55  replaced by md_section.section
  test_review_checklist.py — _section body delegates (keeps its `-> str | None`
    contract via `or None`); shared-file rule: this file is also touched by sibling
    task shared-engine-pin — this task owns ONLY the slicer lines + its import,
    never reformats or reorders
Schema: no engine change · no state.json change · no new dependency · tooling-tests only
```

Status: FROZEN @ v1 — approved by Tin (2026-06-08; one-approval bundle gate; terminator-only fence-awareness named as a deliberate scope cut at the freeze)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every contracted behavior has a test (6 scenarios → 6 tests); the four refactored suites stay green
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_basic_slice_heading_to_next_h2: arrange synthetic doc / act section() / assert inclusive start, body present, next section excluded
  - test_fenced_h2_does_not_terminate: arrange fence containing "## Fake" + after-fence prose / act / assert after-fence prose in slice, real next section out
  - test_missing_heading_returns_empty: arrange doc without heading / act / assert ""
  - test_unclosed_fence_scans_to_end: arrange never-closed fence / act / assert slice runs to end, no raise
  - test_four_importers_no_leftover_idiom: arrange the four file paths / act scan source / assert "md_section" present AND no '\n## ' split/find remains in each
  - test_four_guards_still_green: arrange unittest loader / act run the four suites / assert all pass
</test_plan>

Tests live in: `add-method/tooling/test_md_section.py` · MUST run red (missing implementation) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the four guards' ASSERTIONS never change — only the slicing mechanism moves; in `test_review_checklist.py` touch ONLY the `_section` body + the new import (sibling task owns the ENGINE_MD5 line).
Code lives in: `add-method/tooling/md_section.py` (new) + the four importer edits
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — own suite 6/6 (red 5F/1P → green, worker-run); integration on main after BOTH merges: full tooling suite 586 OK (the wave-close green)
- [x] coverage did not decrease — no test removed; four guard suites keep every assertion
- [x] no test or contract was altered during build — worker diff = md_section.py (new, 56 lines) + four in-lane importer edits; §3/§4 untouched post-freeze; heading-inclusion confirmed harmless (no strips needed, §1 ⚠2 resolved by evidence)
- [x] concurrency / timing safe — isolated worktree; D1 sync gate FIRED (same stale pool base d2d0825 → merged to f45342e, evidence verified == base before merge-back); declared-overlap file auto-merged cleanly across A's pin edit (3-way), both lanes verified intact
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib line scan, no IO, no regex
- [x] layering & dependencies follow CONVENTIONS.md — engine untouched (586-green includes the five pin guards); cherry-pick merge-back excluded all shared state
- [x] reviewed — auto-resolved under `autonomy: auto` (worker verdict PASS + orchestrator-verified commit scope, fork-base evidence, overlap diff, and the all-green integration suite); no security, concurrency, or architecture residue to escalate

### GATE RECORD
Outcome: PASS — auto-resolved (autonomy: auto), owner: v19 wave-1 worker B run + orchestrator integration Verify, 2026-06-08. Not a human signature: recorded on complete evidence per run.md; the human approval for this task was the bundle freeze.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the next guarded section that embeds a fenced template — does the author still reach for the ### workaround out of habit?
Spec delta for the next loop: none — the contract shipped as frozen (terminator-only scope cut stands until a fenced start-anchor actually bites); wave-level findings live in the v19 Wave log digest.

### Competency deltas
- [ADD · folded] CHANGE-REQUEST against streams.md "Wave ledger": the pre-spawn fork-base evidence cell is UNSATISFIABLE on a runner that creates the worktree AT spawn (Claude Code; proven 2/2 workers this wave — both forked a stale v17-era pool base), so `unverified_fork_base` must be allowed to execute at MERGE-time (worker step-0 sync echo, orchestrator-verified before merge-back) as a contracted alternative, not an undocumented deviation — the wave-ledger's own founding lesson (a check that exists only in prose never runs) recursing onto itself (evidence: v19 Wave log, D1 fired twice)
- [SDD · folded] `import md_section` (module reference) over `from md_section import section` — avoids shadowing local `section` variables in test_audit_ci/test_intake_interview; name-collision awareness extends to import style (evidence: worker B's build choice, zero collisions)
- [TDD · folded] the heading-inclusion ⚠ resolved by evidence, not argument — all four importers green with zero compensating strips; contracting the expected-harmless and letting the suite arbitrate beat pre-emptive compatibility shims (evidence: this task's §1 ⚠2 → §6)
