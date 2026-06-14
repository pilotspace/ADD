# Getting started with ADD — your first feature in ~10 minutes

This is a runnable walkthrough. Follow it top to bottom and you'll take one real
feature — *transfer money between a user's own accounts* (the book's worked
example) — from nothing to a verified, passing result, using the ADD method.

You'll learn the whole loop by doing it once:

> **Specify → Scenarios → Contract → Tests → Build → Verify → Observe**

ADD is **AI-first**: you talk to the agent and it drives the method. Reading this
guide top to bottom, you will type exactly **one shell command — the install**.
After that, everything happens in conversation (`/add` is how you start it, not
a terminal command): the agent's hands are the CLI, and the same CLI is your
escape hatch whenever you want to take the wheel (it's all in the appendix at
the end).

---

## 0 · Prerequisites

- **Python 3.10+** — required; the tool itself is stdlib-only (no pip dependencies).
- **One installer**, whichever you already have: **Node.js ≥ 18** (for `npx`) *or*
  **pip** (Python). Both install the exact same `.add/` runtime.
- A project folder. It can be empty or an existing repo.

> **Windows:** use `py` wherever this guide writes `python3` (the Python launcher on
> Windows) — e.g. `py .add\tooling\add.py status`. Both installers handle the install
> step for you; only the by-hand `add.py` commands in the appendix differ.

---

## 1 · Install — the one command you type

From your project root, pick **one** path — both produce the same install:

**Option A — npm (Node.js ≥ 18):**

```bash
npx @pilotspace/add init
```

**Option B — pip (Python 3.10+):**

```bash
pip install pilotspace-add
pilotspace-add init
```

No flags needed — the agent infers your project's name from the folder and starts
at the `prototype` stage. (Prefer to choose up front? Both installers take
`--name "My App" --stage prototype|poc|mvp|production`; the stage can also be
changed later — see the appendix.)

Either one creates `.add/` (your runtime), drops the `add` skill into
`.claude/skills/add/`, and bundles the book into `.add/docs/`. It deliberately
does **not** initialise the project — that's the agent's first move, so nothing
gets decided without you in the loop.

**When the install finishes: open Claude Code and type `/add`.** That's the
handoff — from here on it's conversation, not terminal commands.

> Why stages exist: the steps never change, only how *deeply* you run them.
> See `.add/docs/10-setup-and-stages.md`.

### Updating to a newer ADD — no re-install

When a new ADD version ships, refresh a project in two steps: bump the package
(your package manager), then re-materialize it into the project with `update`:

```bash
# npm — one shot (npx fetches latest, then re-materializes into this project):
npx @pilotspace/add@latest update

# pip — one shot via pipx (the npx analog: fetch latest + run):
pipx run pilotspace-add update

# …or plain pip, in two steps:
pip install -U pilotspace-add && pilotspace-add update
```

`update` clean-replaces the managed layer (`skill` · `.add/tooling` · `.add/docs`)
and **never touches your work** — `state.json`, `PROJECT.md`, milestones, tasks and
archive are left exactly as they were (it backs `state.json` up first regardless). It
is idempotent (same version twice is a no-op) and writes a `.add/.add-version` stamp.
Run `… update --check` to see whether a project is behind the installed package.

---

## 2 · Your first feature — talk to the agent

In Claude Code, the whole onboarding is one move:

```
in Claude Code:  /add
you:             "I want to let users transfer money between their own accounts."
```

From there the agent runs the **onboarding** for you:

