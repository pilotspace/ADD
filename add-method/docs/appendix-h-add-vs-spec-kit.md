# Appendix H · ADD vs spec-kit — the honest comparison

> **The one-sentence version: spec-kit's discipline is advisory; ADD's is
> enforced.** On easy ground both produce equal measured outcomes — ADD is what
> you keep when the ground stops being easy.

This page is the canonical answer to "why would I use ADD instead of spec-kit
(or any spec-first prompt kit)?" It is deliberately honest — including where
spec-kit wins — because a comparison you can't trust is worthless, and trust is
literally the product.

## What we measured (and published, including our own retraction)

We ran the same six-milestone evolving project (CRUD → business rules + auth →
a breaking API-shape change → filters/pagination/recurring → a cross-cutting
rooms refactor → correctness hardening) through both flows under a pinned model
with deterministic probe scoring — no LLM judge. Full data:
[the campaign report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md).

**Where both flows tied.** With a fresh agent session per milestone resuming
from on-disk state, BOTH flows held every trust floor — requirement coverage
1.0, zero regressions, zero test-gaming — across all six milestones. A
first-edition claim that spec-kit collapsed under evolution was traced to a
defect in our own meter and publicly retracted.

**Where spec-kit wins.** Cost, on friendly ground: ~$1.42–1.68 per milestone vs
ADD's ~$2.58–2.92 (≈1.7–1.8×) at equal measured trust, with fewer artifacts and
less ceremony. If your project is small, single-component, driven by a strong
model, and you personally re-read everything anyway — spec-kit is a rational
choice, and we say so.

**Where the campaign's real finding lives.** Context rot: when ONE continued
conversation carried the milestones, *both* flows decayed identically
(coverage .92 → .80 → .75), locking in an early spec violation for five further
milestones — the agent's memory of its own past decisions outranked the written
spec, in every flow tried. Restarting each milestone from disk eliminated the
decay in every measured cell. The lesson is method-agnostic: **your on-disk
state must be good enough to restart from, every time** — and the deciding
question between flows is what happens when a restart, a weaker model, or a
tempted agent meets your discipline.

## The structural difference: checked, not suggested

spec-kit is templates and prompts — a constitution, spec documents, a plan
format. Nothing *stops* the agent from editing a spec to match what it built,
weakening a failing test, or letting a security finding scroll past. ADD runs a
state kernel that mechanically enforces the floor:

| Guarantee | ADD | spec-kit |
|---|---|---|
| Frozen contract can't be silently edited | tripwire → `contract_tampered`; recovery is a human-visible re-cross | nothing prevents it |
| Tests can't be quietly weakened to reach green | tamper detection on the frozen red suite at the gate | nothing prevents it |
| Security findings can't be waved through | `HARD-STOP` — unstrikeable in every mode, including fully-autonomous lanes | convention only |
| Work produces a verdict | every verify records `PASS` / `RISK-ACCEPTED` / `HARD-STOP` — an audit trail | produces specs, not verdicts |
| The human signature has a defined seam | exactly ONE approval, at the contract freeze | undefined |
| Resume is a primitive | `add.py status` is the resume point; state lives on disk | re-read the documents |
| Spec evolution is an operation | living 5-DD specs + `delta-append`, compacted forward | per-feature docs that drift |
| The method adapts to the project | personas propose each task's lane; outcomes are traced; the loop reflects (GEPA) | static templates |
| Team & lifecycle layer | git-native multi-user, waves, components, graduate/release gates | not in scope |

## When the enforcement should matter (testable predictions)

Enforcement is insurance, and our friendly campaign never made anyone crash.
The regimes where the guarantees are predicted — measurably — to separate the
flows:

1. **Weaker or cheaper models** — discipline substituting for model quality is
   ADD's best-value case (and it attacks the cost gap from both sides).
2. **Hostile or tempting changes** — where the cheapest green is weakening your
   own tests; the tripwire exists for exactly the day conventions fail.
3. **Autonomous operation** — guarantees matter most when nobody is watching
   the diff scroll past.
4. **Long horizons, teams, multi-component repos** — where "re-read the docs"
   stops scaling and audit trails start mattering.

We publish these as predictions, not claims — the hard-case and small-model
tracks in [`benchmark/`](https://github.com/pilotspace/ADD/tree/main/benchmark)
are how they become numbers. When a prediction fails, the retraction gets
published the same way this page's first one was.

## The bottom line

- Choose **spec-kit** for small, friendly, strong-model, human-re-read
  projects where cost-per-milestone dominates.
- Choose **ADD** when the answer to any of these is yes: will this run
  autonomously? will a weaker model touch it? will the spec change hands or
  survive months? does anyone need *proof* — not vibes — that what shipped is
  what was promised?

The agent is the hands. ADD is the memory, judgment, and conscience — the part
of the team that survives when the context window doesn't.
