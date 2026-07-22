# The judgment layer — distilled from strong subagent design

Eleven patterns that separate an expert lens from an undifferentiated keyword list. Each is drawn
from an apple-to-apple read of strong agent files (senior-rust/-java engineers, python-expert,
module-doc-generator, component-tracer, ux-design-architect, and peers) plus a diagnosis of the
vendored teacher corpus, and cast for an ADD persona. Contract (which section) →
`references/contract.md`; this file is *how to fill it well*.

## Contents
1. Earned-perspective Identity
2. Bold-lead Critical Rules
3. The qualification gate
4. Read-before-you-assert
5. Failure-mode-aware Success Metrics
6. ORIENT-first Abilities
7. Design-for-failure (conditional)
8. Guilty-until-proven Anti-patterns
9. Numbers you'd defend
10. Per-flow stance
11. Deliberate exclusions — what NOT to put in a persona

---

## 1. Earned-perspective Identity
Every strong agent opens not with a title but with *what it has seen*. State the domain depth AND
the scar that shapes its judgement.
- ✗ "You are a senior payments engineer with expertise in APIs."
- ✓ "…has shipped reconciliation systems where a single un-idempotent retry double-charged a
  customer, so it treats every write as replayable until proven otherwise."
The scar is what makes the later Anti-patterns feel inevitable rather than arbitrary.

## 2. Bold-lead Critical Rules
Lead each rule with a **bold clause**, then the why. Scannable beats prose. Keep it to what the
persona would actually *refuse to wave through* — not a wish list.
- ✗ "Always make sure to handle errors properly and think about idempotency."
- ✓ "**Every write is idempotent** — a retried request must not double-apply; key it or reject it."
When a rule is subtle, one ✗/✓ contrast pair teaches more than a paragraph — "follow best
practices" is useless; "wrap MobX components in `observer()` (see `RoleSkillCard.tsx:15`)" acts.

## 3. The qualification gate
The single sharpest transferable stance. Before elaborating, name the simplest baseline that meets
the contract; if it wins, take it and STOP. Cleverness is a tax the project pays forever.
- ✓ Critical Rule: "**Simplest baseline first** — if a plain table + unique index meets the
  contract, ship that; an event-sourced ledger earns its keep or it's a tax."
Its sibling move covers contradictory requirements ("minimal but feature-rich"): name the tension
and propose the balance with its cost — never silently satisfy one half. And perspective proves
itself by naming the losing option: *why this, not that — and why that loses*.

## 4. Read-before-you-assert
The reporting agents (module-doc, component-tracer) make this a hard rule: never cite a file,
symbol, or line you have not opened. In an ADD persona it is an Anti-pattern:
- ✓ "a claim resting on a file/symbol not opened → open it or cut the claim."
It binds outputs too: every path or example the persona's own deliverable cites must exist at the
named place — a placeholder that survives into the deliverable is the same defect. This mirrors
the add-worker floor ("never invent a file you have not opened") as a domain instinct.

## 5. Failure-mode-aware Success Metrics
A metric is only expertise if it names the way of being wrong it catches. State each as an
INVARIANT (true as the project grows), paired with its failure mode.
- ✗ "High test coverage; good performance."
- ✓ "**No double-post under retry** — a replayed request leaves the ledger byte-identical (catches
  the un-idempotent write); **p95 < 150 ms at 100 rps** (catches the N+1 that only shows under load)."
Each bar must be checkable IN-SESSION by the agent holding the lens — a behaviour it can observe
or a test it can run. An invented outcome statistic ("engagement +40%") sounds measured and never
was; it is the signature rot of weak persona corpora.

## 6. ORIENT-first Abilities
Lead the ability list with the 1–3 commands the lens RUNS on load before acting — `add.py status`,
the domain's suite, the diff to judge. Acting on ground truth beats re-deriving it. State every
other ability as something doable *now*, anchored to a real file/tool/command — not an aspiration.
- ✓ "can diff two response fixtures byte-for-byte to prove passthrough" (checkable)
- ✗ "understands API design deeply" (unfalsifiable)

## 7. Design-for-failure (conditional)
Any persona that owns I/O, network, or infra carries a design-for-failure ability: it can name the
**timeout · retry · circuit-breaker · rollback** for every external call. An unbounded await or a
silent half-write is a defect, never "expected". Omit this for pure design/docs lenses — forcing it
on a lens that touches no I/O is noise. Match the pattern to the persona's real surface.

## 8. Guilty-until-proven Anti-patterns
Distinct from Critical Rules (always-do): these are the smells the lens treats as *guilty until
proven innocent*, each with its default reaction. The sharpest are the instincts the Identity's
scars produced — and the strongest attach the COST to the smell:
- ✓ "'0 issues found' on a first pass → look harder."
- ✓ "an abstraction with no second caller → cut it."
- ✓ "PIL in production preprocessing → 3× slower than cv2; reach for cv2 first."
A smell with its price is an argument; a bare smell is a style opinion.

## 9. Numbers you'd defend
The cheapest bytes-per-judgment in strong agents: a named budget beats an adjective. "Optimize
performance" buys nothing; "p95 < 200 ms at the declared load", "44×44 px touch targets", "batch
wait ≤ 10 ms" anchor the lens to a bar it can hold a build to. Two conditions, or the number is
cosplay: the expert could defend WHY that number (name what breaks past it), and the lens can
check it in-session (see 5). Fake precision reads as measured and teaches the agent to invent —
worse than no number at all.

## 10. Per-flow stance
The strongest agents split behaviour by mode and bind a bookend to each — *reviewing opens with
the defect sweep; reimplementing opens with the qualification gate; explaining closes with failure
modes*. A persona claiming more than one `flow:` does the same in one or two lines: what it LEADS
with at build, what it REFUSES at verify. A verify stance carries the default verdict — NEEDS-WORK
until the evidence cites the actual run — plus its automatic-fail triggers. A lens whose rules
read identically at every flow hasn't decided what each surface is for.

## 11. Deliberate exclusions — what NOT to put in a persona
A persona is a layer in a stack; keep the other layers' work OUT of it.
- **No tone/voice** — that is SOUL.md's. A persona that prescribes phrasing is duplicating it.
- **No self-score / confidence rubric** — the agent (add-worker) owns the six-dimension score.
- **No output skeleton** — the deliverable's shape is the agent's Return contract, not the lens's.
- **No stakes/CoT priming** ("take a deep breath", "$500 tip") — motivation is the agent's; the
  persona supplies judgment, not pep talk.
- **No keyword taxonomy** — a page of noun-phrase bullets ("saga pattern, composite indexes, …")
  buys no behaviour; the model knows the words. Every bullet carries an opinion or it goes.
- **No tutorial code dumps** — framework boilerplate rots fast; a snippet earns its place only
  when it encodes a rule the prose can't.
- **No invented metrics or fabricated telemetry** — "+40% engagement", "47 pipelines deployed":
  numbers that sound measured train the lens to hallucinate finished-ness.
- **No adverb-padded checklists** — "documented thoroughly", "monitored comprehensively" are
  unverifiable filler wearing a checklist's clothes.
- **No other project's paths** — a persona anchors to THIS project's real files and commands;
  an inherited path from a seed source is contamination, not context.
Every line you cut from these categories makes the judgment that remains sharper.
