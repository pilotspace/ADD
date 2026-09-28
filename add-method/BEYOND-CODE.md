# ADD beyond code — one month-end close, end to end

You are closing the books. A bank statement and a ledger disagree by some amount, you have to
decide whether that gap is acceptable, and every line of it needs a source document behind it.
Nobody is writing software.

This walkthrough takes that job to a **verified** result — one whose green is backed by a check
that ran at a known commit, not by a reviewer's feeling that the spreadsheet looked right. It is
the same three beats a software team uses, because the part that makes them trustworthy was
never about code:

> **Direction → Build → Verify**

**The checker and the ledger below are executed by ADD's own test suite**
(`tests/book/test_beyond_code.py`): the ledger must pass, a blown threshold and an uncited line
must fail. A walkthrough nobody runs is a promise nobody kept.

> Building software instead? [GETTING-STARTED.md](./GETTING-STARTED.md) walks the same loop with
> a code example.

---

## What ADD is actually offering you

Not automation. **A record of why a number was accepted, that cannot be quietly edited after the
fact to look better.**

| | What it means at month-end |
|---|---|
| **A sealed threshold** | the materiality threshold is written and committed *before* anyone reconciles the variance — so the number was never chosen to fit the answer |
| **A recorded run** | the verdict names the command that checked the ledger, its exit code, and the commit it ran on |
| **A visible change** | moving the threshold or the checker after the seal shows up in `git diff`; changing the ledger after the verdict means the verdict is about a commit that is no longer current |

In a spreadsheet, changing a figure after sign-off leaves no trace. Here the sign-off names the
exact version it signed.

---

## 0 · What you need

- **A folder under git.** `git init` is enough. The seal is a commit.
- **Python 3**, for a checker of about twenty lines.
- **A coding agent** (Claude Code, Cursor, Codex, …). You talk; it drives. Every step here is one
  you *can* do yourself.

## 1 · Install

```bash
npx @pilotspace/add init        # or: pip install pilotspace-add && pilotspace-add init
```

Then `/add` and describe the job. On first use the agent writes `.add/PROJECT.md` for your domain;
rewrite each spec's `## Now` in your own language before the first task — lenses are cheap to
reframe now and expensive after a contract has been sealed against them.

## 2 · The job, as a task

Month-end close touches financial **data**, so it is at least a Task. Its artifact is the ledger
extract — data, not code:

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

(That is the ledger *after* the close. When the task starts, line `v2` has no source document.)

## 3 · Direction — decide the threshold before you see whether it holds

The task file `.add/tasks/close-2026-07.md` has `kind: data`, `scope: [ledger.json, checks/close.py]`,
and says what must be true, in your own words:

<!-- recon-rules -->
```
## RULES
- M1 unexplained variance stays within materiality — at most 0.5% of gross (from: finance policy FP-12)
- R:UNCITED a variance line with no source document is never accepted (from: audit guidance)

## ASSUMPTIONS
- A1 [when] the policy does not say whether 0.5% itself passes → exactly 0.5% passes → a one-cent difference in what counts as material
- A2 [absent] a line with an empty source_doc string is not mentioned → treated as uncited → none
```

**The threshold lives in the rule, and the rule is sealed.** A threshold buried in a script is a
number anyone can move on the day it fails.

Then each rule gets a check. Non-code work names its mode — here, a `script`:

<!-- recon-checks -->
```
## CHECKS
- C1 covers: M1, A1 · script · checks/close.py::test_variance_within_materiality
- C2 covers: R:UNCITED, A2 · script · checks/close.py::test_every_variance_line_cited
```

There is no test runner for month-end close, so the check is a script:

<!-- recon-checker -->
```python
import json, sys

d = json.load(open("ledger.json"))            # your artifact — data, not code
cases = [                                      # (name, passed, message)
    ("test_variance_within_materiality",
     d["variance"] <= 0.005 * d["gross"],      # the threshold M1 sealed
     f'variance {d["variance"]} exceeds 0.5% of {d["gross"]}'),
    ("test_every_variance_line_cited",
     all(line.get("source_doc") for line in d["lines"]),
     "a variance line carries no source document"),
]
for name, ok, msg in cases:
    print(f'{"PASS" if ok else "FAIL"} checks/close.py::{name}' + ("" if ok else f" — {msg}"))
sys.exit(0 if all(ok for _, ok, _ in cases) else 1)
```

Run it against the ledger as it stands. It must fail for the right reason — the missing source
document, not a typo:

<!-- recon-red -->
```text
$ python3 checks/close.py
PASS checks/close.py::test_variance_within_materiality
FAIL checks/close.py::test_every_variance_line_cited — a variance line carries no source document
```

Now the seal — the task file and the checker, committed together:

```bash
git add .add/tasks/close-2026-07.md checks/close.py
git commit -m "freeze(close-2026-07): July close within materiality, every line cited"
```

## 4 · Build — do the close

This is the real work: trace line `v2` to the interest statement, record `INT-2026-07-0912` as its
source, and commit the ledger. The threshold and the checker are sealed; the ledger is what you
change. If the policy itself turns out to be wrong, that is a `refreeze(close-2026-07): <why>`
commit with the reason under `## LOG` — visible to every reviewer, never a quiet edit.

## 5 · Verify — seal, fresh run, verdict

```bash
F=$(git log -1 --format=%H --grep='freeze(close-2026-07)')
git diff $F HEAD -- .add/tasks/close-2026-07.md checks/close.py     # must print nothing
python3 checks/close.py                                              # on the committed ledger
```

Then read what the checks cannot see — is each cited document real, and does it say what the line
claims? — and write the verdict:

```markdown
## EVIDENCE
freeze: <sha> · head: <sha>
seal: git diff <freeze> <head> -- .add/tasks/close-2026-07.md checks/close.py → empty
check: `python3 checks/close.py` → exit 0 · 2 passed
residue: data — both source documents opened and match their amounts; no line added after the freeze
verdict: PASS
```

Commit: `verify(close-2026-07): PASS`.

## 6 · What you are actually buying

**A blown threshold fails the run.** Push the variance past 0.5% and the checker exits 1; the
verdict cannot honestly be `PASS`.

**A moved threshold is visible.** Change `0.005` in the checker after the seal and the seal check
prints the diff. The only honest way to change it is a `refreeze` commit that says why.

**A late ledger edit is visible.** Change a figure after the verdict and the evidence still names
the commit it was about — anyone re-running the check at `HEAD` sees whether it still holds.

> **What a green verdict does not mean.** It proves the checks you wrote ran and passed on that
> commit. It never proves they were *enough*. A check that asserts nothing still passes. Deciding
> what would have caught the error is your judgement; ADD makes sure the record shows what you
> actually checked.

---

## Where this goes next

The same shape covers eval scores, backtest returns, plan-diff review, contrast ratios, and
citation resolution — a reference that resolves to nothing is a failing case, not a warning. What
it does **not** cover well is taste: brand voice, visual polish, prose elegance get a `rubric`
check at best, and the record should say so.

- The method, chapter by chapter — https://pilotspace.github.io/ADD/
- The same loop with a code example — [GETTING-STARTED.md](./GETTING-STARTED.md)

**Direction before speed. Trust comes from checks you declared and ran — never from a result that
reads plausible.**
