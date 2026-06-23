# The dynamic run — executing a locked scope

Once a task's CONTRACT is frozen (phase 3), the scope is *locked*. That lock is ADD's autonomy
decision point — below it code is disposable; above it nothing breaks. This rubric covers the
**build->verify half, executed as a dynamic, self-improving run**. The human-led **specification
bundle** (Specify · Scenarios · Contract) still owns *direction*, but v7 compresses it to a
**single human approval at the decision point** — the AI drafts the whole bundle, a human approves
it once. The engine stays judgment-free: this is a rubric, not `add.py`.

## The specification bundle (v7)

v7 compresses the old three-approval flow to **one**. The AI **drafts the whole specification
bundle in one pass** — Spec, Scenarios, Contract, and failing Tests — and presents it together.
The human gives **one approval, at the frozen contract** (the decision point).

Why one and not zero: the decision point **stays human**. The AI *drafts* the contract but never
*freezes its own* — a person approves the frozen shape before any auto-run touches code. What the
human approves: that the Spec captures real intent, the Scenarios cover the cases that matter, and
the Contract shape is the one to freeze. Reject any part and the bundle goes back to draft —
backward-correction (principle 4), not failure. The decision-point guide (`phases/3-contract.md`) carries the **freeze review checklist** —
seven lines that walk the human through exactly this, ⚠-first.

**The lowest-confidence flag.** The AI presents the bundle **lowest-confidence first**: the
**1–2 points most likely to be wrong**, tagged by part
(`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). The `because` names the §1
assumption that makes it uncertain; the `if wrong` names what it costs if that assumption is off.
If nothing is materially uncertain, the AI still names the single biggest risk — never a blank "none".
Raising this flag is honor-system: the lint cannot force the AI to engage with it — closing that
gap is a CI checker's job, not prose.

## When the run begins — the scope-lock trigger

The trigger is the **frozen contract**, nothing else. A run may start only when §3 CONTRACT is
marked `FROZEN @ vN` AND §4 TESTS exist and are RED for the right reason.

No frozen contract -> no run: starting early is the forward-skip the flow forbids.

## The change scope — what the run may and may not touch

<constraints>
A locked run has a hard boundary. It MAY:

- write and rewrite **code** (`src/`) — code is disposable below the decision point;
- drive the **tests** to green WITHOUT weakening them;
- gather **evidence** for the verify gate (test output, non-functional review).

It MUST NOT:

- change the **frozen contract** or the **locked scope** — a discovered gap is backward-correction:
  the run STOPS and hands back to a human to reopen Specify (principle 4).
- weaken, delete, or skip a **test** to make the build pass.
- touch the **specification-bundle artifacts** (§1–§3) except to halt and escalate.
</constraints>

## The dynamic run — fan-out and in-run convergence

The run **fans out** independent work and **converges** with three loops:

- **loop-until-dry** — keep hunting failures until N consecutive passes find nothing new.
- **adversarial verify** — an independent skeptic tries to REFUTE every "done" claim.
- **completeness-critic** — a final pass asking "what did we NOT cover?" Whatever it finds re-enters.

The run ends only when the loops go dry AND the auto-gate's evidence is satisfied.

## The automated quality gate

<constraints>
The verify gate may be resolved by **evidence** rather than by a person (principle 7: an automated,
recorded pass is an explicit pass, not a skip).

- **Auto-PASS requires ALL of:** every test green; coverage not decreased; no test weakened and no
  contract edited; loops dry; completeness-critic clean; and the deep check below.
- **The deep check (every gate, do not skim).** If the task produced code, record that every new symbol is referenced (wiring) and that no new dead/unused code was introduced. If it produced prose or non-code, record a semantic read. An unfilled deep check is a **shallow verify**, not an auto-PASS.
- **Always escalates to a human (never auto-passed):** any **security** finding (HARD-STOP, always);
  a **concurrency**/timing risk the tests cannot exercise; an **architecture**/layering violation;
  any failing test.
- **Records exactly one outcome** (no silent skip): `PASS` · `RISK-ACCEPTED` · `HARD-STOP`. The
  record states it was auto-resolved, names the run, and lists the residue checks performed.

The auto-gate NEVER writes a human signature it did not get.
</constraints>

## The bounded self-heal loop

Evidence can be **gamed** — test or contract edited after the red run, src overfit to fixtures,
vacuous asserts, or real logic stubbed away. That is a **confirmed cheat**: HARD-STOP-class, never
auto-passed, never RISK-ACCEPTED-waived.

A first cheat enters a **bounded self-heal loop**: the engine returns the task to **build** for an
honest redo, counts the attempt, and caps it. After **3 honest** re-build attempts a fourth confirmed
cheat forces a **HARD-STOP** that escalates to the human. The counter is **monotonic** — only an
honest build escapes.

Two findings enter the loop:
- **mechanical** (enforced) — the tamper tripwire: at the gate the engine re-hashes the red test
  files + frozen §3 against the `tests→build` snapshot; any divergence routes to the loop.
- **semantic** (honor-system) — the **adversarial refute-read** (`6-verify.md`): on a confirmed
  overfit/vacuous/stub the agent reports it with `add.py heal <slug> --reason "<finding>"`.
  The engine cannot see a judgment cheat, so this entry is the agent's honest report — the human
  verify gate stays the real backstop.

Either way: ≤3 honest redos, then escalate. A gamed green never ships.

## Emitting deltas — feeding the foundation back

Every gap the completeness-critic finds becomes an **`open` lesson learned** in the task's OBSERVE
block (`deltas.md` grammar). These `open` deltas feed v5's human-gated consolidation (`fold.md`)
at milestone close — the loop closing: **v6 run -> v5 foundation**.

## The autonomy level

<constraints>
How much a run may auto-gate is a **per-scope setting** (principle 5). A task declares it in its
`TASK.md` header — this is not an add.py flag; it is a rubric convention:

```
autonomy: manual | conservative | auto
```

- **auto (the default)** — the run may auto-PASS when evidence + residue checks are satisfied.
  Security still always escalates.
- **conservative** — the deliberate *lowering*: the run converges but STOPS at the verify gate.
- **manual** — the strict floor: the human owns the verify gate; the engine never auto-resolves.

> **v7 reversal (recorded).** Earlier the default was `conservative`; v7 flips it — `auto` is the
> default, `conservative` is the deliberate lowering. The level is still **per-scope** and is
> lowered wherever risk demands.

**The high-risk guard.** On a **high-risk or method-defining scope** `auto` must be lowered to
`conservative` or `manual`; leaving it at `auto` is the reject code **`unguarded_high_risk_auto`**.
The scope declares **`risk: high`** in the `TASK.md` header (the engine never classifies scope).
Since v14 the guard is mechanical for the declared case:
the engine refuses the declared combination — `add.py gate` will not complete (`PASS`/`RISK-ACCEPTED`)
a task whose header carries `risk: high` without a lowered level (`HARD-STOP` always records);
`add.py audit` flags finished records whose header was tampered or whose GATE RECORD reviewer is
the auto-gate (CI enforces). An undeclared high-risk scope passes — a scope without `risk: high`
in its header is not blocked by the v14 mechanical guard.

**Autonomy is earned by goal-clarity — the auto-ready goal.** A milestone goal is auto-ready
when **every exit criterion cites a verifier** — `(verify: <test | command | metric>)`.
`add.py check` raises a `goal_not_auto_ready` WARN while criteria are uncited, and `status`
prints a `goal-ready:` line every session. It **measures, never blocks**. The lint cannot prove
the citation is honest — `(verify: it works)` passes the check — that judgment stays the human's.
</constraints>
