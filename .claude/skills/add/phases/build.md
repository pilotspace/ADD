# Build — AI writes the code (the beat you drive to green)

Objective: implement the feature so EVERY failing test — or, for a non-coding task, every §4
acceptance check — passes, without changing any test or the contract. This is the only phase the
AI leads; §1–§4 removed all ambiguity. Write code into `.add/tasks/<slug>/src/` (a non-coding
task writes its artifact to the path its §5 Scope declares).

## The reasoning discipline — build's slice of the arc (definitions: `phases/direction.md`)

**Fluent ≠ true** holds in code: a diff feels done in proportion to how much you wrote, not how
much you verified — a green you haven't refuted is a claim, not evidence. Run the arc per batch:

- **FRAME** — restate the batch's tests and the frozen §3 clause they cover before writing a line.
- **GROUND** — open every anchor before editing it; a recalled file/symbol/flag is `[PRIOR]`
  until re-confirmed against the live tree THIS session; a live read outranks memory.
- **REASON** — name the mechanism ("because…"), simulate one concrete input through the change
  before committing it; when a red survives a fix, hold a second hypothesis instead of patching harder.
- **ATTACK** — before presenting green: re-run the suite fresh, then reviewer-read your own diff
  hunting the cheap falsifying input (file · line · values). An earned green is one you tried to
  kill. Security findings stay HARD-STOP.
- **DELIVER** — the green report leads with the outcome and tags its claims: a pass you ran THIS
  session is `[OBSERVED]`; a remembered pass is `[PRIOR]` — never present it bare.
- **Constraint loop on the §5 Scope allowlist** — don't eyeball it: list the files actually
  touched (`git status` / diff) and check each against the declared Scope tokens mechanically
  before the gate; a miss is `scope_violation` — caught by you, not by the engine.
- **Follow-through (the Floor's second check)** — green tests ≠ the goal reached; simulate the
  human's end state once — run the artifact under the BARE declared runtime — before calling
  the batch done.

## Work in small batches

Pick ONE task-sized slice, restate its tests, implement, iterate to green —
each batch small enough to review in full.

## Declaring the scope of impact (Scope + Strategy)

§5's declarations are drafted with the bundle and frozen by the §3 approval — never invented mid-build:

- **Scope (may touch)** — the allowlist the build may write (backticked tokens); a file outside it is a **STOP → change request** back to Specify.
- **Strategy (ordered batches)** — the planned build order; guidance, not enforced.
- **Strategy facets** — Approach (domain strategy) · Data strategy · Pattern · Optimization stance: the domain HOW, anchored upstream (§1 Framings · §3 Schema · CONVENTIONS.md Honors), drafted at tests->build in the Persona's domain vocabulary; ⚠-mark the facet you trust least (risk: high → spawn `add-advisor`, advise-midflight mode). Advisory, never a gate.

Enforced: a completing verify gate refuses an out-of-scope build (`scope_violation` → self-heal).

## Persona overlay (optional)

Load the active `.add/personas/<slug>.md` as a domain **overlay** atop `SOUL.md` (SOUL = voice/trust; persona = domain **stance**) — name it in §5; its domain supplies the facet vocabulary. SOUL.md is **human-owned**: the overlay never rewrites it (voice deltas: `deltas.md`). Advisory — it never lowers a gate; security still **HARD-STOPs**.

## A red outside your suite — locate first

`add.py locate path::test_name`, never a blind fix. **in-node** — a live task owns it;
coordinate. **interface-regression** — you broke a DONE task's contract: fix the breaker; a
contract change is a change request, the printed closure names who re-verifies. **unowned** —
host/foreign surface = your §3 Regression floor; keep it green. A §4 `covers:` map quotes the
frozen §3 clause — repair the clause, not the symptom.

## The cardinal rule

**Never weaken or delete a test to make it pass, and never edit the frozen
contract.** A genuine need to change either is a change request back to Specify. Honor the §5 safety rule (e.g. atomic balance update).

## Exit gate

<exit_gate>
- [ ] All tests (or §4 acceptance checks) pass.
- [ ] Coverage did not decrease.
- [ ] No test and no contract modified by the AI.
- [ ] No dependency outside the allow-list.
- [ ] No file outside the declared §5 Scope was touched.
- [ ] Change small enough to review in full.
</exit_gate>

> **Advisor · Confidence** — delegate a well-scoped batch (the advisor spawn, `phases/verify.md`); self-score before presenting green, refine while cheap (the confidence self-score, `phases/direction.md`).

## Next

`python3 .add/tooling/add.py gate PASS` (from build — compound-crosses to verify in one call) → `phases/verify.md` on demand.
Book: `docs/07-step-5-build.md`.

> Under `autonomy: auto` Build and Verify run together as one evidence-auto-gated run. See `run.md`.
>
> **Honest redo.** A confirmed cheat returns the task HERE — revert the tampered file or de-overfit src, then advance again (the bounded self-heal loop, `run.md`; capped, then HARD-STOPs to the human). Never weaken a test or edit the frozen contract to pass.

## The self-improving map — every loop feeds four artifacts

You emit `open`; the human confirms; the engine transcribes — **nothing self-approves**. Emission
lives in observe (§7); every earlier step feeds it: ground surprises → §1 · the freeze's ⚠ flag →
the next spec · a red-suite gap → a TDD lesson · build's strategy-actually-used → the ADR block ·
verify residue → a SPEC delta.

| what improves | grammar (closes `(evidence: …)`) | consolidator |
|---|---|---|
| the living specs — `.add/specs/` | `[DDD\|SDD\|UDD\|TDD\|ADD · open] lesson` | `add.py delta-append <dd>` |
| personas — the agents' stances | `… · persona:<slug> · critical-rule\|success-metric\|anti-pattern\|ability` | the persona loop |
| `SOUL.md` — your voice | a voice delta, `open` | human rewrite (`deltas.md`) |
| the next scope | `[SPEC · open]` → seeded · dropped · carried | `loop.md` → `new-task` |

Routing: `ddd`→domain · `sdd`→system · `udd`→experience · `tdd`→quality · `add`→method — each
lands in-flight in its living spec via `add.py delta-append <dd>` (grammar: `deltas.md`). A
HOW-an-agent-behaves lesson → a persona, not the shared pile. Deltas prepend newest-first;
the spec diff is the receipt. Self-score before emitting (the confidence six dimensions; name the weakest, refine).
