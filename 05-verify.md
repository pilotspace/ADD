# 05 · Verify — evidence, residue lenses, the gate

[← 04 Build — red to green, inside scope](./04-build.md) · [Contents](./README.md) · Next: [06 The loop — observe, learn, close →](./06-the-loop.md)

---

## Where trust is actually established

The build produced passing checks. That is necessary but not sufficient. Verification is where trust is established — and the principle governing it is *trust through evidence, not inspection.*

This needs care, because it is easy to misread. "Not by inspection" does not mean "do not look at the code." It means the *basis* of trust is the passing evidence plus a deliberate check of the specific things checks cannot easily catch — not a general impression that the code reads plausibly. Plausibility is exactly the trap: AI code is frequently plausible and wrong. So verification has two parts: confirm the evidence, then examine the residue automation cannot cover.

## Part one — gather the evidence: a fresh, bound receipt

Trust rests on a run you can point to, not a claim. Execute the task's checks and record the result as a receipt:

```
add run <slug> --junitxml r.xml -- <the test command>
```

`add run` executes your command, parses the JUnit report, and writes a **Run receipt** into the task's bundle. Two properties the gate will demand of it:

- **fresh** — the receipt records the git blob hash of every in-`scope:` file at the moment it ran; the gate recomputes those hashes and refuses on any difference. This kills the stale-green failure — a suite that passed *before* the last edit is not evidence for the code as it stands now.
- **bound** — this is **covers-binding**. Every check in the node's `## CHECKS` cites the Must, Reject, or Edge it proves, via its `covers:` line. The gate refuses a PASS unless each of those checks appears in the receipt with a passing outcome. A rule with no passing check behind it cannot be waved green. An assumption marked `· probe:` in `## ASSUMPTIONS` binds the same way — its `A<n>` id must be cited by a passing check, or the gate holds the PASS.
- **build-entered** — the receipt must postdate a recorded brief: an `act: brief` stamp between the latest (re)freeze and the receipt's run stamp. A `PASS` with no such entry is refused (`R:UNBRIEFED`) — the sealed direction was never compiled into the working prompt, so whatever the suite proves, it does not prove the build followed the direction. (`depth: quick` is exempt.)

A stale, unbound, or unbriefed receipt is refused at the gate — so confirm the evidence is real before reading further: every check green, no check or frozen contract altered during the build, and every rule in `## RULES` traced to a passing check by its `covers:` line. If any of that is false, stop here and return to the build; there is nothing to verify yet.

## Part two — the residue: three lenses tests cannot cover

Automated checks are excellent at behavior on defined inputs and poor at a few specific things. Examine, by hand, the narrow set they miss — every time:

- **Security.** Are there exposed secrets, injection openings, or unexpected dependencies? AI-generated code is known to hardcode secrets and to pull in packages by plausible-but-wrong names. **A security finding is always a `HARD-STOP`** — it escalates to a human and is never waved through, whatever the evidence says.
- **Concurrency and timing.** Is the operation correct when two of them happen at once? Checks usually run serially and miss races.
  - ▶ *Example: the balance update must be one atomic transaction. Confirm that two simultaneous transfers from the same account cannot both pass the balance check and overdraw it.* This is the single most important check for this feature, and it is why the build prompt named atomicity explicitly.
- **Architecture conformance.** Does the change respect the layering and dependency boundaries the project already committed to? Speed with no architectural check produces a fast-growing tangle that becomes unmaintainable within months.

This residue stays at human speed. You may move as fast as your *automated* verification carries you, and no faster on the part only a human can check.

## The deep check — reviewer discipline, not an engine gate

Two failures slip straight past green checks, and no engine can see them for you — this is diligence the reviewer owes, not a box the tool fills:

