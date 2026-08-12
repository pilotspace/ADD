# Getting started with ADD — your first feature in ~10 minutes

This is a runnable walkthrough. Follow it top to bottom and you'll take one real
feature — *transfer money between a user's own accounts* (the book's worked
example) — from nothing to a **verified** result: one whose green is backed by a
recorded receipt, not by a diff that reads plausible.

You'll learn the whole loop by doing it once. ADD has three beats:

> **Direction → Build → Verify**

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
- **Ideally a git repository.** Not required to install, but `add gate` establishes
  freshness from git blob hashes; outside a working tree it can only compare
  timestamps and will refuse to record a `PASS`. `git init` is enough.

> **Windows:** use `py` wherever this guide writes `python3` (the Python launcher on
> Windows) — e.g. `py .add\tooling\cli.py status`. Both installers handle the install
> step for you; only the by-hand commands in the appendix differ.

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

No flags needed — the tool infers your project's name from the folder. (Prefer to
choose up front? Both installers take `--name "My App"`.)

Either one creates `.add/` (your runtime) and drops the `add` skill into
`.claude/skills/add/`. The book itself is published at
https://pilotspace.github.io/ADD/ and never installs into the project. It deliberately
does **not** initialise the project — that's the agent's first move, so nothing
gets decided without you in the loop.

**When the install finishes: open Claude Code and type `/add`.** That's the
handoff — from here on it's conversation, not terminal commands.

### Updating to a newer ADD — no re-install

When a new ADD version ships, refresh a project in one step:

```bash
# npm — npx fetches latest, then re-materializes into this project:
npx @pilotspace/add@latest update

# pip — one shot via pipx (the npx analog):
pipx run pilotspace-add update

# …or plain pip, in two steps:
pip install -U pilotspace-add && pilotspace-add update
```

`update` clean-replaces the managed layer (`skill` · `.add/tooling`) and **never
touches your work** — `index.md`, `PROJECT.md`, milestones, tasks and archive are
left exactly as they were. It is idempotent (same version twice is a no-op).
Run `… update --check` to see whether a project is behind the installed package.

---

## 2 · Your first feature — talk to the agent

In Claude Code, the whole onboarding is one move:

```
in Claude Code:  /add
you:             "I want to let users transfer money between their own accounts."
```

From there the agent runs the **onboarding** for you:

1. **Orient** — it reads the bundle's resume point, never re-reading your whole
   repo. On a fresh install it initialises the project itself and drafts the
   foundation for your sign-off.
2. **Intake** — it sizes your request and proposes a **milestone** (goal · scope ·
   tasks · exit criteria). *You confirm the shape.*
3. **Direction** — for each task it drafts the RULES (Musts and Rejects), the PLAN
   (contract and scope), and the CHECKS that will prove them, then writes the tests
   **red first**. *You give one approval: the freeze.*
4. **Build → Verify** — it builds to green, records a receipt from a real test run,
   and gates on that evidence. A security finding always stops back to you.

So a milestone-sized feature is: **describe it → confirm the milestone → approve each
freeze → review the result.** Everything between is the agent.

> New term: **bundle** — the `.add/` tree that holds your project's state as plain
> markdown. See https://pilotspace.github.io/ADD/appendix-c-glossary/.

---

## 3 · What just happened (and your override)

Behind the conversation, the agent drove the CLI: it read the resume point, sized
the milestone, sealed the contract you approved, ran the tests red, built to green,
recorded a receipt, and gated on it. **The state lives on disk, not in the chat
window.**

If you ever want to see that state yourself — or take over entirely — the same
CLI is yours:

```bash
python3 .add/tooling/cli.py status
```

`status` is the resume point: the node roster, each node's beat, and the exact next
command. `brief <slug>` composes everything needed to work one task — its own body,
the cards of what it depends on, and the specs' bind lines — without reading your
whole repo. That is how **any agent** — Claude Code, Codex, OpenCode, Cursor,
Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline, Aider — follows ADD through the
CLI alone. The installer detects which one you're in and drops the file it reads
(`CLAUDE.md`, `AGENTS.md`, or `.clinerules`).

> Tip: shorten typing with an alias — `alias add="python3 .add/tooling/cli.py"` —
> then you can run `add status`, `add brief transfer`, etc. This guide uses the
> `add …` short form from here on.

---

## Resume next session

Close your laptop, come back tomorrow, type `/add` again — the agent reorients
itself from disk and continues exactly where you left off. The bundle is the
carrier; nothing depends on the conversation surviving.

The same resume point is yours directly:

```bash
add status
```

---

## Self-check

Confirm your bundle is internally consistent at any time:

```bash
add doctor
```

`doctor` **reports and never writes** — a checker that silently repairs is one whose
report you cannot trust, because you can't tell what it found from what it changed.
When you *want* the repair, ask for it explicitly with `add doctor --sync`.

---

## Under the hood — the three beats by hand (escape hatch)

