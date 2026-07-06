# The dynamic run — executing a locked scope

Once a task's CONTRACT is frozen (phase 3), the scope is *locked* — ADD's autonomy decision point:
below it code is disposable; above it nothing breaks. This rubric covers the **build->verify half,
executed as a dynamic, self-improving run**. The human-led **specification bundle** (Specify ·
Scenarios · Contract) still owns *direction*. The engine stays judgment-free: this is a rubric, not `add.py`.

## The specification bundle (v7)

v7 compresses the old three-approval flow to **one**: the AI drafts Spec · Scenarios ·
Contract · failing Tests in one pass; the human gives **one approval, at the frozen
contract** — the decision point stays human (the AI never freezes its own shape; a
rejected part goes back to draft, backward-correction not failure). The freeze
presentation — the bundle led **lowest-confidence first** by its ⚠ flag, the
freeze review checklist (seven lines, ⚠-first) — lives in `phases/3-contract.md`,
its one home; this rubric owns what happens AFTER the freeze.

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
- **The recorded refute-read (under `auto`).** The earned-green refute-read (`6-verify.md`) is not just run — its **verdict is recorded** in §6 (`EARNED | NOT-EARNED`); `add.py audit` surfaces an unrecorded one as `refute_unrecorded` — one of three shape lints it lists (with `shallow_deep_check` + `risk_unset`) — and a human spot-audit is the backstop. NOT-EARNED routes to `add.py heal`, never an auto-PASS.
- **The recorded Advisor 3-lens verdict (under `auto`).** The Advisor 3-lens sweep (security → concurrency → architecture, `6-verify.md`) is recorded in §6 `### Advisor 3-lens verdict`; `add.py audit` surfaces an unfilled block as `advisor_verdict_unrecorded` — a shape lint alongside `refute_unrecorded`.
- **The rendered gate report (§3/§6).** Report-template.md's ceremony is recorded, not just performed — a `Reported: yes` line in §3/§6; `add.py audit` surfaces an unrecorded one as `contract_report_unrecorded`/`verify_report_unrecorded`; a human spot-audit is the backstop.
- **The `advisor-gate-relax` pathway.** A `risk: high` + `sensitivity: mechanical` task whose §6 Advisor 3-lens verdict records Verdict `PASS` and Residue `none` may auto-complete via `add.py gate PASS` **without** a lowered autonomy level. Security and every non-mechanical sensitivity class are never relaxed by this pathway — the high-risk guard still applies.
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
  Security still always escalates — but only a finding the AI *surfaces*: a security issue the
  reviewer misses is **invisible** to the engine, so under `auto` a human **spot-audit** is the
  only backstop for a missed finding.
- **conservative** — the deliberate *lowering*: the run converges but STOPS at the verify gate.
- **manual** — the strict floor: the human owns the verify gate; the engine never auto-resolves.

> **v7 reversal (recorded).** Earlier the default was `conservative`; v7 flips it to `auto` as
> the default. The level is still **per-scope** and is lowered wherever risk demands.

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
`add.py check` raises `goal_not_auto_ready` while criteria are uncited; `status` prints a
`goal-ready:` line. It **measures, never blocks** — the lint cannot prove the citation honest
(`(verify: it works)` passes); that judgment stays the human's.
</constraints>
