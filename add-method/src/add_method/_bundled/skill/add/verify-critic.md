# Verify — independent verification (Generator–Verifier separation)

Self-critique in the same context that wrote the code is unreliable: a model
favours its own output (self-enhancement bias) and repeats its own errors, so
an in-context "skeptic" approves it uncritically. ADD makes the skeptic **structurally
independent** — the auto-gate decision is computed by the engine from structured
verdicts produced by **fresh, context-isolated verifier subagents**, not by the
builder reconsidering its own work.

## How the auto-gate verifies (`autonomy: auto`)

Spawn each verifier as a **fresh subagent with an isolated context**. Give it
ONLY:

- §3 CONTRACT · §4 TESTS · the diff / `src/` · CONVENTIONS.md.

Never give it the build conversation, your reasoning, or why you think the code is
right. Its job is to **refute**, not to agree.

Run **three independent lenses** (one subagent each — they do not see each other):

- `wiring` — is every new symbol referenced and reachable? any dead end left behind?
- `concurrency-security` — races/timing under parallel use; secrets, injection,
  invented/unexpected dependencies. A security finding is **always** HARD-STOP.
- `contract-conformance` — does observable behaviour match §3 exactly, including
  every rejection path?

Each subagent returns exactly **one structured verdict**:

<verdict>
{ "lens": "wiring",
  "verdict": "pass" | "fail" | "risk",
  "evidence": "what it actually observed (required — no shallow 'looks good')",
  "refutation": "the strongest counter-argument it tried, and the result",
  "security": false }
</verdict>

Record each verdict, then read the decision — **the engine computes it, never you:**

```bash
add.py verdict <slug> --lens wiring --verdict pass \
  --evidence "every new symbol is called; dead-code scan clean" \
  --refutation "looked for an unreachable export — none"
add.py verdict <slug> --lens concurrency-security --verdict pass --evidence "..."
add.py verdict <slug> --lens contract-conformance --verdict pass --evidence "..."

add.py consensus <slug>          # PASS | HARD-STOP | ESCALATE
```

Map the consensus to the gate — do not second-guess it:

| `consensus` | Meaning | Action |
|-------------|---------|--------|
| `PASS` | ≥3 independent lenses agree, none refuted | `add.py gate PASS` |
| `HARD-STOP` | any refutation, or any security finding | `add.py gate HARD-STOP` → return to Build |
| `ESCALATE` | residue (a `risk`) or coverage too thin | human-led gate — **no auto-PASS** |

**Auto-PASS requires `add.py consensus` == `PASS`.** A green test suite alone never
auto-passes — structural independence is the evidence the run still owes.

## Measuring the gate itself (data layer)

Recorded verdicts are durable, labelled data — not throwaway chat. Score the
decision logic against known-good and seeded-bad fixtures:

```bash
add.py eval --fixtures .add/eval
```

A fixture is `{ "verdicts": [...], "label": "PASS|HARD-STOP|ESCALATE" }` — the
decision the gate *should* make for a known build. `recall` is the safety metric:
every seeded-bad build must be caught (`missed-bad(fn) = 0`). This is red/green TDD
applied to the AI gate's own judgment, not just to the code.
