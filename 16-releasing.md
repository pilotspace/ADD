# 16 · Releasing

[← 15 Foundations and lineage](./15-foundations-and-lineage.md) · [Contents](./README.md) · Next: [17 Components — monorepo and multi-repo →](./17-components.md)

---

The flow chapters ([03](./03-direction.md)–[05](./05-verify.md)) take one feature from
direction to verified. The loop chapter ([06](./06-the-loop.md)) keeps a milestone going until
its goal is met. None of them *ship*. This chapter names the act every project eventually
performs and that the engine deliberately does **not** perform for you: bundling closed
milestones into a versioned, user-facing release whose notes are evidence-backed, whose risk
is disclosed, and whose behaviour is then watched.

Releasing sits at the seam between the engine and the human. The engine's part ends at a
**goal-gated milestone close**; the versioned cut — the notes, the tag, the publish, the
deploy, the watch — is the **human's outward act**, tool-agnostic by construction
([01 · principle 8](./01-principles.md)). This chapter is the *why* behind that seam.

## 16.1 · Milestone ≠ release

A number bump is not a release. A release is the moment one or more **closed milestones**
become a versioned cut real users can run. Two distinctions keep the concept clean:

- **Milestone ≠ release.** A milestone is *feature-complete and consolidated* — its goal is
  met and its lessons are folded into the foundation (see [14 · The foundation](./14-foundation.md)
  and the `fold` retrospective in [06](./06-the-loop.md)). A release is *shipped and
  watched*. The first is an internal state; the second faces outward.
- **A release bundles; it does not equal.** One version may attribute several milestones —
  "we shipped after a couple of milestones closed" is the normal case, not the exception.
  Forcing one release per milestone is the anti-pattern; the decoupling is the point.

So release is an outward act layered on top of the engine's granularity ladder — intake →
milestone → task — not a scope level the engine tracks with a verb of its own.

## 16.2 · The engine's part — the goal-gated close

The engine takes a milestone exactly as far as *done*, and no further. Two verbs, both
guarded:

- `add milestone-done <slug>` is **goal-gated**. It refuses to close a milestone while any
  criterion in its `## EXIT` section is still unchecked, and holds the milestone open until
  every box is checked. Those checkboxes are the human's affirmation that the goal is
  genuinely met — the engine reads the tally, it never judges the goal itself.
- `add milestone-archive <slug>` **retires** a done milestone and refuses anything not yet
  done — so the one goal-gate cannot be slipped by archiving around it.

That tally is never a readiness verdict. `milestone-done` tells you the goal criteria are
checked; it does not tell you the version is ready to ship. There is no readiness score to
read off, because a number that pretended to be a verdict would invite reading the number
instead of the evidence.

## 16.3 · The notes' source — consolidated lessons, never memory

You do not write release notes from memory. The foundation already recorded what changed:
when each milestone closed, its confirmed lessons were folded into the specs
(`add learn` files them, `add fold` consolidates them). `add deltas` lists what is still
open across the specs, and the folded lessons behind each closed milestone are the **source
of the changelog**. This is why the release comes *after* consolidation, not before. The
lifecycle order is one line:

`gate PASS → learn → fold → milestone-done → milestone-archive → ship → watch`

