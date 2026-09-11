# Beat 3 · Verify — trust on evidence, then the gate

A change is trusted because its checks pass **and** the residue tests can't catch was examined — not
because the diff reads plausible. Verify is where that trust is recorded, once. Judge it through a
**lens**: the `.add/personas/` entry whose `flow:` names verify (else advisor) and whose `task-kinds:`
covers the node's `kind:`; no fit → `.add/personas-index/use-when.md`; none there → proceed. `add advise <slug> --persona <p>`.

## 1 · Gather the evidence — a fresh, bound receipt

```bash
add run <slug> -- <the test command, carrying its own `--junitxml="${TMPDIR:-/tmp}/add-run.xml"`>
```

`run` executes your command, parses the JUnit report, and writes a **Run receipt** under
`.add/tasks/<slug>.d/runs/`. Your command WRITES the report; `run` READS it, sniffing the path from the
command you handed it (either spelling of `--junitxml`, `=` or the next token; the last one wins). Name
no path and the receipt records only an exit code, nothing binds, and the gate refuses naming the unbound
rules; a runner that reports where its command line never says states `--junitxml` BEFORE the `--`.
Two properties the gate will demand:
- **fresh** — the receipt records the git blob hash of every in-`scope:` file at run time; the gate
  recomputes it and refuses on any difference (the stale-green failure). A directory scope enumerates
  through git, so gitignored build output never enters the digest. Outside git: mtime, and it says so.
- **bound** — every check ID in `## CHECKS` must appear in the receipt with `outcome: pass`; a `covers:`
  naming a check that did not demonstrably pass fails the gate. Probed assumptions bind the same way.

The gate also demands the build was **entered**: an `act: brief` stamp between the freeze and this
receipt's run (`phases/build.md`); briefing after the fact buys nothing — re-run under the brief.

**Keep the receipt command narrow.** The gate demands exactly the checks `## CHECKS` binds — wrap the
**narrowest command that reports every bound check** (one file, one marker, one target); the full suite
rides CI or a backgrounded run, and a slow unbound check stays out of the receipt loop. The wrapped
command's ceiling is **900 s**; a legitimately slow bound check raises it with `--timeout <s>` — a
timeout is *recorded* as exit 124 and the gate refuses the PASS.

Evidence kinds the engine can stamp, strongest first: `test-ids` (a runner reported the IDs your
`covers:` names) > `command-exit` (exit 0, nothing bound). A findings-only explore gates on `sources`.
A weaker kind is a *visible* weakening (the receipt records which it earned), never a silent one.

## 2 · Check the residue — three lenses

Automation covers the checks; it does not cover everything. Examine, by hand, the narrow set tests miss:
- **security** — always escalates to a human; a finding is a **HARD-STOP**, whatever the evidence says.
- **concurrency** — races, ordering, atomicity under load.
- **architecture** — boundary and dependency violations a passing test won't reveal.

This residue stays at human speed: as fast as automated verification carries you, no faster on the rest.

**The refute-read.** Before a verdict, read the green as a skeptic and RECORD it: `add refute <slug>
--by "<name>" --tier T2 --held|--found "<input>" --probes N`. A green that survives is *earned*; one never read against
is only *reported* — at a plan-or-human floor the gate refuses a PASS with no refute citing the receipt (R:UNREFUTED) or a refuted one (R:REFUTED); quick, process and explore are exempt.

<!-- probe-derivation -->
A probe is a check the builder never saw as a target. Derive one to three from the frozen node, and only
these ways: instantiate a frozen rule with values the bound checks do not use · compose two frozen rules
(a Reject reached through a Must's path) · walk a boundary a rule or filled edge implies · vary a swept
dimension the ASSUMPTIONS sweep named. Never invent a requirement: an expected answer
not derivable from frozen RULES, EDGES and interviewed ASSUMPTIONS is a spec silence — a change-request
back to Direction, never a finding. A probe that finds a defect graduates into a filled edge at the
refreeze; one that holds stays in the repo, unbound.
<!-- /probe-derivation -->

**Who refutes — the tier ladder.** T0 nobody (quick depth · process floor: receipt + residue) · T1 the
building session, after its own green — a prelude, optional, never the rung's answer · T2 the DEFAULT at
floor ≥ plan: SPAWN a fresh session — `add-advisor` in `refute` mode or a new `add-worker` verify beat —
briefed from the frozen node before it reads the diff, and record the line it returns with `--tier T2` ·
T3 a human, at the interview and the gate (floor human) · T4 a protected holdout the builder cannot read — a CI recipe, not shipped: a prompt is not isolation.

## 3 · The gate — one recorded outcome

```bash
add gate <slug> PASS --by "<name>"          # a PASS auto-closes (add done only after RISK-ACCEPTED)
```

Exactly one outcome, always recorded:
- **PASS** — complete, fresh, bound evidence and clean residue. At **quick** depth, on a green,
  no-residue, `covers`-bound receipt the AI may record the PASS itself at `process` authority — an
  explicit pass you run, never an engine auto-verdict; residue or a higher floor escalates to a human.
- **RISK-ACCEPTED** — a known, signed acceptance of a non-security risk: `add gate <slug> RISK-ACCEPTED --by "<name>" --reason "<owner · ticket · expiry>"`.
- **HARD-STOP** — a security finding, or a gate that cannot be honestly passed. The task does **not**
  close: the finding goes back to **Direction** as a change-request (fix the build, or add the Must the
  gate exposed), then re-Verify. A **security** HARD-STOP always escalates to a human and is **never**
  folded into a RISK-ACCEPTED — engine-enforced: `gate` refuses a `RISK-ACCEPTED` on any
  **security-floored** node (resolve it to PASS, or HARD-STOP) and a `PASS` on one carrying no lens.
  Security-floored = `sensitivity: security`, **or** a `scope:` entry matching `index.md`'s
  `sensitive_paths:` — so a task editing a sensitive path cannot sign itself away by omitting `sensitivity:`.

No silent skips: a gate that isn't PASS is RISK-ACCEPTED or HARD-STOP, on the record with an owner.
Present the gate via `gate.md`.

## 4 · Observe → learn

Emit any lesson as a tagged delta (`deltas.md`) — it sharpens a 5-DD spec at close. Reuse the checks as
production monitors; a production failure becomes a filled `E<n>` with a bound acceptance check on the next
node that touches the surface (`loop.md`). A milestone is done when its **goal** is met, not merely its tasks.
