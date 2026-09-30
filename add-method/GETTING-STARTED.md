# Getting started with ADD — your first feature in ~10 minutes

This walkthrough takes one real feature — *transfer money between a user's own accounts*, the
book's worked example — from nothing to a **verified** result: one whose green is backed by
test output recorded at a known commit, not by a diff that reads plausible.

ADD has three beats:

> **Direction → Build → Verify**

ADD is **AI-first**: you talk to the agent and it drives the method. You will type exactly **one
shell command — the install**. After that it is conversation. There is no ADD command-line tool;
the agent's tools are files, git, and your project's own test command, and they are yours too.

---

## 0 · Prerequisites

- **One installer**, whichever you have: **Node.js ≥ 18** (for `npx`) *or* **Python 3.10+** (for pip).
- **A git repository.** The seal is a git commit: `git init` is enough.
- **A test command** your project already runs (`pytest`, `npm test`, `go test ./...`, …).
- **A coding agent** — Claude Code natively; Cursor, Codex, Copilot and others through their context file.

---

## 1 · Install — the one command you type

From your project root, pick **one**:

```bash
npx @pilotspace/add init                              # npm
```
```bash
pip install pilotspace-add && pilotspace-add init     # pip
```

The installer drops files only: the `add` skill into `.claude/skills/add/`, starter personas into
`.add/personas/`, and — for agents other than Claude Code — a short managed ADD block in their
context file. It does not create your project's bundle: that is the agent's first move, so nothing
is decided without your request in front of it.

**When it finishes: open Claude Code and type `/add`.**

To update later: `npx @pilotspace/add@latest update` or `pipx run pilotspace-add update`. Your
`.add/` project files are left exactly as they were.

---

## 2 · Your first feature — talk to the agent

```
in Claude Code:  /add
you:             "I want to let users transfer money between their own accounts."
```

The agent then:

1. **Orients** — reads `.add/PROJECT.md` and any open task files. On a fresh project it creates
   `PROJECT.md` — `goal:`, `invariants:`, `test_cmd:` — and empty `specs/`, `milestones/`, `tasks/`,
   drafting from your code if there is any.
2. **Sizes** the request. A mechanical edit or small behavior — ≤3 adjacent files, one sitting, no
   unknowns — goes **Quick**: a failing test, the fix, a commit, no task file. One behavior worth a
   contract becomes a **Task**. An open question becomes an **Explore** task that ends in cited
   findings. A theme becomes a **Milestone**. Anything touching security, data or architecture is
   at least a Task. *Moving money touches data, so this one is a Task.*
3. **Direction** — writes `.add/tasks/transfer-own-accounts.md`: the rules (what it must do and
   refuse), the assumptions (every gap in your request it had to fill, and what it would cost if
   wrong), the plan, and the checks. It runs the checks and watches them **fail** because the
   feature does not exist yet, then commits the task file and the checks together:
   `freeze(transfer-own-accounts): …`. That commit is the seal.
4. **Build** — writes code until the checks pass, without touching the sealed files.
5. **Verify** — confirms the sealed files are unchanged since the freeze commit, runs the checks and
   your full suite fresh, reads the diff for security, concurrency and architecture, tries to break
   its own green, and writes one verdict — `PASS`, `RISK-ACCEPTED` or `HARD-STOP` — with the real
   output into the task file's `## EVIDENCE`. Commit: `verify(transfer-own-accounts): PASS`.
6. **Reports** — any `HARD-STOP` first, then the verdict, the evidence, and **every assumption it
   took**.

Nothing stops for approval along the way. Your part is the review at the end.

---

## 3 · Review what it did

Read the report first — especially the assumptions. For the transfer, expect lines like:

```
A4 [who] the destination's owner is not mentioned → both accounts must be the caller's
   → if transfers to other users are wanted, R:FORBIDDEN is too strict
```

If a reading is wrong, say so; the fix is a new request, and the agent takes it from there.

Then check anything you like, with tools you already have:

```bash
git log --oneline --grep='(transfer-own-accounts)'       # freeze, any refreeze, verify
cat .add/tasks/transfer-own-accounts.md                  # rules, assumptions, checks, evidence
```

```bash
# was anything sealed changed after the seal?
F=$(git log -1 --format=%H --grep='freeze(transfer-own-accounts)')
git diff $F HEAD -- .add/tasks/transfer-own-accounts.md tests/     # the task's check files
```

The `## EVIDENCE` section names the exact commands and the commit they ran on — re-run them to see
the same result.

---

## 4 · Resume next session

State lives on disk, not in the chat. Close the laptop; tomorrow, type `/add` (or `/add status`)
and the agent reads `PROJECT.md`, the open task files and recent commits, and picks up where it
left off.

---

## Self-check

- [ ] `.add/PROJECT.md` states the goal, the invariants and the test command.
- [ ] The task file has rules, assumptions, checks and an `## EVIDENCE` block with a verdict.
- [ ] `git log` shows a `freeze(...)` commit before the code and a `verify(...)` commit after.
- [ ] You read every assumption, and agree — or you asked for a change.

---

## Where to read more

- The worked example, every command and output: https://pilotspace.github.io/ADD/appendix-d-worked-example/
- The loop, beat by beat: https://pilotspace.github.io/ADD/02-the-flow/
- The file format: https://pilotspace.github.io/ADD/12-bundle-format/
- Coming from 3.x: https://pilotspace.github.io/ADD/20-whats-new-in-4/
- The same loop where the artifact is a ledger: [BEYOND-CODE.md](./BEYOND-CODE.md)
