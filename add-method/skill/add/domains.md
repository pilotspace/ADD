# ADD across domains — one spine, many vocabularies

ADD's trust spine is already domain-neutral: the sweep dimensions name no code, the `covers:`
grammar names no code, and the freshness digest hashes any git-tracked file — data and prose
included. What is code-shaped is the **vocabulary and the worked examples**. This ref supplies both.

Nothing here changes what PASSES. A domain configures what gets **authored** — the words, the
lenses, the checker — never what a gate accepts. That asymmetry is the whole reason a receipt
still means the same thing in finance as in code.

## 1 · Earn a real receipt — write the checker

When no test runner exists for your domain, **write one**. `add run` parses JUnit XML and does not
care what produced it, so any script that compares a measured value against a threshold your frozen
`## RULES` already state earns the top rung — `kind: test-ids`, every `covers:` referent bound.

The threshold belongs in the frozen Must, never inside the checker. That is what keeps this honest:
the human approves the number at freeze, and the checker only compares against it.

<!-- checker-recipe -->
```python
import json, sys, xml.etree.ElementTree as ET

d = json.load(open("recon.json"))            # your domain artifact — data, not code
cases = []                                    # (name, passed, message)
cases.append(("test_variance_within_materiality",
              d["variance"] <= 0.005 * d["gross"],          # the threshold M1 froze
              f'variance {d["variance"]} exceeds 0.5% of {d["gross"]}'))
cases.append(("test_every_variance_line_cited",
              all(line.get("source_doc") for line in d["lines"]),
              "a variance line carries no source document"))

suite = ET.Element("testsuite", name="checks.recon", tests=str(len(cases)))
for name, ok, msg in cases:
    tc = ET.SubElement(suite, "testcase", classname="checks.recon", name=name)
    if not ok:
        ET.SubElement(tc, "failure", message=msg).text = msg
ET.ElementTree(suite).write(sys.argv[1])
sys.exit(0 if all(ok for _, ok, _ in cases) else 1)
```

Cite those IDs from `## CHECKS` exactly as a test runner would, then run it like any other build:

```bash
add run <slug> --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- \
  python3 checks/recon.py "${TMPDIR:-/tmp}/add-run.xml"
```

**Declare the artifact in `scope:`.** A digested data file makes the receipt `freshness: content` —
edit the ledger after the run and the gate refuses the stale green. **Without a git-tracked artifact
freshness falls back to mtime**, and the receipt says so; do not claim stale-green protection you
did not earn.

The same shape covers eval scores, reconciliation deltas, backtest returns, contrast ratios,
plan-diff summaries, and citation resolution (a reference that resolves to nothing is a failing
case, not a warning). It does **not** cover taste — brand voice, visual polish, prose elegance.
Those gate weakly on purpose; that is the evidence ladder being honest, not a gap to paper over.

## 2 · Your domain's word, ADD's floor

Floors are computed by the engine and the set is closed. Map your vocabulary **onto** it, upward
only — never rename anything into it.

| Domain word | Floor | Why |
|---|---|---|
| regulatory · statutory · licensing | security | an unlawful artifact is never a signed risk |
| privilege · confidentiality | security | disclosure cannot be undone |
| patient safety · clinical | security | harm is irreversible |
| PII · consent · retention | data | the existing data floor already fits |
| model · schema · system-of-record | architecture | it forecloses downstream choices |

A word this table does not carry inherits the closed-floor rule already in force: **when in doubt,
size up**. Absence from the table is never evidence that no floor applies.

## 3 · Frame the bundle — re-author the lenses

Only `code` and `doc` ship as profiles, and `init` refuses any other name — a profile is a set of
spec lenses that has to exist, not a label your domain can assert into being.

Start from `add init --profile doc "<name>"` — its four lenses already assume no test runner —
then rewrite each spec's `## Now` line in your domain's language, **before** creating the first
task, so no contract freezes against code-framed lenses.

| Lens | Rewrite `## Now` to |
|---|---|
| domain | what the work must get right about the subject |
| experience | who consumes the output and what they need from it |
| quality | what counts as proof here — name the checker |
| method | how drafts proceed to a verdict, and what one costs |

Never overwrite a spec a human already edited — `init`'s own rule is that a human's file outranks
a template, and re-authoring inherits it.
