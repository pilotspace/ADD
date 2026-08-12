# Beat 3 · Verify — trust on evidence, then the gate

A change is trusted because its checks pass **and** the residue tests can't catch was examined — not
because the diff reads plausible. Verify is where that trust is recorded, once.

## 1 · Gather the evidence — a fresh, bound receipt

```bash
add run <slug> --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- <the test command>
```

`run` executes your command, parses the JUnit report, and writes a **Run receipt** under
`.add/tasks/<slug>.d/runs/`. Two properties the gate will demand:
- **fresh** — the receipt records the git blob hash of every in-`scope:` file at run time; a gate
  recomputes it and refuses on any difference. This kills the stale-green failure (tests that passed
  before the last edit). A directory scope enumerates through git, so **gitignored files (build
  output, dependencies) never enter the digest** — a rebuild cannot stale a receipt no source edit
  touched. Outside git it falls back to mtime and says so.
- **bound** — every check ID in `## CHECKS` must appear in the receipt with `outcome: pass`; a
  `covers:` naming a check that did not demonstrably pass fails the gate. Probed assumptions
  (`· probe:` lines) bind the same way — a declared-checkable reading with no passing check
  holds the PASS.

The gate also demands the build was **entered**: an `act: brief` stamp between the freeze and
this receipt's run (see `phases/build.md`). Briefing after the fact buys nothing — the fix the
refusal names is a re-run under the brief.

**Keep the receipt command narrow.** The gate demands exactly the checks `## CHECKS` binds —
nothing rewards wrapping more. Wrap the **narrowest command that reports every bound check**
(one test file, one marker, one target); the full suite rides CI or a backgrounded run, and a
slow check that no `covers:` names (a whole production build, cost-tuned hashing) stays out of
the receipt loop unless a frozen check demands it. A receipt run costs minutes only when the
wrapped command does — the notary itself is milliseconds. The wrapped command's ceiling is
**900 s by default**; a legitimately slow receipt (a bound build check) raises it explicitly
with `--timeout <s>` — a timeout is *recorded* as exit 124, and the gate will refuse the PASS.

Evidence kinds the engine can actually stamp, strongest first: `test-ids` (a runner reported the
IDs your `covers:` names) > `command-exit` (the command exited 0, and nothing is bound to a named
check). A findings-only explore gates on `sources` instead — cited questions closed, no run
receipt. A weaker kind is a *visible* weakening (the receipt records which it earned), never a
silent one — and a kind nothing can stamp is not a weak rung, it is a false one.

## 2 · Check the residue — three lenses

Automation covers the checks; it does not cover everything. Examine, by hand, the narrow set tests miss:
- **security** — always escalates to a human; a finding is a **HARD-STOP**, whatever the evidence says.
- **concurrency** — races, ordering, atomicity under load.
- **architecture** — boundary and dependency violations a passing test won't reveal.

This residue stays at human speed. You may move as fast as your automated verification carries you, and
no faster on the part only a human can check.

## 3 · The gate — one recorded outcome

```bash
add gate <slug> PASS --by "<name>"          # a PASS auto-closes (add done only after RISK-ACCEPTED)
```

Exactly one outcome, always recorded:
- **PASS** — complete, fresh, bound evidence and clean residue. At **quick** depth, on a green,
  no-residue, `covers`-bound receipt the AI may record the PASS itself at `process` authority — an
  explicit pass you run, never an engine auto-verdict. Residue, or a higher sensitivity floor,
  escalates to a human.
- **RISK-ACCEPTED** — a known, signed acceptance of a non-security risk. Sign it with the reason the
  engine requires: `add gate <slug> RISK-ACCEPTED --by "<name>" --reason "<owner · ticket · expiry>"`.
- **HARD-STOP** — a security finding, or a gate that cannot be honestly passed. The task does **not**
  close: it stays open, and the finding goes back to **Direction** as a change-request (fix the build,
  or add the Must the gate exposed), then you re-Verify. A **security** HARD-STOP always escalates to a
  human and is **never** folded into a RISK-ACCEPTED — and this one is **engine-enforced**: `gate`
  refuses a `RISK-ACCEPTED` on any **security-floored** node (resolve it to PASS, or HARD-STOP), and
  refuses a `PASS` on one carrying no lens. Security-floored = `sensitivity: security`, **or** a
  `scope:` entry matching `index.md`'s `sensitive_paths:` — the path floor arms both refusals, so a
  task editing a sensitive path cannot sign itself away by omitting `sensitivity:`.

No silent skips: a gate that isn't PASS is RISK-ACCEPTED or HARD-STOP, on the record with an owner.
Present the gate via `gate.md`.

## 4 · Observe → learn

Emit any lesson as a tagged delta (`deltas.md`) — it sharpens a 5-DD spec at close. Reuse the checks as
production monitors; what production teaches becomes the next node's Direction (`loop.md`). A milestone
is done when its **goal** is met (exit criteria checked), not merely when its tasks are.
