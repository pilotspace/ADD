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

## ADD in plain words

We gave Claude Code the same 300 real bugs from popular open-source projects twice: once on its own,
and once with ADD installed. Same AI, same bugs, same settings.

| | Claude Code on its own | Claude Code + ADD |
|---|---|---|
| 🐛 Bugs fixed | 215 of 300 | **226 of 300** |
| ✅ Ran the tests and saw them pass before saying "done" | 53 of 300 | **274 of 300** |
| 🧪 The fix came with its own test | 17 of 300 | **299 of 300** |
| 📝 Wrote down its guess where the request was silent ("who may cancel a booking?") | 0 of 3 | **3 of 3** |
| 💰 Price and time per bug | about 9¢ · 32 s | about 16¢ · 80 s (1.8× the money, 2.5× the time) |

**In short:** ADD fixes at least as many bugs, checks and tests almost every fix, and tells you what
it assumed. It costs more, and the gain in bugs fixed is small enough that it is not yet proven. Run
it with `--effort medium`. **[See the results animated, in plain words →](https://pilotspace.github.io/ADD/add-results.html)**

## ✨ Highlights

- 📜 **Every change leaves its reasoning in your repo** — the rules, the guesses and the checks live in one task file next to the code, so the next session or teammate reads the intent instead of guessing it.
- 🛡️ **Safer guesses where your spec is silent** — ADD takes the least-privilege reading when nobody said *who* may act, and seals a check for it.
- 🔒 **Trust rests on evidence, not a plausible diff** — checks are sealed in a `freeze` commit before the build, and every task ends in a verdict you can re-run. Security findings always lead the report.
- ⚖️ **An honest price** — Measured on ADD 4.1.0 with Claude Sonnet 5.5 (n = 300 real bugs, both at `--effort medium`): ADD resolved 226 to vanilla Claude Code's 215, at 1.8× the dollars and 2.5× the seconds per bug. On small apps it costs 1.3–1.9× the dollars and 1.8–2.4× the minutes; correctness ties, and its tests catch more seeded bugs (0.81 vs 0.43) ([results](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md)).
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
| 🧪 **Tests that run, and stay** | ADD runs your repo's own tests and ships its new ones with the change | on all 300 SWE-bench Lite issues ADD saw a passing test run before shipping in 274 of 300 and shipped a test with 299 of 300; vanilla did in 53 of 300 and 17 of 300. ADD's tests also catch more seeded bugs (0.81 vs 0.43, rounds 8–9 pooled) |
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

The same Claude Code with and without the ADD skill, on `claude-sonnet-5-5` (Sonnet 5.5): two small
apps at n = 3 per arm, and all 300 SWE-bench Lite issues once per arm ([results](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md) ·
[both flows, animated](https://pilotspace.github.io/ADD/add-vs-vanilla.html) ·
[the earlier rounds, animated](https://pilotspace.github.io/ADD/add-value.html)).

| what you get | vanilla Claude Code | Claude Code + ADD |
|---|---|---|
| **Fixes that land** — SWE-bench Lite, all 300 issues resolved (both at medium) | 215 of 300 | **226 of 300** (p = 0.099) |
| **Verified before it ships** — a passing test run seen (SWE, 300 issues) | 53 of 300 | **274 of 300** |
| **Ships with a test** — the fix carries its own test (SWE, 300 issues) | 17 of 300 | **299 of 300** |
| **Tests that catch bugs** — seeded bugs its own tests catch (wm1 · amb1, rounds 8–9 pooled) | 0.78 · 0.43 | 0.86 · **0.81** |
| **Guesses you can review** — "who may cancel?" read as owner-only and written down (amb1) | 0 of 3 | **3 of 3** |
| **Ambiguities handled right** — of 7 planted (amb1) | 5.0 | 5.3 |
| **Claims you can trust** — claimed test count = a fresh rerun | no claim made | **every parsed claim** |
| **Correct on small apps** — requirement oracle · held-out edge cases (wm1) | 1.00 · 22 of 22 | 1.00 · 22 of 22, a tie |
| **you pay:** SWE dollars · seconds per issue (both at medium) | $0.089 · 32 s | $0.162 · 80 s, **1.8× · 2.5×** |
| **you pay:** small apps, dollars per run (wm1 · amb1; ADD at low) | $0.21 · $0.17 | $0.28 · $0.32, **1.3× · 1.9×** |
| **you pay:** small apps, minutes per run (wm1 · amb1; ADD at low) | 0.9 · 0.7 min | 1.6 · 1.7 min, **1.8× · 2.4×** |

**Effort matters.** At `--effort low` ADD read its skill in only half its runs and resolved 201 of 300 to vanilla's 215.
At medium it read the skill in 292 of 300 and resolved 226. In a blind six-issue review, one reviewer preferred vanilla's shorter output in 6 of 6, while 2 of the 5 vanilla patches
they approved as is fail the benchmark's tests; timed review is not measured ([fresh 300 at medium](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md)).

**What changed after the measurement.** The 300-issue numbers were measured while Quick required a test on every fix.
The shipped 4.1.0 skill makes a small change directly and writes a new test only when it is important (a plausible wrong fix
would pass every existing check); the rest is proven by running the repro and the suite. That change is not re-measured:
expect fewer shipped tests than 299 of 300, and an unknown effect on the fix rate.

Earlier rounds, older models and the full method are in [the results history](./benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md).

<sub>**Fine print:** both arms ran with the operator's own `~/.claude` kept out of the session; earlier rounds loaded it, and its `security-guidance` plugin slowed every ADD commit. Run ADD at `--effort medium`: at `--effort low` it skipped its own skill in half the SWE runs and resolved 25 fewer issues. The small apps are n = 3: direction, not proof.</sub>

## When vanilla Claude is the right call

- **Throwaway work** (a script, a spike, a one-shot), or a fix you will not review: use vanilla. It
  runs about 2.5× faster at about half the price, and on SWE-bench Lite it resolved 215 of 300 to ADD's 226.
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
