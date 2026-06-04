# Getting started with ADD — your first feature in ~10 minutes

This is a runnable walkthrough. Follow it top to bottom and you'll take one real
feature — *transfer money between a user's own accounts* (the book's worked
example) — from nothing to a verified, passing result, using the ADD method.

You'll learn the whole loop by doing it once:

> **Specify → Scenarios → Contract → Tests → Build → Verify → Observe**

ADD is **AI-first**: you talk to the agent and it drives the method — you don't
hand-type the commands. The commands below are the agent's hands (and your escape
hatch); the rest of this guide shows both so you can see what the agent does.

---

## The fast path — talk to the agent

After installing (step 1 below), the whole on-ramp is one move:

```
in Claude Code:  /add
you:             "I want to let users transfer money between their own accounts."
```

From there the agent runs the **on-ramp** for you:

1. **Orient** — it reads `add.py status` (the resume point), never re-reading your repo.
2. **Intake** — it sizes your request into versioned scope and proposes a **milestone**
   (goal · scope · breadth-first tasks · exit criteria). *You confirm the shape.*
3. **One-approval front** — for each task it drafts Spec + Scenarios + Contract + Tests
   as one bundle. *You give one approval at the frozen contract.*
4. **Self-driving run** — build→verify runs to green; a security finding always stops
   back to you.

So a milestone-sized feature is: **describe it → confirm the milestone → approve each
contract → review the result.** Everything between is the agent.

> New term: **On-ramp** — the install→first-milestone path. See `docs/appendix-c-glossary.md`.

---

## 0 · Prerequisites

- **Python 3.10+** — required; the tool itself is stdlib-only (no pip dependencies).
- **One installer**, whichever you already have: **Node.js ≥ 18** (for `npx`) *or*
  **pip** (Python). Both install the exact same `.add/` runtime.
- A project folder. It can be empty or an existing repo.

> **Windows:** use `py` wherever this guide writes `python3` (the Python launcher on
> Windows) — e.g. `py .add\tooling\add.py status`. Both installers handle the install
> step for you; only the by-hand `add.py` commands below differ.

---

## 1 · Install

From your project root, pick **one** path — both produce the same install:

**Option A — npm (Node.js ≥ 18):**

```bash
npx @pilotspace/add init --name "My App" --stage prototype
```

**Option B — pip (Python 3.10+):**

```bash
pip install pilotspace-add
pilotspace-add init --name "My App" --stage prototype
```

Either one creates `.add/` (your runtime), drops the `add` skill into
`.claude/skills/add/`, and bundles the book into `.add/docs/`. Pick the stage that
matches your intent — `prototype`, `poc`, `mvp`, or `production`. You can change it
later with `python3 .add/tooling/add.py stage mvp`.

> Why stages exist: the steps never change, only how *deeply* you run them.
> See `.add/docs/10-setup-and-stages.md`.

---

## 2 · Orient — the command you'll use most

```bash
python3 .add/tooling/add.py status
```

`add.py status` is your home base. It reads `.add/state.json` and tells you the
project stage, the active task, and which phase you're in. **Start every session
with it** — that's how ADD resumes work without re-reading your whole repo.

> Tip: shorten typing with an alias — `alias add="python3 .add/tooling/add.py"` —
> then you can run `add status`, `add advance`, etc. The rest of this guide writes
> the full `python3 .add/tooling/add.py ...` form so copy-paste always works.

And when you're mid-task and unsure what the current phase needs, ask:

```bash
python3 .add/tooling/add.py guide
```

`status` tells you *where* you are; `guide` tells you *what to do next* — the active
task's phase, the one concrete next action, the chapter to read, and the exact command
to run once that phase is done.

---

## 3 · Start your first feature

```bash
python3 .add/tooling/add.py new-task transfer --title "Transfer money between my accounts"
```

This scaffolds `.add/tasks/transfer/TASK.md` — **one file holding all seven phase
sections** — plus empty `tests/` and `src/` folders, and makes it the active task
at phase `specify`.

Open `.add/tasks/transfer/TASK.md` in your editor. You'll fill it top to bottom.

---

## Under the hood — the seven phases by hand (escape hatch)

Everything above is what the agent drives for you through the one-approval front. This
section is the **escape hatch**: the same seven phases run by hand, so you can see what
each one produces and step in manually whenever you want to. You never *have* to type
these — they are the agent's hands, and yours when you take the wheel.

The rhythm is always: **fill the section → run `python3 .add/tooling/add.py advance`.**
The tool keeps the `phase:` marker at the top of TASK.md in sync.

### Phase 1 — Specify (`docs/03-step-1-specify.md`)

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

### Phase 2 — Scenarios (`docs/04-step-2-scenarios.md`)

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

### Phase 3 — Contract (`docs/05-step-3-contract.md`)

In **§3**, fix the external shape and **freeze** it (`Status: FROZEN @ v1`):

```
POST /transfers  body: { fromAccountId, toAccountId, amount }
  200 -> { transferId, fromBalance, toBalance }
  400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
  403 -> { error: "forbidden" }
```

A frozen contract is the seam that makes the AI build safe. Then advance.

### Phase 4 — Tests, red first (`docs/06-step-4-tests.md`)

Write one test per scenario into `.add/tasks/transfer/tests/`, then **run them and
confirm they FAIL** — there's no code yet. A test that passes now is testing
nothing. This is red/green TDD: red before green. Then advance.

### Phase 5 — Build (`docs/07-step-5-build.md`)

Now let the AI write code into `.add/tasks/transfer/src/` until **every test
passes** — without changing any test or the frozen contract. Honor the safety rule
(here: debit + credit in one atomic transaction). Then advance.

### Phase 6 — Verify (`docs/08-step-6-verify.md`)

In **§6**, confirm the evidence (all green, nothing weakened) and check what tests
miss: concurrency, security, architecture. Record the gate — and close the task:

```bash
python3 .add/tooling/add.py gate PASS
```

`gate PASS` marks the task `done`. (Use `gate HARD-STOP` to send it back to Build,
or `gate RISK-ACCEPTED` for a signed, non-security waiver.)

### Phase 7 — Observe (`docs/09-the-loop.md`)

In **§7**, note what to watch in production and the next spec delta. Every learning
becomes the next `new-task`. The flow is a loop, not a finish line.

---

## 5 · Self-check

Confirm your project is internally consistent at any time:

```bash
python3 .add/tooling/add.py check
```

It verifies state is valid, every task has its TASK.md, and markers match. Exit
code 0 means healthy — handy as a CI gate.

---

## 6 · Resume next session

Close your laptop, come back tomorrow, run:

```bash
python3 .add/tooling/add.py status
```

It tells you exactly where you left off and what to do next. No context rot — the
state lives on disk, not in a chat window.

---

## 7 · Where to read more

You just ran the method; now read *why* it's shaped this way:

- The shift & principles — `.add/docs/00-introduction.md`, `.add/docs/01-principles.md`
- The flow end to end — `.add/docs/02-the-flow.md`
- Each step in depth — `.add/docs/03..09`
- Operating it on a team — `.add/docs/11-governance.md`, `.add/docs/12-roles.md`
- A fully worked example — `.add/docs/appendix-d-worked-example.md`

The rule to remember: **build the right thing (direction), prove it's right
(verification), and let the AI do the building in between.**
