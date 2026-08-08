# TASK: Minimalism & coverage audit: prove the Minimal pillar, expire waivers, sweep the matrix

slug: minimalism-audit · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The "Minimal" pillar audit. Three deliverables, one theme: the method's minimalism
claims must be PROVED (not just written) and the engine's state must stay lean. Findings
from the audit (read before building):
  - FINDING-A (the headline): the Minimal claim "Story is never auto-loaded"
    (01-principles.md, code comment add.py:166-172 citing ETH-Zurich) is written but
    UNPROVED. `init` scaffolds no docs/; every engine read is State (state.json, TASK.md,
    templates, the guideline files — the ADD block is a hardcoded constant, not a docs
    read). Invariant holds; no test would catch a regression. test_two_surface only pins
    the prose STRING — fails the circularity bar.
  - FINDING-B: Matrix 4 already promises waiver fields are "stored in state for a later
    `check` to expire" — but `cmd_check` does NOT expire them. A Story↔State drift the
    book itself flags.
  - FINDING-C (record, do not enforce): Matrix 3 says "done only when all six documents
    exist"; the engine checks TASK.md EXISTS, not that its sections are filled. Whether the
    engine should parse sections is a minimalism question — record + recommend, do not add.
  - FINDING-D: v2's MILESTONE.md is an unfilled template (transparency gap).
  - FINDING-E: the flow now has THREE kept-in-sync surfaces (mermaid + ASCII + PNG) — a
    minimalism smell flagged in T3 OBSERVE. Decide from evidence whether the ASCII earns
    its keep.

Must:
  - PROVE the Minimal headline behaviorally: a test asserts that an ADD project with NO
    docs/ present runs its full command lifecycle (init → new-milestone → new-task →
    phase/advance → gate → status → check → ready → milestone-done) with every command
    succeeding — i.e. the engine never requires the Story at runtime. Non-vacuous: the
    test must go RED if a docs/ read is injected into any command (demonstrate, then revert).
  - ENFORCE waiver expiry: `add.py check` FAILS (exit 1) for any task whose gate is
    RISK-ACCEPTED and whose stored waiver `expires` is strictly before today. A waiver with
    expires >= today, or any non-RISK-ACCEPTED task, passes. Close the Matrix 4 promise.
  - SWEEP the matrix: audit Matrices 1-3 for engine-enforceable-but-unproved claims; the
    expired-waiver row IS the cheap win; record every other gap (incl. FINDING-C) as a
    Matrix 4 / OBSERVE finding with a recommendation — do NOT silently enforce new rules.
  - DECIDE the ASCII (FINDING-E) from audit evidence; if dropped, keep 02-the-flow.md's
    loopback test + tree-identity md5 green (a backward-correction edit to a frozen file).
  - FILL v2's MILESTONE.md (FINDING-D) with an honest record of what v2 delivered.
  - If the state audit finds state.json already lean, SAY so — do not manufacture a trim.
Reject (what the engine / a reviewer must turn down):
  - a RISK-ACCEPTED task whose waiver `expires` < today, seen by `check` -> "waiver_expired"
  - a "minimal-pillar" test that only greps add.py source for docs reads (pins
    implementation in reverse, fails the circularity bar) -> reject, require behavioral proof
  - enforcing section-completeness or matrix depth in the engine this task (scope creep /
    anti-minimal) -> reject, record as a finding instead
After:
  - `test_min_pillar.py` proves Story is not on the runtime path (docs-absent lifecycle);
    `cmd_check` flags expired waivers (new Matrix 4 row + proof test); the matrix sweep is
    recorded; the ASCII decision is made + executed; v2 MILESTONE.md is filled; suite green.
