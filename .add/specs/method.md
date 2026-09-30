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
- 2026-09-30 open · a rule stated in SKILL.md lands at the grain the model already thinks in: "malformed or wrong-typed input is refused" became a field-type check in 6 of 6 contracts and never a body-is-not-an-object check, so null/number bodies still 5xx'd in 4 of 6 runs; one run's tests sent naive timestamps and its DELETE crashed on aware ones. Both are the check sharing the builder's picture of the input — a "shape" sweep (inputs as a real caller sends them) is the proposed fix; the falsifier practice is the one with a measured gain (mutation +0.17/+0.26) and Direction is 41–44% of tokens at ~20 API messages against "two turns" (evidence: benchmark/PILOT-4v3-2026-09-30.md)
- 2026-09-29 open · the security-floor second reader is the one control that costs real turns (+46% tokens, 2.6× wall on invite-expiry) and in its first run it found a real contract gap (consume-before-add ordering); measure its yield from `lens:` lines before keeping it at subagent strength (evidence: close-research-gaps EVIDENCE)
- 2026-09-29 open · outcome oracles did not separate the new skill from the old on three small fixtures — claude-sonnet-5 got all of them right either way; the gains showed in the contract (falsifiers, M3) and the report (HARD-STOP), so evals of this method need fixtures where the plausible build is wrong (evidence: close-research-gaps EVIDENCE)
