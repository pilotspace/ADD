# Appendix G — References & Lineage

ADD did not appear from nowhere. It sits at the meeting point of three currents:
the **recursive self-improvement** thesis (AI that helps build the next AI), the
**spec-driven development** movement (the specification, not the code, is the
source of truth), and a decade of **agentic + tests-first** research showing that
a generate→check→refine loop, constrained by executable tests, turns fluent model
output into trustworthy software. This appendix is the curated, verified grounding
for that lineage — every source below is reachable and annotated with a `↔ ADD:`
line saying exactly how it relates to the method.

**The frame — "closing the loop."** Anthropic's recursive-self-improvement picture
runs from autonomous agents delegating to workers *today* toward a future where
Claude improves Claude. ADD is a deliberately **human-gated, evidence-trusted**
instance of that loop: the AI drives spec→build→verify→observe, but a human owns the
frozen contract and the verify gate, and trust comes from passing tests and
re-resolved evidence — never from a plausible-looking diff. The sources here are
the shoulders that posture stands on.

The four sections below are the four currents. The comparison table places ADD next
to its two closest peers — GitHub's **spec-kit** and **GSD (Get Shit Done)** — and
names where ADD diverges. Read "How to cite" first; the rest of the book cites into
the keys defined here.

## How to cite

The book uses one inline citation form — **author-year** — and every entry's lead
`(Author Year)` *is* its cite-key. Resolve any inline `[…]` to the matching entry below.

| Authors | Inline form | Example |
|---|---|---|
| one author | `[Surname Year]` | `[Schmidhuber 2003]` |
| two authors | `[Surname & Surname Year]` | `[Mathews & Nagappan 2024]` |
| three or more | `[Surname et al. Year]` | `[Zelikman et al. 2023]` |
| an organisation | `[Org Year]` | `[Anthropic 2026a]` · `[GitHub 2025]` |
| several at once | joined by `; ` | `[Schmidhuber 2003; Zelikman et al. 2023]` |
| same author, same year | add a `Year`-letter suffix | `[Anthropic 2025a]` / `[Anthropic 2025b]` |

The 3+-author rule becomes **et al.**; an organisation stands in as the author
when no individual is credited; and when two org-authored sources collide on a year
(several Anthropic 2025/2026 items do, below) a trailing letter disambiguates them.
There is exactly one entry per cite-key.

## spec-kit ↔ ADD (and GSD)

ADD shares the spec-first DNA of GitHub's **spec-kit** and the Claude-Code,
context-rot-fighting niche of **GSD**. The phase models line up closely:

| ADD phase | spec-kit command | GSD phase |
|---|---|---|
| foundation · principles | `/speckit.constitution` → `constitution.md` | (project setup / `CLAUDE.md`-level) |
| §1 specify (what / why) | `/speckit.specify` → `spec.md` | **discuss** — capture decisions before planning |
| §3 contract (how, frozen) | `/speckit.plan` → `plan.md`, `contracts/` | **plan** — research, decompose, fit fresh context |
| milestone tasks / waves | `/speckit.tasks` → `tasks.md` | (phases → parallel waves) |
| §5 build | `/speckit.implement` | **execute** — parallel waves, fresh 200k-token context each |
| §6 verify | `/speckit.analyze` + `/speckit.checklist` | **verify** — walk what was built, fix before declaring done |

**Where ADD diverges.** spec-kit stops at `implement`; GSD ends at verify (GSD Core
adds a fifth *ship* phase). ADD closes the loop past both by adding three things
neither has as a first-class gate: a **failing-tests-first** gate (§4 — no build
starts until the tests are red for the right reason), an **observe→`fold`**
self-improvement step (§7 — confirmed learnings consolidate into a versioned foundation),
and an engine-tracked **dynamic goal-loop** that will hold a milestone open and
reopen tasks until its exit criteria are met. ADD also deliberately targets **less
doc-time than GSD** — a lean foundation and one human approval per task, rather than
a document per phase. The shared lineage is real; the tests-first gate, the `fold`,
and the goal-loop are ADD's contribution.

## 1. Recursive self-improvement

