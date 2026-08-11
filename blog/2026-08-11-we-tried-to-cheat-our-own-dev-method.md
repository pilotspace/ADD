<!-- meta: We tampered, bypassed, and benchmarked ADD 2.5 vs 3.0. Real refusals, real receipts, real numbers — and what ADD 3.0 deliberately does not claim. -->

# We Tried to Cheat Our Own Dev Method. ADD 3.0 Refused — With Receipts

There's a moment every team using AI coding agents eventually hits. The agent says the tests pass. The diff looks plausible. You merge. And three days later you find out the "passing" test was asserting `True`, or the suite never ran, or the one rule that mattered was quietly rewritten the night before.

We hit that moment on purpose. While preparing ADD 3.0, we took our own previous release — ADD 2.5 — and tried to make it lie. It did, on the first try: **2.5 recorded a `PASS` on a task whose test suite was failing.** No warning. Exit code 0.

Then we ran the same attacks against 3.0. This post is what happened — the actual terminal output, the actual artifacts, the numbers we're proud of, and the two we aren't. By the end you'll know exactly what ADD 3.0 guarantees, what it deliberately doesn't, and how to verify every claim yourself.

## What ADD is, in sixty seconds

ADD (AI-Driven Development) is a method for building software with AI agents without losing the thing that matters: **knowing what's true**. It has three beats:

> **Direction → Build → Verify**

You describe a feature in conversation (`/add` in Claude Code — or any agent, via one CLI). The agent drafts the rules, the contract, and the tests; you approve once (the *freeze*); it builds to green and records a *receipt* from a real test run; a *gate* checks the receipt against the frozen rules. All state lives in plain markdown files under `.add/` — no database, no lock-in. If you can edit a text file, you can drive the whole method by hand.

That much was true in 2.5 as well. What changed in 3.0 is one hard-won principle.

## The law 3.0 is built on

While benchmarking 3.0, we ran a planted-ambiguity experiment three times, patching the method between runs. Every single time, the same pattern appeared:

**Rules written as prose get routed around. Rules enforced by the engine hold.**

- We *asked* agents (in the docs) to enumerate every API surface. They didn't — until `freeze` refused otherwise.
- We *asked* for one assumption per line. They bundled three into one — until the scaffold made splitting the default.
- We *asked* for one surface per ID. One run collapsed five endpoints into one — until the engine started refusing that too.

Three interventions, three evasions, three checkpoints — and every checkpoint held. That's not a slogan; it's the empirical result that decided 3.0's design. 2.5 was built mostly from prose rules. 3.0 is built from refusals.

## Same feature, both versions — the actual artifacts

We planned the identical feature — *transfer money between a user's own accounts* — in both versions, clean-room installs, driven to a successful freeze in each.

**ADD 2.5** scaffolds a 126-line, 8.6 KB `PLAN.md`: seven numbered sections, ~30 embedded HTML-comment instructions, checkboxes for verification, a slot for your riskiest assumption, an autonomy dial defaulting to `auto`. It reads like a thorough questionnaire.

Here's the uncomfortable part: **almost none of it is checked.** We grepped the shipped 2.5 engine — the `<assumptions>` block is read by *zero* lines of code. The eight verify checkboxes: never read. The refute-read verdict: never read. And 2.5 froze our plan — crossing straight into build — with **zero red tests on disk**.

**ADD 3.0** scaffolds a 51-line, 1.6 KB node. Authored, it came to 3.5 KB against 2.5's 9.1 KB — and every section is load-bearing. Trying to freeze it early produced this:

```
cannot freeze `transfer` — the node still carries template placeholders: …
cannot freeze `transfer` — `gives:` is unauthored, so there are no surfaces to sweep
cannot freeze `transfer` — one surface per S id: S1 …
cannot freeze `transfer` — these (dimension, surface) pairs are unswept: who:S2 · which:S2 · …
```

Four different refusals, each naming exactly what's missing and what to do next. When it finally froze, the freeze wrote a cryptographic seal:

```yaml
verified:
  - { by: "tin", at: 2026-08-11, act: freeze, authority: human, direction: "sha256:8034caf4323539bb" }
```

Keep that hash in mind. It's about to matter.

## Five attacks, five results

**1. Evidence.** 2.5's `gate PASS` takes no receipt and executes nothing — that's how it passed a failing suite. 3.0's gate refuses in layers: no receipt → failed receipt → unbound rules → drift → stale receipt. A 3.0 receipt records the exit code, the passing test IDs, and the git blob hash of every in-scope file at run time.

**2. The bypass hunt.** 2.5 ships `add.py phase verify <slug>` — an unconditional override that its own refusal messages *advertise*. We used it to gate a never-frozen task to PASS. 3.0 has no phase verb at all — your position in the loop is derived from stamps, so there's no marker to lie with. We looked for a bypass. We didn't find one.

**3. Security.** 2.5 closed a security-sensitive task with a signed waiver (`--owner --ticket --expires`). 3.0 refuses categorically: security is always a hard stop, the authority floor is computed from the task's declared sensitivity and its file paths — never from whoever happens to be typing — and a security PASS requires a named reviewer lens on record.

**4. The tamper test.** After freezing in both versions, we gutted a frozen rule — `M1 a transfer moves the amount…atomically` became `M1 anything goes`.

- 2.5's checker: **`9 passed, 0 failed`.** The edit was invisible.
- 3.0: `sealed sha256:8034… ≠ now sha256:1e17…` → **the gate refuses the PASS** and points you at re-freeze or reopen.

**5. Cost.** All of that enforcement comes with *less* overhead, not more: generated state 48.6 KB → 4.5 KB (10.7×), session resume read-set 12.3 KB across 3 files → 2.9 KB in one node, the vendored engine 16 files → 2, verbs 34 → 20 (21 as of beta.2, which adds `upgrade`). And a second, independent conformance checker ships in the box and agrees with the engine on every bundle we've driven.

## The feature we're most proud of: silences on the record

The most dangerous line in any AI-built feature isn't a wrong answer — it's an **unasked question** stated as fact. In our benchmark, every 2.5-era run did this: the spec never said *whose* bookings a list endpoint returns, and every run silently decided "everyone's" and wrote it in the same confident voice as a real requirement. Nothing in the artifact distinguished *told* from *decided*.

3.0 gives that its own enforced section. Every surface your task publishes is swept across five dimensions — *who · which · when · absent · order* — and `freeze` refuses until each pair is covered or explicitly retired. The scaffold even frames the register for you. Here's a line from a real benchmark run, verbatim:

```
- A1 [who] covers: S1,S2,S3,S4,S5 · the request does not say whether Authorization
  restricts who may read/cancel a booking; taking "no ownership check — any caller
  may read or cancel any booking" -> cost if wrong: no per-tenant isolation
```

Read that carefully. The agent's chosen reading is *wrong* — and that's the point. Six runs earlier this decision was invisible. Now it's declared, priced, and sitting in the one document you approve at freeze, where you can veto it in ten seconds. `add todo` counts the remaining pairs down as you author, so the gate confirms work you've done instead of ambushing you.

## What ADD 3.0 does *not* claim

Here's the part most product posts skip, and the reason you should trust the rest of this one.

Across every benchmark run, on two of the seven planted ambiguities, the agent chose the wrong reading — before *and* after all our improvements. **3.0 makes agents ask the right questions; it cannot make them give the right answers.** No artifact checker can. What it guarantees is *auditability*: the guess is on the record, tagged with its cost, at the exact moment a human is already reviewing. That's the whole claim of the 3.0 beta, and we've written it into the release notes rather than around them.

We also measured the price of rigor honestly: a fully-swept run cost $3.46 in agent time versus $1.82 for a run that dodged the ceremony. Honesty costs about 35–90% more than its evasions. We think a wrong `who-can-cancel-a-booking` decision reaching production costs more.

## Found by fire