From those consolidated lessons you draft a [Keep a Changelog](https://keepachangelog.com/)
entry: group the changes under Added / Changed / Fixed and name the headline capabilities
concretely, in the user's language, not the commit's. Each bundled milestone's goal anchors
one or more entries. Then propose the version — a breaking change is a MAJOR, a new
capability a MINOR, a fix-only cut a PATCH. You propose the bump; the **human confirms it**.
The version is a judgement, not a default a tool fills in.

## 16.4 · The floor — the security HARD-STOP does not move

Everything the verify gate refuses to auto-pass, the cut refuses too. The line that carries
across is absolute: **a security finding is a `HARD-STOP`, and it is never shipped.** A
milestone carrying an open security `HARD-STOP` is not *done* — `milestone-done` has nothing
to close, because the gate never passed. Resolve it first, as a change request back to
Direction. This mirrors the verify gate exactly ([05 · Verify](./05-verify.md)) and the
governance ceiling no depth or lane may lift ([09 · Governance](./09-governance.md)): the
security stop is the one outcome the method refuses to auto-pass, at verify and again at the
cut.

Disclosure is the other half of the floor. A `RISK-ACCEPTED` waiver — a signed, non-security
risk carried past verify — that rides into a release must be **named in the notes**. A
shipped risk the user cannot read about is a hidden risk; disclosure is what makes an
accepted risk honest rather than buried.

## 16.5 · The cut versus the ship — the engine records, the human ships

Here is the line that keeps releasing honest: **the engine records; the human ships.** The
engine is a NO-EXEC notary — it records the goal-gated close and the archive, and it stops
there. What it does **not** do is act outward: it **never tags, publishes, or deploys.** The
outward act — `git tag`, `npm publish`, the deploy pipeline — is the human's, tool-agnostic,
exactly as the engine "never renders" a design and "never spawns" a subagent.

Design-for-failure — timeouts, retries, rollback, a tested revert path — belongs in the
pipeline the human owns, not in a method tool that has no business holding deploy
credentials. Release behind a mechanism that limits the blast radius of a mistake: a feature
flag, a gradual rollout, or both. Verification established the feature is correct against
everything you anticipated; a controlled release is your protection against what you did
not. The tag is the human-gated trigger; the archived milestone is the engine's receipt that
the goal-gate was met.

## 16.6 · Watch and the hotfix path — re-entering observe

A release is not the finish line; it is where the most reliable information finally appears.
The `## CHECKS` that were pass/fail cases at build time become **live monitors** for the
released version, and error-budget burn feeds the next loop. Live-registry and deploy
confirmation are post-cut *evidence*, gathered after the tag — not a unit test pretending to
be one.

The unhappy path is first-class. A regression found in the wild re-enters at
[Direction](./03-direction.md) as a **change request**, which narrows to a **hotfix** — the
same three-beat loop, scoped to the fix, cut as a PATCH. Releasing has no separate emergency
mode; it has the ordinary loop at a tighter scope. And when a deepened verify finds an exit
criterion unmet on a milestone whose task is already `done`, `add reopen <task> --to <beat>
--reason "…"` returns it to the flow with a recorded reason and a reset gate.

Ceremony scales the same way it does everywhere in the method — by the **depth dial** and the
**sensitivity floor**, never by a separate release mode. A quick preview is a one-line note
and a tag; a load-bearing cut is full notes, a tag, a deploy behind a rollback-tested
pipeline, and live monitors. The steps do not change; the ceremony around them does.

## 16.7 · The flow, in one arc

One arc, from a met goal to a watched release:

**close the milestone → archive → draft notes → confirm the version → ship → watch**

1. **close** — `add milestone-done <slug>` refuses while any `## EXIT` box is unchecked.
2. **archive** — `add milestone-archive <slug>` retires the done milestone; refuses one not done.
3. **draft notes** — a Keep-a-Changelog entry drawn from the consolidated lessons (`add deltas`); propose the version.
4. **floor** — an open security `HARD-STOP` is un-shippable; a `RISK-ACCEPTED` waiver must be disclosed.
5. **ship** — the human tags, publishes, and deploys behind a rollback-tested pipeline. The engine never does this.
6. **watch** — the checks become monitors; a wild regression becomes a PATCH hotfix at Direction.

The engine owns steps 1–2 and the security floor; the human owns the version, the tag, and
the ship. That division is the whole chapter.

## 16.8 · Worked example — this method's own cut

The repository already runs this by hand, which is the best evidence the flow is real. A
milestone closed on its goal-gate (every `## EXIT` box checked) and its lessons were folded
into the specs. From those consolidated lessons the human drafted the changelog entry, bumped
the version sources in lockstep, and a forward-pinned test asserted in-repo readiness: the
versions agree, the changelog lineage survives, the feature anchors are named, and the engine
is untouched by the release. The cut itself — the `git tag` that triggers publish — stayed
human-gated, and the live-registry confirmation was gathered *after* the tag as verify
evidence, never as a unit test.

That ritual is what this chapter describes. The engine gates the milestone on its goal and
records the close; the folded lessons feed the notes; the security floor holds; and the human
still owns the tag. The method releases itself the way it asks every project to release:
meet the goal, disclose the risk, and let a person make the outward call.

---

[← 15 Foundations and lineage](./15-foundations-and-lineage.md) · [Contents](./README.md) · Next: [17 Components →](./17-components.md)