- **Wiring.** New code that is never *wired in* — a function nothing calls, an endpoint no route reaches. Its checks pass in isolation while the feature is, in practice, absent. For every new hook, closure, or middleware, trace from the process entry point to the call site: symbol, file, line. A symbol reachable only through a test helper but not through the production entry point is not wired.
- **Dead code.** The opposite — code left behind a path nothing exercises, quietly rotting. Scan that nothing new is orphaned.
- **Semantic read.** For a change that produced prose rather than code, the equivalent failure is signing off on a claim you never actually read in full. Note what you read and what it confirmed.

Plausibility hides all three, which is why this is *evidence*, not impression: a reference search showing where each new symbol is called, a scan confirming nothing new is orphaned, or — for prose — a note of exactly what was read. Skimming here is a shallow verify, not a pass.

## The gate — one recorded outcome

Every verification ends with exactly one recorded outcome, carrying an accountable owner — never a silent pass:

```
add gate <slug> PASS --by "<name>"
```

| Outcome | Meaning | Allowed when |
|---------|---------|--------------|
| `PASS` | complete, fresh, bound evidence and clean residue | the normal path |
| `RISK-ACCEPTED` | proceed on a signed waiver: named owner, linked ticket, expiry | a **non-security** gap only |
| `HARD-STOP` | cannot proceed | any failing check, or any security finding |

A **`gate PASS` auto-closes** the task — there is no separate close step on the normal path. A `RISK-ACCEPTED` is a deliberate, documented decision to ship a known, non-security limitation; sign it with the reason the engine requires — owner, ticket, expiry — so the team can find and close it later:

```
add gate <slug> RISK-ACCEPTED --by "<name>" --reason "<owner · ticket · expiry>"
```

A `HARD-STOP` does not close the task: it stays open, and the finding goes back to Direction as a change request — fix the build, or add the Must the gate exposed — then you re-verify. A **security** `HARD-STOP` always escalates to a human and is never folded into a `RISK-ACCEPTED`; this one is engine-enforced — the gate refuses a `RISK-ACCEPTED` on a security-sensitive node. Resolve it to `PASS`, or `HARD-STOP`.

## The verification checklist

- [ ] The receipt is **fresh** (every in-`scope:` file unchanged since the run) and **bound** (every check the rules `covers:` passed).
- [ ] No check or frozen contract was altered during the build.
- [ ] Concurrency/timing of the risky operation is safe.
- [ ] No exposed secrets, injection openings, or unexpected dependencies.
- [ ] Layering and dependency boundaries are respected.
- [ ] Deep check: for code, every new symbol is referenced (wiring) and no new dead code was introduced; for prose, a semantic read is recorded.
- [ ] Exactly one outcome is recorded — `PASS` / `RISK-ACCEPTED` / `HARD-STOP` — with an accountable owner.

## Common mistakes

- **Shipping on plausibility.** Reading the diff, finding it reasonable, and approving — without the receipt and the residue review — is the precise failure the method exists to prevent.
- **Treating a security gap as acceptable risk.** It is a `HARD-STOP`, not a waiver.
- **Skipping the concurrency check** because the checks are green. Checks rarely exercise simultaneity; this is a manual review by design.
- **Trusting a self-reported test count.** A build agent running a filtered suite (e.g. `-E 'test(theme)'`) only sees checks inside the filter. Collateral failures outside it are invisible; a full-suite run is load-bearing, never to be skipped on the grounds that a scoped run was green.
- **User-observable-only failures escalated before probing.** When a symptom is only observable by a person (a permission dialog, a visual flicker), do not respond by running the suite again. Design two or three targeted probes that distinguish cause A from cause B in one interaction each.
- **A hang misdiagnosed as a test failure.** A check that never exits is not a logic failure — it is a hang. Background the process, find it with `pgrep`, sample the stack with the platform profiler (`sample <pid>` on macOS, `perf` on Linux), then `lsof -p <pid>` to see open files.

## If the check fails

A failing check or a security finding returns the change to the [build](./04-build.md) beat. A non-security limitation may proceed only with a signed `RISK-ACCEPTED` record carrying an owner and an expiry — so the team can find and close it later. Nothing proceeds on an unrecorded decision.