Assumptions (confirm before building):
  - [x] T4 boundary = core proof + expired-waiver + ASCII decision + fill MILESTONE.md +
        START the matrix sweep (record gaps, prove the cheap one); defer enforcing
        section/depth. CONFIRMED (AskUserQuestion — user chose the wider boundary).
  - [x] The minimal-pillar proof must be BEHAVIORAL (docs-absent lifecycle), not a source
        grep. CONFIRMED (advisor — circularity bar).
  - [x] Expiry compares stored `expires` (ISO date) to real `date.today()`; tests use
        clearly-past / clearly-future fixtures so no date mocking is needed. CONFIRMED.
  - [x] PROCESS for the ASCII keep/drop: decided FROM audit evidence, then surfaced to the
        human (AskUserQuestion) BEFORE any edit to the T3-frozen 02-the-flow.md. The outcome
        is a deliverable decided mid-task, not an assumption carried forward. CONFIRMED
        (standing rule: all decisions discussed with the human).

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the engine runs the whole flow with no Story present   # FINDING-A, behavioral
  Given a freshly initialised ADD project that has NO docs/ directory at all
  When I run init, new-milestone, new-task, advance/phase, gate PASS, status, check, ready, milestone-done
  Then every command exits 0
  And no command read any path under docs/                        # Story is off the runtime path

Scenario: the minimal-pillar proof is non-vacuous                 # the circularity bar
  Given the docs-absent lifecycle test
  When a docs/ read is injected into any command (a scratch experiment)
  Then the test goes RED                                          # proves it catches the real regression
  And after reverting the injection it is green again

Scenario: check flags an expired waiver                           # FINDING-B / Reject "waiver_expired"
  Given a task gated RISK-ACCEPTED whose stored waiver expires is strictly before today
  When I run add.py check
  Then it FAILS (exit 1) reporting waiver_expired for that task
  And no state is mutated (check is read-only)

Scenario: check tolerates a still-valid waiver                    # the boundary of the rule
  Given a task gated RISK-ACCEPTED whose waiver expires is today or later
  When I run add.py check
  Then that task does not raise waiver_expired
  And a non-RISK-ACCEPTED task is never expiry-checked

Scenario: the matrix sweep is recorded, not silently enforced     # SWEEP + FINDING-C
  Given the audit of Matrices 1-3 for engine-enforceable-but-unproved claims
  When the sweep completes
  Then the expired-waiver row is proved and indexed in Matrix 4
  And every other gap (incl. section-completeness) is a written finding with a recommendation
  And no new enforcement rule was added to the engine beyond expiry   # anti-scope-creep

Scenario: the three-surface smell is decided from evidence         # FINDING-E, human-gated
  Given the audit's evidence on whether the ASCII earns its keep
  When the keep/drop call is made
  Then it is surfaced to the human before any edit to the frozen 02-the-flow.md
  And if dropped, the loopback test and the tree-identity md5 stay green

Scenario: the milestone record is honest                          # FINDING-D
  Given v2's MILESTONE.md was an unfilled template
  When the audit fills it
  Then it records what v2 actually delivered (the four+one tasks and their pillars)
  And it is not left as placeholder text
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

Two engine surfaces change; the rest is documentation + a human decision.

```
add.py check                       (extends cmd_check — read-only, exit 1 on any FAIL)
  for each task t with t.gate == "RISK-ACCEPTED":
    exp = t["waiver"]["expires"]   (ISO "YYYY-MM-DD", guaranteed present — gate refuses without it)
    FAIL "waiver_expired" if date.fromisoformat(exp) < date.today()
  -> adds one check row per task; never mutates state; malformed/missing exp -> FAIL (fail-closed)
Schema: reads state["tasks"][*]["waiver"]["expires"]; no new fields written.

test_min_pillar.py                 (NEW — behavioral proof of FINDING-A)
  init a temp project (tmpdir), assert NO docs/ exists, drive the full lifecycle via add.main([...]),
  assert every call exits 0 and the project never grows a docs/ dir.
  -> proves Story is not on the runtime path; goes RED if a command reads under docs/.

test_proof_harness.py / test_waiver.py   (extended — proof of FINDING-B)
  test_check_flags_expired_waiver        : past expires -> SystemExit(1), stderr/stdout names waiver_expired
  test_check_passes_unexpired_waiver     : today-or-future expires -> clean
```

