# Appendix H · ADD vs spec-kit — the honest comparison

[← Appendix G References](./appendix-g-references.md) · [Contents](./README.md)

> **The one-sentence version:** both are methods an agent follows from text; ADD's difference is that every claim it makes — the contract was not weakened, the checks ran, this is what was guessed — is left behind as something a reviewer can check with git.

This page answers "why would I use ADD instead of spec-kit (or any spec-first prompt kit)?" It is deliberately honest, including where spec-kit wins, because a comparison you cannot trust is worthless.

## What we measured

The measurements below were taken on earlier ADD versions (2.x and 3.x, which carried an engine). They are reported as measured; 4.0 has not been re-measured on these tracks yet.

We ran the same six-milestone evolving project (CRUD → business rules + auth → a breaking API-shape change → filters/pagination/recurring → a cross-cutting rooms refactor → correctness hardening) through both flows under a pinned model with deterministic probe scoring — no LLM judge. Full data: [the campaign report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md).

**Where both flows tied.** With a fresh agent session per milestone resuming from on-disk state, both flows held every trust floor — requirement coverage 1.0, zero regressions, zero test-gaming — across all six milestones. A first-edition claim that spec-kit collapsed under evolution was traced to a defect in our own meter and publicly retracted.

**Where spec-kit wins.** Cost, on friendly ground: ~$1.42–1.68 per milestone vs ADD's ~$2.58–2.92 (≈1.7–1.8×) at equal measured trust, with fewer artifacts and less ceremony. That gap, and a larger one against plain prompting, is why 4.0 removed the engine ([20 · What changed in 4.0](./20-whats-new-in-4.md)). If your project is small, single-component, driven by a strong model, and you re-read everything anyway, spec-kit is a rational choice.

**Where the real finding lives.** Context rot: when one continued conversation carried the milestones, *both* flows decayed identically (coverage .92 → .80 → .75), locking in an early spec violation for five further milestones. Restarting each milestone from disk eliminated the decay in every measured cell. The lesson is method-agnostic: **your on-disk state must be good enough to restart from, every time.**

## The structural difference

spec-kit is templates and prompts — a constitution, spec documents, a plan format, a task list. ADD 4.0 is also a text method: one skill file. Neither runs an enforcement engine. What differs is what each leaves behind for a reviewer.

| Guarantee | ADD 4.0 | spec-kit |
|---|---|---|
| Checks exist before the code | red-first checks, run and seen failing before any production code | tests are a task among others |
| The contract cannot be quietly weakened | task file and checks are sealed in a `freeze(<slug>)` commit; any later change is visible in `git diff` or is an explicit `refreeze` with a reason | convention only |
| Every rule is checked | every Must and Reject is named by a check's `covers:` line | convention only |
| Guesses are visible | every silence the agent filled is an `ASSUMPTIONS` line with its cost, reported to the human | not a first-class artifact |
| A verdict is recorded | `PASS` / `RISK-ACCEPTED` / `HARD-STOP` in the task file, with the exact commands, exit codes and counts | produces specs, not verdicts |
| Security findings cannot scroll past | a security finding is always `HARD-STOP`, at the top of the report | convention only |
| Resume is a primitive | read `PROJECT.md` and the open task files; nothing lives in the chat | re-read the documents |
| Specs evolve | five living specs; lessons with evidence promoted into binding decisions | per-feature docs that drift |

None of this is mechanically enforced in 4.0. A dishonest agent could write a verdict it did not earn — and a reviewer would catch it by re-running the recorded commands at the recorded commit. That checkability is the product.

## When the discipline should matter

1. **Weaker or cheaper models** — discipline substituting for model quality.
2. **Tempting changes** — where the cheapest green is weakening your own tests.
3. **Autonomous operation** — nobody is watching the diff scroll past, so the record has to carry the review.
4. **Long horizons, teams, several components** — where "re-read the docs" stops scaling.

These are predictions, not claims; the tracks in [`benchmark/`](https://github.com/pilotspace/ADD/tree/main/benchmark) are how they become numbers.

**One data point on prediction 1, from 3.x (published because it went against us at first):** a smoke run of three SWE-bench Lite issues scored bare haiku-4.5 at 3/3 and haiku+ADD at 2/3 — the small model over-built and broke two adjacent tests because the loop checked only its own task's tests, not the host suite ([SWE smoke report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-swe-smoke.md)). The diagnosis became method — every task now declares a `regression:` command for the host suite — and the re-run scored 3/3 ([atomic remeasure](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-atomic-remeasure.md)).

## The bottom line

- Choose **spec-kit** for small, friendly, strong-model projects you re-read yourself, where cost dominates.
- Choose **ADD** when any of these is yes: will this run autonomously? will a weaker model touch it? will the spec change hands or live for months? does anyone need to *check* — not trust — that what shipped is what was promised?

The agent is the hands. ADD is the memory, judgment and conscience — the part of the team that survives when the context window doesn't.
