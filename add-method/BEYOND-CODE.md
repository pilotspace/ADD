# ADD beyond code — one month-end close, end to end

You are closing the books. A bank statement and a ledger disagree by some amount, you
have to decide whether that gap is acceptable, and every line of it needs a source
document behind it. Nobody is writing software.

This walkthrough takes that job from nothing to a **verified** result — one whose green
is backed by a recorded receipt, not by a reviewer's judgement that the spreadsheet
looked right. It is the same three beats a software team uses, because the part that
makes them trustworthy was never about code:

> **Direction → Build → Verify**

**Every command and file below is executed by ADD's own test suite** on each run
(`tests/skill/test_beyond_code_walkthrough.py`). If any of it stops working, that test
goes red before you ever read this page. A walkthrough nobody runs is a promise nobody
kept.

> Building software instead? [GETTING-STARTED.md](./GETTING-STARTED.md) walks the same
> loop with a code example.

---

## What ADD is actually offering you

Not automation. **A record of why a number was accepted, that cannot be edited after
the fact to look better.**

Three things hold that up, and none of them assume code:

| | What it means at month-end |
|---|---|
| **A frozen contract** | you approve the materiality threshold *before* anyone looks at the variance — so the number was never chosen to fit the answer |
| **A bound receipt** | the verdict cites which checks ran and passed, by name, against which version of the ledger |
| **A refused stale green** | edit the ledger after the check ran and the gate refuses — the old pass no longer applies to the new file |

That last one is the whole thing. In a spreadsheet, changing a figure after sign-off
leaves no trace. Here it invalidates the sign-off.

---

## 0 · What you need

- **Python 3.10+** — ADD is stdlib-only, no dependencies. You will also write about
  twenty lines of Python for the checker in §4; if that is a hard no, this walkthrough
  is not yet your path.
- **A folder under git.** `git init` is enough. Without it ADD can only compare
  timestamps, and it will say so on the receipt rather than pretend otherwise.
- **A coding agent** (Claude Code, Cursor, Codex, …). ADD is agent-first: you talk, it
  drives. Every command here is one you *can* run yourself.

## 1 · Install, then frame the bundle for your domain

```bash
npx @pilotspace/add init        # or: pip install pilotspace-add && pilotspace-add init
```

The installer only drops files. Creating the bundle is a separate step, and it is where
you choose your **lenses** — the standing questions each spec answers:

```bash
python3 .add/tooling/cli.py init --profile doc "Month-end close"
```

`--profile doc` gives you four lenses that assume no test runner: *what the work must
get right · who consumes it · what counts as proof · how drafts reach a verdict*. The
`code` profile would ask how the product is built and what that forecloses — questions a
reconciliation has no answer to.

Two profiles ship, `code` and `doc`, and **`init` refuses any other name.** Ask it for a
`finance` profile and it tells you what it actually has, rather than quietly handing you
the code lenses under a label it never understood.

Then rewrite each spec's `## Now` line in your own language before you create any task —
lenses are cheap to reframe now and expensive after a contract has frozen against them.

## 2 · The job, as a task

```bash
add new Task close --title "Month-end close" --depth standard --scope "ledger.json"
```

`--scope` is the load-bearing flag. It names the files this task's verdict is *about*,
and it is what makes the stale-green refusal possible: the gate digests exactly these
files and compares them against what the check actually ran on.

Your ledger extract is the artifact under check — data, not code:

<!-- recon-data -->
```json
{
  "period": "2026-07",
  "gross": 1000000,
  "variance": 3200,
  "lines": [
    {"id": "v1", "amt": 2100, "source_doc": "BS-2026-07-p4"},
    {"id": "v2", "amt": 1100, "source_doc": "INT-2026-07-0912"}
  ]
}
```

## 3 · Direction — decide the threshold before you see whether it holds

This is the beat that earns everything else. Write what must be true, in your own words:

<!-- recon-rules -->
```
<must>
- M1 unexplained variance stays within materiality — at most 0.5% of gross
</must>
<reject>
- R:UNCITED a variance line with no source document must never be accepted -> "UNCITED"
</reject>
```

**The threshold lives in the Must, never in the checker.** That is what makes the record
honest: you approved 0.5% at freeze, and the script can only compare against it. A
threshold buried in a script is a number anyone can move on the day it fails.

Then bind each rule to the check that will prove it:

<!-- recon-checks -->
```
- checks.close::test_variance_within_materiality · covers: M1 · variance is at most 0.5% of gross
- checks.close::test_every_variance_line_cited · covers: R:UNCITED · every line names a source document
```