Documentation deliverables (no engine change): Matrix 4 gains the expired-waiver row +
the FINDING-C / sweep findings; v2 MILESTONE.md is filled; the ASCII decision is recorded.

Frozen invariants: the expiry rule is fail-closed (a RISK-ACCEPTED task with an unparseable
or absent `expires` FAILS check); `check` stays strictly read-only; the minimal-pillar proof
is behavioral, never a source grep. Error code matches GLOSSARY/Reject: `waiver_expired`.

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- changing the fail-closed rule, the read-only guarantee, or the behavioral-proof requirement = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the two engine behaviors (min-pillar invariant + waiver expiry); the
documentation/decision scenarios are human-gated, not coded.
Plan (one test per testable scenario):
  - test_min_pillar.py::test_full_lifecycle_runs_with_no_story — init a project with NO
    docs/, drive the whole lifecycle, assert every command exits 0 and no docs/ is ever
    created. Proves Story not REQUIRED at runtime.
  - test_min_pillar.py::test_no_command_reads_a_docs_chapter — spy on every read_text
    across the lifecycle; assert none resolves under a docs/ dir. Proves Story not READ.
    Non-vacuity guard (see below).
  - test_min_pillar.py::test_every_subcommand_is_covered — derive the full command set
    from build_parser() and assert LIFECYCLE (+ init) covers it exactly. Closes the
    advisor-caught gap: the read-spy claim is universal ("no command"), so the spy must
    run EVERY subcommand, not a subset. LIFECYCLE was widened to drive all 14 non-init
    commands (added stage, set-milestone, phase, sync-guidelines, archive-milestone); a
    NEW subcommand now fails this test until classified. Non-vacuity: adding a dummy
    subparser absent from LIFECYCLE flags it.
  - test_waiver.py::WaiverExpiryCheckTest — flags an expired waiver (FAIL+waiver_expired,
    no mutation); passes a future waiver; fails-closed on an unparseable expires.

Red-first evidence:
  - waiver expiry: 2 of 3 RED before build (flags_expired, failclosed) — feature absent;
    the future-waiver case is trivially clean until the rule exists.
  - min-pillar: GREEN from the start (the invariant already holds). NON-VACUITY proven by
    injecting a `docs/02-the-flow.md` read into cmd_status → BOTH tests went RED (errors=2)
    → reverted (add.py md5 back to ff2c578…). This clears the circularity bar: the test
    catches a REAL regression, not just "someone edited a file".

Tests live in: `add-method/tooling/test_min_pillar.py` (new) + `test_waiver.py` (extended).

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the expiry check is read-only and fail-closed — it parses
a stored date inside try/except so a malformed `expires` FAILS loudly (never a silent pass)
and `check` never mutates state. Compares to real `date.today()` (already imported).
Built:
  - add.py cmd_check: +1 per-task check — RISK-ACCEPTED tasks whose `expires` < today (or is
    missing/unparseable) FAIL with `waiver_expired`. Synced byte-identical to .add/tooling
    (md5 f567fa6…). No other command touched.
  - test_min_pillar.py (NEW, 2 tests) + test_waiver.py (+3 tests, WaiverExpiryCheckTest).
  - 02-the-flow.md ASCII: 人 → "human" (FINDING-E decision = KEEP+fix, via AskUserQuestion);
    propagated to all 3 trees (md5 ae43e4d…); flow-diagram tests stay green.
  - appendix-f Matrix 4: +2 proved rows (Minimal pillar, waiver expiry) + a "Sweep findings"
    block recording FINDING-C (section-completeness deliberately NOT enforced) and the lean
    state.json bill; propagated to all 3 trees (md5 2233bf7…).
  - .add/milestones/v2/MILESTONE.md filled (FINDING-D) with the honest v2 record.
