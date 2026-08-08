# TASK: audit wired into CI — the enforcer distinct from the agent

slug: audit-ci · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the gate-audit runs OUTSIDE the agent — a CI job in this repo enforces the
  dogfood board on every push/PR, and consumers get the same enforcement as a
  copy-paste workflow in GETTING-STARTED (closes "a self-asserted gate is circular",
  open since v7 — second half of gate-audit)
Framings weighed: distinct CI job + docs snippet (chosen: the exit criterion says
  "a job distinct from the agent"; one canonical command works in dogfood AND
  consumer repos because the installer places add.py at the same path) · audit as a
  step inside the existing test job (rejected: enforcement visibility — a seam
  failure must be named as ITS OWN red check, not buried in a test matrix) ·
  init-scaffolded workflow file into consumers' .github/ (rejected: the installer
  never writes outside .add/; docs snippet is the lean call-to-action)
Must:
  - `.github/workflows/ci.yml` gains a SEPARATE job `seam-audit` (alongside `test`):
    checkout → setup-python 3.12 → run exactly `python3 .add/tooling/add.py audit`
    from the repo root — auditing the live dogfood board; nonzero exit fails CI.
  - The exact command string in ci.yml is BEHAVIORALLY proven: extracted from the
    YAML by the test and executed via subprocess in an installed-layout fixture
    (.add/tooling/add.py) — exit 1 naming the task on a malformed seam record,
    exit 0 on a clean board (the wiring is tested, not just prose).
  - GETTING-STARTED.md gains an "enforce the seams in CI" section: a complete
    copy-paste workflow (checkout · setup-python · the same canonical command) so
    any consumer repo gets the identical enforcement.
  - Package side: the audit engine already ships (gate-audit synced ×3); a guard
    pins that the bundled add.py keeps the `audit` subcommand — "shipped in the
    package" stays true by test, not by memory.
Reject:
  - a malformed seam record committed to the board -> CI job `seam-audit` red,
    output names {task, code} (inherited from gate-audit's frozen exit semantics)
  - the agent stamping its own enforcement green -> impossible by construction:
    the job runs on GitHub runners from the committed tree (never-self-gate at the
    infrastructure level, foundation v2)
After:
  - every push/PR to main re-verifies all recorded human seams; a forged or
    malformed record is caught by a machine the agent does not control, making
    forgery attributable in CI history (gate-audit §7 handoff honored)
Assumptions — least-sure first:
  ⚠ the seam-audit job BLOCKS merges (a true gate, not informational) — least sure
    because any future edit that malformes a legacy record halts CI until fixed;
    if wrong: flip is one line (continue-on-error), but a non-blocking audit is
    theater — chosen: blocking
  - [x] docs-snippet (not scaffolded file) is the right consumer ship — confirmed
    by the installer's .add-only write boundary and the minimal-over-ceremony rule
  - [x] no publish.yml change needed — it re-runs this same suite at tag time, so
    the new wiring tests ride along automatically

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: clean board passes the CI command
  Given an installed-layout project (.add/tooling/add.py) whose done tasks all
        carry well-formed seam records
  When the exact command string from ci.yml's seam-audit job is executed
  Then it exits 0
  And no file in the project changes (audit purity, inherited)

Scenario: malformed seam record fails the CI command
  Given the same project after a commit strips a freeze stamp from a done task
  When the exact command string from ci.yml's seam-audit job is executed
  Then it exits 1 and the output names the task and the finding code
  And no file in the project changes

Scenario: enforcement is a job distinct from the agent
  Given .github/workflows/ci.yml
  When its jobs are listed
  Then `seam-audit` exists as its own job beside `test`
  And its run line is exactly `python3 .add/tooling/add.py audit`

Scenario: a consumer can copy the same enforcement
  Given GETTING-STARTED.md
  When the reader reaches the CI section
  Then a complete workflow snippet with the same canonical command is present

Scenario: the package keeps shipping the audit engine
  Given the bundled tooling (_bundled/tooling/add.py)
  When its subcommands are inspected
  Then `audit` is among them (×3 parity already pins byte-equality)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
.github/workflows/ci.yml          (this repo — the dogfood enforcer)
  jobs.test        : unchanged (matrix 3.10/3.12, full suite)
  jobs.seam-audit  : NEW — runs-on ubuntu-latest
                     steps: checkout@v4 · setup-python@v5 (3.12) ·
                            run: python3 .add/tooling/add.py audit
  semantics        : audit exit 1 -> job red -> CI red (BLOCKING)

add-method/GETTING-STARTED.md     (the consumer ship)
  NEW section "## Enforce the seams in CI" — complete copy-paste workflow
  (name: seam-audit · on push/PR · permissions contents:read · same run line)

ENGINE UNTOUCHED: add.py byte-identical across all 3 trees (audit exit codes +
finding grammar consumed AS FROZEN by gate-audit @ v1 — this task only wires).
GUARD: add-method/tooling/test_audit_ci.py — the run line is EXTRACTED from
ci.yml and executed (subprocess) in a fixture; changing the command in ci.yml
without updating enforcement = red test, not silent drift.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion; ⚠ blocking-gate + docs-snippet flags surfaced and accepted at the freeze)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject above has a test; suite stays green elsewhere.
Plan (one test per scenario, asserting behavior not internals):
  - test_ci_defines_distinct_seam_audit_job: arrange read ci.yml / assert both
    `  test:` and `  seam-audit:` are jobs-level keys and the canonical run line
    sits under seam-audit (RED: job absent)
  - test_ci_audit_command_is_canonical: assert the extracted run line equals
    `python3 .add/tooling/add.py audit` exactly (RED)
  - test_ci_command_fails_on_malformed_seam: arrange installed-layout fixture
    through the real CLI, strip a freeze stamp / act subprocess-run the EXTRACTED
    line / assert returncode 1 + task named + no file mutated (RED: no line to
    extract)
  - test_ci_command_passes_clean_board: same fixture, clean / assert returncode 0
    (RED: same extraction)
  - test_getting_started_ships_consumer_workflow: assert the GETTING-STARTED
    section exists with the same canonical run line (RED: section absent)
  - test_bundle_ships_audit_engine: assert `_bundled/tooling/add.py` exposes the
    `audit` subparser (green-by-design regression guard on "shipped in the package")

