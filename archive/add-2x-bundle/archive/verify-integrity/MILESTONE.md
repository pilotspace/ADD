# MILESTONE: Verify integrity — prove the green was EARNED, not gamed

goal: A verify gate can tell whether the build EARNED its green or gamed the TDD signal — test/contract tampering is caught MECHANICALLY (an md5 tripwire on the red suite), the judgment cheats (src overfit to fixtures · vacuous asserts · stubbed-away logic) by an INDEPENDENT adversarial refute-read, and a confirmed cheat self-heals for up to 3 honest re-build attempts before it HARD-STOPs to the human; a gamed green is never auto-passed.
rationale: new-major — a new pillar of the method's TRUST core (the whole method rests on "trust evidence, not inspection"; today nothing stops a build from gaming the evidence). No active milestone's goal covers verify-phase anti-cheat. Risk: HIGH / method-defining — introduces the method's FIRST mechanically-enforced HARD-STOP (every prior gate is guidance + never-red measures); the engine pin bumps. Human-confirmed at intake: severity = HARD-STOP (like security); detection = engine tripwire + semantic rubric; loop = ≤3 self-heal attempts then escalate to the human.
stage: mvp · status: active · created: 2026-06-11

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:
- **Mechanical tamper tripwire** — `add.py` snapshots the md5 of the test files + the §3 contract at the `tests→build` advance; at the verify gate it re-checks, and ANY edit to a test or the frozen contract since the red run is a mechanical cheat signal. Tool-agnostic: it HASHES files, never runs tests or measures coverage. (→ `tamper-tripwire`)
- **The earned-green rubric (judgment cheats)** — `6-verify.md` + the `## 6 · VERIFY` TASK.md template gain a named **build-integrity / earned-green** rubric for the cheats the engine can't see: **src overfit to the test fixtures** (special-cased to the literal inputs) · **vacuous / tautological asserts** (green-trivial even at §4) · **real logic stubbed away** (returns a constant). Scored by an **independent adversarial refute-read** — a reviewer (or subagent under `autonomy: auto`) prompted to argue "the green was NOT earned", separate from the build context. The guide RECOMMENDS a subagent; the engine never spawns one (tool-agnostic). (→ `earned-green-rubric`)
- **Bounded self-heal → escalate** — a confirmed cheat (mechanical tripwire OR semantic finding) returns to build for an HONEST redo; the engine tracks attempts and, after **3**, forces a `HARD-STOP` that escalates to the human for a decision/suggestion. Never auto-passes a cheat; never loops unbounded. (→ `heal-then-escalate`)
- Synced across the ×3 skill/template trees + the ×4 book/glossary where the rubric / loop is described.

Out (deferred — the anti-scope-creep list):
- **Running the suite or measuring coverage inside the engine** — NO; tool-agnostic stays. The tripwire hashes files, never executes; coverage-drop stays the existing manual checkbox.
- **Mutation testing** (re-run the suite against stubbed src to prove asserts bite) — powerful but tool-specific + expensive; the adversarial refute-read covers it by JUDGMENT for now.
- **The engine auto-FIXING a cheat** — no; the engine flags + counts + escalates, the AGENT does the honest re-build.
- **A general retry-budget for ALL verify failures** — the ≤3 loop is scoped to CHEAT findings (the build↔verify honesty loop), not every gate failure.
- **Touching the security HARD-STOP or the autonomy model** beyond adding the cheat-HARD-STOP + the bounded loop. Security stays its own line.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **earned green / build integrity** — the green is EARNED when the implementation makes the UNCHANGED red suite pass by GENERAL behavior, not by editing tests, overfitting to fixtures, vacuous asserts, or stubbing logic. (new GLOSSARY term)
- **tamper tripwire** — the md5 snapshot of test+contract files at `tests→build`, re-checked at verify; an edit since the red run is a mechanical cheat signal. A measure with TEETH (feeds the HARD-STOP), unlike the existing never-red WARNs.
- **adversarial refute-read** — the judgment half is scored by an INDEPENDENT read prompted to refute "the green was earned"; a recommendation (a subagent under `auto`), engine never spawns it (tool-agnostic). Extends the ground-context subagent pattern.
- **bounded self-heal** — a cheat finding loops back to build for an honest redo, capped at 3 attempts, then HARD-STOPs to the human. Never auto-passes a cheat; never loops unbounded.
- **a confirmed cheat is a HARD-STOP** — like security: never auto-passed, never RISK-ACCEPTED-waived.

## Shared / risky contracts (freeze these first)
- **Tamper-snapshot shape + storage + timing** — WHAT is hashed (the §4 `Tests live in:` paths + the §3 contract block), WHERE the snapshot is stored (state.json vs TASK.md §6), WHEN taken (`tests→build` advance) and checked (verify gate). The riskiest contract (new engine state + the first mechanical HARD-STOP path). → owning task `tamper-tripwire`; `heal-then-escalate` consumes its signal. Freeze first.
- **Attempt-counter shape + cap (3) + escalation record** — where the counter lives, how a reset/increment is triggered, and the exact escalation outcome. → owning task `heal-then-escalate`.

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] tamper-tripwire     depends-on: none             — engine: snapshot md5(test paths + §3 contract) at `tests→build`; re-check at the verify gate; any edit since the red run → a mechanical cheat flag feeding the HARD-STOP path. Tool-agnostic (hashes, never runs tests). Engine pin bumps. The mechanical floor + the riskiest contract.
- [x] earned-green-rubric depends-on: none             — prose: `6-verify.md` + `## 6 · VERIFY` template gain the earned-green rubric (overfit · vacuous · stub) scored by an independent adversarial refute-read (subagent recommended; engine never spawns). ×3/×4 synced; a guard test pins it. Pin holds (no engine change).
- [x] heal-then-escalate  depends-on: tamper-tripwire   — engine + guide: a confirmed cheat (tripwire OR rubric finding) → return-to-build honest-redo loop; the engine counts attempts, caps at 3, then forces a HARD-STOP that escalates to the human for a decision. Engine pin bumps.

## Exit criteria (observable; map each to the task that delivers it)
- [x] At verify, editing a test file or the §3 contract after the red run is MECHANICALLY detected and blocks an auto-PASS  (verify: `add.py` snapshots at `tests→build` + re-checks at the gate; a guard test proves a post-red edit raises the tamper flag)  (← tamper-tripwire)
- [x] `6-verify.md` + the `## 6 · VERIFY` template carry the earned-green rubric (overfit · vacuous · stub) scored by an independent adversarial refute-read, byte-synced ×3/×4  (verify: a guard test asserts the guide+template name the 3 judgment cheats + the refute-read; ×3/×4 parity)  (← earned-green-rubric)
- [x] A confirmed cheat drives ≤3 honest re-build attempts then a HARD-STOP that escalates to the human — never an auto-PASS, never an unbounded loop  (verify: the engine records attempts, caps at 3, forces the escalation; a guard test proves the 4th attempt HARD-STOPs)  (← heal-then-escalate)
