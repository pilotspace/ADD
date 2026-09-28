# 15 · Foundations and lineage

[← 14 The foundation and the five living specs](./14-foundation.md) · [Contents](./README.md) · Next: [16 Releasing →](./16-releasing.md)

---

ADD did not appear from nowhere. It sits where four currents meet: the **recursive
self-improvement** thesis (AI that helps build the next AI), a decade of **autonomous and
agentic** research, the **spec-driven development** movement (the specification, not the
code, is the source of truth), and the **tests-first** discipline that constrains a
generate→check→refine loop with executable tests. This chapter tells that story, then the
method's *own* story: how it went from **AIDD 2.x** through **ADD 3.x** to the skill-only
**ADD 4.0**, and what each step retired. [Appendix G](./appendix-g-references.md) is the
verified source list; every `[Author Year]` here resolves to an entry there.

## The frame — "closing the loop"

Anthropic's recursive-self-improvement picture runs from autonomous agents delegating to
workers *today* toward a future where Claude improves Claude — *closing the loop* on the
work of building AI itself [Favaro & Clark 2026]. ADD's position inside that picture is
deliberately narrow: an **evidence-trusted** instance of the loop. The AI drives the whole
inner cycle — direction → build → verify → learn — but trust comes from checks sealed before
the build and run fresh after it, never from a diff that merely reads plausibly, and a human
owns the direction and reviews every decision the agent took. The argument is not that the
loop should stay open forever; it is that it should be *bounded by human direction* rather
than left to run unread [Amodei 2024].

## The four currents

**Recursive self-improvement.** The mathematical anchor is the Gödel machine — a
self-modifying agent that rewrites itself *only when it can prove the rewrite helps*
[Schmidhuber 2003]. ADD enforces the same discipline socially rather than formally: the
never-weaken-a-sealed-check rule is "only change on proof". The algorithmic kin arrived
later — a scaffolding program that improves the code that improves code
[Zelikman et al. 2023], a generate→critique→refine micro-loop [Madaan et al. 2023], agents
that keep verbal reflections and retry [Shinn et al. 2023], an agent that grows a reusable
skill library over time [Wang et al. 2023], and an evolutionary coder that beat a
long-standing matrix-multiplication record under continuous checking
[Novikov et al. 2025]. Where a self-rewarding loop has the model judge its own reward
[Yuan et al. 2024], ADD diverges by design — the sealed checks and a human reviewer are the
reward signal, not the model's own opinion.

**Autonomous and agentic workflows.** The architecture vocabulary comes from the canonical
taxonomy of prompt-chaining, routing, orchestrator-workers, and the evaluator-optimizer loop
[Schluntz & Zhang 2024] — evaluator-optimizer *is* build→verify→refine, and
orchestrator-workers is ADD's parallel worktrees. Underneath sit the base agent loop of
interleaved think→act→observe [Yao et al. 2022], the self-supervised tool use that lets an
agent run its own tests [Schick et al. 2023], and the designed agent–computer interface
that lifts autonomous issue resolution [Yang et al. 2024] — the role ADD's task file and
commit conventions play. The production reports close the gap to practice: checkpoints,
subagents and rollback for autonomous work [Anthropic 2025a], and a lead orchestrating
subagents under an LLM judge [Anthropic 2025b].

**Spec-driven development.** ADD's closest siblings are explicit specification systems.
GitHub's **spec-kit** runs `constitution` → `specify` → `plan` → `tasks` → `implement` with
the spec as the executable source of truth [GitHub 2025]; its launch framed task
decomposition as "TDD for your AI agent" [Delimarsky 2025], and its rationale named the
failure spec-driven work exists to solve — context degrading over a long session
[Vesely 2025]. The academic vocabulary followed, with a taxonomy of Spec-First,
Spec-Anchored and Spec-as-Source rigor [Piskala 2026], and the pattern is converging across
vendors [InfoQ 2025]. Nearest of all is **GSD** — a spec-driven, context-engineering system
for the same Claude Code niche [GSD 2025].