Everything above is what the agent drives for you. This appendix is the **escape
hatch**: the same three beats run by hand, so you can see what each one produces and
step in manually whenever you want to. You never *have* to type these — they are the
agent's hands, and yours when you take the wheel.

### Before the beats — initialise and scaffold

Starting cold? Install first as in §1. Then initialise the bundle and scaffold the
task yourself (the agent normally does both):

```bash
add init --profile code "Ledger"
add new Task transfer --title "Transfer money between my accounts" --scope "src/,tests/"
```

This creates `.add/tasks/transfer.md` — **one file, eight sections** — and leaves it
at beat `direction`. Open it in your editor; you'll fill it top to bottom.

### Beat 1 — Direction (https://pilotspace.github.io/ADD/03-direction/)

Write the rules in **`## RULES`**. State what must hold (`M<n>`) and what must never
happen (`R:<NAME>`, each with a named error code):

```
<must>
- M1 an amount moves from one of my accounts to another of mine
- M2 the debit and the credit happen in one atomic transaction
</must>
<reject>
- R:AMOUNT_INVALID an amount <= 0 must never be accepted -> "amount_invalid"
- R:SAME_ACCOUNT source and destination must never be the same -> "same_account"
- R:OVERDRAW a balance must never go negative -> "insufficient_funds"
</reject>
```

Now the section people skip, and the one that earns its place fastest. **`## ASSUMPTIONS`**
is for what the request did **not** say:

```
- A1 [who] covers: S1 · the request never says whether I may transfer from an account
     I do not own; taking it as own-accounts-only -> if wrong, it moves other people's money
- A2 [which] covers: S1 · it never says whether closed accounts are transferable;
     excluding them -> if wrong, legitimate transfers are refused
- A3 [when] covers: S1 · it never says whether a transfer can be backdated; taking it as
     now-only -> if wrong, reconciliation breaks
- A4 [absent] covers: S1 · it never says what currency the amount is in; assuming one
     implicit currency -> if wrong, cross-currency transfers corrupt balances
- A5 [order] n/a · a single transfer exposes no ordered collection
- A6 [experience] covers: S1 · it never says who reads a refused transfer or what tells
     them why; taking it as the payer, who needs the reason and the fix in the refusal
     itself -> if wrong, a correct refusal reads as a fault and they retry until locked out
```

`A6` is the one dimension that is not about correctness. `A1` asks *whose* money it is;
`A6` asks who has to live with the answer. Note that its cost line does not describe a
bug — the refusal is right — and no other section has anywhere to record that.

RULES records what you were **told**. EDGES records the boundaries of those rules. Neither
has anywhere to put what nobody said — so without this section, an unstated requirement
becomes a Must phrased exactly like a stated one, and a reader cannot tell *given* from
*decided*.

**Sweep, don't free-associate.** The axis is the `S<n>` surfaces you list in the node's
`gives:` frontmatter (here `S1 POST /transfers`) — `new` scaffolds that slot and `freeze`
refuses while it is still template. Take each surface and ask all six dimensions —
`who · which · when · absent · order · experience` — tagging each line with the one it answers and the
surfaces it covers. `freeze` refuses until every `(dimension, surface)` pair is covered or
retired with `[<dim>] n/a · <why>`, and names the pairs it's waiting on:

```
cannot freeze `transfer` — these (dimension, surface) pairs are unswept: who:S1
```

`add todo` counts them down while you author, so freeze confirms work you've already done.

The matrix exists because free-association follows the *request's* emphasis, not the risk:
it's the dimension nobody wrote a sentence about that ships as a silent decision. (Working
at `--depth quick`? The sweep is skipped — depth tunes ceremony.)

An assumption is a declared unknown, not a rule: `A1` needs no check, and changing one
does not break the freeze seal.

Fix the external shape in **`## PLAN`**:

```
contract: POST /transfers { fromAccountId, toAccountId, amount }
          200 -> { transferId, fromBalance, toBalance }
          400 -> { error: "amount_invalid" | "same_account" | "insufficient_funds" }
scope: src/, tests/
```

Name any boundary case worth its own check in **`## EDGES`** (optional, but an edge you
write here is a rule the gate will hold you to):

```
- E1 a mid-transfer failure must leave both balances unchanged
```

Then bind every rule to the check that will prove it, in **`## CHECKS`**:

```
- test_transfer_moves_funds · covers: M1 · balances move by exactly the amount
- test_transfer_is_atomic · covers: M2, E1 · a mid-transfer failure leaves both balances unchanged
- test_rejects_non_positive · covers: R:AMOUNT_INVALID · zero and negatives are refused
- test_rejects_same_account · covers: R:SAME_ACCOUNT · source == destination is refused
- test_rejects_overdraw · covers: R:OVERDRAW · a balance never goes negative
```

Two things the gate will enforce later, so get them right now:

- **`covers:` takes a list.** One check can discharge several rules — `covers: M2, E1`
  above. What it cannot do is leave a rule unbound: **every** `M<n>`, `R:<NAME>` and
  `E<n>` needs some check naming it, or `gate PASS` refuses and tells you which.