Constraints honored: stdlib only; no test or frozen contract weakened; the engine gained
exactly ONE new enforcement (expiry) — section/depth were recorded, not enforced (anti-creep).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 88/88 OK (83 + 5 new); dogfood `add.py check` 53/0
- [x] coverage did not decrease — net +5 tests (2 min-pillar, 3 waiver-expiry)
- [x] no test or contract was altered during build — tests written + run RED first; the
      waiver-expiry tests went red before cmd_check learned the rule; the min-pillar tests
      proved non-vacuous by a scratch docs-read injection (errors=2), then reverted
- [x] timing/IO safety — the expiry check is read-only and fail-closed (try/except around
      date parsing; a malformed `expires` FAILS, never silently passes); `check` mutates nothing
- [x] no exposed secrets / no unexpected deps — stdlib only (datetime.date already imported);
      no network IO; no new package
- [x] layering follows CONVENTIONS.md — engine logic in add.py (synced byte-identical to
      .add/tooling, md5 f567fa6…); tests in add-method/tooling; docs propagated to all 3 trees
- [x] engine gained exactly ONE enforcement (expiry); section/depth recorded NOT enforced
      (anti-creep, the contracted Reject) — the audit's chosen boundary is documented
- [x] a person reviewed and approved the change — the two load-bearing decisions (the wider
      T4 boundary; ASCII keep+fix over drop) were made by the author via AskUserQuestion
      before execution; the rest is machine-proved. Author review below.

### GATE RECORD
Outcome: PASS
Note: The Minimal pillar is now PROVED, not merely asserted — the engine runs the whole
lifecycle with no Story present and reads no docs/ chapter at runtime (FINDING-A closed,
the same headline-claimed-but-unproved shape as the earlier RISK-ACCEPTED bug). `check` now
expires lapsed waivers (FINDING-B, closing a Matrix 4 promise). The matrix sweep ran:
section-completeness is deliberately left to the human Verify gate, not the engine
(FINDING-C, recorded with rationale); state.json confirmed lean. The ASCII earns its keep
as the zero-renderer surface, with its non-English 人 glyph fixed (FINDING-E, decided via
AskUserQuestion). v2 MILESTONE.md filled (FINDING-D). One new enforcement only — the rest
recorded, honoring the Minimal pillar this task audits.
Reviewed by: Tin Dang (author, decisions via AskUserQuestion) · date: 2026-05-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does any future command start reading a docs/ chapter
(test_min_pillar goes red = the Minimal pillar regressing)? Do real waivers ever lapse
unnoticed (now `check` catches them — watch for them in CI)?
Spec delta for the next loop (feeds v3 / future milestones):
  - Expiry is enforced at `check` time, not at `gate` time — a waiver can be signed already
    expired and only caught later. A future loop could refuse signing a past-dated waiver at
    the gate (defense in depth). Deferred (separate decision, separate task).
  - FINDING-C stands as a deliberate boundary: the engine grades structure, the human grades
    section content. If that boundary ever feels wrong, it is a v3 SPEC question, not a bug.
  - The matrix sweep ran ONCE. Matrices 1–2 (per-level ownership, per-milestone depth) are
    largely human/process promises, not engine-enforceable — the audit found no further cheap
    engine proofs. Re-run the sweep whenever a new engine command adds an enforceable promise.
  - Three flow surfaces (mermaid + ASCII + PNG) were KEPT (each serves a distinct render
    context) and are all pinned (mermaid test + tree md5; PNG human gate). The smell is
    resolved-as-accepted, not open — revisit only if a fourth surface appears.
  - The read-spy patches only Path.read_text (every read site in add.py uses it today). A
    future read via open(p).read() would evade the guard — assumption noted in the test
    docstring; tighten only if a non-read_text read site is ever introduced.
  - English-only (T3's contract) is now where the Minimal pillar was before this audit:
    asserted in a written contract, one violation (人) hand-fixed, no test guarding
    regression. Off-thesis to fix here (scope); a clean future-loop candidate — "assert,
    not prove" → add a no-non-ASCII-in-docs guard if it ever regresses.