**Tests-first and verification.** Supplying tests alongside the prompt measurably lifts
pass rates [Mathews & Nagappan 2024], and the field's yardstick judges a fix solely by
whether the project's own tests pass [Jimenez et al. 2023]. "Done" means the checks pass —
which is exactly how ADD verifies a change. The safety framing completes the current: human
control and transparency made concrete [Anthropic 2025c], under a governance ceiling that
grows *more* binding as the loop gets more capable [Anthropic 2026b].

## From AIDD to ADD 4.0 — the lineage inside the method

ADD is also the current cut of a method that has changed its own mind in the open. Naming
what was retired, and why, is the honest way to earn the claim this book makes everywhere
else: that it teaches only what the method does.

- **AIDD 2.x — documents and a state file.** Working state lived in a `state.json` treated
  as the source of truth, beside a per-feature plan cut into fixed sections and a set of
  standalone foundation files. A state file as truth needs merge-conflict detection,
  migration code and reconciliation, and hand-written summaries drift from what they
  summarise within a day. It also set autonomy with one global switch and graduated projects
  through fixed stages.
- **ADD 3.x — an engine.** 3.x replaced all of that with the lean `.add/` bundle — files
  are the state, one task file per change — and a stdlib-Python notary engine with a CLI of
  some thirty verbs that stamped freezes, recorded run receipts and refused a verdict it
  could not back. It replaced the autonomy switch with a per-task sensitivity floor and
  stages with lanes, and it put one human approval at the freeze.
- **ADD 4.0 — one skill.** 4.0 removed the engine and the approval. Measured against
  vanilla prompting and against spec-kit at comparable fidelity, 3.x cost roughly 3.5–4× the
  former and 1.8× the latter per unit of work, and a large share of the agent's turns went to
  driving the ceremony rather than doing the work. What the engine protected turned out to be expressible with what every
  repository already has: the seal is a git commit, the receipt is real command output
  written into the task file, the verdict is a line a reviewer can re-run, and the human's
  review moved from a mid-run approval to a report of every assumption taken. The full
  account, with its citations, is [20 · What changed in 4.0](./20-whats-new-in-4.md).

The through-line: every mechanism was retired because a leaner one does the same job with
less that can rot. What survived every cut is the spine — direction before speed, evidence
over inspection, never weaken a check to pass, and the security HARD-STOP.

## Where ADD diverges

The shared lineage is real, but ADD is not a re-skin of its siblings. spec-kit stops at
`implement`; GSD ends at verify. ADD adds three things neither spec-kit [GitHub 2025] nor
GSD [GSD 2025] carries as a first-class step:

- **red checks first, sealed** — no build starts until the checks fail for the right
  reason, and the checks are committed with the contract so any later weakening shows in
  `git diff`;
- **assumptions on the record** — every silence the agent filled is written down with its
  cost, and that list is what the human reviews;
- **a goal-held milestone and a learning loop** — a milestone stays open until its exit
  criteria are met with evidence, and lessons with evidence are promoted into binding
  decisions that shape the next task.

## The evidence chain — the loop already runs

The case that this is not speculative rests on three measured facts. The length of work
models complete unaided keeps doubling [Favaro & Clark 2026]. By 2026 more than 80% of the
code merged at Anthropic was Claude-authored [Favaro & Clark 2026]. And nine parallel Claude
agents recovered roughly 97% of the human-expert gap on an alignment task in five days
against the human team's seven [Anthropic 2026a] — parallel agents working under review,
which is ADD's parallel-plus-verify shape. The loop already runs.

What it does *not* yet supply is the discipline to trust the output. That is ADD's
contribution: the sealed checks, the never-weaken rule, evidence over inspection, and the
security HARD-STOP that is never accepted as a risk [Anthropic 2025c], held beneath the
responsible-scaling governance ceiling [Anthropic 2026b].
