# TASK: TESTS column falls back to the §4 'Tests live in:' declared path

slug: tests-declared-fallback · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: TESTS column declared-path fallback (P3 of the per-phase report review)
Framings weighed: declared-path fallback with †footnote (chosen) · always-trust-§4 (rejected:
  would let prose override the canonical `tests/` dir even when real files exist) ·
  lint-§4-vs-dir mismatch (rejected: adds judgment; the engine extracts, never judges)
Must:
  - When `tasks/<slug>/tests/` yields 0 tests AND §4 has a `Tests live in:` line, the
    TESTS count falls back to counting `def test_` at the declared path(s).
  - A fallback count renders with a `†` marker in the table cell (e.g. `18†`) and ONE
    footnote line under the task table: `† counted at the §4-declared path`.
  - The primary count (files in `tasks/<slug>/tests/`) ALWAYS wins when > 0 — never
    mixed with, or overridden by, the declared count.
  - Declared tokens are the backticked spans on the FIRST `Tests live in:` line of the
    raw §4 body; resolution: `./…` → task dir · contains `/` → project root (parent of
    `.add`) · bare filename → sibling of the previous resolved token (else task dir).
  - A directory token counts `*.py` inside it (non-recursive); a `.py` token counts that
    file; resolved paths are deduped before counting; the counting regex is byte-identical
    to the primary one (`^\s*def test_`, re.M).
  - `report --json` tasks gain ONE additive key `tests_declared: bool`; `report --decide`
    facts reuse the truthful count with the frozen key-set `{phase,gate,deps,tests}` UNCHANGED.
Reject:
  - declared path missing / unreadable / outside grammar -> count contribution 0,
    fail-closed, exit 0, NO crash, NO footnote for that row ("never misleading" ≠ "never 0":
    a true 0 stays a bare 0)
  - any write during report/decide -> impossible by construction (v9 purity carried)
After:
  - A reviewer of this dogfood repo sees `18†` instead of a misleading bare `0` for tasks
    whose suites live at the §4-declared `add-method/tooling/test_*.py` path; standard
    consumers (`./tests/`) see zero behavior change.
Assumptions — least-sure first:
  ⚠ sibling-shorthand resolution (bare `test_b.py` after `dir/test_a.py` means the same
    dir) is inferred from 3 real §4 lines in this repo, not from any written grammar —
    least sure because authors may intend something else; if wrong: that token counts 0
    (fail-closed), the total under-counts but never crashes or over-claims.
  - [ ] additive `tests_declared` key in report --json is compatible — no frozen key-set
    test exists for report tasks (verified: only decide facts are pinned, test_decide_digest.py:174);
    if wrong: a meta-test registry update, never an assertion weakening.
  - [ ] first `Tests live in:` line only is enough — all 36 real task files in this repo
    carry exactly one; continuation lines never hold the backticked paths.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: declared fallback renders the footnoted count
  Given a task whose tests/ dir is empty
  And its §4 holds "Tests live in: `tooling/test_real.py`" with 3 def test_ functions there
  When add.py report <ms> renders the table
  Then the task's TESTS cell reads "3†"
  And exactly one footnote line "† counted at the §4-declared path" follows the table
  And report --json shows tests=3, tests_declared=true

Scenario: primary count always wins
  Given a task with 2 tests in tasks/<slug>/tests/
  And a §4 line declaring a different file holding 5 tests
  When the report renders
  Then the TESTS cell reads "2" with no †
  And tests_declared=false
  And the declared file is never read into the count

Scenario: nothing anywhere stays a bare honest zero
  Given a task with no tests/ files and no "Tests live in:" line in §4
  When the report renders
  Then the TESTS cell reads "0" with no † and no footnote line
  And the exit code is 0

Scenario: missing declared path fails closed
  Given a §4 line declaring `tooling/does_not_exist.py`
  When the report renders
  Then the count is 0, no †, exit 0, no crash
  And no file outside .add/ was created or modified

Scenario: sibling shorthand sums multiple tokens
  Given §4 declares "`tooling/test_a.py` + `test_b.py`" where both exist beside each other
  When the count resolves
  Then it equals the sum of def test_ in both files
  And duplicate resolved paths are counted once

Scenario: directory token counts its *.py files
  Given §4 declares a directory token ending in "/"
  When the count resolves
  Then every *.py directly inside contributes its def test_ count (non-recursive)

Scenario: decide facts reuse the truthful count, shape frozen
  Given the declared-fallback task above at a gate seam
  When add.py report <ms> <slug> --decide --json runs
  Then facts.tests equals the declared count
  And facts keys are exactly {phase, gate, deps, tests}   # unchanged from v13 task 1

Scenario: every path stays pure
  Given any of the scenarios above
  When report / report --json / report --decide run
  Then the .add tree's file set and state.json bytes are unchanged
  And every invocation exits 0
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_declared_tests_count(root, slug) -> int
  # raw §4 body via _raw_phase_bodies (decide-digest's scanner — ONE canonical § source)
  # FIRST line matching ^\s*Tests live in:  → tokens = all `…` backticked spans on that line
  # resolve: "./…" → root/tasks/<slug>/…  ·  has "/" → root.parent/…  ·  bare → previous
  #          token's parent dir (else task dir)
  # count: dir → each *.py inside (glob, non-recursive) · *.py file → itself
  #        dedupe resolved files · regex ^\s*def test_ (re.M) — identical to _tests_count
  # ANY OSError / no §4 / no line → 0   (fail-closed, pure)

_tests_info(root, slug) -> tuple[int, bool]          # (count, declared)
  # primary = _tests_count(...)  →  primary > 0  ⇒ (primary, False)
  # else d = _declared_tests_count(...)  →  d > 0  ⇒ (d, True)  else (0, False)

