# 15 · Foundations and lineage

[← 14 The foundation and the five living specs](./14-foundation.md) · [Contents](./README.md) · Next: [16 Releasing →](./16-releasing.md)

---

ADD did not appear from nowhere. It sits where four currents meet: the **recursive
self-improvement** thesis (AI that helps build the next AI), a decade of **autonomous and
agentic** research, the **spec-driven development** movement (the specification, not the
code, is the source of truth), and the **tests-first** discipline that constrains a
generate→check→refine loop with executable tests — turning fluent model output into
trustworthy software. This chapter tells that story, and then the method's *own* story: how
the earlier **AIDD 2.x** line became **ADD 3.0**, and what 3.0 retired to get there.
[Appendix G](./appendix-g-references.md) is the verified source list it cites into. Every
`[Author Year]` here resolves to an entry there.

## The frame — "closing the loop"

Anthropic's recursive-self-improvement picture runs from autonomous agents delegating to
workers *today* toward a future where Claude improves Claude — *closing the loop* on the
work of building AI itself [Favaro & Clark 2026]. That is the backdrop ADD is built for, and
its position inside that picture is deliberately narrow: ADD is a **human-gated,
evidence-trusted** instance of recursive self-improvement. The AI drives the whole inner
cycle — direction → build → verify → observe — but a human owns the frozen contract and the
verify gate, and trust comes from passing checks and re-resolved evidence, never from a
diff that merely reads plausibly. The argument is not that the loop should stay open
forever; it is that the loop should be *bounded by human direction* rather than left to run
unattended [Amodei 2024]. ADD is one concrete shape for that bound.

## The four currents

**Recursive self-improvement.** The mathematical anchor is the Gödel machine — a
self-modifying agent that rewrites itself *only when it can prove the rewrite helps*
[Schmidhuber 2003]. ADD enforces the same discipline socially rather than formally: the
never-weaken-a-check rule is "only change on proof" expressed as a gate. The algorithmic kin
arrived later — a scaffolding program that improves the code that improves code
[Zelikman et al. 2023], a generate→critique→refine micro-loop [Madaan et al. 2023], agents
that keep verbal reflections and retry [Shinn et al. 2023], an agent that grows a reusable
skill library over time [Wang et al. 2023], and an evolutionary coder that beat a
long-standing matrix-multiplication record under continuous checking
[Novikov et al. 2025]. And where a self-rewarding loop has the model judge its own reward
[Yuan et al. 2024], ADD diverges by design — it makes the checks and a human the reward
signal, not the model's own opinion.

**Autonomous and agentic workflows.** The architecture vocabulary comes from the canonical
taxonomy of prompt-chaining, routing, orchestrator-workers, and the evaluator-optimizer loop
[Schluntz & Zhang 2024] — where evaluator-optimizer *is* build→verify→refine and
orchestrator-workers is ADD's wave parallelism. Underneath it sit the base agent loop of
interleaved think→act→observe [Yao et al. 2022], the self-supervised tool use that lets an
agent run its own tests and builds [Schick et al. 2023], and the designed agent–computer
interface that materially lifts autonomous issue resolution [Yang et al. 2024] — the role
ADD's `add` engine plays for the method. The production reports close the gap from theory
to practice: checkpoints, subagents, and rollback for autonomous work [Anthropic 2025a], and
a lead orchestrating subagents under an LLM judge [Anthropic 2025b].

**Spec-driven development.** ADD's closest siblings are explicit specification systems.
GitHub's **spec-kit** runs `constitution` → `specify` → `plan` → `tasks` → `implement` with
the spec as the executable source of truth [GitHub 2025]; its launch framed task
decomposition as "TDD for your AI agent" [Delimarsky 2025], and its rationale named the
failure spec-driven work exists to solve — context degrading over a long session
[Vesely 2025]. The academic vocabulary followed, with a taxonomy of Spec-First,
Spec-Anchored, and Spec-as-Source rigor [Piskala 2026], and the pattern is converging across
vendors [InfoQ 2025]. Nearest of all is **GSD** — a spec-driven, context-engineering system
for the same Claude-Code niche [GSD 2025].

**Tests-first and verification.** The empirical backbone is direct: supplying tests
alongside the prompt measurably lifts pass rates [Mathews & Nagappan 2024], and the field's
yardstick judges a fix solely by whether the project's own tests pass [Jimenez et al. 2023].
"Done" means the checks pass — which is exactly how ADD gates a feature. The safety framing
completes the current: human control and transparency made concrete [Anthropic 2025c], under
a governance ceiling that grows *more* binding, not less, as the loop gets more capable
[Anthropic 2026b].

## From AIDD to ADD — the lineage inside the method

ADD is not only heir to the field; it is the current cut of a method that has changed its
own mind in the open. Its earlier form was **AIDD** — AI-Driven Development, the 2.x line —
and much of what 2.x carried is **no longer** in the shipped 3.0 engine. Naming what was
retired, and why, is the honest way to earn the claim this book makes everywhere else: that
the book teaches only what the package does. The brand is now **ADD**; **AIDD** is the
earlier name this one chapter preserves so the lineage stays legible.

