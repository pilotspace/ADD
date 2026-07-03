# 08 · Step 6 — Verify

[← 07 Step 5 Build](./07-step-5-build.md) · [Contents](./README.md) · Next: [09 The loop →](./09-the-loop.md)

> **Purpose:** confirm the result is correct and safe to release.
> **Produces:** a reviewed change with a recorded outcome, ready to release.
> **Who resolves it:** set per task by the `autonomy:` header. Under `autonomy: auto` (the default) the run resolves the gate on evidence; under `conservative`, or for any residue, it is the human's check. **Security always escalates to a human.**

---

## Where trust is actually established

The build produced passing tests. That is necessary but not sufficient. Verification is where a person establishes trust — and the principle governing it is *trust through evidence, not inspection.*

This needs care, because it is easy to misread. "Not by inspection" does not mean "do not look at the code." It means the *basis* of trust is the passing evidence plus a deliberate check of the specific things tests cannot easily catch — not a general impression that the code reads plausibly. Plausibility is exactly the trap: AI code is frequently plausible and wrong. So verification has two parts: confirm the evidence, then check the known non-functional risks.

## Who resolves Verify — the automated quality gate

Verify can be resolved two ways, set per task by the `autonomy:` header (see [governance](./11-governance.md) and the autonomy level):

- **Auto (the default).** When `autonomy: auto`, the run resolves the gate on **evidence** rather than waiting for a person — but only when *all* of these hold — the **same canonical list run.md owns**: every test green, coverage not decreased, no test weakened and no contract edited, the convergence loops dry, the completeness-critic clean, the deep check filled, the earned-green refute-read verdict recorded (the §6 `### Refute-read verdict` field, under auto), and **no residue** (security, concurrency, or architecture). It records `PASS` as *auto-resolved*, naming the run as the accountable owner — an explicit pass, not a skip. This is principle 7: a gate may be resolved by evidence when that evidence is sufficient and the result is logged.
- **Human.** When `autonomy: conservative`, or whenever the run finds residue it cannot judge, the gate stops for a person; the two parts below are theirs.

**Security is always a `HARD-STOP` and is never auto-passed, at any autonomy level.** The two parts that follow — confirm the evidence, then check the non-functional risks — are what *either* resolver works through; the only question is whether a person or the recorded run signs the outcome.

## Part one — confirm the evidence

Before the build, the task pre-declares its **build expectations** — the observable outcomes a correct build must produce, read off §2's scenarios and §3's contract. Confirm each one here against evidence you can see, not a restated test name: this is what makes the gate check the build is *right*, not merely that the suite is green.

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test or contract was altered during the build.
- [ ] Every pre-declared build expectation is confirmed by real evidence (not merely a green test).
- [ ] Every §1 Must/Reject rule still traces to a §2 scenario tag or a §4 `covers:` line.
- [ ] Every symbol §3's contract cites still resolves in the *current* tree, not just at Ground SHA.

If any of these is false, stop here and return to the build; there is nothing to verify yet.

A green suite proves the tests you wrote pass — it says nothing about a rule you never wired a scenario or test to at all. That is a different failure than the ones Part four covers: not a cheated pass, but a rule with no trace of ever being checked. `add.py check` scans every task project-wide for exactly this — a §1 Must or Reject with no §2 scenario tag and no §4 `covers:` line — but that sweep is easy to forget to run. `add.py audit`'s `rule_coverage_gap` notice surfaces the SAME check for the task actually at this gate, the moment it reaches Verify (a task that never adopted the tag convention at all is silently grandfathered, never retro-flagged). Neither blocks the gate; both make an already-real gap impossible to miss.

The second check guards against a quieter kind of drift. §0's Ground SHA anchors the symbols §3's contract cites to the commit they were read at — but code moves *during* the build that follows. Before this gate, re-resolve every one of those symbols against the tree as it stands now, not the Ground SHA snapshot, and record it in §6's **Live-verify evidence** block. A moved or renamed anchor caught here is a one-line note; the same drift left silent is a future reader chasing a line number that no longer means what it did at Ground.

## Part two — check what tests miss

Automated tests are excellent at behavior on defined inputs and poor at a few specific things. Check those by hand, every time:

