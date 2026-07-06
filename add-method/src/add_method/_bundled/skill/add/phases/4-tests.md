# Phase 4 — Tests (failing-first suite)

Goal: tests from scenarios + contract that FAIL before any code exists. Fill **§4 TESTS**; the suite lives in `.add/tasks/<slug>/tests/`.

## The must-fail principle

Run the suite now, with no implementation — **red for the right reason**
(missing implementation, not a broken harness). A test green before code
exists is testing nothing.

**A test is any machine-checkable assertion**, not only xUnit code —
a metric threshold (ML/data), a reconciliation query (data integrity),
a plan-diff (infra/IaC), a rendered-screen diff (UI). Red-first holds
for each: the assertion must FAIL before the change exists.

## Produce

<output_format>
- One executable test per scenario (§2), asserting **behavior, not internals**.
- Contract-conformance tests (shapes + error responses from §3).
- Side-effect assertions on rejection paths (`assert balance unchanged`).
- A recorded coverage target in §4.
- §6 **Build expectations** filled now, BEFORE build — observable outcomes from §2 + §3.
</output_format>

## Declaring where tests live

§4's `Tests live in:` line is machine-read: with no local `tests/`, `add.py report`
counts test functions at the declared backticked paths (FIRST such line only).
`./…` → this task dir · a token with `/` → the project root · a bare name → a
sibling of the previous token's dir. A directory counts its `*.py` files
(non-recursive); a `.py` file counts itself. Resolved files dedupe; declared counts
marked `†`. Paths are confined: outside the project root counts 0 — `..` traversal,
absolute paths, and symlink escapes are never read.

## AI prompt

<prompt>
Role: a test author who writes tests before code.
Read first: §2 · §3.
Steps: turn each scenario into an executable test; add contract-conformance and
edge cases; run the suite red for the right reason; record a coverage target.
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
> **Advisor · Confidence** — spawn a test-author for a broad red suite (advisor.md); score Completeness honestly (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/5-build.md`.
Book: `docs/06-step-4-tests.md`.
