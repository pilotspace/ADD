# TASK: _detail_body leaves fenced blocks unwrapped so contracts round-trip

slug: fence-safe-wrap · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fence-safe wrap in the phase drill-down (P4 of the per-phase report review)
Framings weighed: fence-aware verbatim emit in _detail_body (chosen) · skip-wrap whole §3
  only (rejected: gherkin in §2 and fences in any §body break the same way) · markdown
  renderer (rejected: a terminal dashboard, not a md pipeline — minimalism)
Must:
  - A line whose lstrip() starts with ``` TOGGLES fence state; the delimiter lines
    themselves and EVERY line inside an open fence render VERBATIM: indent prefix + raw
    bytes — never word-wrapped, never whitespace-collapsed, even when longer than width.
  - Internal runs of spaces inside fenced lines survive (aligned contract columns).
  - Prose lines OUTSIDE fences keep today's soft-wrap behavior byte-for-byte.
  - An unclosed fence runs verbatim to the end of the §body (fail-open: better an
    unwrapped paragraph than a reflowed contract).
  - Blank lines inside a fence stay "" (as today); fence state resets per §body.
Reject:
  - any §body content -> never a crash; drill-down exit stays 0
  - any write during the drill-down -> impossible (v9 purity carried)
After:
  - Copy-paste of the §3 contract block from `report <ms> <task>` round-trips after
    stripping the uniform 3-space indent; no mid-token wrap exists anywhere in a fence.
Assumptions — least-sure first:
  ⚠ the uniform 3-space indent counts as "round-trips" (strip-indent round-trip) — least
    sure because the exit criterion says byte-identical; if the human wants true zero-indent
    paste inside fences, this contract gets re-cut (cost: one render decision, small).
  - [ ] ``` is the only fence grammar in real §bodies — verified: 210 fences across all
    task files, zero `~~~`, all at column 0 (lstrip handles indented ones anyway).
  - [ ] >width verbatim lines may visually wrap in the terminal — bytes win over looks;
    no existing test pins soft-wrap of over-long lines (verified test_phase_detail.py).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: fenced contract line never wraps
  Given a §3 body holding a fenced line longer than the render width
  When report <ms> <task> renders the drill-down
  Then that line appears as ONE output line: indent + raw bytes, mid-token intact
  And the exit code is 0

Scenario: aligned columns survive
  Given a fenced line containing runs of multiple spaces (column alignment)
  When the drill-down renders
  Then every internal space run is byte-preserved

Scenario: prose outside fences still soft-wraps
  Given an over-long prose line in the same §body, outside any fence
  When the drill-down renders
  Then it soft-wraps across 2+ lines exactly as today
  And fenced content in the same body is untouched

Scenario: delimiters render verbatim
  Given a body with a ```gherkin opener and a bare ``` closer
  When the drill-down renders
  Then both delimiter lines appear verbatim (with the indent prefix)

Scenario: unclosed fence fails open
  Given a body whose fence is never closed
  When the drill-down renders
  Then everything after the opener renders verbatim to the §body end
  And no crash, exit 0

Scenario: blank lines inside a fence stay blank
  Given a fenced block containing an empty line
  When the drill-down renders
  Then that line renders as "" (no indent residue)

Scenario: drill-down stays pure
  Given any of the bodies above
  When report <ms> <task> and its --json twin run
  Then the .add file set and state.json bytes are unchanged
  And every invocation exits 0
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_detail_body(body, width) -> list[str]        # signature UNCHANGED — single caller
                                              # render_task_detail needs no edit
  # fence state: starts CLOSED per §body; a line whose lstrip() startswith "```"
  #   toggles it; delimiter lines get verbatim treatment themselves
  # inside a fence (incl. delimiters): emit indent + raw — byte-verbatim, no wrap,
  #   no whitespace collapse, even when len(indent + raw) > width
  # outside a fence: today's behavior byte-for-byte (blank -> "", fits -> indent + raw,
  #   over-long -> soft-wrap on spaces preserving leading indent)
  # unclosed fence: verbatim to end of §body (fail-open)
CLI · JSON · render_task_detail · task_phases: all unchanged · purity carried (v9)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front; strip-indent round-trip accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must (verbatim long line · space runs · prose regression ·
delimiters · unclosed fence · blank-in-fence) + purity — one test per scenario,
asserting rendered output lines, never _detail_body internals.
Plan (one test per scenario):
  - test_fenced_long_line_never_wraps: 100-char fenced line @ width 72 → ONE line,
    bytes intact mid-token
  - test_fenced_space_runs_survive: "a    b      c" inside fence → byte-preserved
  - test_prose_still_soft_wraps: over-long prose in same body → 2+ lines (regression guard)
  - test_delimiters_verbatim: ```gherkin opener + ``` closer both present
  - test_unclosed_fence_fails_open: opener, no closer → verbatim tail, exit 0
  - test_blank_inside_fence: empty fenced line → "" in output
  - test_drilldown_pure: file set + state hash unchanged across text + --json, exits 0

Tests live in: `add-method/tooling/test_fence_wrap.py` (suite root, like every prior
tooling task) · MUST run red (fenced lines currently re-wrapped) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): prose soft-wrap outside fences must stay byte-identical —
the regression guard pins it; only fenced content changes treatment.
Code lives in: `add-method/tooling/add.py` (canonical) → synced to `.add/tooling/add.py`
and `add-method/src/add_method/_bundled/tooling/add.py` (3-tree md5 parity).
Constraints: do NOT change any test or the contract; stdlib only; touch-boundary =
`_detail_body` in add.py ×3 + the new test file; no caller/CLI/JSON changes.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 362/362 (355 prior + 7 new), `add.py check` 194/0 (4 pre-existing warns)
- [x] coverage did not decrease — 7 tests added, none removed/weakened; red 4-for-the-right-reason
      (mid-token wrap + space collapse visible in the failing render) + 3 green-by-design
      regression guards (delimiters · blank-in-fence · purity)
- [x] no test or contract was altered during build — §3 untouched post-freeze; the only code
      change is inside `_detail_body` (signature unchanged, single caller untouched)
- [x] concurrency / timing safe — pure text transform, no IO added, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; the
      change renders already-read text verbatim instead of re-wrapping it; no new read, no
      write, nothing on this line to escalate
- [x] layering & dependencies follow conventions — fence state is local to `_detail_body`;
      3-tree md5 parity c607d214161911af7d700e3314dd3191 ×3
- [x] a person reviewed and approved the change — Tin approved the frozen contract
      (one-approval front, 2026-06-05); gate auto-resolved on complete evidence per
      `autonomy: auto` (no deviation, no residue, security line genuinely empty)

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence — all green · loops dry · no residue ·
no deviation: build touched exactly `_detail_body` ×3 trees + the new test file)
Reviewed by: auto-gate under `autonomy: auto` · contract approved by Tin · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): any drill-down render where a fence visually breaks
(would mean a fence grammar the toggle misses — e.g. `~~~` arriving in real bodies);
copy-paste complaints about the 3-space indent (would reopen the zero-indent flag).
Spec delta for the next loop: fenced content is now byte-faithful end-to-end (decide
digest §3 verbatim + drill-down fence-safe); the remaining presentation gap is prose-only
wrap, which is intentional.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [TDD · folded] making a red test fail for the RIGHT reason sometimes needs the fixture to
    exceed a hidden threshold (lines under the render width were already verbatim — only
    over-width lines exposed the wrap/collapse); name the threshold in the test constants
    (evidence: LONG_FENCED/SPACED deliberately > width 72, 4 red as predicted)