Two more findings, because a method that audits itself should show its own scars. During this comparison we found a parser bug in 3.0: a bare apostrophe (as in *"the caller's own transfer history"*) silently swallowed the freeze stamps — the tamper seal stopped verifying, with the full test suite green. Found by driving the artifacts, fixed the same day with failing-tests-first, and pinned so it can't return. Earlier, benchmark validation caught that 3.0 had shipped *without* the contract tripwire 2.5 had — a real regression, also fixed before this beta. Every claim in this post survived the same adversarial process that produced those fixes.

## Try it in ten minutes

```bash
# from your project root — either installer, same result:
npx @pilotspace/add init
# or:
pip install pilotspace-add && pilotspace-add init
```

Then open Claude Code and type `/add`, describe a feature, and watch the loop run: milestone proposal → your one freeze approval → red tests → build → receipt → gate. When you want to see the state yourself: `python3 .add/tooling/cli.py status`. Everything is markdown in `.add/` — read it, diff it, grep it.

And run our tamper test on your own bundle: freeze a task, edit a frozen rule, try to gate. Watch it refuse.

## What we said would ship next — and what beta.2 shipped

This post originally closed with a seven-item roadmap. One day later, **3.0.0-beta.2** converted five of those items from prose into engine refusals — each one red-tests-first, 48 new tests total. Since the whole post is about the difference between a promise and a checkpoint, here is that list graded against itself:

- **The XML brief as a checkpoint — SHIPPED.** `add brief` on a frozen task now records an `act: brief` stamp, and the gate refuses a `PASS` whose receipts predate it. Verbatim, from a live bundle:

  ```
  cannot record `PASS` — no brief entered this build — the sealed direction
  was never compiled into the working prompt since the last (re)freeze
  -> "R:UNBRIEFED"
  next: add brief transfer to record the entry, then re-run
  ```

  Briefing *after* the build buys nothing — the entry must precede the evidence, and stamp order is append-only chronology. The checkpoint law, applied to the thing that taught it to us.
- **Answer correctness via gate probes — SHIPPED.** Mark an assumption `· probe: <what shipped behavior must show>` and its `A` id binds exactly like a rule: some check must cite it and report passing, or the gate holds the PASS. Opt-in on purpose — the engine enforces exactly what you declared checkable, and an unmarked line stays what it always was: a priced guess on the record.
- **Broader surface detection — SHIPPED.** "One surface per ID" now also refuses two distinct `name()` callables or two backticked documents hiding under one id. Prose mentions are still never judged — a notary that guesses at prose shape becomes a guard.
- **Persona routing metadata — SHIPPED.** The generated 232-lens routing index gains a freshness check: `doctor` warns when the vendored corpus and the index disagree, so a stale roster can no longer misroute silently.
- **A guided 2.x upgrade — SHIPPED.** `add upgrade` renames your 2.x bundle whole into `.add-2x-archive/` (byte-identical, nothing deleted), initialises 3.0 beside it, and leaves a `MIGRATION.md` that walks the re-authoring. 2.x state is deliberately *not* translated — its phase markers and waivers mean things 3.0 refuses to mean.
- **More measurement, published — tooling SHIPPED, runs still a spend decision.** `benchmark/campaign.py` now aggregates repetition sets into a committed, reproducible record; `CAMPAIGN-amb1.md` is in the repo, per-item verdicts included (`A-list-scope`: wrong 7 runs out of 7 — on the record), with its heterogeneous-engines caveat printed in-band. Funding a homogeneous n≥3 set on the beta.2 engine remains open.
- **3.0.0 final — open by design.** The beta hardens through live use; the tag follows.

The bet behind all of it stays the same: **every guarantee becomes a refusal, every refusal gets a test, and every claim gets measured before it's published** — including the ones that come back embarrassing. And the release claim has not moved an inch: beta.2 makes more of the record enforceable; it still promises **auditability, not correctness**.

---

*ADD 3.0.0-beta.2 · Direction → Build → Verify · [pilotspace.github.io/ADD](https://pilotspace.github.io/ADD/)*
