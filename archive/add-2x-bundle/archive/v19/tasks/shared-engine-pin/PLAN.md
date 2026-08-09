# TASK: one ENGINE_MD5 source, five importers

slug: shared-engine-pin · created: 2026-06-07 · stage: mvp · autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- autonomy: auto — test-infrastructure refactor, engine untouched, no judgment surface;
     the bundle freeze stays human, as always. Wave context: v19 worker A. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a single `ENGINE_MD5` source module; the five pin-bearing suites import it
Framings weighed: a constant in a sibling module `engine_pin.py` (chosen) · recompute the hash dynamically (rejected: a pin that recomputes is vacuous — it can never catch drift, which is the pin's whole job) · environment/config file (rejected: a test constant is code, not config; one more parse path is one more failure path)
Must:
<must>
  - `add-method/tooling/engine_pin.py` exposes `ENGINE_MD5`, a hard-coded 32-hex string LITERAL — the recorded pin, never computed
  - the literal equals the md5 of all three engine copies (canonical `add-method/tooling/add.py` · dogfood `.add/tooling/add.py` · bundle `_bundled/tooling/add.py`) at the commit that lands this task
  - the five pin-bearing suites (test_getting_started_spine, test_installer_handoff, test_release_1_1_0, test_review_checklist, test_skill_onramp) bind `ENGINE_MD5` via `from engine_pin import ENGINE_MD5` — their own hash literals are deleted
  - single-source sweep: NO tooling .py file other than engine_pin.py assigns a 32-hex literal to a name containing `ENGINE_MD5` — every *.py, not just test files, so a pin cannot hide in a helper module
  - `engine_pin` imports cwd-independently: with the tooling dir on sys.path, the import succeeds from ANY working directory (proven by subprocess, the way the full-suite runner loads modules)
  - all five existing `test_engine_untouched` guards stay green and unweakened — same assertions, same paths, only the constant's home moves
</must>
Reject:
<reject>
  - a second hard-coded engine pin appearing anywhere in tooling tests -> "pin_not_single_source"  (sweep test fails)
  - engine_pin computing its value from add.py at runtime -> "vacuous_pin"  (literal-source test fails)
  - any byte change to the three add.py engine copies -> "engine_touched"  (the five guards themselves — this task moves their constant, never their teeth)
</reject>
After:
<after>
  - a legitimate engine change re-aims exactly ONE line (`engine_pin.py`) instead of five hand-edits — the stale-guard sweep (dd5b665, wave-status-hint) shrinks to a single edit
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ plain `import engine_pin` resolves for every runner of these suites — lowest confidence because the suites are run both as `python3 -m unittest <mod>` from `add-method/tooling/` AND via the full-suite runner; if a runner imports from another cwd the sibling import breaks; if wrong: cost is a sys.path shim in engine_pin importers — small, but it would show up as 5 red suites immediately
  ⚠ no consumer outside tooling reads the five files' `ENGINE_MD5` attribute — if wrong: that consumer keeps working anyway (the name survives via the import); cost ≈ zero, flagged for honesty
  - [x] the pin value does not change in this task — engine untouched, so the moved literal is byte-identical to today's "1082fd0fbc353e855fd1d7f983718dfb"
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the single source exists and is a literal
  Given the tooling directory
  When engine_pin is imported
  Then it exposes ENGINE_MD5 matching ^[0-9a-f]{32}$
  And the module SOURCE contains that value as a string literal   # vacuous_pin
  And the module source never reads add.py                        # vacuous_pin

Scenario: the pin matches all three engine copies
  Given the three add.py engine copies (canonical · dogfood · bundle)
  When each file's md5 is computed
  Then every digest equals engine_pin.ENGINE_MD5

Scenario: five importers, zero local literals
  Given the five pin-bearing suite files
  When their source is scanned
  Then each contains "from engine_pin import ENGINE_MD5"
  And none assigns a 32-hex string literal to an ENGINE_MD5 name   # pin_not_single_source

Scenario: sweep — no second pin anywhere
  Given EVERY *.py under add-method/tooling/ (tests and helpers alike)
  When scanned for `ENGINE_MD5… = "<32-hex>"` assignments
  Then zero matches outside engine_pin.py                          # pin_not_single_source

Scenario: the pin imports from any cwd
  Given a subprocess whose cwd is an unrelated temp dir, with the tooling dir on sys.path
  When `import engine_pin` runs
  Then it succeeds and prints the 32-hex pin   # closes ⚠1 with evidence, not precedent

Scenario: the five guards keep their teeth
  Given the refactored suites
  When the five suites run
  Then all pass, and test_engine_untouched still asserts digest == ENGINE_MD5 per path   # engine_touched stays catchable
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
MODULE add-method/tooling/engine_pin.py        (new; the ONLY pin home)
  ENGINE_MD5: str — hard-coded 32-hex literal "1082fd0fbc353e855fd1d7f983718dfb"
  no imports of hashlib, no file reads — a constant, nothing else
IMPORTERS (exactly these five, in-lane edits only)
  test_getting_started_spine.py · test_installer_handoff.py · test_release_1_1_0.py
  · test_review_checklist.py · test_skill_onramp.py
  each: local `ENGINE_MD5 = "<hex>"` line REPLACED by `from engine_pin import ENGINE_MD5`
  no other line of these files moves (shared-file rule: test_review_checklist.py is
  also touched by sibling task fence-aware-section — this task owns ONLY the pin
  line + its import, never reformats or reorders)
GUARANTEES (test-pinned)
  sweep scope: EVERY add-method/tooling/*.py except engine_pin.py — zero 32-hex
  ENGINE_MD5 assignments anywhere else
  import: cwd-independent given tooling dir on sys.path (subprocess-proven)
Schema: no engine change · no state.json change · no new dependency · tooling-tests only
```

Status: FROZEN @ v1 — approved by Tin (2026-06-08; one-approval bundle gate; ⚠1 import-mechanics + sweep-scope hardened at the human's change-request before the freeze)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every contracted behavior has a test (6 scenarios → 6 tests); the five refactored suites stay green
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_pin_module_is_literal_source: arrange import engine_pin + read its source / act / assert ENGINE_MD5 matches ^[0-9a-f]{32}$, appears as a literal in source, source has no hashlib/read of add.py
  - test_pin_matches_all_three_engines: arrange three engine paths / act md5 each / assert all == engine_pin.ENGINE_MD5
  - test_five_importers_no_local_literals: arrange the five file paths / act scan source / assert "from engine_pin import ENGINE_MD5" present AND no 32-hex assignment to an ENGINE_MD5 name in each
  - test_sweep_no_second_pin: arrange ALL tooling *.py (minus engine_pin.py) / act regex scan / assert zero ENGINE_MD5-literal assignments
  - test_pin_importable_from_any_cwd: arrange subprocess in temp-dir cwd with tooling on sys.path / act import engine_pin / assert exit 0 + 32-hex stdout
  - test_five_guards_still_green: arrange unittest loader / act run the five suites' engine-pin test cases / assert all pass
</test_plan>

Tests live in: `add-method/tooling/test_shared_engine_pin.py` · MUST run red (missing implementation) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the five guards' ASSERTIONS never change — only the constant's home moves; in `test_review_checklist.py` touch ONLY the pin line + the new import (sibling task owns the slicer lines).
Code lives in: `add-method/tooling/engine_pin.py` (new) + the five importer edits
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — own suite 6/6 (red 5F/1P → green, worker-run); integration on main after merge: 586 ran, only reds = the sibling task's declared pending suite (test_md_section ×5)
- [x] coverage did not decrease — suite grew 580→586; no test removed
- [x] no test or contract was altered during build — worker diff = engine_pin.py (new, 13 lines) + five 1-line pin→import swaps; §3/§4 untouched post-freeze
- [x] concurrency / timing safe — built in an isolated worktree; D1 sync gate FIRED (stale v17-era pool base d2d0825 → merged to base f45342e, evidence verified == base before merge-back); declared-overlap file diff = exactly 1 line (in-lane)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; engine_pin is a literal constant, no IO
- [x] layering & dependencies follow CONVENTIONS.md — engine untouched (the moved pin still matches all three copies); cherry-pick merge-back excluded all shared state
- [x] reviewed — auto-resolved under `autonomy: auto` (worker verdict PASS + orchestrator-verified commit scope, fork-base evidence, and integration suite); no security, concurrency, or architecture residue to escalate

### GATE RECORD
Outcome: PASS — auto-resolved (autonomy: auto), owner: v19 wave-1 worker A run + orchestrator integration Verify, 2026-06-08. Not a human signature: recorded on complete evidence per run.md; the human approval for this task was the bundle freeze (hardened at the human's pre-freeze change-request).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the next legitimate engine change — was the re-aim really one line?
Spec delta for the next loop: none — the contract shipped as frozen; wave-level findings live in the v19 Wave log digest.

### Competency deltas
- [TDD · folded] a human pre-freeze change-request made the bundle strictly stronger at near-zero cost — sweep widened to all *.py + cwd-independence subprocess-proven; the "Fix a flag first" option earns its place in every freeze presentation (evidence: this task's freeze round-trip)
- [ADD · folded] worker SUMMARY.md must be IN the worker's commit, not just written — uncommitted worktree files survive only by harness courtesy; the worker contract's <return> should say "commit SUMMARY.md with your code" (evidence: wt-A's SUMMARY.md/deltas.md were left uncommitted and had to be hand-copied before worktree removal)
