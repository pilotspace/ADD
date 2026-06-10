# Auto-gate eval fixtures

Labeled fixtures for `add.py eval` — they score the **consensus decision logic**
(the deterministic part of the independent-verifier auto-gate) against builds whose
correct verdict is known. This is red/green TDD applied to the AI gate's own
judgment, not just to the code.

Each fixture is one JSON file:

```json
{
  "verdicts": [
    { "lens": "wiring", "verdict": "pass", "evidence": "..." },
    { "lens": "concurrency-security", "verdict": "fail", "evidence": "race on balance", "security": false },
    { "lens": "contract-conformance", "verdict": "pass", "evidence": "..." }
  ],
  "label": "HARD-STOP"
}
```

- `verdicts` — the structured verdicts the three independent lenses would emit.
- `label` — the decision the gate **should** make: `PASS` · `HARD-STOP` · `ESCALATE`.

Run:

```bash
add.py eval --fixtures add-method/eval
```

`recall` is the safety metric: every seeded-bad build must be caught
(`missed-bad(fn) = 0`). Add a new fixture every time a real build slips through or
is wrongly blocked — the fixture set is how the gate's judgment is regression-tested.