Tests live in: `add-method/tooling/test_audit_ci.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the engine (add.py) and the frozen audit grammar are
READ-ONLY for this task — wiring only; if the wiring reveals an engine gap, that is a
change request, never an inline edit.
Code lives in: `.github/workflows/ci.yml` · `add-method/GETTING-STARTED.md` · `add-method/tooling/test_audit_ci.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 401/401 OK (was 395; +6 in test_audit_ci.py, 6/6 OK)
- [x] coverage did not decrease — 5 red→green + 1 green-by-design guard added;
      `add.py check` 202 passed / 0 failed (4 pre-existing warnings)
- [~] no test or contract was altered during build — DISCLOSED: one in-build
      STRENGTHENING of the §4 suite — `_run_ci_command` gained a refuse-non-canonical
      precondition (assertEqual line == CANONICAL before subprocess) after the
      security pass below found the execute-extracted-string surface; strictly
      stronger, nothing weakened; non-vacuity proven (drifted ci.yml line → 2 red
      WITHOUT executing the drift; ci.yml restored byte-identical). §3 contract
      untouched.
- [x] concurrency / timing of the risky operation is safe — the seam-audit job runs
      parallel to the test matrix on independent checkouts; the audit is read-only
      (purity asserted in test_gate_audit AND re-asserted through the subprocess
      fixture here); the test subprocess carries a 60s timeout
- [x] no exposed secrets, injection openings, or unexpected dependencies — ⚠ NOTE
      (security line): the behavioral test executes a command string EXTRACTED from
      ci.yml; that surface was closed during build with the refuse-non-canonical
      precondition (drift fails red without ever executing the drifted string —
      proven, then reverted). The workflow itself: static run lines only, zero
      `github.event` interpolation (the workflow-injection hook guidance was
      checked), file-level `permissions: contents: read` inherited by the new job,
      stdlib-only, no new dependencies.
- [x] layering & dependencies follow CONVENTIONS.md — wiring only: engine
      byte-identical ×3 (md5 92bdaae03677674e756568ab7c69fed8); the frozen audit
      grammar consumed as-is; docs + workflow + tests are the only touched files
- [x] a person reviewed and approved the change — ESCALATED (security-line note +
      in-build test amendment) and confirmed by Tin via AskUserQuestion

### GATE RECORD
Outcome: PASS — human-confirmed (escalated: ⚠ security note on the closed
  execute-extracted-string surface + the disclosed in-build strengthening; both
  accepted)
Reviewed by: Tin (human gate) · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the seam-audit job's first live runs on main
(stays green while the board is clean); subprocess flakiness on runners (60s
timeout in the tests); the accepted ⚠ cost — a legacy-record edit that malformes
a seam halts CI until the record is fixed (fix the record, never the auditor).
Spec delta for the next loop: "a self-asserted gate is circular" (open since v7)
is CLOSED on the next push — enforcement runs on a machine the agent does not
control; high-risk-signal extends the same audit surface, release-1-1-0 ships it.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [TDD · folded] a test that executes a string extracted from a repo artifact must
    refuse-on-drift — assert the extracted value equals the pinned constant BEFORE
    executing, so drift turns the suite red without ever running unpinned input
    (evidence: drifted ci.yml run line refused; proven non-vacuously, then reverted)
  - [ADD · folded] an in-build test amendment that strictly STRENGTHENS is legal but
    never silent — disclose it at the gate beside the security note that motivated
    it, and let the human adjudicate both in one escalation (evidence: this gate,
    confirmed by Tin 2026-06-05)
