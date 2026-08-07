# 15 · Foundations and lineage

[← 14 The foundation and the five living specs](./14-foundation.md) · [Contents](./README.md) · Next: [16 Releasing →](./16-releasing.md)

---

ADD did not appear from nowhere. It sits where four currents meet: the **recursive
self-improvement** thesis (AI that helps build the next AI), a decade of **autonomous and
agentic** research, the **spec-driven development** movement (the specification, not the
code, is the source of truth), and the **tests-first** discipline that constrains a
generate→check→refine loop with executable tests — turning fluent model output into
trustworthy software. This chapter tells that story; [Appendix G](./appendix-g-references.md)
is the verified source list it cites into. Every `[Author Year]` here resolves to an entry
there.

## The frame — "closing the loop"

Anthropic's recursive-self-improvement picture runs from autonomous agents delegating to
workers *today* toward a future where Claude improves Claude — *closing the loop* on the
work of building AI itself [Favaro & Clark 2026]. That is the backdrop ADD is built for, and
its position inside that picture is deliberately narrow: ADD is a **human-gated,
evidence-trusted** instance of recursive self-improvement. The AI drives the whole inner
cycle — specify → build → verify → observe — but a human owns the frozen contract and the
verify gate, and trust comes from passing tests and re-resolved evidence, never from a
diff that merely reads plausibly. The argument is not that the loop should stay open
forever; it is that the loop should be *bounded by human direction* rather than left to run
unattended [Amodei 2024]. ADD is one concrete shape for that bound.

## The four currents

**Recursive self-improvement.** The mathematical anchor is the Gödel machine — a
self-modifying agent that rewrites itself *only when it can prove the rewrite helps*
[Schmidhuber 2003]. ADD enforces the same discipline socially rather than formally: the
never-weaken-a-test rule is "only change on proof" expressed as a gate. The algorithmic kin
arrived later — a scaffolding program that improves the code that improves code
[Zelikman et al. 2023], a generate→critique→refine micro-loop [Madaan et al. 2023], agents
that keep verbal reflections and retry [Shinn et al. 2023], an agent that grows a reusable
skill library over time [Wang et al. 2023], and an evolutionary coder that beat a
long-standing matrix-multiplication record under continuous checking
[Novikov et al. 2025]. And where a self-rewarding loop has the model judge its own reward
[Yuan et al. 2024], ADD diverges by design — it makes the tests and a human the reward
signal, not the model's own opinion.

**Autonomous and agentic workflows.** The architecture vocabulary comes from the canonical
taxonomy of prompt-chaining, routing, orchestrator-workers, and the evaluator-optimizer loop
[Schluntz & Zhang 2024] — where evaluator-optimizer *is* build→verify→refine and
orchestrator-workers is ADD's wave parallelism. Underneath it sit the base agent loop of
interleaved think→act→observe [Yao et al. 2022], the self-supervised tool use that lets an
agent run its own tests and builds [Schick et al. 2023], and the designed agent–computer
interface that materially lifts autonomous issue resolution [Yang et al. 2024] — the role
ADD's `add.py` engine plays for the method. The production reports close the gap from theory
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
"Done" means the tests pass — which is exactly how ADD gates a feature. The safety framing
completes the current: human control and transparency made concrete [Anthropic 2025c], under
a governance ceiling that grows *more* binding, not less, as the loop gets more capable
[Anthropic 2026b].

## Where ADD diverges

The shared lineage is real, but ADD is not a re-skin of its siblings. spec-kit stops at
`implement`; GSD ends at verify. ADD closes the loop past both by adding three things
neither spec-kit [GitHub 2025] nor GSD [GSD 2025] carries as a first-class gate:

- a **failing-tests-first gate** — no build starts until the tests are red for the right
  reason, so the contract is proven executable before any code exists;
- an **observe → `fold`** step — confirmed lessons learned consolidate back into a versioned
  foundation, so the method improves itself across loops (retrospective consolidation is the
  recursive-self-improvement current turned inward on ADD);
- a **dynamic goal-loop** — the engine holds a milestone open and reopens tasks until its
  exit criteria are met, rather than declaring done when a checklist empties.

ADD also deliberately targets **less doc-time than GSD** — a lean foundation and one human
approval per task instead of a document per phase. The tests-first gate, the `fold`, and the
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
contribution: the frozen contract, the never-weaken-a-test rule, the evidence-over-inspection
gate, and the security HARD-STOP that no autonomy level may auto-pass [Anthropic 2025c],
held beneath the responsible-scaling governance ceiling [Anthropic 2026b]. As the loop grows
more capable, those gates and the human-owned verify matter more, not less. ADD is the human-gated, evidence-trusted way to stand inside the
closing loop and still own the result.
