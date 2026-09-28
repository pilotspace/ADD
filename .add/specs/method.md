---
type: Spec
lens: method
---
## Now
ADD 4.0 is one markdown skill. The model sizes the work, writes the contract and failing checks,
seals them with a `freeze(<slug>)` commit, builds to green, verifies against the seal, and writes
the verdict into the task's `## EVIDENCE`. The human reviews after, through the session report or PR.
The 3.x method record (68 deltas, the engine's decisions) is kept at `archive/add-3x-bundle/specs/method.md`.

## Decisions that bind
- D1 no engine: the method ships as prose the model follows; git and the project's test command are the only tools (evidence: user interview 2026-09-28; benchmark/BENCHMARK.md final cross-arm comparison — 3.x ADD 18.2M tokens ~$15 vs spec-kit 3.8M $2.53 at fidelity min 0.97 vs 0.95; benchmark/FINDINGS-2026-08-10.md amb1 — ADD $2.13-2.52 vs vanilla $0.61, the ASSUMPTIONS section moved auditability, not correctness)
- D2 git is the seal: `freeze(<slug>)` / `refreeze(<slug>)` commits; verify diffs the sealed files against the latest one (evidence: user interview 2026-09-28)
- D3 no human approval gate and nothing interrupts the run; the report lists every ASSUMPTION taken so the review can disagree (evidence: user interview 2026-09-28)
- D4 a security finding is a HARD-STOP verdict — the task stays open and the finding leads the report (evidence: user interview 2026-09-28)
- D5 adherence is not free: the 3.x benchmark only held the loop once it was enforced and census-verified, so SKILL.md stays short, the artifacts few, and every step leaves a file or commit a reviewer can see was skipped (evidence: benchmark/BENCHMARK.md — "loop enforced (census-verified)")

## Deltas