- **When AI builds itself** (Favaro & Clark 2026) — https://www.anthropic.com/institute/recursive-self-improvement — essay. The RSI thesis: by 2026 >80% of code merged at Anthropic was Claude-authored and the 50%-task time-horizon keeps doubling; recursive self-improvement would shift humans from builders to validators. ↔ ADD: the seed source — ADD is the human-gated, evidence-trusted way to run a spec→build→verify→observe loop while the human stays the validator.
- **Automated Alignment Researchers** (Anthropic 2026a) — https://www.anthropic.com/research/automated-alignment-researchers — research. Nine parallel Claude agents recovered ~97% of the human-expert gap on an alignment task in 5 days versus 7 for the human team. ↔ ADD: the strongest evidence the recursive loop is not speculative — parallel agents under review are exactly ADD's wave-plus-verify shape.
- **Machines of Loving Grace** (Amodei 2024) — https://www.darioamodei.com/essay/machines-of-loving-grace — essay. A "country of geniuses in a datacenter," argued with a measured, bounded position on recursive self-improvement. ↔ ADD: the intent framing behind milestoning — bound the loop with human direction rather than let it run open.
- **Gödel Machines: Self-Referential Universal Problem Solvers** (Schmidhuber 2003) — https://arxiv.org/abs/cs/0309048 — paper. A provably-optimal self-modifying agent that rewrites itself only when it can prove the rewrite helps. ↔ ADD: the mathematical anchor of the lineage — and a precedent for "only change on proof," which ADD enforces socially via the never-weaken-a-test rule.
- **STOP: Self-Taught Optimizer** (Zelikman et al. 2023) — https://arxiv.org/abs/2310.02304 — paper. A scaffolding program recursively improves the code that improves code. ↔ ADD: the algorithmic kin of the `fold` step — consolidate confirmed learnings back into the method that produced them.
- **Self-Refine: Iterative Refinement with Self-Feedback** (Madaan et al. 2023) — https://arxiv.org/abs/2303.17651 — paper. Generate→critique→refine with the same model lifts quality ~20% with no extra training. ↔ ADD: the micro-loop inside build→verify — produce, check against the contract, refine.
- **Self-Rewarding Language Models** (Yuan et al. 2024) — https://arxiv.org/abs/2401.10020 — paper. A model acts as its own reward judge to improve across iterations. ↔ ADD: the risk ADD answers — a self-judging loop needs an external gate; ADD makes tests and a human the reward signal, not the model's own opinion.
- **Reflexion: Language Agents with Verbal Reinforcement Learning** (Shinn et al. 2023) — https://arxiv.org/abs/2303.11366 — paper. Agents keep verbal reflections in episodic memory and retry, reaching 91% on HumanEval. ↔ ADD: the principle behind "reopen the task if criteria are unmet" — a failed check becomes feedback for the next attempt, not a dead end.
- **Voyager: An Open-Ended Embodied Agent with LLMs** (Wang et al. 2023) — https://arxiv.org/abs/2305.16291 — paper. An auto-curriculum agent that grows a reusable skill library over time. ↔ ADD: the growing foundation — each milestone's consolidated deltas are ADD's accumulating skill library.
- **AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery** (Novikov et al. 2025) — https://arxiv.org/abs/2506.13131 — paper. An evolutionary coding agent that beat a long-standing matrix-multiplication record and shipped a production scheduler improvement. ↔ ADD: the end-state evidence — a generate-and-verify loop can exceed human baselines when every candidate is checked.

## 2. Autonomous & agentic workflows

- **Building Effective Agents** (Schluntz & Zhang 2024) — https://www.anthropic.com/research/building-effective-agents — blog. The canonical taxonomy: prompt-chaining, routing, orchestrator-workers, and the evaluator-optimizer loop. ↔ ADD: the architecture cite — evaluator-optimizer is build→verify→refine; orchestrator-workers is ADD's wave parallelism.
- **Enabling Claude Code to work more autonomously** (Anthropic 2025a) — https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously — news. Checkpoints, subagents, hooks, background tasks, and `/rewind` rollback. ↔ ADD: checkpoint/rewind is the rollback strategy behind phase gates; hooks are where the engine enforces them.
- **How we built our multi-agent research system** (Anthropic 2025b) — https://www.anthropic.com/engineering/multi-agent-research-system — blog. An Opus lead orchestrating Sonnet subagents, with an LLM acting as judge, lifting task performance ~90%. ↔ ADD: the lead-plus-subagents-plus-judge pattern is exactly ADD's wave execution under a verify gate.
- **ReAct: Synergizing Reasoning and Acting in Language Models** (Yao et al. 2022) — https://arxiv.org/abs/2210.03629 — paper. Interleaving think→act→observe turns a model into an agent. ↔ ADD: the base loop every ADD phase runs on.
- **Toolformer: Language Models Can Teach Themselves to Use Tools** (Schick et al. 2023) — https://arxiv.org/abs/2302.04761 — paper. Self-supervised learning of when and how to call external tools. ↔ ADD: the capability that lets an agent run its own tests, linters, and builds — the evidence ADD trusts.
- **SWE-agent: Agent–Computer Interfaces Enable Automated Software Engineering** (Yang et al. 2024) — https://arxiv.org/abs/2405.15793 — paper. A designed agent–computer interface materially improves autonomous issue resolution. ↔ ADD: the structured agent↔environment contract — ADD's `add.py` engine is that interface for the method.
- **The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery** (Lu et al. 2024) — https://arxiv.org/abs/2408.06292 — paper. A full idea→experiment→write→review research loop at ~$15 per paper. ↔ ADD: the research analog of ADD's loop — and a reminder that an automated reviewer is the weak link a human gate protects.

