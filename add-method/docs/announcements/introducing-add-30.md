<!-- meta: The v3.0.0 launch post — published with the final tag. Written and test-bound at beta.2: tests/book/test_launch_blog.py pins every measured claim to the committed campaign record. Served copy: docs/announcements/ (byte-identical, guarded). -->

# ADD 3.0: A Dev Method Your AI Agent Can't Talk Its Way Around

Here is the uncomfortable truth about building software with AI agents in 2026: the code arrives faster than your ability to check it. The agent says the tests pass. The diff looks right. And somewhere in that green wall of confidence there may be a test asserting `True`, a requirement that quietly became a guess, or a suite that never actually ran.

Most teams respond with process — review checklists, prompting guidelines, PR templates. We tried that too. Then we measured it, three separate times, and got the same result every time: **rules written as prose get routed around. Rules enforced by a tool hold.** Agents don't disobey your guidelines maliciously; they optimize past them. The only instructions that survived contact with a working agent were the ones a program refused to proceed without.

ADD 3.0 is that finding, turned into a method.

## What ADD is

ADD (AI-Driven Development) is a lightweight method for working with AI coding agents without losing track of what's true. It has three beats:

> **Direction → Build → Verify**

You describe a feature in conversation. The agent drafts the rules, the contract, and a set of failing tests. You approve that direction **once** — the *freeze*, which seals what was agreed under a cryptographic digest. The agent builds until the tests pass and records a *receipt* from a real run. A *gate* checks the receipt against the frozen rules and records one outcome.

Everything lives in plain markdown files under `.add/` in your repo — readable, diffable, greppable. There is no server, no database, no dashboard. The engine is two Python files, vendored into your project, and it follows one law: **it is a notary, not a guard.** It never runs your code on its own initiative and never writes your rules for you. It records what happened — and refuses to record what didn't.

## What "refuses" means in practice

Every guarantee in 3.0 is a refusal you can trigger yourself, today:

- **You can't approve a template.** `add freeze` refuses a task whose sections are unfilled scaffolding, and names exactly what's missing.
- **You can't skip the awkward questions.** Every surface your task publishes gets swept across five ambiguity dimensions — *who · which · when · absent · order*. The freeze refuses until each one is answered or explicitly retired. What the request didn't say gets written down as a priced assumption — in a section you read before approving — instead of shipping silently as a decision wearing a requirement's voice.
- **You can't pass without evidence.** The gate refuses a `PASS` with no receipt, a failed receipt, a stale receipt (it re-hashes every in-scope file), or a receipt where any frozen rule lacks a passing test behind it.
- **You can't build against instructions nobody compiled.** New in the latest engine: `add brief` records the moment the sealed direction became the working prompt, and the gate refuses evidence that predates it. Briefing *after* the build proves nothing, and the stamp order is append-only chronology.
- **You can't quietly edit the agreement.** Change a frozen rule after the freeze and the seal no longer verifies — the gate refuses the pass and points you at an explicit re-freeze, on the record.
- **Security never gets waved through.** A security finding is a hard stop with a required human floor, computed from the task itself — never from whoever happens to be typing.

We know these hold because we attacked them ourselves. Before this release we spent a sustained effort trying to cheat our own method — tampering with frozen rules, hunting for bypass verbs, gating without evidence. Our previous release, ADD 2.5, failed that audit on the first try: it recorded a green `PASS` on a failing suite. 3.0 refused every attack we threw at it. The full transcript — real terminal output, including the parts that embarrassed us — is in [the companion post](./2026-08-11-we-tried-to-cheat-our-own-dev-method.md).

## The numbers, exactly as measured

We benchmark ADD against a planted-ambiguity suite: a realistic feature request with seven deliberately unspecified decisions, driven end-to-end by an agent, then scored on what surfaced versus what shipped as a silent guess. The current record: **n=3 independent runs, all on the same release engine, no version pooling.**

- **Safe outcomes: 5 of the 7 planted ambiguities in every rep** — zero spread across all three runs. "Safe" means the agent either surfaced the question to a human or happened to guess right; the campaign record lists every item and verdict.
- **Requirement coverage 1.0, functional oracle 1.0, regressions 0** — in all three reps.
- **Cost: $3.00 mean per full run** in agent time. Honest rigor costs real money; we think a wrong who-can-see-whose-data decision reaching production costs more.

And the two failures are on the record too: the same two ambiguities were resolved *wrong* in all three reps — stable misses, not noise. That stability is why the newest engine lets you mark any recorded assumption with a `probe:`, which binds it to the test suite exactly like a rule: shipped behavior must demonstrate the reading, or the gate holds the pass.

## What ADD 3.0 does not claim

**ADD makes agents ask the right questions; it cannot make them give the right answers.** No artifact checker can. What the method guarantees is *auditability*: every guess is on the record, tagged with its cost, at the exact moment a human is already reviewing — where a veto takes ten seconds. That's the whole claim: **auditability, not correctness.** We've written it into the release notes rather than around them, and the benchmark that produced the numbers above ships in the repo, re-runnable by anyone.

## Try it in ten minutes

```bash
# from your project root — either installer, same result:
npx @pilotspace/add init
# or:
pip install pilotspace-add && pilotspace-add init
```

Open Claude Code (or any agent — the whole method drives through one CLI), type `/add`, and describe a feature. Watch the loop: proposal → your one freeze approval → red tests → build → receipt → gate. Check the state anytime with `add status`; see what's open with `add todo`. Coming from ADD 2.x? `add upgrade` archives your old bundle whole — byte-identical, nothing deleted — and starts a fresh 3.0 bundle beside it.

Then, before you trust us with anything real, run the audit yourself: freeze a task, edit a frozen rule, and try to gate it. Watch the refusal name exactly what you did.

---

*ADD 3.0.0 · Direction → Build → Verify · [pilotspace.github.io/ADD](https://pilotspace.github.io/ADD/) · evidence trail: [We Tried to Cheat Our Own Dev Method](./2026-08-11-we-tried-to-cheat-our-own-dev-method.md)*