- **Concurrency and timing.** Is the operation correct when two of them happen at once? Tests usually run serially and miss races.
  - ▶ *Example: the balance update must be one atomic transaction. Confirm that two simultaneous transfers from the same account cannot both pass the balance check and overdraw it.* This is the single most important check for this feature, and it is the reason the build prompt named atomicity explicitly.
- **Security.** Are there exposed secrets, injection openings, or unexpected dependencies? AI-generated code is known to hardcode secrets and to pull in packages by plausible-but-wrong names. A security finding is always a `HARD-STOP`, never a waiver — and it escalates only if it is *written down*: `add.py audit`'s `unescalated_security_note` check fires on a **marked** note that slipped through as an auto-gate PASS, but a finding you **never marked** is invisible to the engine, escalated to no one. That is the honest limit of the auto-gate: under `auto`, a human **spot-audit** (reading the diff) is the only backstop for a *missed* security finding — the same backstop named for an unrecorded earned-green refute-read.
- **Architecture conformance.** Does the change respect the layering and dependency rules in `CONVENTIONS.md`? Speed with no architectural check produces a fast-growing tangle that becomes unmaintainable within months.

## Part three — the deep check (do not skim)

Two failures slip straight past green tests. The first is code that is never *wired in* — a new function that nothing calls, an endpoint no route reaches: the tests for it pass in isolation while the feature is, in practice, absent. The second is the opposite — code left *dead* behind a path nothing exercises, quietly rotting. And for a change that produced prose rather than code, the equivalent failure is signing off on a claim you never actually read in full. Plausibility hides all three. So verification carries one explicit requirement beyond the non-functional review:

> Deep check — do not skim. If the task produced code, record that every new symbol is referenced (wiring) and that no new dead/unused code was introduced. If it produced prose or non-code, record a semantic read — what you read in full and what it confirmed. Which path applies is the resolver's judgement; the engine never classifies.

This is *evidence*, not impression: a reference search showing where each new symbol is called, a scan confirming nothing new is orphaned, or — for prose — a note of exactly what was read and what it confirmed. An unfilled deep check is a **shallow verify**, not a pass. The engine cannot judge wiring, dead code, or whether prose was truly read; the resolver records the evidence, and a person (under `conservative`) or the recorded run (under `auto`) signs it.

**The wiring trace is a named step, not a free-form note.** For every new hook, closure, or middleware registered in this task: trace from the process entry point to the call site and record it explicitly — symbol, file, line. A symbol that is only reachable via a test helper or `make_config` but not via the production entry point (e.g. `build_harness_with_dispatcher`, `interactive_mode`) is not wired. This is the third repeated class in production: "runtime-activation-order/silent-noop" — the code exists and the unit tests pass, but the feature is absent in the running program. The wiring trace is how you catch it before a user does.

## Part four — was the green earned?