## 3. Spec-driven development & spec-kit

- **GitHub Spec Kit** (GitHub 2025) — https://github.com/github/spec-kit — repo. The reference SDD toolkit: the phase model is `constitution` → `specify` → `plan` → `tasks` → `implement`, with the spec as the executable source of truth. ↔ ADD: the closest spec-first sibling — ADD's specify and plan phases map onto specify and plan; see the comparison table for the divergence.
- **Spec-driven development with AI: get started with a new open-source toolkit** (Delimarsky 2025) — https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/ — blog. The spec-kit launch post; frames `tasks` as "TDD for your AI agent." ↔ ADD: independent articulation of why decomposing a spec into checkable units beats one big prompt.
- **Spec-driven development: using Markdown as a programming language when building with AI** (Vesely 2025) — https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/ — blog. Spec-as-source, with context-rot named as the failure SDD exists to solve. ↔ ADD: the rationale for the frozen contract — a stable written spec is what survives when the model's context degrades.
- **Get Shit Done (GSD)** (GSD 2025) — https://github.com/open-gsd/gsd-core — repo. A meta-prompting, context-engineering, spec-driven system for Claude Code; its `discuss` → `plan` → `execute` → `verify` cycle runs each phase in a fresh subagent context to fight context-rot (originally `gsd-build/get-shit-done`, now continued as GSD Core). ↔ ADD: ADD's closest peer — same Claude-Code, context-rot niche; ADD diverges with the tests-first gate, the observe→`fold` step, and the dynamic goal-loop, and aims for less doc-time than GSD.
- **Beyond Vibe Coding: Amazon Introduces Kiro, the Spec-Driven Agentic IDE** (InfoQ 2025) — https://www.infoq.com/news/2025/08/aws-kiro-spec-driven-agent/ — blog. Kiro structures work as requirements→design→tasks with execution hooks. ↔ ADD: cross-vendor confirmation that spec-first is converging across the industry, not a single-tool idea.
- **Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants** (Piskala 2026) — https://arxiv.org/abs/2602.00180 — paper. A taxonomy of SDD rigor — Spec-First, Spec-Anchored, Spec-as-Source — reporting human-refined specs can cut LLM code errors substantially, with BDD as SDD's ancestor. ↔ ADD: places ADD as "Spec-Anchored" and gives the academic vocabulary for the contract-freeze decision.

## 4. Tests-first & verification

- **Test-Driven Development for Code Generation** (Mathews & Nagappan 2024) — https://arxiv.org/abs/2402.13521 — paper. Supplying tests alongside the prompt measurably lifts pass rates on MBPP and HumanEval. ↔ ADD: the empirical backbone of the failing-tests-first gate — tests as the constraint that makes generation verifiable.
- **SWE-bench: Can Language Models Resolve Real-World GitHub Issues?** (Jimenez et al. 2023) — https://arxiv.org/abs/2310.06770 — paper. 2,294 real issues judged by whether the project's own tests pass; <2% solved at release. ↔ ADD: the yardstick that proves the point — "done" means the tests pass, which is exactly how ADD gates a feature.
- **Our framework for developing safe and trustworthy agents** (Anthropic 2025c) — https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents — news. Five principles: human control, transparency, alignment, privacy, and security. ↔ ADD: the frozen-contract gate and never-weaken-a-test rule are human control and transparency made concrete; the security HARD-STOP is the security principle.
- **Responsible Scaling Policy v3.0** (Anthropic 2026b) — https://www.anthropic.com/news/responsible-scaling-policy-v3 — policy. The AI Safety Level framework; ASL-3 governs autonomous R&D capability. ↔ ADD: the governance ceiling that makes ADD's discipline necessary — as the loop gets more capable, the gates and the human-owned verify matter more, not less.