- **The file model.** AIDD 2.x kept its working state in a `state.json` treated as the
  source of truth, alongside a per-feature `PLAN.md` cut into fixed sections `§0–§7`, plus
  standalone foundation files — `PROJECT.md`, `MILESTONE.md`, `CONVENTIONS.md`,
  `SETUP-REVIEW.md` — and a `dependencies.allowlist`. That model paid a tax: a
  `state.json`-as-truth needs merge-conflict detection, forward-migration code, and a
  doc↔state reconciliation pass, and a hand-authored summary file drifts from the nodes it
  summarises within a day. ADD 3.0 **replaced** all of it with the lean `.add/` bundle
  (ABF-1): **files are the database**, each entity one markdown file with frontmatter, and
  `graph.json` is a rebuildable cache, never trusted over the files. The `§0–§7` plan is
  **retired** in favour of one atomic task node (`CARD · RULES · PLAN · CHECKS · EVIDENCE ·
  LESSONS`); the standalone foundation files are **gone**, absorbed into `.add/index.md` and
  the five living specs ([14](./14-foundation.md)).

- **The autonomy ladder.** 2.x set how far the AI could run unattended with an explicit
  `autonomy: auto | conservative | manual` switch — a single global mode. ADD 3.0
  **retired the autonomy ladder** and replaced the global switch with a per-task
  **sensitivity floor**: `mechanical → process`, `data | architecture → plan`,
  `security → human`, computed by the engine from *what the task touches*, never flipped as
  a mode ([01](./01-principles.md), [09](./09-governance.md)). Trust is earned per scope,
  not granted globally.

- **Stages and graduation.** The earlier method graduated a project's rigor through fixed
  stages (prototype → poc → mvp → production) with a graduation ceremony and a graduation
  report. ADD 3.0 **dropped stage graduation** as a ceremony: sizing now happens at intake
  through three **lanes** — quick · task · project/milestone — and the **depth dial**
  (quick · standard · deep) tunes ceremony per task. Neither lane nor depth ever changes
  authority; only the sensitivity floor does ([07](./07-setup-and-lanes.md)).

- **The ADR harvest and the ship-review.** 2.x harvested Architecture Decision Records into
  a Decisions ledger and ran a dedicated ship-review before release. Both are **no longer**
  separate rituals. Decisions now live inline in each spec's `## Decisions that bind`;
  review is the ordinary **verify** beat with its three residue lenses and its bound
  receipt — there is **no** separate ship-review gate, and releasing is the goal-gated
  milestone close ([16](./16-releasing.md)), not a distinct review stage.

- **Roles.** 2.x modeled the team as a fixed org chart of titles. ADD 3.0 **replaced** the
  chart with **personas** — project-fit lenses the agent adopts, seeded → grown → applied,
  that carry a domain's judgment without pretending an AI sits in a chair
  ([10](./10-personas.md), [18](./18-personas.md)).

The through-line: every one of these was retired because a leaner mechanism does the same
job with less that can rot. What survived is the spine — direction before speed, evidence
over inspection, the security HARD-STOP — carried now on a bundle small enough never to rot
the context it lives in.

## Where ADD diverges

The shared lineage is real, but ADD is not a re-skin of its siblings. spec-kit stops at
`implement`; GSD ends at verify. ADD closes the loop past both by adding three things
neither spec-kit [GitHub 2025] nor GSD [GSD 2025] carries as a first-class gate:

- a **red-checks-first gate** — no build starts until the checks are red for the right
  reason, so the contract is proven executable before any code exists;
- an **observe → `fold`** step — confirmed lessons consolidate back into a versioned
  foundation, so the method improves itself across loops (retrospective consolidation is the
  recursive-self-improvement current turned inward on ADD);
- a **dynamic goal-loop** — the engine holds a milestone open and reopens tasks until its
  exit criteria are met, rather than declaring done when a checklist empties.

ADD also deliberately targets **less doc-time than GSD** — a lean foundation and one human
approval per task instead of a document per phase. The red-first gate, the `fold`, and the
goal-loop are ADD's contribution; everything beneath them is inherited.

## The evidence chain — the loop already runs

The case that this is not speculative rests on three measured facts. First, the task
time-horizon: the length of work models complete unaided keeps doubling [Favaro & Clark 2026].
Second, the authorship share: by 2026 more than 80% of the code merged at Anthropic was
Claude-authored [Favaro & Clark 2026]. Third, the **Automated Alignment Researchers** result:
nine parallel Claude agents recovered roughly 97% of the human-expert gap on an alignment task
in five days against the human team's seven [Anthropic 2026a] — parallel agents working under
review, which is precisely ADD's wave-plus-verify shape. The loop already runs.

What it does *not* yet supply is the discipline to trust the output. That is ADD's
contribution: the frozen contract, the never-weaken-a-check rule, the evidence-over-inspection
gate, and the security HARD-STOP that the engine never auto-passes [Anthropic 2025c],
held beneath the responsible-scaling governance ceiling [Anthropic 2026b]. As the loop grows
more capable, those gates and the human-owned verify matter more, not less. ADD is the
human-gated, evidence-trusted way to stand inside the closing loop and still own the result.
