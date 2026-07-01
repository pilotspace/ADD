# Phase 4 — Tests (failing-first suite)

Goal: turn scenarios + contract into automated tests and confirm they FAIL before any code exists — red now, green only after Build. Fill **§4 TESTS** and write the suite into `.add/tasks/<slug>/tests/`.

## The must-fail principle

Run the suite now, with no implementation — it must be **red for the right
reason** (missing implementation, not a broken harness). A test that passes
before code exists is testing nothing and will wave bad code through later.

## Produce

<output_format>
- One executable test per scenario (§2), asserting **behavior, not internals**.
- Contract-conformance tests (shapes + error responses from §3).
- Side-effect assertions on rejection paths (`assert balance unchanged`).
- A recorded coverage target in §4.
</output_format>

## Declaring where tests live

§4's `Tests live in:` line is machine-read: with no local `tests/`, `add.py report`
counts test functions at the declared backticked paths instead (FIRST `Tests live in:`
line only). Resolution: `./…` → this task's dir · a token with `/` → the project root
(parent of `.add/`) · a bare name → a sibling of the previous token's dir (else the
task dir). A directory token counts the `*.py` files directly inside it (non-recursive); a `.py`
file counts itself; else ignored. Resolved files dedupe; declared counts marked `†`. Paths
are confined: anything resolving outside the project root counts 0 — `..` traversal, absolute
paths, and symlink escapes are never read.

## AI prompt

<prompt>
Role: a test author who writes tests before code.
Read first: §2 · §3.
Objective: a red suite that fails for the right reason — behavior, not internals.
Steps:
  1. Turn each scenario into an executable test.
  2. Add contract-conformance and edge-case tests.
  3. Run the suite and confirm it fails for the right reason; record a coverage target.
Never: implement the feature, or assert on internals.
</prompt>

## Exit gate

<exit_gate>
- [ ] One test per scenario.
- [ ] Suite runs and is **red for the right reason**.
- [ ] Tests assert observable behavior.
- [ ] Coverage target recorded.
</exit_gate>

> **Persona** — let the fit persona's `## Success Metrics` shape the red suite (advisory).
> **Advisor · Confidence** — spawn a test-author for a broad red suite (advisor.md); score Completeness — one test per scenario, every rejection covered (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/5-build.md`.
Book: `docs/06-step-4-tests.md`.