Every `M<n>` and every `R:<NAME>` needs some check naming it. Leave one unbound and
`gate PASS` refuses and tells you which — a rule nobody checks is a rule nobody kept.

Now the one approval:

```bash
add freeze close --by "your name" --authority human
```

That stamps a digest over your rules and checks. Change either afterwards and the gate
refuses until you re-freeze, deliberately: a contract that can be edited to match the
result is not a contract.

> **Floors you do not get to choose.** If this work touched personal data it would sit
> at the `data` floor; a regulatory or licensing question sits at the `security` floor,
> which always stops back to a human. The set is closed and the engine computes it from
> the task — you map your vocabulary onto it, never the other way round.

## 4 · Build — write the checker

Entering the build compiles the sealed contract into the working prompt, and the gate
later refuses a verdict that never entered one:

```bash
add brief close
```

There is no test runner for month-end close, so write one. `add run` reads JUnit XML and
does not care what produced it, so ~20 lines of Python earns the same top-rung receipt a
software test suite does:

<!-- recon-checker -->
```python
import json, sys, xml.etree.ElementTree as ET

d = json.load(open("ledger.json"))            # your artifact — data, not code
cases = []                                     # (name, passed, message)
cases.append(("test_variance_within_materiality",
              d["variance"] <= 0.005 * d["gross"],          # the threshold M1 froze
              f'variance {d["variance"]} exceeds 0.5% of {d["gross"]}'))
cases.append(("test_every_variance_line_cited",
              all(line.get("source_doc") for line in d["lines"]),
              "a variance line carries no source document"))

suite = ET.Element("testsuite", name="checks.close", tests=str(len(cases)))
for name, ok, msg in cases:
    tc = ET.SubElement(suite, "testcase", classname="checks.close", name=name)
    if not ok:
        ET.SubElement(tc, "failure", message=msg).text = msg
ET.ElementTree(suite).write(sys.argv[1])
sys.exit(0 if all(ok for _, ok, _ in cases) else 1)
```

The names must match what you cited in `## CHECKS` exactly — the gate binds on the id in
the report, not on your intent.

## 5 · Verify — run it, then take the verdict

```bash
add run close --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- \
  python3 checks/close.py "${TMPDIR:-/tmp}/add-run.xml"
```

The flag appears twice on purpose: the first tells ADD where to *read* the report, the
one after `--` is part of your command that *writes* it. Omit the second and the receipt
records only an exit code, and nothing binds to your rules.

Your receipt now says `kind: test-ids` — the top rung — and `freshness: content`, meaning
it digested your ledger's git blob. **Without git, freshness degrades to timestamps and
the receipt says so.** Do not claim protection you did not earn.

```bash
add gate close PASS --by "your name"
```

## 6 · The two refusals — what you are actually buying

Both of these are executed by ADD's test suite. Neither is a description.

**A blown threshold fails the run.** Push the variance past 0.5% and
`test_variance_within_materiality` fails, the receipt records the failure, and the gate
refuses to record a `PASS` over it. Nobody has to notice.

**A late edit refuses the stale green.** Run the checks, get a clean pass, then change
one figure in `ledger.json`. The gate now refuses: the files it digested are no longer
the files that were checked. Your earlier green was true about a ledger that no longer
exists, and ADD will not let it stand in for this one.

These are different refusals for different reasons, and the message tells you which.
That distinction is the point — one means *the numbers are wrong*, the other means
*this verdict is about a file you have since changed*.

> **What a green gate does not mean.** It proves the checks you declared ran, passed,
> and are bound to your rules. It never proves they were *enough*. A check that asserts
> nothing still binds and still passes. Deciding what would have caught the error is
> your judgement; ADD can only prove you ran what you wrote.

---

## Where this goes next

The same shape covers eval scores, backtest returns, plan-diff review, contrast ratios,
and citation resolution — a reference that resolves to nothing is a failing case, not a
warning. What it does **not** cover is taste: brand voice, visual polish, prose elegance
gate weakly on purpose. That is the evidence ladder being honest rather than a gap.

- The method, chapter by chapter — https://pilotspace.github.io/ADD/
- Mapping your vocabulary onto the closed floors — `skill/add/domains.md`
- The same loop with a code example — [GETTING-STARTED.md](./GETTING-STARTED.md)

**Direction before speed. Trust comes from checks you declared and ran — never from a
result that reads plausible.**