1. **Orient** — it reads the project state (the resume point), never re-reading
   your repo. On a fresh install it initialises the project itself and drafts
   the foundation for your sign-off (the **baseline approval** — the one signature the
   installer's closing message points at).
2. **Intake** — it sizes your request into versioned scope and proposes a **milestone**
   (goal · scope · breadth-first tasks · exit criteria). *You confirm the shape.*
3. **Specification bundle** — for each task it drafts Spec + Scenarios + Contract + Tests
   as one bundle, led by its lowest-confidence points. *You give one approval at the
   frozen contract.*
4. **Self-driving run** — build→verify runs to green; a security finding always stops
   back to you.

So a milestone-sized feature is: **describe it → confirm the milestone → approve each
contract → review the result.** Everything between is the agent. For the
transfer-money feature above, that's four short conversations — and zero typed
commands.

> New term: **Onboarding** — the install→first-milestone path. See `.add/docs/appendix-c-glossary.md`.

---

## 3 · What just happened (and your override)

Behind the conversation, the agent drove the CLI: it read the resume point, sized
the milestone, froze the contract you approved, ran the tests red, built to green,
and recorded the gate. The state lives on disk, not in the chat window.

If you ever want to see that state yourself — or take over entirely — the same
CLI is yours:

```bash
python3 .add/tooling/add.py status
```

`add.py status` is the resume point: project stage, active task, current phase.
And `add.py guide` tells you what the current phase needs — its `guide  :` line
names the exact phase-guide file to read (`.claude/skills/add/phases/…` — plain
markdown), which is how **any** agent — Claude, Cursor, Copilot, Codex — follows
ADD through the CLI alone.

> Tip: shorten typing with an alias — `alias add="python3 .add/tooling/add.py"` —
> then you can run `add status`, `add guide`, etc. These are override and resume
> surfaces, not steps you owe the method: the appendix walks the full by-hand path
> whenever you want the wheel.

---

## Resume next session

Close your laptop, come back tomorrow, type `/add` again — the agent reorients
itself from disk and continues exactly where you left off. No context rot.

The same resume point is yours directly:

```bash
python3 .add/tooling/add.py status
```

---

## Self-check

Confirm your project is internally consistent at any time:

```bash
python3 .add/tooling/add.py check
```

It verifies state is valid, every task has its TASK.md, and markers match. Exit
code 0 means healthy — handy as a CI gate.

---

## Enforce the decision points in CI

`add.py audit` re-verifies every recorded human gate on your board — a named
human at each contract freeze, exactly one gate outcome per done task, a human
reviewer wherever the security line carries a note. It exits non-zero naming
the task and the finding, which makes it a CI gate: enforcement runs on a
machine the agent does not control, so the agent can never stamp its own work
green (*never self-gate*).

Drop this workflow into `.github/workflows/seam-audit.yml`:

```yaml
name: seam-audit

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  seam-audit:
    name: Decision-point audit (recorded human gates)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Audit recorded decision points
        run: python3 .add/tooling/add.py audit
```

The command is the same one you can run locally — the installer already placed
`add.py` at `.add/tooling/add.py`, and the audit is read-only (it never edits
your board). A red `seam-audit` job means a decision record is malformed or a
security note was left to the auto-gate; fix the record (or escalate the gate
to a human), never the auditor.

---

## Under the hood — the seven phases by hand (escape hatch)

Everything above is what the agent drives for you through the one-approval flow. This
appendix is the **escape hatch**: the same seven phases run by hand, so you can see what
each one produces and step in manually whenever you want to. You never *have* to type
these — they are the agent's hands, and yours when you take the wheel.

The rhythm is always: **fill the section → run `python3 .add/tooling/add.py advance`.**
The tool keeps the `phase:` marker at the top of TASK.md in sync.

### Before the phases — initialise and scaffold

Starting cold? Install first as in §1 (`npx @pilotspace/add init`). Then
initialise once and scaffold the task yourself (the agent normally does both):

```bash
python3 .add/tooling/add.py init
python3 .add/tooling/add.py new-task transfer --title "Transfer money between my accounts"
```

> **Note:** the installer's closing hint shows `init --await-lock` — that form
> arms the baseline-approval gate so a *human* signs the AI-drafted foundation before
> any build. Plain `init` skips that gate, which is fine here: by hand, the
> human IS the one driving every step.

This scaffolds `.add/tasks/transfer/TASK.md` — **one file holding all seven phase
sections** — plus empty `tests/` and `src/` folders, and makes it the active task
at phase `specify`. Open it in your editor; you'll fill it top to bottom.

You can also change the project's depth at any time:

```bash
python3 .add/tooling/add.py stage mvp
```

### Phase 1 — Specify (`.add/docs/03-step-1-specify.md`)

Write the rules in **§1**. State what it *must* do, what it must *reject* (each
with a named error code), and what's true after success:

```
Must:
  - move an amount from one of my accounts to another of mine
  - amount > 0 ; source ≠ destination ; source has enough balance
After:
  - source balance -= amount, destination balance += amount
Reject:
  - amount <= 0           -> "amount_invalid"
  - source == destination -> "same_account"
  - balance < amount      -> "insufficient_funds"
  - account not mine      -> "forbidden"
```

Confirm every assumption (no FX, no daily limit in v1). Then:

```bash
python3 .add/tooling/add.py advance
```

### Phase 2 — Scenarios (`.add/docs/04-step-2-scenarios.md`)

In **§2**, turn each rule into a Given/When/Then. For every rejection, assert what
must stay **unchanged**:

```gherkin
Scenario: insufficient funds
  Given A has 20, mine
  When I transfer 50 from A to B
  Then it is rejected "insufficient_funds"
  And no balance changes
```

Then `python3 .add/tooling/add.py advance`.

### Phase 3 — Contract (`.add/docs/05-step-3-contract.md`)

In **§3**, fix the external shape and **freeze** it (`Status: FROZEN @ v1`):

```
POST /transfers  body: { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
```

A frozen contract is the decision point that makes the AI build safe. Then advance.

### Phase 4 — Tests, red first (`.add/docs/06-step-4-tests.md`)

Write one test per scenario into `.add/tasks/transfer/tests/`, then **run them and
confirm they FAIL** — there's no code yet. A test that passes now is testing
nothing. This is red/green TDD: red before green. Then advance.

### Phase 5 — Build (`.add/docs/07-step-5-build.md`)

Now let the AI write code into `.add/tasks/transfer/src/` until **every test
passes** — without changing any test or the frozen contract. Honor the safety rule
(here: debit + credit in one atomic transaction). Then advance.

### Phase 6 — Verify (`.add/docs/08-step-6-verify.md`)

In **§6**, confirm the evidence (all green, nothing weakened) and check what tests
miss: concurrency, security, architecture. Record the gate — and close the task:

```bash
python3 .add/tooling/add.py gate PASS
```

`gate PASS` marks the task `done`. (Use `gate HARD-STOP` to send it back to Build,
or `gate RISK-ACCEPTED` for a signed, non-security waiver.)

### Phase 7 — Observe (`.add/docs/09-the-loop.md`)

In **§7**, note what to watch in production and the next spec delta. Every learning
becomes the next `new-task`. The flow is a loop, not a finish line.

---

## Where to read more

You just ran the method; now read *why* it's shaped this way:

- The shift & principles — `.add/docs/00-introduction.md`, `.add/docs/01-principles.md`
- The flow end to end — `.add/docs/02-the-flow.md`
- Each step in depth — `.add/docs/03-step-1-specify.md` through `.add/docs/09-the-loop.md`
- Operating it on a team — `.add/docs/11-governance.md`, `.add/docs/12-roles.md`
- A fully worked example — `.add/docs/appendix-d-worked-example.md`

The rule to remember: **build the right thing (direction), prove it's right
(verification), and let the AI do the building in between.**
