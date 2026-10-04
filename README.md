<p align="center">
  <img src="add-banner.jpg" alt="ADD — AI-Driven Development" width="100%">
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@pilotspace/add"><img alt="npm version" src="https://img.shields.io/npm/v/@pilotspace/add.svg"></a>
  <a href="https://pypi.org/project/pilotspace-add/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/pilotspace-add.svg"></a>
  <a href="https://github.com/pilotspace/ADD/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://pilotspace.github.io/ADD/"><img alt="Read the book" src="https://img.shields.io/badge/docs-read%20the%20book-blue.svg"></a>
  <a href="https://github.com/pilotspace/ADD/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/pilotspace/ADD.svg"></a>
</p>

<h1 align="center">ADD — AI-Driven Development</h1>
<p align="center"><strong>Your AI's first milestone is always great. ADD is for every milestone after that.</strong></p>
<p align="center">Describe the feature. The agent plans, seals, builds and verifies it — and hands you a report of every decision it made, backed by evidence you can re-run.</p>

---

## ✨ Highlights

- 📜 **Every change leaves its reasoning in your repo** — the rules, the guesses and the checks live in one task file next to the code, so the next session or teammate reads the intent instead of guessing it.
- 🛡️ **Safer guesses where your spec is silent** — ADD takes the least-privilege reading when nobody said *who* may act, and seals a check for it.
- 🔒 **Trust rests on evidence, not a plausible diff** — checks are sealed in a `freeze` commit before the build, and every task ends in a verdict you can re-run. Security findings always lead the report.
- ⚖️ **An honest price** — Measured on ADD 4.0.0 with Claude Sonnet 5.5 at `--effort low` against vanilla Claude Code at medium, n = 3 per arm per workload: 1.3–1.9× the dollars and 1.8–2.4× the minutes. Correctness ties; ADD's own tests catch more seeded bugs on an ambiguous spec (0.81 vs 0.43, rounds 8–9 pooled), and on 30 SWE-bench Lite issues it resolved 23 to vanilla's 21 ([results](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md)).
- 💸 **Ceremony only where it buys trust** — most changes take the Quick lane: one red→green test, one commit, no task file.

## What ADD gives your project

Vanilla Claude Code already writes good code: on Sonnet 5.5 it passed every held-out edge case in
our benchmark. What it does not leave behind is the *why*. ADD 4.0 is one skill file, with no
engine and no CLI, that makes every change leave the reasoning in your repository, next to the code:

| | What your project keeps | Why it pays off later |
|---|---|---|
| 📜 **A contract per change** | `.add/tasks/<slug>.md`: the rules, the guesses, and the checks that prove them | the next session, or the next teammate, reads the intent instead of reverse-engineering it from code |
| 🙋 **Every guess on the record** | each silence in your request becomes an ASSUMPTION: the reading taken and the cost if wrong, costliest first | you review a short list of decisions, not a diff; a wrong guess is one line to correct |
| 🛡️ **Safer readings of silence** | when nobody said *who* may do something, ADD takes the least-privilege reading and seals a check for it | the booking benchmark never said who may cancel: vanilla let anyone in 8 of 8 runs; ADD chose owner-only in 3 of 3 on Sonnet 5.5 |
| 🔒 **Checks sealed before the code** | the failing checks are committed as `freeze(<slug>)` before any build | a test weakened to get green shows up in `git diff`; a change of intent is a visible `refreeze` commit |
| 🧪 **Tests that run, and stay** | ADD runs your repo's own tests and ships its new ones with the change | on 30 SWE-bench Lite issues ADD ran the repo's tests in 30 of 30 runs and shipped tests in 30 of 30 patches; vanilla ran them in 7 of 30 and shipped tests in 2 of 30. ADD's tests also catch more seeded bugs (0.81 vs 0.43, rounds 8–9 pooled) |
| 🔬 **Evidence you can re-run** | a verdict (`PASS`, `RISK-ACCEPTED` or `HARD-STOP`) with the exact commands and counts, committed as `verify(<slug>)` | the claimed test count matched a fresh rerun in 33 of 33 benchmark runs; security findings always lead the report |
| 🧠 **Memory that outlives the chat** | state lives on disk, not in the conversation | over six evolving milestones, one long chat's requirement coverage fell .92 → .75, while fresh sessions resuming from disk held 1.0 ([report](./benchmark/results/2026-07-add-2.0-remeasure.md)) |

