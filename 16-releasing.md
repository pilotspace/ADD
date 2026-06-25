# 16 · Releasing

[← 15 Foundations & Lineage](./15-foundations-and-lineage.md) · [Contents](./README.md) · Next: [17 Components →](./17-components.md)

---

The flow chapters ([03](./03-step-1-specify.md)–[08](./08-step-6-verify.md)) take one feature from
spec to verified. The loop chapter ([09](./09-the-loop.md)) keeps a milestone going until its goal
is met. The stages chapter ([10](./10-setup-and-stages.md)) graduates the project's rigor. None of
them *ship*. This chapter names the act every project eventually performs and that the method, until
now, never formalized: bundling closed milestones into a versioned, user-facing release whose notes
are evidence-backed, whose risk is disclosed, and whose behaviour is then watched.

Releasing is the **fifth scope level** — after setup, intake, the milestone loop, and stage graduation.
Like every scope level it runs the same shape: **gather → propose → the human
confirms → the engine records and enforces a floor.** And like graduation, it ends with an outward
act the human owns. The operational recipe lives in the `release.md` skill guide; this chapter is the
*why* behind it.

## 16.1 · Why release is its own scope level

A number bump is not a release. A release is the moment one or more **closed milestones** become a
versioned cut that real users can run. Three distinctions make it its own scope level:

- **Milestone ≠ release.** A milestone is *feature-complete and consolidated* — its goal is met and
  its lessons are gathered into the foundation (see [14 · The foundation](./14-foundation.md) and the
  `fold.md` retrospective consolidation). A release is *shipped and watched*. The first is an internal
  state; the second faces outward.
- **Graduation ≠ release.** Stage graduation moves the project's *rigor* (mvp → production); a release
  ships a *version*. The two axes are orthogonal: you cut a prototype preview, an mvp beta, and a
  production GA, each at its own stage. You release at every stage, not only at the end.
- **A release bundles; it does not equal.** One version may attribute several milestones — "we shipped
  after a couple of milestones closed" is the normal case, not the exception. Forcing one release per
  milestone is the anti-pattern; the decoupling is the whole point.

So release sits beside the other scope levels rather than inside any of them. The granularity ladder
is now complete: intake → milestone → task, with stage graduation and release as the two cross-cutting
levels that change *rigor* and ship *versions* respectively (see the **Scope level** entry in
[Appendix C](./appendix-c-glossary.md)).

## 16.2 · The cue and the inventory — gather, never judge

The trigger is a status line. When at least one milestone is `done`, archived, and not yet attributed
to any release, `add.py status` prints:

```
  → releasable: N milestone(s) closed since last release
```

That line is a **tally**, never a verdict. It counts archived-but-unreleased milestones; it is silent
for a project that has never released or has already shipped everything (grandfathered — zero change).
It says *there is something to consider*, not *you are ready*.

To gather the cut's evidence, run `add.py release-report`. It clusters five labeled record-sets: the
closed milestones since the last release · their **consolidated deltas** (the "what changed" record) ·
the open `RISK-ACCEPTED` waivers riding into the release · any open security `HARD-STOP` (a blocker) ·
the §2 scenarios to take live as monitors. The report **gathers; it does not judge** — there is no
readiness score to read off, because a tally that pretended to be a verdict would invite reading the
number instead of the evidence.

The reuse claim, stated plainly: **the consolidated deltas are the changelog source.** You do not write
release notes from memory. The foundation already recorded what changed when each milestone was
consolidated (`fold.md`); the release surfaces it. This is why release runs *after* consolidation, not
before. The lifecycle order is one line:
`milestone-done → fold → compact → archive → (repeat ≥1×) → release → watch`.

## 16.3 · Drafting the notes and the version — the proposal

