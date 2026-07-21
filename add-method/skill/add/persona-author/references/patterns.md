# The judgment layer — distilled from strong subagent design

Nine patterns that separate an expert lens from an undifferentiated keyword list. Each is drawn
from an apple-to-apple read of strong agent files (senior-rust/-java engineers, python-expert,
module-doc-generator, component-tracer, ux-design-architect, and peers) and cast for an ADD
persona. Contract (which section) → `references/contract.md`; this file is *how to fill it well*.

## Contents
1. Earned-perspective Identity
2. Bold-lead Critical Rules
3. The qualification gate
4. Read-before-you-assert
5. Failure-mode-aware Success Metrics
6. ORIENT-first Abilities
7. Design-for-failure (conditional)
8. Guilty-until-proven Anti-patterns
9. Deliberate exclusions — what NOT to put in a persona

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

## 3. The qualification gate
The single sharpest transferable stance. Before elaborating, name the simplest baseline that meets
the contract; if it wins, take it and STOP. Cleverness is a tax the project pays forever.
- ✓ Critical Rule: "**Simplest baseline first** — if a plain table + unique index meets the
  contract, ship that; an event-sourced ledger earns its keep or it's a tax."

## 4. Read-before-you-assert
The reporting agents (module-doc, component-tracer) make this a hard rule: never cite a file,
symbol, or line you have not opened. In an ADD persona it is an Anti-pattern:
- ✓ "a claim resting on a file/symbol not opened → open it or cut the claim."
This mirrors the add-worker floor ("never invent a file you have not opened") — the persona makes
it a domain instinct, not just a boundary.

## 5. Failure-mode-aware Success Metrics
A metric is only expertise if it names the way of being wrong it catches. State each as an
INVARIANT (true as the project grows), paired with its failure mode.
- ✗ "High test coverage; good performance."
- ✓ "**No double-post under retry** — a replayed request leaves the ledger byte-identical (catches
  the un-idempotent write); **p95 < 150 ms at 100 rps** (catches the N+1 that only shows under load)."

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
scars produced.
- ✓ "'0 issues found' on a first pass → look harder."
- ✓ "an abstraction with no second caller → cut it."
- ✓ "a 'temporary' manual retry in a hot path → it will become the retry policy; design it now."

## 9. Deliberate exclusions — what NOT to put in a persona
A persona is a layer in a stack; keep the other layers' work OUT of it.
- **No tone/voice** — that is SOUL.md's. A persona that prescribes phrasing is duplicating it.
- **No self-score / confidence rubric** — the agent (add-worker) owns the six-dimension score.
- **No output skeleton** — the deliverable's shape is the agent's Return contract, not the lens's.
- **No stakes/CoT priming** ("take a deep breath", "$500 tip") — motivation is the agent's; the
  persona supplies judgment, not pep talk.
Every line you cut from these categories makes the judgment that remains sharper.