## Vanilla Claude vs Claude + ADD — the same request, two flows

Two real round-6 runs on Sonnet 5.5, given the same spec: a booking service whose requirements
contradict each other (a conflict gets `202` waitlisted *and* `409` rejected) and say nothing on six
other decisions. ▶ **[Watch both play on one clock](https://pilotspace.github.io/ADD/add-vs-vanilla.html)**.

| clock | 🏃 **vanilla Claude Code** (`vanilla-amb/rep1`) | 🛡️ **Claude Code + ADD** (`add-4-amb/rep1`) |
|---|---|---|
| 0 s | reads the repo | orients from `.add/PROJECT.md` |
| 31 s | writes `app/` and 7 tests in one command | … |
| 46 s | tests pass, smoke run OK: **done, $0.28** | … |
| 56–94 s | | **Direction:** writes `.add/tasks/booking-waitlist.md` with 17 rules, 8 ASSUMPTIONS and 19 checks, plus the tests |
| 97 s | | runs the 19 checks red and seals them: `freeze(booking-waitlist)` |
| 110–138 s | | **Build:** code until all 19 pass, sealed files untouched, then a build commit |
| 154–186 s | | **Verify:** a live probe with `curl`, a fresh run (19 OK) and an empty seal diff, then `verify(booking-waitlist): PASS` |
| 195 s | | **done, $0.63** |
| **the contradiction** | caught it and chose waitlist-by-default with a `"waitlist": false` opt-out, **in its chat reply** | caught it and made the same choice, **as ASSUMPTION A1 in the task file**, first in the report as the costliest guess |
| **who may cancel a booking?** | anyone | the owner only (rule `R:OWNER`, sealed check C11) |
| **left in your repo** | the code and its tests | the code, the checks, the contract and the evidence, as three commits |

Same code quality, same headline decision. The difference is where that decision lives, and the
guesses nobody asked about.

## Measured on 4.0 — what you get, what you pay

The same Claude Code with and without the ADD skill, on `claude-sonnet-5-5` (Sonnet 5.5), n = 3 per
arm per workload ([results](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md) ·
[both flows, animated](https://pilotspace.github.io/ADD/add-vs-vanilla.html) ·
[the earlier rounds, animated](https://pilotspace.github.io/ADD/add-value.html)).

| on Sonnet 5.5 (wm1 · amb1) | vanilla Claude Code · effort medium | + ADD 4.0 · effort low |
|---|---|---|
| **you pay:** dollars per run | $0.21 · $0.17 | $0.28 · $0.32, **1.3× · 1.9×** |
| **you pay:** minutes per run | 0.9 · 0.7 min | 1.6 · 1.7 min, **1.8× · 2.4×** |
| requirement oracle | 1.00 · 1.00 | 1.00 · 1.00, a tie |
| held-out edge cases passed (wm1) | 22 of 22 | 22 of 22, a tie |
| seeded bugs its own tests catch (mutation, rounds 8–9 pooled) | 0.78 · 0.43 | 0.86 · **0.81** |
| planted ambiguities handled right, of 7 (amb1) | 5.0 | 5.3 |
| "who may cancel?" read as owner-only (amb1) | 0 of 3 | **3 of 3** |
| SWE-bench Lite, 30 issues resolved | 21 | **23** (all of vanilla's, plus 2) |
| claimed test count = a fresh rerun | no claim made | **every parsed claim** |

On the older Sonnet 5 (rounds 4–5), ADD's own tests caught more seeded bugs (0.68 vs 0.51 and 0.79
vs 0.53) and vanilla shipped no tests in 2 of 5 runs, at 2.2–2.9× the dollars. Sonnet 5.5 closed
those gaps on these workloads, and ADD's cost fell from $1.67 to $0.52 a run.

<sub>**Fine print:** both arms ran with the operator's `~/.claude` kept out of the session (`--setting-sources project,local`). Earlier rounds loaded it: its `security-guidance` plugin reviewed every `git commit`, so ADD's commits paid 100–185 s each, and that is where the old 4–5× minutes came from. Run ADD at `--effort low`; it costs about a fifth less than medium with no measured quality loss. Both small workloads saturate at Sonnet 5.5, and n = 3 is direction, not proof.</sub>

## When vanilla Claude is the right call

- **Throwaway work** (a script, a spike, a one-shot): use vanilla. It runs 4–5× faster at about
  half the price, and on a strong model the code is as good.
- **A product you will still be changing next month** (several milestones, teammates, or anything
  where *who may do this?* matters): use ADD. The decisions outlive the chat, the guesses get
  reviewed, and the checks cannot quietly weaken.
- **In between**, ADD sizes each request itself. Most changes take the Quick lane, which is one
  red→green test and one commit, with no task file.

ADD works with the agent you already use (Claude Code, Codex, Cursor, Copilot, Gemini) and installs
via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from evidence you can re-run, not from reading code and finding it plausible._

---

## 🚀 Get Started

**Prerequisites:** Node ≥ 18 *(npm path)* or Python ≥ 3.10 *(pip path)*, a git repository, and a coding agent.

### 1 · Install into your project

```bash
npx @pilotspace/add init      # Node / npm
```
```bash
pip install pilotspace-add && pilotspace-add init      # Python / pip
```
```text
# Claude Code plugin — no npm or pip needed
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

> See a real one: this repo's own [`.add/`](https://github.com/pilotspace/ADD/tree/main/.add) folder.

### 2 · Describe your first feature

In Claude Code, run **`/add`** and say what you want to build:

```bash
/add 'Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out.'
```

The agent:

1. 🧭 **Orients** from `.add/PROJECT.md` and the open task files — never re-reading your whole repo.
2. 📐 **Sizes** the request: Quick, Task, Explore or Milestone.
3. ✍️ **Writes the direction** — rules, assumptions and failing checks — and seals them in a `freeze` commit.
4. ✅ **Builds and verifies** to a written verdict, then reports; a security finding always goes to the top.

### 3 · Resume anytime

```markdown
/add status | continue
```

State lives on disk, not in the chat.

---

## ⚙️ How ADD Works

**One task · three beats · one file.** Every change worth a contract is one task file at
**`.add/tasks/<slug>.md`**. **Direction** writes its rules, assumptions and checks, runs the
checks red, and seals them with a `freeze(<slug>)` commit. **Build** turns them green without
touching the sealed files. **Verify** proves the seal is intact, runs everything fresh, reads
what tests cannot show, tries to break the green, and writes one verdict — `PASS`,
`RISK-ACCEPTED`, or `HARD-STOP` — committed as `verify(<slug>)`. The decisions are what you keep;
the code is disposable.

![Foundation Domain Documents](add-foundation.png)

**Tasks compound into milestones; milestones grow the project.** A milestone lists its tasks up
front, runs each just in time, and is done only when every exit criterion carries its evidence.

---

## 📚 Learn More

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full method, chapter by chapter
- 🆕 [What changed in 4.0](https://pilotspace.github.io/ADD/20-whats-new-in-4/) — the engine removed, and why
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/)
- ⚡ [Getting Started](./GETTING-STARTED.md) · 🔍 [Full walkthrough](./add-method/GETTING-STARTED.md)
- 📒 [Beyond code — a month-end close, end to end](./add-method/BEYOND-CODE.md)
- 📊 [Benchmark results](./benchmark/) — every trust and cost claim, reproducible from this repo
- 📦 [Package source](./add-method/README.md) · [Changelog](./add-method/CHANGELOG.md)
- 🗞️ [ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)

**Releases:** [`@pilotspace/add`](https://www.npmjs.com/package/@pilotspace/add) (npm) · [`pilotspace-add`](https://pypi.org/project/pilotspace-add/) (PyPI)

---

## Star History

<a href="https://www.star-history.com/?repos=pilotspace%2FADD&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&legend=top-left" />
 </picture>
</a>

---

<p align="center">MIT License · <a href="https://github.com/pilotspace/ADD">pilotspace/ADD</a></p>