From those record-sets you draft a [Keep a Changelog](https://keepachangelog.com/) entry: group the
changes under Added / Changed / Fixed and name the headline capabilities concretely, in the user's
language, not the commit's. Each bundled milestone's goal anchors one or more entries.

Then propose the version. Semver is a decision the evidence informs but does not make for you: a
breaking change is a MAJOR, a new capability a MINOR, a fix-only cut a PATCH. You propose the bump; the
**human confirms it** — the version is a judgement, not a default the tool fills in.

Both the notes and the version are *shown before they are asked about*. Present the drafted entry, the
proposed version, and the waivers shipping in this cut via the report template — opening with the ARC
(goal · done · plan) — and let the human approve once. The question is a summary to decide on; the
artifact itself is rendered first, never pre-stamped.

## 16.4 · The floor — what the engine enforces

`add.py release <version>` is **guarded**. Before it records anything it enforces a readiness floor,
refusing with a non-zero exit and leaving every file byte-unchanged on any of four conditions:

- `release_security_open` — an open security `HARD-STOP` exists. This is the non-negotiable one: a
  security finding is never shipped. Resolve it first, as a change request back to Specify.
- `release_tests_red` — the suite is not green. A release ships on evidence, not on a plausible diff.
- `release_no_closed_milestone` — nothing new since the last release. The cut would be a no-op; do not
  bump a version to mark time.
- `release_undisclosed_waiver` — a `RISK-ACCEPTED` waiver rides into the release but is missing from the
  notes. Disclosure *is* the floor: a shipped risk the user cannot read about is a hidden risk.

The security stop is **un-forceable.** `--force` exists for grandfathered and brownfield first-cuts —
the same authority valve as `stage --force` ([10 · Setup and stages](./10-setup-and-stages.md)) — and
it can override the other three rejects, but it can never override `release_security_open`. This mirrors
the verify gate exactly ([08 · Verify](./08-step-6-verify.md)) and the governance ceiling that no
autonomy level may lift ([11 · Governance](./11-governance.md)): a security `HARD-STOP` is the one
outcome the method refuses to auto-pass, at verify and again at the cut.

## 16.5 · The cut versus the ship — the engine records, the human ships

Only after the human confirms do you run the cut. And here is the line that keeps releasing honest:
**the engine records; the human ships.**

`add.py release <version>` **records** the marker. It prepends the entry to `CHANGELOG.md`, stamps one
append-only row (newest-first, like the §Key Decisions log) into `RELEASES.md` — date · version ·
milestones · waivers shipped · evidence — and attributes the bundled milestones to this version, so the
cue stops firing for them. The ledger is the attribution source: a milestone is "released" because a
`RELEASES.md` row says so, never because a file was edited to claim it.

What the engine does **not** do is act outward. It **never tags, publishes, or deploys.** The outward
act — `git tag`, `npm publish`, the deploy pipeline — is the human's, tool-agnostic, exactly as the
method tool "never renders" in design and "never spawns" a subagent. Design-for-failure — timeouts,
retries, rollback, a tested revert path — belongs in the pipeline the human owns, not in a method tool
that has no business holding deploy credentials. The tag is the human-gated trigger; the record is the
engine's receipt that the floor was met.

> **A caveat worth one paragraph.** `add.py release` writes `CHANGELOG.md` at the **project root**. That
> is the right default for most repositories. But a repo with a different changelog convention — for
> instance a **nested-package** layout whose root `CHANGELOG.md` is a deliberate pointer to a package's
> own changelog — will get release blocks *prepended above* its existing content rather than replacing
> it (the writer preserves what is there; it does not clobber). Reconcile per repo: either let the root
> file carry the canonical log, or point the human's publish step at the package changelog the team
> treats as the source of truth.

## 16.6 · Watch and the hotfix path — re-entering observe

A release is not the finish line; it is where the most reliable information finally appears. The §2
scenarios that were pass/fail cases at build time become **live monitors** for the released version, and
error-budget burn feeds the next loop. Live-registry and deploy confirmation are post-cut *evidence*,
gathered after the tag — not unit tests pretending to be one.

The unhappy path is first-class. A regression found in the wild re-enters at Specify as a **change
request**, which narrows to a **hotfix release** — the same seven-step flow, scoped to the fix, cut as a
PATCH. Releasing does not have a separate emergency mode; it has the ordinary flow at a tighter scope.

Depth follows the stage, as everywhere in the method:

- **prototype / poc** — a one-line preview note and a tag; no deploy ceremony. The point is feedback.
- **mvp** — full notes, a tag, a guarded publish; watch the headline scenarios.
- **production** — every step at full rigor: notes, tag, a deploy behind a rollback-tested pipeline,
  live scenario monitors, and error-budget watch. The hotfix path is a routine capability here, not a
  fire drill.

## 16.7 · The flow, in one arc

One arc, seven steps:

**cue → gather → draft notes → readiness floor → human confirms → cut → watch**

1. **cue** — `add.py status` prints `→ releasable: N` when an archived milestone is unreleased.
2. **gather** — `add.py release-report` clusters the five record-sets (gather, never judge).
3. **draft notes** — a Keep-a-Changelog entry drawn from the consolidated deltas; propose the version.
4. **readiness floor** — the four guarded rejects; the security stop is un-forceable.
5. **human confirms** — the notes, version, and waivers are shown, then approved once.
6. **cut** — `add.py release <version>` records the CHANGELOG block + the `RELEASES.md` row + attribution.
7. **watch** — the scenarios become monitors; a wild regression becomes a PATCH hotfix release.

The recipe for each step — flags, the report's `--json` shape, the exact ledger row — lives in the
`release.md` skill guide. This chapter is the reasoning; the guide is the procedure.

## 16.8 · Worked example — this method's own 1.5.0

The repository already runs this by hand, which is the best evidence the flow is real. The
`udd-design-loop` milestone closed (4/4) and consolidated into `foundation-version 33`. From those
deltas the human drafted the `## [1.5.0]` changelog entry, bumped the three version sources in
lockstep, and a forward-pinned `test_release_1_5_0.py` asserted in-repo readiness: the versions agree,
the changelog lineage survives, the feature anchors are named, and the engine is untouched by the
release. The cut itself — the `git tag` that triggers the npm and PyPI publish — stayed human-gated,
and the live-registry confirmation was gathered *after* the tag as verify evidence, never as a unit
test.

That ritual is what this chapter formalizes. `release-report` gathers the inventory, the floor enforces
the security stop and the disclosures, `add.py release` records the cut, and the human still owns the
tag. The method releases itself the way it asks every project to release: gather the evidence, disclose
the risk, record the marker, and let a person make the outward call.

---

[← 15 Foundations & Lineage](./15-foundations-and-lineage.md) · [Contents](./README.md) · Next: [17 Components →](./17-components.md)