report_data tasks[i]:  "tests": int (now truthful) · "tests_declared": bool   # ONE additive key
render_report cell  :  f"{n}†" when declared else f"{n}"   # still ≤5 cols for n ≤ 9999
render_report extra :  one line directly after the task table, only if any row declared:
                       " † counted at the §4-declared path"
decide_data facts   :  "tests" = _tests_info(...)[0]   # key-set {phase,gate,deps,tests} FROZEN
Purity              :  all paths read-only (v9) · no new CLI flag · no state.json change
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-04 (one-approval front; 3 least-sure flags accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 3 resolution forms (./ · path/ · bare-sibling) + both render surfaces
(report cell+footnote · decide facts) + the additive --json key + fail-closed + purity —
one test per scenario, asserting rendered bytes / JSON values, never internals.
Plan (one test per scenario):
  - test_declared_fallback_footnote: empty tests/ + §4 file w/ 3 tests → cell "3†",
    exactly one footnote line, --json tests=3/tests_declared=true
  - test_primary_wins: 2 real + 5 declared → "2", no †, tests_declared=false
  - test_bare_zero_no_footnote: nothing anywhere → "0", no "†" anywhere in output, exit 0
  - test_missing_declared_failclosed: nonexistent declared path → 0, exit 0
  - test_sibling_shorthand_sums: `dir/test_a.py` + bare `test_b.py` → sum; dup token counted once
  - test_directory_token: dir token → non-recursive *.py sum
  - test_decide_facts_truthful_frozen: --decide --json facts.tests = declared count,
    facts key-set exactly {phase,gate,deps,tests}
  - test_purity_all_paths: file-set + state.json hash unchanged across report/--json/--decide,
    every exit code asserted 0

Tests live in: `add-method/tooling/test_declared_fallback.py` (suite root, like every prior
tooling task) · MUST run red (no `_tests_info`, no †) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): every report path stays PURE — the fallback only ever READS
the declared paths; any OSError yields 0, never an exception, never a write.
Code lives in: `add-method/tooling/add.py` (canonical) → synced to `.add/tooling/add.py`
and `add-method/src/add_method/_bundled/tooling/add.py` (3-tree md5 parity).
Constraints: do NOT change any test or the contract; stdlib only; touch-boundary =
add.py ×3 + the new test file; decide facts key-set is FROZEN (v13 task 1) — never add keys there.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 355/355 (347 prior + 8 new), `add.py check` 190/0 (4 pre-existing warns)
- [x] coverage did not decrease — 8 tests added, none removed/weakened; red 5-for-the-right-reason
      (KeyError tests_declared · 0≠3 · cells lacked †) + 3 green-by-design regression guards
      (bare-zero · fail-closed · purity) asserting what must REMAIN unchanged
- [x] no test or contract was altered during build — §3 untouched post-freeze; only the NEW
      test file exists; existing suites byte-identical
- [x] concurrency / timing safe — every path read-only (purity test pins file-set + state hash);
      no shared mutable state, no subprocess, no network
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only.
      NOTE (reviewed, no finding): a §4 token can name a path outside the project
      (absolute / `..`); the engine then READS that file but reveals only an integer
      `def test_` count — no content, no write, no privilege boundary crossed (add.py is a
      local tool reading files its user already owns). Confinement would be a new Reject
      rule = change request; logged as an open delta below.
- [x] layering & dependencies follow conventions — helpers live beside `_tests_count`; ONE
      counting regex by construction (`_count_test_defs` shared); render stays in render_report;
      3-tree md5 parity 8b8b20bae6b1efb3ff677c0c87b22d43 ×3
- [x] a person reviewed and approved the change — Tin approved the frozen contract
      (one-approval front, 2026-06-04); gate auto-resolved on complete evidence per
      `autonomy: auto` (no deviation, no residue, no security finding)

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence — all green · loops dry · no residue ·
no deviation: build touched exactly the declared boundary, add.py ×3 + the new test file)
Reviewed by: auto-gate under `autonomy: auto` · contract approved by Tin · date: 2026-06-04
Correction (2026-06-05): the §6 security-line note (out-of-tree declared token is READ,
leaking only an integer def-count) was auto-reclassified "no finding" — that judgment
belongs to the human gate. Escalated post-hoc; Tin CONFIRMED PASS, 2026-06-05.
Confinement stays an open SDD delta for a future contract version.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): share of task rows rendering `†` vs bare counts (a rising
† share means suites keep living outside `tests/` — the template default may want updating);
any report crash on a malformed `Tests live in:` line (must stay impossible — fail-closed).
Spec delta for the next loop: the misleading-0 is closed for declared suites; the remaining
honest gap is that the declaration grammar (backticked tokens · sibling shorthand) lives as
inferred convention, not written spec.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [SDD · folded] the `Tests live in:` grammar (backticked tokens, sibling shorthand) is engine-parsed
    but nowhere written as spec — the TASK.md template/§4 guide should state it (evidence: §1 ⚠ flag
    had to infer the sibling rule from 3 observed lines)
  - [SDD · folded] declared tokens can name paths outside the project root (read-only, leaks only a
    def-count integer — reviewed at §6, no finding); a confinement Reject rule is a candidate for a
    future contract version (evidence: §6 security note, gate PASS)
  - [ADD · folded] an item the AI itself wrote on the §6 security line was auto-reclassified
    "no finding" and auto-gated — security-category judgment always belongs to the human gate,
    whatever the apparent severity (evidence: gate record correction, Tin confirmed PASS post-hoc)