- **The name must be the id your runner reports.** The gate matches on the id in the
  JUnit report, not on your intent. Parametrize `test_rejects_non_positive` in pytest and
  the report says `test_rejects_non_positive[0]` — which binds to nothing, and the gate
  refuses with `R:AMOUNT_INVALID` unbound. Keep one check per name, or declare the
  generated ids.

**Write those tests now, and confirm they FAIL.** There's no code yet; a test that
passes here is testing nothing. This is red/green TDD — red before green.

Now seal the direction:

```bash
add freeze transfer --by "your name"
```

Two things to know about `freeze`. It **refuses a node that still carries template
placeholders** — you cannot approve a scaffold. And it stamps a `direction:` digest
over RULES · CHECKS · `gives:`, so if any of them change afterwards, the gate will
refuse the PASS and tell you to refreeze. A frozen contract changes by refreezing,
never by a silent edit.

The authority the freeze is recorded at is **computed**, never asserted: it comes from
the node's `sensitivity:` and the bundle's `sensitive_paths:`. A `security` task needs
a human, whatever you pass.

### Beat 2 — Build (https://pilotspace.github.io/ADD/04-build/)

Now write code until **every test passes** — without changing a test or the frozen
contract. Then record a receipt from a real run:

```bash
add run transfer --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- python3 -m pytest -q --junitxml="${TMPDIR:-/tmp}/add-run.xml"
```

Note the flag appears **twice**, and that is not a typo: `--junitxml "${TMPDIR:-/tmp}/add-run.xml"` tells ADD
where to *read* the report, and `--junitxml="${TMPDIR:-/tmp}/add-run.xml"` after the `--` is part of the test
command that *writes* it. Omit the second and the receipt records only an exit code —
`ids: unknown` — and nothing binds to your rules.

`run` records what happened. A failing command is a recorded result, not an error.

### Beat 3 — Verify (https://pilotspace.github.io/ADD/05-verify/)

Check what tests miss — the three residue lenses: security, concurrency,
architecture. Then record exactly one outcome:

```bash
add gate transfer PASS --by "your name"
```

`gate PASS` auto-closes the task. It **refuses** unless there is a fresh receipt, the
receipt passed, the files in scope still digest to what was run, and every rule is
bound to a **passing** test id — naming the unbound ones when it refuses. A refusal
here is the method working, not a tooling error: it means the evidence does not yet
cover what you promised. Fix the binding, `run` again, gate again. (Changing RULES or
CHECKS to fix it breaks the direction seal, so refreeze first — that is deliberate,
and it is one command: `add freeze transfer --by "your name"`.) Use `gate HARD-STOP`
to send it back, or
`gate RISK-ACCEPTED --reason "…"` for a signed, non-security waiver. A security
finding is always `HARD-STOP` — that floor cannot be waived.

**What a green gate does and does not mean.** It proves the checks you *declared*
ran, passed, and are bound to your rules — never that those checks were *enough*. A
check that asserts nothing still binds and still passes. Writing the check that would
have caught the bug is your job; the engine can only prove you ran the ones you wrote.
See `FORMAT.md` §10.

### Closing the loop (https://pilotspace.github.io/ADD/06-the-loop/)

Record what you learned, so the next task starts better than this one did:

```bash
add learn tdd "atomicity needs a mid-transaction failure test, not just a happy path" \
    --evidence .add/tasks/transfer.md
add deltas                 # what the traces say across lanes
add todo                   # what is still open
```

The first argument is the **lens** — which of the five living specs this lesson
sharpens (`ddd · sdd · udd · tdd · add`). It is a closed vocabulary, not free text:
a lesson with nowhere to fold is a lesson nobody re-reads.

When every task in a milestone is done, `add milestone-done <slug>` checks the exit
criteria and refuses if the goal is unmet. The flow is a loop, not a finish line.

---

## Where to read more

You just ran the method; now read *why* it's shaped this way:

- The shift & principles — https://pilotspace.github.io/ADD/00-introduction/, https://pilotspace.github.io/ADD/01-principles/
- The flow end to end — https://pilotspace.github.io/ADD/02-the-flow/
- Each beat in depth — https://pilotspace.github.io/ADD/03-direction/, https://pilotspace.github.io/ADD/04-build/, https://pilotspace.github.io/ADD/05-verify/
- Setup and lanes — https://pilotspace.github.io/ADD/07-setup-and-lanes/
- Working in parallel — https://pilotspace.github.io/ADD/08-parallel-work/
- Operating it on a team — https://pilotspace.github.io/ADD/09-governance/, https://pilotspace.github.io/ADD/10-personas/
- Every verb and flag — https://pilotspace.github.io/ADD/13-command-reference/
- The bundle format — https://pilotspace.github.io/ADD/12-bundle-format/
- A fully worked example — https://pilotspace.github.io/ADD/appendix-d-worked-example/

The rule to remember: **build the right thing (direction), prove it's right
(verification), and let the AI do the building in between.**