Passing tests say the code satisfies the cases you wrote down. They do not say it earned that pass honestly — and the mechanical tamper tripwire (Step 6's floor) only catches an *edited* test or contract, not a build that gamed the *unchanged* suite. The same rubric the phase guide carries names what the tripwire cannot see:

A green suite proves the tests pass — not that the build EARNED them. Three judgment cheats pass the unchanged suite without earning it: src overfit to the test fixtures (special-cased to the literal inputs, not the general behavior §1 asked for), vacuous asserts (tautological — green even against an empty implementation), and real logic stubbed away (the function returns a constant the tests happen to accept). These cheats are invisible to the mechanical tamper tripwire, which only sees edited files. Score them with an adversarial refute-read: an independent reviewer — a subagent under `autonomy: auto` is recommended, the engine never spawns one — prompted to argue the green was NOT earned from outside the build context. This is the verify-gate, whole-suite specialization of run.md's adversarial verify (see run.md), not a new discipline. A confirmed earned-green failure is HARD-STOP-class: never auto-passed, never RISK-ACCEPTED — but a first cheat is a chance to redo: a confirmed cheat (mechanical tamper or a reported earned-green failure) enters the bounded self-heal loop — it returns to build for an honest redo, and only after the loop's cap does it HARD-STOP to the human (the loop lives in run.md).

Under `autonomy: auto` there is no human at the gate to confirm the refute-read happened, so the verdict is **recorded** — a `### Refute-read verdict` field in §6 (`Verdict: EARNED | NOT-EARNED`, plus who read it and what they adversarially probed). This closes an honesty gap the auto-gate would otherwise leave open: the method *says* an auto-PASS rests on an earned-green check, but nothing made that check visible. Now `add.py audit` surfaces a verify-or-later task whose verdict block is still a placeholder as `refute_unrecorded` — a **measure, not a gate**: it never blocks the run (a hard gate on this universal completion path would break far too much to justify it, and the engine cannot read whether a self-graded `EARNED` is *true* anyway — only whether it was written). The honest backstop is the same one named for a missed security finding: a human **spot-audit** reading the diff. A `NOT-EARNED` verdict is not a dead end — it routes through `add.py heal` for an honest redo, never an auto-PASS. The discipline this records is simple: under auto, you are the accountable owner of the gate, so you leave the trace of the check you owe.

## Recording the outcome

Every verification ends with exactly one recorded outcome, with an accountable owner — never a silent pass:

| Outcome | Meaning | Allowed when |
|---------|---------|--------------|
| `PASS` | all checks met | the normal path |
| `RISK-ACCEPTED` | proceed with a signed waiver: named owner, linked ticket, expiry date | a non-security gap only |
| `HARD-STOP` | cannot proceed | any failing test or any security finding |

A security finding is always a `HARD-STOP`; it is never waved through with a waiver. A `RISK-ACCEPTED` outcome is a deliberate, documented decision to ship a known, non-security limitation — not a way to skip the check.

## The verification checklist

- [ ] All tests pass (the evidence).
- [ ] Every pre-declared build expectation is confirmed by observable evidence.
- [ ] Every §1 rule traces to §2/§4; every §3-cited symbol still resolves in the current tree.
- [ ] Concurrency/timing of the risky operation is safe.
- [ ] No exposed secrets, injection openings, or unexpected dependencies.
- [ ] Layering and dependencies follow `CONVENTIONS.md`.
- [ ] Deep check (do not skim): for code, every new symbol is referenced (wiring) and no new dead/unused code was introduced; for prose/non-code, a semantic read is recorded.
- [ ] The change is approved — by a person, **or** (under `autonomy: auto`, no residue) auto-resolved by the run as the recorded accountable owner.
- [ ] An outcome is recorded (`PASS` / `RISK-ACCEPTED` / `HARD-STOP`).

## Common mistakes

- **Shipping on plausibility.** Reading the diff, finding it reasonable, and approving — without the evidence and the non-functional review — is the precise failure the method exists to prevent.
- **Treating a security gap as acceptable risk.** It is a `HARD-STOP`, not a waiver.
- **Skipping the concurrency check** because the tests are green. Tests rarely exercise simultaneity; this is a manual check by design.
- **Trusting the green agent's self-reported test count.** A build agent running a filtered suite (e.g. `-E 'test(theme)'`) only sees tests inside the filter. Collateral failures outside the filter — a stale count in `all_commands_in_registry`, an e2e snapshot the agent did not touch — are invisible. The orchestrator's **full-suite rerun is load-bearing**; never skip it on the grounds that the scoped run was green.
- **User-observable-only failures escalate to the human before exhausting discriminating probes.** When a symptom is only observable by a person (a TCC dialog, a visual flicker, an OS-level prompt), do not respond by running the suite again. Instead, design two or three targeted probes that let the user distinguish cause A from cause B in one interaction each. Three AskUser probes resolve what three blind reruns cannot.
- **Background-process hangs misdiagnosed as test failures.** A test that never exits is not a failure in the test logic — it is a hang. The diagnosis recipe: background the test process, run `pgrep` to find it, use the platform profiler (`sample <pid>` on macOS, `perf` on Linux) to sample the stack, then `lsof -p <pid>` to see open files. Run an isolation experiment (suspect line on/off, 3×3) before reading any code. Entry-count caps do not bound wall time — a single huge directory or a blocking syscall inside a `spawn_blocking` call can hang indefinitely even when the entry cap is satisfied.

## If the check fails

A failing test or a security finding returns the change to the build step ([Step 5](./07-step-5-build.md)). A non-security limitation may proceed only with a signed `RISK-ACCEPTED` record carrying an owner and an expiry — so the team can find and close it later. Nothing proceeds on an unrecorded decision.
